import altair as alt
import pandas as pd
import streamlit as st

import ui

ui.page_title("Insights", "Analytics dashboard",
              "Live view of every valuation saved in SQL Server — trends, distribution and locations.")

c1, c2, _ = st.columns([1, 1, 3])
limit = c1.selectbox("Records to load", [100, 500, 1000, 5000], index=1)
if c2.button("🔄  Refresh", width="stretch"):
    st.rerun()

stats, err = ui.api_get("/predict/stats")
if err:
    st.error(err)
    st.stop()
history, err = ui.api_get("/predict/history", {"limit": limit})
if err:
    st.error(err)
    st.stop()

if not history:
    ui.empty_state("🗄️", "No valuations saved yet",
                   "Run your first valuation and it will appear here automatically.")
    st.page_link("views/valuate.py", label="Go to Instant Valuation", icon="💎")
    st.stop()

df = pd.DataFrame(history)
df["created_at"] = pd.to_datetime(df["created_at"])
df["Value"] = df["estimated_price_usd"].map(ui.convert)

ui.kpis([("Total valuations", f"{stats['total']:,}"), ("Average value", ui.money(stats["average_usd"])),
         ("Lowest value", ui.money(stats["min_usd"])), ("Highest value", ui.money(stats["max_usd"]))])

cur = st.session_state.currency
tab1, tab2, tab3, tab4 = st.tabs(["📈  Trend", "📊  Distribution", "🗺️  Locations", "🗂️  Records"])

with tab1:
    trend = df.sort_values("created_at")
    trend["Rolling average"] = trend["Value"].rolling(10, min_periods=1).mean()
    base = alt.Chart(trend).encode(x=alt.X("created_at:T", title=None))
    pts = base.mark_circle(size=55, color=ui.NAVY2, opacity=.55).encode(
        y=alt.Y("Value:Q", title=f"Estimated value ({cur})"),
        tooltip=[alt.Tooltip("created_at:T", title="Time"), alt.Tooltip("Value:Q", format=",.0f")])
    avg_line = base.mark_line(color=ui.GOLD, strokeWidth=3).encode(y="Rolling average:Q")
    st.altair_chart((pts + avg_line).properties(height=330), width="stretch")
    st.caption("Dots = individual valuations · gold line = 10-valuation rolling average.")

with tab2:
    c1, c2 = st.columns(2)
    hist = alt.Chart(df).mark_bar(color=ui.GOLD, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Value:Q", bin=alt.Bin(maxbins=20), title=f"Estimated value ({cur})"),
        y=alt.Y("count()", title="Valuations")).properties(height=300, title="Value distribution")
    c1.altair_chart(hist, width="stretch")
    scatter = alt.Chart(df).mark_circle(size=60, opacity=.6).encode(
        x=alt.X("MedInc:Q", title="Median income ($10k)"),
        y=alt.Y("Value:Q", title=f"Value ({cur})"),
        color=alt.Color("HouseAge:Q", scale=alt.Scale(scheme="goldorange"), title="House age"),
        tooltip=["MedInc", "HouseAge", alt.Tooltip("Value:Q", format=",.0f")],
    ).properties(height=300, title="Income vs value")
    c2.altair_chart(scatter, width="stretch")

with tab3:
    st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}), size=800, color="#C9A227")

with tab4:
    show = df[["id", "created_at", "estimated_price_usd", *ui.FEATURE_KEYS]].rename(
        columns={"created_at": "Saved at", "estimated_price_usd": "Value (USD)"})
    st.dataframe(show, width="stretch", hide_index=True,
                 column_config={"Value (USD)": st.column_config.NumberColumn(format="$%d")})
    st.download_button("⬇  Export CSV", show.to_csv(index=False).encode(), "estateiq_history.csv", "text/csv")
