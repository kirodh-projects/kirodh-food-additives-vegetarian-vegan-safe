"""Tests for species trait heuristics (pure functions, no DB needed)."""

from src.species.traits import (
    build_trait_update_sql,
    compute_gunas,
    compute_mobility,
    compute_size,
    compute_warm_blood,
)


class TestPhysicalTraits:
    def test_mammal_mobile_and_warm(self):
        assert compute_mobility("Animalia", "Chordata", "Mammalia", "") == 0.85
        assert compute_warm_blood("Animalia", "Chordata", "Mammalia", "") == 0.95

    def test_plants_sessile_and_cold(self):
        assert compute_mobility("Plantae", "Tracheophyta", "Magnoliopsida", "") == 0.0
        assert compute_warm_blood("Plantae", "Tracheophyta", "Magnoliopsida", "") == 0.0

    def test_order_overrides_class(self):
        # Lamniformes (great white sharks) override Elasmobranchii mobility
        assert compute_mobility("Animalia", "Chordata", "Elasmobranchii", "Lamniformes") == 0.90

    def test_unknown_defaults(self):
        assert compute_mobility("", "", "", "") == 0.25
        assert compute_warm_blood("", "", "", "") == 0.0
        assert compute_size("", "", "", "") == 0.10


class TestGunas:
    def test_gunas_sum_to_one(self):
        for args in [
            ("Animalia", "Chordata", "Mammalia", "Carnivora"),
            ("Plantae", "Tracheophyta", "Magnoliopsida", ""),
            ("Fungi", "Basidiomycota", "Agaricomycetes", ""),
            ("", "", "", ""),
        ]:
            sattva, rajas, tamas = compute_gunas(*args)
            assert abs(sattva + rajas + tamas - 1.0) < 1e-9

    def test_carnivora_rajasic(self):
        sattva, rajas, tamas = compute_gunas("Animalia", "Chordata", "Mammalia", "Carnivora")
        assert rajas > sattva
        assert rajas > tamas

    def test_flowering_plants_sattvic(self):
        sattva, rajas, tamas = compute_gunas("Plantae", "Tracheophyta", "Magnoliopsida", "")
        assert sattva > rajas
        assert sattva > tamas


class TestTraitSql:
    def test_update_sql_sets_all_columns(self):
        sql = build_trait_update_sql()
        for col in (
            "mobility_score",
            "warm_blood_score",
            "size_score",
            "purity_score",
            "passion_score",
            "ignorance_score",
        ):
            assert col in sql
        assert sql.strip().upper().startswith("UPDATE SPECIES SET")
