# Streamlit app (Phase 7)

Calls **`POST {API_BASE_URL}/v1/recommendations`** on your FastAPI service (same JSON contract as `frontend/`).

## Local (default)

1. From the repo root, start the API (see root `README.md`).
2. Install: `pip install -r requirements-streamlit.txt`
3. Run:

```bash
streamlit run streamlit_app/app.py
```

The app defaults to **`http://127.0.0.1:8000`**. Optional: set `API_BASE_URL` in the shell, or add `API_BASE_URL` in `.streamlit/secrets.toml` (see `secrets.toml.example`). You can also override the base URL in the sidebar for this session.

## Example `.streamlit/secrets.toml` (local, do not commit)

```toml
API_BASE_URL = "http://127.0.0.1:8000"
```

If you later deploy Streamlit or the API to the internet, both must use a **public** URL for the API; that is optional and not required for local development.
