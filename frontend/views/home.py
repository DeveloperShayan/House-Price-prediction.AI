import streamlit as st

import ui

stats, _ = ui.api_get("/predict/stats")
total = stats["total"] if stats else 0
avg = stats.get("average_usd") if stats else None

# ---------------------------------------------------------------- hero
st.markdown(
    f"""
<div class="hero">
  <span class="hero-badge">✦ AI-Powered Property Intelligence</span>
  <h1>Know what a property is worth — <em>in seconds</em>, not weeks.</h1>
  <p>EstateIQ turns neighbourhood data into instant, explainable valuations. Value a single home,
     compare options side by side, process whole portfolios and download investor-ready PDF reports.</p>
  <div class="hero-stats">
    <div class="hero-stat"><b>{total:,}</b><span>Valuations delivered</span></div>
    <div class="hero-stat"><b>{ui.money(avg, short=True) if avg else "—"}</b><span>Average estimate</span></div>
    <div class="hero-stat"><b>&lt; 1 sec</b><span>Time to valuation</span></div>
    <div class="hero-stat"><b>8</b><span>Market signals analysed</span></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, _ = st.columns([1.2, 1.2, 1.2, 2])
c1.page_link("views/valuate.py", label="Get a free valuation", icon="💎")
c2.page_link("views/compare.py", label="Compare properties", icon="⚖️")
c3.page_link("views/dashboard.py", label="View analytics", icon="📊")

# ---------------------------------------------------------------- features
st.markdown(
    """
<div class="section-title"><span class="kicker">Why EstateIQ</span>
  <h3>Everything you need to price property with confidence</h3>
  <p>One platform for buyers, sellers, agents and investors — from a quick estimate to a full portfolio review.</p>
</div>
<div class="grid grid-3">
  <div class="feature"><div class="ico">⚡</div><h4>Instant valuations</h4>
    <p>Enter eight neighbourhood signals and receive a market estimate in under a second.</p></div>
  <div class="feature"><div class="ico">🔍</div><h4>Explainable AI</h4>
    <p>See exactly which factors pushed the price up or down — no black-box numbers.</p></div>
  <div class="feature"><div class="ico">🎛️</div><h4>What-if simulator</h4>
    <p>Change income, age or location and watch the value respond in real time.</p></div>
  <div class="feature"><div class="ico">⚖️</div><h4>Side-by-side comparison</h4>
    <p>Compare up to three properties and instantly spot the best value.</p></div>
  <div class="feature"><div class="ico">📦</div><h4>Batch portfolio valuation</h4>
    <p>Upload a CSV with up to 1,000 properties and value them all in one click.</p></div>
  <div class="feature"><div class="ico">📄</div><h4>Branded PDF reports</h4>
    <p>Download polished, shareable valuation and comparison reports.</p></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- how it works
st.markdown(
    """
<div class="section-title"><span class="kicker">How it works</span>
  <h3>From data to decision in three steps</h3></div>
<div class="grid grid-3">
  <div class="step"><div class="num">1</div><h4>Describe the property</h4>
    <p>Enter the neighbourhood profile and location, or start from a ready-made market preset.</p></div>
  <div class="step"><div class="num">2</div><h4>AI does the analysis</h4>
    <p>A gradient-boosted model trained on 20,000+ real districts estimates the value and explains it.</p></div>
  <div class="step"><div class="num">3</div><h4>Act with confidence</h4>
    <p>Compare, simulate scenarios and export a professional PDF to share with clients or partners.</p></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- audiences
st.markdown(
    """
<div class="section-title"><span class="kicker">Built for</span>
  <h3>Professionals who need answers fast</h3></div>
<div class="grid grid-4">
  <div class="feature"><div class="ico">🏡</div><h4>Home buyers</h4><p>Check a fair price before you make an offer.</p></div>
  <div class="feature"><div class="ico">🤝</div><h4>Real-estate agents</h4><p>Back your listing price with data and a report.</p></div>
  <div class="feature"><div class="ico">📈</div><h4>Investors</h4><p>Screen whole portfolios and find undervalued areas.</p></div>
  <div class="feature"><div class="ico">🧮</div><h4>Analysts</h4><p>Track every valuation in a live SQL-backed dashboard.</p></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- FAQ
st.markdown('<div class="section-title"><span class="kicker">FAQ</span><h3>Common questions</h3></div>',
            unsafe_allow_html=True)
faq = {
    "How accurate are the valuations?":
        "The model explains roughly 85% of the price variation (R² ≈ 0.85) on held-out test data from the "
        "California Housing dataset. Treat results as a strong indicative estimate, not a formal appraisal.",
    "Can I use it for property in Pakistan?":
        "Not reliably. The model learned from California data. You can display results in PKR using your own "
        "exchange rate, but local prices depend on factors this model has never seen.",
    "Is my data stored?":
        "Single and batch valuations are saved to the SQL Server database so they appear in the analytics "
        "dashboard. What-if simulations and comparisons are not saved.",
    "What do I need for batch valuation?":
        "A CSV file with the eight feature columns. Download the ready-made template on the Batch Valuation page.",
}
for q, a in faq.items():
    with st.expander(q):
        st.write(a)

# ---------------------------------------------------------------- CTA
st.markdown(
    '<div class="cta-band"><h3>Ready to value your first property?</h3>'
    '<p>It is free, instant and takes less than a minute.</p></div>',
    unsafe_allow_html=True,
)
_, mid, _ = st.columns([2, 1.2, 2])
mid.page_link("views/valuate.py", label="Start valuation now →", icon="💎")
