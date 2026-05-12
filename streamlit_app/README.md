# Streamlit app (Phase 7)

Thin UI that calls **`POST {API_BASE_URL}/v1/recommendations`** on your FastAPI service (same contract as `frontend/`).

## Local

1. Start the API from the repo root (see root `README.md`).
2. Install deps: `pip install -r requirements-streamlit.txt` (or `pip install -r streamlit_app/requirements.txt`).
3. From repo root:

```bash
export API_BASE_URL=http://127.0.0.1:8000   # optional if this is the default
streamlit run streamlit_app/app.py
```

Or use **Streamlit secrets** instead of env: create `.streamlit/secrets.toml` locally (gitignored pattern — use the template below).

## Streamlit Community Cloud

1. Connect [https://github.com/dheerajmw/zomatoMS1](https://github.com/dheerajmw/zomatoMS1) (or your fork).
2. **Main file:** `streamlit_app/app.py`
3. **Requirements file:** `streamlit_app/requirements.txt` (or `requirements-streamlit.txt` at repo root — set in app advanced settings if needed).
4. **Secrets** (App settings → Secrets), TOML:

```toml
API_BASE_URL = "https://your-public-api.example.com"
```

The API must be reachable from Streamlit’s servers (public HTTPS URL, or tunnel). **CORS** does not apply to server-side `httpx`; configure the API for browser clients separately.

## Example local secrets (do not commit)

```toml
API_BASE_URL = "http://127.0.0.1:8000"
```

Place at `.streamlit/secrets.toml` in the working directory from which you run `streamlit run`, or use Streamlit’s documented secrets paths for your install.
