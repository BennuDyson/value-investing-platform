"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas import CompanyResponse, HealthResponse, MetricResponse
from app.services import ResearchService
from database.init_db import init_db
from database.session import SessionLocal

app = FastAPI(title="Value Investing Platform", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/ticker/{symbol}", response_model=CompanyResponse)
def get_ticker(symbol: str, db: Session = Depends(get_db)) -> CompanyResponse:
    service = ResearchService(db)
    company = service.get_company(symbol)
    if company is None:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return CompanyResponse(
        ticker=company.ticker,
        name=company.name,
        sector=company.sector,
        market_cap=company.market_cap,
        employees=company.employees,
    )


@app.get("/ticker/{symbol}/financials", response_model=list[MetricResponse])
def ticker_financials(symbol: str, db: Session = Depends(get_db)) -> list[MetricResponse]:
    service = ResearchService(db)
    return [
        MetricResponse(
            ticker=m.ticker,
            metric_name=m.metric_name,
            metric_value=m.metric_value,
            as_of_date=m.as_of_date,
        )
        for m in service.get_ticker_financials(symbol)
    ]


@app.get("/screen/graham")
def screen_graham(tickers: list[str] = Query(default=[]), db: Session = Depends(get_db)) -> list[dict]:
    service = ResearchService(db)
    frame = service.latest_metrics_frame(tickers or None)
    if frame.empty:
        return []
    return service.run_screen("graham", frame).to_dict(orient="records")


@app.get("/screen/buffett")
def screen_buffett(tickers: list[str] = Query(default=[]), db: Session = Depends(get_db)) -> list[dict]:
    service = ResearchService(db)
    frame = service.latest_metrics_frame(tickers or None)
    if frame.empty:
        return []
    return service.run_screen("buffett", frame).to_dict(orient="records")


@app.get("/screen/combined")
def screen_combined(tickers: list[str] = Query(default=[]), db: Session = Depends(get_db)) -> list[dict]:
    service = ResearchService(db)
    frame = service.latest_metrics_frame(tickers or None)
    if frame.empty:
        return []
    return service.run_screen("combined", frame).to_dict(orient="records")
