"""Persistence routines for collected data."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from data_pipeline.collector import CollectedTickerData
from database.models import (
    AnalystData,
    BalanceSheet,
    Cashflow,
    Company,
    IncomeStatement,
    InsiderData,
    NewsItem,
    Price,
)


class DataRepository:
    """Store normalized data into relational tables."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_collected_data(self, data: CollectedTickerData) -> None:
        self._upsert_company(data)
        self._store_prices(data.ticker, data.prices)
        self._store_statement(data.income_annual, IncomeStatement)
        self._store_statement(data.income_quarterly, IncomeStatement)
        self._store_statement(data.balance_annual, BalanceSheet)
        self._store_statement(data.balance_quarterly, BalanceSheet)
        self._store_statement(data.cashflow_annual, Cashflow)
        self._store_statement(data.cashflow_quarterly, Cashflow)
        self._store_analyst(data.ticker, data.analyst)
        self._store_insider(data.ticker, data.insider)
        self._store_news(data.news)

    def _upsert_company(self, data: CollectedTickerData) -> None:
        profile = data.profile
        company = self.session.query(Company).filter_by(ticker=data.ticker).first()
        if company is None:
            company = Company(ticker=data.ticker)
            self.session.add(company)
        company.name = profile.get("longName") or profile.get("shortName")
        company.sector = profile.get("sector")
        company.market_cap = profile.get("marketCap")
        company.employees = profile.get("fullTimeEmployees")

    def _store_prices(self, ticker: str, prices: pd.DataFrame) -> None:
        if prices.empty:
            return
        prices = prices.rename(columns={"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        for _, row in prices.iterrows():
            d = pd.to_datetime(row.get("date"), errors="coerce")
            if pd.isna(d):
                continue
            entry = Price(
                ticker=ticker,
                date=d.date(),
                open=_to_float(row.get("open")),
                high=_to_float(row.get("high")),
                low=_to_float(row.get("low")),
                close=_to_float(row.get("close")),
                volume=_to_float(row.get("volume")),
            )
            self.session.merge(entry)

    def _store_statement(self, tidy_frame: pd.DataFrame, model: type[IncomeStatement] | type[BalanceSheet] | type[Cashflow]) -> None:
        if tidy_frame.empty:
            return
        for _, row in tidy_frame.iterrows():
            self.session.add(
                model(
                    ticker=row["ticker"],
                    statement=row["statement"],
                    line_item=row["line_item"],
                    period=row["period"],
                    frequency=row["frequency"],
                    value=_to_float(row["value"]),
                )
            )

    def _store_analyst(self, ticker: str, analyst_frames: dict[str, pd.DataFrame]) -> None:
        for category, frame in analyst_frames.items():
            if frame is None or frame.empty:
                continue
            normalized = frame.reset_index().melt(id_vars=[c for c in ["index"] if c in frame.reset_index().columns], var_name="metric", value_name="value")
            for _, row in normalized.iterrows():
                self.session.add(
                    AnalystData(
                        ticker=ticker,
                        category=category,
                        metric=str(row.get("metric")),
                        period=str(row.get("index")) if "index" in row else None,
                        value=str(row.get("value")),
                    )
                )

    def _store_insider(self, ticker: str, insider_frames: dict[str, pd.DataFrame]) -> None:
        for source, frame in insider_frames.items():
            if frame is None or frame.empty:
                continue
            for _, row in frame.reset_index().iterrows():
                tx_date = pd.to_datetime(row.get("Date") or row.get("Start Date"), errors="coerce")
                self.session.add(
                    InsiderData(
                        ticker=ticker,
                        source=source,
                        transaction_date=tx_date.date() if not pd.isna(tx_date) else None,
                        insider=str(row.get("Insider") or row.get("Insider Name") or ""),
                        shares=_to_float(row.get("Shares")),
                        value=_to_float(row.get("Value") or row.get("Transaction")),
                        transaction_type=str(row.get("Text") or row.get("Transaction") or ""),
                    )
                )

    def _store_news(self, news_items: list[dict]) -> None:
        for item in news_items:
            if not item.get("headline"):
                continue
            self.session.add(NewsItem(**item))


def _to_float(value: object) -> float | None:
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None
