"""Math expression parser and evaluator.

This module implements a hand-written recursive-descent parser for
arithmetic expressions.  It supports:

  * the four basic operators: + - * /
  * parentheses for grouping
  * unary plus / minus (e.g. -5, 3 * -2, +8)
  * decimal numbers

Design notes:
  * ``eval`` / ``exec`` (or any other arbitrary code execution) are
    intentionally NOT used: the expression is tokenized and parsed by
    hand so that only well-formed arithmetic expressions can be
    evaluated.
  * The parser follows the classic grammar:

        expression := term (('+' | '-') term)*
        term       := factor (('*' | '/') factor)*
        factor     := ('+' | '-') factor | NUMBER | '(' expression ')'

  * A character whitelist check is applied before parsing as a second
    line of defence against unexpected input.
"""

from __future__ import annotations

import re
from typing import List, Union

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class InvalidExpressionError(ValueError):
    """Raised when the expression is syntactically invalid."""


class DivisionByZeroError(ArithmeticError):
    """Raised when an expression divides a number by zero."""


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

# Only digits, operators, parentheses, dots and spaces are accepted.
_ALLOWED_CHARS = re.compile(r"^[0-9+\-*/().\s]+$")
_MAX_EXPRESSION_LENGTH = 200

_TOKEN_NUMBER = "NUMBER"
_TOKEN_PLUS = "PLUS"
_TOKEN_MINUS = "MINUS"
_TOKEN_TIMES = "TIMES"
_TOKEN_DIVIDE = "DIVIDE"
_TOKEN_LPAREN = "LPAREN"
_TOKEN_RPAREN = "RPAREN"
_TOKEN_END = "END"

_NUMBER_RE = re.compile(r"\d+(\.\d+)?")


class _Token:
    """A single lexical token."""

    def __init__(self, kind: str, value: Union[str, float]) -> None:
        self.kind = kind
        self.value = value

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"_Token({self.kind}, {self.value!r})"


def _tokenize(expression: str) -> List[_Token]:
    """Convert the raw expression string into a list of tokens."""
    if not expression or not expression.strip():
        raise InvalidExpressionError("Empty expression")
    if len(expression) > _MAX_EXPRESSION_LENGTH:
        raise InvalidExpressionError("Expression is too long")
    if not _ALLOWED_CHARS.match(expression):
        raise InvalidExpressionError("Expression contains unsupported characters")

    tokens: List[_Token] = []
    index = 0
    length = len(expression)

    while index < length:
        char = expression[index]
        if char.isspace():
            index += 1
            continue
        if char.isdigit():
            match = _NUMBER_RE.match(expression, index)
            if match is None:  # pragma: no cover - defensive
                raise InvalidExpressionError(f"Unexpected character at position {index}")
            tokens.append(_Token(_TOKEN_NUMBER, float(match.group())))
            index = match.end()
            continue
        mapping = {
            "+": _TOKEN_PLUS,
            "-": _TOKEN_MINUS,
            "*": _TOKEN_TIMES,
            "/": _TOKEN_DIVIDE,
            "(": _TOKEN_LPAREN,
            ")": _TOKEN_RPAREN,
        }
        kind = mapping.get(char)
        if kind is None:
            raise InvalidExpressionError(f"Unexpected character '{char}' at position {index}")
        tokens.append(_Token(kind, char))
        index += 1

    tokens.append(_Token(_TOKEN_END, None))
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser + evaluator
# ---------------------------------------------------------------------------

class _Parser:
    """Recursive-descent parser that evaluates the expression on the fly."""

    def __init__(self, tokens: List[_Token]) -> None:
        self._tokens = tokens
        self._position = 0

    # -- token helpers ------------------------------------------------------

    def _peek(self) -> _Token:
        return self._tokens[self._position]

    def _advance(self) -> _Token:
        token = self._tokens[self._position]
        self._position += 1
        return token

    def _expect(self, kind: str) -> _Token:
        token = self._peek()
        if token.kind != kind:
            raise InvalidExpressionError(f"Expected {kind} but found {token.kind}")
        return self._advance()

    def _accept(self, kind: str) -> Union[_Token, None]:
        if self._peek().kind == kind:
            return self._advance()
        return None

    # -- grammar rules ------------------------------------------------------

    def parse(self) -> float:
        """Parse the whole token stream and return the numeric result."""
        result = self._expression()
        if self._peek().kind != _TOKEN_END:
            raise InvalidExpressionError(
                f"Unexpected trailing token {self._peek().kind}"
            )
        return result

    def _expression(self) -> float:
        """expression := term (('+' | '-') term)*"""
        value = self._term()
        while True:
            if self._accept(_TOKEN_PLUS):
                value = value + self._term()
            elif self._accept(_TOKEN_MINUS):
                value = value - self._term()
            else:
                return value

    def _term(self) -> float:
        """term := factor (('*' | '/') factor)*"""
        value = self._factor()
        while True:
            if self._accept(_TOKEN_TIMES):
                value = value * self._factor()
            elif self._accept(_TOKEN_DIVIDE):
                divisor = self._factor()
                if divisor == 0:
                    raise DivisionByZeroError("Division by zero")
                value = value / divisor
            else:
                return value

    def _factor(self) -> float:
        """factor := ('+' | '-') factor | NUMBER | '(' expression ')'"""
        if self._accept(_TOKEN_PLUS):
            return self._factor()
        if self._accept(_TOKEN_MINUS):
            return -self._factor()
        if self._peek().kind == _TOKEN_NUMBER:
            return float(self._advance().value)
        if self._accept(_TOKEN_LPAREN):
            value = self._expression()
            self._expect(_TOKEN_RPAREN)
            return value
        raise InvalidExpressionError(f"Unexpected token {self._peek().kind}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _format_number(value: float) -> str:
    """Format the result, removing unnecessary floating-point noise.

    Examples:
        3.0   -> "3"
        2.5   -> "2.5"
        0.3   -> "0.3"   (0.1 + 0.2 rounded to 10 digits)
    """
    rounded = round(value, 10)
    if rounded == int(rounded):
        return str(int(rounded))
    return str(rounded)


def calculate(expression: str) -> str:
    """Evaluate an arithmetic expression string.

    Args:
        expression: the raw expression, e.g. "(1+2)*3".

    Returns:
        The formatted result as a string, e.g. "9".

    Raises:
        InvalidExpressionError: if the expression is not well formed.
        DivisionByZeroError: if the expression divides by zero.
    """
    tokens = _tokenize(expression)
    value = _Parser(tokens).parse()
    return _format_number(value)
