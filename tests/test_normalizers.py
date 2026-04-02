"""Tests for E-code normalization and category mapping."""

from src.etl.normalizers import (
    deduplicate_records,
    extract_numeric_base,
    normalize_category,
    normalize_e_code,
    normalize_halal_status,
)


class TestNormalizeECode:
    def test_already_normalized(self):
        assert normalize_e_code("E100") == "E100"

    def test_lowercase(self):
        assert normalize_e_code("e100") == "E100"

    def test_no_prefix(self):
        assert normalize_e_code("100") == "E100"

    def test_uppercase_suffix(self):
        assert normalize_e_code("E160A") == "E160a"

    def test_lowercase_suffix(self):
        assert normalize_e_code("E101a") == "E101a"

    def test_whitespace(self):
        assert normalize_e_code("  E100  ") == "E100"

    def test_mixed_case(self):
        assert normalize_e_code("e160B") == "E160b"


class TestExtractNumericBase:
    def test_simple(self):
        assert extract_numeric_base("E100") == "100"

    def test_with_suffix(self):
        assert extract_numeric_base("E160a") == "160a"

    def test_from_raw(self):
        assert extract_numeric_base("e100") == "100"


class TestNormalizeCategory:
    def test_coloring(self):
        assert normalize_category("Coloring") == "Colouring"

    def test_colour(self):
        assert normalize_category("Colour") == "Colouring"

    def test_compound_type(self):
        result = normalize_category("Stabiliser - Thickener")
        assert result == "Stabiliser"

    def test_empty(self):
        assert normalize_category("") == "Unknown"

    def test_whitespace(self):
        assert normalize_category("  preservative  ") == "Preservative"

    def test_yellow_orange_as_colouring(self):
        assert normalize_category("Yellow-orange") == "Colouring"

    def test_unknown_type_titlecased(self):
        result = normalize_category("Some New Type")
        assert result == "Some New Type"


class TestNormalizeHalalStatus:
    def test_halal(self):
        assert normalize_halal_status("Halal") == "Halal"

    def test_doubtful(self):
        assert normalize_halal_status("Doubtful") == "Doubtful"

    def test_empty(self):
        assert normalize_halal_status("") == "Unknown"

    def test_whitespace(self):
        assert normalize_halal_status("  halal  ") == "Halal"


class TestDeduplicateRecords:
    def test_no_duplicates(self):
        records = [
            {"e_number": "E100", "description": "Info", "common_name": "A"},
            {"e_number": "E200", "description": "Info", "common_name": "B"},
        ]
        result = deduplicate_records(records)
        assert len(result) == 2

    def test_prefers_richer_description(self):
        records = [
            {"e_number": "E100", "description": "Short", "common_name": "A"},
            {"e_number": "E100", "description": "A much longer and richer description", "common_name": "B"},
        ]
        result = deduplicate_records(records)
        assert len(result) == 1
        assert "longer" in result[0]["description"]

    def test_fills_missing_fields(self):
        records = [
            {"e_number": "E100", "description": "Long description text here", "common_name": "A", "category": None},
            {"e_number": "E100", "description": "Short", "common_name": "B", "category": "Colouring"},
        ]
        result = deduplicate_records(records)
        assert len(result) == 1
        assert result[0]["category"] == "Colouring"
