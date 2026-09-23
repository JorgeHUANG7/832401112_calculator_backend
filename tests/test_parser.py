"""Unit tests for the expression parser and evaluator.

Run with::

    python -m pytest tests/ -v
    # or, without pytest:
    python tests/test_parser.py
"""

from __future__ import annotations

import unittest

from app.parser import (
    DivisionByZeroError,
    InvalidExpressionError,
    calculate,
)


class CalculateTest(unittest.TestCase):
    """Test basic arithmetic, precedence, parentheses and unary signs."""

    CASES = [
        # (expression, expected)
        ("12+8", "20"),
        ("12 + 8", "20"),
        ("1+2*3", "7"),
        ("(1+2)*3", "9"),
        ("10/2+7", "12"),
        ("8-3*2", "2"),
        ("-5+8", "3"),
        ("3*-2", "-6"),
        ("2.5*2", "5"),
        ("0.1+0.2", "0.3"),
        ("(2+3)*4", "20"),
        ("100/4/5", "5"),
        ("((1+2)*(3+4))", "21"),
        ("-(-5)", "5"),
        ("--5", "5"),
        ("2*(3+4*(5-1))", "38"),
        ("7/2", "3.5"),
        ("0*999", "0"),
        ("-0.5+1.5", "1"),
        ("  1  +   2  ", "3"),
    ]

    def test_expected_results(self) -> None:
        for expression, expected in self.CASES:
            with self.subTest(expression=expression):
                self.assertEqual(calculate(expression), expected)

    def test_invalid_expressions(self) -> None:
        invalid = [
            "",
            "   ",
            "1+",
            "+",
            "*3",
            "(1+2",
            "1+2)",
            "()",
            "1++*2",
            "a+1",
            "1+2;rm -rf /",
            "1..2",
            "1 2 3",
            "((1+2)",
        ]
        for expression in invalid:
            with self.subTest(expression=expression):
                with self.assertRaises(InvalidExpressionError):
                    calculate(expression)

    def test_division_by_zero(self) -> None:
        for expression in ("1/0", "1/(3-3)", "5/(2-2)", "1/0+"):
            with self.subTest(expression=expression):
                with self.assertRaises(DivisionByZeroError):
                    calculate(expression)

    def test_very_long_expression_is_rejected(self) -> None:
        with self.assertRaises(InvalidExpressionError):
            calculate("1" * 300 + "+1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
