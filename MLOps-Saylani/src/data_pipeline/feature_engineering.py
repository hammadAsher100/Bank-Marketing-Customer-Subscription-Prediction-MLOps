import numpy as np
from pathlib import Path
import pandas as pd
import yaml
ROOT = Path(__file__).resolve().parents[2]  # goes up to MLOps-Saylani/
# PARAMS = yaml.safe_load(open(ROOT / "params.yaml"))
PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)
CLEANED_PATH  = Path(PARAMS["data"]["cleaned_path"])
FEATURES_PATH = Path(PARAMS["data"]["features_path"])


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    # ── Fix: threshold from cleaned data ─────────────────────────────────────
    avg_duration = df["duration"].mean()
    print(f"[engineer]   avg_duration (post-clean) = {avg_duration:.1f}s")

    # contacted_before: pdays == -1 → never contacted → 0
    df["contacted_before"] = (df["pdays"] != -1).astype(int)

    # is_long_call: uses cleaned-data threshold (fixed)
    df["is_long_call"] = (df["duration"] > avg_duration).astype(int)

    # pdays_clipped: replace -1 sentinel with 0, cap at 900
    # FIX: raised cap from 400 → 900 because actual pdays max is 871;
    # 400 was silently clipping 234 real values
    df["pdays_clipped"] = df["pdays"].clip(lower=0, upper=900)
    # -1 sentinel → 0 (never contacted)
    df.loc[df["pdays"] == -1, "pdays_clipped"] = 0

    # call_intensity: log(1 + campaign * duration)
    df["call_intensity"] = np.log1p(df["campaign"] * df["duration"])

    # prev_success: before encoding poutcome
    if "poutcome" in df.columns:
        df["prev_success"] = (df["poutcome"] == "success").astype(int)

    print(f"[engineer]   contacted_before dist: {df['contacted_before'].value_counts().to_dict()}")
    print(f"[engineer]   is_long_call dist:     {df['is_long_call'].value_counts().to_dict()}")
    print(f"[engineer]   prev_success dist:     {df['prev_success'].value_counts().to_dict()}")
    return df


def encode(df: pd.DataFrame) -> pd.DataFrame:
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    # Remove target if it somehow ended up as object
    cat_cols = [c for c in cat_cols if c != "y"]

    print(f"[engineer]   One-hot encoding columns: {cat_cols}")
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True, dtype=int)
    return df


def engineer():
    FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CLEANED_PATH)
    print(f"[engineer] Loaded cleaned data: {df.shape}")

    df = add_features(df)
    df = encode(df)

    df.to_csv(FEATURES_PATH, index=False)
    print(f"[engineer] ✓ Saved feature-engineered data to {FEATURES_PATH}  shape={df.shape}")
    print(f"[engineer]   Columns ({len(df.columns)}): {df.columns.tolist()}")


if __name__ == "__main__":
    engineer()