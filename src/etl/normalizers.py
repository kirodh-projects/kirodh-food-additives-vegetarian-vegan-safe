"""Data normalization: E-code standardization, category mapping, deduplication."""

import re

from src.utils.constants import CATEGORY_MAP


def normalize_e_code(raw_code: str) -> str:
    """Normalize E-code to canonical form.

    Examples:
        'E100' -> 'E100'
        'e100' -> 'E100'
        '100'  -> 'E100'
        'E160A' -> 'E160a'
        'E101a' -> 'E101a'
    """
    code = raw_code.strip()

    if not code.upper().startswith("E"):
        code = "E" + code

    match = re.match(r"(E)(\d+)(.*)", code, re.IGNORECASE)
    if not match:
        return code.upper()

    prefix = "E"
    number = match.group(2)
    suffix = match.group(3).lower().strip()

    return f"{prefix}{number}{suffix}"


def extract_numeric_base(e_code: str) -> str:
    """Extract the normalized form without 'E' prefix.

    'E100' -> '100', 'E160a' -> '160a', 'E100(i)' -> '100(i)'
    """
    code = normalize_e_code(e_code)
    if code.startswith("E"):
        return code[1:]
    return code


def normalize_category(raw_type: str) -> str:
    """Map raw e_type values to canonical categories.

    Handles compound types by taking the first component.
    """
    if not raw_type or not raw_type.strip():
        return "Unknown"

    raw = raw_type.strip()

    raw_lower = raw.lower().strip()
    if raw_lower in CATEGORY_MAP:
        return CATEGORY_MAP[raw_lower]

    for sep in [" - ", " – ", ", ", " / "]:
        if sep in raw:
            first_part = raw.split(sep)[0].strip().lower()
            if first_part in CATEGORY_MAP:
                return CATEGORY_MAP[first_part]

    for key, value in CATEGORY_MAP.items():
        if key in raw_lower:
            return value

    return raw.title()


def normalize_halal_status(raw: str) -> str:
    """Standardize halal status values."""
    if not raw or not raw.strip():
        return "Unknown"

    val = raw.strip().lower()
    if val in ("halal", "yes"):
        return "Halal"
    if val in ("doubtful", "mushbooh", "maybe"):
        return "Doubtful"
    if val in ("haram", "no"):
        return "Haram"
    return "Unknown"


def normalize_ins_code(raw_code: str) -> str:
    """Normalize INS code: strip spaces, lowercase suffixes.

    '100' -> '100', '160a' -> '160a', '100(i)' -> '100(i)'
    """
    return raw_code.strip().lower() if raw_code else ""


def deduplicate_records(records: list[dict]) -> list[dict]:
    """Merge records by e_number, preferring records with richer info."""
    seen: dict[str, dict] = {}

    for record in records:
        e_num = record.get("e_number", "")
        if not e_num:
            continue

        if e_num not in seen:
            seen[e_num] = record
        else:
            existing = seen[e_num]
            existing_info_len = len(existing.get("description", "") or "")
            new_info_len = len(record.get("description", "") or "")

            if new_info_len > existing_info_len:
                for key, value in record.items():
                    if value and (not existing.get(key)):
                        existing[key] = value
                if new_info_len > existing_info_len:
                    existing["description"] = record["description"]
            else:
                for key, value in record.items():
                    if value and (not existing.get(key)):
                        existing[key] = value

    return list(seen.values())
