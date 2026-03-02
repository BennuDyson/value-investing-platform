"""API response schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class CompanyResponse(BaseModel):
    ticker: str
    name: str | None
    sector: str | None
    market_cap: float | None
    employees: int | None


class MetricResponse(BaseModel):
    ticker: str
    metric_name: str
    metric_value: float | None
    as_of_date: date
