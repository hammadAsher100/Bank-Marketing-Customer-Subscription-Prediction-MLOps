from pathlib import Path
import pandas as pd
import yaml
ROOT = Path(__file__).resolve().parents[2]  # goes up to MLOps-Saylani/
# PARAMS = yaml.safe_load(open(ROOT / "params.yaml"))
PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)
RAW_PATH = Path(PARAMS["data"]["raw_path"])

EXPECTED_COLUMNS = [
    "age", "job", "marital", "education", "default", "balance",
    "housing", "loan", "contact", "day", "month", "duration",
    "campaign", "pdays", "previous", "poutcome", "y",
]

NUMERIC_COLUMNS = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]
CATEGORICAL_COLUMNS = ["job", "marital", "education", "default", "housing", "loan",
                       "contact", "month", "poutcome", "y"]

VALID_TARGET_VALUES = {"yes", "no"}
MIN_ROWS = 40_000          # Fail if dataset is suspiciously small
MAX_DUPLICATE_RATE = 0.05  # Allow ≤5% exact duplicates


def load_raw() -> pd.DataFrame:
    sep = PARAMS["data"].get("sep", ";")
    df = pd.read_csv(RAW_PATH, sep=sep)
    return df


def check_schema(df: pd.DataFrame) -> list[str]:
    issues = []
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    extra = set(df.columns) - set(EXPECTED_COLUMNS)
    if missing:
        issues.append(f"CRITICAL — Missing columns: {sorted(missing)}")
    if extra:
        issues.append(f"WARNING  — Unexpected columns: {sorted(extra)}")
    return issues


def check_row_count(df: pd.DataFrame) -> list[str]:
    issues = []
    if len(df) < MIN_ROWS:
        issues.append(f"CRITICAL — Only {len(df):,} rows (expected ≥ {MIN_ROWS:,})")
    return issues


def check_nulls(df: pd.DataFrame) -> list[str]:
    """Raw dataset should have zero true NaN values (unknowns are encoded as 'unknown')."""
    issues = []
    nulls = df.isnull().sum()
    bad = nulls[nulls > 0]
    if not bad.empty:
        issues.append(f"CRITICAL — Null values found:\n{bad.to_string()}")
    return issues


def check_target(df: pd.DataFrame) -> list[str]:
    issues = []
    if "y" not in df.columns:
        return ["CRITICAL — Target column 'y' missing"]
    actual = set(df["y"].unique())
    unexpected = actual - VALID_TARGET_VALUES
    if unexpected:
        issues.append(f"CRITICAL — Unexpected target values: {unexpected}")
    pos_rate = (df["y"] == "yes").mean()
    if pos_rate < 0.05 or pos_rate > 0.50:
        issues.append(f"WARNING  — Unusual positive-class rate: {pos_rate:.2%}")
    return issues


def check_numeric_ranges(df: pd.DataFrame) -> list[str]:
    issues = []
    checks = {
        "age":      (18, 100),
        "duration": (0, 5000),
        "campaign": (1, 100),
        "previous": (0, 50),
    }
    for col, (lo, hi) in checks.items():
        if col not in df.columns:
            continue
        bad = df[(df[col] < lo) | (df[col] > hi)]
        if not bad.empty:
            issues.append(f"WARNING  — {col}: {len(bad)} rows outside [{lo}, {hi}]")
    return issues


def check_duplicates(df: pd.DataFrame) -> list[str]:
    issues = []
    dup_rate = df.duplicated().mean()
    if dup_rate > MAX_DUPLICATE_RATE:
        issues.append(f"WARNING  — Duplicate rate {dup_rate:.2%} exceeds threshold {MAX_DUPLICATE_RATE:.2%}")
    return issues


def validate():
    print(f"[validate] Loading raw data from {RAW_PATH}")
    df = load_raw()
    print(f"[validate] Shape: {df.shape}")

    all_issues: list[str] = []
    all_issues += check_schema(df)
    all_issues += check_row_count(df)
    all_issues += check_nulls(df)
    all_issues += check_target(df)
    all_issues += check_numeric_ranges(df)
    all_issues += check_duplicates(df)

    criticals = [i for i in all_issues if i.startswith("CRITICAL")]
    warnings  = [i for i in all_issues if i.startswith("WARNING")]

    for w in warnings:
        print(f"  ⚠  {w}")
    for c in criticals:
        print(f"  ✗  {c}")

    if criticals:
        raise ValueError(f"[validate] {len(criticals)} critical issue(s) found. Pipeline halted.")

    print(f"[validate] ✓ Passed ({len(warnings)} warning(s))")


if __name__ == "__main__":
    validate()