"""Streamlit UI: calls FastAPI POST /v1/recommendations (architecture §16)."""

from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st


def _api_base() -> str:
    try:
        v = st.secrets.get("API_BASE_URL")
        if v:
            return str(v).strip().rstrip("/")
    except Exception:
        pass
    return os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")


def _post_recommendations(payload: dict[str, Any]) -> tuple[int, Any]:
    url = f"{_api_base()}/v1/recommendations"
    with httpx.Client(timeout=120.0) as client:
        r = client.post(url, json=payload, headers={"Accept": "application/json"})
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text[:2000]}
    return r.status_code, body


st.set_page_config(
    page_title="Restaurant recommender",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("Restaurant recommender")
st.caption(
    "Calls your FastAPI service at `POST /v1/recommendations`. "
    "Set **API_BASE_URL** in Streamlit secrets or the environment."
)

with st.sidebar:
    st.markdown("**API**")
    st.code(_api_base(), language="text")
    st.markdown(
        "Streamlit Cloud: add `API_BASE_URL` in **App settings → Secrets** "
        "(public URL of your API, no trailing slash)."
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

        if status == 200 and isinstance(body, dict):
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
