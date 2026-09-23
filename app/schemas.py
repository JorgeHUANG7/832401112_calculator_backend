"""Request/response models for the calculator API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CalculateRequest(BaseModel):
    """Payload sent by the front end for one calculation."""

    expression: str = Field(..., min_length=1, max_length=200,
                            description="Arithmetic expression, e.g. (1+2)*3")


class CalculateResponse(BaseModel):
    """Successful response of POST /api/calculate."""

    success: bool = True
    expression: str
    result: str
    record_id: int
    created_at: str


class ErrorResponse(BaseModel):
    """Uniform error payload returned by the API."""

    success: bool = False
    message: str


class HistoryRecord(BaseModel):
    """One row of the calculation history."""

    id: int
    expression: str
    result: str
    created_at: str


class HistoryResponse(BaseModel):
    """Response of GET /api/history."""

    success: bool = True
    total: int
    data: list[HistoryRecord]


class HealthResponse(BaseModel):
    """Response of GET /api/health."""

    status: str
    service: str
