# Calculator Backend (前后端分离计算器 · 后端)

EE308FZ Software Engineering — Assignment 1: Front-End and Back-End
Separation Calculator System. This repository contains the **back end** of
the project: it receives calculation requests from the front end, parses
and evaluates the arithmetic expressions, stores every successful
calculation into the database, and serves the calculation history.

> The front end lives in a **separate repository**:
> https://github.com/JorgeHUANG7/832401112_calculator_frontend
>
> Deployed API (Render): https://calculator-backend-oaoe.onrender.com
> — health check at `/api/health`, interactive docs at `/docs`.

## Project Introduction

The back end is a RESTful API built with **FastAPI** (Python). It owns the
core calculation logic — the front end only sends the raw expression
string, and **all parsing and evaluation happen here**. A hand-written
recursive-descent parser is used; `eval` / `exec` are intentionally
forbidden.

Every successful calculation is persisted into a **SQLite** database, so
the history survives page refreshes and client restarts.

## Technology Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Language | Python 3.10+                      |
| Web      | FastAPI + Uvicorn                 |
| Database | SQLite (stdlib `sqlite3`)         |
| Validation | Pydantic v2                    |
| Tests    | `unittest` (stdlib)               |

SQLite is used so the project runs anywhere without a database server.
You can switch to MySQL/PostgreSQL by replacing the `HistoryRepository`
implementation in `app/database.py`.

## Directory Structure

```
calculator_backend/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app, CORS, API routes
│   ├── parser.py      # hand-written expression parser / evaluator
│   ├── database.py    # SQLite repository for calculation history
│   └── schemas.py     # Pydantic request/response models
├── tests/
│   └── test_parser.py # unit tests for the parser
├── requirements.txt
├── README.md
└── codestyle.md
```

## Runtime Environment

- Python 3.10 or newer (developed with Python 3.12)
- `pip` for installing dependencies

## Installation

```bash
cd calculator_backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Startup

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API is then available at `http://localhost:8000`, and the interactive
Swagger documentation at `http://localhost:8000/docs`.

## Configuration

| Environment variable | Default                        | Description                          |
|----------------------|--------------------------------|--------------------------------------|
| `CALCULATOR_DB`      | `./calculator.db` (project dir) | Path of the SQLite database file    |
| `--host` / `--port`  | `0.0.0.0:8000`                 | Uvicorn bind address (CLI options)  |

Example with a custom database path:

```bash
CALCULATOR_DB=/var/lib/calculator/calc.db uvicorn app.main:app --port 8000
```

## Database Initialization

No manual step is required: the `calculation_history` table is created
automatically on the first start (`app/database.py` → `_initialize`).

Schema:

```sql
CREATE TABLE IF NOT EXISTS calculation_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expression  TEXT    NOT NULL,
    result      TEXT    NOT NULL,
    created_at  TEXT    NOT NULL
);
```

## API Reference

| Method | Endpoint               | Description                                     |
|--------|------------------------|-------------------------------------------------|
| POST   | `/api/calculate`       | Evaluate an expression and store it             |
| GET    | `/api/history`         | List stored history (newest first)              |
| DELETE | `/api/history/{id}`    | Delete one history record                       |
| DELETE | `/api/history`         | Clear all history (extra feature)               |
| GET    | `/api/health`          | Health check for deployment verification        |

### POST /api/calculate

Request:

```json
{ "expression": "(1+2)*3" }
```

Successful response (`200`):

```json
{
  "success": true,
  "expression": "(1+2)*3",
  "result": "9",
  "record_id": 4,
  "created_at": "2026-09-22 22:24:44"
}
```

Error response (`400`):

```json
{ "detail": { "success": false, "message": "Division by zero" } }
```

### GET /api/history

```json
{
  "success": true,
  "total": 3,
  "data": [
    { "id": 4, "expression": "(1+2)*3", "result": "9", "created_at": "..." }
  ]
}
```

## Connecting the Front End

The front end talks to this API over HTTP/JSON. CORS is enabled for all
origins so the front end can be served from any address during
development/deployment. Set `API_BASE` in the front-end
`src/js/calculator.js` to the deployed back-end URL.

## Running the Tests

```bash
python -m unittest tests.test_parser -v
```

## Verifying the Separation

Stop this back-end service: the front end must then be **unable** to
produce a new calculation result (it shows a "cannot reach backend"
error). This proves that the calculation is not performed on the front end.
