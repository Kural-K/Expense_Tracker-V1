import streamlit as st
import pandas as pd
import os
from datetime import date

# ── Config ────────────────────────────────────────────────────────────────────
CSV_FILE   = "expenses.csv"
CATEGORIES = ["Food", "Rent", "Transport", "Shopping", "Health",
              "Entertainment", "Utilities", "Education", "Other"]

st.set_page_config(page_title="$ Expense Tracker", page_icon="$", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; }

/* Rich dark green money background with money symbol pattern */
.stApp {
    background-color: #050f07;
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Ctext x='10'  y='50'  font-size='36' fill='%23c9a84c08' font-family='serif' font-weight='bold'%3E%24%3C/text%3E%3Ctext x='80'  y='120' font-size='28' fill='%23c9a84c06' font-family='serif' font-weight='bold'%3E%E2%82%B9%3C/text%3E%3Ctext x='140' y='60'  font-size='30' fill='%23c9a84c07' font-family='serif' font-weight='bold'%3E%E2%82%AC%3C/text%3E%3Ctext x='30'  y='160' font-size='26' fill='%23c9a84c06' font-family='serif' font-weight='bold'%3E%C2%A3%3C/text%3E%3Ctext x='120' y='180' font-size='32' fill='%23c9a84c07' font-family='serif' font-weight='bold'%3E%C2%A5%3C/text%3E%3Ctext x='60'  y='90'  font-size='18' fill='%230d2e0508' font-family='serif'%3E%E2%97%88%3C/text%3E%3Ctext x='160' y='140' font-size='18' fill='%230d2e0508' font-family='serif'%3E%E2%97%88%3C/text%3E%3C/svg%3E"),
        radial-gradient(ellipse at top left,  #0a2e1a 0%, transparent 60%),
        radial-gradient(ellipse at bottom right, #1a2e0a 0%, transparent 60%),
        linear-gradient(160deg, #050f07 0%, #0d1f0f 40%, #091a0b 100%);
    color: #e8d9a0;
}

/* Gold shimmer banner at the very top */
.stApp::before {
    content: "";
    display: block;
    height: 3px;
    background: linear-gradient(90deg, transparent, #c9a84c, #f0d060, #c9a84c, transparent);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071a0a 0%, #0d2410 100%);
    border-right: 1px solid #c9a84c55;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0d2410 60%, #162e12 100%);
    border: 1px solid #c9a84c88;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 4px 24px #000a, inset 0 1px 0 #c9a84c33;
}
.metric-card .value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f0d060;
    text-shadow: 0 0 12px #c9a84c88;
}
.metric-card .label { font-size: 0.75rem; color: #7a9e7a; margin-top: 4px; }

/* Expense rows */
.expense-row {
    background: linear-gradient(90deg, #0d2410, #122814);
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 3px solid #c9a84c;
    box-shadow: 0 2px 8px #0005;
}

/* Buttons */
div[data-testid="stButton"] button {
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    background: linear-gradient(135deg, #c9a84c, #f0d060) !important;
    color: #050f07 !important;
    border: none !important;
}

/* Form */
div[data-testid="stForm"] {
    background: linear-gradient(135deg, #0d2410, #122814);
    border: 1px solid #c9a84c66;
    border-radius: 12px;
    padding: 20px;
}

/* Inputs */
.stSelectbox > div, .stTextInput > div, .stNumberInput > div {
    background: #071a0a !important;
    border-color: #c9a84c44 !important;
}

/* Headings */
h1 {
    font-family: 'Playfair Display', serif !important;
    color: #f0d060 !important;
    text-shadow: 0 0 20px #c9a84c66;
    letter-spacing: 1px;
}
h2, h3 { color: #c9a84c !important; }

/* Tabs */
button[data-baseweb="tab"] {
    color: #7a9e7a !important;
    font-family: 'JetBrains Mono', monospace !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #f0d060 !important;
    border-bottom-color: #f0d060 !important;
}

/* Divider */
hr { border-color: #c9a84c33 !important; }

/* Dataframe */
.stDataFrame { border: 1px solid #c9a84c33; border-radius: 8px; }

/* Caption / subtext */
.stCaption { color: #7a9e7a !important; }
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        return df
    return pd.DataFrame(columns=["date", "category", "amount", "note"])

def save_data(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False)

# ── State ─────────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# ── Header ────────────────────────────────────────────────────────────────────
st.title("$ Expense Tracker")
st.caption("Track · Analyze · Save — all from your browser")
st.divider()

# ── Top Metrics ───────────────────────────────────────────────────────────────
total      = df["amount"].sum()
this_month = df[df["date"].dt.to_period("M") == pd.Period(date.today(), "M")]["amount"].sum() \
             if not df.empty else 0
num        = len(df)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="value">₹{total:,.0f}</div>
        <div class="label">Total Spent</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="value">₹{this_month:,.0f}</div>
        <div class="label">This Month</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="value">{num}</div>
        <div class="label">Transactions</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sidebar: Add Expense ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ➕ Add Expense")
    with st.form("add_form", clear_on_submit=True):
        exp_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", CATEGORIES)
        amount   = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")
        note     = st.text_input("Note (optional)")
        submitted = st.form_submit_button("✅ Add Expense", use_container_width=True)

    if submitted:
        new_row = pd.DataFrame([{
            "date": pd.Timestamp(exp_date),
            "category": category,
            "amount": round(amount, 2),
            "note": note
        }])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_data(st.session_state.df)
        st.success(f"₹{amount:.2f} added under {category}!")
        st.rerun()

    st.divider()
    st.markdown("### 📁 Data")
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "rb") as f:
            st.download_button("⬇️ Download CSV", f, file_name="expenses.csv",
                               mime="text/csv", use_container_width=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 View & Delete", "📊 Monthly Summary", "📈 Charts"])

# ── Tab 1: View & Delete ──────────────────────────────────────────────────────
with tab1:
    st.markdown("#### All Expenses")
    if df.empty:
        st.info("No expenses yet. Add one from the sidebar!")
    else:
        col1, col2 = st.columns([2, 2])
        with col1:
            filt_cat = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="filt")
        with col2:
            sort_by = st.selectbox("Sort by", ["Date (newest)", "Date (oldest)", "Amount (high)", "Amount (low)"])

        view = df.copy()
        if filt_cat != "All":
            view = view[view["category"] == filt_cat]

        if sort_by == "Date (newest)":     view = view.sort_values("date", ascending=False)
        elif sort_by == "Date (oldest)":   view = view.sort_values("date", ascending=True)
        elif sort_by == "Amount (high)":   view = view.sort_values("amount", ascending=False)
        elif sort_by == "Amount (low)":    view = view.sort_values("amount", ascending=True)

        view_display = view.copy()
        view_display["date"]   = view_display["date"].dt.strftime("%Y-%m-%d")
        view_display["amount"] = view_display["amount"].apply(lambda x: f"₹{x:,.2f}")
        view_display.index     = range(1, len(view_display)+1)

        st.dataframe(view_display[["date","category","amount","note"]],
                     use_container_width=True)

        st.markdown("#### 🗑 Delete an Expense")
        del_idx = st.number_input("Row number to delete (from table above)",
                                  min_value=1, max_value=len(view), step=1, value=1)
        if st.button("Delete selected row", type="primary"):
            actual_idx = view.index[del_idx - 1]
            st.session_state.df = st.session_state.df.drop(index=actual_idx).reset_index(drop=True)
            save_data(st.session_state.df)
            st.success("Expense deleted!")
            st.rerun()

# ── Tab 2: Monthly Summary ────────────────────────────────────────────────────
with tab2:
    st.markdown("#### Monthly Breakdown")
    if df.empty:
        st.info("No data yet!")
    else:
        months = sorted(df["date"].dt.to_period("M").astype(str).unique(), reverse=True)
        sel_month = st.selectbox("Select month", months)

        mdf = df[df["date"].dt.to_period("M").astype(str) == sel_month]
        grand = mdf["amount"].sum()
        st.markdown(f"**Total for {sel_month}: ₹{grand:,.2f}**")

        summary = mdf.groupby("category")["amount"].sum().sort_values(ascending=False)
        for cat, amt in summary.items():
            pct = (amt / grand * 100) if grand > 0 else 0
            st.markdown(f"""
            <div class="expense-row">
                <span>{cat}</span>
                <span style="color:#f7a26a;font-weight:700;">₹{amt:,.2f} &nbsp;
                <span style="color:#9090b0;font-size:0.8rem;">({pct:.1f}%)</span></span>
            </div>""", unsafe_allow_html=True)

        # Progress bars
        st.markdown("<br>", unsafe_allow_html=True)
        for cat, amt in summary.items():
            pct = int((amt / grand * 100)) if grand > 0 else 0
            st.markdown(f"`{cat}`")
            st.progress(pct)

# ── Tab 3: Charts ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### Spending Charts")
    if df.empty:
        st.info("No data yet!")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**By Category (All Time)**")
            cat_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(cat_totals)

        with col2:
            st.markdown("**Monthly Trend**")
            monthly = df.groupby(df["date"].dt.to_period("M").astype(str))["amount"].sum()
            st.line_chart(monthly)

        st.markdown("**Daily Spending**")
        daily = df.groupby(df["date"].dt.date)["amount"].sum()
        st.area_chart(daily)