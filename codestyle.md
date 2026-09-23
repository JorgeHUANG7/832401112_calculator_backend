# Code Style — Calculator Backend (Python)

## Source of the standard

This document is derived from the following official / widely recognised
standards:

1. **PEP 8 — Style Guide for Python Code**
   https://peps.python.org/pep-0008/
2. **Google Python Style Guide**
   https://google.github.io/styleguide/pyguide.html
3. **PEP 257 — Docstring Conventions**
   https://peps.python.org/pep-0257/

The rules below are the subset that this project actually follows; when a
topic is not covered here, the PEP 8 / Google guide is the authority.

## 1. Formatting

- **Indentation**: 4 spaces per level. No tabs.
- **Line length**: at most 79 characters for code, 72 for docstrings
  (PEP 8 default); lines exceeding the limit must be wrapped with
  parentheses.
- **Blank lines**: two blank lines between top-level definitions
  (module-level classes/functions); one blank line between methods inside
  a class.
- **Trailing whitespace**: forbidden.
- **Quotes**: single quotes preferred for string literals unless the
  string contains a single quote.

## 2. Naming

| Category            | Convention    | Example                  |
|---------------------|---------------|--------------------------|
| Module / file       | `lowercase`   | `parser.py`, `database.py` |
| Class               | `CapWords`    | `HistoryRepository`, `CalculateRequest` |
| Function / method   | `snake_case`  | `calculate()`, `insert()`, `_tokenize()` |
| Variable            | `snake_case`  | `expression`, `record_id` |
| Constant            | `UPPER_CASE`  | `_MAX_EXPRESSION_LENGTH` |
| Private (module/method) | leading `_` | `_Token`, `_Parser`, `_initialize()` |

- Names must be descriptive; avoid single-letter names except for throw-away
  loop indexes.
- Use `from __future__ import annotations` when annotations are used.

## 3. Imports

- One import per line; group imports in the order:
  1. standard library
  2. third-party
  3. local application modules

  with one blank line between each group.

## 4. Functions and Docstrings

- Every public function and class has a docstring (PEP 257), describing:
  - what it does,
  - `Args:` — parameters,
  - `Returns:` — the return value,
  - `Raises:` — exceptions that may be raised.
- Type annotations are required for public functions
  (`def calculate(expression: str) -> str:`).

## 5. Error Handling

- Prefer raising **specific** custom exceptions
  (`InvalidExpressionError`, `DivisionByZeroError`) over bare `Exception`.
- Never silently swallow exceptions; log or re-raise when appropriate.

## 6. Comments

- Comments explain **why**, not what; the code itself should be
  self-explanatory.
- Use `#` followed by a space; separate comment blocks with blank lines
  where needed.

## 7. Class Design

- Each class has a single responsibility (SRP).
- Data classes (request/response models) are grouped in `schemas.py`.
- Repository access is isolated in `database.py`; business logic stays out
  of the API layer.

## 8. Anti-patterns to Avoid

- `eval()` / `exec()` / `compile()` on user input — **forbidden** in this
  project (the parser is hand-written).
- Global mutable state (only the module-level `repository` singleton is
  acceptable here).
- `except:` without an exception type.
- Long function bodies — split into smaller helper functions.
