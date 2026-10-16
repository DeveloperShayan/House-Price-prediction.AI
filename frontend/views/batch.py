import altair as alt
import pandas as pd
import streamlit as st

import report
import ui

ui.page_title("Valuation tools", "Batch portfolio valuation",
              "Upload a spreadsheet of up to 1,000 properties and value the whole portfolio in one click.")

template = pd.DataFrame(list(ui.PRESETS.values()))
c1, c2 = st.columns([1, 2], gap="large")
with c1:
    st.markdown('<div class="card"><p class="card-title">1 · Get the template</p>'
                '<p class="card-sub">A CSV with the 8 required columns and 6 example rows.</p></div>',
                unsafe_allow_html=True)
    st.download_button("⬇  Download CSV template", template.to_csv(index=False).encode(),
                       "estateiq_template.csv", "text/csv", width="stretch")
    save = st.toggle("Save results to the database", value=True,
                     help="Turn off to run a quick test without storing anything.")
with c2:
    st.markdown('<div class="card"><p class="card-title">2 · Upload your properties</p>'
                f'<p class="card-sub">Required columns: {", ".join(ui.FEATURE_KEYS)}</p></div>',
                unsafe_allow_html=True)
    upload = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

if upload is not None:
    try:
        data = pd.read_csv(upload)
    except Exception as e:  # noqa: BLE001
        st.error(f"Could not read the file: {e}")
        st.stop()

    missing = [c for c in ui.FEATURE_KEYS if c not in data.columns]
    if missing:
        st.error(f"Missing column(s): {', '.join(missing)}. Use the template above.")
        st.stop()
    clean = data[ui.FEATURE_KEYS].apply(pd.to_numeric, errors="coerce")
    bad = clean.isna().any(axis=1)
    if bad.any():
        st.warning(f"{int(bad.sum())} row(s) have empty or non-numeric values and will be skipped.")
    clean = clean[~bad]
    if len(clean) > 1000:
        st.warning("Only the first 1,000 rows will be valued.")
        clean = clean.head(1000)
    if clean.empty:
        st.error("No valid rows to value.")
        st.stop()

    st.markdown(f"**{len(clean):,} properties ready.**")
    if st.button("Value portfolio  →", type="primary"):
        with st.spinner(f"Valuing {len(clean):,} properties…"):
            preds, err = ui.api_post("/predict/batch" if save else "/predict/preview",
                                     {"items": clean.to_dict(orient="records")})
        if err:
            st.error(err)
        else:
            out = clean.reset_index(drop=True).copy()
            out["Estimated value (USD)"] = [p["estimated_price_usd"] for p in preds]
            st.session_state.batch_result = out
            ui.api_online.clear()

res = st.session_state.get("batch_result")
if res is not None:
    prices = res["Estimated value (USD)"]
    st.markdown("<br>", unsafe_allow_html=True)
    ui.kpis([("Properties valued", f"{len(res):,}"), ("Total portfolio value", ui.money(prices.sum(), short=True)),
             ("Average value", ui.money(prices.mean())), ("Highest value", ui.money(prices.max()))])

    tab1, tab2, tab3 = st.tabs(["📊  Distribution", "🗺️  Map", "🗂️  Results table"])
    with tab1:
        dist = pd.DataFrame({"Value": prices.map(ui.convert)})
        chart = alt.Chart(dist).mark_bar(color=ui.GOLD, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Value:Q", bin=alt.Bin(maxbins=20), title=f"Estimated value ({st.session_state.currency})"),
            y=alt.Y("count()", title="Properties"),
        ).properties(height=300)
        st.altair_chart(chart, width="stretch")
    with tab2:
        st.map(res.rename(columns={"Latitude": "lat", "Longitude": "lon"}), size=600, color="#C9A227")
    with tab3:
        st.dataframe(res, width="stretch", hide_index=True,
                     column_config={"Estimated value (USD)": st.column_config.NumberColumn(format="$%d")})

    c1, c2, _ = st.columns([1, 1, 2])
    c1.download_button("⬇  Results CSV", res.to_csv(index=False).encode(), "estateiq_results.csv",
                       "text/csv", width="stretch")
    c2.download_button("📄  Portfolio PDF", report.portfolio_pdf(res), "EstateIQ-portfolio.pdf",
                       "application/pdf", type="primary", width="stretch")
