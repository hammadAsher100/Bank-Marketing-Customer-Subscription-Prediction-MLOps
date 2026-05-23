"""
Main entry point for Render deployment
This file should be used as the start command: python app_render.py
"""
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    uvicorn.run(
        "src.serving.api:app",
        host=host,
        port=port,
        reload=False
    )
