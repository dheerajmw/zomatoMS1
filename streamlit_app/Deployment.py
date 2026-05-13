"""
Full-stack Streamlit entry (deployment): Next.js (iframe) + embedded FastAPI + Streamlit recommendation form.

Run locally:
  streamlit run streamlit_app/Deployment.py

Streamlit Cloud: set **Main file** to `streamlit_app/Deployment.py`, same requirements as `app.py`.

Secrets / env:
  — `FRONTEND_URL` — public HTTPS URL of your Next.js app (e.g. Vercel). Shown in the left iframe when set.
  — Same API secrets as `app.py`: `USE_EMBEDDED_FASTAPI`, `API_BASE_URL`, plus repo `.env` keys for FastAPI when embedded (e.g. `GROQ_API_KEY`, `SKIP_DATASET_LOAD`).
"""

from __future__ import annotations

import os
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from streamlit_shared import (
    SESSION_API_OVERRIDE,
    SESSION_USE_EMBEDDED,
    connect_error_help,
    initial_embedded_from_secrets,
    post_recommendations,
    resolve_api_base_url,
    resolve_frontend_url,
)


def _secrets_str(key: str) -> str | None:
    try:
        return str(st.secrets[key]).strip()
    except Exception:
        return None


def _api_base() -> str:
    ov = ""
    if SESSION_API_OVERRIDE in st.session_state:
        ov = str(st.session_state[SESSION_API_OVERRIDE] or "").strip()
    return resolve_api_base_url(
        sidebar_override=ov,
        secrets_api_base=_secrets_str("API_BASE_URL"),
        env_api_base=os.environ.get("API_BASE_URL", ""),
    )


st.set_page_config(
    page_title="Restaurant recommender — full stack",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if SESSION_USE_EMBEDDED not in st.session_state:
    st.session_state[SESSION_USE_EMBEDDED] = initial_embedded_from_secrets(st.secrets)

with st.sidebar:
    st.markdown("### Deployment")
    st.checkbox(
        "Run API inside Streamlit (embedded)",
        key=SESSION_USE_EMBEDDED,
        help="Embed FastAPI in this process (backend). Leave on for Streamlit Cloud unless you use a separate API URL.",
    )
    st.text_input(
        "HTTP base URL (when embedded is off)",
        key=SESSION_API_OVERRIDE,
        placeholder="http://127.0.0.1:8000",
    )
    fe = resolve_frontend_url(st.secrets)
    if fe:
        st.success(f"**Frontend iframe:** `{fe}`")
    else:
        st.info("Set **`FRONTEND_URL`** in Secrets (or env) to embed your Next.js app on the left.")
    if st.session_state.get(SESSION_USE_EMBEDDED, True):
        st.caption("Backend: **embedded** FastAPI")
    else:
        st.caption("Backend: **HTTP** →")
        st.code(_api_base(), language="text")

st.title("Restaurant recommender — Next.js + API")
st.caption(
    "**Left:** Next.js UI (iframe) when `FRONTEND_URL` is set. **Right:** Streamlit form calling the same "
    "`POST /v1/recommendations` as `frontend/` (embedded backend by default)."
)

fe_url = resolve_frontend_url(st.secrets)

left, right = st.columns([1.05, 1.0], gap="large")

with left:
    st.subheader("Next.js (frontend)")
    if fe_url:
        if fe_url.startswith("http://localhost") or fe_url.startswith("http://127.0.0.1"):
            safe = fe_url
        elif fe_url.startswith("https://"):
            safe = fe_url
        elif fe_url.startswith("http://"):
            safe = "https://" + fe_url.removeprefix("http://")
        else:
            safe = "https://" + fe_url
        components.iframe(safe, height=820, scrolling=True)
    else:
        st.markdown(
            "Deploy Next (`frontend/`) to Vercel or similar, then add to **Streamlit Secrets**:\n\n"
            "```toml\nFRONTEND_URL = \"https://your-app.vercel.app\"\n```\n\n"
            "Or run Next locally on port 3000 — Cloud cannot reach `localhost`; use a tunnel or split deploys."
        )

with right:
    st.subheader("Recommendations (Streamlit + API)")
    with st.form("prefs_deploy", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            location = st.text_input("Location", value="Bangalore", max_chars=160)
            budget = st.text_input("Budget", value="medium", max_chars=40)
        with c2:
            min_rating = st.number_input("Minimum rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
            limit = st.number_input("Top N", min_value=1, max_value=50, value=5, step=1)
        cuisines_raw = st.text_input(
            "Cuisines (comma-separated)",
            value="Chinese, North Indian",
        )
        notes = st.text_area("Notes (optional)", max_chars=8000, height=72)
        submitted = st.form_submit_button("Get recommendations", type="primary")

    if submitted:
        cuisines = [s.strip() for s in cuisines_raw.replace(";", ",").split(",") if s.strip()]
        if not cuisines:
            st.error("Enter at least one cuisine.")
        else:
            payload: dict[str, Any] = {
                "location": location.strip(),
                "budget": budget.strip(),
                "cuisines": cuisines,
                "min_rating": float(min_rating),
                "notes": notes.strip() or None,
                "limit": int(limit),
            }
            embedded = bool(st.session_state.get(SESSION_USE_EMBEDDED, True))
            with st.spinner("Calling API…"):
                status, body = post_recommendations(payload, embedded=embedded, api_base=_api_base())

            if status == -1:
                kind = isinstance(body, dict) and body.get("_error")
                if kind == "timeout":
                    st.error("The API did not respond in time.")
                elif kind == "import":
                    st.error(
                        f"**Import error:** `{body.get('detail', '')}` — run "
                        "`pip install -r requirements-streamlit.txt` from repo root."
                    )
                elif kind == "async_loop":
                    st.error("Turn **off** embedded and use HTTP + Uvicorn.")
                elif kind in ("asgi",):
                    st.error(f"Embedded error: `{body.get('detail', body)}`")
                else:
                    st.markdown(connect_error_help(_api_base()))
            elif status == 200 and isinstance(body, dict):
                rid = body.get("request_id", "—")
                st.success(f"Request **{rid}**")
                exp = body.get("experience")
                deg = body.get("degraded", False)
                if exp == "empty":
                    st.warning("No matches (F1).")
                elif deg or exp == "degraded":
                    st.info("Degraded mode (L1).")
                else:
                    st.info("Results loaded.")
                for m in body.get("messages") or []:
                    st.caption(m)
                for row in body.get("results") or []:
                    rank = row.get("rank", "?")
                    name = row.get("name", "?")
                    rating = row.get("rating", 0)
                    city = row.get("city", "")
                    band = row.get("cost_band", "")
                    cuis = row.get("cuisines") or []
                    expl = row.get("explanation", "")
                    st.markdown(f"#### #{rank} {name}")
                    st.caption(f"{city} · {band} · {', '.join(cuis)} · ★ {rating}")
                    st.write(expl)
                    st.divider()
            elif status == 400 and isinstance(body, dict):
                d = body.get("detail")
                if isinstance(d, dict) and d.get("message"):
                    st.error(f"Validation: {d.get('message')}")
                else:
                    st.error(str(body))
            else:
                st.error(f"HTTP {status}: {body}")
