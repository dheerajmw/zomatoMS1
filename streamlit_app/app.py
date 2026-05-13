"""Streamlit UI: POST /v1/recommendations — HTTP to Uvicorn or in-process FastAPI (§16)."""

from __future__ import annotations

import streamlit as st

from streamlit_ui import DEFAULT_CAPTION, ensure_embedded_session, render_recommendation_form_and_results, render_sidebar_api_mode

st.set_page_config(
    page_title="Restaurant recommender",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="expanded",
)

ensure_embedded_session()
render_sidebar_api_mode()
render_recommendation_form_and_results(form_key="prefs", page_caption=DEFAULT_CAPTION)
