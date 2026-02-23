import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, json, calendar
from datetime import date, datetime, timedelta
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
CSV_FILE       = "expenses.csv"
BUDGET_FILE    = "budgets.json"
INCOME_FILE    = "income.json"
RECURRING_FILE = "recurring.json"

CATEGORIES = ["Food", "Rent", "Transport", "Shopping", "Health",
              "Entertainment", "Utilities", "Education", "Other"]

st.set_page_config(page_title="$ WalletWatch", page_icon="💸", layout="wide")

# ── Theme ─────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
DM = st.session_state.dark_mode

if DM:
    BG      = "#050f07";  SURFACE = "#0d2410";  BORDER  = "#c9a84c55"
    TEXT    = "#e8d9a0";  SUBTEXT = "#7a9e7a";  GOLD    = "#f0d060"
    GOLD2   = "#c9a84c";  RED     = "#f76a6a";  GREEN   = "#6af7a2"
    PAT     = "%23c9a84c08"; PAT2 = "%23c9a84c06"
    PLY_TPL = "plotly_dark"; PLY_BG = "#050f07"; PLY_PAPER = "#0d2410"
    PLY_BORDER = "rgba(201,168,76,0.33)"
else:
    BG      = "#f5f0e8";  SURFACE = "#fffdf5";  BORDER  = "#c9a84c88"
    TEXT    = "#1a1a0a";  SUBTEXT = "#5a6e5a";  GOLD    = "#a07820"
    GOLD2   = "#c9a84c";  RED     = "#c0392b";  GREEN   = "#1a8a4a"
    PAT     = "%23c9a84c10"; PAT2 = "%23c9a84c08"
    PLY_TPL = "plotly";    PLY_BG = "#f5f0e8"; PLY_PAPER = "#fffdf5"
    PLY_BORDER = "rgba(201,168,76,0.53)"

GOLD_PALETTE = ["#f0d060","#c9a84c","#e8b84b","#f7c948","#d4a017",
                "#6af7a2","#f76a6a","#6ab8f7","#f76af0","#a2f76a"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=JetBrains+Mono:wght@400;700&display=swap');
html, body, [class*="css"] {{ font-family: 'JetBrains Mono', monospace; }}
.stApp {{
    background-color: {BG};
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Ctext x='10' y='50' font-size='36' fill='{PAT}' font-family='serif' font-weight='bold'%3E%24%3C/text%3E%3Ctext x='80' y='120' font-size='28' fill='{PAT2}' font-family='serif' font-weight='bold'%3E%E2%82%B9%3C/text%3E%3Ctext x='140' y='60' font-size='30' fill='{PAT}' font-family='serif' font-weight='bold'%3E%E2%82%AC%3C/text%3E%3Ctext x='30' y='160' font-size='26' fill='{PAT2}' font-family='serif' font-weight='bold'%3E%C2%A3%3C/text%3E%3Ctext x='120' y='180' font-size='32' fill='{PAT}' font-family='serif' font-weight='bold'%3E%C2%A5%3C/text%3E%3C/svg%3E"),
        linear-gradient(160deg, {BG} 0%, {SURFACE} 50%, {BG} 100%);
    color: {TEXT};
}}
.stApp::before {{ content:""; display:block; height:3px;
    background:linear-gradient(90deg,transparent,{GOLD2},{GOLD},{GOLD2},transparent); }}
section[data-testid="stSidebar"] {{ background:{SURFACE}; border-right:1px solid {BORDER}; }}
.metric-card {{
    background:{SURFACE}; border:1px solid {BORDER}; border-radius:12px;
    padding:16px 18px; text-align:center;
    box-shadow:0 4px 18px #0003; transition:transform .2s,box-shadow .2s;
}}
.metric-card:hover {{ transform:translateY(-2px); box-shadow:0 8px 28px #0005; border-color:{GOLD}; }}
.metric-card .value {{ font-size:1.6rem; font-weight:700; color:{GOLD}; }}
.metric-card .label {{ font-size:0.72rem; color:{SUBTEXT}; margin-top:4px; }}
.metric-card .delta {{ font-size:0.75rem; margin-top:2px; }}
.insight-card {{
    background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px;
    padding:14px 16px; margin-bottom:10px; border-left:3px solid {GOLD};
}}
.insight-card.warn  {{ border-left-color:{RED}; }}
.insight-card.good  {{ border-left-color:{GREEN}; }}
.expense-row {{
    background:{SURFACE}; border-radius:8px; padding:10px 14px; margin-bottom:5px;
    display:flex; justify-content:space-between; align-items:center;
    border-left:3px solid {GOLD2}; transition:border-color .2s,box-shadow .2s;
}}
.expense-row:hover {{ border-color:{GOLD}; box-shadow:0 2px 12px #0003; }}
.budget-bar-wrap {{
    background:{BG}; border-radius:99px; height:12px; margin:3px 0 8px;
    overflow:hidden; border:1px solid {BORDER};
}}
.budget-bar-fill {{ height:100%; border-radius:99px; transition:width .6s ease; }}
.recurring-badge {{
    display:inline-block; background:{SURFACE}; border:1px solid {GOLD2};
    border-radius:99px; padding:2px 10px; font-size:0.72rem; color:{GOLD2}; margin:2px;
}}
.empty-state {{ text-align:center; padding:48px 20px; color:{SUBTEXT}; }}
.empty-state .icon {{ font-size:3rem; }}
h1 {{ font-family:'Playfair Display',serif!important; color:{GOLD}!important;
      text-shadow:0 0 20px {GOLD2}44; }}
h2,h3,h4 {{ color:{GOLD2}!important; }}
hr {{ border-color:{BORDER}!important; }}
div[data-testid="stButton"] button {{
    border-radius:8px; font-family:'JetBrains Mono',monospace; font-weight:700;
    transition:transform .15s;
}}
div[data-testid="stButton"] button:hover {{ transform:scale(1.02); }}
div[data-testid="stForm"] {{
    background:{SURFACE}; border:1px solid {BORDER}; border-radius:12px; padding:20px;
}}
</style>
""", unsafe_allow_html=True)

CONFETTI_JS = """
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
<script>confetti({{particleCount:180,spread:90,origin:{{y:0.5}},
colors:['#f0d060','#c9a84c','#6af7a2','#ffffff','#f7a26a']}});</script>"""

# ── File helpers ──────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        if "note"      not in df.columns: df["note"]      = ""
        if "recurring" not in df.columns: df["recurring"] = False
        return df
    return pd.DataFrame(columns=["date","category","amount","note","recurring"])

def save_data(df): df.to_csv(CSV_FILE, index=False)

def load_json(path, default):
    return json.load(open(path)) if os.path.exists(path) else default

def save_json(path, data):
    with open(path,"w") as f: json.dump(data, f)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("df", load_data()),
             ("budgets",   load_json(BUDGET_FILE,  {})),
             ("income",    load_json(INCOME_FILE,   {"monthly": 0})),
             ("recurring", load_json(RECURRING_FILE, [])),
             ("edit_idx", None), ("delete_idx", None),
             ("confetti_fired", set())]:
    if k not in st.session_state:
        st.session_state[k] = v

df        = st.session_state.df
budgets   = st.session_state.budgets
income    = st.session_state.income
recurring = st.session_state.recurring

# ── Auto-inject recurring expenses ────────────────────────────────────────────
def inject_recurring():
    today     = date.today()
    cur_month = today.strftime("%Y-%m")
    df        = st.session_state.df
    for rec in st.session_state.recurring:
        expected_date = pd.Timestamp(f"{cur_month}-{rec['day']:02d}")
        already = df[
            (df["date"].dt.to_period("M").astype(str) == cur_month) &
            (df["category"] == rec["category"]) &
            (df["amount"]   == rec["amount"]) &
            (df["note"]     == f"[Auto] {rec['name']}")
        ]
        if already.empty and today.day >= rec["day"]:
            new = pd.DataFrame([{"date": expected_date, "category": rec["category"],
                                  "amount": rec["amount"], "note": f"[Auto] {rec['name']}",
                                  "recurring": True}])
            st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
            save_data(st.session_state.df)

inject_recurring()
df = st.session_state.df

# ── Helpers ────────────────────────────────────────────────────────────────────
def plotly_defaults(fig):
    fig.update_layout(
        template=PLY_TPL, paper_bgcolor=PLY_PAPER, plot_bgcolor=PLY_BG,
        font=dict(family="JetBrains Mono", color=TEXT),
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=PLY_BORDER, zerolinecolor=PLY_BORDER)
    fig.update_yaxes(gridcolor=PLY_BORDER, zerolinecolor=PLY_BORDER)
    return fig

def month_df(m): return df[df["date"].dt.to_period("M").astype(str) == m]
def cur_month_str(): return date.today().strftime("%Y-%m")

# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ➕ Add Expense")
    with st.form("add_form", clear_on_submit=True):
        exp_date  = st.date_input("Date", value=date.today())
        category  = st.selectbox("Category", CATEGORIES)
        amount    = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")
        note      = st.text_input("Note (optional)")
        submitted = st.form_submit_button("✅ Add", use_container_width=True)
    if submitted:
        new = pd.DataFrame([{"date": pd.Timestamp(exp_date), "category": category,
                              "amount": round(amount,2), "note": note, "recurring": False}])
        st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
        save_data(st.session_state.df)
        st.success(f"₹{amount:.2f} added!")
        st.rerun()

    st.divider()
    st.markdown("### 💵 Monthly Income")
    with st.form("income_form"):
        new_income = st.number_input("Your monthly income (₹)", min_value=0,
                                      value=int(income.get("monthly", 0)), step=1000)
        if st.form_submit_button("💾 Save", use_container_width=True):
            st.session_state.income = {"monthly": new_income}
            save_json(INCOME_FILE, {"monthly": new_income})
            st.success("Income saved!")
            st.rerun()

    st.divider()
    st.markdown("### 💰 Budget Limits")
    with st.expander("Set per-category budgets"):
        for cat in CATEGORIES:
            val = st.number_input(cat, min_value=0, value=int(budgets.get(cat,0)),
                                  step=500, key=f"bgt_{cat}")
            budgets[cat] = val
        if st.button("💾 Save Budgets", use_container_width=True):
            st.session_state.budgets = budgets
            save_json(BUDGET_FILE, budgets)
            st.success("Saved!")

    st.divider()
    st.markdown("### 📁 Export")
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE,"rb") as f:
            st.download_button("⬇️ Download CSV", f, "expenses.csv",
                               "text/csv", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════════
hc1, hc2 = st.columns([6,1])
with hc1:
    st.title("$ Finance Dashboard")
    st.caption("Track · Forecast · Optimize — portfolio-level personal finance")
with hc2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("☀️ Light" if DM else "🌙 Dark", key="theme"):
        st.session_state.dark_mode = not DM
        st.rerun()

st.divider()

# ── Top metrics ───────────────────────────────────────────────────────────────
monthly_income = income.get("monthly", 0)
cur_m          = cur_month_str()
mdf_cur        = month_df(cur_m)
spent_cur      = mdf_cur["amount"].sum()

# Forecast: linear projection based on days elapsed
today         = date.today()
days_in_month = calendar.monthrange(today.year, today.month)[1]
days_elapsed  = today.day
forecast      = (spent_cur / days_elapsed * days_in_month) if days_elapsed > 0 else 0

savings       = monthly_income - spent_cur
savings_rate  = (savings / monthly_income * 100) if monthly_income > 0 else 0
avg_day       = (df.groupby(df["date"].dt.date)["amount"].sum().mean()) if not df.empty else 0

cols = st.columns(5)
metrics = [
    ("₹{:,.0f}".format(monthly_income), "Monthly Income",  ""),
    ("₹{:,.0f}".format(spent_cur),       "Spent This Month",""),
    ("₹{:,.0f}".format(savings),          "Savings",
     f"<span style='color:{GREEN if savings>=0 else RED}'>{savings_rate:.1f}% rate</span>"),
    ("₹{:,.0f}".format(forecast),         "Forecast Month-End",
     f"<span style='color:{RED if forecast>monthly_income else GREEN}'>{'⚠️ Over income' if forecast>monthly_income>0 else '✅ On track'}</span>"),
    ("₹{:,.0f}".format(avg_day),          "Avg / Day",      ""),
]
for col, (val, label, delta) in zip(cols, metrics):
    with col:
        st.markdown(f"""<div class="metric-card">
            <div class="value">{val}</div>
            <div class="label">{label}</div>
            <div class="delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 View & Manage", "📊 Analytics", "🎯 Budgets", "🔮 Forecast & Insights", "🔁 Recurring"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — VIEW & MANAGE
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### 🔍 Search & Filter")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        search_q = st.text_input("Search notes", placeholder="lunch, gym…", label_visibility="collapsed")
        filt_cat = st.selectbox("Category", ["All"] + CATEGORIES)
    with fc2:
        date_from = st.date_input("From", value=None, key="df_from")
        date_to   = st.date_input("To",   value=None, key="df_to")
    with fc3:
        amt_min = st.number_input("Min ₹", min_value=0.0, value=0.0, step=100.0)
        amt_max = st.number_input("Max ₹", min_value=0.0, value=0.0, step=100.0, help="0 = no limit")

    sort_by = st.selectbox("Sort", ["Date (newest)","Date (oldest)","Amount ↓","Amount ↑"])

    view = df.copy()
    if search_q:  view = view[view["note"].str.contains(search_q, case=False, na=False)]
    if filt_cat != "All": view = view[view["category"] == filt_cat]
    if date_from: view = view[view["date"].dt.date >= date_from]
    if date_to:   view = view[view["date"].dt.date <= date_to]
    if amt_min > 0: view = view[view["amount"] >= amt_min]
    if amt_max > 0: view = view[view["amount"] <= amt_max]
    view = view.sort_values("date", ascending=(sort_by == "Date (oldest)")) \
               if "Date" in sort_by else \
               view.sort_values("amount", ascending=(sort_by == "Amount ↑"))

    st.divider()
    st.markdown(f"#### 📋 Expenses &nbsp;<span style='color:{SUBTEXT};font-size:.8rem;'>{len(view)} result(s)</span>", unsafe_allow_html=True)

    if view.empty:
        st.markdown(f'<div class="empty-state"><div class="icon">🪙</div><p>No expenses found.</p></div>', unsafe_allow_html=True)
    else:
        for idx, row in view.iterrows():
            c1, c2, c3, c4 = st.columns([4,2,1,1])
            badge = '<span class="recurring-badge">🔁 auto</span>' if row.get("recurring") else ""
            with c1:
                st.markdown(f"""<div style='font-size:.85rem;color:{TEXT};'>
                    <b>{row['category']}</b> {badge}&nbsp;
                    <span style='color:{SUBTEXT};font-size:.75rem;'>{pd.Timestamp(row['date']).strftime('%d %b %Y')}</span><br>
                    <span style='color:{SUBTEXT};font-size:.78rem;'>{row['note'] or '—'}</span>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='color:{GOLD};font-weight:700;padding-top:8px;'>₹{row['amount']:,.2f}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("✏️", key=f"e{idx}"):
                    st.session_state.edit_idx = idx; st.rerun()
            with c4:
                if st.button("🗑", key=f"d{idx}"):
                    st.session_state.delete_idx = idx; st.rerun()

    # Delete confirm
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
                    st.rerun()
            with dc2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.delete_idx = None; st.rerun()

    # Edit form
    if st.session_state.edit_idx is not None:
        eidx = st.session_state.edit_idx
        if eidx in st.session_state.df.index:
            row = st.session_state.df.loc[eidx]
            st.divider(); st.markdown("#### ✏️ Edit Expense")
            with st.form("edit_form"):
                e1, e2 = st.columns(2)
                with e1:
                    e_date = st.date_input("Date", value=pd.Timestamp(row["date"]).date())
                    e_cat  = st.selectbox("Category", CATEGORIES,
                                          index=CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else 0)
                with e2:
                    e_amt  = st.number_input("Amount", min_value=0.01, value=float(row["amount"]), step=10.0, format="%.2f")
                    e_note = st.text_input("Note", value=str(row["note"]) if pd.notna(row["note"]) else "")
                s1, s2 = st.columns(2)
                with s1: save_e  = st.form_submit_button("💾 Save", use_container_width=True)
                with s2: cancel_e = st.form_submit_button("❌ Cancel", use_container_width=True)
            if save_e:
                st.session_state.df.at[eidx,"date"]     = pd.Timestamp(e_date)
                st.session_state.df.at[eidx,"category"] = e_cat
                st.session_state.df.at[eidx,"amount"]   = round(e_amt,2)
                st.session_state.df.at[eidx,"note"]     = e_note
                save_data(st.session_state.df); st.session_state.edit_idx = None
                st.success("Updated!"); st.rerun()
            if cancel_e:
                st.session_state.edit_idx = None; st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS (Plotly)
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    if df.empty:
        st.markdown('<div class="empty-state"><div class="icon">📊</div><p>No data yet.</p></div>', unsafe_allow_html=True)
    else:
        months    = sorted(df["date"].dt.to_period("M").astype(str).unique(), reverse=True)
        sel_month = st.selectbox("Month", months, key="ana_m")
        mdf       = month_df(sel_month)
        grand     = mdf["amount"].sum()
        cat_tots  = mdf.groupby("category")["amount"].sum().reset_index()
        cat_tots.columns = ["Category","Amount"]

        # Row 1: pie + bar
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown("**🥧 Category Breakdown**")
            fig = px.pie(cat_tots, names="Category", values="Amount",
                         color_discrete_sequence=GOLD_PALETTE, hole=0.4)
            fig.update_traces(textposition="inside", textinfo="percent+label",
                              marker=dict(line=dict(color=BG, width=2)))
            fig.update_layout(showlegend=False)
            st.plotly_chart(plotly_defaults(fig), use_container_width=True)

        with r1c2:
            st.markdown("**📊 Category Bar Chart**")
            fig = px.bar(cat_tots.sort_values("Amount", ascending=True),
                         x="Amount", y="Category", orientation="h",
                         color="Amount", color_continuous_scale=["#0d2410",GOLD2,GOLD])
            fig.update_layout(coloraxis_showscale=False, yaxis_title="")
            st.plotly_chart(plotly_defaults(fig), use_container_width=True)

        # Row 2: monthly trend + daily
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.markdown("**📈 Monthly Trend**")
            monthly = df.groupby(df["date"].dt.to_period("M").astype(str))["amount"] \
                        .sum().reset_index()
            monthly.columns = ["Month","Amount"]
            fig = px.line(monthly, x="Month", y="Amount",
                          markers=True, color_discrete_sequence=[GOLD])
            fig.update_traces(line=dict(width=2.5),
                              marker=dict(size=7, color=GOLD2, line=dict(color=GOLD,width=2)))
            st.plotly_chart(plotly_defaults(fig), use_container_width=True)

        with r2c2:
            st.markdown("**💸 Daily Spending**")
            daily = mdf.groupby(mdf["date"].dt.date)["amount"].sum().reset_index()
            daily.columns = ["Date","Amount"]
            fig = px.area(daily, x="Date", y="Amount", color_discrete_sequence=[GOLD2])
            fig.update_traces(fillcolor=f"rgba(201,168,76,0.15)", line=dict(color=GOLD))
            st.plotly_chart(plotly_defaults(fig), use_container_width=True)

        # Sunburst (premium feel)
        st.markdown("**🌞 Spending Sunburst**")
        mdf2 = mdf.copy()
        mdf2["month"] = sel_month
        fig = px.sunburst(mdf2, path=["month","category"], values="amount",
                          color="amount", color_continuous_scale=["#0d2410",GOLD2,GOLD])
        fig.update_layout(margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — BUDGETS
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 🎯 Monthly Budget Tracker")
    spent_by_cat = month_df(cur_m).groupby("category")["amount"].sum()
    has_budgets  = any(v > 0 for v in budgets.values())

    if not has_budgets:
        st.markdown('<div class="empty-state"><div class="icon">🎯</div><p>No budgets set. Use the sidebar!</p></div>', unsafe_allow_html=True)
    else:
        all_under = True
        rows_data = []
        for cat in CATEGORIES:
            lim = budgets.get(cat, 0)
            if lim <= 0: continue
            spent = float(spent_by_cat.get(cat, 0))
            pct   = min(spent / lim * 100, 100)
            over  = spent > lim
            if over: all_under = False
            rows_data.append((cat, spent, lim, pct, over))

        # Plotly budget bar
        cats   = [r[0] for r in rows_data]
        spents = [r[1] for r in rows_data]
        limits = [r[2] for r in rows_data]
        colors = [RED if r[4] else (GOLD if r[3]>75 else GREEN) for r in rows_data]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Limit",  x=cats, y=limits,  marker_color=PLY_BORDER, opacity=0.4))
        fig.add_trace(go.Bar(name="Spent",  x=cats, y=spents,  marker_color=colors))
        fig.update_layout(barmode="overlay", xaxis_title="", yaxis_title="₹",
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)

        for cat, spent, lim, pct, over in rows_data:
            bar_col = RED if over else (GOLD if pct > 75 else GREEN)
            status  = "🔴 OVER" if over else f"🟡 {pct:.0f}%" if pct > 75 else f"🟢 {pct:.0f}%"
            st.markdown(f"""
            <div class="expense-row" style="border-left-color:{bar_col};">
                <div><b>{cat}</b><br>
                    <span style="color:{SUBTEXT};font-size:.78rem;">₹{spent:,.0f} / ₹{lim:,.0f}</span>
                </div>
                <span style="color:{bar_col};font-weight:700;">{status}</span>
            </div>
            <div class="budget-bar-wrap">
                <div class="budget-bar-fill" style="width:{pct}%;background:{bar_col};"></div>
            </div>""", unsafe_allow_html=True)

        if all_under and f"confetti_{cur_m}" not in st.session_state.confetti_fired:
            st.success("🎉 Under budget in ALL categories!")
            st.components.v1.html(CONFETTI_JS, height=0)
            st.session_state.confetti_fired.add(f"confetti_{cur_m}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — FORECAST & SMART INSIGHTS
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 🔮 Month-End Forecast")

    if df.empty:
        st.markdown('<div class="empty-state"><div class="icon">🔮</div><p>No data yet.</p></div>', unsafe_allow_html=True)
    else:
        # Build daily cumulative for current month
        days_in  = calendar.monthrange(today.year, today.month)[1]
        elapsed  = today.day
        all_days = [date(today.year, today.month, d) for d in range(1, days_in+1)]

        daily_cur = mdf_cur.groupby(mdf_cur["date"].dt.date)["amount"].sum()
        cum_vals  = []
        running   = 0
        for d in all_days:
            running += daily_cur.get(d, 0)
            cum_vals.append(running if d <= today else None)

        # Forecast line
        daily_rate  = spent_cur / elapsed if elapsed > 0 else 0
        forecast_vals = []
        for i, d in enumerate(all_days):
            if d > today:
                forecast_vals.append(spent_cur + daily_rate * (i + 1 - elapsed))
            else:
                forecast_vals.append(None)
        # Connect at today
        forecast_vals[elapsed - 1] = spent_cur

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=all_days, y=cum_vals, name="Actual",
            line=dict(color=GOLD, width=2.5), mode="lines+markers",
            marker=dict(size=5)))
        fig.add_trace(go.Scatter(
            x=all_days, y=forecast_vals, name="Forecast",
            line=dict(color=GOLD2, width=2, dash="dot"), mode="lines"))
        if monthly_income > 0:
            fig.add_hline(y=monthly_income, line_color=GREEN, line_dash="dash",
                          annotation_text="Income", annotation_position="top right")
        fig.update_layout(xaxis_title="Day", yaxis_title="₹ Cumulative",
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(plotly_defaults(fig), use_container_width=True)

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(f"""<div class="metric-card">
                <div class="value">₹{forecast:,.0f}</div>
                <div class="label">Projected Total</div></div>""", unsafe_allow_html=True)
        with fc2:
            surplus = monthly_income - forecast
            col = GREEN if surplus >= 0 else RED
            st.markdown(f"""<div class="metric-card">
                <div class="value" style="color:{col};">₹{abs(surplus):,.0f}</div>
                <div class="label">{'Projected Surplus' if surplus>=0 else 'Projected Deficit'}</div></div>""", unsafe_allow_html=True)
        with fc3:
            st.markdown(f"""<div class="metric-card">
                <div class="value">₹{daily_rate:,.0f}</div>
                <div class="label">Daily Burn Rate</div></div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🧠 Smart Insights")

    months_list = sorted(df["date"].dt.to_period("M").astype(str).unique(), reverse=True)
    if len(months_list) < 2:
        st.info("Add expenses across at least 2 months to unlock smart insights!")
    else:
        cur_m2  = months_list[0]
        prev_m  = months_list[1]
        cur_df  = month_df(cur_m2)
        prev_df = month_df(prev_m)
        cur_tot  = cur_df["amount"].sum()
        prev_tot = prev_df["amount"].sum()
        cur_cats  = cur_df.groupby("category")["amount"].sum()
        prev_cats = prev_df.groupby("category")["amount"].sum()

        insights = []

        # Overall change
        if prev_tot > 0:
            chg = ((cur_tot - prev_tot) / prev_tot) * 100
            if abs(chg) >= 5:
                kind = "warn" if chg > 0 else "good"
                arrow = "📈" if chg > 0 else "📉"
                insights.append((kind,
                    f"{arrow} Overall spending {'increased' if chg>0 else 'decreased'} by "
                    f"<b>{abs(chg):.1f}%</b> vs last month "
                    f"(₹{prev_tot:,.0f} → ₹{cur_tot:,.0f})"))

        # Per category changes
        all_cats = set(cur_cats.index) | set(prev_cats.index)
        biggest_jump = ("", 0, 0)
        for cat in all_cats:
            c = float(cur_cats.get(cat, 0))
            p = float(prev_cats.get(cat, 0))
            if p > 0 and c > 0:
                pct = ((c - p) / p) * 100
                if abs(pct) >= 20:
                    kind  = "warn" if pct > 0 else "good"
                    arrow = "🔺" if pct > 0 else "🔻"
                    insights.append((kind,
                        f"{arrow} <b>{cat}</b>: {'up' if pct>0 else 'down'} {abs(pct):.0f}% "
                        f"(₹{p:,.0f} → ₹{c:,.0f})"))
                if pct > biggest_jump[1]:
                    biggest_jump = (cat, pct, c)
            elif p == 0 and c > 0:
                insights.append(("warn", f"🆕 New spending in <b>{cat}</b> this month: ₹{c:,.0f}"))

        # Savings rate insight
        if monthly_income > 0:
            sr = (monthly_income - cur_tot) / monthly_income * 100
            if sr >= 30:
                insights.append(("good", f"🏆 Great job! You're saving <b>{sr:.1f}%</b> of your income this month."))
            elif sr < 0:
                insights.append(("warn", f"🚨 You've exceeded your income this month by ₹{abs(monthly_income-cur_tot):,.0f}!"))
            else:
                insights.append(("", f"💡 You're saving <b>{sr:.1f}%</b> of income. Aim for 30%+!"))

        # Top category
        if not cur_cats.empty:
            top = cur_cats.idxmax()
            top_pct = cur_cats[top] / cur_tot * 100 if cur_tot > 0 else 0
            if top_pct > 40:
                insights.append(("warn",
                    f"⚠️ <b>{top}</b> makes up {top_pct:.0f}% of your spending this month. Consider reviewing."))

        if not insights:
            insights.append(("", "✅ Spending looks stable compared to last month. Keep it up!"))

        for kind, text in insights:
            st.markdown(f'<div class="insight-card {kind}">{text}</div>', unsafe_allow_html=True)

        # Month comparison chart
        st.markdown("<br>**📊 Month-over-Month Category Comparison**")
        compare_data = []
        for cat in CATEGORIES:
            compare_data.append({"Category": cat, "Month": prev_m,
                                  "Amount": float(prev_cats.get(cat, 0))})
            compare_data.append({"Category": cat, "Month": cur_m2,
                                  "Amount": float(cur_cats.get(cat, 0))})
        cdf = pd.DataFrame(compare_data)
        cdf = cdf[cdf["Amount"] > 0]
        if not cdf.empty:
            fig = px.bar(cdf, x="Category", y="Amount", color="Month", barmode="group",
                         color_discrete_sequence=[SUBTEXT, GOLD])
            st.plotly_chart(plotly_defaults(fig), use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — RECURRING EXPENSES
# ════════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### 🔁 Recurring Expenses")
    st.caption("These auto-inject into your expenses every month on the specified day.")

    # Add recurring
    with st.form("rec_form", clear_on_submit=True):
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1: r_name = st.text_input("Name", placeholder="Netflix, Rent…")
        with rc2: r_cat  = st.selectbox("Category", CATEGORIES, key="rcat")
        with rc3: r_amt  = st.number_input("Amount (₹)", min_value=1.0, step=100.0, format="%.2f")
        with rc4: r_day  = st.number_input("Day of month", min_value=1, max_value=28, value=1)
        if st.form_submit_button("➕ Add Recurring", use_container_width=True):
            if r_name.strip():
                st.session_state.recurring.append({
                    "name": r_name.strip(), "category": r_cat,
                    "amount": round(r_amt, 2), "day": int(r_day)
                })
                save_json(RECURRING_FILE, st.session_state.recurring)
                st.success(f"'{r_name}' added as recurring on day {r_day}!")
                st.rerun()

    st.divider()

    if not recurring:
        st.markdown('<div class="empty-state"><div class="icon">🔁</div><p>No recurring expenses yet.</p></div>', unsafe_allow_html=True)
    else:
        total_rec = sum(r["amount"] for r in recurring)
        st.markdown(f"**{len(recurring)} recurring expenses · ₹{total_rec:,.0f}/month**")
        st.markdown("<br>", unsafe_allow_html=True)

        for i, rec in enumerate(recurring):
            rc1, rc2, rc3, rc4, rc5 = st.columns([3,2,2,2,1])
            with rc1:
                st.markdown(f"<b style='color:{TEXT}'>{rec['name']}</b><br>"
                            f"<span style='color:{SUBTEXT};font-size:.78rem;'>{rec['category']}</span>",
                            unsafe_allow_html=True)
            with rc2:
                st.markdown(f"<span style='color:{GOLD};font-weight:700;'>₹{rec['amount']:,.2f}</span>",
                            unsafe_allow_html=True)
            with rc3:
                st.markdown(f"<span style='color:{SUBTEXT};font-size:.82rem;'>Every month on day {rec['day']}</span>",
                            unsafe_allow_html=True)
            with rc4:
                st.markdown(f'<span class="recurring-badge">🔁 auto</span>', unsafe_allow_html=True)
            with rc5:
                if st.button("🗑", key=f"rec_del_{i}"):
                    st.session_state.recurring.pop(i)
                    save_json(RECURRING_FILE, st.session_state.recurring)
                    st.rerun()

        # Recurring vs manual breakdown
        st.divider()
        st.markdown("**📊 Recurring vs Manual — This Month**")
        rec_spent    = float(mdf_cur[mdf_cur["recurring"] == True]["amount"].sum())
        manual_spent = float(mdf_cur[mdf_cur["recurring"] != True]["amount"].sum())
        if rec_spent + manual_spent > 0:
            fig = go.Figure(go.Pie(
                labels=["🔁 Recurring","✋ Manual"],
                values=[rec_spent, manual_spent],
                marker_colors=[GOLD2, GREEN], hole=0.5,
                textinfo="percent+label"
            ))
            fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(plotly_defaults(fig), use_container_width=True)