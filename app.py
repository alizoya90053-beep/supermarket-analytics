"""
app.py  —  SuperMarket Sales Analytics  (Streamlit)
====================================================
Run:  streamlit run app.py

Covers all 6 requirements:
  1. Collect & Load CSV dataset
  2. Data cleaning — missing / incorrect values
  3. Calculate Sales = Quantity × Unit price
  4. Group & summarise  (totals, counts, averages)
  5. Charts to compare results
  6. Business decisions from results
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import load_and_clean, DATA_PATH
from analysis import (
    overall_kpis, sales_formula_sample,
    sales_by_branch, sales_by_product,
    sales_by_customer_type, sales_by_gender, sales_by_payment,
    monthly_sales, sales_by_day, sales_by_hour,
    product_branch_pivot, gender_product_sales,
    rating_by_product, full_summary_table,
)

# ─────────────────────────────────────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SuperMarket Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── typography & layout ── */
body, .stApp { font-family: "Segoe UI", system-ui, sans-serif; }

/* ── page header ── */
.pg-title {
    font-size: 2rem; font-weight: 700; color: #0f172a;
    border-bottom: 3px solid #2563eb; padding-bottom: .4rem;
    margin-bottom: .15rem;
}
.pg-sub {
    font-size: .95rem; color: #64748b; margin-bottom: 1.4rem;
}

/* ── step badges ── */
.step-badge {
    display: inline-block;
    background: #2563eb; color: #fff;
    font-size: .72rem; font-weight: 700;
    letter-spacing: .06em; text-transform: uppercase;
    padding: .18rem .55rem; border-radius: 999px;
    margin-right: .45rem; vertical-align: middle;
}

/* ── section headings ── */
.sec-head {
    font-size: 1.05rem; font-weight: 600; color: #0f172a;
    border-left: 4px solid #2563eb; padding-left: .55rem;
    margin-top: 1.6rem; margin-bottom: .7rem;
}

/* ── KPI cards ── */
.kpi-wrap {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 1rem 1.1rem;
    text-align: center; height: 100%;
}
.kpi-label {
    font-size: .7rem; font-weight: 600; color: #64748b;
    text-transform: uppercase; letter-spacing: .07em;
    margin-bottom: .3rem;
}
.kpi-val { font-size: 1.55rem; font-weight: 700; color: #0f172a; }
.kpi-unit { font-size: .78rem; color: #94a3b8; margin-top: .1rem; }

/* ── alert / insight boxes ── */
.box { border-radius: 7px; padding: .75rem 1rem; margin-bottom: .5rem; font-size: .9rem; }
.box-info  { background:#eff6ff; border-left:4px solid #2563eb; color:#1e3a5f; }
.box-good  { background:#f0fdf4; border-left:4px solid #16a34a; color:#14532d; }
.box-warn  { background:#fffbeb; border-left:4px solid #d97706; color:#78350f; }
.box-error { background:#fef2f2; border-left:4px solid #dc2626; color:#7f1d1d; }

/* ── formula callout ── */
.formula {
    background:#f1f5f9; border:1px solid #cbd5e1;
    border-radius:8px; padding:.8rem 1.2rem;
    font-family: "Courier New", monospace; font-size:1.05rem;
    color:#1e293b; margin: .6rem 0 1rem 0;
    text-align: center; font-weight: 600;
}

/* ── sidebar ── */
section[data-testid="stSidebar"] { background: #f8fafc; }

/* ── tab strip ── */
.stTabs [data-baseweb="tab"] { font-weight: 600; font-size: .88rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
COLORS   = px.colors.qualitative.Set2
PLT_BASE = dict(plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=46, b=20, l=10, r=10),
                font=dict(family="Segoe UI, system-ui, sans-serif", size=12))


def kpi(col, label, value, unit=""):
    col.markdown(
        f'<div class="kpi-wrap">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-val">{value}</div>'
        f'<div class="kpi-unit">{unit}</div>'
        f'</div>', unsafe_allow_html=True)


def sec(text, step=None):
    badge = f'<span class="step-badge">Step {step}</span>' if step else ""
    st.markdown(f'<div class="sec-head">{badge}{text}</div>', unsafe_allow_html=True)


def box(kind, text):
    st.markdown(f'<div class="box box-{kind}">{text}</div>', unsafe_allow_html=True)


def bar(df, x, y, title, color=None, horizontal=False, colors=COLORS, text=True):
    kwargs = dict(
        title=title, text_auto=(".2s" if text else False),
        color_discrete_sequence=colors,
    )
    if color:
        kwargs["color"] = color
    else:
        kwargs["color"] = y if not horizontal else x
        kwargs["color_continuous_scale"] = "Blues"
        kwargs["color_discrete_sequence"] = None

    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", **kwargs)
    else:
        fig = px.bar(df, x=x, y=y, **kwargs)

    fig.update_layout(**PLT_BASE)
    if not color:
        fig.update_layout(coloraxis_showscale=False)
    else:
        fig.update_layout(showlegend=True)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Load data (cached)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="⏳ Loading and cleaning dataset…")
def get_data():
    return load_and_clean(DATA_PATH)


df_full, rpt = get_data()


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — filters
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 SuperMarket Analytics")
    st.markdown("---")
    st.markdown("### 🔍 Filters")

    sel_branch  = st.multiselect("Branch",         sorted(df_full["Branch"].unique()),        default=sorted(df_full["Branch"].unique()))
    sel_product = st.multiselect("Product Line",   sorted(df_full["Product line"].unique()),  default=sorted(df_full["Product line"].unique()))
    sel_gender  = st.multiselect("Gender",         sorted(df_full["Gender"].unique()),         default=sorted(df_full["Gender"].unique()))
    sel_ctype   = st.multiselect("Customer Type",  sorted(df_full["Customer type"].unique()), default=sorted(df_full["Customer type"].unique()))
    sel_payment = st.multiselect("Payment Method", sorted(df_full["Payment"].unique()),       default=sorted(df_full["Payment"].unique()))

    min_d = df_full["Date"].min().date()
    max_d = df_full["Date"].max().date()
    date_range = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    st.markdown("---")

# Apply filters
df = df_full.copy()
if sel_branch  : df = df[df["Branch"].isin(sel_branch)]
if sel_product : df = df[df["Product line"].isin(sel_product)]
if sel_gender  : df = df[df["Gender"].isin(sel_gender)]
if sel_ctype   : df = df[df["Customer type"].isin(sel_ctype)]
if sel_payment : df = df[df["Payment"].isin(sel_payment)]
if len(date_range) == 2:
    df = df[(df["Date"].dt.date >= date_range[0]) & (df["Date"].dt.date <= date_range[1])]

with st.sidebar:
    st.caption(f"**{len(df):,}** of **{len(df_full):,}** rows selected")
    st.markdown("---")
    st.markdown(
        "<small style='color:#94a3b8'>Dataset: Jan–Mar 2019<br>"
        "1 000 transactions · 3 branches</small>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Page header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="pg-title">🛒 SuperMarket Sales Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="pg-sub">End-to-end data analytics pipeline · '
    'Steps 1 – 6 · Dataset: Jan–Mar 2019 · 1 000 transactions · 3 branches</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
T = st.tabs([
    "📋 Step 1 — Load Data",
    "🧹 Step 2 — Data Cleaning",
    "🧮 Step 3 — Sales Formula",
    "📊 Step 4 — Summaries",
    "📈 Step 5 — Charts",
    "💡 Step 6 — Decisions",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1  — Collect & Load
# ══════════════════════════════════════════════════════════════════════════════
with T[0]:
    sec("Dataset Overview", step=1)

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    kpi(r1c1, "Total Rows Loaded",  f"{rpt['original_rows']:,}")
    kpi(r1c2, "Total Columns",      f"{len(rpt['original_cols']):,}")
    kpi(r1c3, "Clean Rows",         f"{rpt['final_rows']:,}")
    kpi(r1c4, "Rows Dropped",       f"{rpt['total_dropped']:,}")

    sec("Column Names & Data Types")
    dtype_df = (
        pd.DataFrame({
            "Column"      : df_full.columns.tolist(),
            "Data Type"   : df_full.dtypes.astype(str).tolist(),
            "Non-Null Count": df_full.notna().sum().tolist(),
            "Sample Value": [str(df_full[c].iloc[0]) if len(df_full) else "—" for c in df_full.columns],
        })
    )
    st.dataframe(dtype_df, use_container_width=True, height=400)

    sec("First 50 Rows of Raw Dataset")
    raw_display = df_full.drop(columns=["Month_num","Sales_Original","Sales_Calculated","Sales_Diff"], errors="ignore").head(50)
    st.dataframe(raw_display, use_container_width=True, height=380)

    box("info", f"✅ <b>Loaded successfully</b>: <b>{rpt['original_rows']:,}</b> rows × "
                f"<b>{len(rpt['original_cols'])}</b> columns from <code>supermarket_sales.csv</code>.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2  — Data Cleaning
# ══════════════════════════════════════════════════════════════════════════════
with T[1]:
    sec("Cleaning Summary", step=2)

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "Original Rows",      f"{rpt['original_rows']:,}")
    kpi(c2, "Missing Cells",      f"{rpt['total_missing_cells']:,}")
    kpi(c3, "Duplicates Removed", f"{rpt['duplicates_dropped']:,}")
    kpi(c4, "Rows Dropped Total", f"{rpt['total_dropped']:,}")
    kpi(c5, "Final Clean Rows",   f"{rpt['final_rows']:,}")

    # ── 2A: Missing values ───────────────────────────────────────────────────
    sec("Check 1 — Missing Values")
    if rpt["missing_before"]:
        miss_df = (
            pd.DataFrame.from_dict(rpt["missing_before"], orient="index", columns=["Missing Count"])
            .reset_index().rename(columns={"index": "Column"})
        )
        fig = px.bar(miss_df, x="Column", y="Missing Count",
                     title="Missing Values per Column",
                     color="Missing Count", color_continuous_scale="Reds",
                     text_auto=True)
        fig.update_layout(**PLT_BASE, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        box("good", "✅ <b>No missing values</b> found across all 17 columns.")

    # ── 2B: Duplicates ───────────────────────────────────────────────────────
    sec("Check 2 — Duplicate Invoice IDs")
    if rpt["duplicates_dropped"] == 0:
        box("good", "✅ <b>No duplicate Invoice IDs</b> detected. All 1 000 IDs are unique.")
    else:
        box("warn", f"⚠️ <b>{rpt['duplicates_dropped']}</b> duplicate rows removed. "
                    f"Affected IDs: {', '.join(rpt['duplicate_ids'][:10])}")

    # ── 2C: Category validation ──────────────────────────────────────────────
    sec("Check 3 — Categorical Value Validation")

    cat_rows = []
    for col in ["Customer type", "Gender", "Payment", "Product line"]:
        if col in rpt["invalid_categories"]:
            d = rpt["invalid_categories"][col]
            cat_rows.append({"Column": col, "Status": "❌ Invalid values found",
                             "Count": d["count"], "Invalid Values": str(d["values"])})
        else:
            from data_loader import ALLOWED_VALUES
            cat_rows.append({"Column": col, "Status": "✅ All valid",
                             "Count": 0, "Invalid Values": "—"})
    st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

    # ── 2D: Numeric validation ───────────────────────────────────────────────
    sec("Check 4 — Numeric Column Validation")

    if rpt["negative_found"]:
        for col, cnt in rpt["negative_found"].items():
            box("warn", f"⚠️ <b>[{col}]</b>: {cnt} negative values removed.")
    else:
        box("good", "✅ <b>No negative values</b> found in any numeric column.")

    if rpt["rating_oob"] > 0:
        box("warn", f"⚠️ <b>Rating</b>: {rpt['rating_oob']} rows outside 1–10 range removed.")
    else:
        box("good", "✅ <b>Rating</b>: all values within expected range of 1–10.")

    if rpt["bad_dates_dropped"] > 0:
        box("warn", f"⚠️ <b>Date</b>: {rpt['bad_dates_dropped']} rows had unparseable dates — removed.")
    else:
        box("good", "✅ <b>Date</b>: all 1 000 dates are valid M/D/YYYY format.")

    if rpt["non_numeric_dropped"] > 0:
        box("warn", f"⚠️ {rpt['non_numeric_dropped']} rows contained non-numeric values in numeric columns.")
    else:
        box("good", "✅ All numeric columns contain properly formatted numbers.")

    # ── 2E: Descriptive statistics ───────────────────────────────────────────
    sec("Check 5 — Descriptive Statistics (after cleaning)")
    num_cols = ["Unit price","Quantity","Sales","Tax 5%","cogs","gross income","gross margin percentage","Rating"]
    st.dataframe(
        df[num_cols].describe().round(3).T
        .rename(columns={"count":"Count","mean":"Mean","std":"Std Dev",
                         "min":"Min","25%":"Q1","50%":"Median","75%":"Q3","max":"Max"}),
        use_container_width=True,
    )

    box("info",
        "🔍 <b>Cleaning pipeline:</b> "
        "whitespace stripping → missing-value removal → duplicate removal → "
        "date parsing → numeric coercion → negative-value filter → "
        "category validation → rating range check.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3  — Sales Formula
# ══════════════════════════════════════════════════════════════════════════════
with T[2]:
    sec("Sales Calculation", step=3)

    st.markdown(
        '<div class="formula">Sales &nbsp;=&nbsp; Quantity &nbsp;×&nbsp; Unit Price</div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)
    kpi(f1, "Rows Recalculated", f"{rpt['final_rows']:,}")
    kpi(f2, "Formula Mismatches", f"{rpt['mismatched_sales']:,}")
    kpi(f3, "Accuracy", f"{100*(1 - rpt['mismatched_sales']/max(rpt['final_rows'],1)):.2f}%")

    if rpt["mismatched_sales"] == 0:
        box("good",
            "✅ <b>All Sales values match</b> Quantity × Unit Price exactly. "
            "No corrections were required.")
    else:
        box("warn",
            f"⚠️ <b>{rpt['mismatched_sales']}</b> rows had a stored Sales value that "
            "differed from Qty × Unit Price by more than $0.02. "
            "The formula value has been used as the authoritative figure.")

    sec("Sample: Quantity × Unit Price = Sales  (first 20 rows)")
    sample = sales_formula_sample(df)
    st.dataframe(
        sample.style.format({
            "Quantity"       : "{:.0f}",
            "Unit price"     : "${:.2f}",
            "Qty × Unit Price": "${:.4f}",
            "Original Sales" : "${:.4f}",
            "Difference"     : "${:.4f}",
        }).background_gradient(subset=["Difference"], cmap="RdYlGn_r"),
        use_container_width=True,
        height=440,
    )

    sec("Sales Distribution (after formula recalculation)")
    fig = px.histogram(
        df, x="Sales", nbins=40,
        title="Distribution of Recalculated Sales",
        labels={"Sales": "Sales (USD)"},
        color_discrete_sequence=["#2563eb"],
    )
    fig.update_layout(**PLT_BASE)
    st.plotly_chart(fig, use_container_width=True)

    box("info",
        "ℹ️ The original dataset includes a 5% tax and COGS columns. "
        "For this analysis, <b>Sales = Quantity × Unit Price</b> is used as "
        "the primary revenue metric (pre-tax revenue). "
        "Gross income = Sales × 4.76% (fixed margin).")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4  — Group & Summarise
# ══════════════════════════════════════════════════════════════════════════════
with T[3]:
    kpis = overall_kpis(df)

    sec("Overall KPIs (Totals, Counts & Averages)", step=4)

    row1 = st.columns(5)
    kpi(row1[0], "Total Transactions",   f"{kpis['total_transactions']:,}")
    kpi(row1[1], "Total Sales",          f"${kpis['total_sales']:,.0f}",       "USD")
    kpi(row1[2], "Total Gross Income",   f"${kpis['total_gross_income']:,.0f}", "USD")
    kpi(row1[3], "Total Units Sold",     f"{kpis['total_units_sold']:,}",       "units")
    kpi(row1[4], "Total Tax Collected",  f"${kpis['total_tax']:,.0f}",          "USD")

    st.markdown("<br>", unsafe_allow_html=True)
    row2 = st.columns(5)
    kpi(row2[0], "Avg Sale / Transaction", f"${kpis['avg_sales_per_txn']:,.2f}", "USD")
    kpi(row2[1], "Avg Unit Price",          f"${kpis['avg_unit_price']:,.2f}",    "USD")
    kpi(row2[2], "Avg Quantity / Txn",     f"{kpis['avg_quantity']:.2f}",         "items")
    kpi(row2[3], "Avg Customer Rating",    f"⭐ {kpis['avg_rating']}",            "/ 10")
    kpi(row2[4], "Total COGS",             f"${kpis['total_cogs']:,.0f}",          "USD")

    # ── Branch ───────────────────────────────────────────────────────────────
    sec("Summary by Branch")
    br = sales_by_branch(df)
    st.dataframe(
        br.style.format({
            "Total_Sales"       : "${:,.2f}",
            "Avg_Sales_per_Txn" : "${:,.2f}",
            "Avg_Unit_Price"    : "${:,.2f}",
            "Total_Gross_Income": "${:,.2f}",
            "Avg_Rating"        : "{:.2f}",
            "Avg_Qty_per_Txn"   : "{:.2f}",
        }).background_gradient(subset=["Total_Sales"], cmap="Blues"),
        use_container_width=True, hide_index=True,
    )

    # ── Product Line ─────────────────────────────────────────────────────────
    sec("Summary by Product Line")
    pr = sales_by_product(df)
    st.dataframe(
        pr.style.format({
            "Total_Sales"      : "${:,.2f}",
            "Avg_Unit_Price"   : "${:,.2f}",
            "Avg_Sales_per_Txn": "${:,.2f}",
            "Avg_Rating"       : "{:.2f}",
        }).background_gradient(subset=["Total_Sales"], cmap="Greens"),
        use_container_width=True, hide_index=True,
    )

    # ── Customer Type ─────────────────────────────────────────────────────────
    ct = sales_by_customer_type(df)
    gn = sales_by_gender(df)
    sec("Summary by Customer Type & Gender")
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption("By Customer Type")
        st.dataframe(ct.style.format({
            "Total_Sales": "${:,.2f}", "Avg_Sales_per_Txn": "${:,.2f}", "Avg_Rating": "{:.2f}",
        }), use_container_width=True, hide_index=True)
    with col_b:
        st.caption("By Gender")
        st.dataframe(gn.style.format({
            "Total_Sales": "${:,.2f}", "Avg_Sales_per_Txn": "${:,.2f}",
        }), use_container_width=True, hide_index=True)

    # ── Payment ───────────────────────────────────────────────────────────────
    sec("Summary by Payment Method")
    py = sales_by_payment(df)
    st.dataframe(py.style.format({
        "Total_Sales": "${:,.2f}", "Avg_Sales_per_Txn": "${:,.2f}",
    }), use_container_width=True, hide_index=True)

    # ── Monthly ───────────────────────────────────────────────────────────────
    sec("Monthly Summary (Totals, Counts, Averages)")
    mo = monthly_sales(df)
    st.dataframe(mo.style.format({
        "Total_Sales": "${:,.2f}", "Avg_Sales_per_Txn": "${:,.2f}",
    }), use_container_width=True, hide_index=True)

    # ── Full cross-tab ────────────────────────────────────────────────────────
    with st.expander("📋 Full Cross-Tab Summary  (Branch × Product × Customer × Gender × Payment)"):
        ft = full_summary_table(df)
        st.dataframe(
            ft.style.format({
                "Total_Sales"      : "${:,.2f}",
                "Avg_Sales_per_Txn": "${:,.2f}",
                "Avg_Unit_Price"   : "${:,.2f}",
                "Avg_Rating"       : "{:.2f}",
            }).background_gradient(subset=["Total_Sales"], cmap="Blues"),
            use_container_width=True, height=420,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5  — Charts
# ══════════════════════════════════════════════════════════════════════════════
with T[4]:
    sec("Visual Comparisons", step=5)

    br   = sales_by_branch(df)
    pr   = sales_by_product(df)
    ct   = sales_by_customer_type(df)
    gn   = sales_by_gender(df)
    py   = sales_by_payment(df)
    mo   = monthly_sales(df)
    dy   = sales_by_day(df)
    hr   = sales_by_hour(df)
    rd   = rating_by_product(df)
    gp   = gender_product_sales(df)
    pvt  = product_branch_pivot(df)

    # ── Row A: Branch ─────────────────────────────────────────────────────────
    sec("Branch Comparison")
    a1, a2 = st.columns(2)
    with a1:
        fig = px.bar(br, x="Branch", y="Total_Sales",
                     color="Branch", color_discrete_sequence=COLORS,
                     title="Total Sales by Branch",
                     text_auto=".2s",
                     labels={"Total_Sales": "Total Sales (USD)"})
        fig.update_layout(**PLT_BASE, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with a2:
        fig = px.bar(br, x="Branch", y="Transactions",
                     color="Branch", color_discrete_sequence=COLORS,
                     title="Number of Transactions by Branch",
                     text_auto=True,
                     labels={"Transactions": "Transactions"})
        fig.update_layout(**PLT_BASE, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    a3, a4 = st.columns(2)
    with a3:
        fig = px.bar(br, x="Branch", y="Avg_Rating",
                     color="Branch", color_discrete_sequence=COLORS,
                     title="Average Customer Rating by Branch",
                     text_auto=".2f",
                     labels={"Avg_Rating": "Avg Rating"})
        fig.update_layout(**PLT_BASE, yaxis_range=[0, 10], showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with a4:
        fig = px.bar(br, x="Branch", y="Total_Gross_Income",
                     color="Branch", color_discrete_sequence=COLORS,
                     title="Total Gross Income by Branch",
                     text_auto=".2s",
                     labels={"Total_Gross_Income": "Gross Income (USD)"})
        fig.update_layout(**PLT_BASE, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row B: Product Line ───────────────────────────────────────────────────
    sec("Product Line Comparison")
    b1, b2 = st.columns(2)
    with b1:
        fig = px.bar(pr.sort_values("Total_Sales"),
                     x="Total_Sales", y="Product line", orientation="h",
                     color="Total_Sales", color_continuous_scale="Teal",
                     title="Total Sales by Product Line",
                     text_auto=".2s",
                     labels={"Total_Sales": "Total Sales (USD)", "Product line": ""})
        fig.update_layout(**PLT_BASE, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with b2:
        fig = px.bar(pr.sort_values("Total_Units_Sold"),
                     x="Total_Units_Sold", y="Product line", orientation="h",
                     color="Total_Units_Sold", color_continuous_scale="Purples",
                     title="Units Sold by Product Line",
                     text_auto=True,
                     labels={"Total_Units_Sold": "Units Sold", "Product line": ""})
        fig.update_layout(**PLT_BASE, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    b3, b4 = st.columns(2)
    with b3:
        fig = px.bar(rd, x="Avg_Rating", y="Product line", orientation="h",
                     color="Avg_Rating", color_continuous_scale="RdYlGn",
                     title="Average Rating by Product Line",
                     text_auto=".2f",
                     labels={"Avg_Rating": "Avg Rating", "Product line": ""})
        fig.update_layout(**PLT_BASE, coloraxis_showscale=False, xaxis_range=[0, 10])
        st.plotly_chart(fig, use_container_width=True)
    with b4:
        fig = px.bar(gp, x="Product line", y="Sales",
                     color="Gender",
                     barmode="group",
                     color_discrete_sequence=["#2563eb", "#db2777"],
                     title="Sales by Gender × Product Line",
                     text_auto=".2s",
                     labels={"Sales": "Total Sales (USD)", "Product line": ""})
        fig.update_layout(**PLT_BASE, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row C: Customer & Payment ─────────────────────────────────────────────
    sec("Customer Type & Payment Method")
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(ct, names="Customer type", values="Total_Sales",
                     title="Sales Share — Customer Type",
                     color_discrete_sequence=COLORS, hole=0.42)
        fig.update_layout(**PLT_BASE)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(gn, names="Gender", values="Total_Sales",
                     title="Sales Share — Gender",
                     color_discrete_sequence=["#2563eb", "#db2777"], hole=0.42)
        fig.update_layout(**PLT_BASE)
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        fig = px.pie(py, names="Payment", values="Total_Sales",
                     title="Sales Share — Payment Method",
                     color_discrete_sequence=COLORS, hole=0.42)
        fig.update_layout(**PLT_BASE)
        st.plotly_chart(fig, use_container_width=True)

    c4, c5 = st.columns(2)
    with c4:
        fig = px.bar(ct, x="Customer type", y="Avg_Sales_per_Txn",
                     color="Customer type", color_discrete_sequence=COLORS,
                     title="Avg Sale / Transaction — Customer Type",
                     text_auto=".2f",
                     labels={"Avg_Sales_per_Txn": "Avg Sale (USD)"})
        fig.update_layout(**PLT_BASE, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c5:
        fig = px.bar(py, x="Payment", y="Transactions",
                     color="Payment", color_discrete_sequence=COLORS,
                     title="Transaction Count — Payment Method",
                     text_auto=True)
        fig.update_layout(**PLT_BASE, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row D: Time Trends ────────────────────────────────────────────────────
    sec("Time Trends")

    # Dual-axis monthly chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mo["Month"], y=mo["Total_Sales"],
        name="Total Sales", marker_color="#2563eb",
        text=[f"${v:,.0f}" for v in mo["Total_Sales"]],
        textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=mo["Month"], y=mo["Avg_Sales_per_Txn"],
        name="Avg Sale/Txn", mode="lines+markers",
        marker=dict(size=9, color="#f59e0b"),
        line=dict(width=2.5, color="#f59e0b"),
        yaxis="y2",
    ))
    fig.update_layout(
        **PLT_BASE,
        title="Monthly Sales vs Avg Sale per Transaction",
        yaxis=dict(title="Total Sales (USD)"),
        yaxis2=dict(title="Avg Sale (USD)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.12),
        barmode="overlay",
    )
    st.plotly_chart(fig, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        fig = px.bar(dy, x="Day_of_week", y="Total_Sales",
                     color="Total_Sales", color_continuous_scale="Blues",
                     title="Total Sales by Day of Week",
                     text_auto=".2s",
                     labels={"Day_of_week": "Day", "Total_Sales": "Total Sales (USD)"})
        fig.update_layout(**PLT_BASE, coloraxis_showscale=False, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)
    with d2:
        fig = px.line(hr, x="Hour", y="Total_Sales",
                      markers=True,
                      title="Sales by Hour of Day  (Peak Hours)",
                      labels={"Total_Sales": "Total Sales (USD)", "Hour": "Hour (24h)"},
                      color_discrete_sequence=["#7c3aed"])
        fig.update_traces(line_width=2.5, marker_size=8)
        fig.update_layout(**PLT_BASE)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row E: Heatmap ────────────────────────────────────────────────────────
    sec("Product Line × Branch Heatmap")
    fig = px.imshow(
        pvt, text_auto=".2s",
        color_continuous_scale="Blues",
        title="Total Sales (USD) — Product Line vs Branch",
        labels={"color": "Sales (USD)"},
        aspect="auto",
    )
    fig.update_layout(**PLT_BASE, margin=dict(t=56, b=20, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

    # ── Row F: Monthly units & transactions ───────────────────────────────────
    d3, d4 = st.columns(2)
    with d3:
        fig = px.bar(mo, x="Month", y="Total_Units_Sold",
                     color="Total_Units_Sold", color_continuous_scale="Teal",
                     title="Units Sold per Month",
                     text_auto=True)
        fig.update_layout(**PLT_BASE, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with d4:
        fig = px.line(mo, x="Month", y="Transactions",
                      markers=True, color_discrete_sequence=["#16a34a"],
                      title="Number of Transactions per Month")
        fig.update_traces(line_width=2.5, marker_size=9)
        fig.update_layout(**PLT_BASE)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 6  — Business Decisions
# ══════════════════════════════════════════════════════════════════════════════
with T[5]:
    kpis = overall_kpis(df)
    br   = sales_by_branch(df)
    pr   = sales_by_product(df)
    py   = sales_by_payment(df)
    ct   = sales_by_customer_type(df)
    rd   = rating_by_product(df)
    hr   = sales_by_hour(df)
    mo   = monthly_sales(df)

    def safe_val(frame, col, idx=0):
        return frame.iloc[idx][col] if len(frame) > idx else "N/A"

    top_branch        = safe_val(br, "Branch")
    top_branch_sales  = safe_val(br, "Total_Sales")
    bot_branch        = safe_val(br, "Branch", -1)
    top_product       = safe_val(pr, "Product line")
    bot_product       = safe_val(pr, "Product line", -1)
    top_payment       = safe_val(py, "Payment")
    top_rated_prod    = safe_val(rd, "Product line")
    top_rated_score   = safe_val(rd, "Avg_Rating")
    bot_rated_prod    = safe_val(rd, "Product line", -1)
    bot_rated_score   = safe_val(rd, "Avg_Rating", -1)
    peak_row          = hr.loc[hr["Total_Sales"].idxmax()] if len(hr) else None
    peak_hour_fmt     = f"{int(peak_row['Hour'])}:00 – {int(peak_row['Hour'])+1}:00" if peak_row is not None else "N/A"
    best_month        = safe_val(mo.loc[[mo["Total_Sales"].idxmax()]], "Month") if len(mo) else "N/A"
    worst_month       = safe_val(mo.loc[[mo["Total_Sales"].idxmin()]], "Month") if len(mo) else "N/A"
    member_s          = ct[ct["Customer type"] == "Member"]["Total_Sales"].sum()
    normal_s          = ct[ct["Customer type"] == "Normal"]["Total_Sales"].sum()
    member_pct        = member_s / (member_s + normal_s) * 100 if (member_s + normal_s) > 0 else 0

    sec("Data-Driven Business Recommendations", step=6)

    insights = [
        ("good",  "🏆 Best Performing Branch",
                  f"Branch <b>{top_branch}</b> generated <b>${top_branch_sales:,.0f}</b> in total sales — "
                  f"the highest across all branches. Replicate its operational model "
                  f"(staffing ratios, layout, promotions) in the other branches."),
        ("warn",  "📉 Underperforming Branch",
                  f"Branch <b>{bot_branch}</b> has the lowest sales. "
                  f"Conduct a root-cause investigation: foot traffic, product mix, staff training, "
                  f"or local marketing spend may need adjustment."),
        ("good",  "📦 Top Product Line",
                  f"<b>{top_product}</b> leads in revenue. "
                  f"Increase shelf space, stock levels, and targeted promotions for this category."),
        ("warn",  "📦 Weakest Product Line",
                  f"<b>{bot_product}</b> has the lowest revenue. "
                  f"Consider bundle deals, cross-promotions with top-selling lines, "
                  f"or reviewing its pricing strategy."),
        ("good",  "💳 Preferred Payment Channel",
                  f"<b>{top_payment}</b> is the most-used payment method. "
                  f"Ensure fast, reliable infrastructure for this channel at all POS terminals. "
                  f"Consider exclusive cashback or loyalty points for this method."),
        ("good",  "⭐ Highest Customer Satisfaction",
                  f"<b>{top_rated_prod}</b> has the best average rating of <b>{top_rated_score:.2f}/10</b>. "
                  f"Feature it prominently in marketing materials and near the store entrance."),
        ("warn",  "⚠️ Lowest-Rated Product Line",
                  f"<b>{bot_rated_prod}</b> has the lowest avg rating of <b>{bot_rated_score:.2f}/10</b>. "
                  f"Investigate product quality, packaging, and customer feedback to drive improvement."),
        ("good",  "⏰ Peak Sales Window",
                  f"The highest-revenue hour is <b>{peak_hour_fmt}</b>. "
                  f"Maximise staffing, stock replenishment, and promotional activity during this window."),
        ("good",  "📅 Best Sales Month",
                  f"<b>{best_month}</b> delivered the highest monthly revenue. "
                  f"Analyse what drove that performance (seasonal demand, promotions, events) "
                  f"and replicate it in slower months."),
        ("warn",  "📅 Slowest Month",
                  f"<b>{worst_month}</b> was the weakest month. "
                  f"Plan targeted campaigns (flash sales, loyalty events) to boost off-peak performance."),
        ("info",  "👤 Member vs Normal Customers",
                  f"Members account for <b>{member_pct:.1f}%</b> of total sales. "
                  f"{'Loyalty programs are working well — expand benefits to attract more sign-ups.' if member_pct >= 50 else 'Normal customers dominate — invest in converting them to members via sign-up incentives.'}"),
        ("info",  "💰 Upsell Opportunity",
                  f"Average sale per transaction is <b>${kpis['avg_sales_per_txn']:,.2f}</b>. "
                  f"Train staff in upselling complementary products to push this above "
                  f"<b>${kpis['avg_sales_per_txn']*1.15:,.2f}</b> (+15%)."),
        ("info",  "⭐ Overall Rating Health",
                  f"Average store rating: <b>{kpis['avg_rating']}/10</b>. "
                  f"{'Excellent — above 7, maintain current service levels.' if kpis['avg_rating'] >= 7 else 'Below 7 — urgent attention needed to service quality, cleanliness, and checkout speed.'}"),
    ]

    for kind, title, body in insights:
        st.markdown(
            f'<div class="box box-{kind}"><b>{title}</b><br>{body}</div>',
            unsafe_allow_html=True,
        )

    # ── Branch scorecard ──────────────────────────────────────────────────────
    sec("Branch Scorecard  (Normalised Multi-Metric Comparison)")
    if len(br) >= 2:
        metrics = [("Total_Sales","Total Sales","#2563eb"),
                   ("Transactions","Transactions","#7c3aed"),
                   ("Avg_Rating","Avg Rating","#16a34a"),
                   ("Total_Gross_Income","Gross Income","#d97706")]
        fig = go.Figure()
        for col, lbl, colour in metrics:
            vals = br[col]
            norm = (vals - vals.min()) / (vals.max() - vals.min() + 1e-9)
            fig.add_trace(go.Bar(
                name=lbl, x=br["Branch"], y=norm,
                marker_color=colour,
                text=br[col].round(1), textposition="inside",
            ))
        fig.update_layout(
            **PLT_BASE,
            title="Normalised Branch Scorecard (0 = worst, 1 = best)",
            barmode="group",
            yaxis_title="Normalised Score  (0–1)",
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Top 10 transactions ───────────────────────────────────────────────────
    sec("Top 10 Highest-Value Transactions")
    top10 = (
        df[["Invoice ID","Branch","Product line","Customer type",
            "Gender","Payment","Quantity","Unit price","Sales","Rating"]]
        .sort_values("Sales", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top10.index += 1
    st.dataframe(
        top10.style
        .format({"Unit price": "${:,.2f}", "Sales": "${:,.2f}", "Rating": "{:.1f}"})
        .background_gradient(subset=["Sales"], cmap="Blues"),
        use_container_width=True,
    )

    box("info",
        "📌 <b>How to use these insights:</b> Each recommendation is directly derived "
        "from the aggregated data in Step 4. Use the sidebar filters to drill into "
        "a specific branch, product line, or date range and regenerate all insights "
        "for that segment.")


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:.78rem;color:#94a3b8'>"
    "SuperMarket Sales Analytics &nbsp;·&nbsp; Dataset: Jan–Mar 2019 &nbsp;·&nbsp; "
    "Built with Streamlit &amp; Plotly"
    "</div>",
    unsafe_allow_html=True,
)
