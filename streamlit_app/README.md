# Streamlit app (Phase 7)

Calls **`POST /v1/recommendations`** using either:

1. **Embedded FastAPI (default)** — the same `recommender.api.main:app` runs **inside** the Streamlit process via `httpx.ASGITransport` (no Uvicorn, no `API_BASE_URL` needed for requests). **Use this on Streamlit Community Cloud** so one app = UI + backend.
2. **HTTP mode** — `POST` to `{API_BASE_URL}/v1/recommendations` when you uncheck embedded (local Uvicorn or a public API).

## Dependencies

From the **repo root** (parent of `streamlit_app/`):

```bash
pip install -r requirements-streamlit.txt
```

Embedded mode needs the same runtime stack as the API (FastAPI, datasets, pyarrow, etc.).

## Local

```bash
streamlit run streamlit_app/app.py
```

- **Embedded on (default):** ensure `.env` in repo root has `SKIP_DATASET_LOAD=false` (or unset) when you want real data; first load can download HF / write parquet cache.
- **Embedded off:** start Uvicorn (`uvicorn recommender.api.main:app --host 127.0.0.1 --port 8000`), then uncheck embedded or set `API_BASE_URL`.

## Full stack (Next.js iframe + embedded API)

Single Streamlit page that embeds the **Next.js** UI (iframe) and a **Streamlit** recommendation panel sharing the same backend:

```bash
streamlit run streamlit_app/Deployment.py
```

Set **`FRONTEND_URL`** in Secrets or env to your deployed Next app (`https://…`), or `http://localhost:3000` when testing locally. Many sites send `X-Frame-Options` that block iframing; Vercel deployments often work for demos.

The `.streamlit/` config folder was removed from the repo; Streamlit uses defaults unless you add `.streamlit/config.toml` locally.

## Streamlit Community Cloud

| Use case | Main file |
|----------|-----------|
| Recommendations only | `streamlit_app/app.py` |
| Next iframe + API panel | `streamlit_app/Deployment.py` |

**Requirements:** `streamlit_app/requirements.txt` (or root `requirements-streamlit.txt`).

**Secrets (optional):**

- `USE_EMBEDDED_FASTAPI` — `true` (default if omitted) for embedded backend.
- For HTTP-only mode: `USE_EMBEDDED_FASTAPI` = `false` and `API_BASE_URL` = `https://your-api…`
- **`FRONTEND_URL`** — required for the iframe in `Deployment.py` (production Next URL or local URL when testing).
- Mirror **`GROQ_API_KEY`**, **`SKIP_DATASET_LOAD`**, etc. in Secrets if Cloud cannot read repo `.env`.

## Example `.streamlit/secrets.toml` (local)

See [`secrets.toml.example`](secrets.toml.example).
