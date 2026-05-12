"""Streamlit UI: calls FastAPI POST /v1/recommendations (architecture §16)."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import httpx
import streamlit as st

SESSION_API_OVERRIDE = "api_base_url_override"


def _likely_streamlit_cloud() -> bool:
    """Detect Streamlit Community Cloud / hosted app (not `streamlit run` on your laptop)."""
    markers = ("streamlit.app", "share.streamlit.io", "headless-sg.streamlit.io")
    for val in os.environ.values():
        if isinstance(val, str) and any(m in val.lower() for m in markers):
            return True
    base = (os.environ.get("STREAMLIT_SERVER_BASE_URL") or "").lower()
    if "streamlit.app" in base:
        return True
    for key in (
        "STREAMLIT_COMMUNITY_CLOUD",
        "STREAMLIT_CLOUD",
        "STREAMLIT_SHARING_MODE",
    ):
        if os.environ.get(key, "").lower() in ("1", "true", "yes", "streamlit"):
            return True
    return False


def _normalize_api_base(raw: str) -> str:
    u = (raw or "").strip().rstrip("/")
    if not u:
        return ""
    if u.startswith(("http://", "https://")):
        return u
    low = u.lower()
    if low.startswith("localhost") or low.startswith("127.") or low.startswith("0.0.0.0") or low.startswith("[::1]"):
        return "http://" + u
    return "https://" + u


def _api_base() -> tuple[str, str]:
    """Return (normalized URL, human-readable source). Empty URL means not configured."""
    override = ""
    if SESSION_API_OVERRIDE in st.session_state:
        override = str(st.session_state[SESSION_API_OVERRIDE] or "").strip()
    if override:
        return _normalize_api_base(override), "sidebar (this session only)"

    raw = ""
    try:
        v = st.secrets.get("API_BASE_URL")
        if v:
            raw = str(v).strip()
    except Exception:
        pass
    if raw:
        return _normalize_api_base(raw), "Streamlit Secrets: API_BASE_URL"

    env = os.environ.get("API_BASE_URL", "").strip()
    if env:
        return _normalize_api_base(env), "environment variable API_BASE_URL"

    # Hosted Streamlit must never default to loopback (ConnectError).
    if _likely_streamlit_cloud():
        return "", "not configured — add API_BASE_URL in Secrets or use the sidebar"

    return "http://127.0.0.1:8000", "default (local `streamlit run` + uvicorn on this machine)"


def _host_is_loopback(url: str) -> bool:
    if not (url or "").strip():
        return False
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return True
    if not host:
        return True
    return host in ("localhost", "127.0.0.1", "0.0.0.0", "::1")


def _connection_help_markdown(effective: str, source: str) -> str:
    cloud = _likely_streamlit_cloud()
    loop = _host_is_loopback(effective)
    lines = [
        "**Could not reach the API** (`httpx.ConnectError`). Common causes:",
        "",
        "1. **Streamlit Cloud cannot call `localhost` / `127.0.0.1`.** "
        "That address is the Cloud container, not your laptop. "
        "Deploy FastAPI to a **public HTTPS** host, then either:",
        "   - set **`API_BASE_URL`** in **☰ → Settings → Secrets** (recommended), **or**",
        "   - paste the same URL into **“API base URL override”** in the sidebar (this session only).",
        "",
        "2. **Use a full URL** — e.g. `https://your-service.onrender.com` (no trailing slash). "
        "If you omit `https://`, this app adds it for non-local hosts.",
        "",
    ]

    if not effective.strip():
        lines.append(
            "3. **Configure a base URL first.** After you set a public API, open **`https://your-api.example.com/health`** "
            "in your browser (use your real host — not `127.0.0.1` unless the API runs on the same PC as the browser)."
        )
    elif cloud and loop:
        lines.append(
            "3. **Do not** use `http://127.0.0.1/health` to verify from Streamlit Cloud — that only checks your own computer. "
            "Open **`https://<your-deployed-host>/health`** (the same host you put in Secrets / sidebar)."
        )
    elif loop:
        lines.append(
            "3. With the API on **this machine**, open `{}` in a browser on the same machine.".format(
                effective.rstrip("/") + "/health"
            )
        )
    else:
        lines.append("3. Open **`{}/health`** in a browser to verify the API is up.".format(effective.rstrip("/")))

    lines.extend(
        [
            "",
            f"**Effective base URL:** `{effective or '(not set)'}`",
            f"**Source:** {source}",
        ]
    )
    if cloud and (loop or not effective.strip()):
        lines.insert(
            0,
            ":red[**Hosted app:** configure a **public** API base URL — `127.0.0.1` will not work from Streamlit Cloud.]\n\n---\n\n",
        )
    return "\n".join(lines)


def _post_recommendations(payload: dict[str, Any]) -> tuple[int, Any]:
    base, _src = _api_base()
    if not base.strip():
        return -1, {"_error": "no_url"}
    url = f"{base.rstrip('/')}/v1/recommendations"
    try:
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            r = client.post(url, json=payload, headers={"Accept": "application/json"})
    except httpx.ConnectError:
        return -1, {"_error": "connect"}
    except httpx.TimeoutException:
        return -1, {"_error": "timeout"}
    except httpx.RequestError:
        return -1, {"_error": "request"}
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text[:2000]}
    return r.status_code, body


st.set_page_config(
    page_title="Restaurant recommender",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Sidebar first so `st.session_state[SESSION_API_OVERRIDE]` is current this run.
with st.sidebar:
    st.markdown("### API connection")
    st.text_input(
        "API base URL override",
        key=SESSION_API_OVERRIDE,
        placeholder="https://your-api.onrender.com",
        help="Paste your **public** FastAPI base URL here for quick tests. "
        "Overrides Secrets for this session only. For production, set `API_BASE_URL` in app Secrets.",
    )
    effective_base, source_label = _api_base()
    st.caption("**Resolved base**")
    st.code(effective_base or "(not set — add URL below or in Secrets)", language="text")
    st.caption(f"Source: {source_label}")
    if _likely_streamlit_cloud():
        st.info(
            "**Streamlit Cloud:** ☰ → **Settings** → **Secrets** → add `API_BASE_URL = \"https://…\"` → **Save** → **Reboot app**."
        )

effective_base, source_label = _api_base()
if _likely_streamlit_cloud() and (not effective_base.strip() or _host_is_loopback(effective_base)):
    st.warning(_connection_help_markdown(effective_base, source_label))

st.title("Restaurant recommender")
st.caption(
    "Calls your FastAPI service at `POST /v1/recommendations`. "
    "Configure the API URL in **Secrets** or the **sidebar** (see below)."
)

with st.form("prefs", clear_on_submit=False):
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
        help="Split on commas; trimmed, empty tokens dropped.",
    )
    notes = st.text_area("Notes (optional)", max_chars=8000, height=80)
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
        with st.spinner("Calling API…"):
            status, body = _post_recommendations(payload)

        if status == -1:
            kind = isinstance(body, dict) and body.get("_error")
            if kind == "timeout":
                st.error("The API did not respond in time. Try again or increase server capacity.")
            elif kind == "no_url":
                eff, src = _api_base()
                st.error(
                    "**No API base URL configured.** On Streamlit Cloud, set **`API_BASE_URL`** in Secrets "
                    "or paste your public `https://…` URL in the sidebar, then try again."
                )
                st.markdown(_connection_help_markdown(eff, src))
            else:
                eff, src = _api_base()
                st.markdown(_connection_help_markdown(eff, src))
        elif status == 200 and isinstance(body, dict):
            rid = body.get("request_id", "—")
            st.session_state["last_request_id"] = rid
            st.success(f"Request **{rid}**")

            exp = body.get("experience")
            deg = body.get("degraded", False)
            if exp == "empty":
                st.warning("No matches (F1). Try relaxing filters.")
            elif deg or exp == "degraded":
                st.info("Degraded mode (L1): deterministic ranking / shorter explanations.")
            else:
                st.info("Results loaded.")

            msgs = body.get("messages") or []
            if msgs:
                with st.expander("Diagnostics"):
                    for m in msgs:
                        st.text(m)

            results = body.get("results") or []
            if not results:
                st.write("_No rows in results._")
            else:
                for row in results:
                    rank = row.get("rank", "?")
                    name = row.get("name", "?")
                    rating = row.get("rating", 0)
                    city = row.get("city", "")
                    band = row.get("cost_band", "")
                    cuis = row.get("cuisines") or []
                    expl = row.get("explanation", "")
                    with st.container():
                        st.subheader(f"#{rank}  {name}")
                        st.caption(f"{city} · {band} · {', '.join(cuis)}  ·  ★ {rating}")
                        st.write(expl)
                        st.divider()
        elif status == 400 and isinstance(body, dict):
            detail = body.get("detail")
            if isinstance(detail, dict) and detail.get("message"):
                st.error(f"Validation: {detail.get('message')}")
            else:
                st.error(f"Bad request (400): {body}")
        else:
            st.error(f"HTTP {status}: {body}")

if "last_request_id" in st.session_state:
    st.caption(f"Last request_id: `{st.session_state['last_request_id']}`")
