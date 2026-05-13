"""Shared Streamlit UI — same form, sidebar, and results as local `app.py` (localhost & Cloud)."""

from __future__ import annotations

import os
from typing import Any

import streamlit as st

from streamlit_shared import (
    SESSION_API_OVERRIDE,
    SESSION_USE_EMBEDDED,
    connect_error_help,
    initial_embedded_from_secrets,
    post_recommendations,
    resolve_api_base_url,
)

DEFAULT_CAPTION = (
    "Default: **embedded FastAPI** — one deploy on Streamlit Cloud without a second service. "
    "Turn off embedded to call Uvicorn on `http://127.0.0.1:8000` (local two-terminal setup)."
)


def _secrets_str(key: str) -> str | None:
    try:
        return str(st.secrets[key]).strip()
    except Exception:
        return None


def api_base() -> str:
    ov = ""
    if SESSION_API_OVERRIDE in st.session_state:
        ov = str(st.session_state[SESSION_API_OVERRIDE] or "").strip()
    return resolve_api_base_url(
        sidebar_override=ov,
        secrets_api_base=_secrets_str("API_BASE_URL"),
        env_api_base=os.environ.get("API_BASE_URL", ""),
    )


def ensure_embedded_session() -> None:
    if SESSION_USE_EMBEDDED not in st.session_state:
        st.session_state[SESSION_USE_EMBEDDED] = initial_embedded_from_secrets(st.secrets)


def sidebar_api_mode_widgets() -> None:
    """Run inside `with st.sidebar:` — identical widgets everywhere."""
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
        st.code(api_base(), language="text")


def render_sidebar_api_mode() -> None:
    with st.sidebar:
        sidebar_api_mode_widgets()


def sidebar_optional_frontend_note(fe_url: str | None) -> None:
    st.divider()
    if fe_url:
        st.success(f"**Next iframe:** `{fe_url}`")
    else:
        st.caption("Optional: set **`FRONTEND_URL`** in Secrets to add a Next.js panel (wide layout).")


def render_recommendation_form_and_results(
    *,
    form_key: str,
    page_caption: str = DEFAULT_CAPTION,
    show_page_title: bool = True,
    notes_height: int = 80,
) -> None:
    if show_page_title:
        st.title("Restaurant recommender")
        st.caption(page_caption)

    with st.form(form_key, clear_on_submit=False):
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
        notes = st.text_area("Notes (optional)", max_chars=8000, height=notes_height)
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
                status, body = post_recommendations(payload, embedded=embedded, api_base=api_base())

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
                    st.markdown(connect_error_help(api_base()))
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
