import altair as alt
import pandas as pd
import streamlit as st

import report
import ui

ui.page_title("Valuation tools", "Compare properties side by side",
              "Value two or three properties at once and see which one offers the most — with a shareable PDF.")

count = st.radio("Number of properties", [2, 3], horizontal=True, index=1)
start = list(ui.PRESETS)
cols = st.columns(count, gap="medium")
names = []

for i, col in enumerate(cols):
    prefix = f"c{i}_"
    ui.ensure_inputs(prefix, ui.PRESETS[start[i]])
    st.session_state.setdefault(f"cmp_preset_{i}", start[i])

    def apply(i=i, prefix=prefix):
        name = st.session_state[f"cmp_preset_{i}"]
        if name in ui.PRESETS:
            ui.set_inputs(prefix, ui.PRESETS[name])

    with col:
        st.markdown(f'<div class="card-title">Property {chr(65 + i)}</div>', unsafe_allow_html=True)
        st.selectbox("Preset", ["Custom", *ui.PRESETS], key=f"cmp_preset_{i}", on_change=apply,
                     label_visibility="collapsed")
        with st.expander("Edit details", expanded=False):
            for k in ui.FEATURE_KEYS:
                ui.number_input(st, prefix, k)
        preset = st.session_state[f"cmp_preset_{i}"]
        names.append(preset if preset != "Custom" else f"Custom property {chr(65 + i)}")

if st.button("Compare properties  →", type="primary"):
    feats = [ui.read_inputs(f"c{i}_") for i in range(count)]
    with st.spinner("Valuing properties…"):
        preds, err = ui.api_post("/predict/preview", {"items": feats})
    if err:
        st.error(err)
    else:
        st.session_state.comparison = dict(names=names, features=feats,
                                           prices=[p["estimated_price_usd"] for p in preds])

cmp = st.session_state.get("comparison")
if cmp and len(cmp["names"]) == count:
    prices, feats, labels = cmp["prices"], cmp["features"], cmp["names"]
    best = max(range(count), key=lambda i: prices[i])
    st.markdown("<br>", unsafe_allow_html=True)
    cards = st.columns(count)
    for i, c in enumerate(cards):
        badge = "🏆 Highest value" if i == best else ("Lowest value" if prices[i] == min(prices) else "")
        diff = prices[i] - prices[best]
        c.markdown(
            f'<div class="mini {"best" if i == best else ""}"><small>Property {chr(65 + i)}</small>'
            f'<b>{ui.money(prices[i])}</b><div style="font-size:.82rem;color:#64748B;">{labels[i]}</div>'
            f'<div style="font-size:.8rem;margin-top:.4rem;font-weight:600;color:{"#C9A227" if i == best else "#DC2626"}">'
            f'{badge if i == best else ui.money(diff) + " vs best"}</div></div>',
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        df = pd.DataFrame({"Property": [f"Property {chr(65 + i)}" for i in range(count)],
                           "Value": [ui.convert(p) for p in prices]})
        chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=60).encode(
            x=alt.X("Property:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Value:Q", title=f"Estimated value ({st.session_state.currency})"),
            color=alt.condition(alt.datum.Property == f"Property {chr(65 + best)}",
                                alt.value(ui.GOLD), alt.value(ui.NAVY2)),
            tooltip=["Property", alt.Tooltip("Value:Q", format=",.0f")],
        ).properties(height=320)
        st.altair_chart(chart, width="stretch")
    with c2:
        table = pd.DataFrame(
            {f"Property {chr(65 + i)}": [ui.money(prices[i])] + [f[k] for k in ui.FEATURE_KEYS]
             for i, f in enumerate(feats)},
            index=["Estimated value"] + [ui.FEATURES[k][1] for k in ui.FEATURE_KEYS],
        ).astype(str)
        st.dataframe(table, width="stretch", height=350)

    pdf = report.comparison_pdf(labels, feats, prices)
    st.download_button("📄  Download comparison PDF", pdf, "EstateIQ-comparison.pdf", "application/pdf",
                       type="primary")
