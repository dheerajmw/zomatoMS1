from __future__ import annotations

from typing import Any, Iterable, List, Mapping, Optional, Tuple

from zomato_phase1.models import Restaurant
from zomato_phase1.normalize import (
    cost_to_band,
    derive_area,
    derive_city,
    parse_approx_cost,
    parse_rate,
    split_cuisines,
    stable_restaurant_id,
    truncate_description,
)


def normalize_row(revision: str, row: Mapping[str, Any], *, description_max_chars: int = 1200) -> Optional[Restaurant]:
    """Return a Restaurant or None if the row should be dropped (architecture D4)."""
    name = str(row.get("name") or "").strip()
    if not name:
        return None

    rating = parse_rate(row.get("rate"))
    if rating is None:
        return None

    cuisines = split_cuisines(row.get("cuisines"))
    if not cuisines:
        return None

    cost_amount = parse_approx_cost(row.get("approx_cost(for two people)"))
    band = cost_to_band(cost_amount)
    if band is None:
        return None

    rid = stable_restaurant_id(revision, row)
    city = derive_city(row)
    area = derive_area(row)
    address = str(row.get("address") or "").strip()
    desc = truncate_description(row.get("reviews_list"), max_chars=description_max_chars)

    raw_debug = {
        "url": row.get("url"),
        "votes": row.get("votes"),
        "rest_type": row.get("rest_type"),
    }

    return Restaurant(
        id=rid,
        name=name,
        city=city,
        area=area,
        cuisines=cuisines,
        rating=float(rating),
        cost_band=band,  # type: ignore[arg-type]
        approx_cost_for_two=cost_amount,
        address=address,
        description=desc,
        raw=raw_debug,
    )


def normalize_rows(revision: str, rows: Iterable[Mapping[str, Any]]) -> Tuple[List[Restaurant], int, int]:
    kept: List[Restaurant] = []
    raw_count = 0
    for raw in rows:
        raw_count += 1
        norm = normalize_row(revision, raw)
        if norm is not None:
            kept.append(norm)
    dropped = raw_count - len(kept)
    return kept, raw_count, dropped
