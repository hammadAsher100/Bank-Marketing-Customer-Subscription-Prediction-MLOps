---
title: Bank Marketing Prediction
emoji: 🏦
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.41.1"
app_file: streamlit_app.py
pinned: false
license: mit
---

# 🏦 Bank Marketing Term Deposit Prediction — MLOps Project

A production-grade MLOps pipeline to predict whether a bank client will subscribe to a term deposit based on direct marketing campaign data.

## 🌐 Live Demo

**Try it now:** [https://huggingface.co/spaces/Unknown213141/BankPrediction](https://huggingface.co/spaces/Unknown213141/BankPrediction)

## 🔗 Quick Links

| Resource | Link | Description |
|----------|------|-------------|
| 🚀 **Live Demo** | [Hugging Face Spaces](https://huggingface.co/spaces/Unknown213141/BankPrediction) | Try the app now! |
| 💻 **Source Code** | [GitHub Repository](https://github.com/hammadAsher100/Bank-Marketing-Customer-Subscription-Prediction-MLOps) | Full source code |
| 🐳 **Docker - Backend** | [mlops-saylani-api](https://hub.docker.com/r/hammadasher/mlops-saylani-api) | FastAPI container |
| 🐳 **Docker - Frontend** | [mlops-saylani-frontend](https://hub.docker.com/r/hammadasher/mlops-saylani-frontend) | Streamlit container |

---

## 🚀 Features

- **Machine Learning Models**: LightGBM and XGBoost with hyperparameter optimization
- **Interactive Dashboard**: Real-time predictions with Streamlit UI
- **REST API**: FastAPI backend for model serving
- **Experiment Tracking**: MLflow integration for model versioning
- **Data Pipeline**: Automated data validation, cleaning, and feature engineering
- **Monitoring**: Model performance and data drift detection

---

## 📁 Project Structure

```
├── data_and_model/          # Data & model artifacts
│   ├── features/            # Feature-engineered outputs
│   └── models/              # Trained .pkl files
├── src/
│   ├── data_pipeline/       # Data processing pipeline
│   ├── models/              # Model training and prediction
│   ├── serving/             # FastAPI endpoints
│   └── monitoring/          # Drift detection
├── tests/                   # Unit & integration tests
├── app.py                   # Hugging Face Spaces entrypoint
├── streamlit_app.py         # Dashboard UI
├── params.yaml              # Configuration
└── requirements.txt         # Dependencies
```

---

## 🚀 Quick Start (Local)

### 1. Clone & Setup
```bash
git clone https://github.com/hammadAsher100/Bank-Marketing-Customer-Subscription-Prediction-MLOps.git
cd Bank-Marketing-Customer-Subscription-Prediction-MLOps
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python app.py
# Opens on http://localhost:7860
```

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone https://github.com/hammadAsher100/Bank-Marketing-Customer-Subscription-Prediction-MLOps.git
cd Bank-Marketing-Customer-Subscription-Prediction-MLOps

# Start both services
docker-compose up -d

# Access the application
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

### Docker Hub Images

Pre-built Docker images are available:

**Backend API:**
- **Image:** `hammadasher/mlops-saylani-api:latest`
- **Docker Hub:** [hammadasher/mlops-saylani-api](https://hub.docker.com/r/hammadasher/mlops-saylani-api)

```bash
docker pull hammadasher/mlops-saylani-api:latest
docker run -p 8000:8000 hammadasher/mlops-saylani-api:latest
```

**Frontend Dashboard:**
- **Image:** `hammadasher/mlops-saylani-frontend:latest`
- **Docker Hub:** [hammadasher/mlops-saylani-frontend](https://hub.docker.com/r/hammadasher/mlops-saylani-frontend)

```bash
docker pull hammadasher/mlops-saylani-frontend:latest
docker run -p 8501:8501 -e API_URL=http://localhost:8000 hammadasher/mlops-saylani-frontend:latest
```

---

## 🤗 Hugging Face Spaces Deployment

**🌟 Live Application:** [https://huggingface.co/spaces/Unknown213141/BankPrediction](https://huggingface.co/spaces/Unknown213141/BankPrediction)

This project is deployed on Hugging Face Spaces using the native Streamlit SDK (no Docker required). The deployment automatically:
- Builds on every `git push`
- Installs dependencies from `requirements.txt`
- Loads pre-trained ML models
- Starts FastAPI backend and Streamlit frontend
- Provides HTTPS access with automatic scaling

### Features Available on Live Demo:
- ✅ **Real-time Predictions** - Input customer data and get instant predictions
- ✅ **Multiple Models** - Choose between LightGBM and XGBoost
- ✅ **MLflow Metrics** - View training experiment results and model performance
- ✅ **Batch Predictions** - Upload CSV files for bulk predictions
- ✅ **Interactive Dashboard** - Beautiful, responsive UI with dark theme

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

## 📊 Model Performance

- **LightGBM & XGBoost** models with hyperparameter optimization
- **Quality Gate**: F1 > 0.60, AUC > 0.75
- **Balanced Classes**: SMOTE for handling imbalanced data
- **Experiment Tracking**: MLflow for version control

---

## 🛠️ Tech Stack

- **ML**: scikit-learn, LightGBM, XGBoost, imbalanced-learn
- **Web**: FastAPI, Streamlit, Uvicorn
- **Tracking**: MLflow
- **Data**: Pandas, NumPy
- **Viz**: Plotly

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👥 Author

Hammad Asher - [GitHub](https://github.com/hammadAsher100)