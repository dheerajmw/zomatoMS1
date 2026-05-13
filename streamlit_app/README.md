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

## Streamlit Community Cloud (single deploy)

1. **Main file:** `streamlit_app/app.py`  
2. **Requirements:** `streamlit_app/requirements.txt` (or root `requirements-streamlit.txt`)  
3. **Secrets (optional):**
   - `USE_EMBEDDED_FASTAPI` = `true` (default if omitted)  
   - For HTTP-only mode: `USE_EMBEDDED_FASTAPI` = `false` and `API_BASE_URL` = `https://your-api...`  
4. Add **`GROQ_API_KEY`**, **`SKIP_DATASET_LOAD`**, etc. in **Secrets** if your Cloud app cannot read repo `.env` (Streamlit often does not ship `.env`; mirror needed keys in Secrets or use Streamlit’s env UI).

## Example `.streamlit/secrets.toml` (local)

See [`secrets.toml.example`](secrets.toml.example).
