"""
Deploy entry for Streamlit Cloud.

- **No `FRONTEND_URL`:** same centered layout and UI as `app.py` (matches localhost).
- **With `FRONTEND_URL`:** wide layout — Next.js iframe (left) + same form/results as `app.py` (right).

Run: `streamlit run streamlit_app/Deployment.py`
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from streamlit_shared import resolve_frontend_url
from streamlit_ui import (
    DEFAULT_CAPTION,
    ensure_embedded_session,
    render_recommendation_form_and_results,
    sidebar_api_mode_widgets,
    sidebar_optional_frontend_note,
)

fe_url = resolve_frontend_url(st.secrets)

st.set_page_config(
    page_title="Restaurant recommender" + (" — Next + API" if fe_url else ""),
    page_icon="🍽️",
    layout="wide" if fe_url else "centered",
    initial_sidebar_state="expanded",
)

ensure_embedded_session()

with st.sidebar:
    sidebar_api_mode_widgets()
    sidebar_optional_frontend_note(fe_url)

if not fe_url:
    render_recommendation_form_and_results(form_key="prefs_deploy", page_caption=DEFAULT_CAPTION)
else:
    st.title("Restaurant recommender")
    st.caption(
        "Same recommendation flow as **`streamlit run streamlit_app/app.py`** — Next.js embedded on the left."
    )
    left, right = st.columns([1.05, 1.0], gap="large")

    with left:
        st.subheader("Next.js (frontend)")
        if fe_url.startswith("http://localhost") or fe_url.startswith("http://127.0.0.1"):
            safe = fe_url
        elif fe_url.startswith("https://"):
            safe = fe_url
        elif fe_url.startswith("http://"):
            safe = "https://" + fe_url.removeprefix("http://")
        else:
            safe = "https://" + fe_url
        components.iframe(safe, height=820, scrolling=True)

    with right:
        st.subheader("Recommendations")
        render_recommendation_form_and_results(
            form_key="prefs_deploy_right",
            show_page_title=False,
            notes_height=72,
        )
