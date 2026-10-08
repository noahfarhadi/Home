"""
home_app.py

Homepage that lists the four portfolio tools and explains when to use each.
Needs only Streamlit. Run with:  streamlit run home_app.py

Everything that is meant to be edited sits in the CONFIG and TOOLS blocks below:
page title, texts, links, page width and the alignment of the text in the cards.
"""
import math
import random
from html import escape

import streamlit as st

# ---------------------------------------------------------------------------
# 1. Settings and content (edit here)
# ---------------------------------------------------------------------------
CONFIG = {
    "page_title": "Portfolio Analysis Tools",
    "title": "Portfolio Analysis Tools",
    "subtitle": ("Compare assets, run optimizers, test recommendations out of sample and read "
                 "technical indicators on your own price data."),
    "tools_heading": "The tools",
    "tools_intro": "Each tool opens in a new tab.",
    "guide_heading": "Which tool for which question",
    "steps_heading": "How the tools fit together",
    "notes_heading": "Before you upload",
    "disclaimer": ("These tools calculate results from the data you upload. "
                   "The results are not investment advice."),
    "max_width_px": 1040,          # width of the content column
    "card_text_align": "left",     # "left" or "center" for the text inside the four cards
    "show_plot": False,            # True shows the schematic risk and return picture under the subtitle
    # Settings of the schematic risk and return picture at the top
    "plot_dots": 16, "plot_seed": 11,
}

# One entry per tool. "question" feeds the guide table, "step" feeds the sequence,
# "extra" (optional) adds a third labelled row to the card.
TOOLS = [
    {
        "key": "grid",
        "name": "Investment Grid",
        "url": "https://optimizer-r2-grid.streamlit.app/",
        "what": ("Shows the risk and return of the assets in your file and assigns each asset "
                 "to a class by the median of all assets."),
        "use": "You want to see how the assets in a price file compare with each other on risk and return.",
        "upload": ("Price file (CSV or Excel). The first column is the date, followed by one column "
                   "of closing prices per asset."),
        "question": "Compare the risk and return of the assets in a price file",
        "step": "Look at the assets",
    },
    {
        "key": "optimizer",
        "name": "Portfolio Optimizer Demo",
        "url": "https://optimizer-r2-nexuvia.streamlit.app/",
        "what": "A teaching demo of classic textbook optimizers on historical data.",
        "use": "You want to run a standard optimizer on historical prices or returns, in class or on your own data.",
        "upload": ("Prices or returns (CSV or Excel). The first column is the date, followed by one column "
                   "per asset. A Yahoo Finance data source is available as a demo."),
        "question": "Run a classic optimizer on historical data",
        "step": "Run an optimizer",
    },
    {
        "key": "oos",
        "name": "Out-of-sample Performance Test",
        "url": "https://oosopti.streamlit.app/",
        "what": ("Measures what each portfolio recommendation earned after its date. It reports return, "
                 "volatility, Sharpe ratio and maximum drawdown, and benchmark statistics when you "
                 "include a benchmark column."),
        "use": ("You have dated recommendations and a later price history, and you want to know how "
                "the recommendations performed after their dates."),
        "upload": ("Weight files with the columns date, strategy, asset and weight; one price file with "
                   "prices after the recommendation dates; optionally a ticker mapping file."),
        "question": "Check how dated recommendations performed after their dates",
        "step": "Test on later prices",
    },
    {
        "key": "ta",
        "name": "Technical Analysis",
        "url": "https://teachical-analysis.streamlit.app/",
        "what": ("Shows RSI, Connors RSI, MACD and Williams %R for the asset you pick, "
                 "with overbought and oversold readings."),
        "use": "You want the indicator readings for one asset at a time.",
        "upload": "Price file (CSV, TXT or TSV) with one row per date, or one row per date and asset.",
        "extra": ("Settings", "Indicator lengths, the overbought and oversold levels and the date range."),
        "question": "Read RSI, Connors RSI, MACD or Williams %R for one asset",
        "step": None,
    },
]

# Order of the sequence shown under "How the tools fit together" (keys of TOOLS)
STEP_ORDER = ["grid", "optimizer", "oos"]
STEP_TEXT = {
    "grid": "Check the risk and return of the assets in your price file.",
    "optimizer": "Run a classic optimizer on the same history.",
    "oos": "Upload dated weights and prices from after the recommendation date.",
}
STEPS_FOOTNOTE = "Technical Analysis works on its own and does not need output from the other tools."

NOTES = [
    "Use one currency and one price type per file, for example closing prices.",
    "The out-of-sample test needs prices from after the recommendation dates. Without them there are no returns to measure.",
    "Annualized figures from a short sample are indicative only.",
]

# ---------------------------------------------------------------------------
# 2. Styling
# ---------------------------------------------------------------------------
# Colours are defined once as variables; a second set is used when the visitor's
# system is set to dark mode. The page paints its own background, so it looks the
# same whatever theme Streamlit itself uses.
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap');
:root{--paper:#F4F6F9;--panel:#FFFFFF;--ink:#14213D;--muted:#4A586F;--line:#D3DAE4;
--accent:#0B6E75;--dot:#7C899F;--btn:#14213D;--btn-text:#FFFFFF;--btn-hover:#0B6E75;}
@media (prefers-color-scheme: dark){:root{--paper:#0D1420;--panel:#142033;--ink:#E8ECF4;--muted:#A5B0C4;
--line:#2A3850;--accent:#5CC8CF;--dot:#6A7790;--btn:#E8ECF4;--btn-text:#0D1420;--btn-hover:#5CC8CF;}}
.stApp{background:var(--paper) !important;}
header[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{display:none !important;}
.block-container{max-width:__MAXW__px !important;margin:0 auto !important;padding:3.2rem 1.25rem 3rem !important;}
.hp{color:var(--ink);text-align:center;line-height:1.5;}
.hp a{text-decoration:none;}
.hp-serif,.hp-title,.hp-h2,.hp-name{font-family:'Source Serif 4',Georgia,'Times New Roman',serif;}
.hp-title{font-size:clamp(2.1rem,5.2vw,3.1rem);font-weight:600;letter-spacing:-0.01em;line-height:1.12;margin:0;}
.hp-sub{max-width:36rem;margin:1rem auto 0;font-size:1.15rem;line-height:1.55;color:var(--muted);}
.hp-plot{display:block;margin:2rem auto 0;width:100%;max-width:620px;height:auto;}
.hp-plot .axis{stroke:var(--line);stroke-width:1.5;fill:none;}
.hp-plot .lab{fill:var(--muted);font-size:16px;font-family:inherit;}
.hp-plot .dot{fill:var(--dot);opacity:.7;}
.hp-plot .lower{stroke:var(--line);stroke-width:2;fill:none;stroke-dasharray:5 5;}
.hp-plot .frontier{stroke:var(--accent);stroke-width:3;fill:none;stroke-linecap:round;
stroke-dasharray:1;stroke-dashoffset:0;animation:hp-draw 1.8s ease-out 0.2s both;}
@keyframes hp-draw{from{stroke-dashoffset:1;}to{stroke-dashoffset:0;}}
@media (prefers-reduced-motion: reduce){.hp-plot .frontier{animation:none;}}
.hp-sec{margin-top:3.6rem;}
.hp-h2{font-size:1.7rem;font-weight:600;margin:0;letter-spacing:-0.005em;}
.hp-lead{color:var(--muted);margin:.45rem 0 0;font-size:1.02rem;}
.hp-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.1rem;margin-top:1.6rem;
text-align:__ALIGN__;}
.hp-card{display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--line);
border-radius:6px;padding:1.5rem 1.5rem 1.4rem;}
.hp-name{font-size:1.35rem;font-weight:600;margin:0;line-height:1.25;}
.hp-what{margin:.55rem 0 0;font-size:1rem;line-height:1.55;}
.hp-row{margin-top:1rem;}
.hp-lab{font-weight:600;font-size:.9rem;color:var(--muted);margin-bottom:.1rem;}
.hp-val{font-size:.97rem;line-height:1.5;}
.hp-fill{flex:1;min-height:1.3rem;}
.hp a.hp-btn{display:block;text-align:center;background:var(--btn);color:var(--btn-text) !important;
font-weight:600;padding:.72rem 1rem;border-radius:5px;border:1px solid var(--btn);
transition:background-color .15s,border-color .15s;}
.hp a.hp-btn:hover{background:var(--btn-hover);border-color:var(--btn-hover);}
.hp a:focus-visible{outline:3px solid var(--accent);outline-offset:2px;}
.hp-table{width:100%;max-width:860px;margin:1.5rem auto 0;border-collapse:collapse;text-align:left;
background:var(--panel);border:1px solid var(--line);border-radius:6px;}
.hp-table th,.hp-table td{border:none !important;border-bottom:1px solid var(--line) !important;
background:transparent !important;}
.hp-table th{padding:.8rem 1.1rem;font-size:.9rem;font-weight:600;color:var(--muted);}
.hp-table td{padding:.85rem 1.1rem;vertical-align:top;}
.hp-table tr:last-child td{border-bottom:none !important;}
.hp-table td.to{white-space:nowrap;}
.hp a.hp-link{color:var(--accent) !important;font-weight:600;}
.hp a.hp-link:hover{text-decoration:underline;}
.hp-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.1rem;max-width:900px;
margin:1.7rem auto 0;}
.hp-step{position:relative;padding:0 .4rem;}
.hp-step:not(:last-child)::after{content:"";position:absolute;top:19px;left:calc(50% + 30px);
width:calc(100% + 1.1rem - 60px);border-top:1.5px solid var(--line);}
.hp-num{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;
border:1.5px solid var(--accent);border-radius:50%;color:var(--accent);font-weight:600;
font-family:'Source Serif 4',Georgia,serif;font-size:1.05rem;background:var(--paper);position:relative;z-index:1;}
.hp-stitle{font-weight:600;font-size:1.05rem;margin-top:.7rem;}
.hp-sdesc{color:var(--muted);font-size:.95rem;margin-top:.25rem;}
.hp-slink{margin-top:.35rem;font-size:.95rem;}
.hp-snote{max-width:900px;margin:1.4rem auto 0;color:var(--muted);font-size:.95rem;}
.hp-note{max-width:40rem;margin:.7rem auto 0;font-size:1rem;line-height:1.55;}
.hp-foot{margin-top:3.6rem;padding-top:1.4rem;border-top:1px solid var(--line);color:var(--muted);
font-size:.9rem;}
@media (max-width:760px){
.hp-grid{grid-template-columns:minmax(0,1fr);}
.hp-steps{grid-template-columns:minmax(0,1fr);gap:1.6rem;}
.hp-step:not(:last-child)::after{display:none;}
.hp-table td.to{white-space:normal;}
}
"""


# ---------------------------------------------------------------------------
# 3. Building blocks (each function returns one HTML string without line breaks)
# ---------------------------------------------------------------------------
def link(url, text, css_class):
    """Anchor that opens in a new tab."""
    return (f'<a class="{css_class}" href="{escape(url, quote=True)}" target="_blank" '
            f'rel="noopener noreferrer">{escape(text)}</a>')


def frontier_svg(n_dots, seed):
    """Schematic risk and return plane: scattered assets and a frontier curve. It shows no real data."""
    width, height = 640, 270
    left, right, top, bottom = 58, 620, 14, 232
    sigma0, mu0, k, sigma_max = 0.20, 0.38, 0.55, 0.78

    def sigma_of(mu):                       # risk of the frontier at a given return
        return math.sqrt(sigma0 ** 2 + k * (mu - mu0) ** 2)

    def px(sigma, mu):                      # plane coordinates (0 to 1) to SVG pixels
        return left + sigma / sigma_max * (right - left), bottom - mu * (bottom - top)

    def branch(mu_from, mu_to, steps=40):   # points along one branch of the curve
        mus = [mu_from + (mu_to - mu_from) * i / steps for i in range(steps + 1)]
        pts = [px(sigma_of(m), m) for m in mus]
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    rng = random.Random(seed)
    dots = []
    for _ in range(n_dots):                 # assets sit to the right of the frontier
        mu = rng.uniform(0.08, 0.93)
        sigma = min(sigma_of(mu) + rng.uniform(0.05, 0.30), sigma_max - 0.03)
        x, y = px(sigma, mu)
        dots.append(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/>')

    return (
        f'<svg class="hp-plot" viewBox="0 0 {width} {height}" role="img" aria-hidden="true" focusable="false">'
        f'<path class="axis" d="M{left},{top} L{left},{bottom} L{right},{bottom}"/>'
        f'<text class="lab" x="{(left + right) / 2:.0f}" y="{height - 8}" text-anchor="middle">Risk</text>'
        f'<text class="lab" transform="translate(18 {(top + bottom) / 2:.0f}) rotate(-90)" '
        f'text-anchor="middle">Return</text>'
        f'<path class="lower" d="{branch(mu0, 0.06)}"/>'
        f'{"".join(dots)}'
        f'<path class="frontier" pathLength="1" d="{branch(mu0, 0.95)}"/>'
        f'</svg>'
    )


def card_html(tool):
    """One tool card: name, what it does, when to use it, what to upload, button."""
    extra = ""
    if tool.get("extra"):                   # optional third row
        label, text = tool["extra"]
        extra = f'<div class="hp-row"><div class="hp-lab">{escape(label)}</div><div class="hp-val">{escape(text)}</div></div>'
    return (
        '<div class="hp-card">'
        f'<div class="hp-name" role="heading" aria-level="3">{escape(tool["name"])}</div>'
        f'<div class="hp-what">{escape(tool["what"])}</div>'
        f'<div class="hp-row"><div class="hp-lab">Use it when</div><div class="hp-val">{escape(tool["use"])}</div></div>'
        f'<div class="hp-row"><div class="hp-lab">You upload</div><div class="hp-val">{escape(tool["upload"])}</div></div>'
        f'{extra}'
        '<div class="hp-fill"></div>'
        f'{link(tool["url"], "Open " + tool["name"], "hp-btn")}'
        '</div>'
    )


def guide_html(tools):
    """Table that maps a question to the tool that answers it."""
    rows = "".join(
        f'<tr><td>{escape(t["question"])}</td><td class="to">{link(t["url"], t["name"], "hp-link")}</td></tr>'
        for t in tools)
    return ('<table class="hp-table"><thead><tr><th scope="col">If you want to</th>'
            f'<th scope="col">Use</th></tr></thead><tbody>{rows}</tbody></table>')


def steps_html(tools, order, texts):
    """Numbered sequence; the numbers are real because the order matters."""
    by_key = {t["key"]: t for t in tools}
    items = []
    for i, key in enumerate(order, start=1):
        t = by_key[key]
        items.append(
            '<div class="hp-step">'
            f'<div class="hp-num">{i}</div>'
            f'<div class="hp-stitle">{escape(t["step"])}</div>'
            f'<div class="hp-sdesc">{escape(texts[key])}</div>'
            f'<div class="hp-slink">{link(t["url"], t["name"], "hp-link")}</div>'
            '</div>')
    return f'<div class="hp-steps">{"".join(items)}</div>'


def section(heading, lead=None):
    """Centered section heading with an optional one-line introduction."""
    out = f'<div class="hp-sec"><div class="hp-h2" role="heading" aria-level="2">{escape(heading)}</div>'
    if lead:
        out += f'<div class="hp-lead">{escape(lead)}</div>'
    return out


# ---------------------------------------------------------------------------
# 4. Page
# ---------------------------------------------------------------------------
st.set_page_config(page_title=CONFIG["page_title"], layout="wide", initial_sidebar_state="collapsed")

# Step 1: styles (width and text alignment come from CONFIG)
css = CSS.replace("__MAXW__", str(int(CONFIG["max_width_px"]))).replace("__ALIGN__", CONFIG["card_text_align"])
st.markdown(f"<style>{' '.join(css.split())}</style>", unsafe_allow_html=True)

# Step 2: title, subtitle and, if CONFIG["show_plot"] is True, the schematic picture
st.markdown(
    '<div class="hp">'
    f'<div class="hp-title" role="heading" aria-level="1">{escape(CONFIG["title"])}</div>'
    f'<div class="hp-sub">{escape(CONFIG["subtitle"])}</div>'
    f'{frontier_svg(CONFIG["plot_dots"], CONFIG["plot_seed"]) if CONFIG["show_plot"] else ""}'
    '</div>', unsafe_allow_html=True)

# Step 3: the four tool cards
st.markdown(
    '<div class="hp">'
    f'{section(CONFIG["tools_heading"], CONFIG["tools_intro"])}</div>'
    f'<div class="hp-grid">{"".join(card_html(t) for t in TOOLS)}</div></div>',
    unsafe_allow_html=True)

# Step 4: guide table, sequence and notes
st.markdown(
    '<div class="hp">'
    f'{section(CONFIG["guide_heading"])}{guide_html(TOOLS)}</div>'
    f'{section(CONFIG["steps_heading"])}{steps_html(TOOLS, STEP_ORDER, STEP_TEXT)}'
    f'<div class="hp-snote">{escape(STEPS_FOOTNOTE)}</div></div>'
    f'{section(CONFIG["notes_heading"])}'
    f'{"".join(f"<div class=hp-note>{escape(n)}</div>" for n in NOTES)}</div>'
    f'<div class="hp-foot">{escape(CONFIG["disclaimer"])}</div>'
    '</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Version log
# ---------------------------------------------------------------------------
# v1.0 (2026-10-08)  New file. Added: CONFIG, TOOLS, STEP_ORDER, STEP_TEXT,
#   STEPS_FOOTNOTE, NOTES, CSS, link, frontier_svg, card_html, guide_html,
#   steps_html, section, the optional "extra" row in card_html, and the page
#   build in section 4.
# v1.1 (2026-10-08)  Added: CONFIG["show_plot"] (default False). Modified: the
#   frontier_svg line in step 2 of the page build now runs only if show_plot is True.
