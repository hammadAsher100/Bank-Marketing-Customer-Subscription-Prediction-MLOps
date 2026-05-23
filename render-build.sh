#!/bin/bash
# Build script for Render - runs during deployment
# This installs dependencies and initializes models

echo "[Build] Installing dependencies..."
pip install -r requirements-backend.txt

echo "[Build] Initializing sklearn models (LightGBM, XGBoost)..."
python initialize_models.py

echo "[Build] Initializing PySpark model (optional - requires Java)..."
python initialize_pyspark_model.py || echo "[Build] ⚠️  PySpark initialization skipped (Java not available)"

echo "[Build] Build complete!"
