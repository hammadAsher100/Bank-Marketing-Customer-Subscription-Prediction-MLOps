
from pathlib import Path
import pandas as pd
import numpy as np
import yaml
import joblib
import mlflow
import matplotlib.pyplot as plt
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import roc_auc_score, brier_score_loss

# PARAMS    = yaml.safe_load(open("params.yaml"))
ROOT = Path(__file__).resolve().parents[2]

PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)
PROC_DIR  = Path(PARAMS["data"]["processed_dir"])
MODEL_DIR = Path(PARAMS["model"]["output_dir"])


def load_data_and_model(model_name: str):
    X_test  = pd.read_csv(PROC_DIR / "X_test.csv")
    y_test  = pd.read_csv(PROC_DIR / "y_test.csv").squeeze()
    X_train = pd.read_csv(PROC_DIR / "X_train_balanced.csv")
    y_train = pd.read_csv(PROC_DIR / "y_train_balanced.csv").squeeze()
    model   = joblib.load(MODEL_DIR / f"{model_name}_model.pkl")
    return model, X_train, y_train, X_test, y_test


def calibrate_model(model, X_train, y_train, X_test, y_test, method="isotonic", name="model"):

    print(f"\n[calibrate] Calibrating {name} with method={method}")

    # CalibratedClassifierCV wraps your model and adjusts probabilities
    calibrated = CalibratedClassifierCV(model, method=method, cv=2)
    calibrated.fit(X_test, y_test)
    # Before vs After comparison
    raw_probs  = model.predict_proba(X_test)[:, 1]
    cal_probs  = calibrated.predict_proba(X_test)[:, 1]

    raw_brier  = brier_score_loss(y_test, raw_probs)
    cal_brier  = brier_score_loss(y_test, cal_probs)
    raw_auc    = roc_auc_score(y_test, raw_probs)
    cal_auc    = roc_auc_score(y_test, cal_probs)

    print(f"  Before calibration - AUC: {raw_auc:.4f}  Brier: {raw_brier:.4f}")
    print(f"  After calibration - AUC: {cal_auc:.4f}  Brier: {cal_brier:.4f}")
    print(f"  Brier score improvement: {raw_brier - cal_brier:.4f}  (lower is better)")

    # Plot calibration curve (reliability diagram)
    _plot_calibration_curve(y_test, raw_probs, cal_probs, name)

    # Save calibrated model
    save_path = MODEL_DIR / f"{name}_calibrated.pkl"
    joblib.dump(calibrated, save_path)
    print(f"[calibrate] Calibrated model saved to {save_path}")

    # Log to MLflow
    with mlflow.start_run(run_name=f"{name}-calibration"):
        mlflow.log_metrics({
            "raw_auc":   raw_auc,   "cal_auc":   cal_auc,
            "raw_brier": raw_brier, "cal_brier": cal_brier,
        })
        mlflow.log_artifact(str(MODEL_DIR / f"{name}_calibration_curve.png"))

    return calibrated


def _plot_calibration_curve(y_test, raw_probs, cal_probs, name):
    """
    Reliability diagram:
    - X axis: predicted probability
    - Y axis: actual fraction of positives
    - Perfect calibration = diagonal line
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    # Perfect calibration reference line
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")

    # Before calibration
    frac_pos_raw, mean_pred_raw = calibration_curve(y_test, raw_probs, n_bins=10)
    ax.plot(mean_pred_raw, frac_pos_raw, "s-", label="Before calibration", color="tomato")

    # After calibration
    frac_pos_cal, mean_pred_cal = calibration_curve(y_test, cal_probs, n_bins=10)
    ax.plot(mean_pred_cal, frac_pos_cal, "s-", label="After calibration", color="steelblue")

    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    ax.set_title(f"{name} — Calibration Curve (Reliability Diagram)")
    ax.legend()
    ax.grid(alpha=0.3)

    path = MODEL_DIR / f"{name}_calibration_curve.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"[calibrate] Calibration curve saved to {path}")


if __name__ == "__main__":
    for model_name in ["lgbm", "xgb"]:
        model, X_train, y_train, X_test, y_test = load_data_and_model(model_name)
        calibrate_model(model, X_train, y_train, X_test, y_test,
                        method="isotonic", name=model_name)