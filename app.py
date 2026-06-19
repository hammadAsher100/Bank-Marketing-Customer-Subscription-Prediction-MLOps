"""
Main Hugging Face Spaces entry point
Runs both FastAPI backend and Streamlit frontend in a single application
"""
import os
import subprocess
import time
import sys
from pathlib import Path
import threading

# Initialize models if they don't exist
print("════════════════════════════════════════════")
print("Starting Bank Marketing MLOps Application")
print("════════════════════════════════════════════")

model_dir = Path("data_and_model/models")
lgbm_exists = (model_dir / "lgbm_model.pkl").exists()
xgb_exists = (model_dir / "xgb_model.pkl").exists()

print(f"LightGBM model: {'✅ Found' if lgbm_exists else '❌ Not found'}")
print(f"XGBoost model: {'✅ Found' if xgb_exists else '❌ Not found'}")

if not (lgbm_exists and xgb_exists):
    print("Initializing sklearn models...")
    try:
        import initialize_models
        print("✅ Models initialized")
    except Exception as e:
        print(f"⚠️  Error: {e}")

print("════════════════════════════════════════════")

def start_fastapi():
    """Start FastAPI backend on port 8000"""
    print("Starting FastAPI backend on port 8000...")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "src.serving.api:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

def start_streamlit():
    """Start Streamlit frontend on port 7860 (Hugging Face default)"""
    print("Starting Streamlit frontend on port 7860...")
    time.sleep(3)  # Wait for FastAPI to start
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "streamlit_app.py",
        "--server.port", "7860",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    # Set API URL for Streamlit to connect to FastAPI
    os.environ["API_URL"] = "http://localhost:8000"
    
    # Start FastAPI in a separate thread
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()
    
    # Start Streamlit in main thread
    start_streamlit()
