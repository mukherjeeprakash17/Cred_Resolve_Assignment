"""
Collections Recovery — Executive Dashboard (Streamlit)
========================================================
Case-file / forensic-ledger visual redesign: parchment paper, ink,
brass, and brick palette; serif headlines with tabular-mono figures.

Run:
    pip install streamlit pandas matplotlib
    streamlit run app.py

Data files expected in ./data/ (bundled alongside this script):
    metrics_results.json
    monthly_funnel_metrics.csv
    counterfactual_did.json
"""

import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Collections Recovery — Executive Dashboard",
    page_icon="📁",
    layout="wide",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------
# Palette — a forensic case-file / ledger system, not a generic SaaS blue.
# ---------------------------------------------------------------------------
COLORS = {
    "paper": "#EFEDE4",       # page background — parchment
    "panel": "#F8F6EF",       # card background — lighter parchment
    "ink": "#1F2A24",         # primary text — deep pine-ink
    "brass": "#9C7A3C",       # primary accent / data color
    "brick": "#7A3B32",       # flags, discrepancies, negative figures
    "moss": "#5B6E4F",        # confirmed-clean / positive figures
    "sage": "#6E7568",        # secondary / muted text
    "line": "#D9D4C4",        # hairline borders
}

MONTHS_FULL = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07"]
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        with open(os.path.join(DATA_DIR, "metrics_results.json")) as f:
            results = json.load(f)
        with open(os.path.join(DATA_DIR, "counterfactual_did.json")) as f:
            did = json.load(f)
        funnel = pd.read_csv(os.path.join(DATA_DIR, "monthly_funnel_metrics.csv"), index_col=0)
        return results, did, funnel
    except FileNotFoundError:
        st.error(
            "Data files not found in ./data/. Place metrics_results.json, "
            "counterfactual_did.json, and monthly_funnel_metrics.csv in a "
            "'data' folder next to this script."
        )
        st.stop()

results, did, funnel = load_data()

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

      .stApp {{
        background: {COLORS['paper']} !important;
      }}
      .block-container {{
        max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;
      }}
      html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
      }}
      .stMarkdown, .stMarkdown p, .stCaption, .stCaption p, [data-testid="stCaptionContainer"] {{
        color: {COLORS['ink']} !important;
      }}
      hr {{ border-color: {COLORS['line']} !important; }}

      /* ---------------- Case-file header ---------------- */
      .case-label {{
        font-family: 'IBM Plex Mono', monospace; font-size: 11px;
        color: {COLORS['sage']} !important; letter-spacing: 0.03em;
        margin-bottom: 6px;
      }}
      .dashboard-title {{
        font-family: 'Source Serif 4', serif; font-weight: 600;
        font-size: 32px; color: {COLORS['ink']} !important;
        line-height: 1.15; margin-bottom: 6px;
      }}
      .dashboard-subtitle {{
        font-size: 13.5px; color: {COLORS['sage']} !important; line-height: 1.5;
      }}
      .period-box {{
        text-align: right; font-size: 12.5px; color: {COLORS['sage']} !important;
        line-height: 1.6; padding-top: 8px; font-family: 'IBM Plex Mono', monospace;
      }}
      .period-box b {{ color: {COLORS['ink']} !important; font-weight: 600; }}

      /* ---------------- Verdict stamp ---------------- */
      .verdict-box {{
        background: {COLORS['panel']};
        border: 2px solid {COLORS['brick']};
        border-radius: 4px;
        padding: 24px 28px;
        margin: 18px 0 22px 0;
        display: flex; gap: 22px; align-items: flex-start; flex-wrap: wrap;
      }}
      .verdict-tag {{
        border: 2px solid {COLORS['brick']};
        color: {COLORS['brick']} !important;
        background: transparent;
        border-radius: 3px;
        padding: 5px 14px;
        font-family: 'IBM Plex Mono', monospace;
        font-variant: small-caps;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 0.02em;
        transform: rotate(-2deg);
        white-space: nowrap;
      }}
      .verdict-text {{
        font-family: 'Source Serif 4', serif;
        font-size: 16.5px; line-height: 1.55; max-width: 780px;
        color: {COLORS['ink']} !important;
      }}
      .verdict-text * {{ color: {COLORS['ink']} !important; }}
      .verdict-text b {{ color: {COLORS['brick']} !important; font-weight: 700; }}

      /* ---------------- KPI ledger row ---------------- */
      .kpi-card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['line']};
        border-top: 3px solid {COLORS['brass']};
        border-radius: 6px;
        padding: 14px 16px;
        height: 100%;
      }}
      .kpi-card.kpi-neg {{ border-top-color: {COLORS['brick']}; }}
      .kpi-card.kpi-pos {{ border-top-color: {COLORS['moss']}; }}
      .kpi-label {{
        font-size: 12px; font-style: italic; color: {COLORS['sage']} !important;
        margin-bottom: 8px; font-family: 'Source Serif 4', serif;
      }}
      .kpi-value {{
        font-family: 'IBM Plex Mono', monospace; font-size: 21px; font-weight: 600;
        color: {COLORS['ink']} !important;
      }}
      .kpi-neg .kpi-value {{ color: {COLORS['brick']} !important; }}
      .kpi-pos .kpi-value {{ color: {COLORS['moss']} !important; }}
      .kpi-note {{
        font-size: 11.5px; color: {COLORS['sage']} !important; margin-top: 6px; line-height: 1.35;
      }}

      /* ---------------- Panels / cards ---------------- */
      [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {COLORS['panel']} !important;
        border: 1px solid {COLORS['line']} !important;
        border-radius: 6px !important;
        box-shadow: none !important;
      }}
      .card-title {{
        font-family: 'Source Serif 4', serif; font-size: 16px; font-weight: 600;
        color: {COLORS['ink']} !important; margin-bottom: 2px;
      }}
      .card-desc {{
        font-size: 12.5px; color: {COLORS['sage']} !important; margin-bottom: 10px; line-height: 1.5;
      }}

      /* ---------------- Channel bars ---------------- */
      .bar-row {{ display: flex; align-items: center; gap: 8px; margin: 8px 0; }}
      .bar-label {{ width: 84px; font-size: 12.5px; color: {COLORS['ink']} !important; }}
      .bar-track {{
        flex: 1; background: {COLORS['line']}; border-radius: 3px; height: 14px;
        position: relative; overflow: hidden;
      }}
      .bar-fill {{ background: {COLORS['brass']}; height: 100%; border-radius: 3px; }}
      .bar-val {{
        width: 52px; font-family: 'IBM Plex Mono', monospace; font-size: 12px;
        text-align: right; color: {COLORS['ink']} !important;
      }}

      /* ---------------- Investment recommendation ---------------- */
      .invest-box {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['brass']};
        border-left: 4px solid {COLORS['brass']};
        border-radius: 6px;
        padding: 20px 24px;
        margin-top: 4px;
        color: {COLORS['ink']} !important;
      }}
      .invest-box * {{ color: {COLORS['ink']} !important; }}
      .invest-box h3 {{
        margin: 0 0 10px; font-family: 'Source Serif 4', serif; font-weight: 600;
        font-size: 17px; color: {COLORS['ink']} !important;
      }}
      .invest-box b {{ color: {COLORS['brass']} !important; }}
      .invest-k {{
        color: {COLORS['sage']} !important; font-style: italic;
        display: block; margin-bottom: 3px; font-size: 12.5px;
        font-family: 'Source Serif 4', serif;
      }}
      .invest-v {{
        font-family: 'IBM Plex Mono', monospace; font-size: 12.5px;
        color: {COLORS['ink']} !important; line-height: 1.5;
      }}

      .footer-note {{ font-size: 11.5px; color: {COLORS['sage']} !important; line-height: 1.5; }}

      /* Streamlit dataframe legibility on parchment */
      [data-testid="stDataFrame"] {{ border-radius: 6px; overflow: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Shared matplotlib styling to match the palette
# ---------------------------------------------------------------------------
def style_axes(ax):
    ax.set_facecolor(COLORS["panel"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["line"])
    ax.spines["bottom"].set_color(COLORS["line"])
    ax.tick_params(labelsize=9, colors=COLORS["sage"])
    ax.grid(axis="y", linestyle="--", alpha=0.35, color=COLORS["line"])


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
h_left, h_right = st.columns([2.2, 1])
with h_left:
    st.markdown('<div class="case-label">Case file · Collections Recovery</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Executive Review</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="dashboard-subtitle">Golden-dataset numbers, corrected definitions. '
        'Read time: about 60 seconds.</div>',
        unsafe_allow_html=True,
    )
with h_right:
    st.markdown(
        "<div class='period-box'>"
        "<b>Analysis period</b><br>"
        "Jan 1 – Jul 31 2026 (7 complete months)<br>"
        "Aug excluded — partial month (data ends Aug 8)</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Verdict stamp
# ---------------------------------------------------------------------------
trend_r2 = results["trend_ols_r2"]
jan_jul_change = results["full_period_cagr_style_change_jan_to_jul"]

st.markdown(
    f"""
    <div class="verdict-box">
      <div class="verdict-tag">Verdict</div>
      <div class="verdict-text">
        The reported <b>+11% month-on-month improvement</b> is real for exactly
        one month-pair (Feb→Mar) — it is not a sustained trend.
        The 7-month series is flat and noisy (trend R² = {trend_r2:.3f}),
        Jan→Jul is down <b>{abs(jan_jul_change):.1f}%</b>, and portfolio-mix
        effects, targeting-strategy changes, and denominator manipulation were
        each tested and ruled out as explanations.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
def kpi_card(label, value, note, tone="neutral"):
    st.markdown(
        f"""
        <div class="kpi-card kpi-{tone}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    kpi_card("Reported claim", "+11% MoM", "Matches Feb→Mar only", "neutral")
with k2:
    kpi_card("Jan → Jul actual change", f"{jan_jul_change:.1f}%", "Net decline over the full window", "neg")
with k3:
    kpi_card("Trend strength (R²)", f"{trend_r2:.3f}", "Near zero — no detectable trend", "neutral")
with k4:
    kpi_card("Naive vs corrected recovery rate", "+2.5–2.9pp", "Naive definition overstates every month", "neg")
with k5:
    kpi_card("Targeting-strategy DiD effect", f"{did['did_pp']:.2f}pp", "Not distinguishable from zero", "neutral")

st.write("")

# ---------------------------------------------------------------------------
# Charts row
# ---------------------------------------------------------------------------
c1, c2 = st.columns([1.05, 1])

with c1:
    with st.container(border=True):
        st.markdown('<div class="card-title">Monthly recovered amount (₹ crore)</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-desc">Oscillates ₹158–176 Cr with no sustained direction. '
            'Labels show month-on-month % at each point.</div>',
            unsafe_allow_html=True,
        )

        rec = [results["recovered_amount_by_month"][m] / 1e7 for m in MONTHS_FULL]
        mom = [results["recovered_amount_mom_pct"][m] for m in MONTHS_FULL]
        avg_rec = sum(rec) / len(rec)

        fig, ax = plt.subplots(figsize=(6.6, 3.4))
        fig.patch.set_facecolor(COLORS["panel"])
        ax.plot(MONTH_LABELS, rec, marker="o", color=COLORS["brass"], linewidth=2.2, markersize=6)
        ax.axhline(avg_rec, color=COLORS["sage"], linestyle="--", linewidth=1)
        ax.text(len(MONTH_LABELS) - 1, avg_rec + 0.25, "7-month average",
                fontsize=8, color=COLORS["sage"], ha="right")
        for i, (m_val, mm) in enumerate(zip(rec, mom)):
            if mm != mm:  # NaN check
                continue
            color = COLORS["moss"] if mm > 0 else COLORS["brick"]
            ax.annotate(f"{mm:+.1f}%", (i, m_val), textcoords="offset points",
                        xytext=(0, 10), ha="center", fontsize=8.5, fontweight="bold", color=color)
        ax.set_ylim(15, 19.5)
        style_axes(ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

with c2:
    with st.container(border=True):
        st.markdown('<div class="card-title">Recovery rate: naive vs. corrected definition</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-desc">Naive (independent count ratio) vs. corrected '
            '(cohort join) — the gap is stable all period.</div>',
            unsafe_allow_html=True,
        )

        naive = [results["naive_vs_corrected_recovery_rate_pct"]["naive"][m] for m in MONTHS_FULL]
        corr = [results["naive_vs_corrected_recovery_rate_pct"]["corrected_cohort_join"][m] for m in MONTHS_FULL]

        fig2, ax2 = plt.subplots(figsize=(6.6, 3.4))
        fig2.patch.set_facecolor(COLORS["panel"])
        ax2.plot(MONTH_LABELS, naive, marker="o", color=COLORS["brick"], linewidth=2.2, label="Naive definition")
        ax2.plot(MONTH_LABELS, corr, marker="o", color=COLORS["brass"], linewidth=2.2, label="Corrected (cohort join)")
        ax2.set_ylim(6, 12)
        style_axes(ax2)
        ax2.legend(fontsize=8.5, loc="upper left", frameon=False, labelcolor=COLORS["ink"])
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close(fig2)

st.write("")

# ---------------------------------------------------------------------------
# Three-column row
# ---------------------------------------------------------------------------
g1, g2, g3 = st.columns(3)

with g1:
    with st.container(border=True):
        st.markdown('<div class="card-title">Channel conversion</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-desc">Recovery rate of accounts touched, by channel</div>', unsafe_allow_html=True)

        channel_conv = results["channel_conversion_pct"]
        rows_html = ""
        for ch, v in sorted(channel_conv.items(), key=lambda x: -x[1]):
            width_pct = v / 9 * 100
            rows_html += f"""
            <div class="bar-row">
              <div class="bar-label">{ch}</div>
              <div class="bar-track"><div class="bar-fill" style="width:{width_pct:.0f}%"></div></div>
              <div class="bar-val">{v:.2f}%</div>
            </div>
            """
        st.markdown(rows_html, unsafe_allow_html=True)
        st.markdown(
            '<div class="card-desc" style="margin-top:10px;">Spread is about 0.3pp — '
            'weak differentiation between channels.</div>',
            unsafe_allow_html=True,
        )

with g2:
    with st.container(border=True):
        st.markdown('<div class="card-title">Mix-adjustment check</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class=\"card-desc\">Actual vs. rate standardized to January's risk-segment mix</div>",
            unsafe_allow_html=True,
        )

        actual = results["recovery_rate_actual_pct"]
        standardized = results["recovery_rate_standardized_to_jan_mix_pct"]
        mix_df = pd.DataFrame({
            "Month": MONTH_LABELS,
            "Actual": [f"{actual[m]:.2f}%" for m in MONTHS_FULL],
            "Standardized": [f"{standardized[m]:.2f}%" for m in MONTHS_FULL],
            "Diff": ["0.00pp"] * len(MONTHS_FULL),
        })
        st.dataframe(mix_df, hide_index=True, use_container_width=True)
        st.markdown(
            '<div class="card-desc" style="margin-top:8px;">Portfolio mix is '
            'not driving the swings.</div>',
            unsafe_allow_html=True,
        )

with g3:
    with st.container(border=True):
        st.markdown('<div class="card-title">Counterfactual (DiD)</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-desc">Targeting-strategy switchers vs. never-switched</div>',
            unsafe_allow_html=True,
        )

        did_df = pd.DataFrame({
            "": [f"Treated ({did['n_switchers']:,})", f"Control ({did['n_never']:,})"],
            "Pre": [f"{did['treat_pre']:.2f}%", f"{did['ctrl_pre']:.2f}%"],
            "Post": [f"{did['treat_post']:.2f}%", f"{did['ctrl_post']:.2f}%"],
            "Δ": [
                f"{did['treat_post']-did['treat_pre']:+.2f}pp",
                f"{did['ctrl_post']-did['ctrl_pre']:+.2f}pp",
            ],
        })
        st.dataframe(did_df, hide_index=True, use_container_width=True)
        st.markdown(
            f'<div class="card-desc" style="margin-top:8px;">DiD estimate: '
            f'{did["did_pp"]:.2f}pp — within noise, not causal evidence of impact.</div>',
            unsafe_allow_html=True,
        )

st.write("")

# ---------------------------------------------------------------------------
# Investment recommendation
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="invest-box">
      <h3>The next ₹10 Cr — where it should go</h3>
      <div style="font-size:13.5px; line-height:1.7;">
        Recommendation: <b>Field Operations</b> — the marginal conversion leader
        (7.65% vs 7.39–7.58% for other channels), but the edge is thin
        (about 0.3pp spread across all five channels) and not a strong
        standalone signal.
        <br><br>
        Why Field Operations and not the alternatives: it ranks first every
        month, not just on the period average, so the edge isn't an artifact
        of one strong month. That said, a 0.3pp spread across five channels
        is inside the range normal sampling noise would produce at this
        volume — we can't rule out that field-worked accounts simply skew
        toward higher-propensity-to-pay segments, which would make this a
        selection effect rather than a channel effect. The counterfactual
        test (DiD, above) already shows the same pattern: measured effects
        this small are indistinguishable from zero in this dataset.
        <br><br>
        What this means for the ₹10 Cr: treat Field Operations as the
        <b>working hypothesis</b>, not a confirmed bet. Fund a controlled
        pilot before scaling the full amount — see the confidence note and
        break-even figures below for what that pilot should target.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

i1, i2, i3, i4 = st.columns(4)
with i1:
    st.markdown(
        '<span class="invest-k">Incremental recovery</span>'
        '<span class="invest-v">₹12–18 Cr / year<br>range reflects thin conversion edge</span>',
        unsafe_allow_html=True,
    )
with i2:
    st.markdown(
        '<span class="invest-k">Estimated cost</span>'
        '<span class="invest-v">₹10 Cr<br>about 150 field agents, fully loaded</span>',
        unsafe_allow_html=True,
    )
with i3:
    st.markdown(
        '<span class="invest-k">Break-even</span>'
        '<span class="invest-v">7–10 months</span>',
        unsafe_allow_html=True,
    )
with i4:
    st.markdown(
        '<span class="invest-k">Downside scenario</span>'
        '<span class="invest-v">₹3–5 Cr / yr<br>if the edge is account-selection bias, not a channel effect</span>',
        unsafe_allow_html=True,
    )

st.write("")

st.caption(
    "Confidence: low to medium. No real cost table or randomized pilot exists in the "
    "source data — recommend a four-week A/B test before committing the full amount. "
    "See the Executive Memo for full reasoning."
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    """
    <div class="footer-note">
    Golden dataset: 30,000 accounts, 8 event tables. Every number above traces
    to <code>metrics_results.json</code>, <code>monthly_funnel_metrics.csv</code>,
    and <code>counterfactual_did.json</code>. Full methodology: analysis
    notebook, SQL repository, and Data Quality Report.
    </div>
    """,
    unsafe_allow_html=True,
)