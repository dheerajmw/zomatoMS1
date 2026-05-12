from __future__ import annotations

from zomato_filter import filter_and_cap
from zomato_phase1.models import Restaurant
from zomato_prefs.models import ValidatedPreferences


def _r(**kwargs) -> Restaurant:
    base = dict(
        id="r1",
        name="Test",
        city="Banashankari",
        area="Banashankari",
        cuisines=["chinese", "north indian"],
        rating=4.2,
        cost_band="medium",
        approx_cost_for_two=800,
        address="21st Main, Bangalore",
        description="",
        raw=None,
    )
    base.update(kwargs)
    return Restaurant.model_validate(base)


def _prefs(**kwargs) -> ValidatedPreferences:
    base = dict(
        location_display="Banashankari",
        location_normalized="banashankari",
        budget_band="medium",
        cuisines=["chinese"],
        min_rating=4.0,
        notes=None,
        limit=5,
    )
    base.update(kwargs)
    return ValidatedPreferences.model_validate(base)


def test_filter_matches_basic() -> None:
    rows = [_r(), _r(id="r2", rating=4.1)]
    fr = filter_and_cap(_prefs(), rows, max_candidates_k=10)
    assert fr.match_count == 2
    assert fr.capped_to == 2
    assert fr.candidates[0].rating >= fr.candidates[1].rating


def test_rating_threshold() -> None:
    rows = [_r(rating=3.9), _r(id="r2", rating=4.1)]
    fr = filter_and_cap(_prefs(min_rating=4.0), rows, max_candidates_k=10)
    assert fr.match_count == 1
    assert fr.candidates[0].id == "r2"


def test_budget_mismatch_drops() -> None:
    rows = [_r(cost_band="low")]
    fr = filter_and_cap(_prefs(), rows, max_candidates_k=10)
    assert fr.match_count == 0


def test_cuisine_or_semantics() -> None:
    rows = [_r(cuisines=["thai", "chinese"])]
    fr = filter_and_cap(_prefs(cuisines=["thai", "italian"]), rows, max_candidates_k=10)
    assert fr.match_count == 1


def test_cap_f2() -> None:
    rows = [_r(id=f"r{i}", rating=3.0 + i * 0.01) for i in range(30)]
    fr = filter_and_cap(_prefs(min_rating=0.0), rows, max_candidates_k=5)
    assert fr.match_count == 30
    assert fr.capped_to == 5


def test_stable_tiebreak_f5() -> None:
    rows = [_r(id="r_b", rating=4.0), _r(id="r_a", rating=4.0)]
    fr = filter_and_cap(_prefs(min_rating=0.0), rows, max_candidates_k=10)
    assert [c.id for c in fr.candidates] == ["r_a", "r_b"]


def test_location_address_substring() -> None:
    rows = [_r(city="Indiranagar", area="Indiranagar", address="Near MG Road, Bangalore")]
    fr = filter_and_cap(
        _prefs(location_display="Bangalore", location_normalized="bangalore"),
        rows,
        max_candidates_k=10,
    )
    assert fr.match_count == 1
