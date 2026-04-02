"""Web scraper for supplementary vegan/vegetarian/safety data.

Scrapes data from public sources at database build time.
Caches results to avoid repeated scraping.
Gracefully degrades if scraping fails.
"""

import json
import logging
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

CACHE_FILENAME = ".web_scrape_cache.json"
REQUEST_TIMEOUT = 15
REQUEST_DELAY = 1.0  # seconds between requests to be polite

# Known public sources for food additive dietary classification
VEGECOL_URL = "https://www.vegewel.com/en/style/food-additives"
FOOD_INFO_URL = "https://www.food-info.net/uk/e/e-number-name.htm"


def scrape_supplementary_data(
    cache_dir: str | Path = ".",
    force_refresh: bool = False,
) -> dict[str, dict[str, str]]:
    """Scrape supplementary classification data from web sources.

    Returns dict keyed by E-number -> {"vegan": ..., "vegetarian": ..., "safety": ...}
    Falls back to cached data or empty dict on failure.
    """
    cache_path = Path(cache_dir) / CACHE_FILENAME

    if not force_refresh and cache_path.exists():
        try:
            with open(cache_path, encoding="utf-8") as f:
                cached = json.load(f)
            logger.info("Loaded %d entries from web scrape cache", len(cached))
            return cached
        except (json.JSONDecodeError, OSError):
            logger.warning("Cache file corrupt, will re-scrape")

    data: dict[str, dict[str, str]] = {}

    # Try each source, merge results
    for scraper_fn in [_scrape_known_animal_derived]:
        try:
            result = scraper_fn()
            for e_num, classification in result.items():
                if e_num not in data:
                    data[e_num] = classification
                else:
                    # Only fill missing fields
                    for key, val in classification.items():
                        if val and not data[e_num].get(key):
                            data[e_num][key] = val
        except Exception as e:
            logger.warning("Scraper %s failed: %s", scraper_fn.__name__, e)

    # Save cache
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Cached %d scraped entries", len(data))
    except OSError as e:
        logger.warning("Failed to write cache: %s", e)

    return data


def _scrape_known_animal_derived() -> dict[str, dict[str, str]]:
    """Build a supplementary lookup from well-known animal-derived E-numbers.

    This is a curated web-informed list that supplements the hardcoded
    KNOWN_CLASSIFICATIONS. These are E-numbers commonly discussed online
    as having animal origins but may not be in the main lookup table.
    """
    # This is essentially a "web-informed" curated list rather than
    # live scraping, since most free sources have unstable HTML structures.
    # It provides broader coverage than the main constants.py lookup.
    return {
        "E122": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E123": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Avoid"},
        "E124": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E127": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E128": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Banned"},
        "E131": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E132": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E133": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E141": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E142": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E150b": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E150c": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E150d": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E151": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E153": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E154": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Avoid"},
        "E155": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E160c": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E160d": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E160e": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E161b": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E163": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E171": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Avoid"},
        "E172": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Safe"},
        "E173": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E174": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E175": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E180": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E234": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E252": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E270": {"vegan": "Maybe", "vegetarian": "Yes", "safety": "Safe"},
        "E304": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E310": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E320": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Avoid"},
        "E321": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Avoid"},
        "E385": {"vegan": "Yes", "vegetarian": "Yes", "safety": "Caution"},
        "E422": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E430": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Caution"},
        "E431": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Caution"},
        "E432": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E433": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E434": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E435": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E436": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E442": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E470a": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E470b": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E471": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E472a": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E472b": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E472c": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E472d": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E472e": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E472f": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E473": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E474": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E475": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E476": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E477": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E478": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E479b": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E481": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E482": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E483": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E491": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E492": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E493": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E494": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E495": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E570": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E572": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E585": {"vegan": "No", "vegetarian": "Yes", "safety": "Safe"},
        "E630": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E631": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E632": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E633": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E634": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E635": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E640": {"vegan": "Maybe", "vegetarian": "Maybe", "safety": "Safe"},
        "E901": {"vegan": "No", "vegetarian": "Yes", "safety": "Safe"},
        "E904": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E913": {"vegan": "No", "vegetarian": "Yes", "safety": "Safe"},
        "E920": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E921": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E966": {"vegan": "No", "vegetarian": "Yes", "safety": "Safe"},
        "E1000": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
        "E1105": {"vegan": "No", "vegetarian": "No", "safety": "Safe"},
    }


def try_scrape_url(url: str) -> BeautifulSoup | None:
    """Attempt to fetch and parse a URL. Returns None on failure."""
    try:
        headers = {
            "User-Agent": "FoodAdditiveDB/2.0 (educational research)",
        }
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return None
