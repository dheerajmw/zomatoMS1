# `recommender` package — backend map (architecture **§17.1**)

This tree is the **Python / FastAPI** application named in [phase-wise-architecture.md](../doc/phase-wise-architecture.md#171-backend-python--fastapi).

| Area | Path |
|------|------|
| **HTTP application** | [`api/main.py`](./api/main.py) — thin adapter: `create_app()`, lifespan, `GET /health`, `POST /v1/recommendations` → [`services/recommendations.py`](./services/recommendations.py); optional **CORS** from `CORS_ORIGINS` for `frontend/`. |
| **Configuration** | [`config.py`](./config.py) + repo-root `.env` / `.env.example` |
| **Domain DTOs** | [`domain/models.py`](./domain/models.py) |
| **Data access** | [`infra/restaurant_store.py`](./infra/restaurant_store.py) |
| **Orchestration (application)** | [`services/recommendations.py`](./services/recommendations.py) — filter → Groq → merge → trace |
| **Structured trace (Phase 6)** | [`services/tracing.py`](./services/tracing.py) → logger `recommender.phase6.trace` |
| **Shipped phase marker** | [`runtime.py`](./runtime.py) — `IMPLEMENTATION_PHASE` for `/health` |

| **First-party web UI (§17.2)** | [`../../frontend/README.md`](../../frontend/README.md) — Next.js app in `frontend/` |

Phase packages (`zomato_phase1`, `zomato_prefs`, …) live under `phase1/src/` … `phase6/src/` (see `pyproject.toml` `where` / pytest `pythonpath`).
