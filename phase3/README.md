# Phase 3 — Filtering & candidate selection (standalone package)

Implements [doc/phase-wise-architecture.md](../doc/phase-wise-architecture.md) §12: **hard filters** (location, budget band, cuisines OR, minimum rating), **pre-rank** (rating desc, stable `id` tie-break), and **cap** to *K* before any LLM step (Phase 4).

## Package

- `zomato_filter` under `phase3/src/zomato_filter/`

## Public API

```python
from zomato_filter import FilterResult, filter_and_cap
from zomato_prefs.models import ValidatedPreferences
from zomato_phase1.models import Restaurant

result = filter_and_cap(prefs, restaurants, max_candidates_k=25)
# result.candidates, result.match_count, result.capped_to, result.filter_ms
```

Semantics match architecture §12.1 (default): location substring / equality on `city`, `area`, and `address`; budget **equality** on `cost_band`; cuisines **OR** (any user token matches a row cuisine token); rating **`>= min_rating`** inclusive.
