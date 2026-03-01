from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional


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

    @staticmethod
    def _safe(getter: Callable[[], Any], default: Any) -> Any:
        try:
            value = getter()
        except Exception:
            return default
        return default if value is None else value

    def get_snapshot(self, ticker: str, intraday_interval: str = "1h") -> TickerSnapshot:
        import yfinance as yf

        obj = yf.Ticker(ticker)

        profile = self._safe(lambda: obj.info, {})
        prices_daily = self._safe(
            lambda: obj.history(period="1y", interval="1d").reset_index().to_dict("records"),
            [],
        )
        prices_intraday = self._safe(
            lambda: obj.history(period="7d", interval=intraday_interval).reset_index().to_dict("records"),
            [],
        )

        financials = {
            "income_statement_yearly": self._safe(lambda: obj.income_stmt.to_dict(), {}),
            "income_statement_quarterly": self._safe(lambda: obj.quarterly_income_stmt.to_dict(), {}),
            "balance_sheet_quarterly": self._safe(lambda: obj.get_balance_sheet(freq="quarterly").to_dict(), {}),
            "cash_flow_yearly": self._safe(lambda: obj.cashflow.to_dict(), {}),
            "cash_flow_quarterly": self._safe(lambda: obj.quarterly_cashflow.to_dict(), {}),
        }

        events = {
            "earnings_dates": self._safe(lambda: obj.earnings_dates.reset_index().to_dict("records"), []),
            "calendar": self._safe(
                lambda: obj.calendar.to_dict() if hasattr(obj.calendar, "to_dict") else obj.calendar,
                {},
            ),
            "dividends": self._safe(lambda: obj.dividends.reset_index().to_dict("records"), []),
        }

        recommendations = self._safe(lambda: obj.get_recommendations(), None)

        analyst = {
            "recommendations": []
            if recommendations is None
            else self._safe(lambda: recommendations.reset_index().to_dict("records"), []),
            "price_targets": self._safe(lambda: obj.get_analyst_price_targets(), {}),
            "earnings_estimate": self._safe(lambda: obj.earnings_estimate.to_dict(), {}),
            "revenue_estimate": self._safe(lambda: obj.revenue_estimate.to_dict(), {}),
            "eps_trend": self._safe(lambda: obj.eps_trend.to_dict(), {}),
            "growth_estimates": self._safe(lambda: obj.growth_estimates.to_dict(), {}),
        }

        insider = {
            "purchases": self._safe(lambda: obj.insider_purchases.to_dict(), {}),
            "transactions": self._safe(lambda: obj.insider_transactions.to_dict(), {}),
        }

        news = self._safe(lambda: obj.news, [])

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
            "dividend_or_buyback_signal": bool(profile.get("dividendRate") or 0)
            or bool(profile.get("dividendYield") or 0),
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
