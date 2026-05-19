

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import mlflow
import mlflow.sklearn
import optuna
from optuna.samplers import TPESampler
import lightgbm as lgb
import xgboost as xgb
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score,
    recall_score, classification_report, confusion_matrix
)
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# ── Config ────────────────────────────────────────────────────────────────────
# PARAMS      = yaml.safe_load(open("params.yaml"))
ROOT = Path(__file__).resolve().parents[2]
PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)

print("\n========== PARAMS ==========")
print(PARAMS)
print("\n========== KEYS ==========")
print(PARAMS.keys())
print("\n========== MODEL ==========")
print(PARAMS.get("model"))
PROC_DIR    = Path(PARAMS["data"]["processed_dir"])
MODEL_DIR   = Path(PARAMS["model"]["output_dir"])
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE    = PARAMS["base"]["random_state"]
N_TRIALS        = PARAMS["model"]["n_trials"]
EXPERIMENT_NAME = PARAMS["model"]["experiment_name"]

# ── Load Data ─────────────────────────────────────────────────────────────────
def load_data():
    X_train = pd.read_csv(PROC_DIR / "X_train_balanced.csv")
    y_train = pd.read_csv(PROC_DIR / "y_train_balanced.csv").squeeze()
    X_test  = pd.read_csv(PROC_DIR / "X_test.csv")
    y_test  = pd.read_csv(PROC_DIR / "y_test.csv").squeeze()

    print(f"[train] X_train: {X_train.shape}  X_test: {X_test.shape}")
    print(f"[train] y_train dist:\n{y_train.value_counts()}")
    return X_train, y_train, X_test, y_test


# ── Metrics helper ────────────────────────────────────────────────────────────
def compute_metrics(model, X, y, prefix=""):
    preds  = model.predict(X)
    probs  = model.predict_proba(X)[:, 1]
    return {
        f"{prefix}roc_auc":   round(roc_auc_score(y, probs), 4),
        f"{prefix}f1":        round(f1_score(y, preds), 4),
        f"{prefix}precision": round(precision_score(y, preds), 4),
        f"{prefix}recall":    round(recall_score(y, preds), 4),
    }



# ═══════════════════════════════════════════════════════════════════════════════
# LIGHTGBM  +  OPTUNA
# ═══════════════════════════════════════════════════════════════════════════════
def optimize_lgbm(X_train, y_train, X_test, y_test):
    """
    Optuna searches for best LightGBM hyperparameters.
    Each trial trains a model and returns validation AUC.
    Optuna uses TPE (Tree-structured Parzen Estimator) to
    intelligently explore the hyperparameter space.
    """
    def objective(trial):
        params = {
            "objective":        "binary",
            "metric":           "auc",
            "verbosity":        -1,
            "boosting_type":    "gbdt",
            "random_state":     RANDOM_STATE,
            # ── Hyperparameters Optuna tunes ──────────────────────────────
            "n_estimators":     trial.suggest_int("n_estimators", 200, 1000),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "num_leaves":       trial.suggest_int("num_leaves", 20, 300),
            "max_depth":        trial.suggest_int("max_depth", 3, 12),
            "min_child_samples":trial.suggest_int("min_child_samples", 5, 100),
            "subsample":        trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha":        trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda":       trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        }
        model = lgb.LGBMClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[lgb.early_stopping(50, verbose=False),
                       lgb.log_evaluation(-1)]
        )
        probs = model.predict_proba(X_test)[:, 1]
        return roc_auc_score(y_test, probs)

    # TPE sampler = smarter than random search
    sampler = TPESampler(seed=RANDOM_STATE)
    study   = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)

    print(f"\n[lgbm] Best AUC: {study.best_value:.4f}")
    print(f"[lgbm] Best params: {study.best_params}")
    return study.best_params


def train_lgbm(X_train, y_train, X_test, y_test):
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name="LightGBM-Optuna"):
        print("\n[lgbm] Starting Optuna search...")
        best_params = optimize_lgbm(X_train, y_train, X_test, y_test)

        # Train final model with best params
        final_params = {
            "objective":    "binary",
            "random_state": RANDOM_STATE,
            "verbosity":    -1,
            **best_params
        }
        model = lgb.LGBMClassifier(**final_params)
        model.fit(X_train, y_train)

        # Metrics
        train_metrics = compute_metrics(model, X_train, y_train, "train_")
        test_metrics  = compute_metrics(model, X_test,  y_test,  "test_")
        all_metrics   = {**train_metrics, **test_metrics}

        # Log to MLflow
        mlflow.log_params(best_params)
        mlflow.log_metrics(all_metrics)
        mlflow.sklearn.log_model(model, "lightgbm_model")

        print(f"\n[lgbm] Train metrics: {train_metrics}")
        print(f"[lgbm] Test  metrics: {test_metrics}")

        # Save model locally
        joblib.dump(model, MODEL_DIR / "lgbm_model.pkl")
        print(f"[lgbm] Model saved to {MODEL_DIR / 'lgbm_model.pkl'}")

        # Confusion matrix
        _plot_confusion_matrix(model, X_test, y_test, "LightGBM")

        return model, all_metrics


# ═══════════════════════════════════════════════════════════════════════════════
# XGBOOST  +  OPTUNA
# ═══════════════════════════════════════════════════════════════════════════════
def optimize_xgb(X_train, y_train, X_test, y_test):
    def objective(trial):
        params = {
            "objective":        "binary:logistic",
            "eval_metric":      "auc",
            "use_label_encoder": False,
            "random_state":     RANDOM_STATE,
            "n_estimators":     trial.suggest_int("n_estimators", 200, 1000),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "max_depth":        trial.suggest_int("max_depth", 3, 10),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "subsample":        trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "gamma":            trial.suggest_float("gamma", 0, 5),
            "reg_alpha":        trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda":       trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        }
        model = xgb.XGBClassifier(**params, early_stopping_rounds=50, verbosity=0)
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        probs = model.predict_proba(X_test)[:, 1]
        return roc_auc_score(y_test, probs)

    sampler = TPESampler(seed=RANDOM_STATE)
    study   = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)

    print(f"\n[xgb] Best AUC: {study.best_value:.4f}")
    print(f"[xgb] Best params: {study.best_params}")
    return study.best_params


def train_xgb(X_train, y_train, X_test, y_test):
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name="XGBoost-Optuna"):
        print("\n[xgb] Starting Optuna search...")
        best_params = optimize_xgb(X_train, y_train, X_test, y_test)

        final_params = {
            "objective":        "binary:logistic",
            "use_label_encoder": False,
            "random_state":     RANDOM_STATE,
            "verbosity":        0,
            **best_params
        }
        model = xgb.XGBClassifier(**final_params)
        model.fit(X_train, y_train)

        train_metrics = compute_metrics(model, X_train, y_train, "train_")
        test_metrics  = compute_metrics(model, X_test,  y_test,  "test_")
        all_metrics   = {**train_metrics, **test_metrics}

        mlflow.log_params(best_params)
        mlflow.log_metrics(all_metrics)
        mlflow.sklearn.log_model(model, "xgboost_model")

        print(f"\n[xgb] Train metrics: {train_metrics}")
        print(f"[xgb] Test  metrics: {test_metrics}")

        joblib.dump(model, MODEL_DIR / "xgb_model.pkl")
        print(f"[xgb] Model saved to {MODEL_DIR / 'xgb_model.pkl'}")

        _plot_confusion_matrix(model, X_test, y_test, "XGBoost")

        return model, all_metrics


# ── Confusion matrix plot ──────────────────────────────────────────────────────
def _plot_confusion_matrix(model, X_test, y_test, name):
    preds = model.predict(X_test)
    cm    = confusion_matrix(y_test, preds)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["No", "Yes"],
                yticklabels=["No", "Yes"])
    plt.title(f"{name} — Confusion Matrix")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    path = MODEL_DIR / f"{name.lower()}_confusion_matrix.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    mlflow.log_artifact(str(path))
    print(f"[train] Confusion matrix saved to {path}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    X_train, y_train, X_test, y_test = load_data()

    lgbm_model, lgbm_metrics = train_lgbm(X_train, y_train, X_test, y_test)
    xgb_model,  xgb_metrics  = train_xgb(X_train,  y_train, X_test, y_test)

    # Compare
    print("\n" + "="*50)
    print("MODEL COMPARISON")
    print("="*50)
    print(f"LightGBM  AUC: {lgbm_metrics['test_roc_auc']}  F1: {lgbm_metrics['test_f1']}")
    print(f"XGBoost   AUC: {xgb_metrics['test_roc_auc']}   F1: {xgb_metrics['test_f1']}")
    
# joblib.dump(
#     X_train.columns.tolist(),
#     MODEL_DIR / "feature_columns.pkl"
# )    