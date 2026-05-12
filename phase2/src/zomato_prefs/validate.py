from __future__ import annotations

from typing import Collection, Optional, Tuple

from zomato_prefs.errors import PreferenceValidationError
from zomato_prefs.models import RawRecommendationRequest, ValidatedPreferences
from zomato_prefs.vocabulary import CANONICAL_BUDGETS, map_budget_to_band, normalize_city_alias, normalize_cuisines


def _truncate_notes(notes: Optional[str], max_len: int) -> Optional[str]:
    if notes is None:
        return None
    s = notes.strip()
    if not s:
        return None
    if len(s) <= max_len:
        return s
    return s[:max_len]


def _location_matches_catalog(location_norm: str, catalog_tokens: Collection[str]) -> bool:
    """Heuristic match: exact token, substring, or prefix (architecture U3)."""
    if not catalog_tokens:
        return True
    if not location_norm:
        return False
    if location_norm in catalog_tokens:
        return True
    if len(location_norm) < 2:
        return False
    for t in catalog_tokens:
        if not t:
            continue
        if location_norm in t or t in location_norm:
            return True
        if len(location_norm) >= 3 and (t.startswith(location_norm) or location_norm.startswith(t)):
            return True
    return False


def validate_preferences(
    raw: RawRecommendationRequest,
    *,
    rating_bounds: Tuple[float, float],
    max_response_limit: int,
    max_notes_length: int = 2000,
    catalog_tokens: Optional[Collection[str]] = None,
) -> ValidatedPreferences:
    """
    Validate and normalize a raw request.

    ``rating_bounds`` should come from the loaded dataset (Phase 1) when available.
    ``catalog_tokens`` is lowercased city/area vocabulary; if ``None`` or empty, location catalog checks are skipped.
    """
    lo, hi = float(rating_bounds[0]), float(rating_bounds[1])
    if lo > hi:
        raise PreferenceValidationError("Invalid rating_bounds: min > max")

    loc_display = raw.location.strip()
    if not loc_display:
        raise PreferenceValidationError(message="location must be non-empty")

    loc_norm = normalize_city_alias(loc_display)
    if catalog_tokens and not _location_matches_catalog(loc_norm, catalog_tokens):
        sample = sorted(set(catalog_tokens))[:25]
        raise PreferenceValidationError(
            message="location is not recognized against the loaded catalog",
            allowed=sample,
        )

    band = map_budget_to_band(raw.budget)
    if band is None:
        raise PreferenceValidationError(
            message="Unknown budget label",
            allowed=list(CANONICAL_BUDGETS),
        )

    cuisines = normalize_cuisines(list(raw.cuisines))
    if not cuisines:
        raise PreferenceValidationError(message="cuisines must contain at least one non-empty item")

    mr = float(raw.min_rating)
    # U2: user cannot require a minimum above the best rating present in the dataset.
    if mr - hi > 1e-6:
        raise PreferenceValidationError(
            message=f"min_rating cannot exceed the dataset maximum ({hi:.2f})",
            allowed=[f"<= {hi:.2f}"],
        )
    if mr < 0:
        raise PreferenceValidationError(message="min_rating must be >= 0")

    lim = int(raw.limit)
    if lim < 1 or lim > max_response_limit:
        raise PreferenceValidationError(
            message=f"limit must be between 1 and {max_response_limit}",
            allowed=[f"1..{max_response_limit}"],
        )

    notes = _truncate_notes(raw.notes, max_notes_length)

    return ValidatedPreferences(
        location_display=loc_display,
        location_normalized=loc_norm,
        budget_band=band,  # type: ignore[arg-type]
        cuisines=cuisines,
        min_rating=mr,
        notes=notes,
        limit=lim,
    )
