from pathlib import Path
import pandas as pd
import yaml
ROOT = Path(__file__).resolve().parents[2]  # goes up to MLOps-Saylani/
# PARAMS = yaml.safe_load(open(ROOT / "params.yaml"))
PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)
RAW_PATH     = Path(PARAMS["data"]["raw_path"])
CLEANED_PATH = Path(PARAMS["data"]["cleaned_path"])
SEP          = PARAMS["data"].get("sep", ";")

# Columns where 'unknown' will be replaced with the column mode
IMPUTE_UNKNOWN_COLS = ["job", "education"]

# Columns where 'unknown' is kept as its own valid category
KEEP_UNKNOWN_COLS = ["contact", "poutcome"]


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH, sep=SEP)
    print(f"[clean] Loaded raw data: {df.shape}")
    return df


def handle_unknowns(df: pd.DataFrame) -> pd.DataFrame:
    for col in IMPUTE_UNKNOWN_COLS:
        if col not in df.columns:
            continue
        mode_val = df.loc[df[col] != "unknown", col].mode()[0]
        n_replaced = (df[col] == "unknown").sum()
        df[col] = df[col].replace("unknown", mode_val)
        print(f"[clean]   {col}: replaced {n_replaced} 'unknown' with mode '{mode_val}'")

    for col in KEEP_UNKNOWN_COLS:
        if col not in df.columns:
            continue
        n = (df[col] == "unknown").sum()
        print(f"[clean]   {col}: keeping {n} 'unknown' as a valid category")

    return df


def drop_zero_duration(df: pd.DataFrame) -> pd.DataFrame:
    """
    duration == 0 means the client was never actually spoken to.
    These records cannot predict subscription and leak future info
    (a recorded 0 always means the call ended immediately → no sale).
    Drop them before any modelling.
    """
    n_before = len(df)
    df = df[df["duration"] > 0].copy()
    print(f"[clean]   Dropped {n_before - len(df)} zero-duration rows. Remaining: {len(df)}")
    return df


def convert_target(df: pd.DataFrame) -> pd.DataFrame:
    df["y"] = df["y"].map({"yes": 1, "no": 0})
    print(f"[clean]   Target distribution after conversion:\n{df['y'].value_counts().to_string()}")
    return df


def clean():
    CLEANED_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = load_raw()
    df = handle_unknowns(df)
    df = drop_zero_duration(df)
    df = convert_target(df)
    df = df.reset_index(drop=True)

    df.to_csv(CLEANED_PATH, index=False)
    print(f"[clean] ✓ Saved cleaned data to {CLEANED_PATH}  shape={df.shape}")


if __name__ == "__main__":
    clean()