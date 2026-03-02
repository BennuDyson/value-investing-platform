import pytest

pd = pytest.importorskip("pandas")

from screens.screeners import combined_screen


def test_screening_ranking_logic() -> None:
    frame = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "price": 50,
                "pe_ratio": 10,
                "pb_ratio": 1.2,
                "current_ratio": 2.0,
                "debt_to_equity": 0.2,
                "graham_number": 90,
                "roe": 0.2,
                "roic": 0.12,
                "fcf_yield": 0.07,
                "gross_margin": 0.4,
                "operating_margin": 0.2,
                "revenue_growth_consistency": 0.8,
                "share_count_trend": -0.01,
            },
            {
                "ticker": "BBB",
                "price": 95,
                "pe_ratio": 20,
                "pb_ratio": 2.0,
                "current_ratio": 1.0,
                "debt_to_equity": 1.0,
                "graham_number": 90,
                "roe": 0.1,
                "roic": 0.05,
                "fcf_yield": 0.02,
                "gross_margin": 0.2,
                "operating_margin": 0.1,
                "revenue_growth_consistency": 0.3,
                "share_count_trend": 0.02,
            },
        ]
    )

    ranked = combined_screen(frame)
    assert ranked.iloc[0]["ticker"] == "AAA"
    assert ranked.iloc[0]["combined_score"] > ranked.iloc[1]["combined_score"]
