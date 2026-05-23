"""
Main entry point for Render deployment
This file should be used as the start command: python app_render.py
"""
import sys
import os
from pathlib import Path

print("[Startup] ════════════════════════════════════════════")
print("[Startup] Starting Bank Marketing API Server")
print("[Startup] ════════════════════════════════════════════")

# Initialize models if they don't exist
print("[Startup] Checking if models exist...")
model_dir = Path("data_and_model/models")
lgbm_exists = (model_dir / "lgbm_model.pkl").exists()
xgb_exists = (model_dir / "xgb_model.pkl").exists()

print(f"[Startup] LightGBM model: {'✅ Found' if lgbm_exists else '❌ Not found'}")
print(f"[Startup] XGBoost model: {'✅ Found' if xgb_exists else '❌ Not found'}")

if not (lgbm_exists and xgb_exists):
    print("[Startup] Models not found. Initializing...")
    try:
        # Import and run initialization
        sys.path.insert(0, str(Path(__file__).parent))
        import initialize_models
        print("[Startup] ✅ Model initialization completed")
    except Exception as e:
        print(f"[Startup] ⚠️  Model initialization error: {e}")
        print("[Startup] Continuing... Models will be available after first train")
else:
    print("[Startup] ✅ Models ready to load")

print("[Startup] ════════════════════════════════════════════")

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"[Startup] Starting API on {host}:{port}")
    
    uvicorn.run(
        "src.serving.api:app",
        host=host,
        port=port,
        reload=False
    )
