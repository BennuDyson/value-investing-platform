"""Normalization helpers for yfinance data."""

from __future__ import annotations

from datetime import datetime

import pandas as pd


def to_tidy_statement(
    ticker: str,
    statement_name: str,
    frame: pd.DataFrame,
    frequency: str,
) -> pd.DataFrame:
    """Convert wide yfinance financial statement into tidy format."""
    if frame is None or frame.empty:
        return pd.DataFrame(columns=["ticker", "statement", "line_item", "period", "frequency", "value"])

    tidy = frame.copy()
    tidy.index = tidy.index.astype(str)
    tidy = tidy.reset_index().rename(columns={"index": "line_item"})
    tidy = tidy.melt(id_vars=["line_item"], var_name="period", value_name="value")
    tidy["period"] = pd.to_datetime(tidy["period"], errors="coerce").dt.date
    tidy["ticker"] = ticker
    tidy["statement"] = statement_name
    tidy["frequency"] = frequency
    tidy = tidy[["ticker", "statement", "line_item", "period", "frequency", "value"]]
    return tidy.dropna(subset=["period"])


def normalize_news(ticker: str, news_items: list[dict]) -> list[dict]:
    """Normalize yfinance news payload."""
    normalized: list[dict] = []
    for item in news_items or []:
        ts = item.get("providerPublishTime")
        normalized.append(
            {
                "ticker": ticker,
                "headline": item.get("title"),
                "link": item.get("link"),
                "published_at": datetime.utcfromtimestamp(ts) if ts else None,
                "publisher": item.get("publisher"),
            }
        )
    return normalized
