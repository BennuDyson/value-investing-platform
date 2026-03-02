"""SQLAlchemy ORM models for value investing platform."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(128))
    market_cap: Mapped[float | None] = mapped_column(Float)
    employees: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (UniqueConstraint("ticker", "date", name="uq_price_ticker_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float | None] = mapped_column(Float)
    high: Mapped[float | None] = mapped_column(Float)
    low: Mapped[float | None] = mapped_column(Float)
    close: Mapped[float | None] = mapped_column(Float)
    volume: Mapped[float | None] = mapped_column(Float)


class IncomeStatement(Base):
    __tablename__ = "income_statements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    statement: Mapped[str] = mapped_column(String(32), default="income")
    line_item: Mapped[str] = mapped_column(String(128), index=True)
    period: Mapped[date] = mapped_column(Date, index=True)
    frequency: Mapped[str] = mapped_column(String(16), default="annual")
    value: Mapped[float | None] = mapped_column(Float)


class BalanceSheet(Base):
    __tablename__ = "balance_sheets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    statement: Mapped[str] = mapped_column(String(32), default="balance")
    line_item: Mapped[str] = mapped_column(String(128), index=True)
    period: Mapped[date] = mapped_column(Date, index=True)
    frequency: Mapped[str] = mapped_column(String(16), default="annual")
    value: Mapped[float | None] = mapped_column(Float)


class Cashflow(Base):
    __tablename__ = "cashflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    statement: Mapped[str] = mapped_column(String(32), default="cashflow")
    line_item: Mapped[str] = mapped_column(String(128), index=True)
    period: Mapped[date] = mapped_column(Date, index=True)
    frequency: Mapped[str] = mapped_column(String(16), default="annual")
    value: Mapped[float | None] = mapped_column(Float)


class AnalystData(Base):
    __tablename__ = "analyst_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    metric: Mapped[str] = mapped_column(String(128))
    period: Mapped[str | None] = mapped_column(String(32))
    value: Mapped[str | None] = mapped_column(Text)


class InsiderData(Base):
    __tablename__ = "insider_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    transaction_date: Mapped[date | None] = mapped_column(Date)
    insider: Mapped[str | None] = mapped_column(String(128))
    shares: Mapped[float | None] = mapped_column(Float)
    value: Mapped[float | None] = mapped_column(Float)
    transaction_type: Mapped[str | None] = mapped_column(String(64))


class NewsItem(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    headline: Mapped[str] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    publisher: Mapped[str | None] = mapped_column(String(128))


class ComputedMetric(Base):
    __tablename__ = "computed_metrics"
    __table_args__ = (UniqueConstraint("ticker", "metric_name", "as_of_date", name="uq_metric_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    metric_name: Mapped[str] = mapped_column(String(128), index=True)
    metric_value: Mapped[float | None] = mapped_column(Float)
    as_of_date: Mapped[date] = mapped_column(Date, index=True)
    source: Mapped[str | None] = mapped_column(String(64), default="computed")
