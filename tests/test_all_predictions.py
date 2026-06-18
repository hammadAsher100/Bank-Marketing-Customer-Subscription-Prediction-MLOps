"""
test_all_predictions.py
Comprehensive test of all prediction endpoints with sample data.
Tests: /health, /predict (lgbm, xgb), /batch, /mlflow-metrics
"""
import requests
import json
import sys
import time
import os

# Fix Windows console encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

API_URL = "http://localhost:8000"

# -- Sample customer data ---------------------------------------------------
SAMPLE_CUSTOMERS = [
    {
        "name": "Management professional, married, high balance",
        "data": {
            "age": 35, "job": "management", "marital": "married",
            "education": "tertiary", "default": "no", "balance": 1500,
            "housing": "yes", "loan": "no", "contact": "cellular",
            "day": 15, "month": "may", "duration": 300,
            "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
        }
    },
    {
        "name": "Blue-collar worker, divorced, low balance",
        "data": {
            "age": 52, "job": "blue-collar", "marital": "divorced",
            "education": "secondary", "default": "no", "balance": 200,
            "housing": "no", "loan": "yes", "contact": "telephone",
            "day": 8, "month": "nov", "duration": 120,
            "campaign": 5, "pdays": -1, "previous": 0, "poutcome": "unknown",
        }
    },
    {
        "name": "Retired, single, very high balance, prev success",
        "data": {
            "age": 67, "job": "retired", "marital": "single",
            "education": "primary", "default": "no", "balance": 5000,
            "housing": "no", "loan": "no", "contact": "cellular",
            "day": 20, "month": "mar", "duration": 600,
            "campaign": 1, "pdays": 100, "previous": 3, "poutcome": "success",
        }
    },
    {
        "name": "Student, single, zero balance, short call",
        "data": {
            "age": 20, "job": "student", "marital": "single",
            "education": "secondary", "default": "no", "balance": 0,
            "housing": "no", "loan": "no", "contact": "unknown",
            "day": 1, "month": "jan", "duration": 30,
            "campaign": 10, "pdays": -1, "previous": 0, "poutcome": "failure",
        }
    },
    {
        "name": "Entrepreneur, married, negative balance, in default",
        "data": {
            "age": 45, "job": "entrepreneur", "marital": "married",
            "education": "unknown", "default": "yes", "balance": -500,
            "housing": "yes", "loan": "yes", "contact": "telephone",
            "day": 28, "month": "sep", "duration": 80,
            "campaign": 3, "pdays": 300, "previous": 2, "poutcome": "other",
        }
    },
]

PASS = 0
FAIL = 0


def log_pass(test_name, detail=""):
    global PASS
    PASS += 1
    msg = f"  [PASS] {test_name}"
    if detail:
        msg += f"  ({detail})"
    print(msg)


def log_fail(test_name, detail=""):
    global FAIL
    FAIL += 1
    msg = f"  [FAIL] {test_name}"
    if detail:
        msg += f"  ({detail})"
    print(msg)


def validate_prediction_response(result, model_name):
    """Validate a single prediction response has all required fields."""
    required = ["prediction", "probability", "model_used", "threshold_used", "label"]
    for key in required:
        if key not in result:
            return False, f"Missing key: {key}"
    if result["prediction"] not in (0, 1):
        return False, f"Invalid prediction value: {result['prediction']}"
    if not (0.0 <= result["probability"] <= 1.0):
        return False, f"Probability out of range: {result['probability']}"
    if result["model_used"] != model_name:
        return False, f"Expected model '{model_name}', got '{result['model_used']}'"
    if not isinstance(result["threshold_used"], (int, float)):
        return False, f"Invalid threshold: {result['threshold_used']}"
    return True, ""


# ===========================================================================
# TEST 1: Health Check
# ===========================================================================
def test_health():
    print("\n=== TEST 1: Health Check ===")
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log_pass("Health endpoint returns 200")
            for key in ["lgbm_loaded", "xgb_loaded", "mlflow_db"]:
                if data.get(key):
                    log_pass(f"  {key} = True")
                else:
                    log_fail(f"  {key} = False (not available)")
        else:
            log_fail("Health endpoint", f"status={r.status_code}")
    except Exception as e:
        log_fail("Health endpoint", str(e))


# ===========================================================================
# TEST 2: LightGBM Predictions
# ===========================================================================
def test_lgbm_predictions():
    print("\n=== TEST 2: LightGBM Predictions ===")
    for sample in SAMPLE_CUSTOMERS:
        payload = {**sample["data"], "model_type": "lgbm", "threshold": None}
        try:
            r = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()
                ok, err = validate_prediction_response(result, "lgbm")
                if ok:
                    label = "Yes" if result["prediction"] == 1 else "No"
                    log_pass(
                        f"LGBM: {sample['name']}",
                        f"pred={label}, prob={result['probability']:.4f}, threshold={result['threshold_used']}"
                    )
                else:
                    log_fail(f"LGBM: {sample['name']}", err)
            else:
                log_fail(f"LGBM: {sample['name']}", f"status={r.status_code}, {r.text}")
        except Exception as e:
            log_fail(f"LGBM: {sample['name']}", str(e))


# ===========================================================================
# TEST 3: XGBoost Predictions
# ===========================================================================
def test_xgb_predictions():
    print("\n=== TEST 3: XGBoost Predictions ===")
    for sample in SAMPLE_CUSTOMERS:
        payload = {**sample["data"], "model_type": "xgb", "threshold": None}
        try:
            r = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()
                ok, err = validate_prediction_response(result, "xgb")
                if ok:
                    label = "Yes" if result["prediction"] == 1 else "No"
                    log_pass(
                        f"XGB: {sample['name']}",
                        f"pred={label}, prob={result['probability']:.4f}, threshold={result['threshold_used']}"
                    )
                else:
                    log_fail(f"XGB: {sample['name']}", err)
            else:
                log_fail(f"XGB: {sample['name']}", f"status={r.status_code}, {r.text}")
        except Exception as e:
            log_fail(f"XGB: {sample['name']}", str(e))

# ===========================================================================
# TEST 4: Custom Threshold
# ===========================================================================
def test_custom_threshold():
    print("\n=== TEST 5: Custom Threshold ===")
    sample = SAMPLE_CUSTOMERS[0]["data"]

    for threshold in [0.3, 0.5, 0.7, 0.9]:
        payload = {**sample, "model_type": "lgbm", "threshold": threshold}
        try:
            r = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()
                if abs(result["threshold_used"] - threshold) < 0.001:
                    label = "Yes" if result["prediction"] == 1 else "No"
                    log_pass(
                        f"Threshold={threshold}",
                        f"pred={label}, prob={result['probability']:.4f}"
                    )
                else:
                    log_fail(f"Threshold={threshold}", f"Expected threshold {threshold}, got {result['threshold_used']}")
            else:
                log_fail(f"Threshold={threshold}", f"status={r.status_code}")
        except Exception as e:
            log_fail(f"Threshold={threshold}", str(e))


# ===========================================================================
# TEST 5: Batch Predictions
# ===========================================================================
def test_batch_predictions():
    print("\n=== TEST 5: Batch Predictions ===")
    records = []
    for s in SAMPLE_CUSTOMERS:
        rec = {**s["data"], "model_type": "lgbm", "threshold": None}
        records.append(rec)

    for model in ["lgbm", "xgb"]:
        payload = {"records": records, "model_type": model, "threshold": 0.5}
        try:
            r = requests.post(f"{API_URL}/batch", json=payload, timeout=60)
            if r.status_code == 200:
                result = r.json()
                if result["total_records"] == len(SAMPLE_CUSTOMERS):
                    log_pass(
                        f"Batch {model.upper()}",
                        f"total={result['total_records']}, subs={result['subscribers']}, non_subs={result['non_subscribers']}"
                    )
                    # Validate each individual result
                    all_ok = True
                    for i, pred in enumerate(result["results"]):
                        ok, err = validate_prediction_response(pred, model)
                        if not ok:
                            log_fail(f"Batch {model.upper()} record #{i+1}", err)
                            all_ok = False
                    if all_ok:
                        log_pass(f"Batch {model.upper()}: all individual results valid")
                else:
                    log_fail(f"Batch {model.upper()}", f"Expected {len(SAMPLE_CUSTOMERS)} records, got {result['total_records']}")
            else:
                log_fail(f"Batch {model.upper()}", f"status={r.status_code}, {r.text}")
        except Exception as e:
            log_fail(f"Batch {model.upper()}", str(e))


# ===========================================================================
# TEST 6: MLflow Metrics
# ===========================================================================
def test_mlflow_metrics():
    print("\n=== TEST 6: MLflow Metrics ===")
    try:
        r = requests.get(f"{API_URL}/mlflow-metrics", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "error" in data:
                log_fail("MLflow metrics", data["error"])
            elif "experiment" in data and "runs" in data:
                log_pass("MLflow metrics endpoint", f"experiment='{data['experiment']}', runs={len(data['runs'])}")
            else:
                log_fail("MLflow metrics", "Unexpected response format")
        else:
            log_fail("MLflow metrics", f"status={r.status_code}")
    except Exception as e:
        log_fail("MLflow metrics", str(e))


# ===========================================================================
# TEST 7: Edge Cases & Validation
# ===========================================================================
def test_edge_cases():
    print("\n=== TEST 7: Edge Cases & Validation ===")

    # Test with invalid age (should fail validation)
    bad_payload = {
        "age": 10, "job": "student", "marital": "single",
        "education": "primary", "default": "no", "balance": 0,
        "housing": "no", "loan": "no", "contact": "cellular",
        "day": 15, "month": "may", "duration": 300,
        "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
        "model_type": "lgbm", "threshold": None,
    }
    try:
        r = requests.post(f"{API_URL}/predict", json=bad_payload, timeout=10)
        if r.status_code == 422:
            log_pass("Validation: age < 18 rejected (422)")
        else:
            log_fail("Validation: age < 18", f"Expected 422, got {r.status_code}")
    except Exception as e:
        log_fail("Validation: age < 18", str(e))

    # Test with duration = 0 (should fail)
    bad_payload2 = {
        "age": 35, "job": "management", "marital": "married",
        "education": "tertiary", "default": "no", "balance": 1500,
        "housing": "yes", "loan": "no", "contact": "cellular",
        "day": 15, "month": "may", "duration": 0,
        "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
        "model_type": "lgbm", "threshold": None,
    }
    try:
        r = requests.post(f"{API_URL}/predict", json=bad_payload2, timeout=10)
        if r.status_code == 422:
            log_pass("Validation: duration=0 rejected (422)")
        else:
            log_fail("Validation: duration=0", f"Expected 422, got {r.status_code}")
    except Exception as e:
        log_fail("Validation: duration=0", str(e))

    # Test with invalid job value
    bad_payload3 = {
        "age": 35, "job": "invalid_job", "marital": "married",
        "education": "tertiary", "default": "no", "balance": 1500,
        "housing": "yes", "loan": "no", "contact": "cellular",
        "day": 15, "month": "may", "duration": 300,
        "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
        "model_type": "lgbm", "threshold": None,
    }
    try:
        r = requests.post(f"{API_URL}/predict", json=bad_payload3, timeout=10)
        if r.status_code == 422:
            log_pass("Validation: invalid job rejected (422)")
        else:
            log_fail("Validation: invalid job", f"Expected 422, got {r.status_code}")
    except Exception as e:
        log_fail("Validation: invalid job", str(e))

    # Test empty batch
    try:
        r = requests.post(f"{API_URL}/batch", json={"records": [], "model_type": "lgbm"}, timeout=10)
        if r.status_code == 400:
            log_pass("Validation: empty batch rejected (400)")
        else:
            log_fail("Validation: empty batch", f"Expected 400, got {r.status_code}")
    except Exception as e:
        log_fail("Validation: empty batch", str(e))


# ===========================================================================
# MAIN
# ===========================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  BANK MARKETING PREDICTION - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    test_health()
    test_lgbm_predictions()
    test_xgb_predictions()
    test_custom_threshold()
    test_batch_predictions()
    test_mlflow_metrics()
    test_edge_cases()

    print("\n" + "=" * 60)
    print(f"  RESULTS:  {PASS} passed  |  {FAIL} failed")
    print("=" * 60)

    sys.exit(1 if FAIL > 0 else 0)
