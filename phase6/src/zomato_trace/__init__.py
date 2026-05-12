"""Phase 6: structured trace logging and operational helpers."""

from zomato_trace.telemetry import (
    build_recommendation_trace_payload,
    emit_recommendation_trace,
    find_orphan_result_ids,
    get_trace_logger,
    result_ids_from_items,
    warn_orphan_ids,
)

__all__ = [
    "build_recommendation_trace_payload",
    "emit_recommendation_trace",
    "find_orphan_result_ids",
    "get_trace_logger",
    "result_ids_from_items",
    "warn_orphan_ids",
]
