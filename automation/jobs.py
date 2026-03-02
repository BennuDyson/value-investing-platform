"""Scheduled automation jobs for ingesting and screening."""

from __future__ import annotations

from datetime import date

import pandas as pd

from app.services import ResearchService
from database.models import ComputedMetric
from database.session import get_session


def update_tickers(tickers: list[str]) -> None:
    with get_session() as session:
        service = ResearchService(session)
        for ticker in tickers:
            service.ingest_ticker(ticker)


def recompute_metrics(tickers: list[str]) -> None:
    with get_session() as session:
        service = ResearchService(session)
        for ticker in tickers:
            # In production, this row should be assembled from normalized DB statements.
            baseline = {
                "price": 100,
                "eps": 5,
                "book_value_per_share": 30,
                "current_assets": 200,
                "current_liabilities": 100,
                "total_debt": 50,
                "total_equity": 200,
                "net_income": 30,
                "nopat": 20,
                "invested_capital": 180,
                "operating_cash_flow": 40,
                "capex": -10,
                "gross_profit": 80,
                "operating_income": 25,
                "revenue": 150,
                "market_cap": 1_000,
            }
            service.compute_metrics_for_ticker(ticker, baseline)


def run_undervalued_screen(tickers: list[str]) -> None:
    with get_session() as session:
        rows = (
            session.query(ComputedMetric)
            .filter(ComputedMetric.ticker.in_([t.upper() for t in tickers]), ComputedMetric.as_of_date == date.today())
            .all()
        )

        by_ticker: dict[str, dict[str, float]] = {}
        for metric in rows:
            by_ticker.setdefault(metric.ticker, {})[metric.metric_name] = metric.metric_value

        screen_frame = pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "price": metrics.get("pe_ratio", 0) * 1,
                    "pe_ratio": metrics.get("pe_ratio"),
                    "pb_ratio": metrics.get("pb_ratio"),
                    "current_ratio": metrics.get("current_ratio"),
                    "debt_to_equity": metrics.get("debt_to_equity"),
                    "graham_number": metrics.get("graham_number"),
                    "roe": metrics.get("roe"),
                    "roic": metrics.get("roic"),
                    "fcf_yield": metrics.get("fcf_yield"),
                    "gross_margin": metrics.get("gross_margin"),
                    "operating_margin": metrics.get("operating_margin"),
                    "revenue_growth_consistency": 0.7,
                    "share_count_trend": -0.01,
                }
                for ticker, metrics in by_ticker.items()
            ]
        )
        if screen_frame.empty:
            return
        service = ResearchService(session)
        _ = service.run_screen("combined", screen_frame)
