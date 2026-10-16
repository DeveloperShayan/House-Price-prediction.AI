"""Shared look & feel, header/footer, settings and API helpers used by every page."""
from datetime import datetime

import requests
import streamlit as st

# ============================================================== settings
API_BASE = "http://127.0.0.1:8000"

BRAND = "EstateIQ"
DEV_NAME = "Shayan Niaz"
DEV_TITLE = "Software Engineer"
DEV_LINKEDIN = "https://www.linkedin.com/in/shayan-niaz-301054227/"

NAVY, NAVY2, GOLD, GOLD2 = "#0B1B33", "#13294B", "#C9A227", "#E4C766"

LINKEDIN_ICON = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41'
    'v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 '
    '2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 '
    '24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>'
)

# ============================================================== model features
# key: (label, short name, step, min, max, help)
FEATURES = {
    "MedInc":     ("Median income ($10k units)", "Income", 0.1, 0.0, 20.0,
                   "Median household income of the block. 5.0 = $50,000."),
    "HouseAge":   ("House age (years)", "House age", 1.0, 0.0, 100.0, "Median age of houses in the block."),
    "AveRooms":   ("Average rooms", "Rooms", 0.1, 0.0, 50.0, "Average number of rooms per household."),
    "AveBedrms":  ("Average bedrooms", "Bedrooms", 0.1, 0.0, 20.0, "Average number of bedrooms per household."),
    "Population": ("Block population", "Population", 10.0, 0.0, 50000.0, "People living in the block group."),
    "AveOccup":   ("Average occupancy", "Occupancy", 0.1, 0.0, 20.0, "Average number of people per household."),
    "Latitude":   ("Latitude", "Latitude", 0.01, -90.0, 90.0, "North-south position."),
    "Longitude":  ("Longitude", "Longitude", 0.01, -180.0, 180.0, "East-west position."),
}
FEATURE_KEYS = list(FEATURES)

PRESETS = {
    "Los Angeles · Suburban family home": dict(MedInc=5.0, HouseAge=20.0, AveRooms=6.0, AveBedrms=1.0,
                                                Population=1000.0, AveOccup=3.0, Latitude=34.05, Longitude=-118.25),
    "San Francisco · Premium district": dict(MedInc=8.3, HouseAge=41.0, AveRooms=7.0, AveBedrms=1.0,
                                             Population=320.0, AveOccup=2.5, Latitude=37.79, Longitude=-122.42),
    "San Diego · Coastal residence": dict(MedInc=6.5, HouseAge=15.0, AveRooms=6.5, AveBedrms=1.0,
                                          Population=900.0, AveOccup=2.8, Latitude=32.72, Longitude=-117.16),
    "San Jose · Tech corridor": dict(MedInc=9.5, HouseAge=25.0, AveRooms=6.8, AveBedrms=1.05,
                                     Population=1200.0, AveOccup=3.0, Latitude=37.34, Longitude=-121.89),
    "Sacramento · Starter home": dict(MedInc=3.2, HouseAge=30.0, AveRooms=5.0, AveBedrms=1.1,
                                      Population=1400.0, AveOccup=3.1, Latitude=38.58, Longitude=-121.49),
    "Fresno · Affordable inland": dict(MedInc=2.5, HouseAge=35.0, AveRooms=5.2, AveBedrms=1.1,
                                       Population=1600.0, AveOccup=3.4, Latitude=36.74, Longitude=-119.79),
}
DEFAULTS = PRESETS["Los Angeles · Suburban family home"]


# ============================================================== state & formatting
def init_state():
    st.session_state.setdefault("currency", "USD")
    st.session_state.setdefault("pkr_rate", 280.0)


def convert(usd: float) -> float:
    return usd * st.session_state.pkr_rate if st.session_state.currency == "PKR" else usd


def money(usd, short: bool = False) -> str:
    if usd is None:
        return "—"
    v = convert(float(usd))
    sym = "Rs " if st.session_state.currency == "PKR" else "$"
    if short:
        for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(v) >= div:
                return f"{sym}{v / div:,.1f}{suf}"
    return f"{sym}{v:,.0f}"


def money_plain(usd: float) -> str:
    """PDF-safe (ASCII) version of money()."""
    return money(usd).replace("—", "-")


# ============================================================== API
def _friendly(error: Exception) -> str:
    if isinstance(error, requests.exceptions.ConnectionError):
        return "Cannot reach the prediction engine. Start the backend: python -m uvicorn app.main:app --reload"
    if isinstance(error, requests.exceptions.Timeout):
        return "The request timed out. Please try again."
    if isinstance(error, requests.exceptions.HTTPError):
        return ("The server could not complete the request (status "
                f"{error.response.status_code}). Check the backend terminal — usually a database issue.")
    return f"Unexpected error: {error}"


def api_get(path: str, params: dict | None = None):
    try:
        r = requests.get(API_BASE + path, params=params, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:  # noqa: BLE001
        return None, _friendly(e)


def api_post(path: str, payload):
    try:
        r = requests.post(API_BASE + path, json=payload, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:  # noqa: BLE001
        return None, _friendly(e)


@st.cache_data(ttl=10, show_spinner=False)
def api_online() -> bool:
    try:
        return requests.get(API_BASE + "/", timeout=2).ok
    except requests.exceptions.RequestException:
        return False


# ============================================================== form helpers
def ensure_inputs(prefix: str, values: dict | None = None):
    for k, v in (values or DEFAULTS).items():
        st.session_state.setdefault(prefix + k, float(v))


def set_inputs(prefix: str, values: dict):
    for k, v in values.items():
        st.session_state[prefix + k] = float(v)


def read_inputs(prefix: str) -> dict:
    return {k: float(st.session_state[prefix + k]) for k in FEATURE_KEYS}


def number_input(container, prefix: str, key: str):
    label, _, step, lo, hi, help_ = FEATURES[key]
    fmt = "%.2f" if key in ("Latitude", "Longitude") else None
    container.number_input(label, min_value=lo, max_value=hi, step=step,
                           key=prefix + key, help=help_, format=fmt)


# ============================================================== layout pieces
def navbar():
    st.markdown(
        f"""
<div class="navbar">
  <div class="nav-brand"><div class="nav-logo">🏛️</div>
    <div><div class="nav-title">Estate<span>IQ</span></div><div class="nav-tag">AI Property Valuation</div></div>
  </div>
  <div class="nav-dev">
    <div class="nav-dev-text"><b>{DEV_NAME}</b><span>{DEV_TITLE}</span></div>
    <a class="btn-in" href="{DEV_LINKEDIN}" target="_blank" rel="noopener">{LINKEDIN_ICON} LinkedIn</a>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def page_title(kicker: str, title: str, subtitle: str):
    st.markdown(
        f'<div class="page-head"><span class="kicker">{kicker}</span><h2>{title}</h2><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def kpis(items: list[tuple[str, str]]):
    tiles = "".join(f'<div class="kpi"><span>{a}</span><b>{b}</b></div>' for a, b in items)
    st.markdown(f'<div class="kpis">{tiles}</div>', unsafe_allow_html=True)


def empty_state(icon: str, title: str, text: str):
    st.markdown(
        f'<div class="empty"><div class="big">{icon}</div>'
        f'<p style="font-weight:600;color:#0F172A;margin:.4rem 0 .2rem;">{title}</p>'
        f'<p style="margin:0;font-size:.88rem;">{text}</p></div>',
        unsafe_allow_html=True,
    )


def sidebar():
    with st.sidebar:
        online = api_online()
        st.markdown(
            f'<div class="status"><div class="dot {"ok" if online else "bad"}"></div>'
            f'Prediction engine {"online" if online else "offline"}</div>',
            unsafe_allow_html=True,
        )
        if not online:
            st.caption("Start the backend: `python -m uvicorn app.main:app --reload`")

        st.markdown('<div class="side-label">Display currency</div>', unsafe_allow_html=True)
        st.radio("Currency", ["USD", "PKR"], key="currency", horizontal=True, label_visibility="collapsed")
        if st.session_state.currency == "PKR":
            st.number_input("PKR per 1 USD (set today's rate)", min_value=1.0, step=1.0, key="pkr_rate")

        st.markdown(
            f'<div class="dev-card"><span>Developed by</span><b>{DEV_NAME}</b><span>{DEV_TITLE}</span><br>'
            f'<a href="{DEV_LINKEDIN}" target="_blank" rel="noopener">{LINKEDIN_ICON} Connect on LinkedIn</a></div>',
            unsafe_allow_html=True,
        )


def footer():
    year = datetime.now().year
    st.markdown(
        f"""
<div class="site-footer">
  <div class="foot-grid">
    <div>
      <div class="foot-brand">Estate<span>IQ</span></div>
      <p>AI-powered property valuation platform. Instant estimates, transparent value drivers,
         portfolio analysis and professional reports — every valuation securely recorded.</p>
    </div>
    <div>
      <h4>Platform</h4>
      <ul><li>Instant valuation</li><li>Compare properties</li><li>Batch valuation</li>
          <li>Analytics dashboard</li><li>PDF reports</li></ul>
    </div>
    <div>
      <h4>Technology</h4>
      <ul><li>LightGBM · Scikit-Learn</li><li>FastAPI REST backend</li>
          <li>Microsoft SQL Server</li><li>Streamlit interface</li></ul>
    </div>
    <div>
      <h4>Developer</h4>
      <p><b style="color:#fff;font-size:1rem;">{DEV_NAME}</b></p>
      <p>{DEV_TITLE}</p>
      <a class="btn-in" href="{DEV_LINKEDIN}" target="_blank" rel="noopener">{LINKEDIN_ICON} Connect on LinkedIn</a>
    </div>
  </div>
  <div class="foot-bottom">
    <span>© {year} {BRAND} · Designed &amp; developed by
      <a href="{DEV_LINKEDIN}" target="_blank" rel="noopener">{DEV_NAME}</a></span>
    <span>Estimates use the California Housing dataset and are for demonstration only, not a formal appraisal.</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================== CSS
def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
  --navy:#0B1B33; --navy-2:#13294B; --gold:#C9A227; --gold-2:#E4C766;
  --ink:#0F172A; --muted:#64748B; --line:#E2E8F0; --card:#FFFFFF; --bg:#F5F7FB;
  --ok:#16A34A; --bad:#DC2626;
}
html, body, [class*="css"], .stApp { font-family:'Inter', sans-serif !important; }
span[data-testid="stIconMaterial"], .material-symbols-rounded{ font-family:'Material Symbols Rounded' !important; }
.stApp { background:var(--bg); }
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stAppDeployButton"],
[data-testid="stToolbarActions"], [data-testid="stStatusWidget"] { display:none !important; }
header[data-testid="stHeader"]{ background:transparent !important; box-shadow:none !important; }
.block-container { padding-top:3.2rem; padding-bottom:0; max-width:1280px; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] { background:linear-gradient(180deg,var(--navy) 0%,var(--navy-2) 100%); }
section[data-testid="stSidebar"] * { color:#E2E8F0 !important; }
section[data-testid="stSidebar"] input{ color:var(--ink) !important; }
[data-testid="stSidebarNav"] a, [data-testid="stSidebarNavLink"]{ border-radius:10px; }
[data-testid="stSidebarNavLink"][aria-current="page"], [data-testid="stSidebarNav"] a[aria-current="page"]{
  background:rgba(201,162,39,.18) !important; border-left:3px solid var(--gold); }
[data-testid="stSidebarNavLink"]:hover{ background:rgba(255,255,255,.08) !important; }
[data-testid="stNavSectionHeader"]{ opacity:.6; text-transform:uppercase; letter-spacing:.12em; font-size:.7rem !important; }
.side-label{ font-size:.72rem; text-transform:uppercase; letter-spacing:.12em; opacity:.6; margin:1.2rem 0 .5rem; }
.status{ display:flex; align-items:center; gap:.5rem; padding:.6rem .8rem; border-radius:10px;
  background:rgba(255,255,255,.06); font-size:.85rem; }
.dot{ width:9px; height:9px; border-radius:50%; }
.dot.ok{ background:var(--ok); box-shadow:0 0 0 4px rgba(22,163,74,.25); }
.dot.bad{ background:var(--bad); box-shadow:0 0 0 4px rgba(220,38,38,.25); }
.dev-card{ margin-top:1.4rem; padding:1rem; border-radius:12px; background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.12); }
.dev-card b{ display:block; font-size:.95rem; }
.dev-card span{ font-size:.78rem; opacity:.75; }
.dev-card a{ display:inline-flex; align-items:center; gap:.4rem; margin-top:.7rem; padding:.4rem .7rem;
  border-radius:8px; background:#0A66C2; color:#fff !important; font-size:.8rem; font-weight:600; text-decoration:none !important; }

/* Sidebar open / close buttons with clear labels */
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"]{
  visibility:visible !important; display:flex !important; z-index:1000; }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button, [data-testid="collapsedControl"] button{
  background:var(--navy) !important; border-radius:10px !important; border:1px solid rgba(201,162,39,.5) !important;
  box-shadow:0 6px 16px -6px rgba(11,27,51,.6); width:auto !important; height:auto !important; min-height:0 !important;
  padding:.5rem .95rem !important; margin:.4rem 0 0 .4rem; cursor:pointer; }
[data-testid="stExpandSidebarButton"] > *, [data-testid="stSidebarCollapsedControl"] button > *,
[data-testid="collapsedControl"] button > *{ display:none !important; }
[data-testid="stExpandSidebarButton"]::after, [data-testid="stSidebarCollapsedControl"] button::after,
[data-testid="collapsedControl"] button::after{
  content:"☰  Menu"; white-space:pre; color:var(--gold-2); font:600 .9rem 'Inter', sans-serif; }
[data-testid="stSidebarCollapseButton"]{ visibility:visible !important; opacity:1 !important; display:block !important; }
[data-testid="stSidebarCollapseButton"] button{ width:auto !important; height:auto !important; padding:.35rem .75rem !important;
  border:1px solid rgba(255,255,255,.2) !important; border-radius:8px !important; background:rgba(255,255,255,.06) !important; }
[data-testid="stSidebarCollapseButton"] button > *{ display:none !important; }
[data-testid="stSidebarCollapseButton"] button::after{ content:"✕  Close"; white-space:pre; color:#E2E8F0; font:500 .8rem 'Inter', sans-serif; }

/* ---------- Navbar ---------- */
.navbar{ display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;
  background:#fff; border:1px solid var(--line); border-radius:16px; padding:.75rem 1.2rem;
  box-shadow:0 8px 24px -16px rgba(15,23,42,.25); margin-bottom:1.4rem; }
.nav-brand{ display:flex; align-items:center; gap:.7rem; }
.nav-logo{ width:40px; height:40px; border-radius:11px; display:grid; place-items:center;
  background:linear-gradient(135deg,var(--navy),var(--navy-2)); font-size:1.2rem; }
.nav-title{ font-weight:800; font-size:1.2rem; letter-spacing:-.02em; color:var(--ink); line-height:1.1; }
.nav-title span{ color:var(--gold); }
.nav-tag{ font-size:.72rem; color:var(--muted); letter-spacing:.04em; }
.nav-dev{ display:flex; align-items:center; gap:.7rem; }
.nav-dev-text{ text-align:right; line-height:1.2; }
.nav-dev-text b{ display:block; font-size:.88rem; color:var(--ink); }
.nav-dev-text span{ font-size:.75rem; color:var(--muted); }
.btn-in{ display:inline-flex; align-items:center; gap:.4rem; padding:.45rem .8rem; border-radius:9px;
  background:#0A66C2; color:#fff !important; text-decoration:none !important; font-size:.82rem; font-weight:600; }
.btn-in:hover{ background:#004182; }

/* ---------- Page head ---------- */
.page-head{ margin:.2rem 0 1.2rem; }
.page-head .kicker{ font-size:.72rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--gold); }
.page-head h2{ font-size:clamp(1.4rem,2.6vw,2rem); font-weight:800; letter-spacing:-.03em; color:var(--ink); margin:.2rem 0 .3rem; padding:0; }
.page-head p{ color:var(--muted); margin:0; max-width:760px; }

/* ---------- Hero (home) ---------- */
.hero{ position:relative; overflow:hidden; border-radius:24px; padding:3rem 2.6rem;
  background:radial-gradient(900px 400px at 95% -10%, rgba(201,162,39,.4), transparent 60%),
             radial-gradient(600px 300px at -10% 120%, rgba(56,97,166,.45), transparent 60%),
             linear-gradient(135deg,var(--navy) 0%,var(--navy-2) 100%);
  color:#fff; box-shadow:0 30px 60px -30px rgba(11,27,51,.7); margin-bottom:1rem; }
.hero-badge{ display:inline-block; font-size:.72rem; font-weight:600; letter-spacing:.14em; text-transform:uppercase;
  color:var(--gold-2); border:1px solid rgba(228,199,102,.4); padding:.3rem .8rem; border-radius:999px; }
.hero h1{ font-size:clamp(1.9rem,4.2vw,3.3rem); font-weight:800; letter-spacing:-.035em; line-height:1.08;
  margin:1rem 0 .8rem; color:#fff; max-width:780px; padding:0; }
.hero h1 em{ font-style:normal; color:var(--gold-2); }
.hero p{ color:#CBD5E1; font-size:clamp(.95rem,1.5vw,1.12rem); max-width:640px; margin:0; }
.hero-stats{ display:flex; flex-wrap:wrap; gap:2.4rem; margin-top:2rem; }
.hero-stat b{ display:block; font-size:1.6rem; color:var(--gold-2); }
.hero-stat span{ font-size:.8rem; color:#94A3B8; }

.section-title{ text-align:center; margin:2.6rem 0 1.4rem; }
.section-title .kicker{ font-size:.72rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--gold); }
.section-title h3{ font-size:clamp(1.3rem,2.4vw,1.9rem); font-weight:800; letter-spacing:-.02em; color:var(--ink); margin:.3rem 0; padding:0; }
.section-title p{ color:var(--muted); max-width:620px; margin:0 auto; }

.grid{ display:grid; gap:1rem; }
.grid-3{ grid-template-columns:repeat(3,minmax(0,1fr)); }
.grid-4{ grid-template-columns:repeat(4,minmax(0,1fr)); }
.feature{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:1.4rem;
  box-shadow:0 8px 24px -16px rgba(15,23,42,.18); transition:transform .2s, box-shadow .2s; }
.feature:hover{ transform:translateY(-3px); box-shadow:0 18px 36px -18px rgba(15,23,42,.3); }
.feature .ico{ width:44px; height:44px; border-radius:12px; display:grid; place-items:center; font-size:1.3rem;
  background:linear-gradient(135deg,#FEF7E0,#FDEFC2); margin-bottom:.9rem; }
.feature h4{ font-size:1rem; font-weight:700; color:var(--ink); margin:0 0 .35rem; padding:0; }
.feature p{ font-size:.87rem; color:var(--muted); margin:0; }
.step{ position:relative; background:#fff; border:1px solid var(--line); border-radius:18px; padding:1.6rem 1.4rem 1.4rem; }
.step .num{ width:34px; height:34px; border-radius:50%; display:grid; place-items:center; font-weight:800;
  color:var(--navy); background:linear-gradient(135deg,var(--gold),var(--gold-2)); margin-bottom:.8rem; }
.step h4{ font-size:1rem; font-weight:700; color:var(--ink); margin:0 0 .3rem; padding:0; }
.step p{ font-size:.87rem; color:var(--muted); margin:0; }
.cta-band{ border-radius:22px; padding:2.2rem; text-align:center; color:#fff; margin:2.6rem 0 1rem;
  background:linear-gradient(135deg,#B8901B 0%,var(--gold) 45%,var(--gold-2) 100%); }
.cta-band h3{ color:var(--navy); font-size:clamp(1.3rem,2.6vw,1.9rem); font-weight:800; margin:0 0 .4rem; padding:0; }
.cta-band p{ color:#3B2F0B; margin:0; }

/* ---------- Cards / form ---------- */
.card{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1.3rem 1.4rem;
  box-shadow:0 8px 24px -14px rgba(15,23,42,.12); margin-bottom:1rem; }
.card-title{ font-size:1rem; font-weight:700; color:var(--ink); margin:0 0 .2rem; }
.card-sub{ font-size:.82rem; color:var(--muted); margin:0 0 .4rem; }
.section-head{ display:flex; align-items:center; gap:.5rem; font-weight:700; color:var(--ink); font-size:.95rem; margin:.5rem 0 .2rem; }
.section-head .ico{ width:28px; height:28px; border-radius:8px; display:grid; place-items:center; background:#FEF7E0; font-size:.95rem; }
div[data-testid="stForm"]{ background:var(--card); border:1px solid var(--line); border-radius:16px;
  padding:1.4rem 1.5rem; box-shadow:0 8px 24px -12px rgba(15,23,42,.08); }
.stNumberInput label p{ font-weight:500 !important; color:#334155 !important; font-size:.85rem !important; }
.stNumberInput input{ border-radius:10px !important; }
div[data-testid="stFormSubmitButton"]>button, .stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"]{
  width:100%; padding:.75rem 1rem; border:none !important; border-radius:12px; font-weight:700;
  color:var(--navy) !important; background:linear-gradient(135deg,var(--gold),var(--gold-2)) !important;
  box-shadow:0 10px 20px -10px rgba(201,162,39,.8); transition:transform .15s; }
div[data-testid="stFormSubmitButton"]>button:hover, .stButton>button[kind="primary"]:hover,
.stDownloadButton>button[kind="primary"]:hover{ transform:translateY(-1px); }
[data-testid="stPageLink"] a{ border-radius:12px; }

/* Result */
.result{ border-radius:18px; padding:1.7rem; color:#fff;
  background:linear-gradient(135deg,#0B1B33 0%,#1E3A66 100%); box-shadow:0 20px 40px -20px rgba(11,27,51,.7); }
.result small{ color:#94A3B8; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:600; }
.result .price{ font-size:clamp(2rem,4.5vw,3rem); font-weight:800; letter-spacing:-.03em; color:var(--gold-2); margin:.3rem 0; }
.result .meta{ color:#CBD5E1; font-size:.88rem; }
.result .range{ margin-top:.7rem; font-size:.85rem; color:#CBD5E1; }
.pill{ display:inline-block; padding:.25rem .65rem; border-radius:999px; font-size:.75rem; font-weight:600;
  background:rgba(22,163,74,.15); color:#4ADE80; margin-top:.8rem; }
.tier{ display:inline-block; padding:.25rem .65rem; border-radius:999px; font-size:.75rem; font-weight:700;
  background:rgba(228,199,102,.15); color:var(--gold-2); margin:.8rem 0 0 .4rem; }
.mini{ border-radius:16px; padding:1.2rem; background:#fff; border:1px solid var(--line); text-align:center; }
.mini.best{ border:2px solid var(--gold); box-shadow:0 12px 26px -14px rgba(201,162,39,.7); }
.mini small{ color:var(--muted); font-size:.75rem; font-weight:600; text-transform:uppercase; letter-spacing:.08em; }
.mini b{ display:block; font-size:1.6rem; color:var(--ink); margin:.2rem 0; }
.empty{ border:2px dashed var(--line); border-radius:18px; padding:2.4rem 1.5rem; text-align:center; color:var(--muted); background:#fff; }
.empty .big{ font-size:2.4rem; }
.kpis{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; margin:1rem 0; }
.kpi{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem; }
.kpi span{ font-size:.75rem; color:var(--muted); font-weight:500; }
.kpi b{ display:block; font-size:1.2rem; color:var(--ink); margin-top:.2rem; }
.stTabs [data-baseweb="tab-list"]{ gap:.4rem; flex-wrap:wrap; }
.stTabs [data-baseweb="tab"]{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:.5rem 1rem; }
.stTabs [aria-selected="true"]{ border-color:var(--gold) !important; background:#FFFBEB !important; }
[data-testid="stExpander"]{ background:#fff; border-radius:12px; }

/* ---------- Footer ---------- */
.site-footer{ margin-top:3rem; border-radius:22px 22px 0 0; padding:2.4rem 2.4rem 1.2rem;
  background:linear-gradient(135deg,var(--navy) 0%,var(--navy-2) 100%); color:#CBD5E1; }
.foot-grid{ display:grid; grid-template-columns:1.6fr 1fr 1fr 1.2fr; gap:2rem; }
.foot-grid h4{ color:#fff; font-size:.8rem; text-transform:uppercase; letter-spacing:.12em; margin:0 0 .8rem; padding:0; }
.foot-grid p, .foot-grid li{ font-size:.86rem; margin:0 0 .4rem; color:#CBD5E1; }
.foot-grid ul{ list-style:none; padding:0; margin:0; }
.foot-brand{ font-weight:800; font-size:1.3rem; color:#fff; margin-bottom:.5rem; }
.foot-brand span{ color:var(--gold-2); }
.foot-bottom{ border-top:1px solid rgba(255,255,255,.1); margin-top:1.8rem; padding-top:1rem;
  display:flex; justify-content:space-between; flex-wrap:wrap; gap:.6rem; font-size:.78rem; color:#94A3B8; }
.foot-bottom a{ color:var(--gold-2) !important; text-decoration:none !important; }

/* ---------- Responsive ---------- */
@media (max-width: 1000px){
  .grid-4{ grid-template-columns:repeat(2,minmax(0,1fr)); }
  .foot-grid{ grid-template-columns:1fr 1fr; }
}
@media (max-width: 900px){
  .kpis{ grid-template-columns:repeat(2,minmax(0,1fr)); }
  .grid-3{ grid-template-columns:1fr; }
  .hero{ padding:2rem 1.5rem; }
  .hero-stats{ gap:1.4rem; }
}
@media (max-width: 640px){
  .block-container{ padding-left:.8rem; padding-right:.8rem; }
  div[data-testid="stForm"], .card, .result{ padding:1.1rem; }
  .grid-4, .foot-grid{ grid-template-columns:1fr; }
  .nav-dev-text{ display:none; }
  .site-footer{ padding:1.6rem 1.2rem 1rem; }
  .cta-band{ padding:1.5rem 1.1rem; }
}
</style>
"""
