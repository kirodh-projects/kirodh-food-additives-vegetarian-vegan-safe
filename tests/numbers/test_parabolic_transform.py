"""Tests for parabolic-transform core logic."""

import math

from src.numbers.parabolic_transform import (
    FUNCTIONS,
    arc_length,
    compute_transformed_function,
    transform_point,
    x_from_signed_arc,
)


class TestArcLength:
    def test_zero(self):
        assert arc_length(0) == 0

    def test_symmetry(self):
        assert arc_length(1.0) == -arc_length(-1.0)

    def test_monotonic(self):
        assert arc_length(2.0) > arc_length(1.0) > 0


class TestXFromSignedArc:
    def test_roundtrip_positive(self):
        s = arc_length(1.0)
        x = x_from_signed_arc(s, -2.0, 2.0)
        assert x is not None
        assert abs(x - 1.0) < 1e-6

    def test_roundtrip_negative(self):
        s = arc_length(-1.0)
        x = x_from_signed_arc(s, -2.0, 2.0)
        assert x is not None
        assert abs(x - (-1.0)) < 1e-6

    def test_out_of_range(self):
        assert x_from_signed_arc(1e9, -2.0, 2.0) is None


class TestTransformPoint:
    def test_vertex(self):
        pt = transform_point(1.0, 0.0, -2.0, 2.0)
        assert pt is not None
        assert pt[0] == 1.0
        assert pt[1] == 0.0

    def test_out_of_range(self):
        assert transform_point(0.0, 1e9, -2.0, 2.0) is None


class TestComputeTransformedFunction:
    def test_small_function_stays_in_range(self):
        new_x, new_y, skipped = compute_transformed_function(
            lambda x: 0.0, -2.0, 2.0, n_points=10
        )
        assert len(new_x) == 10
        assert skipped == []

    def test_large_function_skipped(self):
        new_x, new_y, skipped = compute_transformed_function(
            lambda x: 1e9, -2.0, 2.0, n_points=10
        )
        assert new_x == []
        assert len(skipped) == 10


class TestFunctions:
    def test_preset_functions_exist(self):
        assert "exp(-x^2)" in FUNCTIONS
        assert "sin(x)" in FUNCTIONS
        assert abs(FUNCTIONS["sin(x)"](0.0)) < 1e-12
        assert abs(FUNCTIONS["exp(-x^2)"](0.0) - 1.0) < 1e-12
        assert abs(FUNCTIONS["x^2"](3.0) - 9.0) < 1e-12
        assert abs(FUNCTIONS["tanh(x)"](0.0)) < 1e-12
        assert abs(FUNCTIONS["1/(1+x^2)"](0.0) - 1.0) < 1e-12
        assert math.isfinite(FUNCTIONS["2^x"](10.0))
