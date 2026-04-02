"""Shared test fixtures."""

import sqlite3

import pytest

from src.db.schema import create_tables


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database with the schema applied."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    yield conn
    conn.close()


@pytest.fixture
def populated_db(in_memory_db):
    """In-memory database populated with sample additive records."""
    sample_records = [
        ("E100", "100", "", "Curcumin / Turmeric", "", "Colouring", "yellows",
         "Curcumin is the main yellow-orange pigment of turmeric.",
         "Halal", "Yes", "Yes", "Safe", "Natural (Plant)", None, 1, 0, 1, 0, "test"),
        ("E120", "120", "", "Cochineal", "", "Colouring", "reds",
         "Obtained from crushed cochineal insects.",
         "Halal", "No", "No", "Safe", "Natural (Animal)", None, 1, 0, 1, 0, "test"),
        ("E102", "102", "", "Tartrazine", "", "Colouring", "yellows",
         "E102 gives a yellow color. Synthetic azo dye.",
         "Halal", "Yes", "Yes", "Caution", "Synthetic", None, 1, 1, 1, 0, "test"),
        ("E428", None, "", "Gelatin", "", "Thickener", "",
         "Gelatin from animal bones and hides.",
         "Doubtful", "No", "No", "Safe", "Natural (Animal)", None, 1, 0, 0, 0, "test"),
        ("E901", None, "", "Beeswax", "", "Glazing Agent", "waxes",
         "Beeswax, white and yellow. Produced by bees.",
         "Halal", "No", "Yes", "Safe", "Natural (Animal)", None, 1, 0, 0, 0, "test"),
        ("E104", None, "", "Quinoline Yellow", "", "Colouring", "",
         "Potentially carcinogenic. Synthetic. Neurotoxic.",
         "Halal", "Yes", "Yes", "Avoid", "Synthetic", None, 1, 0, 0, 0, "test"),
        ("E128", None, "", "Red 2G", "", "Colouring", "",
         "Banned in the EU. Synthetic azo dye. Carcinogenic.",
         "Halal", "Yes", "Yes", "Banned", "Synthetic", None, 0, 0, 0, 1, "test"),
        ("E471", None, "", "Mono- and diglycerides", "", "Emulsifier", "",
         "Can be from animal or vegetable origin. Glycerides of fatty acids.",
         "Doubtful", "Maybe", "Maybe", "Safe", "Mixed", None, 1, 0, 1, 0, "test"),
        ("E966", None, "", "Lactitol", "", "Sweetener", "",
         "Derived from lactose (milk sugar).",
         "Halal", "No", "Yes", "Safe", "Natural (Animal)", None, 1, 0, 0, 0, "test"),
        ("E1105", None, "", "Lysozyme", "", "Preservative", "",
         "From egg whites. Used as preservative.",
         "Doubtful", "No", "No", "Safe", "Natural (Animal)", None, 1, 0, 0, 0, "test"),
    ]

    for rec in sample_records:
        in_memory_db.execute("""
            INSERT INTO additives (
                e_number, ins_number, chemical_name, common_name,
                alternative_names, category, subcategory, description,
                halal_status, vegan_status, vegetarian_status, safety_level,
                origin, adi, approval_eu, approval_us, approval_codex,
                is_banned_anywhere, source_files
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rec)

    in_memory_db.commit()
    yield in_memory_db


@pytest.fixture
def sample_info_texts() -> dict[str, str]:
    """Sample info texts for classification testing."""
    return {
        "E100": "Curcumin is the main yellow-orange pigment of turmeric powder. It is used as a natural coloring agent.",
        "E120": "Obtained from crushed cochineal insects. The dye is used in food products.",
        "E1100": "The origin of this additive is the pancreas of pigs, green mold and genetic engineering.",
        "E1000": "Extract of cow bile, can be produced synthetically. Part of the bile of vertebrates.",
        "E471_ambiguous": "Can be of animal or vegetable origin. Mono- and diglycerides of fatty acids.",
        "E102": "It is used as a synthetic coloring agent. E102 gives a yellow color. Azo dye.",
        "E104_carcinogenic": "It is a synthetic substance, carcinogenic. Neurotoxic. Produced artificially from petrochemical.",
        "E128_banned": "Banned in the EU. It could be carcinogenic. Synthetic azo dye.",
        "E300": "Ascorbic acid (Vitamin C). No side effects have been found. Can be from fruit or synthetic.",
        "E170": "Calcium carbonate is a mineral. Limestone or chalk. No known side effects.",
        "short_info": "Yellow-orange",
        "lab_animals": "Tested on laboratory animals. No carcinogenic effects observed in animals. Synthetic origin.",
        "E966_dairy": "Derived from lactose which is a milk sugar. Used as sweetener.",
        "E1105_egg": "Lysozyme from egg whites. Natural enzyme used as preservative.",
    }
