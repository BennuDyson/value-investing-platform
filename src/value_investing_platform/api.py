from __future__ import annotations

from typing import List

from fastapi import FastAPI, Query

from .screener import YFinanceGateway, screen_undervalued

app = FastAPI(title="Value Investing Platform API", version="0.1.0")
_gateway = YFinanceGateway()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/tickers/{ticker}/snapshot")
def ticker_snapshot(ticker: str, intraday_interval: str = Query(default="1h")) -> dict:
    snapshot = _gateway.get_snapshot(ticker, intraday_interval=intraday_interval)
    return {
        "ticker": snapshot.ticker,
        "profile": snapshot.profile,
        "prices": {
            "daily": snapshot.prices_daily,
            "intraday": snapshot.prices_intraday,
        },
        "financials": snapshot.financials,
        "events": snapshot.events,
        "analyst": snapshot.analyst,
        "insider": snapshot.insider,
        "news": snapshot.news,
    }


@app.get("/screen/undervalued")
def undervalued(tickers: List[str] = Query(..., description="Tickers to evaluate")) -> dict:
    return {"results": screen_undervalued(tickers)}
