from __future__ import annotations

import re
from typing import Dict, Optional

# Canonical budget bands (aligns with Phase 1 `cost_band`).
CANONICAL_BUDGETS = ("low", "medium", "high")

# Map free-text / UI tokens → canonical band (case-insensitive keys added at lookup time).
_BUDGET_SYNONYMS: Dict[str, str] = {
    "low": "low",
    "cheap": "low",
    "budget": "low",
    "1": "low",
    "₹": "low",
    "medium": "medium",
    "mid": "medium",
    "moderate": "medium",
    "2": "medium",
    "₹₹": "medium",
    "high": "high",
    "expensive": "high",
    "luxury": "high",
    "3": "high",
    "₹₹₹": "high",
}

# Normalized city spellings → canonical token used for catalog matching (lowercase).
_CITY_ALIASES: Dict[str, str] = {
    "bengaluru": "bangalore",
    "blr": "bangalore",
    "bombay": "mumbai",
    "calcutta": "kolkata",
    "delji": "delhi",
}


def normalize_budget_token(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip().lower())


def map_budget_to_band(raw: str) -> Optional[str]:
    """Return ``low`` / ``medium`` / ``high`` or None if unknown."""
    key = normalize_budget_token(raw)
    if not key:
        return None
    syn = _BUDGET_SYNONYMS.get(key)
    if syn is not None:
        return syn
    # Rupee-style hints (aligned with ``zomato_phase1.normalize.cost_to_band`` thresholds).
    digits = re.sub(r"[^\d]", "", key)
    if digits:
        try:
            cost = int(digits)
        except ValueError:
            return None
        if cost < 500:
            return "low"
        if cost <= 1200:
            return "medium"
        return "high"
    return None


def normalize_city_alias(raw: str) -> str:
    """Strip, lowercase, apply a small alias table (architecture §11.2)."""
    s = raw.strip().lower()
    if not s:
        return ""
    return _CITY_ALIASES.get(s, s)


def normalize_cuisine_token(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def normalize_cuisines(values: list) -> list[str]:
    out: list[str] = []
    for v in values:
        if v is None:
            continue
        t = normalize_cuisine_token(str(v))
        if t:
            out.append(t)
    return out
