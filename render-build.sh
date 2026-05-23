#!/bin/bash
# Build script for Render - runs during deployment
# This installs dependencies and initializes models

echo "[Build] Installing dependencies..."
pip install -r requirements-backend.txt

echo "[Build] Initializing models..."
python initialize_models.py

echo "[Build] Build complete!"
