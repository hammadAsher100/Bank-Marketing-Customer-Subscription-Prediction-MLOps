"""
initialize_pyspark_model.py
Trains PySpark GBT model for deployment
Runs if PySpark model doesn't exist
"""
import sys
import os
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

print("[PySpark Init] Starting PySpark model initialization...")

# Check if Java is available (required for PySpark)
java_check = os.system("java -version > /dev/null 2>&1")
if java_check != 0:
    print("[PySpark Init] ⚠️  Java not found - PySpark requires Java")
    print("[PySpark Init] Attempting to install Java...")
    
    # Try to install Java
    if sys.platform == "linux":
        os.system("apt-get update && apt-get install -y default-jdk")
    elif sys.platform == "win32":
        print("[PySpark Init] Manual Java installation required on Windows")
        print("[PySpark Init] Download from: https://www.oracle.com/java/technologies/downloads/")
        sys.exit(1)
    else:
        print("[PySpark Init] ⚠️  PySpark support requires Java JDK")
        sys.exit(1)

try:
    import yaml
    import pandas as pd
    import numpy as np
    from pyspark.sql import SparkSession
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import GBTClassifier
    from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
    from pyspark.ml.evaluation import BinaryClassificationEvaluator
    
    print("[PySpark Init] ✅ PySpark imports successful")
    
except ImportError as e:
    print(f"[PySpark Init] ⚠️  Error importing PySpark: {e}")
    print("[PySpark Init] Install PySpark: pip install pyspark")
    sys.exit(1)

# Load params
PARAMS = yaml.safe_load(open(ROOT / "params.yaml"))
MODEL_DIR = Path(PARAMS["pyspark"]["output_dir"])
SPARK_MODEL_PATH = Path(PARAMS["pyspark"]["model_path"])
PROCESSED_DIR = Path(PARAMS["data"]["processed_dir"])

# Create directories
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Check if model already exists
if SPARK_MODEL_PATH.exists():
    print(f"[PySpark Init] ✅ PySpark model already exists at {SPARK_MODEL_PATH}")
    sys.exit(0)

print("[PySpark Init] Creating Spark session...")

# Create Spark session
spark = SparkSession.builder \
    .appName(PARAMS["pyspark"]["app_name"]) \
    .master(PARAMS["pyspark"]["master"]) \
    .config("spark.driver.memory", PARAMS["pyspark"]["driver_memory"]) \
    .config("spark.executor.memory", PARAMS["pyspark"]["executor_memory"]) \
    .getOrCreate()

try:
    print("[PySpark Init] Loading training data...")
    
    # Try to load real data
    if (PROCESSED_DIR / "X_train_balanced.csv").exists():
        print("[PySpark Init] Loading real processed data...")
        X_train = pd.read_csv(PROCESSED_DIR / "X_train_balanced.csv")
        y_train = pd.read_csv(PROCESSED_DIR / "y_train_balanced.csv")
        X_test = pd.read_csv(PROCESSED_DIR / "X_test.csv")
        y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv")
        
        # Combine X and y
        train_df = pd.concat([X_train, y_train], axis=1)
        test_df = pd.concat([X_test, y_test], axis=1)
        
        print(f"[PySpark Init] ✅ Loaded real data: train={train_df.shape}, test={test_df.shape}")
    else:
        print("[PySpark Init] ⚠️  Processed data not found, creating synthetic data...")
        from sklearn.datasets import make_classification
        
        X_train, y_train = make_classification(
            n_samples=5000, n_features=20, n_informative=10, n_redundant=5,
            n_classes=2, weights=[0.8, 0.2], random_state=42
        )
        X_test, y_test = make_classification(
            n_samples=1000, n_features=20, n_informative=10, n_redundant=5,
            n_classes=2, weights=[0.8, 0.2], random_state=43
        )
        
        feature_names = [f"feature_{i}" for i in range(20)]
        train_df = pd.DataFrame(X_train, columns=feature_names)
        train_df['y'] = y_train
        test_df = pd.DataFrame(X_test, columns=feature_names)
        test_df['y'] = y_test
        
        print(f"[PySpark Init] ✅ Generated synthetic data: train={train_df.shape}, test={test_df.shape}")
    
    # Convert to Spark DataFrames
    train_spark = spark.createDataFrame(train_df)
    test_spark = spark.createDataFrame(test_df)
    
    # Get feature columns (all except 'y')
    feature_cols = [col for col in train_spark.columns if col != 'y']
    
    print(f"[PySpark Init] Building pipeline with {len(feature_cols)} features...")
    
    # Build pipeline
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    gbt = GBTClassifier(
        labelCol="y",
        featuresCol="features",
        maxIter=50,
        maxDepth=5,
        stepSize=0.05,
        seed=42
    )
    
    pipeline = Pipeline(stages=[assembler, gbt])
    
    print("[PySpark Init] Training GBT model...")
    model = pipeline.fit(train_spark)
    
    # Save model
    model.save(str(SPARK_MODEL_PATH))
    print(f"[PySpark Init] ✅ PySpark model saved to {SPARK_MODEL_PATH}")
    
    # Evaluate
    predictions = model.transform(test_spark)
    evaluator = BinaryClassificationEvaluator(labelCol="y", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    auc = evaluator.evaluate(predictions)
    print(f"[PySpark Init] Model AUC Score: {auc:.4f}")
    
    print("[PySpark Init] ✅ PySpark model initialization complete!")

except Exception as e:
    print(f"[PySpark Init] ❌ Error training PySpark model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    spark.stop()
    print("[PySpark Init] Spark session closed")
