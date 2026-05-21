from pathlib import Path
import pandas as pd
import yaml
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
ROOT = Path(__file__).resolve().parents[2]  # goes up to MLOps-Saylani/
# PARAMS = yaml.safe_load(open(ROOT / "params.yaml"))
PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)
FEATURES_PATH = Path(PARAMS["data"]["features_path"])
PROCESSED_DIR = Path(PARAMS["data"]["processed_dir"])

RANDOM_STATE  = PARAMS["base"]["random_state"]
TEST_SIZE     = PARAMS["data"].get("test_size", 0.20)
SMOTE_K       = PARAMS["data"].get("smote_k_neighbors", 5)

def balance():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(FEATURES_PATH)
    print(f"[balance] Loaded features: {df.shape}")

    if "y" not in df.columns:
        raise KeyError("[balance] Target column 'y' not found in feature file.")

    X = df.drop(columns=["y"])
    y = df["y"]

    print(f"[balance] Class distribution before balance:\n{y.value_counts().to_string()}")

    # ── Train / test split (stratified) ─────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"[balance] Train size: {len(X_train)}  |  Test size: {len(X_test)}")

    # ── SMOTE on train only ──────────────────────────────────────────────────
    smote = SMOTE(k_neighbors=SMOTE_K, random_state=RANDOM_STATE)
    X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
    print(f"[balance] After SMOTE - Train: {len(X_train_bal)}  "
          f"Class dist:\n{pd.Series(y_train_bal).value_counts().to_string()}")

    # ── Save ────────────────────────────────────────────────────────────────
    X_train_bal.to_csv(PROCESSED_DIR / "X_train_balanced.csv", index=False)
    pd.Series(y_train_bal, name="y").to_csv(PROCESSED_DIR / "y_train_balanced.csv", index=False)
    X_test.to_csv(PROCESSED_DIR / "X_test.csv", index=False)
    y_test.to_csv(PROCESSED_DIR / "y_test.csv", index=False)

    print(f"[balance] Balanced datasets saved to {PROCESSED_DIR}")


if __name__ == "__main__":
    balance()