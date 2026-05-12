from __future__ import annotations

import json
import logging

import pytest

from recommender.domain.models import RecommendationItem
from zomato_trace.telemetry import (
    build_recommendation_trace_payload,
    emit_recommendation_trace,
    find_orphan_result_ids,
    result_ids_from_items,
    warn_orphan_ids,
)


def test_build_recommendation_trace_payload_has_section_15_1_keys() -> None:
    p = build_recommendation_trace_payload(
        request_id="rid-1",
        dataset_revision="rev-a",
        filter_match_count=12,
        k_cap=25,
        llm_model="llama-test",
        llm_latency_ms=120.5,
        llm_retry_count=1,
        degraded=True,
        prompt_template_version="v0",
        request_duration_ms=200.0,
        returned_count=3,
        experience="degraded",
        sent_to_llm=10,
        filter_ms=5.0,
        outcome="ok_results",
    )
    for k in (
        "request_id",
        "dataset_revision",
        "filter_match_count",
        "k_cap",
        "llm_model",
        "llm_latency_ms",
        "llm_retry_count",
        "degraded",
        "prompt_template_version",
    ):
        assert k in p
    assert "api_key" not in json.dumps(p).lower()
    json.dumps(p)  # serializable


def test_find_orphan_result_ids() -> None:
    store = {"a": 1, "b": 2}
    assert find_orphan_result_ids(["a", "ghost"], store) == ["ghost"]


def test_result_ids_from_items() -> None:
    items = [
        RecommendationItem(
            id="x",
            rank=1,
            name="N",
            city="C",
            cuisines=["c"],
            rating=4.0,
            cost_band="low",
            explanation="e",
        )
    ]
    assert result_ids_from_items(items) == ["x"]


def test_emit_recommendation_trace_with_caplog(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    log = logging.getLogger("recommender.phase6.trace.test")
    payload = build_recommendation_trace_payload(
        request_id="r",
        dataset_revision=None,
        filter_match_count=0,
        k_cap=25,
        llm_model="m",
        llm_latency_ms=0.0,
        llm_retry_count=0,
        degraded=False,
        prompt_template_version="v0",
        request_duration_ms=1.0,
        returned_count=0,
        experience="empty",
        sent_to_llm=0,
        filter_ms=1.0,
        outcome="empty_f1",
    )
    emit_recommendation_trace(log, payload)
    assert any("recommendation_trace" in r.message for r in caplog.records)


def test_warn_orphan_ids(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    log = logging.getLogger("recommender.phase6.trace.test_warn")
    warn_orphan_ids(log, request_id="rid", orphan_ids=["bad"])
    assert any("orphan_result_ids" in r.message for r in caplog.records)
