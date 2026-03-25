import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

API = "http://localhost:8000/api"

st.set_page_config(page_title="Churn AI Dashboard", page_icon="🔮", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0a1a 0%, #0d0d2b 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d0d2b, #1a0a2e); border-right: 1px solid #2a1a4e; }
[data-testid="stSidebar"] * { color: #c4b5fd !important; }
h1 { background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem !important; }
h2, h3 { color: #a78bfa !important; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
    border: 1px solid #4a2a7e;
    border-radius: 12px; padding: 16px;
    box-shadow: 0 4px 20px rgba(124,58,237,0.2);
}
div[data-testid="metric-container"] label { color: #a78bfa !important; font-size: 12px !important; }
div[data-testid="metric-container"] div { color: #ffffff !important; font-size: 24px !important; font-weight: 700 !important; }
.stButton button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4) !important;
}
.stButton button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(124,58,237,0.6) !important; }
div[data-baseweb="select"] > div { background: #1a1a3e !important; border-color: #4a2a7e !important; color: white !important; }
.stSlider > div > div { background: linear-gradient(135deg, #7c3aed, #2563eb) !important; }
input[type="number"] { background: #1a1a3e !important; color: white !important; border-color: #4a2a7e !important; }
.stDataFrame { border: 1px solid #2a1a4e; border-radius: 10px; }
hr { border-color: #2a1a4e !important; }
.stDownloadButton button { background: linear-gradient(135deg, #059669, #0d9488) !important; }
</style>
""", unsafe_allow_html=True)

CHART_THEME = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,30,0.5)",
                   font_color="#c4b5fd", margin=dict(t=20,b=20,l=10,r=10))

# ── API Calls ────────────────────────────────────────────
def get_dashboard():
    try: return requests.get(f"{API}/dashboard", timeout=5).json()
    except: return None

def get_customers():
    try:
        r = requests.get(f"{API}/customers", timeout=5).json()
        if isinstance(r, list): return r
        if isinstance(r, dict): return [r] if r.get("id") else []
        return []
    except: return []

def add_customer(data):
    try:
        r = requests.post(f"{API}/customers", json=data, timeout=10)
        return r.json(), r.ok
    except Exception as e: return {"detail": str(e)}, False

def update_customer(uid, data):
    try:
        r = requests.put(f"{API}/customers/{uid}", json=data, timeout=10)
        return r.json(), r.ok
    except Exception as e: return {"detail": str(e)}, False

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.markdown("## 🔮 Churn AI")
st.sidebar.markdown("---")

tab = st.sidebar.radio("Action", ["➕ Add Customer", "✏️ Update Customer"], label_visibility="collapsed")

if tab == "➕ Add Customer":
    st.sidebar.markdown("### ➕ Add Customer")
    with st.sidebar.form("add"):
        gender   = st.selectbox("Gender", ["Male", "Female"])
        senior   = st.selectbox("Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x else "No")
        tenure   = st.slider("Tenure (months)", 0, 72, 12)
        charges  = st.number_input("Monthly Charges ($)", min_value=1.0, value=50.0, step=0.5, format="%.2f")
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        submit   = st.form_submit_button("🚀 Predict & Add", type="primary")

        if submit:
            result, ok = add_customer({"gender": gender, "seniorcitizen": senior,
                                        "tenure": tenure, "monthlycharges": charges, "contract": contract})
            if ok:
                p = result.get("prediction") or {}
                label, prob = p.get("prediction","?"), p.get("probability",0)
                st.success(f"{'🔴' if label=='Yes' else '🟢'} Churn: **{label}** ({prob*100:.1f}%)")
            else:
                st.error(result.get("detail","Error"))

else:
    st.sidebar.markdown("### ✏️ Update Customer")
    with st.sidebar.form("update"):
        uid      = st.number_input("Customer ID", min_value=1, step=1, value=1)
        u_tenure  = st.slider("New Tenure", 0, 72, 12)
        u_charges = st.number_input("New Charges ($)", min_value=1.0, value=50.0, step=0.5, format="%.2f")
        u_contract= st.selectbox("New Contract", ["Month-to-month", "One year", "Two year"])
        u_submit  = st.form_submit_button("🔄 Update & Re-Predict", type="primary")

        if u_submit:
            result, ok = update_customer(uid, {"tenure": u_tenure, "monthlycharges": u_charges, "contract": u_contract})
            if ok:
                p = result.get("prediction") or {}
                label, prob = p.get("prediction","?"), p.get("probability",0)
                st.success(f"Updated! {'🔴' if label=='Yes' else '🟢'} **{label}** ({prob*100:.1f}%)")
            else:
                st.error(result.get("detail","Error"))

st.sidebar.markdown("---")
auto = st.sidebar.toggle("🔄 Auto Refresh (5s)", value=False)
if auto:
    st.sidebar.info("Live mode active")

# ── Main ─────────────────────────────────────────────────
st.title("🔮 Churn Prediction Dashboard")
st.caption("Real-time customer churn analysis powered by ML")
st.markdown("---")

dash = get_dashboard()
customers = get_customers()

if not dash:
    st.error("⚠️ API connect nahi ho rahi — `uvicorn app.main:app --reload` chalao")
    st.stop()

# ── KPI Metrics ──────────────────────────────────────────
m1,m2,m3,m4,m5,m6 = st.columns(6)
m1.metric("👥 Total Customers",    dash["total_customers"])
m2.metric("🔴 Churn",              dash["churn_count"])
m3.metric("🟢 Active",             dash["non_churn_count"])
m4.metric("📉 Churn Rate",         f"{dash['churn_percentage']}%")
m5.metric("⚠️ High Risk",          dash["high_risk_customers"])
m6.metric("💰 Avg Charges",        f"${dash['avg_monthly_charges']}")
st.markdown("---")

if not customers:
    st.info("📭 Koi customer nahi — sidebar se add karo!")
    if auto: time.sleep(5); st.rerun()
    st.stop()

# ── Build DataFrame ──────────────────────────────────────
rows = []
for c in customers:
    if not isinstance(c, dict): continue
    p = c.get("prediction") or {}
    rows.append({
        "ID":       c.get("id"),
        "Gender":   c.get("gender"),
        "Senior":   c.get("seniorcitizen"),
        "Tenure":   c.get("tenure"),
        "Charges":  c.get("monthlycharges"),
        "Contract": c.get("contract"),
        "Churn":    p.get("prediction", "N/A"),
        "Prob":     p.get("probability", 0),
        "Risk":     "High" if p.get("probability",0)>0.7 else ("Medium" if p.get("probability",0)>0.4 else "Low")
    })

df = pd.DataFrame(rows)

# ── Filters ──────────────────────────────────────────────
st.subheader("🔍 Filters")
f1,f2,f3,f4 = st.columns(4)
f_churn    = f1.selectbox("Churn Filter",    ["All","Yes","No"])
f_risk     = f2.selectbox("Risk Filter",     ["All","High","Medium","Low"])
f_contract = f3.selectbox("Contract Filter", ["All","Month-to-month","One year","Two year"])
f_gender   = f4.selectbox("Gender Filter",   ["All","Male","Female"])

fdf = df.copy()
if f_churn    != "All": fdf = fdf[fdf["Churn"]    == f_churn]
if f_risk     != "All": fdf = fdf[fdf["Risk"]     == f_risk]
if f_contract != "All": fdf = fdf[fdf["Contract"] == f_contract]
if f_gender   != "All": fdf = fdf[fdf["Gender"]   == f_gender]

st.markdown("---")

# ── Charts Row 1 ─────────────────────────────────────────
c1,c2,c3 = st.columns(3)

with c1:
    st.subheader("🥧 Churn Distribution")
    fig = px.pie(names=["Churn","Active"], values=[dash["churn_count"],dash["non_churn_count"]],
                 color_discrete_sequence=["#ef4444","#22c55e"], hole=0.55)
    fig.update_layout(**CHART_THEME)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("📊 Risk Breakdown")
    rc = df["Risk"].value_counts().reset_index()
    rc.columns = ["Risk","Count"]
    fig2 = px.bar(rc, x="Risk", y="Count", color="Risk",
                  color_discrete_map={"High":"#ef4444","Medium":"#f59e0b","Low":"#22c55e"})
    fig2.update_layout(**CHART_THEME, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.subheader("📈 Tenure vs Probability")
    fig3 = px.scatter(df, x="Tenure", y="Prob", color="Churn", size="Charges",
                      color_discrete_map={"Yes":"#ef4444","No":"#22c55e","N/A":"#888"}, opacity=0.75)
    fig3.update_layout(**CHART_THEME)
    st.plotly_chart(fig3, use_container_width=True)

# ── Charts Row 2 ─────────────────────────────────────────
c4,c5 = st.columns(2)

with c4:
    st.subheader("📦 Contract vs Churn")
    cc = df.groupby(["Contract","Churn"]).size().reset_index(name="Count")
    fig4 = px.bar(cc, x="Contract", y="Count", color="Churn", barmode="group",
                  color_discrete_map={"Yes":"#ef4444","No":"#22c55e"})
    fig4.update_layout(**CHART_THEME)
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    st.subheader("👤 Gender vs Churn")
    gc = df.groupby(["Gender","Churn"]).size().reset_index(name="Count")
    fig5 = px.bar(gc, x="Gender", y="Count", color="Churn", barmode="group",
                  color_discrete_map={"Yes":"#ef4444","No":"#22c55e"})
    fig5.update_layout(**CHART_THEME)
    st.plotly_chart(fig5, use_container_width=True)

# ── Charges Distribution ─────────────────────────────────
st.subheader("💰 Monthly Charges Distribution")
fig6 = px.histogram(df, x="Charges", color="Churn", nbins=30, barmode="overlay",
                    color_discrete_map={"Yes":"#ef4444","No":"#22c55e"}, opacity=0.75)
fig6.update_layout(**CHART_THEME)
st.plotly_chart(fig6, use_container_width=True)

# ── Table ────────────────────────────────────────────────
st.markdown("---")
st.subheader(f"📋 Customers Table ({len(fdf)} results)")

def color_risk(val):
    colors = {"High":"background-color:#3a0a0a;color:#ef4444",
              "Medium":"background-color:#3a2a0a;color:#f59e0b",
              "Low":"background-color:#0a2a0a;color:#22c55e"}
    return colors.get(val,"")

st.dataframe(
    fdf.style.applymap(color_risk, subset=["Risk"]),
    use_container_width=True, hide_index=True
)

col_a, col_b = st.columns(2)
csv = fdf.to_csv(index=False).encode()
col_a.download_button("⬇️ Export CSV", csv, "churn_data.csv", "text/csv")

high_risk_df = df[df["Risk"]=="High"]
if not high_risk_df.empty:
    col_b.download_button("🔴 Export High Risk", high_risk_df.to_csv(index=False).encode(),
                          "high_risk.csv", "text/csv")

if auto:
    time.sleep(5)
    st.rerun()