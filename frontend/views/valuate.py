from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

import report
import ui

P = "v_"  # session-state prefix for this page's inputs
ui.ensure_inputs(P)


def tier(usd: float) -> str:
    if usd < 150_000:
        return "Affordable"
    if usd < 250_000:
        return "Mid-market"
    if usd < 400_000:
        return "Premium"
    return "Luxury"


def on_preset():
    name = st.session_state.v_preset
    if name in ui.PRESETS:
        ui.set_inputs(P, ui.PRESETS[name])


ui.page_title("Valuation tools", "Instant property valuation",
              "Describe the property, get an explainable market estimate and download a branded report.")

left, right = st.columns([1.3, 1], gap="large")

# ---------------------------------------------------------------- form
with left:
    st.selectbox("Start from a market preset (optional)", ["Custom", *ui.PRESETS],
                 key="v_preset", on_change=on_preset)
    with st.form("valuation_form", border=False):
        st.markdown('<div class="section-head"><span class="ico">💼</span>Neighbourhood economics</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        ui.number_input(c1, P, "MedInc")
        ui.number_input(c2, P, "Population")
        st.markdown('<div class="section-head"><span class="ico">🏠</span>Property characteristics</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        ui.number_input(c1, P, "HouseAge")
        ui.number_input(c2, P, "AveOccup")
        c1, c2 = st.columns(2)
        ui.number_input(c1, P, "AveRooms")
        ui.number_input(c2, P, "AveBedrms")
        st.markdown('<div class="section-head"><span class="ico">📍</span>Location</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        ui.number_input(c1, P, "Latitude")
        ui.number_input(c2, P, "Longitude")
        submitted = st.form_submit_button("Generate valuation  →")

# ---------------------------------------------------------------- run valuation
if submitted:
    features = ui.read_inputs(P)
    if features["AveBedrms"] > features["AveRooms"]:
        st.warning("Average bedrooms is higher than average rooms — please double-check the inputs.")
    with right, st.spinner("Analysing market signals…"):
        result, err = ui.api_post("/predict/", features)
        if err:
            st.error(err)
        else:
            explanation, _ = ui.api_post("/predict/explain", features)
            st.session_state.last_valuation = dict(
                features=features,
                price=result["estimated_price_usd"],
                model_output=result["predicted_value"],
                explanation=explanation,
                time=datetime.now(),
                ref="EIQ-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            )
            ui.api_online.clear()

last = st.session_state.get("last_valuation")

# ---------------------------------------------------------------- result panel
with right:
    if last:
        f, price = last["features"], last["price"]
        st.markdown(
            f"""
<div class="result">
  <small>Estimated market value</small>
  <div class="price">{ui.money(price)}</div>
  <div class="meta">Ref {last['ref']} · {last['time'].strftime('%d %b %Y, %H:%M')}</div>
  <div class="range">Indicative range: {ui.money(price * 0.9)} – {ui.money(price * 1.1)}</div>
  <span class="pill">✓ Saved to database</span><span class="tier">★ {tier(price)}</span>
</div>
""",
            unsafe_allow_html=True,
        )
        rpp = f["AveRooms"] / f["AveOccup"] if f["AveOccup"] else 0
        ui.kpis([("Income", ui.money(f["MedInc"] * 10000)), ("House age", f"{f['HouseAge']:.0f} yrs"),
                 ("Rooms", f"{f['AveRooms']:.1f}"), ("Rooms / person", f"{rpp:.2f}")])
        st.map(pd.DataFrame({"lat": [f["Latitude"]], "lon": [f["Longitude"]]}), zoom=9, height=220)
        pdf = report.valuation_pdf(f, price, last["explanation"], last["ref"], tier(price))
        st.download_button("📄  Download PDF report", pdf, f"{last['ref']}.pdf", "application/pdf",
                           type="primary", width="stretch")
    else:
        ui.empty_state("📊", "No valuation yet",
                       "Fill in the property details or choose a preset, then click <b>Generate valuation</b>.")

# ---------------------------------------------------------------- insights
if last:
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔍  Why this price?", "🎛️  What-if simulator"])

    with tab1:
        exp = last["explanation"]
        if not exp:
            st.info("Explanations are not available for this model.")
        else:
            st.caption(f"The average property starts at **{ui.money(exp['base_value_usd'])}**. "
                       "Each bar shows how much a factor moved this estimate up (green) or down (red).")
            df = pd.DataFrame(exp["contributions"])
            df["Factor"] = df["feature"].map(lambda k: ui.FEATURES[k][1])
            df["Impact"] = df["impact_usd"].map(ui.convert)
            df["Label"] = df["impact_usd"].map(lambda v: ("+" if v >= 0 else "−") + ui.money(abs(v)))
            df["Direction"] = df["impact_usd"].map(lambda v: "Raises value" if v >= 0 else "Lowers value")
            chart = (
                alt.Chart(df).mark_bar(cornerRadius=4, height=22)
                .encode(
                    x=alt.X("Impact:Q", title=f"Impact on value ({st.session_state.currency})"),
                    y=alt.Y("Factor:N", sort=alt.EncodingSortField("Impact", op="sum", order="descending"), title=None),
                    color=alt.Color("Direction:N", scale=alt.Scale(domain=["Raises value", "Lowers value"],
                                                                   range=["#16A34A", "#DC2626"]),
                                    legend=alt.Legend(orient="top", title=None)),
                    tooltip=["Factor", "Label", alt.Tooltip("value:Q", title="Input value")],
                ).properties(height=330)
            )
            st.altair_chart(chart, width="stretch")

    with tab2:
        st.caption("Pick one factor, keep everything else the same, and see how the value would change. "
                   "Simulations are not saved to the database.")
        c1, c2 = st.columns([1.2, 1])
        key = c1.selectbox("Factor to simulate", ui.FEATURE_KEYS, format_func=lambda k: ui.FEATURES[k][0])
        spread = c2.slider("Range around current value", 10, 100, 50, step=10, format="±%d%%")
        base = last["features"][key]
        _, _, _, lo_lim, hi_lim, _ = ui.FEATURES[key]
        if key in ("Latitude", "Longitude"):
            lo, hi = base - spread / 50, base + spread / 50
        elif base == 0:
            lo, hi = 0.0, 10.0
        else:
            lo, hi = base * (1 - spread / 100), base * (1 + spread / 100)
        lo, hi = max(lo, lo_lim), min(hi, hi_lim)
        points = [lo + (hi - lo) * i / 20 for i in range(21)]
        items = [{**last["features"], key: v} for v in points]
        preds, err = ui.api_post("/predict/preview", {"items": items})
        if err:
            st.error(err)
        else:
            sim = pd.DataFrame({ui.FEATURES[key][1]: points,
                                "Value": [ui.convert(p["estimated_price_usd"]) for p in preds]})
            x = ui.FEATURES[key][1]
            line = alt.Chart(sim).mark_area(
                line={"color": ui.GOLD, "strokeWidth": 3},
                color=alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                                   stops=[alt.GradientStop(color="rgba(201,162,39,0.02)", offset=0),
                                          alt.GradientStop(color="rgba(201,162,39,0.35)", offset=1)]),
            ).encode(x=alt.X(f"{x}:Q", title=x),
                     y=alt.Y("Value:Q", title=f"Estimated value ({st.session_state.currency})",
                             scale=alt.Scale(zero=False)),
                     tooltip=[alt.Tooltip(f"{x}:Q", format=".2f"), alt.Tooltip("Value:Q", format=",.0f")])
            now = alt.Chart(pd.DataFrame({x: [base], "Value": [ui.convert(last["price"])]})).mark_point(
                size=160, filled=True, color=ui.NAVY).encode(x=f"{x}:Q", y="Value:Q")
            st.altair_chart((line + now).properties(height=320), width="stretch")
            vals = [p["estimated_price_usd"] for p in preds]
            ui.kpis([("Current value", ui.money(last["price"])), ("Lowest in range", ui.money(min(vals))),
                     ("Highest in range", ui.money(max(vals))),
                     ("Potential upside", ui.money(max(vals) - last["price"]))])
