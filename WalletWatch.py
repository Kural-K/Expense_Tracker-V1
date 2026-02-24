import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, json, calendar
from datetime import date, timedelta
from auth import register_user, login_user, get_user_data_paths, init_db

st.set_page_config(page_title="WalletWatch", page_icon="💸", layout="wide")
init_db()

CATEGORIES = ["Food", "Rent", "Transport", "Shopping", "Health",
              "Entertainment", "Utilities", "Education", "Other"]

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
DM = st.session_state.dark_mode

if DM:
    BG="050f07"; SURFACE="#0d2410"; BORDER="#c9a84c55"
    TEXT="#e8d9a0"; SUBTEXT="#7a9e7a"; GOLD="#f0d060"
    GOLD2="#c9a84c"; RED="#f76a6a"; GREEN="#6af7a2"
    PAT="%23c9a84c08"; PAT2="%23c9a84c06"
    PLY_TPL="plotly_dark"; PLY_BG="#050f07"; PLY_PAPER="#0d2410"
    PLY_BORDER="rgba(201,168,76,0.33)"
    BG="#050f07"
else:
    BG="#f5f0e8"; SURFACE="#fffdf5"; BORDER="#c9a84c88"
    TEXT="#1a1a0a"; SUBTEXT="#5a6e5a"; GOLD="#a07820"
    GOLD2="#c9a84c"; RED="#c0392b"; GREEN="#1a8a4a"
    PAT="%23c9a84c10"; PAT2="%23c9a84c08"
    PLY_TPL="plotly"; PLY_BG="#f5f0e8"; PLY_PAPER="#fffdf5"
    PLY_BORDER="rgba(201,168,76,0.53)"

GOLD_PALETTE=["#f0d060","#c9a84c","#e8b84b","#f7c948","#d4a017",
              "#6af7a2","#f76a6a","#6ab8f7","#f76af0","#a2f76a"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=JetBrains+Mono:wght@400;700&display=swap');
html,body,[class*="css"]{{font-family:'JetBrains Mono',monospace;}}
.stApp{{background-color:{BG};background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Ctext x='10' y='50' font-size='36' fill='{PAT}' font-family='serif' font-weight='bold'%3E%24%3C/text%3E%3Ctext x='80' y='120' font-size='28' fill='{PAT2}' font-family='serif' font-weight='bold'%3E%E2%82%B9%3C/text%3E%3Ctext x='140' y='60' font-size='30' fill='{PAT}' font-family='serif' font-weight='bold'%3E%E2%82%AC%3C/text%3E%3Ctext x='30' y='160' font-size='26' fill='{PAT2}' font-family='serif' font-weight='bold'%3E%C2%A3%3C/text%3E%3Ctext x='120' y='180' font-size='32' fill='{PAT}' font-family='serif' font-weight='bold'%3E%C2%A5%3C/text%3E%3C/svg%3E"),linear-gradient(160deg,{BG} 0%,{SURFACE} 50%,{BG} 100%);color:{TEXT};}}
.stApp::before{{content:"";display:block;height:3px;background:linear-gradient(90deg,transparent,{GOLD2},{GOLD},{GOLD2},transparent);}}
section[data-testid="stSidebar"]{{background:{SURFACE};border-right:1px solid {BORDER};}}
.metric-card{{background:{SURFACE};border:1px solid {BORDER};border-radius:12px;padding:16px 18px;text-align:center;box-shadow:0 4px 18px #0003;transition:transform .2s;}}
.metric-card:hover{{transform:translateY(-2px);border-color:{GOLD};}}
.metric-card .value{{font-size:1.6rem;font-weight:700;color:{GOLD};}}
.metric-card .label{{font-size:0.72rem;color:{SUBTEXT};margin-top:4px;}}
.metric-card .delta{{font-size:0.75rem;margin-top:2px;}}
.auth-card{{background:{SURFACE};border:1px solid {BORDER};border-radius:16px;padding:36px 40px;max-width:440px;margin:40px auto;box-shadow:0 8px 40px #0006;}}
.auth-title{{font-family:'Playfair Display',serif;font-size:2rem;color:{GOLD};text-align:center;margin-bottom:4px;}}
.auth-sub{{text-align:center;color:{SUBTEXT};font-size:.82rem;margin-bottom:24px;}}
.user-badge{{background:{SURFACE};border:1px solid {BORDER};border-radius:99px;padding:4px 14px;font-size:.8rem;color:{GOLD2};display:inline-block;}}
.insight-card{{background:{SURFACE};border:1px solid {BORDER};border-radius:10px;padding:14px 16px;margin-bottom:10px;border-left:3px solid {GOLD};}}
.insight-card.warn{{border-left-color:{RED};}}
.insight-card.good{{border-left-color:{GREEN};}}
.expense-row{{background:{SURFACE};border-radius:8px;padding:10px 14px;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center;border-left:3px solid {GOLD2};transition:border-color .2s;}}
.expense-row:hover{{border-color:{GOLD};}}
.budget-bar-wrap{{background:{BG};border-radius:99px;height:12px;margin:3px 0 8px;overflow:hidden;border:1px solid {BORDER};}}
.budget-bar-fill{{height:100%;border-radius:99px;transition:width .6s ease;}}
.recurring-badge{{display:inline-block;background:{SURFACE};border:1px solid {GOLD2};border-radius:99px;padding:2px 10px;font-size:.72rem;color:{GOLD2};margin:2px;}}
.empty-state{{text-align:center;padding:48px 20px;color:{SUBTEXT};}}
.empty-state .icon{{font-size:3rem;}}
h1{{font-family:'Playfair Display',serif!important;color:{GOLD}!important;text-shadow:0 0 20px {GOLD2}44;}}
h2,h3,h4{{color:{GOLD2}!important;}}
hr{{border-color:{BORDER}!important;}}
div[data-testid="stButton"] button{{border-radius:8px;font-family:'JetBrains Mono',monospace;font-weight:700;}}
div[data-testid="stForm"]{{background:{SURFACE};border:1px solid {BORDER};border-radius:12px;padding:20px;}}
</style>
""", unsafe_allow_html=True)

CONFETTI_JS="""<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
<script>confetti({{particleCount:180,spread:90,origin:{{y:0.5}},colors:['#f0d060','#c9a84c','#6af7a2','#ffffff']}});</script>"""

# ── THE KEY FIX: single helper that ALWAYS returns a proper datetime df ───────
def fix_df(df: pd.DataFrame) -> pd.DataFrame:
    """Guarantee date column is datetime. Call this every time df is touched."""
    if df.empty:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"] if "date" in df.columns else [], errors="coerce")
        return df
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    if "note"      not in df.columns: df["note"]      = ""
    if "recurring" not in df.columns: df["recurring"] = False
    return df

def load_data(paths) -> pd.DataFrame:
    if os.path.exists(paths["csv"]):
        return fix_df(pd.read_csv(paths["csv"]))
    empty = pd.DataFrame(columns=["date","category","amount","note","recurring"])
    return fix_df(empty)

def save_data(df, paths):
    fix_df(df).to_csv(paths["csv"], index=False)

def load_json(path, default):
    return json.load(open(path)) if os.path.exists(path) else default

def save_json(path, data):
    with open(path,"w") as f: json.dump(data,f)

def plotly_defaults(fig):
    fig.update_layout(template=PLY_TPL, paper_bgcolor=PLY_PAPER, plot_bgcolor=PLY_BG,
        font=dict(family="JetBrains Mono",color=TEXT),
        margin=dict(l=10,r=10,t=36,b=10), legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor=PLY_BORDER, zerolinecolor=PLY_BORDER)
    fig.update_yaxes(gridcolor=PLY_BORDER, zerolinecolor=PLY_BORDER)
    return fig

def month_df(df, m):
    df = fix_df(df)
    if df.empty: return df
    return df[df["date"].dt.to_period("M").astype(str) == m]

def cur_month_str(): return date.today().strftime("%Y-%m")

def get_df(uk):
    """Always returns a properly typed df from session state."""
    return fix_df(st.session_state[f"{uk}df"])

def set_df(uk, df, paths):
    """Save df to session state and disk, always fixing types first."""
    df = fix_df(df)
    st.session_state[f"{uk}df"] = df
    save_data(df, paths)

# ════════════════════════════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════════════════════════════
def show_auth():
    st.markdown(f'<div class="auth-card"><div class="auth-title">💸 WalletWatch</div><div class="auth-sub">Your personal finance dashboard</div></div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        t1, t2 = st.tabs(["🔑 Login","📝 Sign Up"])
        with t1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit   = st.form_submit_button("Login →", use_container_width=True)
            if submit:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, msg, user = login_user(username, password)
                    if ok:
                        st.session_state.user = user
                        st.session_state.logged_in = True
                        st.success(f"Welcome back, {user['username']}! 👋")
                        st.rerun()
                    else:
                        st.error(msg)
        with t2:
            with st.form("signup_form"):
                nu = st.text_input("Username")
                ne = st.text_input("Email")
                np = st.text_input("Password", type="password")
                np2= st.text_input("Confirm Password", type="password")
                s2 = st.form_submit_button("Create Account →", use_container_width=True)
            if s2:
                if not all([nu,ne,np,np2]): st.error("Fill in all fields.")
                elif np != np2:             st.error("Passwords don't match.")
                else:
                    ok, msg = register_user(nu, ne, np)
                    st.success(msg) if ok else st.error(msg)

# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════════
def show_app():
    user  = st.session_state.user
    paths = get_user_data_paths(user["id"])
    uk    = f"u{user['id']}_"

    # Init session state for this user
    for k, v in [(f"{uk}df",        load_data(paths)),
                 (f"{uk}budgets",   load_json(paths["budgets"],   {})),
                 (f"{uk}income",    load_json(paths["income"],    {"monthly":0})),
                 (f"{uk}recurring", load_json(paths["recurring"], [])),
                 (f"{uk}edit_idx",  None),
                 (f"{uk}del_idx",   None),
                 (f"{uk}confetti",  set())]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ALWAYS get df through fix_df
    df        = get_df(uk)
    budgets   = st.session_state[f"{uk}budgets"]
    income    = st.session_state[f"{uk}income"]
    recurring = st.session_state[f"{uk}recurring"]
    today     = date.today()
    cur_m     = cur_month_str()

    # Auto-inject recurring
    for rec in recurring:
        expected = pd.Timestamp(f"{cur_m}-{rec['day']:02d}")
        already  = df[
            (df["date"].dt.to_period("M").astype(str) == cur_m) &
            (df["category"] == rec["category"]) &
            (df["amount"]   == rec["amount"]) &
            (df["note"]     == f"[Auto] {rec['name']}")
        ]
        if already.empty and today.day >= rec["day"]:
            new = pd.DataFrame([{"date": expected,"category":rec["category"],
                                  "amount":rec["amount"],"note":f"[Auto] {rec['name']}","recurring":True}])
            df = fix_df(pd.concat([df, new], ignore_index=True))
            set_df(uk, df, paths)

    # ── Header ────────────────────────────────────────────────────────────
    hc1,hc2,hc3 = st.columns([5,1,1])
    with hc1:
        st.title("$ WalletWatch")
        st.markdown(f'<span class="user-badge">👤 {user["username"]}</span>', unsafe_allow_html=True)
    with hc2:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("☀️" if DM else "🌙",key="theme"):
            st.session_state.dark_mode = not DM; st.rerun()
    with hc3:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
    st.divider()

    # ── Metrics ───────────────────────────────────────────────────────────
    monthly_income = income.get("monthly",0)
    mdf_cur        = month_df(df, cur_m)
    spent_cur      = mdf_cur["amount"].sum()
    days_in        = calendar.monthrange(today.year, today.month)[1]
    elapsed        = today.day
    forecast       = (spent_cur/elapsed*days_in) if elapsed>0 else 0
    savings        = monthly_income - spent_cur
    savings_rate   = (savings/monthly_income*100) if monthly_income>0 else 0
    avg_day        = df.groupby(df["date"].dt.date)["amount"].sum().mean() if not df.empty else 0

    for col,(val,label,delta) in zip(st.columns(5),[
        (f"₹{monthly_income:,.0f}","Monthly Income",""),
        (f"₹{spent_cur:,.0f}","Spent This Month",""),
        (f"₹{savings:,.0f}","Savings",f"<span style='color:{GREEN if savings>=0 else RED}'>{savings_rate:.1f}% rate</span>"),
        (f"₹{forecast:,.0f}","Forecast Month-End",f"<span style='color:{RED if forecast>monthly_income>0 else GREEN}'>{'⚠️ Over' if forecast>monthly_income>0 else '✅ On track'}</span>"),
        (f"₹{avg_day:,.0f}","Avg / Day",""),
    ]):
        with col:
            st.markdown(f'<div class="metric-card"><div class="value">{val}</div><div class="label">{label}</div><div class="delta">{delta}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 👋 Hey, {user['username']}!")
        st.caption(user["email"]); st.divider()
        st.markdown("### ➕ Add Expense")
        with st.form("add_form", clear_on_submit=True):
            exp_date = st.date_input("Date", value=date.today())
            category = st.selectbox("Category", CATEGORIES)
            amount   = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")
            note     = st.text_input("Note (optional)")
            if st.form_submit_button("✅ Add", use_container_width=True):
                new = pd.DataFrame([{"date":pd.Timestamp(exp_date),"category":category,
                                      "amount":round(amount,2),"note":note,"recurring":False}])
                set_df(uk, pd.concat([df,new],ignore_index=True), paths)
                st.success(f"₹{amount:.2f} added!"); st.rerun()

        st.divider()
        st.markdown("### 💵 Monthly Income")
        with st.form("income_form"):
            new_inc = st.number_input("Income (₹)",min_value=0,value=int(income.get("monthly",0)),step=1000)
            if st.form_submit_button("💾 Save",use_container_width=True):
                st.session_state[f"{uk}income"]={"monthly":new_inc}
                save_json(paths["income"],{"monthly":new_inc}); st.success("Saved!"); st.rerun()

        st.divider()
        st.markdown("### 💰 Budgets")
        with st.expander("Set per-category budgets"):
            for cat in CATEGORIES:
                budgets[cat]=st.number_input(cat,min_value=0,value=int(budgets.get(cat,0)),step=500,key=f"b_{cat}")
            if st.button("💾 Save Budgets",use_container_width=True):
                st.session_state[f"{uk}budgets"]=budgets
                save_json(paths["budgets"],budgets); st.success("Saved!")

        st.divider()
        if os.path.exists(paths["csv"]):
            with open(paths["csv"],"rb") as f:
                st.download_button("⬇️ Export CSV",f,"walletwatch.csv","text/csv",use_container_width=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1,tab2,tab3,tab4,tab5 = st.tabs(["📋 View & Manage","📊 Analytics","🎯 Budgets","🔮 Forecast","🔁 Recurring"])

    # ── TAB 1 ─────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("#### 🔍 Search & Filter")
        fc1,fc2,fc3 = st.columns(3)
        with fc1:
            sq=st.text_input("Search notes",placeholder="lunch…",label_visibility="collapsed")
            filt_cat=st.selectbox("Category",["All"]+CATEGORIES)
        with fc2:
            d_from=st.date_input("From",value=None,key="df_from")
            d_to  =st.date_input("To",  value=None,key="df_to")
        with fc3:
            a_min=st.number_input("Min ₹",min_value=0.0,value=0.0,step=100.0)
            a_max=st.number_input("Max ₹",min_value=0.0,value=0.0,step=100.0)
        sort_by=st.selectbox("Sort",["Date (newest)","Date (oldest)","Amount ↓","Amount ↑"])

        view = fix_df(df.copy())
        if sq:            view=view[view["note"].str.contains(sq,case=False,na=False)]
        if filt_cat!="All": view=view[view["category"]==filt_cat]
        if d_from:        view=view[view["date"].dt.date>=d_from]
        if d_to:          view=view[view["date"].dt.date<=d_to]
        if a_min>0:       view=view[view["amount"]>=a_min]
        if a_max>0:       view=view[view["amount"]<=a_max]
        view=view.sort_values("date",ascending=(sort_by=="Date (oldest)")) if "Date" in sort_by \
             else view.sort_values("amount",ascending=(sort_by=="Amount ↑"))

        st.divider()
        st.markdown(f"#### 📋 Expenses &nbsp;<span style='color:{SUBTEXT};font-size:.8rem;'>{len(view)} result(s)</span>",unsafe_allow_html=True)
        if view.empty:
            st.markdown('<div class="empty-state"><div class="icon">🪙</div><p>No expenses found.</p></div>',unsafe_allow_html=True)
        else:
            for idx,row in view.iterrows():
                c1,c2,c3,c4=st.columns([4,2,1,1])
                badge='<span class="recurring-badge">🔁</span>' if row.get("recurring") else ""
                with c1:
                    st.markdown(f"<div style='font-size:.85rem;'><b>{row['category']}</b> {badge} &nbsp;<span style='color:{SUBTEXT};font-size:.75rem;'>{pd.Timestamp(row['date']).strftime('%d %b %Y')}</span><br><span style='color:{SUBTEXT};font-size:.78rem;'>{row['note'] or '—'}</span></div>",unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div style='color:{GOLD};font-weight:700;padding-top:8px;'>₹{row['amount']:,.2f}</div>",unsafe_allow_html=True)
                with c3:
                    if st.button("✏️",key=f"e{idx}"):
                        st.session_state[f"{uk}edit_idx"]=idx; st.rerun()
                with c4:
                    if st.button("🗑",key=f"d{idx}"):
                        st.session_state[f"{uk}del_idx"]=idx; st.rerun()

        if st.session_state[f"{uk}del_idx"] is not None:
            didx=st.session_state[f"{uk}del_idx"]
            if didx in df.index:
                row=df.loc[didx]
                st.warning(f"⚠️ Delete **{row['category']}** — ₹{row['amount']:.2f}?")
                dc1,dc2=st.columns(2)
                with dc1:
                    if st.button("✅ Yes, Delete",type="primary",use_container_width=True):
                        set_df(uk, df.drop(index=didx).reset_index(drop=True), paths)
                        st.session_state[f"{uk}del_idx"]=None; st.rerun()
                with dc2:
                    if st.button("❌ Cancel",use_container_width=True):
                        st.session_state[f"{uk}del_idx"]=None; st.rerun()

        if st.session_state[f"{uk}edit_idx"] is not None:
            eidx=st.session_state[f"{uk}edit_idx"]
            if eidx in df.index:
                row=df.loc[eidx]
                st.divider(); st.markdown("#### ✏️ Edit Expense")
                with st.form("edit_form"):
                    e1,e2=st.columns(2)
                    with e1:
                        e_date=st.date_input("Date",value=pd.Timestamp(row["date"]).date())
                        e_cat =st.selectbox("Category",CATEGORIES,index=CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else 0)
                    with e2:
                        e_amt =st.number_input("Amount",min_value=0.01,value=float(row["amount"]),step=10.0,format="%.2f")
                        e_note=st.text_input("Note",value=str(row["note"]) if pd.notna(row["note"]) else "")
                    s1,s2=st.columns(2)
                    with s1: save_e  =st.form_submit_button("💾 Save",use_container_width=True)
                    with s2: cancel_e=st.form_submit_button("❌ Cancel",use_container_width=True)
                if save_e:
                    updated=df.copy()
                    updated.at[eidx,"date"]=pd.Timestamp(e_date)
                    updated.at[eidx,"category"]=e_cat
                    updated.at[eidx,"amount"]=round(e_amt,2)
                    updated.at[eidx,"note"]=e_note
                    set_df(uk, updated, paths)
                    st.session_state[f"{uk}edit_idx"]=None; st.success("Updated!"); st.rerun()
                if cancel_e:
                    st.session_state[f"{uk}edit_idx"]=None; st.rerun()

    # ── TAB 2 ─────────────────────────────────────────────────────────────
    with tab2:
        if df.empty:
            st.markdown('<div class="empty-state"><div class="icon">📊</div><p>No data yet.</p></div>',unsafe_allow_html=True)
        else:
            months=sorted(df["date"].dt.to_period("M").astype(str).unique(),reverse=True)
            sel_month=st.selectbox("Month",months,key="ana_m")
            mdf=month_df(df,sel_month); grand=mdf["amount"].sum()
            cat_tots=mdf.groupby("category")["amount"].sum().reset_index()
            cat_tots.columns=["Category","Amount"]

            r1,r2=st.columns(2)
            with r1:
                st.markdown("**🥧 Category Breakdown**")
                fig=px.pie(cat_tots,names="Category",values="Amount",color_discrete_sequence=GOLD_PALETTE,hole=0.4)
                fig.update_traces(textposition="inside",textinfo="percent+label",marker=dict(line=dict(color=BG,width=2)))
                fig.update_layout(showlegend=False)
                st.plotly_chart(plotly_defaults(fig),use_container_width=True)
            with r2:
                st.markdown("**📊 Category Bar**")
                fig=px.bar(cat_tots.sort_values("Amount",ascending=True),x="Amount",y="Category",orientation="h",color="Amount",color_continuous_scale=["#0d2410",GOLD2,GOLD])
                fig.update_layout(coloraxis_showscale=False,yaxis_title="")
                st.plotly_chart(plotly_defaults(fig),use_container_width=True)

            r3,r4=st.columns(2)
            with r3:
                st.markdown("**📈 Monthly Trend**")
                monthly=df.groupby(df["date"].dt.to_period("M").astype(str))["amount"].sum().reset_index()
                monthly.columns=["Month","Amount"]
                fig=px.line(monthly,x="Month",y="Amount",markers=True,color_discrete_sequence=[GOLD])
                fig.update_traces(line=dict(width=2.5),marker=dict(size=7,color=GOLD2))
                st.plotly_chart(plotly_defaults(fig),use_container_width=True)
            with r4:
                st.markdown("**💸 Daily Spending**")
                daily=mdf.groupby(mdf["date"].dt.date)["amount"].sum().reset_index()
                daily.columns=["Date","Amount"]
                fig=px.area(daily,x="Date",y="Amount",color_discrete_sequence=[GOLD2])
                fig.update_traces(fillcolor="rgba(201,168,76,0.15)",line=dict(color=GOLD))
                st.plotly_chart(plotly_defaults(fig),use_container_width=True)

            st.markdown("**🌞 Sunburst**")
            mdf2=mdf.copy(); mdf2["month"]=sel_month
            fig=px.sunburst(mdf2,path=["month","category"],values="amount",color="amount",color_continuous_scale=["#0d2410",GOLD2,GOLD])
            fig.update_layout(margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(plotly_defaults(fig),use_container_width=True)

    # ── TAB 3 ─────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("#### 🎯 Monthly Budget Tracker")
        spent_by_cat=month_df(df,cur_m).groupby("category")["amount"].sum()
        has_budgets=any(v>0 for v in budgets.values())
        if not has_budgets:
            st.markdown('<div class="empty-state"><div class="icon">🎯</div><p>No budgets set. Use the sidebar!</p></div>',unsafe_allow_html=True)
        else:
            all_under=True; rows_data=[]
            for cat in CATEGORIES:
                lim=budgets.get(cat,0)
                if lim<=0: continue
                spent=float(spent_by_cat.get(cat,0)); pct=min(spent/lim*100,100); over=spent>lim
                if over: all_under=False
                rows_data.append((cat,spent,lim,pct,over))

            cats=[r[0] for r in rows_data]; spents=[r[1] for r in rows_data]
            limits=[r[2] for r in rows_data]; colors=[RED if r[4] else(GOLD if r[3]>75 else GREEN) for r in rows_data]
            fig=go.Figure()
            fig.add_trace(go.Bar(name="Limit",x=cats,y=limits,marker_color=PLY_BORDER,opacity=0.4))
            fig.add_trace(go.Bar(name="Spent",x=cats,y=spents,marker_color=colors))
            fig.update_layout(barmode="overlay",xaxis_title="",yaxis_title="₹",legend=dict(orientation="h",y=1.1))
            st.plotly_chart(plotly_defaults(fig),use_container_width=True)

            for cat,spent,lim,pct,over in rows_data:
                bc=RED if over else(GOLD if pct>75 else GREEN)
                status="🔴 OVER" if over else f"🟡 {pct:.0f}%" if pct>75 else f"🟢 {pct:.0f}%"
                st.markdown(f'<div class="expense-row" style="border-left-color:{bc};"><div><b>{cat}</b><br><span style="color:{SUBTEXT};font-size:.78rem;">₹{spent:,.0f} / ₹{lim:,.0f}</span></div><span style="color:{bc};font-weight:700;">{status}</span></div><div class="budget-bar-wrap"><div class="budget-bar-fill" style="width:{pct}%;background:{bc};"></div></div>',unsafe_allow_html=True)

            if all_under and f"c_{cur_m}" not in st.session_state[f"{uk}confetti"]:
                st.success("🎉 Under budget in ALL categories!")
                st.components.v1.html(CONFETTI_JS,height=0)
                st.session_state[f"{uk}confetti"].add(f"c_{cur_m}")

    # ── TAB 4 ─────────────────────────────────────────────────────────────
    with tab4:
        st.markdown("#### 🔮 Month-End Forecast")
        if df.empty:
            st.markdown('<div class="empty-state"><div class="icon">🔮</div><p>No data yet.</p></div>',unsafe_allow_html=True)
        else:
            days_in=calendar.monthrange(today.year,today.month)[1]
            all_days=[date(today.year,today.month,d) for d in range(1,days_in+1)]
            daily_cur=mdf_cur.groupby(mdf_cur["date"].dt.date)["amount"].sum()
            cum_vals=[]; running=0
            for d in all_days:
                running+=daily_cur.get(d,0)
                cum_vals.append(running if d<=today else None)
            daily_rate=spent_cur/elapsed if elapsed>0 else 0
            forecast_vals=[None]*len(all_days); forecast_vals[elapsed-1]=spent_cur
            for i in range(elapsed,len(all_days)):
                forecast_vals[i]=spent_cur+daily_rate*(i+1-elapsed)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=all_days,y=cum_vals,name="Actual",line=dict(color=GOLD,width=2.5),mode="lines+markers",marker=dict(size=5)))
            fig.add_trace(go.Scatter(x=all_days,y=forecast_vals,name="Forecast",line=dict(color=GOLD2,width=2,dash="dot"),mode="lines"))
            if monthly_income>0:
                fig.add_hline(y=monthly_income,line_color=GREEN,line_dash="dash",annotation_text="Income",annotation_position="top right")
            fig.update_layout(xaxis_title="Day",yaxis_title="₹",legend=dict(orientation="h",y=1.1))
            st.plotly_chart(plotly_defaults(fig),use_container_width=True)

            surplus=monthly_income-forecast
            for col,(val,label,color) in zip(st.columns(3),[
                (f"₹{forecast:,.0f}","Projected Total",GOLD),
                (f"₹{abs(surplus):,.0f}","Surplus" if surplus>=0 else "Deficit",GREEN if surplus>=0 else RED),
                (f"₹{daily_rate:,.0f}","Daily Burn Rate",GOLD),
            ]):
                with col:
                    st.markdown(f'<div class="metric-card"><div class="value" style="color:{color};">{val}</div><div class="label">{label}</div></div>',unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 🧠 Smart Insights")
        months_list=sorted(df["date"].dt.to_period("M").astype(str).unique(),reverse=True)
        if len(months_list)<2:
            st.info("Add expenses across 2+ months to unlock insights!")
        else:
            cm=months_list[0]; pm=months_list[1]
            cdf=month_df(df,cm); pdf=month_df(df,pm)
            ct=cdf["amount"].sum(); pt=pdf["amount"].sum()
            cc=cdf.groupby("category")["amount"].sum(); pc=pdf.groupby("category")["amount"].sum()
            insights=[]
            if pt>0:
                chg=((ct-pt)/pt)*100
                if abs(chg)>=5:
                    insights.append(("warn" if chg>0 else "good",f"{'📈' if chg>0 else '📉'} Overall spending {'increased' if chg>0 else 'decreased'} <b>{abs(chg):.1f}%</b> vs last month"))
            for cat in set(cc.index)|set(pc.index):
                c=float(cc.get(cat,0)); p=float(pc.get(cat,0))
                if p>0 and c>0:
                    pct=((c-p)/p)*100
                    if abs(pct)>=20:
                        insights.append(("warn" if pct>0 else "good",f"{'🔺' if pct>0 else '🔻'} <b>{cat}</b>: {'up' if pct>0 else 'down'} {abs(pct):.0f}% (₹{p:,.0f}→₹{c:,.0f})"))
                elif p==0 and c>0:
                    insights.append(("warn",f"🆕 New spending in <b>{cat}</b>: ₹{c:,.0f}"))
            if monthly_income>0:
                sr=(monthly_income-ct)/monthly_income*100
                if sr>=30:   insights.append(("good",f"🏆 Saving <b>{sr:.1f}%</b> of income — great job!"))
                elif sr<0:   insights.append(("warn",f"🚨 Exceeded income by ₹{abs(monthly_income-ct):,.0f}!"))
                else:        insights.append(("",f"💡 Saving <b>{sr:.1f}%</b>. Aim for 30%+!"))
            if not cc.empty:
                top=cc.idxmax(); tp=cc[top]/ct*100 if ct>0 else 0
                if tp>40: insights.append(("warn",f"⚠️ <b>{top}</b> is {tp:.0f}% of spending."))
            if not insights: insights.append(("","✅ Spending looks stable!"))
            for kind,text in insights:
                st.markdown(f'<div class="insight-card {kind}">{text}</div>',unsafe_allow_html=True)

            st.markdown("<br>**📊 Month-over-Month Comparison**")
            compare=[]
            for cat in CATEGORIES:
                compare.append({"Category":cat,"Month":pm,"Amount":float(pc.get(cat,0))})
                compare.append({"Category":cat,"Month":cm,"Amount":float(cc.get(cat,0))})
            cdf2=pd.DataFrame(compare); cdf2=cdf2[cdf2["Amount"]>0]
            if not cdf2.empty:
                fig=px.bar(cdf2,x="Category",y="Amount",color="Month",barmode="group",color_discrete_sequence=[SUBTEXT,GOLD])
                st.plotly_chart(plotly_defaults(fig),use_container_width=True)

    # ── TAB 5 ─────────────────────────────────────────────────────────────
    with tab5:
        st.markdown("#### 🔁 Recurring Expenses")
        with st.form("rec_form",clear_on_submit=True):
            rc1,rc2,rc3,rc4=st.columns(4)
            with rc1: r_name=st.text_input("Name",placeholder="Netflix…")
            with rc2: r_cat=st.selectbox("Category",CATEGORIES,key="rcat")
            with rc3: r_amt=st.number_input("Amount (₹)",min_value=1.0,step=100.0,format="%.2f")
            with rc4: r_day=st.number_input("Day of month",min_value=1,max_value=28,value=1)
            if st.form_submit_button("➕ Add",use_container_width=True):
                if r_name.strip():
                    st.session_state[f"{uk}recurring"].append({"name":r_name.strip(),"category":r_cat,"amount":round(r_amt,2),"day":int(r_day)})
                    save_json(paths["recurring"],st.session_state[f"{uk}recurring"])
                    st.success(f"'{r_name}' added!"); st.rerun()
        st.divider()
        if not recurring:
            st.markdown('<div class="empty-state"><div class="icon">🔁</div><p>No recurring expenses yet.</p></div>',unsafe_allow_html=True)
        else:
            st.markdown(f"**{len(recurring)} recurring · ₹{sum(r['amount'] for r in recurring):,.0f}/month**")
            for i,rec in enumerate(recurring):
                rc1,rc2,rc3,rc4=st.columns([3,2,3,1])
                with rc1: st.markdown(f"<b>{rec['name']}</b><br><span style='color:{SUBTEXT};font-size:.78rem;'>{rec['category']}</span>",unsafe_allow_html=True)
                with rc2: st.markdown(f"<span style='color:{GOLD};font-weight:700;'>₹{rec['amount']:,.2f}</span>",unsafe_allow_html=True)
                with rc3: st.markdown(f"<span style='color:{SUBTEXT};font-size:.82rem;'>Day {rec['day']} every month</span>",unsafe_allow_html=True)
                with rc4:
                    if st.button("🗑",key=f"rdel_{i}"):
                        st.session_state[f"{uk}recurring"].pop(i)
                        save_json(paths["recurring"],st.session_state[f"{uk}recurring"]); st.rerun()
            rec_s=float(mdf_cur[mdf_cur["recurring"]==True]["amount"].sum())
            man_s=float(mdf_cur[mdf_cur["recurring"]!=True]["amount"].sum())
            if rec_s+man_s>0:
                fig=go.Figure(go.Pie(labels=["🔁 Recurring","✋ Manual"],values=[rec_s,man_s],
                    marker_colors=[GOLD2,GREEN],hole=0.5,textinfo="percent+label"))
                fig.update_layout(showlegend=False,margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(plotly_defaults(fig),use_container_width=True)

# ── Entry point ───────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_auth()
else:
    show_app()