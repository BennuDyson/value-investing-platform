import sys
import types

from value_investing_platform.screener import YFinanceGateway


class _FakeFrame:
    def reset_index(self):
        return self

    def to_dict(self, _orient=None):
        return [{"ok": True}]


class _FakeTicker:
    info = {"shortName": "Test Co"}
    income_stmt = _FakeFrame()
    quarterly_income_stmt = _FakeFrame()
    cashflow = _FakeFrame()
    quarterly_cashflow = _FakeFrame()
    dividends = _FakeFrame()
    calendar = {"earningsDate": "soon"}
    insider_purchases = _FakeFrame()
    insider_transactions = _FakeFrame()
    earnings_estimate = _FakeFrame()
    revenue_estimate = _FakeFrame()
    eps_trend = _FakeFrame()
    growth_estimates = _FakeFrame()
    news = [{"title": "headline"}]

    def history(self, **_kwargs):
        return _FakeFrame()

    def get_balance_sheet(self, **_kwargs):
        return _FakeFrame()

    @property
    def earnings_dates(self):
        raise ImportError("missing lxml")

    def get_recommendations(self):
        return _FakeFrame()

    def get_analyst_price_targets(self):
        return {"targetMeanPrice": 100}


class _FakeYF:
    @staticmethod
    def Ticker(_ticker):
        return _FakeTicker()


def test_get_snapshot_handles_optional_dependency_errors(monkeypatch):
    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(Ticker=_FakeYF.Ticker))

    snapshot = YFinanceGateway().get_snapshot("AAPL")

    assert snapshot.ticker == "AAPL"
    assert snapshot.events["earnings_dates"] == []
    assert snapshot.profile["shortName"] == "Test Co"
    assert snapshot.analyst["price_targets"]["targetMeanPrice"] == 100
