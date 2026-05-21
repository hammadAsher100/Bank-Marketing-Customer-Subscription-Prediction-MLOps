import os
import shutil
import zipfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
PARAMS = yaml.safe_load((ROOT / "params.yaml").open("r"))
RAW_PATH = Path(PARAMS["data"]["raw_path"])


def download():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    # If already present (e.g. pulled via DVC), skip download
    if RAW_PATH.exists():
        print(f"[download] Dataset already present at {RAW_PATH}. Skipping.")
        return

    source = PARAMS["data"].get("source_url", "")
    if not source:
        raise FileNotFoundError(
            f"Raw dataset not found at {RAW_PATH} and no source_url set in params.yaml. "
            "Run `dvc pull` or provide data.source_url."
        )

    import urllib.request
    print(f"[download] Fetching from {source}")

    if source.lower().endswith(".zip"):
        temp_zip = RAW_PATH.parent / "download.zip"
        urllib.request.urlretrieve(source, temp_zip)
        print(f"[download] Downloaded zip to {temp_zip}")

        with zipfile.ZipFile(temp_zip, "r") as zf:
            candidate = None
            for name in zf.namelist():
                if name.endswith("bank-full.csv") or name.endswith("bank.csv"):
                    candidate = name
                    break

            if candidate is None:
                raise FileNotFoundError(
                    "Downloaded zip did not contain bank-full.csv or bank.csv."
                )

            zf.extract(candidate, RAW_PATH.parent)
            extracted = RAW_PATH.parent / candidate
            if extracted != RAW_PATH:
                extracted.rename(RAW_PATH)

        temp_zip.unlink(missing_ok=True)
        print(f"[download] Extracted raw dataset to {RAW_PATH}")
        return

    urllib.request.urlretrieve(source, RAW_PATH)
    print(f"[download] Saved to {RAW_PATH}")


if __name__ == "__main__":
    download()