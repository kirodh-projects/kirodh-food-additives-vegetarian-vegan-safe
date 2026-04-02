"""Tests for E-number to INS number mapping."""

from src.etl.e_ins_mapper import build_e_to_ins_map, _map_suffix_to_parenthetical


class TestMapSuffixToParenthetical:
    def test_a_to_i(self):
        assert _map_suffix_to_parenthetical("101a") == "101(i)"

    def test_b_to_ii(self):
        assert _map_suffix_to_parenthetical("101b") == "101(ii)"

    def test_c_to_iii(self):
        assert _map_suffix_to_parenthetical("160c") == "160(iii)"

    def test_no_suffix(self):
        assert _map_suffix_to_parenthetical("100") is None

    def test_parenthetical_input(self):
        assert _map_suffix_to_parenthetical("100(i)") is None


class TestBuildEToInsMap:
    def test_direct_mapping(self):
        e_index = [{"e_number": "E100"}]
        ins_index = [{"ins_code": "100"}]
        merged = []

        result = build_e_to_ins_map(e_index, ins_index, merged)
        assert result.get("E100") == "100"

    def test_suffix_mapping(self):
        e_index = [{"e_number": "E101a"}]
        ins_index = [{"ins_code": "101(i)"}]
        merged = []

        result = build_e_to_ins_map(e_index, ins_index, merged)
        assert result.get("E101a") == "101(i)"

    def test_unmapped_returns_none(self):
        e_index = [{"e_number": "E999"}]
        ins_index = [{"ins_code": "100"}]
        merged = []

        result = build_e_to_ins_map(e_index, ins_index, merged)
        assert result.get("E999") is None

    def test_multiple_mappings(self):
        e_index = [
            {"e_number": "E100"},
            {"e_number": "E200"},
            {"e_number": "E300"},
        ]
        ins_index = [
            {"ins_code": "100"},
            {"ins_code": "200"},
        ]
        merged = [{"ins_code": "300"}]

        result = build_e_to_ins_map(e_index, ins_index, merged)
        assert result.get("E100") == "100"
        assert result.get("E200") == "200"
        assert result.get("E300") == "300"
