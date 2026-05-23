# 🏦 Bank Marketing Term Deposit Prediction — MLOps Project

A production-grade MLOps pipeline to predict whether a bank client will subscribe to a term deposit based on direct marketing campaign data.

---

## 🔗 Live Links

| Resource | Link |
|---|---|
| 🌐 Live Dashboard | [mlops-saylani.streamlit.app](https://mlops-saylani-9deyypoxdzmnsr4wvuyshg.streamlit.app/) |
| 🧪 Experiment Tracking (DagsHub) | [dagshub.com/hammadAsher100/MLOps-Saylani](https://dagshub.com/hammadAsher100/MLOps-Saylani) |
| 🐳 Docker Image | [hub.docker.com/r/hammadasher/bank_predict](https://hub.docker.com/repository/docker/hammadasher/bank_predict/general) |

---

## 📁 Project Structure

```
bank_marketing_mlops/
├── .dvc/                    # DVC configuration & remote
├── .github/workflows/       # CI/CD & retraining pipelines
├── data_and_model/          # Data & model artifacts (DVC-tracked)
│   ├── raw/                 # bank-additional-full.csv (45,211 rows)
│   ├── processed/           # Cleaned & balanced datasets
│   ├── features/            # Feature-engineered outputs
│   └── models/              # Trained .pkl files + metrics.json
├── src/
│   ├── data_pipeline/       # Download → Validate → Clean → Engineer → Balance
│   ├── models/              # Train → HyperOpt → Calibrate → Predict
│   ├── serving/             # FastAPI schema + endpoints
│   └── monitoring/          # Drift detection + PSI metrics
├── tests/                   # Unit & integration tests (pytest)
├── notebooks/               # EDA & model development (Jupyter)
├── docker/                  # Dockerfiles for API and Streamlit
├── kubernetes/              # K8s deployment, service, HPA
├── terraform/               # Cloud infrastructure as code
├── app.py                   # FastAPI entrypoint
├── prediction.py            # Batch inference script
├── streamlit_app.py         # Marketing team dashboard
├── params.yaml              # All hyperparameters & config
├── dvc.yaml                 # DVC pipeline stages
└── requirements.txt         # Python dependencies
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/hammadAsher100/MLOps-Saylani.git
cd bank_marketing_mlops
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your credentials
```

### 2. Pull Data with DVC
```bash
dvc pull
```

### 3. Run the Full Pipeline
```bash
dvc repro
```

### 4. Start the API
```bash
uvicorn app:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

### 5. Launch the Dashboard
```bash
streamlit run streamlit_app.py
# Dashboard: http://localhost:8501
```

### 6. Track Experiments
```bash
mlflow ui --port 5000
# UI: http://localhost:5000
```

---

## 🐳 Docker

Pull and run the pre-built image from Docker Hub:

```bash
docker pull hammadasher/bank_predict:latest
docker run -p 8000:8000 hammadasher/bank_predict:latest
```

Image: [hub.docker.com/r/hammadasher/bank_predict](https://hub.docker.com/repository/docker/hammadasher/bank_predict/general)

---

## 🔄 CI/CD Pipeline

| Workflow | Trigger | Stages |
|---|---|---|
| `ci.yml` | PR to main/develop | Lint → Test → Validate → Model Gate → Docker Build |
| `cd_deploy.yml` | Push to main | Build Images → Deploy Staging → Deploy Production |
| `retrain_schedule.yml` | Every Sunday 02:00 UTC | Drift Check → Retrain → Promote |

---

## 👥 Team Roles

| Role | Responsibility | Key Files |
|---|---|---|
| ML Engineer 1 | Data pipeline + DVC + Feature engineering | `src/data_pipeline/` |
| ML Engineer 2 | Model training + MLflow + Hyperparameter tuning | `src/models/` |
| MLOps Engineer | CI/CD + Docker + Kubernetes + Monitoring | `.github/`, `docker/`, `kubernetes/`, `src/monitoring/` |
| Data Scientist | EDA + Dashboard + Business insights | `notebooks/`, `streamlit_app.py` |

---

## 📊 Dataset

- **Source:** [Bank Marketing UCI Dataset](https://www.kaggle.com/datasets/ashnaimtiaz/bank-marketing-uci-dataset)
- **Records:** 45,211 rows × 17 columns
- **Target:** `y` — binary (yes/no) subscription to term deposit
- **Class distribution:** ~11% positive, ~89% negative (imbalanced)

---

## 🔑 Key MLOps Design Decisions

- **Imbalanced classes** handled with SMOTE (configurable via `params.yaml`)
- **Data validation** via Great Expectations on every pipeline run
- **Experiment tracking** with MLflow — all runs, params, and metrics logged
- **Drift detection** with Evidently AI — auto-triggers retraining when PSI > 0.2
- **Probability calibration** via Platt scaling for reliable confidence scores
- **Model gate** in CI — blocks deployment if F1 < 0.60 or AUC < 0.75