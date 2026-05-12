# Phase 1 — Data ingestion (standalone package)

Implements [doc/phase-wise-architecture.md](../doc/phase-wise-architecture.md) §10: Hugging Face load, normalization, canonical `Restaurant` rows, and access helpers.

## Layout

- `src/zomato_phase1/` — Python package `zomato_phase1`
- `tests/` — unit tests (no network by default)

## Usage

```python
from zomato_phase1 import Restaurant, load_restaurants, get_by_ids

restaurants, meta = load_restaurants(
    dataset_id="ManikaSaini/zomato-restaurant-recommendation",
    cache_path="./data/zomato.parquet",
    use_cache=True,
)
subset = get_by_ids(restaurants, ["…", "…"])
```

Install the repo root in editable mode (`pip install -e ".[dev,data]"`) so `zomato_phase1` is on `PYTHONPATH`.

## Column mapping (ManikaSaini dataset)

| HF column | Canonical `Restaurant` field |
|-----------|------------------------------|
| `name` | `name` |
| `listed_in(city)` / `location` / address tail | `city` |
| `location` | `area` |
| `cuisines` | `cuisines[]` (lowercased tokens) |
| `rate` (`4.1/5`, etc.) | `rating` |
| `approx_cost(for two people)` | `approx_cost_for_two` + `cost_band` (`low` / `medium` / `high`) |
| `reviews_list` | `description` (truncated) |
| stable hash of key columns + revision | `id` |
