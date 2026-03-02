from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="Value Investing Platform API")

CACHE_TTL_SECONDS = 60
_cache: dict[str, tuple[datetime, dict[str, Any]]] = {}


def _to_iso(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def _clean_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.generic,)):
        value = value.item()
    if isinstance(value, float) and np.isnan(value):
        return None
    if pd.isna(value):
        return None
    return _to_iso(value)


def _serialize_dataframe(df: Any) -> Any:
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return None

    safe = df.copy().astype(object).where(pd.notna(df), None)
    columns = [str(col) for col in safe.columns]
    index = [_clean_scalar(idx) for idx in safe.index.tolist()]
    data = [[_clean_scalar(cell) for cell in row] for row in safe.values.tolist()]
    return {"columns": columns, "index": index, "data": data}


def _serialize_series(series: Any) -> Any:
    if series is None or not isinstance(series, pd.Series) or series.empty:
        return None

    safe = series.copy().astype(object).where(pd.notna(series), None)
    return {
        "index": [_clean_scalar(idx) for idx in safe.index.tolist()],
        "data": [_clean_scalar(val) for val in safe.tolist()],
    }


def _serialize_generic(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        return _serialize_dataframe(value)
    if isinstance(value, pd.Series):
        return _serialize_series(value)
    if isinstance(value, dict):
        return {str(k): _serialize_generic(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_generic(v) for v in value]
    return _clean_scalar(value)


def _error_response(status_code: int, message: str, details: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"message": message, "details": details}},
    )


def _get_cached(symbol: str) -> dict[str, Any] | None:
    cached = _cache.get(symbol)
    if not cached:
        return None
    expires_at, payload = cached
    if datetime.now(timezone.utc) >= expires_at:
        _cache.pop(symbol, None)
        return None
    return payload


def _set_cache(symbol: str, payload: dict[str, Any]) -> None:
    expires = datetime.now(timezone.utc) + pd.Timedelta(seconds=CACHE_TTL_SECONDS)
    _cache[symbol] = (expires, payload)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/ticker/{symbol}/all", response_model=None)
def ticker_all(symbol: str) -> Any:
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        return _error_response(400, "Invalid symbol", "Ticker symbol is required.")

    cached = _get_cached(normalized_symbol)
    if cached:
        return cached

    try:
        data = yf.Ticker(normalized_symbol)
        info = data.info or {}

        datasets = {
            "price_history": data.history(period="7d", interval="1m"),
            "pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendRate"),
            "dividend_history": data.dividends,
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume"),
            "volume_avg": info.get("averageVolume"),
            "volume_avg_10": info.get("averageVolume10days"),
            "income_statement": data.income_stmt,
            "quaterly_income_statement": data.quarterly_income_stmt,
            "balance_sheet": data.get_balance_sheet(as_dict=False, pretty=False, freq="quarterly"),
            "earnings_dates": data.earnings_dates,
            "calendar": data.calendar,
            "recommendations": data.get_recommendations(),
            "price_targets": data.get_analyst_price_targets(),
            "earnings_estimate": data.earnings_estimate,
            "revenue_estimate": data.revenue_estimate,
            "eps_trend": data.eps_trend,
            "growth_estimates": data.growth_estimates,
            "insider_purchases": data.insider_purchases,
            "insider_transactions": data.insider_transactions,
            "news": data.news,
        }

        payload = {
            "symbol": normalized_symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {key: _serialize_generic(value) for key, value in datasets.items()},
        }
        _set_cache(normalized_symbol, payload)
        return payload
    except HTTPException as exc:
        return _error_response(exc.status_code, "Request failed", str(exc.detail))
    except Exception as exc:  # noqa: BLE001
        return _error_response(502, "Failed to fetch ticker data", str(exc))
