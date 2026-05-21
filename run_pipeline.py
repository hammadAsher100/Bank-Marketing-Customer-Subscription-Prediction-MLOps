import sys
from pathlib import Path
# Ensure src/ is on the path when running from project root
sys.path.insert(0, str(Path(__file__).parent))

from src.data_pipeline.download import download
from src.data_pipeline.validate import validate
from src.data_pipeline.clean    import clean
from src.data_pipeline.feature_engineering import engineer
from src.data_pipeline.balance  import balance


def main():
    print("=" * 60)
    print("BANK MARKETING — DATA PIPELINE (Engineer 1)")
    print("=" * 60)

    stages = [
        ("1/5  Download",         download),
        ("2/5  Validate",         validate),
        ("3/5  Clean",            clean),
        ("4/5  Feature Engineer", engineer),
        ("5/5  Balance (SMOTE)",  balance),
    ]

    for label, fn in stages:
        print(f"\n── {label} ──")
        fn()

    print("\n" + "=" * 60)
    print("✓ Data pipeline complete. Outputs in data_and_model/")
    print("=" * 60)


if __name__ == "__main__":
    main()
