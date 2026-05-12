# Operations runbook — dataset (HF) & LLM outages

Cross-references: [edge-cases.md](../doc/edge-cases.md) (F1, D2, L1, L3), [problemStratement.md](../doc/problemStratement.md).

## Hugging Face / Parquet cache (D1, D2)

| Symptom | Checks | Mitigation |
|--------|--------|------------|
| Startup slow or fails; `load_source: huggingface` errors | Network, HF Hub status, rate limits | Set `HF_TOKEN` for higher limits; retry |
| Corrupt or partial Parquet | `DATA_CACHE_PATH` file size / errors in logs | Delete the cache file and restart to re-download |
| Intentionally skip remote load | — | `SKIP_DATASET_LOAD=true` → empty store; API still validates; F1 for recommendations |

Env: `HF_DATASET`, `DATA_CACHE_PATH`, `SKIP_DATASET_LOAD`, optional `HF_TOKEN`.

## Groq / LLM (L1, L3)

| Symptom | Checks | Mitigation |
|--------|--------|------------|
| High `degraded=true` rate; `llm_retry_count` at max | Groq status, model deprecation, `LLM_TIMEOUT_MS` | Increase timeout slightly; switch `GROQ_MODEL`; verify `GROQ_BASE_URL` |
| All requests degraded instantly | Invalid or revoked key | Rotate `GROQ_API_KEY`; never log the key |
| Cost / latency | `llm_latency_ms` in trace logs | Lower `MAX_CANDIDATES_K`; tune `LLM_MAX_RETRIES` |

Env: `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_BASE_URL`, `LLM_TIMEOUT_MS`, `LLM_MAX_RETRIES`, `LLM_TEMPERATURE`.

## Browser / CORS (Next.js, §17.2)

| Symptom | Checks | Mitigation |
|--------|--------|------------|
| Browser shows *NetworkError* or CORS blocked on `POST /v1/recommendations` | DevTools console | Set **`CORS_ORIGINS`** on the API to the exact web origin (e.g. `http://localhost:3000`), restart API |
| Wrong API host from the UI | `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` | Point at running FastAPI base URL |

## Logs & SLIs (§15.3)

- Parse JSON lines from logger **`recommender.phase6.trace`** with `"event":"recommendation_trace"`.
- Track: p95 `request_duration_ms`; rate of `degraded==true`; count of `orphan_result_ids` warnings (should be **0**).

## Test matrix ↔ edge cases

See [edge-cases.md §9](../doc/edge-cases.md#9-test-matrix-expanded) (e.g. T-F1 ↔ F1, T-L1 ↔ L1). Repo tests live under `tests/`, `phase1/tests/` … `phase6/tests/`.
