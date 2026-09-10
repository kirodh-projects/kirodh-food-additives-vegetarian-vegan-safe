"""Legacy entry point. Canonical location: :mod:`src.shared.data_downloader`."""

from src.shared.data_downloader import DATA_DIR, E_DATA_URL, download_file, ensure_data

__all__ = ["DATA_DIR", "E_DATA_URL", "download_file", "ensure_data"]


if __name__ == '__main__':
    ensure_data()