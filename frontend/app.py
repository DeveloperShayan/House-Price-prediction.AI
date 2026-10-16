"""
EstateIQ — entry point.  Run with:  python -m streamlit run frontend/app.py
Each page lives in frontend/views/. Shared design, header & footer live in frontend/ui.py.
"""
import streamlit as st

st.set_page_config(
    page_title="EstateIQ · AI Property Valuation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import ui  # noqa: E402  (must come after set_page_config)

ui.init_state()
ui.inject_css()

pages = {
    "Welcome": [
        st.Page("views/home.py", title="Home", icon="🏠", default=True),
    ],
    "Valuation tools": [
        st.Page("views/valuate.py", title="Instant Valuation", icon="💎", url_path="valuation"),
        st.Page("views/compare.py", title="Compare Properties", icon="⚖️", url_path="compare"),
        st.Page("views/batch.py", title="Batch Valuation", icon="📦", url_path="batch"),
    ],
    "Insights": [
        st.Page("views/dashboard.py", title="Analytics Dashboard", icon="📊", url_path="dashboard"),
        st.Page("views/about.py", title="About", icon="ℹ️", url_path="about"),
    ],
}

nav = st.navigation(pages)
ui.sidebar()
ui.navbar()
nav.run()
ui.footer()
