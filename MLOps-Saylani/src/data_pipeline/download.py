import os
import shutil
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
# goes up to MLOps-Saylani/
ROOT = Path(__file__).resolve().parents[2]

PARAMS = yaml.safe_load(
    open(ROOT / "params.yaml")
)
print(type(PARAMS))
print(PARAMS)

RAW_PATH = Path(PARAMS["data"]["raw_path"])

def download():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    # If already present (e.g. pulled via DVC), skip download
    if RAW_PATH.exists():
        print(f"[download] Dataset already present at {RAW_PATH}. Skipping.")
        return

    source = PARAMS["data"].get("source_url", "")
    if source:
        import urllib.request
        print(f"[download] Fetching from {source}")
        urllib.request.urlretrieve(source, RAW_PATH)
        print(f"[download] Saved to {RAW_PATH}")
    else:
        raise FileNotFoundError(
            f"Raw dataset not found at {RAW_PATH} and no source_url set in params.yaml. "
            "Run `dvc pull` or provide data.source_url."
        )


if __name__ == "__main__":
    download()