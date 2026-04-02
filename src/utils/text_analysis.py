"""Text analysis utilities for keyword-based classification."""

import re

from src.utils.constants import ANIMAL_CONTEXT_EXCLUSIONS, ADI_PATTERNS


def contains_phrase(
    text: str,
    keywords: list[str],
    exclusions: list[str] | None = None,
) -> bool:
    """Check if text contains any of the keyword phrases.

    Uses multi-word phrase matching to reduce false positives.
    Applies context exclusions to avoid misclassifying phrases like
    'laboratory animals' as indicating animal origin.
    """
    if not text:
        return False

    text_lower = text.lower()

    if exclusions:
        for excl in exclusions:
            text_lower = text_lower.replace(excl.lower(), "")

    return any(kw.lower() in text_lower for kw in keywords)


def contains_animal_keyword(text: str, keywords: list[str]) -> bool:
    """Check for animal-related keywords while excluding test/study contexts."""
    return contains_phrase(text, keywords, exclusions=ANIMAL_CONTEXT_EXCLUSIONS)


def extract_adi(info_text: str) -> str | None:
    """Extract Acceptable Daily Intake from info text if present."""
    if not info_text:
        return None

    for pattern in ADI_PATTERNS:
        match = re.search(pattern, info_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None
