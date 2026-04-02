"""Tests for vegan/vegetarian/safety/origin classification logic."""

import pytest

from src.etl.classifiers import (
    classify_origin,
    classify_safety,
    classify_vegan,
    classify_vegetarian,
)


class TestClassifyVegan:
    def test_known_vegan(self):
        assert classify_vegan("E100", "") == "Yes"

    def test_known_non_vegan_insect(self):
        assert classify_vegan("E120", "") == "No"

    def test_known_non_vegan_gelatin(self):
        assert classify_vegan("E428", "") == "No"

    def test_known_maybe(self):
        assert classify_vegan("E471", "") == "Maybe"

    def test_info_animal_keywords(self, sample_info_texts):
        result = classify_vegan("E9999", sample_info_texts["E1100"])
        assert result == "No"

    def test_info_ambiguous_origin(self, sample_info_texts):
        result = classify_vegan("E9999", sample_info_texts["E471_ambiguous"])
        assert result == "Maybe"

    def test_info_synthetic_is_vegan(self, sample_info_texts):
        result = classify_vegan("E9999", sample_info_texts["E102"])
        assert result == "Yes"

    def test_info_dairy_not_vegan(self, sample_info_texts):
        result = classify_vegan("E9999", sample_info_texts["E966_dairy"])
        assert result == "No"

    def test_info_egg_not_vegan(self, sample_info_texts):
        result = classify_vegan("E9999", sample_info_texts["E1105_egg"])
        assert result == "No"

    def test_short_info_returns_unknown(self, sample_info_texts):
        result = classify_vegan("E9999", sample_info_texts["short_info"])
        assert result == "Unknown"

    def test_empty_info_returns_unknown(self):
        result = classify_vegan("E9999", "")
        assert result == "Unknown"

    def test_lab_animals_not_false_positive(self, sample_info_texts):
        """'laboratory animals' should NOT trigger non-vegan classification."""
        result = classify_vegan("E9999", sample_info_texts["lab_animals"])
        assert result == "Yes"  # synthetic origin -> vegan

    def test_web_data_fallback(self):
        web_data = {"E9999": {"vegan": "No"}}
        result = classify_vegan("E9999", "", web_data)
        assert result == "No"


class TestClassifyVegetarian:
    def test_known_vegetarian(self):
        assert classify_vegetarian("E100", "") == "Yes"

    def test_known_not_vegetarian_insect(self):
        """Insects killed -> not vegetarian."""
        assert classify_vegetarian("E120", "") == "No"

    def test_known_not_vegetarian_egg(self):
        """Eggs -> not lacto-vegetarian."""
        assert classify_vegetarian("E1105", "") == "No"

    def test_known_dairy_is_vegetarian(self):
        """Dairy products -> lacto-vegetarian OK."""
        assert classify_vegetarian("E966", "") == "Yes"

    def test_known_beeswax_is_vegetarian(self):
        """Bee products -> vegetarian OK (no killing)."""
        assert classify_vegetarian("E901", "") == "Yes"

    def test_info_egg_not_vegetarian(self, sample_info_texts):
        result = classify_vegetarian("E9999", sample_info_texts["E1105_egg"])
        assert result == "No"

    def test_info_dairy_is_vegetarian(self, sample_info_texts):
        result = classify_vegetarian("E9999", sample_info_texts["E966_dairy"])
        assert result == "Yes"

    def test_info_animal_killing_not_vegetarian(self, sample_info_texts):
        result = classify_vegetarian("E9999", sample_info_texts["E1100"])
        assert result == "No"

    def test_info_synthetic_is_vegetarian(self, sample_info_texts):
        result = classify_vegetarian("E9999", sample_info_texts["E102"])
        assert result == "Yes"

    def test_ambiguous_is_maybe(self, sample_info_texts):
        result = classify_vegetarian("E9999", sample_info_texts["E471_ambiguous"])
        assert result == "Maybe"


class TestClassifySafety:
    def test_known_safe(self):
        assert classify_safety("E100", "") == "Safe"

    def test_known_caution(self):
        assert classify_safety("E102", "") == "Caution"

    def test_known_avoid(self):
        assert classify_safety("E104", "") == "Avoid"

    def test_info_banned(self, sample_info_texts):
        result = classify_safety("E9999", sample_info_texts["E128_banned"])
        assert result == "Banned"

    def test_info_carcinogenic(self, sample_info_texts):
        result = classify_safety("E9999", sample_info_texts["E104_carcinogenic"])
        assert result == "Avoid"

    def test_info_safe(self, sample_info_texts):
        result = classify_safety("E9999", sample_info_texts["E300"])
        assert result == "Safe"

    def test_short_info_unknown(self, sample_info_texts):
        result = classify_safety("E9999", sample_info_texts["short_info"])
        assert result == "Unknown"


class TestClassifyOrigin:
    def test_known_plant(self):
        assert classify_origin("E100", "") == "Natural (Plant)"

    def test_known_synthetic(self):
        assert classify_origin("E102", "") == "Synthetic"

    def test_known_animal(self):
        assert classify_origin("E120", "") == "Natural (Animal)"

    def test_known_mineral(self):
        assert classify_origin("E170", "") == "Natural (Mineral)"

    def test_known_mixed(self):
        assert classify_origin("E471", "") == "Mixed"

    def test_info_mineral(self, sample_info_texts):
        result = classify_origin("E9999", sample_info_texts["E170"])
        assert result == "Natural (Mineral)"

    def test_info_synthetic(self, sample_info_texts):
        result = classify_origin("E9999", sample_info_texts["E102"])
        assert result == "Synthetic"

    def test_short_info_unknown(self, sample_info_texts):
        result = classify_origin("E9999", sample_info_texts["short_info"])
        assert result == "Unknown"
