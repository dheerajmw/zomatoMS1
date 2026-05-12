# Zomato-inspired restaurant recommender

Phases **0–6** are implemented in code; **Phase 7** adds an optional **Streamlit** UI under `streamlit_app/` (see [architecture §16](doc/phase-wise-architecture.md#16-phase-7-streamlit-deployment)). Backend: [§17.1](doc/phase-wise-architecture.md#171-backend-python--fastapi); Next.js: [§17.2](doc/phase-wise-architecture.md#172-frontend-and-api-clients) in **`frontend/`**.

Related docs: [problem statement](doc/problemStratement.md), [architecture](doc/phase-wise-architecture.md), [edge cases](doc/edge-cases.md).

## Repository layout

```
doc/
frontend/                 # Next.js UI (architecture §17.2) — see frontend/README.md
streamlit_app/            # Streamlit UI (Phase 7) — see streamlit_app/README.md
phase1/src/zomato_phase1/   # HF load, normalize, access (Phase 1)
phase2/src/zomato_prefs/    # Raw request + validation (Phase 2)
phase3/src/zomato_filter/   # Hard filters + pre-rank + cap (Phase 3)
phase4/src/zomato_groq/     # Groq ranking + explanations (Phase 4)
phase5/src/zomato_output/   # Merge, L6/L7, dedupe, HTML escape helper (Phase 5)
phase6/src/zomato_trace/    # Structured logs + orphan-id warnings (Phase 6)
phase6/RUNBOOK.md           # HF / LLM outage notes
src/recommender/            # FastAPI app, config, domain, infra, services (see src/recommender/README.md)
config/schemas/             # JSON Schema exports
data/                       # Parquet cache (gitignored when large)
tests/                      # API + service tests
phase1/tests/ … phase6/tests/
scripts/
output/                     # optional local demo outputs (gitignored if desired)
```

## Quickstart

```bash
cd zomatoMS1
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"       # pulls datasets/pyarrow/pandas for Phase 1
cp .env.example .env        # optional; then edit secrets; keys mirror pydantic defaults where set
```

**Prefetch / extract dataset (Hugging Face → parquet cache)**

With **`SKIP_DATASET_LOAD=false`** in `.env`, the API loads data on startup. To **pull and cache data once** (same Phase 1 pipeline), from the **repo root**:

```bash
python3 scripts/prefetch_zomato_dataset.py
```

This script **always** loads (it ignores `SKIP_DATASET_LOAD` for that run). Ensure `HF_DATASET` / `DATA_CACHE_PATH` in `.env` match what you want; first download needs network access.

**Run the API**

```bash
uvicorn recommender.api.main:app --reload --host 0.0.0.0 --port 8000
# or:
zomato-serve
# or:
python -m recommender
```

**Smoke check**

- Health: `GET http://127.0.0.1:8000/health` (includes dataset load stats when `SKIP_DATASET_LOAD=false`)
- Stub recommendations: `POST http://127.0.0.1:8000/v1/recommendations` with a JSON body (see OpenAPI or `config/schemas/raw-recommendation-request.json`).
- Interactive OpenAPI: `http://127.0.0.1:8000/docs`

## Next.js UI (`frontend/`)

1. In **API** `.env`, set `CORS_ORIGINS=http://localhost:3000` (see `.env.example`).
2. From `frontend/`: `npm install && npm run dev` → [http://localhost:3000](http://localhost:3000).

Details: [`frontend/README.md`](frontend/README.md).

## Streamlit UI (`streamlit_app/`)

1. Run the **API** (same as above).
2. `pip install -r requirements-streamlit.txt`
3. `streamlit run streamlit_app/app.py` — defaults to `http://127.0.0.1:8000` (see [`streamlit_app/README.md`](streamlit_app/README.md)).

## Configuration

Environment variables are listed in [`.env.example`](.env.example) and loaded via `pydantic-settings` in `src/recommender/config.py`. **Do not commit real API keys**; `.env` is gitignored.

## Contracts

| Artifact | Location |
|----------|----------|
| Pydantic models (source of truth) | `src/recommender/domain/models.py` + `phase2/src/zomato_prefs/models.py` |
| JSON Schema exports | `config/schemas/*.json` |
| Regenerate schemas after model changes | `python scripts/export_json_schemas.py` |
| Live OpenAPI | `/openapi.json` when the server is running |

Error codes used in API responses follow the taxonomy in architecture §9.3 (`VALIDATION_ERROR`, `NO_DATA`, `NO_MATCHES`, `UPSTREAM_LLM`).

## Tests

```bash
pytest
```

## Phase 3 filter package (`phase3/`)

- Package: `zomato_filter` (`phase3/src/zomato_filter/`)
- Entry point: `filter_and_cap(validated_prefs, restaurants, max_candidates_k=...)`
- See `phase3/README.md`

## Phase 2 preferences package (`phase2/`)

- Package: `zomato_prefs` (`phase2/src/zomato_prefs/`)
- Request body model: `RawRecommendationRequest` (flexible `budget` string)
- Validated model: `ValidatedPreferences` (passed to Phase 3 `zomato_filter`)
- See `phase2/README.md`

## Phase 1 data package (`phase1/`)

Ingestion and normalization live in a **separate installable tree** per project layout:

- Package: `zomato_phase1` under `phase1/src/zomato_phase1/`
- HF dataset default: `ManikaSaini/zomato-restaurant-recommendation`
- At API startup, `SKIP_DATASET_LOAD=false` (default) loads data into memory (see lifespan in `recommender.api.main`; recommendation orchestration in `recommender.services.recommendations`).
- **Tests** force `SKIP_DATASET_LOAD=true` via `tests/conftest.py` so CI stays offline.

See `phase1/README.md` for column mapping and usage.


## Out of scope (unchanged)

Per [doc/problemStratement.md](doc/problemStratement.md): live Zomato APIs, payments, orders, and persistent user profiles are not part of this milestone.
