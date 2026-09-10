"""Tests for reverse-subtraction core logic."""

from src.numbers.reverse_subtraction import compute_reverse_subtraction, reverse_number


class TestReverseNumber:
    def test_single_digit(self):
        assert reverse_number(8) == 8

    def test_two_digits(self):
        assert reverse_number(21) == 12

    def test_trailing_zero(self):
        assert reverse_number(100) == 1

    def test_negative(self):
        assert reverse_number(-21) == -12

    def test_zero(self):
        assert reverse_number(0) == 0


class TestComputeReverseSubtraction:
    def test_known_values(self):
        xs, ys = compute_reverse_subtraction(21, 21)
        assert xs == [21]
        assert ys == [9]

    def test_palindromes_give_zero(self):
        xs, ys = compute_reverse_subtraction(1, 9)
        assert all(y == 0 for y in ys)

    def test_range_length(self):
        xs, ys = compute_reverse_subtraction(1, 200)
        assert len(xs) == 200
        assert len(ys) == 200
        # 100 -> 100 - 1 = 99
        assert ys[xs.index(100)] == 99

    def test_negative_range(self):
        xs, ys = compute_reverse_subtraction(-21, -21)
        assert ys == [-9]
