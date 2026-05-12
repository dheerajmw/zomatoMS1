from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Mapping, Optional, Sequence

from recommender.domain.models import RecommendationItem

TRACE_LOGGER_NAME = "recommender.phase6.trace"
TRACE_EVENT = "recommendation_trace"


def find_orphan_result_ids(
    result_ids: Sequence[str],
    store_by_id: Mapping[str, Any],
) -> List[str]:
    """Return ids present in API results but missing from the authoritative store map (§15.3)."""
    return [rid for rid in result_ids if rid not in store_by_id]


def build_recommendation_trace_payload(
    *,
    request_id: str,
    dataset_revision: Optional[str],
    filter_match_count: int,
    k_cap: int,
    llm_model: str,
    llm_latency_ms: float,
    llm_retry_count: int,
    degraded: bool,
    prompt_template_version: str,
    request_duration_ms: float,
    returned_count: int,
    experience: str,
    sent_to_llm: int,
    filter_ms: float,
    outcome: str,
) -> Dict[str, Any]:
    """
    §15.1 required fields plus operational extras for SLIs.

    ``outcome`` examples: ``empty_f1``, ``ok_results`` — not part of §15.1 but aids log analysis.
    """
    return {
        "event": TRACE_EVENT,
        "request_id": request_id,
        "dataset_revision": dataset_revision,
        "filter_match_count": int(filter_match_count),
        "k_cap": int(k_cap),
        "llm_model": llm_model,
        "llm_latency_ms": float(llm_latency_ms),
        "llm_retry_count": int(llm_retry_count),
        "degraded": bool(degraded),
        "prompt_template_version": prompt_template_version,
        "request_duration_ms": float(request_duration_ms),
        "returned_count": int(returned_count),
        "experience": experience,
        "sent_to_llm": int(sent_to_llm),
        "filter_ms": float(filter_ms),
        "outcome": outcome,
    }


def emit_recommendation_trace(logger: Optional[logging.Logger], payload: Mapping[str, Any]) -> None:
    """Emit one JSON log line (no secrets; payload must be pre-built)."""
    if logger is None or not logger.isEnabledFor(logging.INFO):
        return
    body = dict(payload)
    body.setdefault("event", TRACE_EVENT)
    logger.info("%s", json.dumps(body, ensure_ascii=False, default=str))


def get_trace_logger() -> logging.Logger:
    return logging.getLogger(TRACE_LOGGER_NAME)


def warn_orphan_ids(logger: Optional[logging.Logger], *, request_id: str, orphan_ids: Sequence[str]) -> None:
    if not orphan_ids or logger is None or not logger.isEnabledFor(logging.WARNING):
        return
    logger.warning(
        "%s",
        json.dumps(
            {
                "event": "orphan_result_ids",
                "request_id": request_id,
                "orphan_ids": list(orphan_ids),
            },
            ensure_ascii=False,
        ),
    )


def result_ids_from_items(items: Sequence[RecommendationItem]) -> List[str]:
    return [it.id for it in items]
