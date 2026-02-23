import os
import requests
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "./data")
E_DATA_URL = os.getenv("E_DATA_URL")
# INS_DATA_URL = os.getenv("INS_DATA_URL")

os.makedirs(DATA_DIR, exist_ok=True)

def download_file(url: str, filepath: str):
    if os.path.exists(filepath):
        return

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)

def ensure_data():
    download_file(E_DATA_URL, f"{DATA_DIR}/e_numbers.csv")
    # download_file(INS_DATA_URL, f"{DATA_DIR}/ins_numbers.csv")


if __name__ == '__main__':
    ensure_data()