from value_investing_platform.screener import ValueScoreEngine


def test_score_flags_undervalued_candidate():
    engine = ValueScoreEngine()
    profile = {
        "forwardPE": 15,
        "priceToBook": 2.5,
        "profitMargins": 0.22,
        "returnOnEquity": 0.18,
        "debtToEquity": 40,
        "freeCashflow": 100,
        "dividendRate": 1.2,
    }

    result = engine.score(profile)

    assert result["classification"] == "undervalued_candidate"
    assert result["score"] >= 70
