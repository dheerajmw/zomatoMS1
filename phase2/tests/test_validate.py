from __future__ import annotations

import pytest

from zomato_prefs import RawRecommendationRequest, validate_preferences
from zomato_prefs.errors import PreferenceValidationError


def _raw(**kwargs) -> RawRecommendationRequest:
    base = dict(
        location="Banashankari",
        budget="medium",
        cuisines=["Chinese"],
        min_rating=3.0,
        notes=None,
        limit=5,
    )
    base.update(kwargs)
    return RawRecommendationRequest.model_validate(base)


def test_budget_synonyms() -> None:
    assert validate_preferences(_raw(budget="₹₹"), rating_bounds=(0, 5), max_response_limit=10).budget_band == "medium"
    assert validate_preferences(_raw(budget="expensive"), rating_bounds=(0, 5), max_response_limit=10).budget_band == "high"


def test_numeric_budget_rupees() -> None:
    assert validate_preferences(_raw(budget="1500"), rating_bounds=(0, 5), max_response_limit=10).budget_band == "high"
    assert validate_preferences(_raw(budget="₹ 800"), rating_bounds=(0, 5), max_response_limit=10).budget_band == "medium"
    assert validate_preferences(_raw(budget="400"), rating_bounds=(0, 5), max_response_limit=10).budget_band == "low"


def test_city_alias_bengaluru() -> None:
    v = validate_preferences(
        _raw(location="Bengaluru"),
        rating_bounds=(0, 5),
        max_response_limit=10,
        catalog_tokens=frozenset({"bangalore", "banashankari"}),
    )
    assert v.location_normalized == "bangalore"


def test_city_alias_delji_to_delhi() -> None:
    v = validate_preferences(
        _raw(location="delji"),
        rating_bounds=(0, 5),
        max_response_limit=10,
        catalog_tokens=frozenset({"delhi", "new delhi"}),
    )
    assert v.location_normalized == "delhi"


def test_min_rating_above_dataset_max_rejected() -> None:
    with pytest.raises(PreferenceValidationError):
        validate_preferences(_raw(min_rating=5.0), rating_bounds=(2.0, 4.9), max_response_limit=10)


def test_unknown_budget() -> None:
    with pytest.raises(PreferenceValidationError) as ei:
        validate_preferences(_raw(budget="platinum"), rating_bounds=(0, 5), max_response_limit=10)
    assert ei.value.allowed


def test_unknown_location_with_catalog() -> None:
    with pytest.raises(PreferenceValidationError):
        validate_preferences(
            _raw(location="Atlantis"),
            rating_bounds=(0, 5),
            max_response_limit=10,
            catalog_tokens=frozenset({"banashankari"}),
        )


def test_limit_over_max() -> None:
    with pytest.raises(PreferenceValidationError):
        validate_preferences(_raw(limit=99), rating_bounds=(0, 5), max_response_limit=10)


def test_notes_truncation() -> None:
    long = "x" * 5000
    v = validate_preferences(_raw(notes=long), rating_bounds=(0, 5), max_response_limit=10, max_notes_length=100)
    assert v.notes is not None
    assert len(v.notes) == 100
