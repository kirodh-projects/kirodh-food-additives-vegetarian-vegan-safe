"""Generic file-download helper.

Moved here from the legacy root ``data_downloader.py`` so all
domains share one implementation.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "./data")
E_DATA_URL = os.getenv("E_DATA_URL")


def download_file(url: str, filepath: str) -> None:
    """Download ``url`` to ``filepath`` unless it already exists."""
    if not url:
        raise ValueError("No URL provided (E_DATA_URL is not set).")
    if os.path.exists(filepath):
        return

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)


def ensure_data(data_dir: str | None = None, e_data_url: str | None = None) -> None:
    """Ensure the raw CSV files exist, downloading them if needed."""
    target_dir = data_dir or DATA_DIR
    os.makedirs(target_dir, exist_ok=True)
    url = e_data_url or E_DATA_URL
    if url:
        download_file(url, f"{target_dir}/e_numbers.csv")


if __name__ == "__main__":
    ensure_data()
