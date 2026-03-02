"""Database bootstrap utilities."""

from database.base import Base
from database.models import (
    AnalystData,
    BalanceSheet,
    Cashflow,
    Company,
    ComputedMetric,
    IncomeStatement,
    InsiderData,
    NewsItem,
    Price,
)
from database.session import engine


def init_db() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
