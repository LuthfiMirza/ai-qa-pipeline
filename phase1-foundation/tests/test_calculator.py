import pytest

from src.calculator import add, divide, multiply, subtract


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-2, -3) == -5


def test_add_mixed_sign_numbers():
    assert add(-2, 3) == 1


def test_subtract_positive_numbers():
    assert subtract(10, 4) == 6


def test_subtract_result_negative():
    assert subtract(4, 10) == -6


def test_multiply_positive_numbers():
    assert multiply(6, 7) == 42


def test_multiply_by_zero():
    assert multiply(99, 0) == 0


def test_multiply_negative_number():
    assert multiply(-5, 4) == -20


def test_divide_positive_numbers():
    assert divide(20, 5) == 4


def test_divide_returns_float_for_fraction():
    assert divide(5, 2) == 2.5


def test_divide_negative_number():
    assert divide(-12, 3) == -4


def test_divide_by_zero_raises_value_error():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
