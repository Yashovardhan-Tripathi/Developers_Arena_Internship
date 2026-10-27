"""
Unit tests for the Calculator module.
File: tests/test_calculator.py
"""

import pytest
from calculator import (
    add,
    subtract,
    multiply,
    divide,
    modulus,
    power,
    evaluate_expression,
)


class TestBasicArithmetic:
    """Test core math functions."""

    def test_add(self):
        assert add(10, 5) == 15
        assert add(-4, 9) == 5
        assert add(2.5, 3.5) == 6.0

    def test_subtract(self):
        assert subtract(10, 4) == 6
        assert subtract(5, 12) == -7
        assert subtract(5.5, 2.0) == 3.5

    def test_multiply(self):
        assert multiply(6, 7) == 42
        assert multiply(-3, 5) == -15
        assert multiply(2.5, 4) == 10.0

    def test_divide(self):
        assert divide(20, 4) == 5.0
        assert divide(7, 2) == 3.5
        assert divide(-9, 3) == -3.0

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            divide(10, 0)

    def test_modulus(self):
        assert modulus(10, 3) == 1
        assert modulus(20, 5) == 0

    def test_modulus_by_zero(self):
        with pytest.raises(ZeroDivisionError, match="divisor of zero"):
            modulus(10, 0)

    def test_power(self):
        assert power(2, 3) == 8
        assert power(5, 0) == 1
        assert power(4, 0.5) == 2.0
        assert power(2, -1) == 0.5

    def test_power_errors(self):
        with pytest.raises(ValueError, match="complex number"):
            power(-4, 0.5)
        with pytest.raises(ValueError, match="too large"):
            power(2, 20000)


class TestSafeExpressionEvaluator:
    """Test AST-based expression evaluation security and correctness."""

    def test_simple_eval(self):
        assert evaluate_expression("2 + 3") == 5
        assert evaluate_expression("10 - 4") == 6
        assert evaluate_expression("6 * 7") == 42
        assert evaluate_expression("20 / 4") == 5.0

    def test_operator_precedence(self):
        assert evaluate_expression("2 + 3 * 4") == 14
        assert evaluate_expression("(2 + 3) * 4") == 20
        assert evaluate_expression("100 - 5 * 10 + 2") == 52

    def test_nested_parentheses(self):
        assert evaluate_expression("((2 + 3) * (4 - 1)) + 5") == 20

    def test_unary_operators(self):
        assert evaluate_expression("-5 + 10") == 5
        assert evaluate_expression("+7 * -2") == -14

    def test_division_by_zero_in_expression(self):
        with pytest.raises(ZeroDivisionError):
            evaluate_expression("10 / (5 - 5)")

    def test_security_rejections(self):
        # Code injection attempts must fail safely
        with pytest.raises(ValueError):
            evaluate_expression("__import__('os').system('ls')")

        with pytest.raises(ValueError):
            evaluate_expression("eval('2 + 2')")

        with pytest.raises(ValueError):
            evaluate_expression("open('/etc/passwd')")

        with pytest.raises(ValueError):
            evaluate_expression("x = 5")

    def test_syntax_errors(self):
        with pytest.raises(ValueError):
            evaluate_expression("")
        with pytest.raises(ValueError):
            evaluate_expression("2 + * 3")
