"""Deprecated: use :mod:`src.food_additives.web_scraper` instead."""

from src.food_additives.web_scraper import *  # noqa: F401,F403
from src.food_additives.web_scraper import scrape_supplementary_data, try_scrape_url

__all__ = ["scrape_supplementary_data", "try_scrape_url"]
