from __future__ import annotations

import re
from typing import Iterable

from zomato_phase1.models import Restaurant

# Heuristic claims that conflict with structured ``cost_band`` (L7).
_HIGH_CONTRADICTION_PHRASES = (
    "very cheap",
    "extremely cheap",
    "lowest price",
    "budget-friendly",
    "cheap eats",
    "under 500",
    "under ₹500",
    "under rs 500",
)
_LOW_CONTRADICTION_PHRASES = (
    "very expensive",
    "luxury pricing",
    "most expensive",
    "pricey fine dining",
)

_RATING_PHRASES = re.compile(
    r"(?:rated|rating|stars?)\s*(?:of|at|is|:)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*/\s*5",
    re.IGNORECASE,
)


def _numbers_in_rating_context(text: str) -> Iterable[float]:
    for m in _RATING_PHRASES.finditer(text):
        g1, g2 = m.group(1), m.group(2)
        if g1:
            yield float(g1)
        elif g2:
            yield float(g2)


def explanation_contradicts_facts(explanation: str, restaurant: Restaurant) -> bool:
    """
    Return True if the explanation plausibly asserts facts incompatible with the row (L7).

    Conservative: prefer false negatives over stripping benign prose.
    """
    expl = (explanation or "").strip()
    if not expl:
        return False

    lo = expl.lower()
    band = restaurant.cost_band
    if band == "high" and any(p in lo for p in _HIGH_CONTRADICTION_PHRASES):
        return True
    if band == "low" and any(p in lo for p in _LOW_CONTRADICTION_PHRASES):
        return True

    rating = float(restaurant.rating)
    for n in _numbers_in_rating_context(expl):
        if n <= 5.0 + 1e-6 and abs(n - rating) > 0.55:
            return True

    return False
