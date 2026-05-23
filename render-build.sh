#!/bin/bash
# Build script for Render - runs during deployment
# This installs dependencies and initializes models

echo "[Build] Installing dependencies..."
pip install -r requirements-backend.txt

# Download a portable Java 11 JRE for PySpark if running in Linux (Render environment)
if [[ "$OSTYPE" == "linux-gnu"* ]] || [ -f /etc/os-release ]; then
  if [ ! -d "jre" ]; then
    echo "[Build] Linux environment detected. Downloading portable Java JRE (Temurin 11)..."
    curl -L "https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.22%2B7/OpenJDK11U-jre_x64_linux_hotspot_11.0.22_7.tar.gz" -o jre.tar.gz
    echo "[Build] Extracting JRE..."
    mkdir -p jre
    tar -xzf jre.tar.gz -C jre --strip-components=1
    rm jre.tar.gz
    echo "[Build] JRE installed locally in ./jre"
  else
    echo "[Build] Portable JRE already exists in ./jre"
  fi

  # Temporarily export for model initialization scripts running during build
  export JAVA_HOME="$(pwd)/jre"
  export PATH="$JAVA_HOME/bin:$PATH"
fi

echo "[Build] Initializing sklearn models (LightGBM, XGBoost)..."
python initialize_models.py

echo "[Build] Initializing PySpark model (optional - requires Java)..."
python initialize_pyspark_model.py || echo "[Build] ⚠️  PySpark initialization failed"

echo "[Build] Build complete!"
