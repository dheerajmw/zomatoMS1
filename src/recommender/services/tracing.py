from __future__ import annotations

import time
from typing import Any, Dict, Optional

from recommender.domain.models import RecommendationResponse

__all__ = ["emit_recommendation_request_trace"]


def emit_recommendation_request_trace(
    *,
    settings: Any,
    store: Any,
    request_id: str,
    fr: Any,
    llm: Any,
    resp: RecommendationResponse,
    sent_to_llm: int,
    t0: float,
    store_by_id: Dict[str, Any],
) -> None:
    """Phase 6 structured log line (architecture §15.1 / §17.1)."""
    from zomato_trace.telemetry import (
        build_recommendation_trace_payload,
        emit_recommendation_trace,
        find_orphan_result_ids,
        get_trace_logger,
        result_ids_from_items,
        warn_orphan_ids,
    )

    trace_log = get_trace_logger()
    rev: Optional[str] = None
    if store is not None and getattr(store, "meta", None) is not None:
        rev = store.meta.dataset_revision

    duration_ms = (time.perf_counter() - t0) * 1000.0
    llm_latency = float(getattr(llm, "llm_ms", 0.0) or 0.0) if llm is not None else 0.0
    llm_retry = int(getattr(llm, "retry_count", 0) or 0) if llm is not None else 0
    experience = str(resp.experience or "ok")
    outcome = "empty_f1" if resp.match_count == 0 else "ok_results"

    payload = build_recommendation_trace_payload(
        request_id=request_id,
        dataset_revision=rev,
        filter_match_count=int(fr.match_count),
        k_cap=int(settings.max_candidates_k),
        llm_model=settings.groq_model,
        llm_latency_ms=llm_latency,
        llm_retry_count=llm_retry,
        degraded=bool(resp.degraded),
        prompt_template_version=settings.prompt_template_version,
        request_duration_ms=duration_ms,
        returned_count=len(resp.results),
        experience=experience,
        sent_to_llm=int(sent_to_llm),
        filter_ms=float(fr.filter_ms),
        outcome=outcome,
    )
    emit_recommendation_trace(trace_log, payload)

    orphans = find_orphan_result_ids(result_ids_from_items(resp.results), store_by_id)
    warn_orphan_ids(trace_log, request_id=request_id, orphan_ids=orphans)
