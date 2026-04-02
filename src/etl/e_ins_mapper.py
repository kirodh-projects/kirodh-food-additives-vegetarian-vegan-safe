"""E-number to INS number cross-reference mapping."""

import re

from src.etl.normalizers import extract_numeric_base, normalize_e_code


def build_e_to_ins_map(
    e_index: list[dict],
    ins_index: list[dict],
    merged_records: list[dict],
) -> dict[str, str]:
    """Build mapping from E-number -> INS number.

    Strategy:
    1. Strip 'E' prefix from E-codes to get numeric base.
    2. Match against INS codes directly where numeric bases match.
    3. Use merged CSV as ground truth for variant mappings (E101a -> 101(i)).
    """
    ins_codes: set[str] = set()
    for rec in ins_index:
        code = rec.get("ins_code", "").strip()
        if code:
            ins_codes.add(code.lower())

    for rec in merged_records:
        code = rec.get("ins_code", "").strip()
        if code:
            ins_codes.add(code.lower())

    e_numbers: set[str] = set()
    for rec in e_index:
        e_num = rec.get("e_number", "").strip()
        if e_num:
            e_numbers.add(normalize_e_code(e_num))

    mapping: dict[str, str] = {}

    for e_num in e_numbers:
        numeric_base = extract_numeric_base(e_num).lower()

        # Direct match: E100 -> INS 100
        if numeric_base in ins_codes:
            mapping[e_num] = numeric_base
            continue

        # Try letter suffix -> parenthetical: E101a -> 101(i), E101b -> 101(ii)
        ins_variant = _map_suffix_to_parenthetical(numeric_base)
        if ins_variant and ins_variant in ins_codes:
            mapping[e_num] = ins_variant
            continue

        # Try stripping letter suffix for parent match: E160a -> 160
        base_number = re.match(r"(\d+)", numeric_base)
        if base_number:
            parent = base_number.group(1)
            if parent in ins_codes and parent != numeric_base:
                mapping[e_num] = parent

    return mapping


_SUFFIX_TO_ROMAN = {
    "a": "(i)", "b": "(ii)", "c": "(iii)", "d": "(iv)",
    "e": "(v)", "f": "(vi)", "g": "(vii)", "h": "(viii)",
}


def _map_suffix_to_parenthetical(numeric_base: str) -> str | None:
    """Map letter suffixes to parenthetical variants.

    '101a' -> '101(i)', '160b' -> '160(ii)', etc.
    """
    match = re.match(r"(\d+)([a-z])$", numeric_base)
    if not match:
        return None

    number = match.group(1)
    suffix = match.group(2)

    roman = _SUFFIX_TO_ROMAN.get(suffix)
    if roman:
        return f"{number}{roman}"

    return None
