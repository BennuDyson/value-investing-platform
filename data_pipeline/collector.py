"""yfinance data collection for company fundamentals."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from data_pipeline.normalizers import normalize_news, to_tidy_statement


@dataclass
class CollectedTickerData:
    ticker: str
    profile: dict
    prices: pd.DataFrame
    income_annual: pd.DataFrame
    income_quarterly: pd.DataFrame
    balance_annual: pd.DataFrame
    balance_quarterly: pd.DataFrame
    cashflow_annual: pd.DataFrame
    cashflow_quarterly: pd.DataFrame
    earnings_dates: pd.DataFrame
    calendar: dict
    analyst: dict[str, pd.DataFrame]
    insider: dict[str, pd.DataFrame]
    news: list[dict]


class YFinanceCollector:
    """Collector wrapping yfinance access patterns with error tolerance."""

    def collect(self, ticker: str, history_period: str = "5y", history_interval: str = "1d") -> CollectedTickerData:
        symbol = ticker.upper()
        tk = yf.Ticker(symbol)

        profile = tk.get_info() or {}
        prices = tk.history(period=history_period, interval=history_interval).reset_index()

        analyst = {
            "recommendations": self._safe_df(tk.recommendations),
            "price_targets": pd.DataFrame([tk.analyst_price_targets or {}]),
            "earnings_estimate": self._safe_df(tk.earnings_estimate),
            "revenue_estimate": self._safe_df(tk.revenue_estimate),
            "eps_trend": self._safe_df(tk.eps_trend),
            "growth_estimates": self._safe_df(tk.growth_estimates),
        }

        insider = {
            "purchases": self._safe_df(tk.insider_purchases),
            "transactions": self._safe_df(tk.insider_transactions),
        }

        news = normalize_news(symbol, tk.news)

        return CollectedTickerData(
            ticker=symbol,
            profile=profile,
            prices=prices,
            income_annual=to_tidy_statement(symbol, "income", self._safe_df(tk.financials), "annual"),
            income_quarterly=to_tidy_statement(symbol, "income", self._safe_df(tk.quarterly_financials), "quarterly"),
            balance_annual=to_tidy_statement(symbol, "balance", self._safe_df(tk.balance_sheet), "annual"),
            balance_quarterly=to_tidy_statement(symbol, "balance", self._safe_df(tk.quarterly_balance_sheet), "quarterly"),
            cashflow_annual=to_tidy_statement(symbol, "cashflow", self._safe_df(tk.cashflow), "annual"),
            cashflow_quarterly=to_tidy_statement(symbol, "cashflow", self._safe_df(tk.quarterly_cashflow), "quarterly"),
            earnings_dates=self._safe_df(tk.earnings_dates),
            calendar=tk.calendar if isinstance(tk.calendar, dict) else {},
            analyst=analyst,
            insider=insider,
            news=news,
        )

    @staticmethod
    def _safe_df(candidate: pd.DataFrame | None) -> pd.DataFrame:
        if candidate is None:
            return pd.DataFrame()
        if isinstance(candidate, pd.DataFrame):
            return candidate.copy()
        return pd.DataFrame(candidate)
