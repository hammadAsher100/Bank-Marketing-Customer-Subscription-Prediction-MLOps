import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import yaml
import joblib
import numpy as np
import pandas as pd
from typing import Literal

# ── Config ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
PARAMS     = yaml.safe_load(open(ROOT / "params.yaml"))
MODEL_DIR  = Path(PARAMS["model"]["output_dir"])          # data_and_model/models
THRESHOLD  = float(PARAMS["model"].get("threshold", 0.5))

# PySpark model path (for GBT)
SPARK_MODEL_PATH = PARAMS["pyspark"]["model_path"]        # data_and_model/models/pyspark_model
# Recommended threshold from pyspark training summary
SPARK_THRESHOLD  = 0.70   # as set in pyspark train.py

# ── Feature columns (saved during training) ───────────────────────────────────
# These are the exact columns the sklearn models were trained on.
# Loaded lazily so startup doesn't fail if file doesn't exist yet.
_FEATURE_COLS = None

def get_feature_cols():
    global _FEATURE_COLS
    if _FEATURE_COLS is None:
        feat_path = MODEL_DIR / "feature_columns.pkl"
        if feat_path.exists():
            _FEATURE_COLS = joblib.load(feat_path)
        else:
            # Fallback: read from a processed CSV header if pkl not saved yet
            proc_dir = Path(PARAMS["data"]["processed_dir"])
            x_path   = proc_dir / "X_test.csv"
            if x_path.exists():
                _FEATURE_COLS = pd.read_csv(x_path, nrows=0).columns.tolist()
    return _FEATURE_COLS


# ═══════════════════════════════════════════════════════════════════════════════
# SKLEARN MODEL LOADER  (LightGBM / XGBoost)
# ═══════════════════════════════════════════════════════════════════════════════
_model_cache: dict = {}   # {"lgbm": model_object, "xgb": model_object}

def load_sklearn_model(model_name: Literal["lgbm", "xgb"] = "lgbm"):
    """
    Load and cache a sklearn-compatible model from disk.
    model_name: "lgbm" → lgbm_model.pkl
                "xgb"  → xgb_model.pkl
    """
    if model_name not in _model_cache:
        pkl_map = {
            "lgbm": MODEL_DIR / "lgbm_model.pkl",
            "xgb":  MODEL_DIR / "xgb_model.pkl",
        }
        pkl_path = pkl_map.get(model_name)
        if pkl_path is None or not pkl_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {pkl_path}. "
                "Run train.py first to generate models."
            )
        _model_cache[model_name] = joblib.load(pkl_path)
        print(f"[predict] Loaded {model_name} model from {pkl_path}")
    return _model_cache[model_name]


# ═══════════════════════════════════════════════════════════════════════════════
# PYSPARK MODEL LOADER  (GBT Pipeline)
# ═══════════════════════════════════════════════════════════════════════════════
_spark_model_cache = None

def load_spark_model():
    """
    Load the PySpark PipelineModel from disk.
    Only imported when needed to avoid Spark startup cost.
    Validates model exists BEFORE starting SparkSession to fail fast.

    Memory settings are read from env vars first, falling back to params.yaml.
    Set SPARK_DRIVER_MEMORY / SPARK_EXECUTOR_MEMORY in the environment to
    override the defaults (e.g. Dockerfile.api sets them to 512m for Render).
    """
    global _spark_model_cache
    if _spark_model_cache is None:
        import sys
        import os

        # ── Python executable: driver & workers must use the same binary ──────
        # If env vars are already set (e.g. by Dockerfile ENV), keep them.
        # Otherwise fall back to the current interpreter.
        if "PYSPARK_PYTHON" not in os.environ:
            os.environ["PYSPARK_PYTHON"] = sys.executable
        if "PYSPARK_DRIVER_PYTHON" not in os.environ:
            os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

        # ── Java JRE: detect local portable JRE (for native Render environment) 
        local_jre = Path(ROOT) / "jre"
        if local_jre.exists() and "JAVA_HOME" not in os.environ:
            os.environ["JAVA_HOME"] = str(local_jre.absolute())
            os.environ["PATH"] = str(local_jre.absolute() / "bin") + os.pathsep + os.environ.get("PATH", "")

        # ── Windows-only: Hadoop winutils ─────────────────────────────────────
        if sys.platform == "win32":
            hadoop_home = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "hadoop")
            )
            os.environ["HADOOP_HOME"] = hadoop_home
            os.environ["PATH"] = (
                os.path.join(hadoop_home, "bin") + os.pathsep + os.environ.get("PATH", "")
            )

        # ── Validate model exists BEFORE starting expensive SparkSession ──────
        model_path = Path(SPARK_MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(
                f"PySpark model not found at {model_path}. "
                "Run the PySpark training pipeline first: "
                "python src/pyspark_workflow/run_pyspark_pipeline.py"
            )
        if not (model_path / "metadata").exists():
            raise FileNotFoundError(
                f"PySpark model at {model_path} is incomplete (missing metadata/). "
                "The model may not have been trained successfully. "
                "Re-run: python src/pyspark_workflow/run_pyspark_pipeline.py"
            )

        # ── Memory: env vars override params.yaml (Docker sets 512m) ─────────
        driver_mem   = os.environ.get("SPARK_DRIVER_MEMORY",   PARAMS["pyspark"]["driver_memory"])
        executor_mem = os.environ.get("SPARK_EXECUTOR_MEMORY", PARAMS["pyspark"]["executor_memory"])

        from pyspark.sql import SparkSession
        from pyspark.ml import PipelineModel

        spark = (
            SparkSession.builder
            .appName("BankMarketing_Serving")
            .config("spark.driver.memory",          driver_mem)
            .config("spark.executor.memory",         executor_mem)
            .config("spark.python.use.daemon",       "false")
            .config("spark.sql.shuffle.partitions",  "2")   # reduce overhead
            .config("spark.default.parallelism",     "2")
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("ERROR")

        _spark_model_cache = (spark, PipelineModel.load(str(model_path)))
        print(f"[predict] Loaded PySpark model from {model_path}")
    return _spark_model_cache


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT ALIGNMENT HELPER
# ═══════════════════════════════════════════════════════════════════════════════
def align_input(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode the raw input DataFrame exactly the same way
    feature_engineering.py does, then align columns to training columns.

    Steps:
      1. Add engineered features (same as feature_engineering.py)
      2. One-hot encode categorical columns
      3. Add missing columns as 0, drop extra columns
      4. Reorder to match training feature order
    """
    df = input_df.copy()

    # ── Step 1: Engineered features ───────────────────────────────────────────
    avg_duration = df["duration"].mean() if len(df) > 1 else df["duration"].iloc[0]
    df["contacted_before"] = (df["pdays"] != -1).astype(int)
    df["is_long_call"]     = (df["duration"] > avg_duration).astype(int)
    df["pdays_clipped"]    = df["pdays"].clip(lower=0, upper=900)
    df.loc[df["pdays"] == -1, "pdays_clipped"] = 0
    df["call_intensity"]   = np.log1p(df["campaign"] * df["duration"])
    if "poutcome" in df.columns:
        df["prev_success"] = (df["poutcome"] == "success").astype(int)

    # ── Step 2: One-hot encode ────────────────────────────────────────────────
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    cat_cols = [c for c in cat_cols if c != "y"]
    df = pd.get_dummies(df, columns=cat_cols, drop_first=False, dtype=int)

    # ── Step 3 & 4: Align to training columns ────────────────────────────────
    feat_cols = get_feature_cols()
    if feat_cols is not None:
        for col in feat_cols:
            if col not in df.columns:
                df[col] = 0           # add missing dummy columns
        df = df[feat_cols]            # reorder + drop extras

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PREDICT FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════
def predict(
    input_data: dict,
    model_type: Literal["lgbm", "xgb", "pyspark"] = "lgbm",
    threshold: float | None = None,
) -> dict:
    """
    Main prediction function called by FastAPI.

    Parameters
    ----------
    input_data  : dict of raw feature values (from PredictRequest schema)
    model_type  : "lgbm" | "xgb" | "pyspark"
    threshold   : override decision threshold (defaults to params.yaml value)

    Returns
    -------
    dict with keys:
        prediction      : int (0 = No, 1 = Yes)
        probability     : float (probability of class 1)
        model_used      : str
        threshold_used  : float
        label           : str ("Will Subscribe" / "Will NOT Subscribe")
    """

    # ── PySpark path ──────────────────────────────────────────────────────────
    if model_type == "pyspark":
        try:
            spark, spark_model = load_spark_model()
            from pyspark.ml.functions import vector_to_array

            raw_df   = pd.DataFrame([input_data])
            
            # Add engineered features expected by PySpark
            avg_duration = raw_df["duration"].mean() if len(raw_df) > 1 else raw_df["duration"].iloc[0]
            raw_df["contacted_before"] = (raw_df["pdays"] != -1).astype(int)
            raw_df["is_long_call"]     = (raw_df["duration"] > avg_duration).astype(int)
            raw_df["pdays_clipped"]    = raw_df["pdays"].clip(lower=0, upper=900)
            raw_df.loc[raw_df["pdays"] == -1, "pdays_clipped"] = 0
            raw_df["call_intensity"]   = np.log1p(raw_df["campaign"] * raw_df["duration"])
            if "poutcome" in raw_df.columns:
                raw_df["prev_success"] = (raw_df["poutcome"] == "success").astype(int)

            spark_df = spark.createDataFrame(raw_df)

            preds    = spark_model.transform(spark_df)
            prob_row = preds.select(vector_to_array("probability")[1].alias("prob_1")).collect()
            prob     = float(prob_row[0]["prob_1"])

            t          = threshold if threshold is not None else SPARK_THRESHOLD
            prediction = int(prob >= t)
            
            label = "Will Subscribe ✅" if prediction == 1 else "Will NOT Subscribe ❌"

            return {
                "prediction":     prediction,
                "probability":    round(prob, 4),
                "model_used":     model_type,
                "threshold_used": t,
                "label":          label,
            }
        except Exception as e:
            # PySpark prediction failed - print detailed error and gracefully fall back to LGBM
            print(f"[predict] ❌ PySpark prediction FAILED: {e}")
            print(f"[predict] Error type: {type(e).__name__}")
            print("[predict] Automatically falling back to LightGBM model for prediction.")
            
            # Call predict recursively using lgbm
            fallback_result = predict(
                input_data=input_data,
                model_type="lgbm",
                threshold=threshold,
            )
            
            # Customize the metadata for the user/frontend to clearly explain the fallback
            fallback_result["model_used"] = "pyspark_fallback (lgbm)"
            fallback_result["message"] = (
                f"PySpark prediction engine failed (Reason: {str(e)[:80]}...). "
                f"We have automatically routed your request to the LightGBM fallback model."
            )
            return fallback_result

    # ── Sklearn path (LightGBM / XGBoost) ────────────────────────────────────
    else:
        model    = load_sklearn_model(model_type)
        raw_df   = pd.DataFrame([input_data])
        aligned  = align_input(raw_df)

        prob       = float(model.predict_proba(aligned)[0, 1])
        t          = threshold if threshold is not None else THRESHOLD
        prediction = int(prob >= t)

    label = "Will Subscribe ✅" if prediction == 1 else "Will NOT Subscribe ❌"

    return {
        "prediction":     prediction,
        "probability":    round(prob, 4),
        "model_used":     model_type,
        "threshold_used": t,
        "label":          label,
    }


# ── Quick local test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "age": 35, "job": "management", "marital": "married",
        "education": "tertiary", "default": "no", "balance": 1500,
        "housing": "yes", "loan": "no", "contact": "cellular",
        "day": 15, "month": "may", "duration": 300,
        "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
    }
    result = predict(sample, model_type="lgbm")
    print(result)