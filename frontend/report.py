"""Branded PDF reports (valuation, comparison, portfolio) with the EstateIQ header & footer."""
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

import ui

NAVY = (11, 27, 51)
NAVY2 = (30, 58, 102)
GOLD = (201, 162, 39)
GOLD2 = (228, 199, 102)
INK = (15, 23, 42)
MUTED = (100, 116, 139)
LINE = (226, 232, 240)
SOFT = (245, 247, 251)
GREEN = (22, 163, 74)
RED = (220, 38, 38)

NL = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)
RIGHT = dict(new_x=XPos.RIGHT, new_y=YPos.TOP)


def _ascii(text: str) -> str:
    return (str(text).replace("—", "-").replace("–", "-").replace("·", "-")
            .replace("’", "'").replace("≈", "~").encode("latin-1", "ignore").decode("latin-1"))


class BrandedPDF(FPDF):
    def __init__(self, title: str):
        super().__init__(format="A4")
        self.report_title = title
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(16, 34, 16)
        self.alias_nb_pages()

    # -------------------------------------------------- header
    def header(self):
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 26, style="F")
        self.set_fill_color(*GOLD)
        self.rect(0, 26, 210, 1.4, style="F")
        # logo tile
        self.set_fill_color(*GOLD)
        self.rect(16, 7, 12, 12, style="F")
        self.set_xy(16, 7)
        self.set_text_color(*NAVY)
        self.set_font("Helvetica", "B", 13)
        self.cell(12, 12, "E", align="C")
        # brand
        self.set_xy(31, 7)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 16)
        self.cell(self.get_string_width("Estate") + 0.5, 7, "Estate", **RIGHT)
        self.set_text_color(*GOLD2)
        self.cell(10, 7, "IQ", **RIGHT)
        self.set_xy(31, 14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(203, 213, 225)
        self.cell(80, 5, "AI PROPERTY VALUATION PLATFORM")
        # developer
        self.set_xy(110, 7)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.cell(84, 6, _ascii(ui.DEV_NAME), align="R", **NL)
        self.set_x(110)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GOLD2)
        self.cell(84, 5, _ascii(f"{ui.DEV_TITLE}  |  LinkedIn"), align="R", link=ui.DEV_LINKEDIN)
        self.set_y(34)

    # -------------------------------------------------- footer
    def footer(self):
        self.set_y(-17)
        self.set_fill_color(*NAVY)
        self.rect(0, 297 - 17, 210, 17, style="F")
        self.set_fill_color(*GOLD)
        self.rect(0, 297 - 17, 210, 0.8, style="F")
        self.set_xy(16, -13)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(203, 213, 225)
        self.cell(120, 4, _ascii(f"(c) {datetime.now().year} {ui.BRAND}  |  Designed & developed by {ui.DEV_NAME}, "
                                 f"{ui.DEV_TITLE}"), link=ui.DEV_LINKEDIN)
        self.set_text_color(*GOLD2)
        self.cell(58, 4, f"Page {self.page_no()} of {{nb}}", align="R", **NL)
        self.set_x(16)
        self.set_text_color(148, 163, 184)
        self.cell(178, 4, _ascii("Indicative estimate for demonstration only - not a formal appraisal. "
                                 "Model trained on the California Housing dataset."))

    # -------------------------------------------------- building blocks
    def title_block(self, title: str, subtitle: str):
        self.set_text_color(*GOLD)
        self.set_font("Helvetica", "B", 8)
        self.cell(0, 5, _ascii(self.report_title.upper()), **NL)
        self.set_text_color(*INK)
        self.set_font("Helvetica", "B", 20)
        self.cell(0, 10, _ascii(title), **NL)
        self.set_text_color(*MUTED)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, _ascii(subtitle), **NL)
        self.ln(4)

    def section(self, text: str):
        self.ln(1.5)
        self.set_fill_color(*GOLD)
        self.rect(self.l_margin, self.get_y() + 1, 1.4, 5.5, style="F")
        self.set_x(self.l_margin + 4)
        self.set_text_color(*INK)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 7.5, _ascii(text), **NL)
        self.ln(1.5)

    def paragraph(self, text: str, size: float = 9):
        self.set_text_color(*MUTED)
        self.set_font("Helvetica", "", size)
        self.multi_cell(0, 4.8, _ascii(text), **NL)

    def value_box(self, label: str, value: str, sub: str, chips: list[str]):
        x, y, w, h = self.l_margin, self.get_y(), 178, 34
        self.set_fill_color(*NAVY)
        self.rect(x, y, w, h, style="F")
        self.set_fill_color(*NAVY2)
        self.rect(x + w * 0.62, y, w * 0.38, h, style="F")
        self.set_xy(x + 7, y + 5)
        self.set_text_color(148, 163, 184)
        self.set_font("Helvetica", "B", 8)
        self.cell(100, 4, _ascii(label.upper()), **NL)
        self.set_xy(x + 7, y + 10)
        self.set_text_color(*GOLD2)
        self.set_font("Helvetica", "B", 26)
        self.cell(100, 12, _ascii(value), **NL)
        self.set_xy(x + 7, y + 24)
        self.set_text_color(203, 213, 225)
        self.set_font("Helvetica", "", 8.5)
        self.cell(100, 5, _ascii(sub))
        cy = y + 7
        for chip in chips:
            self.set_xy(x + w * 0.62 + 6, cy)
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(255, 255, 255)
            self.cell(60, 5, _ascii(chip))
            cy += 7
        self.set_y(y + h + 4)

    def kv_table(self, rows: list[tuple[str, str]], cols: int = 2):
        col_w = 178 / cols
        for i in range(0, len(rows), cols):
            fill = (i // cols) % 2 == 0
            self.set_fill_color(*(SOFT if fill else (255, 255, 255)))
            for j in range(cols):
                if i + j >= len(rows):
                    self.cell(col_w, 7, "", fill=True, **RIGHT)
                    continue
                k, v = rows[i + j]
                self.set_font("Helvetica", "", 8.5)
                self.set_text_color(*MUTED)
                self.cell(col_w * 0.55, 7, "  " + _ascii(k), fill=True, **RIGHT)
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(*INK)
                self.cell(col_w * 0.45, 7, _ascii(v) + "  ", fill=True, align="R", **RIGHT)
            self.ln(7)
        self.ln(1)

    def table(self, header: list[str], rows: list[list[str]], widths: list[float]):
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8.5)
        for i, (h, w) in enumerate(zip(header, widths)):
            self.cell(w, 8, " " + _ascii(h) + " ", fill=True, align="L" if i == 0 else "R", **RIGHT)
        self.ln(8)
        for r_i, row in enumerate(rows):
            self.set_fill_color(*(SOFT if r_i % 2 == 0 else (255, 255, 255)))
            for c_i, (val, w) in enumerate(zip(row, widths)):
                self.set_font("Helvetica", "B" if c_i == 0 else "", 8.5)
                self.set_text_color(*(INK if c_i == 0 else MUTED))
                self.cell(w, 7.5, " " + _ascii(val) + " ", fill=True, align="L" if c_i == 0 else "R", **RIGHT)
            self.ln(7.5)
        self.ln(3)

    def hbars(self, items: list[tuple[str, float, str]], diverging: bool = False):
        """Horizontal bar chart. items = (label, value, value_text)."""
        if not items:
            return
        label_w, text_w = 38, 32
        chart_x = self.l_margin + label_w
        chart_w = 178 - label_w - text_w
        vmax = max(abs(v) for _, v, _ in items) or 1
        zero_x = chart_x + chart_w / 2 if diverging else chart_x
        scale = (chart_w / 2 if diverging else chart_w) / vmax
        for label, value, txt in items:
            y = self.get_y()
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(*INK)
            self.cell(label_w, 6.2, _ascii(label), **RIGHT)
            length = abs(value) * scale
            self.set_fill_color(*SOFT)
            self.rect(chart_x, y + 1.2, chart_w, 3.8, style="F")
            if diverging:
                self.set_fill_color(*(GREEN if value >= 0 else RED))
                self.rect(zero_x if value >= 0 else zero_x - length, y + 1.2, max(length, .4), 3.8, style="F")
            else:
                self.set_fill_color(*GOLD)
                self.rect(chart_x, y + 1.2, max(length, .4), 3.8, style="F")
            self.set_xy(chart_x + chart_w, y)
            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(*(INK if not diverging else (GREEN if value >= 0 else RED)))
            self.cell(text_w, 6.2, _ascii(txt), align="R", **NL)
        if diverging:
            self.set_draw_color(*MUTED)
            top = self.get_y() - 6.2 * len(items)
            self.line(zero_x, top, zero_x, self.get_y())
        self.ln(2)


# ============================================================== reports
def _feature_rows(f: dict) -> list[tuple[str, str]]:
    return [
        ("Median income", ui.money_plain(f["MedInc"] * 10000)),
        ("House age", f"{f['HouseAge']:.0f} years"),
        ("Average rooms", f"{f['AveRooms']:.2f}"),
        ("Average bedrooms", f"{f['AveBedrms']:.2f}"),
        ("Block population", f"{f['Population']:,.0f}"),
        ("Average occupancy", f"{f['AveOccup']:.2f}"),
        ("Latitude", f"{f['Latitude']:.4f}"),
        ("Longitude", f"{f['Longitude']:.4f}"),
    ]


def valuation_pdf(features: dict, price_usd: float, explanation: dict | None,
                  reference: str, tier: str) -> bytes:
    pdf = BrandedPDF("Property Valuation Report")
    pdf.add_page()
    now = datetime.now().strftime("%d %B %Y, %H:%M")
    pdf.title_block("Property Valuation Report", f"Reference {reference}   |   Generated {now}   |   "
                                                 f"Currency {ui.st.session_state.currency}")
    pdf.value_box(
        "Estimated market value", ui.money_plain(price_usd),
        f"Indicative range {ui.money_plain(price_usd * 0.9)} - {ui.money_plain(price_usd * 1.1)}",
        [f"Market tier: {tier}",
         f"Location: {features['Latitude']:.2f}, {features['Longitude']:.2f}",
         f"Model: LightGBM gradient boosting"],
    )

    pdf.section("Property profile")
    pdf.kv_table(_feature_rows(features))

    if explanation:
        pdf.section("What drives this valuation")
        pdf.paragraph(f"Starting from the market average of {ui.money_plain(explanation['base_value_usd'])}, "
                      "each factor below moved the estimate up (green) or down (red).")
        pdf.ln(2)
        contrib = sorted(explanation["contributions"], key=lambda c: abs(c["impact_usd"]), reverse=True)
        pdf.hbars([(ui.FEATURES[c["feature"]][1], ui.convert(c["impact_usd"]),
                    ("+" if c["impact_usd"] >= 0 else "-") + ui.money_plain(abs(c["impact_usd"])))
                   for c in contrib], diverging=True)
        top_up = [c for c in contrib if c["impact_usd"] > 0][:2]
        top_down = [c for c in contrib if c["impact_usd"] < 0][:2]
        summary = []
        if top_up:
            summary.append("Strongest positive factors: " + ", ".join(ui.FEATURES[c["feature"]][1] for c in top_up) + ".")
        if top_down:
            summary.append("Main factors holding the value back: "
                           + ", ".join(ui.FEATURES[c["feature"]][1] for c in top_down) + ".")
        pdf.paragraph(" ".join(summary))

    pdf.section("Methodology")
    pdf.paragraph(
        "This estimate is produced by a gradient-boosted decision-tree model (LightGBM) trained on the "
        "California Housing dataset (20,640 census districts). The model uses eight neighbourhood signals: "
        "income, housing age, rooms, bedrooms, population, occupancy and geographic coordinates. Factor "
        "contributions are SHAP values computed by the model itself. The indicative range is a simple +/-10% band."
    )
    pdf.section("Important notice")
    pdf.paragraph(
        "This report is generated automatically for educational and demonstration purposes. It is not a "
        "certified appraisal and must not be used as the sole basis for financial decisions. Values for "
        "locations outside California are not reliable."
    )
    return bytes(pdf.output())


def comparison_pdf(names: list[str], features: list[dict], prices: list[float]) -> bytes:
    pdf = BrandedPDF("Property Comparison Report")
    pdf.add_page()
    now = datetime.now().strftime("%d %B %Y, %H:%M")
    pdf.title_block("Property Comparison", f"{len(names)} properties   |   Generated {now}")
    best = max(range(len(prices)), key=lambda i: prices[i])
    low = min(range(len(prices)), key=lambda i: prices[i])
    pdf.value_box(
        "Highest estimated value", ui.money_plain(prices[best]), _ascii(names[best]),
        [f"Lowest: {ui.money_plain(prices[low])}",
         f"Spread: {ui.money_plain(prices[best] - prices[low])}",
         f"Average: {ui.money_plain(sum(prices) / len(prices))}"],
    )
    pdf.section("Estimated values")
    pdf.hbars([(f"Property {chr(65 + i)}", ui.convert(p), ui.money_plain(p)) for i, p in enumerate(prices)])

    pdf.section("Side-by-side profile")
    w0 = 46
    wc = (178 - w0) / len(names)
    header = ["Feature"] + [f"Property {chr(65 + i)}" for i in range(len(names))]
    rows = [["Estimated value"] + [ui.money_plain(p) for p in prices]]
    for key in ui.FEATURE_KEYS:
        fmt = "{:,.0f}" if key == "Population" else "{:.2f}"
        rows.append([ui.FEATURES[key][1]] + [fmt.format(f[key]) for f in features])
    pdf.table(header, rows, [w0] + [wc] * len(names))
    pdf.section("Properties")
    for i, n in enumerate(names):
        pdf.paragraph(f"Property {chr(65 + i)}: {n}")
    return bytes(pdf.output())


def portfolio_pdf(df) -> bytes:
    pdf = BrandedPDF("Portfolio Valuation Report")
    pdf.add_page()
    now = datetime.now().strftime("%d %B %Y, %H:%M")
    prices = df["Estimated value (USD)"]
    pdf.title_block("Portfolio Valuation Summary", f"{len(df)} properties   |   Generated {now}")
    pdf.value_box(
        "Total portfolio value", ui.money_plain(prices.sum()),
        f"Average {ui.money_plain(prices.mean())} per property",
        [f"Properties: {len(df):,}", f"Highest: {ui.money_plain(prices.max())}",
         f"Lowest: {ui.money_plain(prices.min())}"],
    )
    pdf.section("Top 10 properties by value")
    top = df.sort_values("Estimated value (USD)", ascending=False).head(10)
    rows = [[f"#{int(i) + 1}", ui.money_plain(r["Estimated value (USD)"]), f"{r['MedInc']:.2f}",
             f"{r['HouseAge']:.0f}", f"{r['AveRooms']:.1f}", f"{r['Latitude']:.2f}", f"{r['Longitude']:.2f}"]
            for i, r in top.iterrows()]
    pdf.table(["Row", "Estimate", "Income", "Age", "Rooms", "Lat", "Long"], rows,
              [22, 40, 24, 20, 22, 25, 25])
    pdf.section("Value distribution (USD)")
    bins = [0, 100_000, 200_000, 300_000, 400_000, float("inf")]
    labels = ["< $100K", "$100K-200K", "$200K-300K", "$300K-400K", "$400K +"]
    counts = [int(((prices >= lo) & (prices < hi)).sum()) for lo, hi in zip(bins[:-1], bins[1:])]
    pdf.hbars([(lab, c, f"{c} homes") for lab, c in zip(labels, counts)])
    return bytes(pdf.output())
