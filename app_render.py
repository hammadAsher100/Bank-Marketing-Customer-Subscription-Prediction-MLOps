"""
Main entry point for Render deployment
This file should be used as the start command: python app_render.py
"""
import sys
import os
from pathlib import Path

# Initialize models if they don't exist
print("[Startup] Checking if models exist...")
model_dir = Path("data_and_model/models")
if not (model_dir / "lgbm_model.pkl").exists() or not (model_dir / "xgb_model.pkl").exists():
    print("[Startup] Models not found. Initializing...")
    try:
        import initialize_models
        print("[Startup] Model initialization completed")
    except Exception as e:
        print(f"[Startup] Warning: Model initialization failed - {e}")
        print("[Startup] API will start but predictions may fail")

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    uvicorn.run(
        "src.serving.api:app",
        host=host,
        port=port,
        reload=False
    )
