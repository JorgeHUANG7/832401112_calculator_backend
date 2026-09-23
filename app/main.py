"""Calculator backend - FastAPI application entry point.

Run with::

    uvicorn app.main:app --host 0.0.0.0 --port 8000

API overview
------------
POST   /api/calculate       calculate one expression (and store it)
GET    /api/history         list the stored calculation history
DELETE /api/history/{id}    delete one history record
DELETE /api/history         clear all history records
GET    /api/health          health check for deployment verification
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .database import repository
from .parser import DivisionByZeroError, InvalidExpressionError, calculate
from .schemas import (
    CalculateRequest,
    CalculateResponse,
    ErrorResponse,
    HealthResponse,
    HistoryRecord,
    HistoryResponse,
)

app = FastAPI(
    title="Calculator Backend API",
    description="Front-end / back-end separated calculator - calculation "
                "and history are handled by this backend.",
    version="1.0.0",
)

# The front end may be served from any origin during development and
# deployment, so permissive CORS is enabled for this assignment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Return a simple health payload used to verify deployment."""
    return HealthResponse(status="ok", service="calculator-backend")


@app.post(
    "/api/calculate",
    response_model=CalculateResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["calculation"],
)
def calculate_expression(payload: CalculateRequest) -> CalculateResponse:
    """Validate, parse, calculate and persist one expression.

    The front end only sends the raw expression string; the actual
    evaluation always happens here in the backend.
    """
    expression = payload.expression.strip()
    try:
        result = calculate(expression)
    except DivisionByZeroError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": str(exc)},
        ) from exc
    except InvalidExpressionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": str(exc)},
        ) from exc

    record_id = repository.insert(expression, result)
    record = repository.get_latest(limit=1)[0]
    return CalculateResponse(
        success=True,
        expression=expression,
        result=result,
        record_id=record_id,
        created_at=str(record["created_at"]),
    )


@app.get("/api/history", response_model=HistoryResponse, tags=["history"])
def list_history(limit: int = 100) -> HistoryResponse:
    """Return the persisted calculation history, newest first."""
    rows = repository.get_latest(limit=limit)
    records = [HistoryRecord(**row) for row in rows]
    return HistoryResponse(success=True, total=len(records), data=records)


@app.delete(
    "/api/history/{record_id}",
    responses={404: {"model": ErrorResponse}},
    tags=["history"],
)
def delete_history_record(record_id: int) -> dict:
    """Delete one history record by its id."""
    if not repository.delete(record_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"History record {record_id} not found"},
        )
    return {"success": True, "message": f"Deleted record {record_id}"}


@app.delete("/api/history", tags=["history"])
def clear_history() -> dict:
    """Delete all history records (extra feature)."""
    removed = repository.clear()
    return {"success": True, "message": f"Removed {removed} record(s)"}
