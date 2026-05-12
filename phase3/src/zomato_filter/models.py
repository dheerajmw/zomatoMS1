from __future__ import annotations

from dataclasses import dataclass
from typing import List

from zomato_phase1.models import Restaurant


@dataclass(frozen=True)
class FilterResult:
    """Outcome of Phase 3 filtering + pre-rank + cap."""

    candidates: List[Restaurant]
    match_count: int
    """Rows passing all hard filters (before cap)."""
    capped_to: int
    """Length of ``candidates`` after applying ``max_candidates_k`` cap."""
    filter_ms: float
    """Wall time spent in the filter engine (architecture §12.3)."""
