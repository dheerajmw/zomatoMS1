# Phase 5 — Output & experience (`zomato_output`)

Implements [architecture §14](../doc/phase-wise-architecture.md#14-phase-5--output--experience-detailed):

- **§14.1 Merge rules:** Deduplicate by restaurant `id`, re-attach **canonical** `Restaurant` rows from the same in-memory snapshot as filtering, default explanation when missing (**L6**), drop or replace LLM copy that **contradicts** structured facts (**L7**).
- **§14.2 UI hints:** `experience` on `RecommendationResponse` — `ok` | `empty` | `degraded` (validation stays HTTP 400).
- **M4 (HTML clients):** `escape_for_html()` for optional escaping of untrusted/LLM text before embedding in HTML; JSON API defaults to **raw** strings.

## Public API

| Symbol | Role |
|--------|------|
| `merge_canonical_rows` | Dedupe + map each row to the store’s canonical `Restaurant` by `id`. |
| `finalize_recommendation_items` | Build `RecommendationItem` list with L6/L7 + optional HTML escape. |
| `escape_for_html` | `html.escape` wrapper. |
| `explanation_contradicts_facts` | Heuristic contradiction check (rating / budget language). |
| `experience_for_response` | Derive `experience` string from counts + `degraded`. |

## Tests

```bash
pytest phase5/tests -q
```

(from repo root with `pyproject.toml` `pythonpath`, or set `PYTHONPATH=src:phase1/src:phase5/src` if invoking `python -m pytest` without the project config.)
