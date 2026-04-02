"""Classification logic for vegan, vegetarian, safety, and origin status.

Uses a three-tier approach:
  Tier 1: Known lookup table (highest confidence)
  Tier 2: Keyword-based text analysis (medium confidence)
  Tier 3: Web-scraped supplementary data (fallback)
"""

from src.utils.constants import (
    AMBIGUOUS_ORIGIN_KEYWORDS,
    BEE_KEYWORDS,
    DAIRY_KEYWORDS,
    EGG_KEYWORDS,
    KNOWN_CLASSIFICATIONS,
    NATURAL_ANIMAL_KEYWORDS,
    NATURAL_MINERAL_KEYWORDS,
    NATURAL_PLANT_KEYWORDS,
    NON_VEGAN_KEYWORDS,
    NON_VEGETARIAN_KEYWORDS,
    SAFETY_AVOID_KEYWORDS,
    SAFETY_BANNED_KEYWORDS,
    SAFETY_CAUTION_KEYWORDS,
    SAFETY_SAFE_KEYWORDS,
    SYNTHETIC_KEYWORDS,
)
from src.utils.text_analysis import contains_animal_keyword, contains_phrase, extract_adi


def classify_vegan(
    e_number: str,
    info_text: str,
    web_data: dict | None = None,
) -> str:
    """Classify vegan status. Returns 'Yes', 'No', 'Maybe', or 'Unknown'."""
    # Tier 1: Known lookup
    if e_number in KNOWN_CLASSIFICATIONS:
        return KNOWN_CLASSIFICATIONS[e_number]["vegan"]

    # Tier 3: Web data (checked before keyword analysis since it's curated)
    if web_data and e_number in web_data:
        vegan = web_data[e_number].get("vegan")
        if vegan:
            return vegan

    if not info_text or len(info_text.strip()) < 20:
        return "Unknown"

    # Tier 2: Keyword analysis
    if contains_phrase(info_text, AMBIGUOUS_ORIGIN_KEYWORDS):
        return "Maybe"

    if contains_animal_keyword(info_text, NON_VEGAN_KEYWORDS):
        return "No"

    if contains_phrase(info_text, EGG_KEYWORDS):
        return "No"

    if contains_phrase(info_text, DAIRY_KEYWORDS):
        return "No"

    if contains_phrase(info_text, BEE_KEYWORDS):
        return "No"

    has_plant = contains_phrase(info_text, NATURAL_PLANT_KEYWORDS)
    has_synthetic = contains_phrase(info_text, SYNTHETIC_KEYWORDS)
    if has_plant or has_synthetic:
        return "Yes"

    return "Unknown"


def classify_vegetarian(
    e_number: str,
    info_text: str,
    web_data: dict | None = None,
) -> str:
    """Classify lacto-vegetarian status (dairy OK, eggs NOT OK).

    Returns 'Yes', 'No', 'Maybe', or 'Unknown'.
    """
    # Tier 1: Known lookup
    if e_number in KNOWN_CLASSIFICATIONS:
        return KNOWN_CLASSIFICATIONS[e_number]["vegetarian"]

    # Tier 3: Web data
    if web_data and e_number in web_data:
        veg = web_data[e_number].get("vegetarian")
        if veg:
            return veg

    if not info_text or len(info_text.strip()) < 20:
        return "Unknown"

    # Tier 2: Keyword analysis
    if contains_phrase(info_text, AMBIGUOUS_ORIGIN_KEYWORDS):
        return "Maybe"

    # Animal killing required -> not vegetarian
    if contains_animal_keyword(info_text, NON_VEGETARIAN_KEYWORDS):
        return "No"

    # Eggs -> not lacto-vegetarian
    if contains_phrase(info_text, EGG_KEYWORDS):
        return "No"

    # Dairy and bee products are OK for lacto-vegetarian
    if contains_phrase(info_text, DAIRY_KEYWORDS):
        return "Yes"

    if contains_phrase(info_text, BEE_KEYWORDS):
        return "Yes"

    has_plant = contains_phrase(info_text, NATURAL_PLANT_KEYWORDS)
    has_synthetic = contains_phrase(info_text, SYNTHETIC_KEYWORDS)
    if has_plant or has_synthetic:
        return "Yes"

    return "Unknown"


def classify_safety(
    e_number: str,
    info_text: str,
    web_data: dict | None = None,
) -> str:
    """Classify safety level. Returns 'Safe', 'Caution', 'Avoid', 'Banned', or 'Unknown'."""
    # Tier 1: Known lookup
    if e_number in KNOWN_CLASSIFICATIONS:
        known_safety = KNOWN_CLASSIFICATIONS[e_number].get("safety")
        if known_safety:
            return known_safety

    # Tier 3: Web data
    if web_data and e_number in web_data:
        safety = web_data[e_number].get("safety")
        if safety:
            return safety

    if not info_text or len(info_text.strip()) < 20:
        return "Unknown"

    # Tier 2: Keyword analysis
    # Check safe phrases first - "no side effects" must override "side effect"
    if contains_phrase(info_text, SAFETY_SAFE_KEYWORDS):
        return "Safe"

    if contains_phrase(info_text, SAFETY_BANNED_KEYWORDS):
        return "Banned"

    if contains_phrase(info_text, SAFETY_AVOID_KEYWORDS):
        return "Avoid"

    if contains_phrase(info_text, SAFETY_CAUTION_KEYWORDS):
        return "Caution"

    return "Unknown"


def classify_origin(e_number: str, info_text: str) -> str:
    """Classify origin. Returns one of:
    'Synthetic', 'Natural (Plant)', 'Natural (Animal)',
    'Natural (Mineral)', 'Mixed', 'Unknown'.
    """
    # Tier 1: Known lookup
    if e_number in KNOWN_CLASSIFICATIONS:
        return KNOWN_CLASSIFICATIONS[e_number]["origin"]

    if not info_text or len(info_text.strip()) < 20:
        return "Unknown"

    has_synthetic = contains_phrase(info_text, SYNTHETIC_KEYWORDS)
    has_plant = contains_phrase(info_text, NATURAL_PLANT_KEYWORDS)
    has_animal = contains_animal_keyword(info_text, NATURAL_ANIMAL_KEYWORDS)
    has_mineral = contains_phrase(info_text, NATURAL_MINERAL_KEYWORDS)

    sources = sum([has_synthetic, has_plant, has_animal, has_mineral])

    if sources > 1:
        return "Mixed"
    if has_synthetic:
        return "Synthetic"
    if has_plant:
        return "Natural (Plant)"
    if has_animal:
        return "Natural (Animal)"
    if has_mineral:
        return "Natural (Mineral)"

    return "Unknown"


def classify_all(
    e_number: str,
    info_text: str,
    web_data: dict | None = None,
) -> dict[str, str | None]:
    """Run all classifiers on an additive. Returns dict of classification results."""
    return {
        "vegan_status": classify_vegan(e_number, info_text, web_data),
        "vegetarian_status": classify_vegetarian(e_number, info_text, web_data),
        "safety_level": classify_safety(e_number, info_text, web_data),
        "origin": classify_origin(e_number, info_text),
        "adi": extract_adi(info_text),
    }
