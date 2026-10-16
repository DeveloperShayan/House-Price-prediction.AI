import streamlit as st

import ui

ui.page_title("About", "About EstateIQ",
              "An end-to-end machine learning platform: model, REST API, database and web interface.")

c1, c2 = st.columns([1.5, 1], gap="large")
with c1:
    st.markdown(
        """
<div class="card">
<p class="card-title">The project</p>
<p style="color:#475569;font-size:.92rem;">EstateIQ shows how a trained machine learning model becomes a real product.
A LightGBM model predicts house values, a FastAPI backend serves predictions and explanations,
Microsoft SQL Server stores every valuation, and this Streamlit interface brings it all together with
analytics and branded PDF reports.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<p class="card-title" style="margin-top:1rem;">How the system fits together</p>',
                unsafe_allow_html=True)
    st.graphviz_chart(
        """
digraph {
  rankdir=LR; bgcolor="transparent";
  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=11 color="#13294B" fillcolor="#FFFFFF" penwidth=1.4];
  edge [color="#C9A227" penwidth=1.6 fontname="Helvetica" fontsize=9 fontcolor="#64748B"];
  ui  [label="Streamlit\\nweb app" fillcolor="#FEF7E0"];
  api [label="FastAPI\\nREST API"];
  ml  [label="LightGBM\\nmodel (.pkl)"];
  db  [label="SQL Server\\nMyFirstAPI" fillcolor="#0B1B33" fontcolor="#E4C766"];
  pdf [label="PDF\\nreports"];
  ui -> api [label="JSON"]; api -> ml [label="predict / explain"]; api -> db [label="save / query"];
  ui -> pdf;
}
""",
        width="stretch",
    )
    st.markdown('<p class="card-title" style="margin-top:1rem;">API endpoints</p>', unsafe_allow_html=True)
    st.dataframe(
        {
            "Method": ["POST", "POST", "POST", "POST", "GET", "GET"],
            "Endpoint": ["/predict/", "/predict/explain", "/predict/preview", "/predict/batch",
                         "/predict/history", "/predict/stats"],
            "Purpose": ["Value one property and save it", "Explain the value drivers",
                        "Value without saving (what-if, compare)", "Value and save many properties",
                        "Read saved valuations", "Summary statistics"],
        },
        width="stretch", hide_index=True,
    )
    st.caption(f"Interactive API docs: {ui.API_BASE}/docs")

with c2:
    st.markdown(
        f"""
<div class="result">
  <small>Designed &amp; developed by</small>
  <div class="price" style="font-size:2rem;">{ui.DEV_NAME}</div>
  <div class="meta">{ui.DEV_TITLE}</div>
  <p style="color:#CBD5E1;font-size:.88rem;margin:.9rem 0;">Full-stack engineer building data-driven products
  across APIs, databases and modern web interfaces.</p>
  <a class="btn-in" href="{ui.DEV_LINKEDIN}" target="_blank" rel="noopener">{ui.LINKEDIN_ICON} Connect on LinkedIn</a>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="card" style="margin-top:1rem;">
<p class="card-title">Tech stack</p>
<p style="color:#475569;font-size:.9rem;line-height:1.9;">
🐍 Python · 🤖 Scikit-Learn &amp; LightGBM<br>⚡ FastAPI · 🗄️ SQL Server &amp; SQLAlchemy<br>
🎨 Streamlit &amp; Altair · 📄 fpdf2</p>
</div>
<div class="card">
<p class="card-title">Important note</p>
<p style="color:#475569;font-size:.88rem;">The model was trained on the California Housing dataset.
Results are indicative estimates for learning and demonstration — not formal appraisals, and not reliable
for property outside California.</p>
</div>
""",
        unsafe_allow_html=True,
    )
