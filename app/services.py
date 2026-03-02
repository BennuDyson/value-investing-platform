"""Service layer used by FastAPI routes."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import desc
from sqlalchemy.orm import Session

from data_pipeline.collector import YFinanceCollector
from data_pipeline.storage import DataRepository
from database.models import Company, ComputedMetric
from screens.metrics import (
    current_ratio,
    debt_to_equity,
    fcf,
    fcf_yield,
    graham_number,
    gross_margin,
    operating_margin,
    pb_ratio,
    pe_ratio,
    roe,
    roic,
)
from screens.screeners import buffett_screen, combined_screen, graham_screen


class ResearchService:
    """Application service encapsulating persistence and analytics."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.collector = YFinanceCollector()
        self.repo = DataRepository(session)

    def ingest_ticker(self, ticker: str) -> None:
        data = self.collector.collect(ticker)
        self.repo.upsert_collected_data(data)

    def get_company(self, ticker: str) -> Company | None:
        return self.session.query(Company).filter_by(ticker=ticker.upper()).first()

    def get_ticker_financials(self, ticker: str) -> list[ComputedMetric]:
        return (
            self.session.query(ComputedMetric)
            .filter_by(ticker=ticker.upper())
            .order_by(desc(ComputedMetric.as_of_date))
            .all()
        )

    def compute_metrics_for_ticker(self, ticker: str, base_row: dict[str, float]) -> None:
        symbol = ticker.upper()
        metrics = {
            "pe_ratio": pe_ratio(base_row.get("price"), base_row.get("eps")),
            "pb_ratio": pb_ratio(base_row.get("price"), base_row.get("book_value_per_share")),
            "current_ratio": current_ratio(base_row.get("current_assets"), base_row.get("current_liabilities")),
            "debt_to_equity": debt_to_equity(base_row.get("total_debt"), base_row.get("total_equity")),
            "graham_number": graham_number(base_row.get("eps"), base_row.get("book_value_per_share")),
            "roe": roe(base_row.get("net_income"), base_row.get("total_equity")),
            "roic": roic(base_row.get("nopat"), base_row.get("invested_capital")),
            "fcf": fcf(base_row.get("operating_cash_flow"), base_row.get("capex")),
            "gross_margin": gross_margin(base_row.get("gross_profit"), base_row.get("revenue")),
            "operating_margin": operating_margin(base_row.get("operating_income"), base_row.get("revenue")),
        }
        metrics["fcf_yield"] = fcf_yield(metrics["fcf"], base_row.get("market_cap"))
        as_of = date.today()
        for name, value in metrics.items():
            self.session.merge(
                ComputedMetric(
                    ticker=symbol,
                    metric_name=name,
                    metric_value=value,
                    as_of_date=as_of,
                    source="service_compute",
                )
            )



    def latest_metrics_frame(self, tickers: list[str] | None = None) -> pd.DataFrame:
        query = self.session.query(ComputedMetric)
        if tickers:
            query = query.filter(ComputedMetric.ticker.in_([t.upper() for t in tickers]))
        rows = query.order_by(desc(ComputedMetric.as_of_date)).all()
        grouped: dict[str, dict[str, float]] = {}
        for row in rows:
            grouped.setdefault(row.ticker, {})
            grouped[row.ticker].setdefault("ticker", row.ticker)
            if row.metric_name not in grouped[row.ticker]:
                grouped[row.ticker][row.metric_name] = row.metric_value
        frame = pd.DataFrame(grouped.values())
        if frame.empty:
            return frame
        frame["price"] = frame.get("price", 100.0)
        frame["revenue_growth_consistency"] = frame.get("revenue_growth_consistency", 0.0)
        frame["share_count_trend"] = frame.get("share_count_trend", 0.0)
        return frame

    def run_screen(self, style: str, frame: pd.DataFrame) -> pd.DataFrame:
        if style == "graham":
            return graham_screen(frame)
        if style == "buffett":
            return buffett_screen(frame)
        return combined_screen(frame)
