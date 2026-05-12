# Phase 6 — Quality, traceability & hardening (`zomato_trace`)

Implements [architecture §15](../doc/phase-wise-architecture.md#15-phase-6--quality-traceability--hardening-detailed).

## §15.1 Structured logging

`build_recommendation_trace_payload` emits a JSON-serializable dict with (at minimum):

`request_id`, `dataset_revision`, `filter_match_count`, `k_cap`, `llm_model`, `llm_latency_ms`, `llm_retry_count`, `degraded`, `prompt_template_version`

plus operational extras: `request_duration_ms`, `returned_count`, `experience`, `sent_to_llm`, `filter_ms`, `outcome`.

Logs are written with logger name **`recommender.phase6.trace`** at **INFO** (one JSON object per line). **Never** include API keys or raw `notes`.

## §15.3 Orphan IDs

`find_orphan_result_ids` compares result `id`s to the in-memory store map; mismatches are logged at **WARNING** (SLI: zero orphan ids in production).

## Runbook

See [RUNBOOK.md](./RUNBOOK.md) (HF / LLM outages) and [edge-cases.md §9](../doc/edge-cases.md#9-test-matrix-expanded) for test ↔ case ids.

## Tests

```bash
pytest phase6/tests -q
```
