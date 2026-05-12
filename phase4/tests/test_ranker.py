from __future__ import annotations

from unittest.mock import patch

from zomato_groq.ranker import groq_rank_candidates
from zomato_phase1.models import Restaurant
from zomato_prefs.models import ValidatedPreferences


def _prefs(limit: int = 5) -> ValidatedPreferences:
    return ValidatedPreferences(
        location_display="Delhi",
        location_normalized="delhi",
        budget_band="low",
        cuisines=["Indian"],
        min_rating=3.0,
        notes=None,
        limit=limit,
    )


def _r(rid: str, name: str) -> Restaurant:
    return Restaurant(
        id=rid,
        name=name,
        city="Delhi",
        area="Connaught Place",
        cuisines=["Indian", "North Indian"],
        rating=4.2,
        cost_band="low",
        description="Test venue.",
    )


def test_no_api_key_skips_network_and_is_not_degraded() -> None:
    a, b = _r("a", "A"), _r("b", "B")
    out = groq_rank_candidates(
        _prefs(limit=2),
        [a, b],
        api_key=None,
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.1-8b-instant",
        timeout_s=5.0,
        max_retries=0,
        temperature=0.0,
        prompt_template_version="v0",
        response_limit=2,
    )
    assert out.degraded is False
    assert [r.id for r in out.rows] == ["a", "b"]
    assert "a" in out.explanations and "b" in out.explanations


def test_groq_reorders_via_mock() -> None:
    a, b = _r("a", "A"), _r("b", "B")
    payload = (
        '{"ordered_ids": ["b","a"], "explanations": {"b": "Closer match.", "a": "Also fits."}}'
    )
    with patch("zomato_groq.ranker._groq_chat", return_value=payload):
        out = groq_rank_candidates(
            _prefs(limit=2),
            [a, b],
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-8b-instant",
            timeout_s=5.0,
            max_retries=1,
            temperature=0.0,
            prompt_template_version="v0",
            response_limit=2,
        )
    assert out.degraded is False
    assert [r.id for r in out.rows] == ["b", "a"]
    assert out.explanations["b"] == "Closer match."


def test_grounding_drops_unknown_ids() -> None:
    a, b = _r("a", "A"), _r("b", "B")
    payload = '{"ordered_ids": ["ghost","b","a"], "explanations": {"ghost": "x", "b": "ok", "a": "fine"}}'
    with patch("zomato_groq.ranker._groq_chat", return_value=payload):
        out = groq_rank_candidates(
            _prefs(limit=3),
            [a, b],
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-8b-instant",
            timeout_s=5.0,
            max_retries=0,
            temperature=0.0,
            prompt_template_version="v0",
            response_limit=3,
        )
    assert [r.id for r in out.rows] == ["b", "a"]
    assert "ghost" not in out.explanations


def test_invalid_json_sets_degraded() -> None:
    a = _r("a", "A")
    with patch("zomato_groq.ranker._groq_chat", return_value="NOT JSON {{{"):
        out = groq_rank_candidates(
            _prefs(limit=1),
            [a],
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-8b-instant",
            timeout_s=5.0,
            max_retries=0,
            temperature=0.0,
            prompt_template_version="v0",
            response_limit=1,
        )
    assert out.degraded is True
    assert [r.id for r in out.rows] == ["a"]
