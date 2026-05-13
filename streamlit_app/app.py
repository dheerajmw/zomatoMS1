"""Streamlit UI: POST /v1/recommendations — HTTP to Uvicorn or in-process FastAPI (§16)."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from urllib.parse import urlparse

import httpx
import streamlit as st


def _ensure_repo_src_on_path() -> None:
    """So `import recommender` works when the app is run from the repo (incl. Streamlit Cloud)."""
    root = Path(__file__).resolve().parent.parent
    for rel in (
        "src",
        "phase1/src",
        "phase2/src",
        "phase3/src",
        "phase4/src",
        "phase5/src",
        "phase6/src",
    ):
        p = root / rel
        if p.is_dir():
            s = str(p)
            if s not in sys.path:
                sys.path.insert(0, s)


_ensure_repo_src_on_path()

SESSION_API_OVERRIDE = "api_base_url_override"
SESSION_USE_EMBEDDED = "use_embedded_fastapi"


def _normalize_api_base(raw: str) -> str:
    u = (raw or "").strip().rstrip("/")
    if not u:
        return "http://127.0.0.1:8000"
    if u.startswith(("http://", "https://")):
        return u
    low = u.lower()
    if low.startswith("localhost") or low.startswith("127.") or low.startswith("0.0.0.0") or low.startswith("[::1]"):
        return "http://" + u
    return "https://" + u


def _api_base() -> str:
    if SESSION_API_OVERRIDE in st.session_state:
        o = str(st.session_state[SESSION_API_OVERRIDE] or "").strip()
        if o:
            return _normalize_api_base(o)
    try:
        v = st.secrets.get("API_BASE_URL")
        if v:
            return _normalize_api_base(str(v).strip())
    except Exception:
        pass
    env = os.environ.get("API_BASE_URL", "").strip()
    if env:
        return _normalize_api_base(env)
    return "http://127.0.0.1:8000"


def _host_is_loopback(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False
    return host in ("localhost", "127.0.0.1", "0.0.0.0", "::1")


def _connect_error_help(base: str) -> str:
    if _host_is_loopback(base):
        return (
            f"**Could not connect to `{base}`.**\n\n"
            "**Quick fix:** In the sidebar, turn **ON** *Run API inside Streamlit (embedded)* — "
            "the FastAPI app runs in this process (no Uvicorn). Repo layout: parent of `streamlit_app/` contains `pyproject.toml`.\n\n"
            "**Or** run `uvicorn recommender.api.main:app --host 127.0.0.1 --port 8000` and turn embedded **OFF**."
        )
    return f"**Could not connect to `{base}`.** Check the URL or use embedded mode."


async def _post_via_asgi_async(payload: dict[str, Any]) -> tuple[int, Any]:
    _ensure_repo_src_on_path()
    from recommender.api.main import app as asgi_app

    transport = httpx.ASGITransport(app=asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://streamlit.embedded", timeout=180.0) as client:
        r = await client.post(
            "/v1/recommendations",
            json=payload,
            headers={"Accept": "application/json"},
        )
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text[:2000]}
    return r.status_code, body


def _post_via_asgi(payload: dict[str, Any]) -> tuple[int, Any]:
    try:
        return asyncio.run(_post_via_asgi_async(payload))
    except ImportError as e:
        return -1, {"_error": "import", "detail": str(e)}
    except RuntimeError as e:
        if "asyncio.run()" in str(e) or "cannot be called from a running event loop" in str(e).lower():
            return -1, {"_error": "async_loop", "detail": str(e)}
        raise
    except Exception as e:
        return -1, {"_error": "asgi", "detail": str(e)}


def _post_recommendations(payload: dict[str, Any]) -> tuple[int, Any]:
    if st.session_state.get(SESSION_USE_EMBEDDED, True):
        return _post_via_asgi(payload)

    base = _api_base()
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


def _initial_embedded() -> bool:
    try:
        v = st.secrets["USE_EMBEDDED_FASTAPI"]
    except Exception:
        return True
    if isinstance(v, str):
        return v.strip().lower() not in ("false", "0", "no", "")
    return bool(v)


st.set_page_config(
    page_title="Restaurant recommender",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="expanded",
)

if SESSION_USE_EMBEDDED not in st.session_state:
    st.session_state[SESSION_USE_EMBEDDED] = _initial_embedded()

with st.sidebar:
    st.markdown("### API mode")
    st.checkbox(
        "Run API inside Streamlit (embedded)",
        key=SESSION_USE_EMBEDDED,
        help="**On (default):** FastAPI runs in-process — best for **Streamlit Cloud** (no separate backend URL). "
        "**Off:** HTTP to the base URL below (local Uvicorn or a public API).",
    )
    st.text_input(
        "HTTP base URL (when embedded is off)",
        key=SESSION_API_OVERRIDE,
        placeholder="http://127.0.0.1:8000",
        help="Used only when embedded mode is unchecked.",
    )
    if st.session_state.get(SESSION_USE_EMBEDDED, True):
        st.caption("Mode: **in-process** (no TCP to localhost).")
    else:
        st.caption("Mode: **HTTP**")
        st.code(_api_base(), language="text")

st.title("Restaurant recommender")
st.caption(
    "Default: **embedded FastAPI** — one deploy on Streamlit Cloud without a second service. "
    "Turn off embedded to call Uvicorn on `http://127.0.0.1:8000` (local two-terminal setup)."
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
                st.error("The API did not respond in time. Try again.")
            elif kind == "import":
                st.error(
                    f"**Could not import the FastAPI app:** `{body.get('detail', '')}`\n\n"
                    "Install deps: **`pip install -r requirements-streamlit.txt`** from the repo root "
                    "(includes FastAPI, datasets, etc.). Or turn **off** embedded and run Uvicorn separately."
                )
            elif kind == "async_loop":
                st.error("Embedded mode hit an asyncio conflict. Turn **off** embedded and use HTTP + Uvicorn.")
            elif kind in ("asgi",):
                st.error(f"Embedded API error: `{body.get('detail', body)}`")
            else:
                st.markdown(_connect_error_help(_api_base()))
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
