"""Value-investing metric calculations."""

from __future__ import annotations


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def pe_ratio(price: float | None, eps: float | None) -> float | None:
    return safe_div(price, eps)


def pb_ratio(price: float | None, book_value_per_share: float | None) -> float | None:
    return safe_div(price, book_value_per_share)


def current_ratio(current_assets: float | None, current_liabilities: float | None) -> float | None:
    return safe_div(current_assets, current_liabilities)


def debt_to_equity(total_debt: float | None, total_equity: float | None) -> float | None:
    return safe_div(total_debt, total_equity)


def graham_number(eps: float | None, book_value_per_share: float | None) -> float | None:
    if eps is None or book_value_per_share is None or eps <= 0 or book_value_per_share <= 0:
        return None
    return (22.5 * eps * book_value_per_share) ** 0.5


def margin_of_safety(intrinsic_value: float | None, price: float | None) -> float | None:
    if intrinsic_value is None or price is None or intrinsic_value <= 0:
        return None
    return (intrinsic_value - price) / intrinsic_value


def roe(net_income: float | None, shareholder_equity: float | None) -> float | None:
    return safe_div(net_income, shareholder_equity)


def roic(nopat: float | None, invested_capital: float | None) -> float | None:
    return safe_div(nopat, invested_capital)


def fcf(operating_cash_flow: float | None, capex: float | None) -> float | None:
    if operating_cash_flow is None or capex is None:
        return None
    return operating_cash_flow - abs(capex)


def fcf_yield(free_cash_flow: float | None, market_cap: float | None) -> float | None:
    return safe_div(free_cash_flow, market_cap)


def gross_margin(gross_profit: float | None, revenue: float | None) -> float | None:
    return safe_div(gross_profit, revenue)


def operating_margin(operating_income: float | None, revenue: float | None) -> float | None:
    return safe_div(operating_income, revenue)
