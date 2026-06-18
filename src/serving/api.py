import sys
from pathlib import Path

# Project root ko Python path mein add karo
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import yaml
import mlflow
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.serving.schema import (
    PredictRequest, PredictResponse,
    BatchPredictRequest, BatchPredictResponse,
    HealthResponse,
)
from src.models.predict import predict, load_sklearn_model, MODEL_DIR

# ── Config ────────────────────────────────────────────────────────────────────
PARAMS = yaml.safe_load(open(ROOT / "params.yaml"))
PORT   = PARAMS.get("serving", {}).get("port", 8000)

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Bank Marketing Prediction API",
    description="""
## 🏦 Bank Marketing MLOps — Prediction API

Yeh API predict karta hai ke koi bank customer **term deposit subscribe karega ya nahi**.

### Models Available:
- **lgbm** → LightGBM + Optuna tuned
- **xgb**  → XGBoost + Optuna tuned  

### How to use:
1. `/health` check karo — models loaded hain ya nahi
2. `/predict` mein customer ka data bhejo
3. Response mein prediction milegi!
    """,
    version="1.0.0",
)

# CORS middleware — Streamlit frontend ko allow karta hai API call karne
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Production mein specific URL daalna
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP EVENT — models preload karo
# ═══════════════════════════════════════════════════════════════════════════════
@app.on_event("startup")
async def startup_event():
    """
    Server start hone par dono models preload karo.
    Isse pehli request slow nahi hogi.
    """
    print("[API] Preloading models...")
    try:
        load_sklearn_model("lgbm")
        print("[API] OK LightGBM model loaded")
    except FileNotFoundError as e:
        print(f"[API] WARN LightGBM not found: {e}")

    try:
        load_sklearn_model("xgb")
        print("[API] OK XGBoost model loaded")
    except FileNotFoundError as e:
        print(f"[API] WARN XGBoost not found: {e}")

    print(f"[API] Server ready at http://localhost:{PORT}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["General"])
def root():
    """Welcome endpoint."""
    return {
        "message": "Bank Marketing Prediction API",
        "docs":    f"http://localhost:{PORT}/docs",
        "health":  f"http://localhost:{PORT}/health",
    }


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """
    Check karo ke kaunse models available hain.
    Streamlit yeh endpoint use karta hai status dikhane ke liye.
    """
    lgbm_ok  = (MODEL_DIR / "lgbm_model.pkl").exists()
    xgb_ok   = (MODEL_DIR / "xgb_model.pkl").exists()
    mlflow_ok = (ROOT / "mlflow.db").exists()

    return HealthResponse(
        status="ok",
        lgbm_loaded=lgbm_ok,
        xgb_loaded=xgb_ok,
        mlflow_db=mlflow_ok,
    )


# ── Single Prediction ─────────────────────────────────────────────────────────
@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
def predict_endpoint(request: PredictRequest):
    """
    ## Single Customer Prediction

    Customer ka data bhejo, model predict karega ke woh subscribe karega ya nahi.

    **model_type choices:**
    - `lgbm`    → LightGBM (fastest, recommended)
    - `xgb`     → XGBoost

    **threshold:** Optional — default params.yaml se aata hai (0.5)
    """
    try:
        # Pydantic model ko dict mein convert karo
        # model_type aur threshold ko alag rakhna hai
        data = request.model_dump()
        model_type = data.pop("model_type")
        threshold  = data.pop("threshold")

        result = predict(
            input_data=data,
            model_type=model_type,
            threshold=threshold,
        )
        return PredictResponse(**result)

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# ── Batch Prediction ──────────────────────────────────────────────────────────
@app.post("/batch", response_model=BatchPredictResponse, tags=["Prediction"])
def batch_predict_endpoint(request: BatchPredictRequest):
    """
    ## Batch Predictions

    Multiple customers ka data ek saath bhejo.

    Returns predictions + summary stats.
    """
    if not request.records:
        raise HTTPException(status_code=400, detail="records list cannot be empty")

    results = []
    for rec in request.records:
        try:
            data = rec.model_dump()
            data.pop("model_type", None)
            data.pop("threshold", None)

            result = predict(
                input_data=data,
                model_type=request.model_type,
                threshold=request.threshold,
            )
            results.append(PredictResponse(**result))
        except Exception as e:
            # Individual record fail hone par skip karo, baqi process karo
            results.append(PredictResponse(
                prediction=0, probability=0.0,
                model_used=request.model_type,
                threshold_used=request.threshold or 0.5,
                label=f"Error: {str(e)}"
            ))

    subscribers     = sum(1 for r in results if r.prediction == 1)
    non_subscribers = len(results) - subscribers

    return BatchPredictResponse(
        results=results,
        total_records=len(results),
        subscribers=subscribers,
        non_subscribers=non_subscribers,
    )


# ── MLflow Metrics ────────────────────────────────────────────────────────────
@app.get("/mlflow-metrics", tags=["Monitoring"])
def get_mlflow_metrics():
    """
    MLflow se latest experiment runs ki metrics fetch karta hai.
    Streamlit dashboard mein yeh metrics dikhaye jaate hain.
    """
    try:
        mlflow_db = ROOT / "mlflow.db"
        tracking_uri = f"sqlite:///{mlflow_db}" if mlflow_db.exists() else "mlruns"
        mlflow.set_tracking_uri(tracking_uri)

        experiment_name = PARAMS["model"].get("experiment_name", "bank_marketing_experiment")
        experiment = mlflow.get_experiment_by_name(experiment_name)

        if experiment is None:
            return {"error": f"Experiment '{experiment_name}' not found. Run train.py first."}

        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=10,
        )

        if runs.empty:
            return {"error": "No runs found in MLflow experiment."}

        metrics_list = []
        for _, row in runs.iterrows():
            metrics_list.append({
                "run_id":      row.get("run_id", ""),
                "run_name":    row.get("tags.mlflow.runName", ""),
                "status":      row.get("status", ""),
                "start_time":  str(row.get("start_time", "")),
                "test_auc":    row.get("metrics.test_roc_auc", None),
                "test_f1":     row.get("metrics.test_f1", None),
                "test_precision": row.get("metrics.test_precision", None),
                "test_recall": row.get("metrics.test_recall", None),
                "train_auc":   row.get("metrics.train_roc_auc", None),
            })

        return {"experiment": experiment_name, "runs": metrics_list}

    except Exception as e:
        return {"error": str(e)}


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.serving.api:app", host="0.0.0.0", port=PORT, reload=True)