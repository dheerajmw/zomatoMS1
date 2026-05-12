# Phase 2 — Preference capture & validation (standalone package)

Implements [doc/phase-wise-architecture.md](../doc/phase-wise-architecture.md) §11: structured **raw** request models, **vocabulary mapping** (budget + city aliases), and **validation** against dataset-derived bounds and catalog tokens.

## Package

- Python package: `zomato_prefs` under `phase2/src/zomato_prefs/`

## Public API

```python
from zomato_prefs import RawRecommendationRequest, ValidatedPreferences, validate_preferences
from zomato_prefs.errors import PreferenceValidationError

validated = validate_preferences(
    raw,
    rating_bounds=(3.0, 5.0),
    max_response_limit=10,
    catalog_tokens=frozenset({"bangalore", "banashankari"}),
)
```

## Rules (checklist §11.1)

- `min_rating` must lie within `rating_bounds` (dataset min/max).
- `cuisines` non-empty after normalization (no “any cuisine” mode in v1).
- `location` non-empty after strip; checked against `catalog_tokens` when provided.
- `notes` truncated to `max_notes_length`.
- `limit` in `[1, max_response_limit]`.

Unknown budget or unknown location (when catalog is non-empty) → `PreferenceValidationError` with optional `allowed` hints.
