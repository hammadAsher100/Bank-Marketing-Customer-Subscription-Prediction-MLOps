import sys
from pathlib import Path
from src.models.predict import predict

test_data = {
    "age": 30,
    "job": "student",
    "marital": "single",
    "education": "tertiary",
    "default": "no",
    "balance": 0,
    "housing": "no",
    "loan": "no",
    "contact": "cellular",
    "day": 1,
    "month": "may",
    "duration": 50,
    "campaign": 1,
    "pdays": -1,
    "previous": 0,
    "poutcome": "unknown"
}

print("Testing PySpark...")
try:
    res1 = predict(test_data, "pyspark", threshold=0.5)
    print("PySpark prob:", res1["probability"])
except Exception as e:
    print("PySpark failed:", e)

print("\nTesting LightGBM...")
try:
    res2 = predict(test_data, "lgbm", threshold=0.5)
    print("LightGBM prob:", res2["probability"])
except Exception as e:
    print("LightGBM failed:", e)

print("\nTesting XGBoost...")
try:
    res3 = predict(test_data, "xgb", threshold=0.5)
    print("XGBoost prob:", res3["probability"])
except Exception as e:
    print("XGBoost failed:", e)
