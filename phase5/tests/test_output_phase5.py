from __future__ import annotations

from zomato_output import DEFAULT_EXPLANATION_TEMPLATE, experience_for_response, explanation_contradicts_facts
from zomato_output.merge import finalize_recommendation_items, merge_canonical_rows
from zomato_output.sanitize import escape_for_html
from zomato_phase1.models import Restaurant


def _r(rid: str, name: str, *, city: str = "X", rating: float = 4.2, band: str = "medium") -> Restaurant:
    return Restaurant(
        id=rid,
        name=name,
        city=city,
        area="A",
        cuisines=["north indian"],
        rating=rating,
        cost_band=band,  # type: ignore[arg-type]
    )


def test_merge_canonical_rows_dedupes_and_prefers_store() -> None:
    a1 = _r("a", "FromLLM", city="Wrong")
    a2 = _r("a", "FromLLM", city="Wrong")
    canonical = _r("a", "Canonical", city="Right")
    store = {"a": canonical}
    merged = merge_canonical_rows([a1, a2, _r("b", "B")], store)
    assert [r.id for r in merged] == ["a", "b"]
    assert merged[0].city == "Right"


def test_finalize_l6_default() -> None:
    r = _r("x", "N")
    items = finalize_recommendation_items([r], {}, limit=5)
    assert len(items) == 1
    assert items[0].explanation == DEFAULT_EXPLANATION_TEMPLATE


def test_finalize_l7_strips_contradiction() -> None:
    r = _r("x", "N", rating=4.9, band="high")
    expl = {"x": "Rated 2.1 stars and very reliable."}
    items = finalize_recommendation_items([r], expl, limit=5)
    assert items[0].explanation == DEFAULT_EXPLANATION_TEMPLATE


def test_escape_for_html() -> None:
    assert "&lt;tag&gt;" in escape_for_html("<tag>")


def test_experience_for_response() -> None:
    assert experience_for_response(match_count=0, degraded=False) == "empty"
    assert experience_for_response(match_count=3, degraded=True) == "degraded"
    assert experience_for_response(match_count=3, degraded=False) == "ok"


def test_explanation_contradicts_high_budget_cheap() -> None:
    r = _r("x", "N", band="high")
    assert explanation_contradicts_facts("Very cheap spot for students.", r) is True
    assert explanation_contradicts_facts("Great north indian food.", r) is False
