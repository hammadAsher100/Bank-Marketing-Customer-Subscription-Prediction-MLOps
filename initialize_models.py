"""
initialize_models.py
This script trains/initializes models for Render deployment
Runs during the build phase if models don't exist
"""
import sys
import os
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import yaml
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
import joblib

print("[Init] Starting model initialization...")

# Load params
PARAMS = yaml.safe_load(open(ROOT / "params.yaml"))
MODEL_DIR = Path(PARAMS["model"]["output_dir"])
PROCESSED_DIR = Path(PARAMS["data"]["processed_dir"])

# Ensure model directory exists
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Check if models already exist
lgbm_path = MODEL_DIR / "lgbm_model.pkl"
xgb_path = MODEL_DIR / "xgb_model.pkl"

if lgbm_path.exists() and xgb_path.exists():
    print("[Init] ✅ Models already exist. Skipping training.")
    sys.exit(0)

print("[Init] Looking for training data...")

# Try to load processed data
X_train = None
y_train = None
X_test = None
y_test = None

if (PROCESSED_DIR / "X_train_balanced.csv").exists():
    print("[Init] Found processed data. Loading...")
    try:
        X_train = pd.read_csv(PROCESSED_DIR / "X_train_balanced.csv")
        y_train = pd.read_csv(PROCESSED_DIR / "y_train_balanced.csv").values.ravel()
        X_test = pd.read_csv(PROCESSED_DIR / "X_test.csv")
        y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv").values.ravel()
        print(f"[Init] ✅ Loaded real data: X_train={X_train.shape}, X_test={X_test.shape}")
    except Exception as e:
        print(f"[Init] ⚠️  Error loading data: {e}")
        X_train = None

# If real data not available, create synthetic data
if X_train is None:
    print("[Init] Creating synthetic training data for model initialization...")
    # Create balanced synthetic dataset similar to bank marketing
    n_features = 20
    n_samples_train = 5000
    n_samples_test = 1000
    
    X_train, y_train = make_classification(
        n_samples=n_samples_train,
        n_features=n_features,
        n_informative=10,
        n_redundant=5,
        n_classes=2,
        weights=[0.8, 0.2],  # Imbalanced like real data
        random_state=42
    )
    
    X_test, y_test = make_classification(
        n_samples=n_samples_test,
        n_features=n_features,
        n_informative=10,
        n_redundant=5,
        n_classes=2,
        weights=[0.8, 0.2],
        random_state=43
    )
    
    # Convert to DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    X_train = pd.DataFrame(X_train, columns=feature_names)
    X_test = pd.DataFrame(X_test, columns=feature_names)
    print(f"[Init] ✅ Generated synthetic data: X_train={X_train.shape}, X_test={X_test.shape}")

print(f"[Init] Training data shape: {X_train.shape}, Test data shape: {X_test.shape}")

# ============================================================================
# Train LightGBM Model
# ============================================================================
if not lgbm_path.exists():
    print("[Init] Training LightGBM model...")
    try:
        lgbm_params = PARAMS["model"].get("lgbm_params", {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.05,
            "random_state": 42,
            "verbose": -1
        })
        
        lgbm_model = LGBMClassifier(**lgbm_params)
        lgbm_model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(lgbm_model, lgbm_path)
        print(f"[Init] ✅ LightGBM model saved to {lgbm_path}")
        
        # Calculate accuracy
        accuracy = lgbm_model.score(X_test, y_test)
        print(f"[Init] LightGBM Test Accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"[Init] ⚠️  LightGBM training failed: {e}")

# ============================================================================
# Train XGBoost Model
# ============================================================================
if not xgb_path.exists():
    print("[Init] Training XGBoost model...")
    try:
        xgb_params = PARAMS["model"].get("xgb_params", {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.05,
            "random_state": 42,
            "verbosity": 0
        })
        
        xgb_model = XGBClassifier(**xgb_params)
        xgb_model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(xgb_model, xgb_path)
        print(f"[Init] ✅ XGBoost model saved to {xgb_path}")
        
        # Calculate accuracy
        accuracy = xgb_model.score(X_test, y_test)
        print(f"[Init] XGBoost Test Accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"[Init] ⚠️  XGBoost training failed: {e}")

# Save feature columns for later use
print("[Init] Saving feature columns...")
feature_cols = X_train.columns.tolist()
joblib.dump(feature_cols, MODEL_DIR / "feature_columns.pkl")
print(f"[Init] ✅ Feature columns saved ({len(feature_cols)} features)")

print("[Init] ✅ Model initialization complete!")


print(f"[Init] Training data shape: {X_train.shape}")
print(f"[Init] Test data shape: {X_test.shape}")

# ============================================================================
# Train LightGBM Model
# ============================================================================
if not lgbm_path.exists():
    print("[Init] Training LightGBM model...")
    try:
        lgbm_params = PARAMS["model"].get("lgbm_params", {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.05,
            "random_state": 42
        })
        
        lgbm_model = LGBMClassifier(**lgbm_params)
        lgbm_model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(lgbm_model, lgbm_path)
        print(f"[Init] ✅ LightGBM model saved to {lgbm_path}")
        
        # Calculate accuracy
        accuracy = lgbm_model.score(X_test, y_test)
        print(f"[Init] LightGBM Test Accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"[Init] ⚠️  LightGBM training failed: {e}")

# ============================================================================
# Train XGBoost Model
# ============================================================================
if not xgb_path.exists():
    print("[Init] Training XGBoost model...")
    try:
        xgb_params = PARAMS["model"].get("xgb_params", {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.05,
            "random_state": 42,
            "verbosity": 0
        })
        
        xgb_model = XGBClassifier(**xgb_params)
        xgb_model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(xgb_model, xgb_path)
        print(f"[Init] ✅ XGBoost model saved to {xgb_path}")
        
        # Calculate accuracy
        accuracy = xgb_model.score(X_test, y_test)
        print(f"[Init] XGBoost Test Accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"[Init] ⚠️  XGBoost training failed: {e}")

# Save feature columns for later use
print("[Init] Saving feature columns...")
feature_cols = X_train.columns.tolist()
joblib.dump(feature_cols, MODEL_DIR / "feature_columns.pkl")
print(f"[Init] ✅ Feature columns saved ({len(feature_cols)} features)")

print("[Init] ✅ Model initialization complete!")

# something is changed