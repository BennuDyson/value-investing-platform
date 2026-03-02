from datetime import date

import pytest

pd = pytest.importorskip("pandas")

from data_pipeline.normalizers import to_tidy_statement


def test_to_tidy_statement_handles_dataframe_input() -> None:
    frame = pd.DataFrame(
        {
            pd.Timestamp("2024-12-31"): [100.0, 50.0],
            pd.Timestamp("2023-12-31"): [90.0, 45.0],
        },
        index=["Total Revenue", "Operating Income"],
    )

    tidy = to_tidy_statement("AAPL", "income", frame, "annual")

    assert not tidy.empty
    assert set(tidy.columns) == {"ticker", "statement", "line_item", "period", "frequency", "value"}
    assert tidy["ticker"].eq("AAPL").all()
    assert tidy["statement"].eq("income").all()
    assert tidy["frequency"].eq("annual").all()


def test_to_tidy_statement_handles_series_input() -> None:
    series = pd.Series(
        [150.0, 30.0],
        index=["Total Assets", "Current Assets"],
        name=pd.Timestamp("2024-12-31"),
    )

    tidy = to_tidy_statement("MSFT", "balance", series, "annual")

    assert len(tidy) == 2
    assert tidy["period"].eq(date(2024, 12, 31)).all()
    assert set(tidy["line_item"]) == {"Total Assets", "Current Assets"}
