from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional



@dataclass
class TickerSnapshot:
    ticker: str
    profile: Dict[str, Any]
    prices_daily: List[Dict[str, Any]]
    prices_intraday: List[Dict[str, Any]]
    financials: Dict[str, Any]
    events: Dict[str, Any]
    analyst: Dict[str, Any]
    insider: Dict[str, Any]
    news: List[Dict[str, Any]]


class YFinanceGateway:
    """Thin wrapper that gathers most yfinance endpoints in one place."""

    def get_snapshot(self, ticker: str, intraday_interval: str = "1h") -> TickerSnapshot:
        import yfinance as yf

        obj = yf.Ticker(ticker)

        profile = obj.info or {}
        prices_daily = obj.history(period="1y", interval="1d").reset_index().to_dict("records")
        prices_intraday = obj.history(period="7d", interval=intraday_interval).reset_index().to_dict("records")

        financials = {
            "income_statement_yearly": obj.income_stmt.to_dict() if obj.income_stmt is not None else {},
            "income_statement_quarterly": obj.quarterly_income_stmt.to_dict() if obj.quarterly_income_stmt is not None else {},
            "balance_sheet_quarterly": obj.get_balance_sheet(freq="quarterly").to_dict(),
            "cash_flow_yearly": obj.cashflow.to_dict() if obj.cashflow is not None else {},
            "cash_flow_quarterly": obj.quarterly_cashflow.to_dict() if obj.quarterly_cashflow is not None else {},
        }

        events = {
            "earnings_dates": obj.earnings_dates.reset_index().to_dict("records") if obj.earnings_dates is not None else [],
            "calendar": obj.calendar.to_dict() if hasattr(obj.calendar, "to_dict") else (obj.calendar or {}),
            "dividends": obj.dividends.reset_index().to_dict("records") if obj.dividends is not None else [],
        }

        analyst = {
            "recommendations": obj.get_recommendations().reset_index().to_dict("records") if obj.get_recommendations() is not None else [],
            "price_targets": obj.get_analyst_price_targets() or {},
            "earnings_estimate": obj.earnings_estimate.to_dict() if obj.earnings_estimate is not None else {},
            "revenue_estimate": obj.revenue_estimate.to_dict() if obj.revenue_estimate is not None else {},
            "eps_trend": obj.eps_trend.to_dict() if obj.eps_trend is not None else {},
            "growth_estimates": obj.growth_estimates.to_dict() if obj.growth_estimates is not None else {},
        }

        insider = {
            "purchases": obj.insider_purchases.to_dict() if obj.insider_purchases is not None else {},
            "transactions": obj.insider_transactions.to_dict() if obj.insider_transactions is not None else {},
        }

        news = obj.news or []

        return TickerSnapshot(
            ticker=ticker,
            profile=profile,
            prices_daily=prices_daily,
            prices_intraday=prices_intraday,
            financials=financials,
            events=events,
            analyst=analyst,
            insider=insider,
            news=news,
        )


class ValueScoreEngine:
    """
    Heuristic score inspired by Buffett/Graham principles.
    Returns higher score for conservative value + quality characteristics.
    """

    def score(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        checks = {
            "positive_pe": self._between(profile.get("forwardPE"), low=0, high=20),
            "reasonable_pb": self._between(profile.get("priceToBook"), low=0, high=3),
            "healthy_margin": self._above(profile.get("profitMargins"), threshold=0.1),
            "strong_roe": self._above(profile.get("returnOnEquity"), threshold=0.12),
            "low_debt": self._between(profile.get("debtToEquity"), low=0, high=80),
            "cash_generation": self._above(profile.get("freeCashflow"), threshold=0),
            "dividend_or_buyback_signal": bool(profile.get("dividendRate") or 0) or bool(profile.get("dividendYield") or 0),
        }

        passed = sum(1 for ok in checks.values() if ok)
        total = len(checks)
        ratio = passed / total if total else 0

        return {
            "checks": checks,
            "score": round(ratio * 100, 2),
            "classification": "undervalued_candidate" if ratio >= 0.7 else "watchlist",
        }

    @staticmethod
    def _between(value: Optional[float], low: float, high: float) -> bool:
        return value is not None and low < float(value) <= high

    @staticmethod
    def _above(value: Optional[float], threshold: float) -> bool:
        return value is not None and float(value) > threshold


def screen_undervalued(tickers: Iterable[str]) -> List[Dict[str, Any]]:
    gateway = YFinanceGateway()
    scorer = ValueScoreEngine()
    results = []

    for ticker in tickers:
        snapshot = gateway.get_snapshot(ticker)
        valuation = scorer.score(snapshot.profile)
        results.append(
            {
                "ticker": ticker,
                "value_score": valuation["score"],
                "classification": valuation["classification"],
                "profile": {
                    "shortName": snapshot.profile.get("shortName"),
                    "sector": snapshot.profile.get("sector"),
                    "marketCap": snapshot.profile.get("marketCap"),
                    "forwardPE": snapshot.profile.get("forwardPE"),
                    "priceToBook": snapshot.profile.get("priceToBook"),
                    "profitMargins": snapshot.profile.get("profitMargins"),
                    "returnOnEquity": snapshot.profile.get("returnOnEquity"),
                    "debtToEquity": snapshot.profile.get("debtToEquity"),
                },
                "checks": valuation["checks"],
            }
        )

    return sorted(results, key=lambda x: x["value_score"], reverse=True)

