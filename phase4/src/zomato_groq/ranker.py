from __future__ import annotations

import json
import random
import re
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import httpx

from zomato_groq.models import LLMRankResult
from zomato_phase1.models import Restaurant
from zomato_prefs.models import ValidatedPreferences


def _truncate(s: str, max_len: int) -> str:
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _candidate_payload(r: Restaurant) -> Dict[str, Any]:
    return {
        "id": r.id,
        "name": r.name,
        "city": r.city,
        "area": r.area,
        "cuisines": list(r.cuisines),
        "rating": float(r.rating),
        "cost_band": r.cost_band,
        "description": _truncate(r.description or "", 450),
    }


def build_messages(
    prefs: ValidatedPreferences,
    candidates: Sequence[Restaurant],
    *,
    prompt_template_version: str,
    response_limit: int,
) -> List[Dict[str, str]]:
    prefs_blob = {
        "location": prefs.location_display,
        "location_normalized": prefs.location_normalized,
        "budget_band": prefs.budget_band,
        "cuisines": prefs.cuisines,
        "min_rating": prefs.min_rating,
        "notes": prefs.notes,
        "desired_top_n": response_limit,
    }
    cand = [_candidate_payload(r) for r in candidates]
    system = (
        "You are a restaurant ranking assistant for a recommendation API. "
        "You MUST only reference restaurants whose `id` appears in the provided candidates JSON. "
        "Do not invent ids, ratings, prices, or venues. "
        "Return ONLY a single JSON object (no markdown fences) with keys:\n"
        '- "ordered_ids": array of ids in best-first order (subset of candidate ids)\n'
        '- "explanations": object mapping each id you include to a short neutral reason (max ~220 chars each)\n'
        f"Prompt template version: {prompt_template_version}."
    )
    user = (
        "User preferences (JSON):\n"
        + json.dumps(prefs_blob, ensure_ascii=False)
        + "\n\nCandidates (JSON array):\n"
        + json.dumps(cand, ensure_ascii=False)
        + "\n\nRank up to the user's desired_top_n for display; you may reorder all candidates. "
        "Keep explanations grounded strictly in the candidate fields."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _extract_json_object(text: str) -> Dict[str, Any]:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s).strip()
    return json.loads(s)


def _parse_ranking(content: str) -> Tuple[List[str], Dict[str, str]]:
    data = _extract_json_object(content)
    ordered = data.get("ordered_ids") or []
    expl = data.get("explanations") or {}
    if not isinstance(ordered, list):
        raise ValueError("ordered_ids must be a list")
    if not isinstance(expl, dict):
        raise ValueError("explanations must be an object")
    ids = [str(x) for x in ordered]
    explanations = {str(k): str(v) for k, v in expl.items()}
    return ids, explanations


def _ground_and_merge(
    ordered_ids: List[str],
    explanations: Dict[str, str],
    candidates: List[Restaurant],
    *,
    response_limit: int,
) -> Tuple[List[Restaurant], Dict[str, str]]:
    by_id = {r.id: r for r in candidates}
    seen = set()
    out_rows: List[Restaurant] = []
    out_expl: Dict[str, str] = {}

    for rid in ordered_ids:
        if rid in by_id and rid not in seen:
            out_rows.append(by_id[rid])
            out_expl[rid] = _truncate(explanations.get(rid, ""), 400) or _fallback_explanation(by_id[rid])
            seen.add(rid)
        if len(out_rows) >= response_limit:
            return out_rows, out_expl

    for r in candidates:
        if r.id not in seen:
            out_rows.append(r)
            out_expl[r.id] = _fallback_explanation(r)
            seen.add(r.id)
        if len(out_rows) >= response_limit:
            break

    return out_rows, out_expl


def _fallback_explanation(r: Restaurant) -> str:
    return (
        f"Matches your filters: {r.cost_band} budget, rating {r.rating:.1f}, "
        f"cuisines include {', '.join(r.cuisines[:3])}."
    )


def _groq_chat(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    timeout_s: float,
    temperature: float,
    use_json_object: bool,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": 1600,
    }
    if use_json_object:
        payload["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code == 400 and use_json_object and "response_format" in payload:
            payload.pop("response_format", None)
            resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Unexpected Groq response shape: {data!r}") from exc


def groq_rank_candidates(
    prefs: ValidatedPreferences,
    candidates: Sequence[Restaurant],
    *,
    api_key: Optional[str],
    base_url: str,
    model: str,
    timeout_s: float,
    max_retries: int,
    temperature: float,
    prompt_template_version: str,
    response_limit: int,
) -> LLMRankResult:
    """
    Ask Groq to reorder/explain, with grounding + deterministic fallback (architecture §13).
    If ``api_key`` is missing/empty, skips the network call entirely.
    """
    cands = list(candidates)
    if not cands:
        return LLMRankResult(rows=[], explanations={}, degraded=False, llm_ms=0.0, retry_count=0)

    if not (api_key or "").strip():
        rows = cands[:response_limit]
        expl = {r.id: _fallback_explanation(r) for r in rows}
        return LLMRankResult(rows=rows, explanations=expl, degraded=False, llm_ms=0.0, retry_count=0)

    messages = build_messages(
        prefs,
        cands,
        prompt_template_version=prompt_template_version,
        response_limit=response_limit,
    )

    t0 = time.perf_counter()
    max_attempts = max(1, int(max_retries) + 1)

    for attempt in range(max_attempts):
        try:
            msgs = list(messages)
            if attempt > 0:
                msgs.append(
                    {
                        "role": "user",
                        "content": "Your previous reply was not valid JSON. Reply with ONLY one JSON object, no markdown.",
                    }
                )
            content = _groq_chat(
                base_url=base_url,
                api_key=api_key.strip(),
                model=model,
                messages=msgs,
                timeout_s=timeout_s,
                temperature=temperature,
                use_json_object=True,
            )
            ordered_ids, explanations = _parse_ranking(content)
            rows, expl = _ground_and_merge(ordered_ids, explanations, cands, response_limit=response_limit)
            elapsed = (time.perf_counter() - t0) * 1000.0
            return LLMRankResult(rows=rows, explanations=expl, degraded=False, llm_ms=elapsed, retry_count=attempt)
        except (httpx.HTTPError, ValueError, json.JSONDecodeError, KeyError) as exc:
            if attempt >= max_attempts - 1:
                break
            if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
                code = exc.response.status_code
                if code < 500 and code not in (408, 409, 429):
                    break
            time.sleep((0.4 * (2**attempt)) + random.random() * 0.15)

    rows = cands[:response_limit]
    expl = {r.id: _fallback_explanation(r) for r in rows}
    elapsed = (time.perf_counter() - t0) * 1000.0
    return LLMRankResult(
        rows=rows,
        explanations=expl,
        degraded=True,
        llm_ms=elapsed,
        retry_count=max_attempts - 1,
    )
