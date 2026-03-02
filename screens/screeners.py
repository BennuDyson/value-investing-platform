"""Pure screening functions for Graham and Buffett styles."""

from __future__ import annotations

import pandas as pd

from screens.metrics import margin_of_safety


def graham_screen(frame: pd.DataFrame) -> pd.DataFrame:
    """Rank companies by conservative value-investing criteria."""
    data = frame.copy()
    data["graham_score"] = 0
    data.loc[data["pe_ratio"] <= 15, "graham_score"] += 1
    data.loc[data["pb_ratio"] <= 1.5, "graham_score"] += 1
    data.loc[data["current_ratio"] >= 1.5, "graham_score"] += 1
    data.loc[data["debt_to_equity"] <= 0.5, "graham_score"] += 1
    data["margin_of_safety"] = data.apply(
        lambda row: margin_of_safety(row.get("graham_number"), row.get("price")), axis=1
    )
    data.loc[data["margin_of_safety"] >= 0.2, "graham_score"] += 1
    return data.sort_values(["graham_score", "margin_of_safety"], ascending=False).reset_index(drop=True)


def buffett_screen(frame: pd.DataFrame) -> pd.DataFrame:
    """Rank companies by quality + cash-generative profile."""
    data = frame.copy()
    data["buffett_score"] = 0
    data.loc[data["roe"] >= 0.15, "buffett_score"] += 1
    data.loc[data["roic"] >= 0.10, "buffett_score"] += 1
    data.loc[data["fcf_yield"] >= 0.05, "buffett_score"] += 1
    data.loc[data["gross_margin"] >= 0.30, "buffett_score"] += 1
    data.loc[data["operating_margin"] >= 0.15, "buffett_score"] += 1
    data.loc[data["revenue_growth_consistency"] >= 0.6, "buffett_score"] += 1
    data.loc[data["share_count_trend"] <= 0, "buffett_score"] += 1
    return data.sort_values("buffett_score", ascending=False).reset_index(drop=True)


def combined_screen(frame: pd.DataFrame) -> pd.DataFrame:
    """Combine both frameworks into one ranking."""
    graham_ranked = graham_screen(frame)
    buffett_ranked = buffett_screen(graham_ranked)
    buffett_ranked["combined_score"] = buffett_ranked["graham_score"] + buffett_ranked["buffett_score"]
    return buffett_ranked.sort_values("combined_score", ascending=False).reset_index(drop=True)
