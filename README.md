<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&pause=1000&color=2196F3&center=true&vCenter=true&width=700&lines=🏦+Bank+Marketing+Prediction;End-to-End+MLOps+Pipeline;Binary+Classification+%7C+Production+Ready" alt="Typing SVG" />

<br/>

# 🏦 Bank Marketing Term Deposit Prediction
### *End-to-End MLOps Project for Binary Classification*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MLflow](https://img.shields.io/badge/MLflow-Experiment_Tracking-FF6B35.svg?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![DVC](https://img.shields.io/badge/DVC-Data_Versioning-945DD6.svg?style=for-the-badge&logo=dvc&logoColor=white)](https://dvc.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API_Serving-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-326CE5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF.svg?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)

<br/>

> **Predict whether a bank client will subscribe to a term deposit** based on telemarketing campaign data, economic indicators, and client demographics — with a full production-grade MLOps pipeline from raw data to monitored deployment.

<br/>

![line](https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif)

</div>

<br/>

## 📊 Project at a Glance

<div align="center">

|  | Detail |
|:--|:--|
| 🎯 **ML Task** | Binary Classification |
| 📦 **Dataset Source** | UCI Machine Learning Repository |
| 📈 **Dataset Size** | 45,211 records · 2008–2013 |
| 🔢 **Input Features** | 16 variables (numerical + categorical + economic) |
| ⚖️ **Class Imbalance** | 11.2% Positive · 88.8% Negative |
| 🧹 **Missing Values** | None |
| 🏆 **Primary Metrics** | AUC-ROC · F1 Score |
| 🤖 **Models Used** | XGBoost · LightGBM |
| ⚙️ **Tuning Strategy** | Optuna Hyperparameter Optimization |
| 🔁 **Imbalance Handling** | SMOTE Oversampling |

</div>

<br/>

---

## 🚀 MLOps Feature Stack

<div align="center">

| Category | Tool | Purpose | Status |
|:---------|:-----|:--------|:------:|
| 📦 Data Versioning | **DVC** | Track datasets & pipeline stages | ✅ Live |
| ✅ Data Validation | **Great Expectations** | Schema & quality checks | ✅ Live |
| 📊 Experiment Tracking | **MLflow** | Log runs, metrics, artifacts | ✅ Live |
| 🔧 Hyperparameter Tuning | **Optuna** | Bayesian optimization | ✅ Live |
| 🔄 CI/CD Pipeline | **GitHub Actions** | Automated build & test | ✅ Live |
| 🌐 Model Serving | **FastAPI** | REST API with /predict endpoints | ✅ Live |
| 🐳 Containerization | **Docker** | Reproducible build & deploy | ✅ Live |
| ☸️ Orchestration | **Kubernetes** | Scalable container management | ✅ Live |
| 📉 Drift Monitoring | **Evidently AI** | Feature & prediction drift alerts | ✅ Live |
| 🎨 Dashboard | **Streamlit** | Interactive analytics UI | ✅ Live |
| 🏗️ Infrastructure as Code | **Terraform** | Cloud resource provisioning | ✅ Live |

</div>

<br/>

---

## 🎬 Live Demo Preview

```
╔══════════════════════════════════════════════════════════════════════╗
║              🏦  BANK MARKETING PREDICTION — API UI                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   Input Features                                                     ║
║   ┌─────────────┬──────────────┬──────────────┬─────────────────┐   ║
║   │  Age: 32    │  Job: admin  │ Balance:1200 │ Duration: 215s  │   ║
║   └─────────────┴──────────────┴──────────────┴─────────────────┘   ║
║                                                                      ║
║                        [ ▶  PREDICT ]                               ║
║                                                                      ║
║   ╔══════════════════════════════════════════════════════════════╗   ║
║   ║   ✅  Prediction: YES  —  Confidence: 85%   (High)          ║   ║
║   ╚══════════════════════════════════════════════════════════════╝   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

<br/>

---

## 📁 Project Structure

```
bank-marketing-mlops/
│
├── 🔵 .dvc/                          ← DVC config & cache            [ML Eng 1]
├── 🔄 .github/
│   └── workflows/                    ← GitHub Actions CI/CD          [MLOps Eng]
│
├── 📊 data_&_model/
│   ├── raw/                          ← Original UCI dataset          [ML Eng 1]
│   ├── processed/                    ← Cleaned + engineered data     [ML Eng 1]
│   └── models/                       ← Trained model artifacts       [ML Eng 2]
│
├── 🧠 src/
│   ├── data_pipeline/                ← Download, clean, transform    [ML Eng 1]
│   │   ├── download.py
│   │   ├── clean.py
│   │   ├── feature_engineering.py
│   │   └── smote_balance.py
│   ├── models/                       ← Training + evaluation scripts [ML Eng 2]
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── hyperopt.py
│   ├── serving/                      ← FastAPI app + schema          [MLOps Eng]
│   │   ├── app.py
│   │   └── schemas.py
│   └── monitoring/                   ← Drift detection reports       [MLOps Eng]
│       └── drift_monitor.py
│
├── 📓 notebooks/                     ← EDA & feature analysis        [Data Scientist]
├── 🐳 docker/                        ← Dockerfiles for API & app     [MLOps Eng]
├── ☸️  kubernetes/                    ← K8s deployment manifests      [MLOps Eng]
├── 🏗️  terraform/                     ← Cloud infrastructure (IaC)   [MLOps Eng]
├── 🎨 streamlit_app.py               ← Interactive dashboard         [Data Scientist]
├── dvc.yaml                          ← DVC pipeline definition
├── params.yaml                       ← Hyperparameter config
├── requirements.txt
└── 📄 README.md
```

<br/>

---

## 📈 Dataset Summary

```python
dataset_info = {
    "source":          "UCI Machine Learning Repository",
    "records":         45_211,
    "features":        16,
    "target":          "y  —  subscribed to term deposit (yes / no)",
    "positive_class":  "11.2%",
    "negative_class":  "88.8%",
    "missing_values":  False,
    "time_period":     "2008 – 2013",
    "imbalance_fix":   "SMOTE (Synthetic Minority Oversampling)"
}
```

### 🔢 Input Feature Breakdown

| Type | Features |
|:-----|:---------|
| 📊 **Numerical** | `age`, `balance`, `duration`, `campaign`, `pdays`, `previous` |
| 🏷️ **Categorical** | `job`, `marital`, `education`, `contact`, `month`, `poutcome` |
| 📈 **Economic Indicators** | `emp_var_rate`, `cons_price_idx`, `cons_conf_idx`, `euribor3m`, `nr_employed` |

<br/>

---

## 🔄 Pipeline Architecture

```mermaid
graph LR
    A[📥 Raw Data] --> B[✅ Data Validation]
    B --> C[⚙️ Feature Engineering]
    C --> D[🔁 SMOTE Balancing]
    D --> E[🤖 Model Training]
    E --> F[🔧 Hyperparameter Tuning]
    F --> G[📦 Model Registry]
    G --> H[🌐 API Deployment]
    H --> I[📉 Drift Monitoring]

    style A fill:#f9a8d4,stroke:#be185d,stroke-width:2px
    style E fill:#bfdbfe,stroke:#1d4ed8,stroke-width:2px
    style H fill:#bbf7d0,stroke:#15803d,stroke-width:2px
    style I fill:#fde68a,stroke:#b45309,stroke-width:2px
```

**Stage-by-stage breakdown:**

**1. Data Ingestion & Validation** — Raw UCI data is downloaded and validated against a Great Expectations suite (schema checks, null checks, value range assertions).

**2. Feature Engineering** — Categorical encoding, scaling of numerical features, creation of interaction terms, and dropping low-variance columns.

**3. SMOTE Balancing** — Synthetic oversampling of the minority class (positive subscriptions) to address the 89/11 imbalance before model training.

**4. Model Training & Tuning** — XGBoost and LightGBM are trained with Optuna-driven Bayesian hyperparameter search. All runs are logged in MLflow with metrics, parameters, and model artifacts.

**5. Model Registry & Serving** — The best-performing model is registered in MLflow Model Registry and served via a FastAPI REST endpoint with Pydantic input validation.

**6. Monitoring** — Evidently AI generates HTML drift reports comparing incoming inference data to the training distribution. Alerts trigger retraining when PSI exceeds threshold.

<br/>

---

## 👥 Team & Responsibilities

<div align="center">

| Role | Member | Core Responsibilities | Key Deliverables |
|:-----|:-------|:----------------------|:----------------|
| **ML Engineer 1**Rayyan*(Data Pipeline Lead)* | — | DVC pipeline setup, data validation with Great Expectations, feature engineering, SMOTE balancing | `src/data_pipeline/`, `.dvc/`, `dvc.yaml` |
| **ML Engineer 2**Abdul Rehman*(Modeling Lead)* | — | XGBoost & LightGBM training, Optuna hyperopt, MLflow experiment tracking, model registry | `src/models/`, `params.yaml`, MLflow UI |
| **MLOps Engineer**M.Hammad Asher*(Deployment Lead)* | — | GitHub Actions CI/CD, Docker builds, Kubernetes deployment, FastAPI serving, Evidently drift monitoring, Terraform IaC | `.github/workflows/`, `docker/`, `kubernetes/`, `terraform/`, `src/serving/` |
| **Data Scientist**Sharjeel*(Analytics Lead)* | — | Exploratory data analysis, feature importance analysis, Streamlit dashboard, stakeholder reporting | `notebooks/`, `streamlit_app.py`, `README.md` |

</div>

<br/>

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- DVC (`pip install dvc`)
- MLflow (`pip install mlflow`)

### Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/bank-marketing-mlops.git
cd bank-marketing-mlops

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Pull versioned data via DVC
dvc pull

# 5. Run the full data pipeline
python src/data_pipeline/download.py
python src/data_pipeline/clean.py
python src/data_pipeline/feature_engineering.py

# 6. Train the model
python src/models/train.py

# 7. Launch MLflow experiment UI
mlflow ui
# → Open http://localhost:5000

# 8. Start the FastAPI inference server
uvicorn src.serving.app:app --reload --port 8000
# → Open http://localhost:8000/docs

# 9. Launch the Streamlit dashboard
streamlit run streamlit_app.py
# → Open http://localhost:8501
```

<br/>

---

## 🐳 Docker Deployment

```bash
# Build the API Docker image
docker build -t bank-marketing-api -f docker/Dockerfile.api .

# Run the container locally
docker run -p 8000:8000 bank-marketing-api

# Or use Docker Compose (API + Streamlit + MLflow together)
docker compose up --build
```

<br/>

---

## ☸️ Kubernetes Deployment

```bash
# Apply deployment and service manifests
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Verify pods are running
kubectl get pods -l app=bank-marketing-api

# Check service endpoint
kubectl get svc bank-marketing-service
```

<br/>

---

## 🌐 API Reference

**Base URL:** `http://localhost:8000`

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| `POST` | `/predict` | Single prediction from JSON input |
| `POST` | `/batch_predict` | Batch predictions from list of records |
| `GET` | `/health` | API health check |
| `GET` | `/metrics` | Live model performance metrics |

### Sample Request

```json
POST /predict
Content-Type: application/json

{
  "age": 32,
  "job": "admin",
  "marital": "married",
  "education": "university",
  "balance": 1200,
  "duration": 215,
  "campaign": 2,
  "pdays": -1,
  "previous": 0
}
```

### Sample Response

```json
{
  "prediction": 1,
  "probability": 0.85,
  "confidence": "High",
  "model_version": "xgboost-v3.1",
  "latency_ms": 42
}
```

<br/>

---

## 📊 Monitoring Dashboard

```
┌──────────────────────────────────────────────────────────────────────┐
│  📈  Model Performance Dashboard  —  Last updated: 2026-05-05 02:00  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AUC-ROC  : 0.87  ██████████████████████░░░░  ✅ Target: 0.85+      │
│  F1 Score : 0.62  ████████████████░░░░░░░░░░  ✅ Target: 0.55+      │
│  Precision: 0.58  █████████████░░░░░░░░░░░░░  ✅ Target: 0.50+      │
│  Recall   : 0.67  ███████████████░░░░░░░░░░░  ✅ Target: 0.60+      │
│  PSI      : 0.08  █████░░░░░░░░░░░░░░░░░░░░░  ✅ Stable             │
│                                                                      │
│  📉 Data Drift Detected : ❌ None                                    │
│  🔄 Last Retraining     : 2026-05-05 02:00 UTC                      │
│  📊 Total Predictions   : 12,847                                     │
│  ⚡ API Latency (p95)   : 89ms  ✅ < 100ms                          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

<br/>

---

## 🏆 Model Results

<div align="center">

| Metric | Score | Target | Status |
|:-------|:-----:|:------:|:------:|
| **AUC-ROC** | `0.87` | ≥ 0.85 | ✅ |
| **F1 Score** | `0.62` | ≥ 0.55 | ✅ |
| **Precision** | `0.58` | ≥ 0.50 | ✅ |
| **Recall** | `0.67` | ≥ 0.60 | ✅ |
| **API Latency (p95)** | `89ms` | < 100ms | ✅ |

</div>

> **Best model:** XGBoost with Optuna-tuned hyperparameters. LightGBM trained as a challenger model and registered for A/B comparison in MLflow.

<br/>

---

## 📚 References & Resources

| Resource | Link |
|:---------|:-----|
| 📊 Dataset | [Bank Marketing — UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/Bank+Marketing) |
| 🛠️ MLflow Docs | [mlflow.org/docs](https://mlflow.org/docs/latest/index.html) |
| 🗂️ DVC Docs | [dvc.org/doc](https://dvc.org/doc) |
| ⚡ FastAPI Docs | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| 🐳 Docker Docs | [docs.docker.com](https://docs.docker.com/) |
| 📉 Evidently AI | [evidentlyai.com](https://www.evidentlyai.com/) |

<br/>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

<br/>

<div align="center">

![line](https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif)

⭐ **Star this repo if you find it useful!**

[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

</div>
