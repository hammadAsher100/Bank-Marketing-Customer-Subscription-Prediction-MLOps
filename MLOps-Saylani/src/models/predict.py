
import pandas as pd
import numpy as np
import joblib
import yaml
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ============================================================
# LOAD CONFIG
# ============================================================
# PARAMS = yaml.safe_load(open("params.yaml"))
ROOT = Path(__file__).resolve().parents[2]

PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)
MODEL_DIR = Path(PARAMS["model"]["output_dir"])
PROC_DIR  = Path(PARAMS["data"]["processed_dir"])


# ============================================================
# LOAD MODEL
# ============================================================
def load_model(model_name="lgbm", use_calibrated=True):

    suffix = "_calibrated" if use_calibrated else "_model"

    # Example:
    # lgbm_calibrated.pkl
    # xgb_model.pkl
    model_path = MODEL_DIR / f"{model_name}{suffix}.pkl"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = joblib.load(model_path)

    print(f"[predict] Loaded model → {model_path}")

    return model


# ============================================================
# BATCH PREDICTION ON TEST SET
# ============================================================
def predict(model_name="lgbm", use_calibrated=True, threshold=0.5):

    print("\n" + "=" * 60)
    print("RUNNING BATCH PREDICTION")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------
    model = load_model(model_name, use_calibrated)

    # --------------------------------------------------------
    # LOAD TEST DATA
    # --------------------------------------------------------
    X_test = pd.read_csv(PROC_DIR / "X_test.csv")
    y_test = pd.read_csv(PROC_DIR / "y_test.csv").squeeze()

    print(f"[predict] X_test shape → {X_test.shape}")

    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------
    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= threshold).astype(int)

    # --------------------------------------------------------
    # RESULTS DATAFRAME
    # --------------------------------------------------------
    results = X_test.copy()

    results["actual"] = y_test.values
    results["predicted"] = preds
    results["prob_yes"] = probs.round(4)
    results["prob_no"] = (1 - probs).round(4)
    results["correct"] = (
        results["actual"] == results["predicted"]
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------
    accuracy = accuracy_score(y_test, preds)

    print("\n[predict] Prediction Summary")
    print("-" * 40)
    print(f"Total Samples   : {len(results)}")
    print(f"Predicted YES   : {preds.sum()}")
    print(f"Predicted NO    : {(preds == 0).sum()}")
    print(f"Accuracy        : {accuracy:.4f}")

    print("\n[predict] Classification Report")
    print("-" * 40)
    print(classification_report(y_test, preds))

    print("\n[predict] Confusion Matrix")
    print("-" * 40)
    print(confusion_matrix(y_test, preds))

    # --------------------------------------------------------
    # SAMPLE OUTPUT
    # --------------------------------------------------------
    print("\n[predict] Sample Predictions")
    print("-" * 40)

    cols = [
        "actual",
        "predicted",
        "prob_yes",
        "correct"
    ]

    print(results[cols].head(10).to_string())

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------
    output_path = MODEL_DIR / f"{model_name}_predictions.csv"

    results.to_csv(output_path, index=False)

    print(f"\n[predict] Predictions saved → {output_path}")

    return results


# ============================================================
# PREPARE SINGLE INPUT
# ============================================================
def prepare_single_input(sample: dict):

    # Load training columns
    X_train = pd.read_csv(PROC_DIR / "X_train_balanced.csv")

    expected_columns = X_train.columns.tolist()

    # Create empty row with all columns
    input_df = pd.DataFrame(columns=expected_columns)

    # Add one row
    input_df.loc[0] = 0

    # Fill available features
    for key, value in sample.items():

        if key in input_df.columns:
            input_df.at[0, key] = value

    return input_df


# ============================================================
# SINGLE CUSTOMER PREDICTION
# ============================================================
def predict_single(sample: dict,
                   model_name="lgbm",
                   use_calibrated=True,
                   threshold=0.5):

    print("\n" + "=" * 60)
    print("SINGLE CUSTOMER PREDICTION")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------
    model = load_model(model_name, use_calibrated)

    # --------------------------------------------------------
    # PREPARE INPUT
    # --------------------------------------------------------
    df = prepare_single_input(sample)

    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------
    prob_yes = model.predict_proba(df)[0][1]

    prediction = 1 if prob_yes >= threshold else 0

    label = "YES ✅" if prediction == 1 else "NO ❌"

    print(f"Probability of Subscription : {prob_yes:.4f}")
    print(f"Prediction                  : {label}")

    return {
        "probability": round(prob_yes, 4),
        "prediction": prediction,
        "label": label
    }


# ============================================================
# LIVE PREDICTION SYSTEM
# ============================================================
def live_prediction(model_name="lgbm", use_calibrated=True):

    print("\n" + "=" * 60)
    print("LIVE CUSTOMER PREDICTION SYSTEM")
    print("=" * 60)

    while True:

        try:
            print("\nEnter customer information")
            print("Type 'exit' anytime to quit")

            age = input("Age: ")
            if age.lower() == "exit":
                break

            balance = input("Balance: ")
            duration = input("Call Duration: ")
            campaign = input("Campaign Contacts: ")
            previous = input("Previous Contacts: ")

            sample = {
                "age": int(age),
                "balance": float(balance),
                "duration": float(duration),
                "campaign": int(campaign),
                "previous": int(previous),
                "contacted_before": 1 if int(previous) > 0 else 0,
                "is_long_call": 1 if float(duration) > 300 else 0,
                "pdays_clipped": 0,
                "call_intensity": float(duration) / max(int(campaign), 1),
                "prev_success": 1 if int(previous) > 0 else 0,
            }

            result = predict_single(
                sample,
                model_name=model_name,
                use_calibrated=use_calibrated
            )

            print("\nFINAL RESULT")
            print("-" * 40)
            print(f"Prediction  : {result['label']}")
            print(f"Probability : {result['probability']}")

        except Exception as e:
            print(f"\n[predict] Error → {e}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":

    # --------------------------------------------------------
    # BATCH PREDICTION
    # --------------------------------------------------------
    predict(
        model_name="lgbm",
        use_calibrated=True,
        threshold=0.5
    )

    # --------------------------------------------------------
    # SINGLE CUSTOMER DEMO
    # --------------------------------------------------------
    sample_customer = {
        "age": 35,
        "balance": 1500,
        "duration": 300,
        "campaign": 2,
        "previous": 0,
        "contacted_before": 0,
        "is_long_call": 1,
        "pdays_clipped": 0,
        "call_intensity": 150,
        "prev_success": 0,
    }

    predict_single(
        sample_customer,
        model_name="lgbm",
        use_calibrated=True
    )

    # --------------------------------------------------------
    # LIVE PREDICTION MODE
    # --------------------------------------------------------
    live_prediction(
        model_name="lgbm",
        use_calibrated=True
    )


