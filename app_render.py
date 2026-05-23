"""
Main entry point for Render deployment
This file should be used as the start command: python app_render.py
"""
import sys
import os
from pathlib import Path

# Detect and set local JRE path (from portable installation on native Render)
local_jre = Path(__file__).parent / "jre"
if local_jre.exists():
    os.environ["JAVA_HOME"] = str(local_jre.absolute())
    os.environ["PATH"] = str(local_jre.absolute() / "bin") + os.pathsep + os.environ.get("PATH", "")
    print(f"[Startup] Found local JRE at: {os.environ['JAVA_HOME']}")

print("[Startup] ════════════════════════════════════════════")
print("[Startup] Starting Bank Marketing API Server")
print("[Startup] ════════════════════════════════════════════")

# Initialize sklearn models if they don't exist
print("[Startup] Checking if sklearn models exist...")
model_dir = Path("data_and_model/models")
lgbm_exists = (model_dir / "lgbm_model.pkl").exists()
xgb_exists = (model_dir / "xgb_model.pkl").exists()

print(f"[Startup] LightGBM model: {'✅ Found' if lgbm_exists else '❌ Not found'}")
print(f"[Startup] XGBoost model: {'✅ Found' if xgb_exists else '❌ Not found'}")

if not (lgbm_exists and xgb_exists):
    print("[Startup] Initializing sklearn models...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import initialize_models
        print("[Startup] ✅ Sklearn models initialized")
    except Exception as e:
        print(f"[Startup] ⚠️  Error: {e}")

# Check PySpark model
pyspark_exists = (model_dir / "pyspark_model" / "metadata").exists()
print(f"[Startup] PySpark model: {'✅ Found' if pyspark_exists else '❌ Not found'}")

if not pyspark_exists:
    print("[Startup] Attempting to initialize PySpark model...")
    try:
        import initialize_pyspark_model
        print("[Startup] ✅ PySpark model initialized")
    except Exception as e:
        print(f"[Startup] ⚠️  PySpark initialization skipped: {e}")

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
