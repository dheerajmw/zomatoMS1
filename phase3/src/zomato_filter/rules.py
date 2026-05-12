from __future__ import annotations

from typing import List, Sequence, Set

from zomato_phase1.models import Restaurant
from zomato_prefs.models import ValidatedPreferences


def cuisines_match_or(user_tokens: Sequence[str], row_cuisines: Sequence[str]) -> bool:
    """OR semantics: any normalized user cuisine appears in the row's cuisine tokens (§12.1)."""
    row_set: Set[str] = set(row_cuisines)
    return any(t in row_set for t in user_tokens)


def location_matches(prefs: ValidatedPreferences, row: Restaurant) -> bool:
    """
    Case-insensitive match on city, area, or address substring (§12.1).
    ``prefs.location_normalized`` is already alias-normalized (Phase 2).
    """
    q = (prefs.location_normalized or "").strip().lower()
    if not q:
        return True
    c = (row.city or "").strip().lower()
    a = (row.area or "").strip().lower()
    addr = (row.address or "").strip().lower()

    if q == c or q == a:
        return True
    if len(q) >= 2:
        if q in c or q in a:
            return True
        if c and c in q:
            return True
        if a and a in q:
            return True
        if addr and q in addr:
            return True
    if len(q) >= 3:
        if c.startswith(q) or a.startswith(q):
            return True
        if q.startswith(c) or q.startswith(a):
            return True
    return False


def passes_hard_filters(prefs: ValidatedPreferences, row: Restaurant) -> bool:
    if row.cost_band != prefs.budget_band:
        return False
    if row.rating + 1e-9 < prefs.min_rating:
        return False
    if not cuisines_match_or(prefs.cuisines, row.cuisines):
        return False
    if not location_matches(prefs, row):
        return False
    return True


def pre_rank_sort(restaurants: List[Restaurant]) -> None:
    """Sort in-place: rating desc, then ``id`` asc (architecture §12.2 / F5)."""
    restaurants.sort(key=lambda r: (-float(r.rating), r.id))
