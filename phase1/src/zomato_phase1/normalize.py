from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Mapping, Optional

_STABLE_KEYS = (
    "address",
    "approx_cost(for two people)",
    "cuisines",
    "listed_in(city)",
    "location",
    "name",
    "rate",
)


def stable_restaurant_id(revision: str, row: Mapping[str, Any]) -> str:
    """Deterministic id from revision + stable raw fields (architecture §10.2)."""
    payload = {k: row.get(k) for k in _STABLE_KEYS}
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.sha256(f"{revision}|{blob}".encode("utf-8")).hexdigest()
    return f"r_{digest[:24]}"


def parse_rate(value: Any) -> Optional[float]:
    """Parse Zomato `rate` like '4.1/5' or 'NEW' or '-'."""
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() in {"NEW", "-", "NAN", "NONE"}:
        return None
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*5\s*$", s)
    if m:
        return float(m.group(1))
    m2 = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*$", s)
    if m2:
        val = float(m2.group(1))
        return val if val <= 5 else min(val / 2, 5.0)  # heuristic if someone stored /10
    return None


def parse_approx_cost(value: Any) -> Optional[int]:
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() in {"NAN", "NONE", "-"}:
        return None
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    return int(digits)


def cost_to_band(cost: Optional[int]) -> Optional[str]:
    """Map rupee 'cost for two' to coarse bands (tunable)."""
    if cost is None:
        return None
    if cost < 500:
        return "low"
    if cost <= 1200:
        return "medium"
    return "high"


def split_cuisines(value: Any) -> list[str]:
    if value is None:
        return []
    parts = re.split(r"[,/|]", str(value))
    out = [p.strip().lower() for p in parts if p.strip()]
    return out


def derive_city(row: Mapping[str, Any]) -> str:
    listed = row.get("listed_in(city)")
    if listed is not None:
        s = str(listed).strip()
        if s:
            return s
    loc = row.get("location")
    if loc is not None and str(loc).strip():
        return str(loc).strip()
    # Very light heuristic from address tail (e.g. ", Bangalore")
    addr = str(row.get("address") or "")
    m = re.search(r",\s*([A-Za-z][A-Za-z\s]+)\s*$", addr)
    if m:
        return m.group(1).strip()
    return "unknown"


def derive_area(row: Mapping[str, Any]) -> str:
    loc = row.get("location")
    if loc is None:
        return ""
    return str(loc).strip()


def truncate_description(reviews_list: Any, max_chars: int = 1200) -> str:
    s = "" if reviews_list is None else str(reviews_list)
    s = s.replace("\r", " ").strip()
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"
