from __future__ import annotations

from typing import FrozenSet, Iterable, Tuple

# Common metros / search tokens merged with dataset vocabulary so users can type
# city names even when the catalog is mostly locality-centric (architecture U3 UX).
DEFAULT_METRO_TOKENS: FrozenSet[str] = frozenset(
    {
        "bangalore",
        "bengaluru",
        "mumbai",
        "delhi",
        "new delhi",
        "gurgaon",
        "gurugram",
        "noida",
        "hyderabad",
        "chennai",
        "kolkata",
        "pune",
        "jaipur",
        "ahmedabad",
        "indore",
        "lucknow",
        "kochi",
        "goa",
        "chandigarh",
    }
)


def rating_bounds_from_ratings(ratings: Iterable[float]) -> Tuple[float, float]:
    rs = [float(x) for x in ratings]
    if not rs:
        return (0.0, 5.0)
    return (min(rs), max(rs))


def city_area_tokens_from_pairs(pairs: Iterable[Tuple[str, str]]) -> FrozenSet[str]:
    """Lowercased unique city + area tokens for catalog validation."""
    out: set[str] = set()
    for city, area in pairs:
        c = (city or "").strip().lower()
        a = (area or "").strip().lower()
        if c:
            out.add(c)
        if a:
            out.add(a)
    return frozenset(out)


def merge_metro_tokens(data_tokens: FrozenSet[str]) -> FrozenSet[str]:
    return frozenset(data_tokens) | DEFAULT_METRO_TOKENS
