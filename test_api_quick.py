import requests

# Test health endpoint
print("Testing health endpoint...")
response = requests.get("http://localhost:8000/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test prediction with LightGBM
print("Testing prediction with LightGBM...")
payload = {
    "age": 35,
    "job": "management",
    "marital": "married",
    "education": "tertiary",
    "default": "no",
    "balance": 1500,
    "housing": "yes",
    "loan": "no",
    "contact": "cellular",
    "day": 15,
    "month": "may",
    "duration": 300,
    "campaign": 2,
    "pdays": -1,
    "previous": 0,
    "poutcome": "unknown",
    "model_type": "lgbm"
}

response = requests.post("http://localhost:8000/predict", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test prediction with XGBoost
print("Testing prediction with XGBoost...")
payload["model_type"] = "xgb"
response = requests.post("http://localhost:8000/predict", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
