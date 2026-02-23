import streamlit as st
import pandas as pd
import os
import json
from datetime import date, datetime
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
CSV_FILE     = "expenses.csv"
BUDGET_FILE  = "budgets.json"
CATEGORIES   = ["Food", "Rent", "Transport", "Shopping", "Health",
                "Entertainment", "Utilities", "Education", "Other"]

st.set_page_config(page_title="$ Expense Tracker", page_icon="$", layout="centered")

# ── Theme ─────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

DM = st.session_state.dark_mode

# Color tokens
if DM:
    BG       = "#050f07"
    SURFACE  = "#0d2410"
    BORDER   = "#c9a84c55"
    TEXT     = "#e8d9a0"
    SUBTEXT  = "#7a9e7a"
    GOLD     = "#f0d060"
    GOLD2    = "#c9a84c"
    RED      = "#f76a6a"
    GREEN    = "#6af7a2"
    PATTERN  = "%23c9a84c08"
    PATTERN2 = "%23c9a84c06"
    INPUT_BG = "#071a0a"
else:
    BG       = "#f5f0e8"
    SURFACE  = "#fffdf5"
    BORDER   = "#c9a84c88"
    TEXT     = "#1a1a0a"
    SUBTEXT  = "#5a6e5a"
    GOLD     = "#a07820"
    GOLD2    = "#c9a84c"
    RED      = "#c0392b"
    GREEN    = "#1a8a4a"
    PATTERN  = "%23c9a84c10"
    PATTERN2 = "%23c9a84c08"
    INPUT_BG = "#faf5e8"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {{ font-family: 'JetBrains Mono', monospace; }}

.stApp {{
    background-color: {BG};
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Ctext x='10' y='50' font-size='36' fill='{PATTERN}' font-family='serif' font-weight='bold'%3E%24%3C/text%3E%3Ctext x='80' y='120' font-size='28' fill='{PATTERN2}' font-family='serif' font-weight='bold'%3E%E2%82%B9%3C/text%3E%3Ctext x='140' y='60' font-size='30' fill='{PATTERN}' font-family='serif' font-weight='bold'%3E%E2%82%AC%3C/text%3E%3Ctext x='30' y='160' font-size='26' fill='{PATTERN2}' font-family='serif' font-weight='bold'%3E%C2%A3%3C/text%3E%3Ctext x='120' y='180' font-size='32' fill='{PATTERN}' font-family='serif' font-weight='bold'%3E%C2%A5%3C/text%3E%3C/svg%3E"),
        linear-gradient(160deg, {BG} 0%, {SURFACE} 50%, {BG} 100%);
    color: {TEXT};
}}
.stApp::before {{
    content: "";
    display: block;
    height: 3px;
    background: linear-gradient(90deg, transparent, {GOLD2}, {GOLD}, {GOLD2}, transparent);
}}
section[data-testid="stSidebar"] {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
}}
.metric-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 4px 18px #0003;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.metric-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 28px #0005;
    border-color: {GOLD};
}}
.metric-card .value {{ font-size: 1.8rem; font-weight: 700; color: {GOLD}; }}
.metric-card .label {{ font-size: 0.75rem; color: {SUBTEXT}; margin-top: 4px; }}
.expense-row {{
    background: {SURFACE};
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 3px solid {GOLD2};
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.expense-row:hover {{ border-color: {GOLD}; box-shadow: 0 2px 12px #0003; }}
div[data-testid="stButton"] button {{
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    transition: transform 0.15s;
}}
div[data-testid="stButton"] button:hover {{ transform: scale(1.02); }}
div[data-testid="stForm"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px;
}}
h1 {{
    font-family: 'Playfair Display', serif !important;
    color: {GOLD} !important;
    text-shadow: 0 0 20px {GOLD2}44;
}}
h2, h3, h4 {{ color: {GOLD2} !important; }}
hr {{ border-color: {BORDER} !important; }}
.stDataFrame {{ border: 1px solid {BORDER}; border-radius: 8px; }}
.stCaption {{ color: {SUBTEXT} !important; }}
.budget-bar-wrap {{
    background: {BG};
    border-radius: 99px;
    height: 14px;
    margin: 4px 0 10px;
    overflow: hidden;
    border: 1px solid {BORDER};
}}
.budget-bar-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}}
.tag {{
    display: inline-block;
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 99px;
    padding: 2px 10px;
    font-size: 0.75rem;
    color: {GOLD2};
    margin: 2px;
}}
.empty-state {{
    text-align: center;
    padding: 48px 20px;
    color: {SUBTEXT};
}}
.empty-state .icon {{ font-size: 3rem; }}
.empty-state p {{ margin-top: 12px; font-size: 1rem; }}
</style>
""", unsafe_allow_html=True)

# ── Confetti JS ───────────────────────────────────────────────────────────────
CONFETTI_JS = """
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
<script>
confetti({ particleCount: 180, spread: 90, origin: { y: 0.5 },
           colors: ['#f0d060','#c9a84c','#6af7a2','#ffffff','#f7a26a'] });
</script>
"""

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        if "note" not in df.columns: df["note"] = ""
        return df
    return pd.DataFrame(columns=["date","category","amount","note"])

def save_data(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False)

def load_budgets() -> dict:
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE) as f:
            return json.load(f)
    return {}

def save_budgets(b: dict):
    with open(BUDGET_FILE, "w") as f:
        json.dump(b, f)

# ── Session state ─────────────────────────────────────────────────────────────
if "df"           not in st.session_state: st.session_state.df       = load_data()
if "budgets"      not in st.session_state: st.session_state.budgets  = load_budgets()
if "edit_idx"     not in st.session_state: st.session_state.edit_idx = None
if "delete_idx"   not in st.session_state: st.session_state.delete_idx = None
if "confetti_fired" not in st.session_state: st.session_state.confetti_fired = set()

df      = st.session_state.df
budgets = st.session_state.budgets

# ── Header row ────────────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([5, 1])
with hcol1:
    st.title("$ Expense Tracker")
    st.caption("Track · Analyze · Save — all from your browser")
with hcol2:
    st.markdown("<br>", unsafe_allow_html=True)
    theme_label = "☀️ Light" if DM else "🌙 Dark"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.divider()

# ── Top metrics ───────────────────────────────────────────────────────────────
total      = df["amount"].sum()
this_month = df[df["date"].dt.to_period("M") == pd.Period(date.today(), "M")]["amount"].sum() \
             if not df.empty else 0.0
avg_day    = (df.groupby(df["date"].dt.date)["amount"].sum().mean()) if not df.empty else 0.0

c1, c2, c3 = st.columns(3)
for col, val, label in [
    (c1, f"₹{total:,.0f}",     "Total Spent"),
    (c2, f"₹{this_month:,.0f}","This Month"),
    (c3, f"₹{avg_day:,.0f}",   "Avg / Day"),
]:
    with col:
        st.markdown(f"""<div class="metric-card">
            <div class="value">{val}</div>
            <div class="label">{label}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ➕ Add Expense")
    with st.form("add_form", clear_on_submit=True):
        exp_date  = st.date_input("Date", value=date.today())
        category  = st.selectbox("Category", CATEGORIES)
        amount    = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")
        note      = st.text_input("Note (optional)")
        submitted = st.form_submit_button("✅ Add Expense", use_container_width=True)

    if submitted:
        new_row = pd.DataFrame([{"date": pd.Timestamp(exp_date),
                                  "category": category,
                                  "amount": round(amount, 2),
                                  "note": note}])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        save_data(st.session_state.df)
        st.success(f"₹{amount:.2f} added under {category}!")
        st.rerun()

    st.divider()

    # Budget settings
    st.markdown("### 💰 Budget Limits")
    with st.expander("Set monthly budgets"):
        for cat in CATEGORIES:
            cur = budgets.get(cat, 0)
            val = st.number_input(cat, min_value=0, value=int(cur), step=500, key=f"bgt_{cat}")
            budgets[cat] = val
        if st.button("💾 Save Budgets", use_container_width=True):
            st.session_state.budgets = budgets
            save_budgets(budgets)
            st.success("Budgets saved!")

    st.divider()
    st.markdown("### 📁 Export")
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "rb") as f:
            st.download_button("⬇️ Download CSV", f, file_name="expenses.csv",
                               mime="text/csv", use_container_width=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 View & Manage", "📊 Analytics", "🎯 Budgets"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — VIEW & MANAGE
# ════════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Search & Filter bar ───────────────────────────────────────────────────
    st.markdown("#### 🔍 Search & Filter")
    fc1, fc2 = st.columns(2)
    with fc1:
        search_q  = st.text_input("Search notes", placeholder="e.g. lunch, gym…", label_visibility="collapsed")
        filt_cat  = st.selectbox("Category", ["All"] + CATEGORIES, key="filt_cat")
    with fc2:
        date_from = st.date_input("From", value=None, key="date_from")
        date_to   = st.date_input("To",   value=None, key="date_to")

    amt_col1, amt_col2 = st.columns(2)
    with amt_col1:
        amt_min = st.number_input("Min amount", min_value=0.0, value=0.0, step=100.0)
    with amt_col2:
        amt_max = st.number_input("Max amount", min_value=0.0, value=0.0, step=100.0,
                                  help="0 = no limit")

    sort_by = st.selectbox("Sort by", ["Date (newest)", "Date (oldest)",
                                        "Amount (high→low)", "Amount (low→high)"])

    # Apply filters
    view = df.copy()
    if search_q:
        view = view[view["note"].str.contains(search_q, case=False, na=False)]
    if filt_cat != "All":
        view = view[view["category"] == filt_cat]
    if date_from:
        view = view[view["date"].dt.date >= date_from]
    if date_to:
        view = view[view["date"].dt.date <= date_to]
    if amt_min > 0:
        view = view[view["amount"] >= amt_min]
    if amt_max > 0:
        view = view[view["amount"] <= amt_max]

    sort_map = {
        "Date (newest)":     ("date",   False),
        "Date (oldest)":     ("date",   True),
        "Amount (high→low)": ("amount", False),
        "Amount (low→high)": ("amount", True),
    }
    col_s, asc_s = sort_map[sort_by]
    view = view.sort_values(col_s, ascending=asc_s)

    st.divider()
    st.markdown(f"#### 📋 Expenses &nbsp; <span style='color:{SUBTEXT};font-size:0.8rem;'>{len(view)} result(s)</span>", unsafe_allow_html=True)

    if view.empty:
        st.markdown(f"""<div class="empty-state">
            <div class="icon">🪙</div>
            <p>No expenses found.<br>Try adjusting your filters or add a new expense!</p>
        </div>""", unsafe_allow_html=True)
    else:
        for i, (idx, row) in enumerate(view.iterrows()):
            col_info, col_amt, col_edit, col_del = st.columns([4, 2, 1, 1])
            with col_info:
                st.markdown(f"""<div style='color:{TEXT};font-size:0.85rem;'>
                    <b>{row['category']}</b> &nbsp;
                    <span style='color:{SUBTEXT};font-size:0.75rem;'>{pd.Timestamp(row['date']).strftime('%d %b %Y')}</span><br>
                    <span style='color:{SUBTEXT};font-size:0.78rem;'>{row['note'] or '—'}</span>
                </div>""", unsafe_allow_html=True)
            with col_amt:
                st.markdown(f"<div style='color:{GOLD};font-weight:700;padding-top:8px;'>₹{row['amount']:,.2f}</div>",
                            unsafe_allow_html=True)
            with col_edit:
                if st.button("✏️", key=f"edit_{idx}", help="Edit"):
                    st.session_state.edit_idx = idx
                    st.rerun()
            with col_del:
                if st.button("🗑", key=f"del_{idx}", help="Delete"):
                    st.session_state.delete_idx = idx
                    st.rerun()

    # ── Delete confirmation dialog ────────────────────────────────────────────
    if st.session_state.delete_idx is not None:
        didx = st.session_state.delete_idx
        if didx in st.session_state.df.index:
            row = st.session_state.df.loc[didx]
            st.warning(f"⚠️ Delete **{row['category']}** — ₹{row['amount']:.2f} on {pd.Timestamp(row['date']).strftime('%d %b %Y')}?")
            dc1, dc2 = st.columns(2)
            with dc1:
                if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                    st.session_state.df = st.session_state.df.drop(index=didx).reset_index(drop=True)
                    save_data(st.session_state.df)
                    st.session_state.delete_idx = None
                    st.success("Deleted!")
                    st.rerun()
            with dc2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.delete_idx = None
                    st.rerun()

    # ── Edit modal ────────────────────────────────────────────────────────────
    if st.session_state.edit_idx is not None:
        eidx = st.session_state.edit_idx
        if eidx in st.session_state.df.index:
            row = st.session_state.df.loc[eidx]
            st.divider()
            st.markdown("#### ✏️ Edit Expense")
            with st.form("edit_form"):
                e_date = st.date_input("Date", value=pd.Timestamp(row["date"]).date())
                e_cat  = st.selectbox("Category", CATEGORIES,
                                      index=CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else 0)
                e_amt  = st.number_input("Amount (₹)", min_value=0.01,
                                          value=float(row["amount"]), step=10.0, format="%.2f")
                e_note = st.text_input("Note", value=str(row["note"]) if pd.notna(row["note"]) else "")
                sc1, sc2 = st.columns(2)
                with sc1:
                    save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)
                with sc2:
                    cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)

            if save_edit:
                st.session_state.df.at[eidx, "date"]     = pd.Timestamp(e_date)
                st.session_state.df.at[eidx, "category"] = e_cat
                st.session_state.df.at[eidx, "amount"]   = round(e_amt, 2)
                st.session_state.df.at[eidx, "note"]     = e_note
                save_data(st.session_state.df)
                st.session_state.edit_idx = None
                st.success("✅ Expense updated!")
                st.rerun()
            if cancel_edit:
                st.session_state.edit_idx = None
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    if df.empty:
        st.markdown(f"""<div class="empty-state">
            <div class="icon">📊</div>
            <p>No data to analyze yet.<br>Start adding expenses!</p>
        </div>""", unsafe_allow_html=True)
    else:
        months     = sorted(df["date"].dt.to_period("M").astype(str).unique(), reverse=True)
        sel_month  = st.selectbox("Select month for analysis", months, key="ana_month")
        mdf        = df[df["date"].dt.to_period("M").astype(str) == sel_month]
        grand      = mdf["amount"].sum()
        cat_totals = mdf.groupby("category")["amount"].sum().sort_values(ascending=False)

        # Highlights
        h1, h2, h3 = st.columns(3)
        top_cat  = cat_totals.idxmax() if not cat_totals.empty else "—"
        top_amt  = cat_totals.max()    if not cat_totals.empty else 0
        num_txns = len(mdf)
        with h1:
            st.markdown(f"""<div class="metric-card">
                <div class="value">{top_cat}</div>
                <div class="label">Top Category</div></div>""", unsafe_allow_html=True)
        with h2:
            st.markdown(f"""<div class="metric-card">
                <div class="value">₹{top_amt:,.0f}</div>
                <div class="label">Highest Spend</div></div>""", unsafe_allow_html=True)
        with h3:
            st.markdown(f"""<div class="metric-card">
                <div class="value">{num_txns}</div>
                <div class="label">Transactions</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts side by side
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("**🥧 Category Breakdown**")
            if not cat_totals.empty:
                st.bar_chart(cat_totals)

        with ch2:
            st.markdown("**📈 Monthly Trend**")
            monthly = df.groupby(df["date"].dt.to_period("M").astype(str))["amount"].sum()
            st.line_chart(monthly)

        st.markdown("**💸 Daily Spending**")
        daily = mdf.groupby(mdf["date"].dt.date)["amount"].sum()
        st.area_chart(daily)

        # Pie-style breakdown table
        st.markdown("**🥧 Pie Breakdown (text)**")
        for cat, amt in cat_totals.items():
            pct = (amt / grand * 100) if grand > 0 else 0
            bar_color = "#f0d060" if pct > 30 else "#6af7a2" if pct < 10 else "#c9a84c"
            st.markdown(f"""
            <div class="expense-row">
                <span>{cat}</span>
                <span style="color:{GOLD};font-weight:700;">
                    ₹{amt:,.2f}
                    <span style="color:{SUBTEXT};font-size:0.8rem;"> ({pct:.1f}%)</span>
                </span>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="budget-bar-wrap">
                <div class="budget-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — BUDGETS
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 🎯 Monthly Budget Tracker")
    st.caption("Set budgets in the sidebar → see your progress here")

    cur_month    = date.today().strftime("%Y-%m")
    month_df     = df[df["date"].dt.to_period("M").astype(str) == cur_month]
    spent_by_cat = month_df.groupby("category")["amount"].sum()

    has_any_budget = any(v > 0 for v in budgets.values())
    if not has_any_budget:
        st.markdown(f"""<div class="empty-state">
            <div class="icon">🎯</div>
            <p>No budgets set yet.<br>Use the sidebar to set monthly limits per category!</p>
        </div>""", unsafe_allow_html=True)
    else:
        all_under = True
        for cat in CATEGORIES:
            limit = budgets.get(cat, 0)
            if limit <= 0:
                continue
            spent = float(spent_by_cat.get(cat, 0))
            pct   = min((spent / limit * 100), 100)
            over  = spent > limit
            if over:
                all_under = False

            bar_color = "#f76a6a" if over else "#f0d060" if pct > 75 else "#6af7a2"
            status    = "🔴 OVER BUDGET" if over else f"🟡 {pct:.0f}%" if pct > 75 else f"🟢 {pct:.0f}%"

            st.markdown(f"""
            <div class="expense-row" style="border-left-color:{bar_color};">
                <div>
                    <b>{cat}</b><br>
                    <span style="color:{SUBTEXT};font-size:0.78rem;">
                        ₹{spent:,.0f} / ₹{limit:,.0f}
                    </span>
                </div>
                <span style="color:{bar_color};font-weight:700;">{status}</span>
            </div>
            <div class="budget-bar-wrap">
                <div class="budget-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
            </div>""", unsafe_allow_html=True)

        # 🎉 Confetti if ALL budgets are under limit
        month_key = f"confetti_{cur_month}"
        if all_under and month_key not in st.session_state.confetti_fired:
            st.success("🎉 Amazing! You're under budget in ALL categories this month!")
            st.components.v1.html(CONFETTI_JS, height=0)
            st.session_state.confetti_fired.add(month_key)