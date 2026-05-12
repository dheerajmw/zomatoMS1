from __future__ import annotations

from typing import Dict, List, Sequence

from zomato_phase1.models import Restaurant


def get_by_ids(restaurants: Sequence[Restaurant], ids: Sequence[str]) -> List[Restaurant]:
    """Return restaurants for the given ids, preserving ``ids`` order (architecture §10.3)."""
    by_id: Dict[str, Restaurant] = {r.id: r for r in restaurants}
    return [by_id[i] for i in ids if i in by_id]
