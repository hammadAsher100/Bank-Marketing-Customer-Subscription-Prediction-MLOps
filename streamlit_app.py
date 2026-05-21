"""
streamlit_app.py  (place in project root)
Bank Marketing MLOps Dashboard - English Version
"""

import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Bank Marketing MLOps",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="metric-container"] {
        background: #1e2130;
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 16px;
    }
    .predict-yes {
        background: linear-gradient(135deg, #0d4f2e, #1a7a47);
        border: 2px solid #2ecc71;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
    }
    .predict-no {
        background: linear-gradient(135deg, #4f0d0d, #7a1a1a);
        border: 2px solid #e74c3c;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
    }
    .predict-yes h2, .predict-no h2 { margin: 0; font-size: 2rem; }
    .predict-yes p,  .predict-no p  { margin: 8px 0 0; font-size: 1.1rem; opacity: 0.9; }
    [data-testid="stSidebar"] { background: #161b2e; border-right: 1px solid #2d3250; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; padding: 0.6rem 2rem; width: 100%;
    }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #667eea;
        border-bottom: 2px solid #667eea; padding-bottom: 4px; margin: 20px 0 12px;
    }
</style>
""", unsafe_allow_html=True)


def check_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def make_prediction(payload):
    try:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()
        st.error(f"API Error {r.status_code}: {r.json().get('detail', 'Unknown error')}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to FastAPI. Run: uvicorn src.serving.api:app --reload --port 8000")
        return None

def get_mlflow_metrics():
    try:
        r = requests.get(f"{API_URL}/mlflow-metrics", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Bank Marketing\n### MLOps Dashboard")
    st.markdown("---")
    page = st.radio("Navigation", ["🏠 Home", "🔮 Predict", "📊 MLflow Metrics", "📁 Batch Predict"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 🔌 API Status")
    health = check_health()
    if health:
        st.success("FastAPI: Online ✅")
        st.markdown(f"- LightGBM: {'✅' if health.get('lgbm_loaded') else '❌'}")
        st.markdown(f"- XGBoost:  {'✅' if health.get('xgb_loaded') else '❌'}")
        st.markdown(f"- PySpark:  {'✅' if health.get('spark_model') else '❌'}")
        st.markdown(f"- MLflow:   {'✅' if health.get('mlflow_db') else '❌'}")
    else:
        st.error("FastAPI: Offline ❌")
        st.info("Run:\n```\nuvicorn src.serving.api:app --reload --port 8000\n```")
    st.markdown("---")
    st.caption("Bank Marketing MLOps | Saylani Welfare Trust")


# ── PAGE 1: HOME ──────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.title("🏦 Bank Marketing Subscription Predictor")
    st.markdown("**Predict whether a bank customer will subscribe to a term deposit.**")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔄 Data Pipeline")
        st.code("Raw CSV\n  ↓\nValidate\n  ↓\nClean\n  ↓\nFeature Eng.\n  ↓\nSMOTE Balance\n  ↓\nTrain (LGB/XGB)\n  ↓\nMLflow Track", language=None)
    with col2:
        st.markdown("### ⚡ PySpark Pipeline")
        st.code("Raw CSV\n  ↓\nSpark ETL\n  ↓\nGBT Training\n  ↓\nGrid Search\n  ↓\nThreshold Tuning\n  ↓\nMLflow Track", language=None)
    with col3:
        st.markdown("### 🌐 Serving Layer")
        st.code("Streamlit UI\n  ↓\nHTTP Request\n  ↓\nFastAPI\n  ↓\npredict.py\n  ↓\n.pkl / Spark Model\n  ↓\nPrediction", language=None)

    st.markdown("---")
    st.markdown("### 📊 Available Models")
    st.dataframe(pd.DataFrame({
        "Model":     ["LightGBM", "XGBoost", "PySpark GBT"],
        "Optimizer": ["Optuna TPE", "Optuna TPE", "Grid Search"],
        "Threshold": ["0.50 (params.yaml)", "0.50 (params.yaml)", "0.70 (fixed)"],
        "Tracking":  ["MLflow ✅", "MLflow ✅", "MLflow ✅"],
    }), use_container_width=True, hide_index=True)


# ── PAGE 2: PREDICT ───────────────────────────────────────────────────────────
elif page == "🔮 Predict":
    st.title("🔮 Customer Subscription Predictor")
    st.markdown("Fill in the customer details below to get a prediction.")

    col_m, col_t = st.columns(2)
    with col_m:
        model_type = st.selectbox("Select Model", ["lgbm", "xgb", "pyspark"],
                                  help="lgbm = LightGBM | xgb = XGBoost | pyspark = Spark GBT")
    with col_t:
        use_custom = st.checkbox("Use Custom Threshold?")
        threshold  = None
        if use_custom:
            threshold = st.slider("Decision Threshold", 0.0, 1.0, 0.70 if model_type == "pyspark" else 0.50, 0.05)

    st.markdown("---")

    with st.form("predict_form"):
        st.markdown('<div class="section-header">👤 Personal Information</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            age     = st.number_input("Age", 18, 100, 35)
            marital = st.selectbox("Marital Status", ["married", "single", "divorced"])
        with c2:
            job       = st.selectbox("Occupation", ["management","technician","blue-collar","admin.","services","retired","self-employed","entrepreneur","housemaid","student","unemployed","unknown"])
            education = st.selectbox("Education Level", ["tertiary","secondary","primary","unknown"])
        with c3:
            balance = st.number_input("Account Balance (€)", value=1500, step=100)
            default = st.selectbox("Credit in Default?", ["no","yes"])

        st.markdown('<div class="section-header">🏠 Loan Information</div>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4: housing = st.selectbox("Has Housing Loan?", ["yes","no"])
        with c5: loan    = st.selectbox("Has Personal Loan?", ["no","yes"])

        st.markdown('<div class="section-header">📞 Last Contact Details</div>', unsafe_allow_html=True)
        c6, c7, c8 = st.columns(3)
        with c6:
            contact = st.selectbox("Contact Type", ["cellular","telephone","unknown"])
            month   = st.selectbox("Month of Contact", ["may","jun","jul","aug","oct","nov","dec","jan","feb","mar","apr","sep"])
        with c7:
            day      = st.number_input("Day of Month", 1, 31, 15)
            duration = st.number_input("Call Duration (seconds)", min_value=1, value=300)
        with c8:
            campaign = st.number_input("Contacts This Campaign", 1, 100, 2)

        st.markdown('<div class="section-header">📋 Previous Campaign Info</div>', unsafe_allow_html=True)
        c9, c10, c11 = st.columns(3)
        with c9:  pdays    = st.number_input("Days Since Last Contact (-1 = Never)", min_value=-1, value=-1)
        with c10: previous = st.number_input("Previous Contacts Count", min_value=0, value=0)
        with c11: poutcome = st.selectbox("Previous Campaign Outcome", ["unknown","failure","success","other"])

        submitted = st.form_submit_button("🔮 Get Prediction")

    if submitted:
        payload = {
            "age": age, "job": job, "marital": marital, "education": education,
            "default": default, "balance": int(balance), "housing": housing,
            "loan": loan, "contact": contact, "day": int(day), "month": month,
            "duration": int(duration), "campaign": int(campaign), "pdays": int(pdays),
            "previous": int(previous), "poutcome": poutcome,
            "model_type": model_type, "threshold": threshold,
        }
        with st.spinner("Running prediction..."):
            result = make_prediction(payload)

        if result:
            r1, r2 = st.columns([2, 1])
            with r1:
                if result["prediction"] == 1:
                    st.markdown('<div class="predict-yes"><h2>✅ Will Subscribe!</h2><p>This customer is likely to subscribe to a term deposit.</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="predict-no"><h2>❌ Will NOT Subscribe</h2><p>This customer is unlikely to subscribe to a term deposit.</p></div>', unsafe_allow_html=True)
            with r2:
                st.metric("Subscription Probability", f"{result['probability']*100:.1f}%")
                st.metric("Model Used", result["model_used"].upper())
                st.metric("Decision Threshold", result["threshold_used"])
                st.progress(result["probability"])
                if result["probability"] >= 0.7:   st.success("High confidence!")
                elif result["probability"] >= 0.4: st.warning("Moderate confidence")
                else:                              st.error("Low likelihood")


# ── PAGE 3: MLFLOW METRICS ────────────────────────────────────────────────────
elif page == "📊 MLflow Metrics":
    st.title("📊 MLflow Experiment Tracking")
    st.markdown("View metrics and results from all model training runs.")

    if st.button("🔄 Refresh"): st.rerun()

    data = get_mlflow_metrics()
    if data is None:
        st.error("Cannot connect to FastAPI server.")
    elif "error" in data:
        st.warning(f"⚠️ {data['error']}")
        st.info("Run `python src/models/train.py` first to generate MLflow runs.")
    else:
        st.success(f"✅ Experiment: **{data['experiment']}**")
        runs = data.get("runs", [])
        if runs:
            latest = runs[0]
            st.markdown("### 🏆 Latest Run")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("AUC-ROC",   f"{latest.get('test_auc',0) or 0:.4f}"       if latest.get('test_auc')       else "N/A")
            c2.metric("F1 Score",  f"{latest.get('test_f1',0) or 0:.4f}"        if latest.get('test_f1')        else "N/A")
            c3.metric("Precision", f"{latest.get('test_precision',0) or 0:.4f}" if latest.get('test_precision') else "N/A")
            c4.metric("Recall",    f"{latest.get('test_recall',0) or 0:.4f}"    if latest.get('test_recall')    else "N/A")

            st.markdown("### 📋 All Runs")
            df = pd.DataFrame(runs)
            cols = [c for c in ["run_name","status","test_auc","test_f1","test_precision","test_recall","start_time"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True, hide_index=True)

            if "test_auc" in df.columns and df["test_auc"].notna().any():
                st.markdown("### 📈 AUC-ROC Comparison")
                st.bar_chart(df[["run_name","test_auc"]].dropna().set_index("run_name"))
        else:
            st.info("No runs found. Run train.py first!")


# ── PAGE 4: BATCH PREDICT ─────────────────────────────────────────────────────
elif page == "📁 Batch Predict":
    st.title("📁 Batch Prediction")
    st.markdown("Upload a CSV file to predict subscription likelihood for multiple customers.")

    st.markdown("### 📥 Sample CSV Template")
    sample = pd.DataFrame([
        {"age":35,"job":"management","marital":"married","education":"tertiary","default":"no","balance":1500,"housing":"yes","loan":"no","contact":"cellular","day":15,"month":"may","duration":300,"campaign":2,"pdays":-1,"previous":0,"poutcome":"unknown"},
        {"age":52,"job":"blue-collar","marital":"divorced","education":"secondary","default":"no","balance":200,"housing":"no","loan":"yes","contact":"telephone","day":8,"month":"nov","duration":120,"campaign":5,"pdays":-1,"previous":0,"poutcome":"unknown"},
    ])
    st.download_button("⬇️ Download Sample CSV", sample.to_csv(index=False).encode(), "sample_customers.csv", "text/csv")
    st.markdown("---")

    u1, u2 = st.columns([2,1])
    with u1: uploaded = st.file_uploader("Upload CSV", type=["csv"])
    with u2:
        bm = st.selectbox("Model", ["lgbm","xgb"], key="bm")
        bt = st.slider("Threshold", 0.0, 1.0, 0.5, 0.05, key="bt")

    if uploaded:
        df_up = pd.read_csv(uploaded)
        st.markdown(f"**{len(df_up)} records loaded**")
        st.dataframe(df_up.head(), use_container_width=True)

        if st.button("🚀 Run Batch Predictions"):
            recs = df_up.to_dict(orient="records")
            for r in recs:
                r["model_type"] = bm
                r["threshold"]  = bt

            with st.spinner(f"Predicting for {len(recs)} customers..."):
                try:
                    resp = requests.post(f"{API_URL}/batch", json={"records":recs,"model_type":bm,"threshold":bt}, timeout=60)
                    if resp.status_code == 200:
                        br = resp.json()
                        c1,c2,c3 = st.columns(3)
                        c1.metric("Total",            br["total_records"])
                        c2.metric("Will Subscribe ✅", br["subscribers"])
                        c3.metric("Will NOT ❌",       br["non_subscribers"])
                        res_df = pd.DataFrame(br["results"])
                        res_df.insert(0, "Customer #", range(1, len(res_df)+1))
                        st.dataframe(res_df, use_container_width=True)
                        st.download_button("⬇️ Download Results", res_df.to_csv(index=False).encode(), "predictions.csv", "text/csv")
                    else:
                        st.error(f"API Error: {resp.json().get('detail','Unknown')}")
                except requests.exceptions.ConnectionError:
                    st.error("FastAPI server is offline!")