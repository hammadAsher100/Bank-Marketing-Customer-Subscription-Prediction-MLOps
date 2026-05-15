import sys
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pyspark_workflow.etl import run_etl
from src.pyspark_workflow.train import train_pyspark_model

def main():
    # Use ASCII characters for compatibility
    print("=" * 60)
    print("PYSPARK RETRAINING PIPELINE")
    print("=" * 60)

    print("\n-- Stage 1: ETL (Spark) --")
    run_etl()

    print("\n-- Stage 2: Training (Spark MLlib) --")
    train_pyspark_model()

    print("\n" + "=" * 60)
    print("PySpark pipeline complete.")
    print("=" * 60)

if __name__ == "__main__":
    main()
