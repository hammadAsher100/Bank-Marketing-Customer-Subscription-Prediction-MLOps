"""
streamlit_app.py  (place in project root)
Bank Marketing MLOps Dashboard - English Version
"""

import streamlit as st
import requests
import pandas as pd

import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ═══════════════════════════════════════════════════════════════════════════════
# STYLING & PAGE CONFIGURATION (UI layer only)
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Bank Marketing MLOps",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

_CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-base: #0F172A;
        --bg-elevated: #1E293B;
        --bg-card: #1E293B;
        --border: #334155;
        --border-soft: #475569;
        --accent: #2563EB;
        --accent-hover: #3B82F6;
        --accent-cyan: #0EA5E9;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --success: #10B981;
        --success-bg: #064E3B;
        --danger: #EF4444;
        --danger-bg: #7F1D1D;
        --warning: #F59E0B;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.25), 0 2px 4px -2px rgb(0 0 0 / 0.2);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.2);
    }

    .stApp {
        background: linear-gradient(165deg, #0F172A 0%, #0B1220 45%, #0F172A 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: var(--text-primary);
    }

    [data-testid="stAppViewContainer"] > section.main > div {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.02em;
    }

    p, label, .stMarkdown, span {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1220 0%, #0F172A 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        margin-bottom: 0.15rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--accent-cyan) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: var(--text-secondary) !important;
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        gap: 0.35rem;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 0.55rem 0.75rem !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
        border-color: var(--accent);
        background: rgba(37, 99, 235, 0.12);
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] label {
        border-color: var(--accent) !important;
        background: rgba(37, 99, 235, 0.2) !important;
        color: var(--text-primary) !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.9));
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem 1.15rem !important;
        box-shadow: var(--shadow);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--accent-cyan);
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1.65rem !important;
    }

    /* Primary / form buttons */
    .stButton > button,
    [data-testid="stFormSubmitButton"] button,
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, var(--accent) 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, var(--accent-hover) 0%, var(--accent) 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.55) !important;
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Inputs */
    .stSelectbox > div > div,
    .stNumberInput > div > div > div,
    .stTextInput > div > div > div {
        background-color: var(--bg-elevated) !important;
        border-color: var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }
    .stCheckbox label span {
        color: var(--text-secondary) !important;
    }

    /* Containers with border */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.25rem 1.5rem !important;
        box-shadow: var(--shadow);
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--accent-cyan)) !important;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1rem 0;
    }

    /* Custom UI blocks */
    .ui-hero {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.18) 0%, rgba(14, 165, 233, 0.08) 100%);
        border: 1px solid rgba(37, 99, 235, 0.35);
        border-radius: var(--radius-lg);
        padding: 1.75rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-lg);
    }
    .ui-hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text-primary);
        background: linear-gradient(90deg, #F8FAFC, #93C5FD);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .ui-hero p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .ui-hero-badge {
        display: inline-block;
        margin-top: 0.85rem;
        padding: 0.35rem 0.85rem;
        background: rgba(14, 165, 233, 0.15);
        border: 1px solid rgba(14, 165, 233, 0.4);
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--accent-cyan);
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .section-header {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--accent-cyan);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border-bottom: 2px solid rgba(14, 165, 233, 0.35);
        padding-bottom: 0.5rem;
        margin: 1.25rem 0 1rem 0;
    }

    .predict-yes {
        background: linear-gradient(135deg, var(--success-bg) 0%, #065F46 100%);
        border: 2px solid var(--success);
        border-radius: var(--radius-lg);
        padding: 2rem 1.5rem;
        text-align: center;
        margin: 0;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.15);
    }
    .predict-no {
        background: linear-gradient(135deg, var(--danger-bg) 0%, #991B1B 100%);
        border: 2px solid var(--danger);
        border-radius: var(--radius-lg);
        padding: 2rem 1.5rem;
        text-align: center;
        margin: 0;
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.12);
    }
    .predict-yes h2, .predict-no h2 {
        margin: 0;
        font-size: 2.25rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    .predict-yes p, .predict-no p {
        margin: 0.65rem 0 0;
        font-size: 1.05rem;
        color: var(--text-secondary);
        line-height: 1.45;
    }

    .result-probability {
        font-size: 3rem;
        font-weight: 800;
        color: var(--accent-cyan);
        line-height: 1;
        letter-spacing: -0.03em;
        text-align: center;
        margin: 0.5rem 0;
    }
    .result-probability-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        text-align: center;
        margin-bottom: 1rem;
    }

    .pipeline-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        height: 100%;
        box-shadow: var(--shadow);
    }
    .pipeline-card h3 {
        margin: 0 0 0.75rem 0;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .sidebar-status-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.4rem 0;
        font-size: 0.88rem;
        color: var(--text-secondary);
        border-bottom: 1px solid rgba(51, 65, 85, 0.5);
    }
    .sidebar-status-item:last-child { border-bottom: none; }
    .status-dot-on { color: var(--success); font-weight: 700; }
    .status-dot-off { color: var(--danger); font-weight: 700; }

    /* Hide Streamlit header chrome for cleaner look */
    [data-testid="stHeader"] {
        background: transparent;
    }
    footer { visibility: hidden; }
</style>
"""

st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


def _section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def _page_hero(title: str, subtitle: str, badge: str = ""):
    badge_html = f'<span class="ui-hero-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="ui-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CORE LOGIC (unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

def check_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def make_prediction(payload):
    try:
        # PySpark needs longer timeout due to SparkSession startup
        timeout = 120 if payload.get("model_type") == "pyspark" else 30
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        try:
            detail = r.json().get('detail', 'Unknown error')
        except Exception:
            detail = r.text
        st.error(f"API Error {r.status_code}: {detail}")
        return None
    except requests.exceptions.ReadTimeout:
        st.error(
            "⏱️ **Request timed out** — the server took too long to respond.\n\n"
            "This usually happens when the PySpark model is loading for the first time "
            "(SparkSession startup can take 30-60 seconds).\n\n"
            "**Try again** — subsequent requests will be much faster."
        )
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to FastAPI. Run: `uvicorn src.serving.api:app --reload --port 8000`")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def get_mlflow_metrics():
    try:
        r = requests.get(f"{API_URL}/mlflow-metrics", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🏦 Bank Marketing\n### MLOps Dashboard")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Home", "🔮 Predict", "📊 MLflow Metrics", "📁 Batch Predict"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### 🔌 API Status")

    health = check_health()
    if health:
        st.success("FastAPI: Online ✅")
        status_rows = [
            ("LightGBM", health.get("lgbm_loaded")),
            ("XGBoost", health.get("xgb_loaded")),
            ("PySpark", health.get("spark_model")),
            ("MLflow", health.get("mlflow_db")),
        ]
        for name, ok in status_rows:
            dot = '<span class="status-dot-on">●</span>' if ok else '<span class="status-dot-off">●</span>'
            st.markdown(
                f'<div class="sidebar-status-item"><span>{name}</span>{dot}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.error("FastAPI: Offline ❌")
        st.info("Run:\n```\nuvicorn src.serving.api:app --reload --port 8000\n```")

    st.divider()
    st.caption("Bank Marketing MLOps | Saylani Welfare Trust")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: HOME
# ═══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Home":
    _page_hero(
        "🏦 Bank Marketing Subscription Predictor",
        "Predict whether a bank customer will subscribe to a term deposit.",
        badge="MLOps Production Dashboard",
    )

    tab_overview, tab_models = st.tabs(["System Overview", "Model Registry"])

    with tab_overview:
        col1, col2, col3 = st.columns(3, gap="medium")

        with col1:
            with st.container(border=True):
                st.markdown('<div class="pipeline-card"><h3>🔄 Data Pipeline</h3></div>', unsafe_allow_html=True)
                st.code(
                    "Raw CSV\n  ↓\nValidate\n  ↓\nClean\n  ↓\nFeature Eng.\n  ↓\nSMOTE Balance\n  ↓\nTrain (LGB/XGB)\n  ↓\nMLflow Track",
                    language=None,
                )

        with col2:
            with st.container(border=True):
                st.markdown('<div class="pipeline-card"><h3>⚡ PySpark Pipeline</h3></div>', unsafe_allow_html=True)
                st.code(
                    "Raw CSV\n  ↓\nSpark ETL\n  ↓\nGBT Training\n  ↓\nGrid Search\n  ↓\nThreshold Tuning\n  ↓\nMLflow Track",
                    language=None,
                )

        with col3:
            with st.container(border=True):
                st.markdown('<div class="pipeline-card"><h3>🌐 Serving Layer</h3></div>', unsafe_allow_html=True)
                st.code(
                    "Streamlit UI\n  ↓\nHTTP Request\n  ↓\nFastAPI\n  ↓\npredict.py\n  ↓\n.pkl / Spark Model\n  ↓\nPrediction",
                    language=None,
                )

    with tab_models:
        st.markdown("### 📊 Available Models")
        with st.container(border=True):
            st.dataframe(
                pd.DataFrame({
                    "Model":     ["LightGBM", "XGBoost", "PySpark GBT"],
                    "Optimizer": ["Optuna TPE", "Optuna TPE", "Grid Search"],
                    "Threshold": ["0.50 (params.yaml)", "0.50 (params.yaml)", "0.70 (fixed)"],
                    "Tracking":  ["MLflow ✅", "MLflow ✅", "MLflow ✅"],
                }),
                use_container_width=True,
                hide_index=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: PREDICT
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "🔮 Predict":
    _page_hero(
        "🔮 Customer Subscription Predictor",
        "Fill in the customer details below to get a prediction.",
        badge="Real-time inference",
    )

    with st.container(border=True):
        col_m, col_t = st.columns(2, gap="large")
        with col_m:
            model_type = st.selectbox(
                "Select Model",
                ["lgbm", "xgb", "pyspark"],
                help="lgbm = LightGBM | xgb = XGBoost | pyspark = Spark GBT",
            )
        with col_t:
            use_custom = st.checkbox("Use Custom Threshold?")
            threshold = None
            if use_custom:
                threshold = st.slider(
                    "Decision Threshold",
                    0.0, 1.0,
                    0.70 if model_type == "pyspark" else 0.50,
                    0.05,
                )

    st.divider()

    with st.form("predict_form"):
        with st.container(border=True):
            _section_header("👤 Personal Information")
            c1, c2, c3 = st.columns(3, gap="medium")
            with c1:
                age     = st.number_input("Age", 18, 100, 35)
                marital = st.selectbox("Marital Status", ["married", "single", "divorced"])
            with c2:
                job       = st.selectbox(
                    "Occupation",
                    ["management","technician","blue-collar","admin.","services","retired",
                     "self-employed","entrepreneur","housemaid","student","unemployed","unknown"],
                )
                education = st.selectbox("Education Level", ["tertiary","secondary","primary","unknown"])
            with c3:
                balance = st.number_input("Account Balance (€)", value=1500, step=100)
                default = st.selectbox("Credit in Default?", ["no","yes"])

        with st.container(border=True):
            _section_header("🏠 Loan Information")
            c4, c5 = st.columns(2, gap="large")
            with c4:
                housing = st.selectbox("Has Housing Loan?", ["yes","no"])
            with c5:
                loan = st.selectbox("Has Personal Loan?", ["no","yes"])

        with st.container(border=True):
            _section_header("📞 Last Contact Details")
            c6, c7, c8 = st.columns(3, gap="medium")
            with c6:
                contact = st.selectbox("Contact Type", ["cellular","telephone","unknown"])
                month   = st.selectbox(
                    "Month of Contact",
                    ["may","jun","jul","aug","oct","nov","dec","jan","feb","mar","apr","sep"],
                )
            with c7:
                day      = st.number_input("Day of Month", 1, 31, 15)
                duration = st.number_input("Call Duration (seconds)", min_value=1, value=300)
            with c8:
                campaign = st.number_input("Contacts This Campaign", 1, 100, 2)

        with st.container(border=True):
            _section_header("📋 Previous Campaign Info")
            c9, c10, c11 = st.columns(3, gap="medium")
            with c9:
                pdays = st.number_input("Days Since Last Contact (-1 = Never)", min_value=-1, value=-1)
            with c10:
                previous = st.number_input("Previous Contacts Count", min_value=0, value=0)
            with c11:
                poutcome = st.selectbox(
                    "Previous Campaign Outcome",
                    ["unknown","failure","success","other"],
                )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🔮 Get Prediction", type="primary", use_container_width=True)

    if submitted:
        payload = {
            "age": age, "job": job, "marital": marital, "education": education,
            "default": default, "balance": int(balance), "housing": housing,
            "loan": loan, "contact": contact, "day": int(day), "month": month,
            "duration": int(duration), "campaign": int(campaign), "pdays": int(pdays),
            "previous": int(previous), "poutcome": poutcome,
            "model_type": model_type, "threshold": threshold,
        }
        with st.spinner("Analyzing parameters and generating prediction..."):
            result = make_prediction(payload)

        if result:
            label = "Will Subscribe" if result["prediction"] == 1 else "Will NOT Subscribe"
            st.toast(f"Prediction complete: {label}", icon="✅")

            st.divider()
            st.markdown("### Prediction Results")

            if "message" in result:
                st.warning(f"⚠️ **Note:** {result['message']}")
            
            r1, r2 = st.columns([2, 1], gap="large")

            with r1:
                with st.container(border=True):
                    if result["prediction"] == 1:
                        st.markdown(
                            '<div class="predict-yes"><h2>✅ Will Subscribe!</h2>'
                            '<p>This customer is likely to subscribe to a term deposit.</p></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="predict-no"><h2>❌ Will NOT Subscribe</h2>'
                            '<p>This customer is unlikely to subscribe to a term deposit.</p></div>',
                            unsafe_allow_html=True,
                        )

            with r2:
                with st.container(border=True):
                    st.markdown(
                        '<div class="result-probability-label">Subscription Probability</div>'
                        f'<div class="result-probability">{result["probability"]*100:.1f}%</div>',
                        unsafe_allow_html=True,
                    )
                    st.metric("Model Used", result["model_used"].upper())
                    st.metric("Decision Threshold", result["threshold_used"])
                    st.progress(result["probability"])
                    if result["probability"] >= 0.7:
                        st.success("High confidence!")
                    elif result["probability"] >= 0.4:
                        st.warning("Moderate confidence")
                    else:
                        st.error("Low likelihood")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: MLFLOW METRICS
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📊 MLflow Metrics":
    _page_hero(
        "📊 MLflow Experiment Tracking",
        "View metrics and results from all model training runs.",
        badge="Experiment monitoring",
    )

    col_refresh, _ = st.columns([1, 4])
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    data = get_mlflow_metrics()
    if data is None:
        st.error("Cannot connect to FastAPI server.")
    elif "error" in data:
        st.warning(f"⚠️ {data['error']}")
        st.info("Run `python src/models/train.py` first to generate MLflow runs.")
    else:
        st.toast(f"Loaded experiment: {data['experiment']}", icon="📊")
        st.success(f"✅ Experiment: **{data['experiment']}**")

        runs = data.get("runs", [])
        if runs:
            latest = runs[0]

            with st.container(border=True):
                st.markdown("### 🏆 Latest Run")
                c1, c2, c3, c4 = st.columns(4, gap="medium")
                c1.metric("AUC-ROC",   f"{latest.get('test_auc',0) or 0:.4f}"       if latest.get('test_auc')       else "N/A")
                c2.metric("F1 Score",  f"{latest.get('test_f1',0) or 0:.4f}"        if latest.get('test_f1')        else "N/A")
                c3.metric("Precision", f"{latest.get('test_precision',0) or 0:.4f}" if latest.get('test_precision') else "N/A")
                c4.metric("Recall",    f"{latest.get('test_recall',0) or 0:.4f}"    if latest.get('test_recall')    else "N/A")

            with st.container(border=True):
                st.markdown("### 📋 All Runs")
                df = pd.DataFrame(runs)
                cols = [c for c in ["run_name","status","test_auc","test_f1","test_precision","test_recall","start_time"] if c in df.columns]
                st.dataframe(df[cols], use_container_width=True, hide_index=True)

            if "test_auc" in df.columns and df["test_auc"].notna().any():
                with st.container(border=True):
                    st.markdown("### 📈 AUC-ROC Comparison")
                    st.bar_chart(df[["run_name","test_auc"]].dropna().set_index("run_name"))
        else:
            st.info("No runs found. Run train.py first!")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: BATCH PREDICT
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📁 Batch Predict":
    _page_hero(
        "📁 Batch Prediction",
        "Upload a CSV file to predict subscription likelihood for multiple customers.",
        badge="Bulk inference",
    )

    tab_template, tab_upload = st.tabs(["Sample Template", "Upload & Predict"])

    with tab_template:
        with st.container(border=True):
            st.markdown("### 📥 Sample CSV Template")
            sample = pd.DataFrame([
                {"age":35,"job":"management","marital":"married","education":"tertiary","default":"no","balance":1500,"housing":"yes","loan":"no","contact":"cellular","day":15,"month":"may","duration":300,"campaign":2,"pdays":-1,"previous":0,"poutcome":"unknown"},
                {"age":52,"job":"blue-collar","marital":"divorced","education":"secondary","default":"no","balance":200,"housing":"no","loan":"yes","contact":"telephone","day":8,"month":"nov","duration":120,"campaign":5,"pdays":-1,"previous":0,"poutcome":"unknown"},
            ])
            st.download_button(
                "⬇️ Download Sample CSV",
                sample.to_csv(index=False).encode(),
                "sample_customers.csv",
                "text/csv",
                use_container_width=True,
            )

    with tab_upload:
        with st.container(border=True):
            u1, u2 = st.columns([2, 1], gap="large")
            with u1:
                uploaded = st.file_uploader("Upload CSV", type=["csv"])
            with u2:
                bm = st.selectbox("Model", ["lgbm","xgb"], key="bm")
                bt = st.slider("Threshold", 0.0, 1.0, 0.5, 0.05, key="bt")

        if uploaded:
            df_up = pd.read_csv(uploaded)
            st.info(f"**{len(df_up)} records loaded**")

            with st.container(border=True):
                st.dataframe(df_up.head(), use_container_width=True)

            if st.button("🚀 Run Batch Predictions", type="primary", use_container_width=True):
                recs = df_up.to_dict(orient="records")
                for r in recs:
                    r["model_type"] = bm
                    r["threshold"]  = bt

                with st.spinner(f"Analyzing {len(recs)} customer records..."):
                    try:
                        resp = requests.post(
                            f"{API_URL}/batch",
                            json={"records":recs,"model_type":bm,"threshold":bt},
                            timeout=120,
                        )
                        if resp.status_code == 200:
                            br = resp.json()
                            
                            # Check for fallback message
                            if br.get("model_used") == "lgbm_fallback" and br.get("message"):
                                st.warning(f"⚠️ **Note:** {br['message']}")

                            st.toast(
                                f"Batch complete: {br['subscribers']} subscribers / {br['total_records']} total",
                                icon="✅",
                            )

                            with st.container(border=True):
                                c1, c2, c3 = st.columns(3, gap="medium")
                                c1.metric("Total",            br["total_records"])
                                c2.metric("Will Subscribe ✅", br["subscribers"])
                                c3.metric("Will NOT ❌",       br["non_subscribers"])

                            res_df = pd.DataFrame(br["results"])
                            res_df.insert(0, "Customer #", range(1, len(res_df)+1))

                            with st.container(border=True):
                                st.dataframe(res_df, use_container_width=True)

                            st.download_button(
                                "⬇️ Download Results",
                                res_df.to_csv(index=False).encode(),
                                "predictions.csv",
                                "text/csv",
                                use_container_width=True,
                            )
                        else:
                            try:
                                detail = resp.json().get('detail', 'Unknown')
                            except Exception:
                                detail = resp.text
                            st.error(f"API Error: {detail}")
                    except requests.exceptions.ReadTimeout:
                        st.error(
                            "⏱️ **Batch request timed out** — try with fewer records or try again."
                        )
                    except requests.exceptions.ConnectionError:
                        st.error("FastAPI server is offline!")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Request failed: {e}")
