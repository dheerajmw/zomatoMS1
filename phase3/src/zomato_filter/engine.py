from __future__ import annotations

import time
from typing import List, Sequence

from zomato_filter.models import FilterResult
from zomato_filter.rules import passes_hard_filters, pre_rank_sort

# Runtime imports (avoid circular typing-only packages in some tooling).
from zomato_phase1.models import Restaurant
from zomato_prefs.models import ValidatedPreferences


def filter_and_cap(
    prefs: ValidatedPreferences,
    restaurants: Sequence[Restaurant],
    *,
    max_candidates_k: int,
) -> FilterResult:
    """
    Apply hard filters, pre-rank, then cap to ``max_candidates_k`` (architecture §12).

    Rows with missing structural fields are handled upstream (Phase 1); this engine
    assumes ``cost_band`` and ``cuisines`` are present for filtering.
    """
    t0 = time.perf_counter()
    k = max(0, int(max_candidates_k))

    matched: List[Restaurant] = [r for r in restaurants if passes_hard_filters(prefs, r)]
    match_count = len(matched)

    pre_rank_sort(matched)
    capped = matched[:k] if k else []
    capped_to = len(capped)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return FilterResult(
        candidates=capped,
        match_count=match_count,
        capped_to=capped_to,
        filter_ms=elapsed_ms,
    )
