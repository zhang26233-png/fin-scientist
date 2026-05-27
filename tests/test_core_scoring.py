import os

import pandas as pd


os.environ["FINSCIENTIST_SKIP_UI"] = "1"

import legacy_app  # noqa: E402
from core import scoring  # noqa: E402


def make_price_frame():
    return pd.DataFrame(
        {
            "Close": list(range(100, 170)),
            "Volume": [1000 + index * 10 for index in range(70)],
        },
        index=pd.date_range("2024-01-01", periods=70, freq="D"),
    )


def test_research_priority_score_typical_input_is_stable():
    metrics = legacy_app.calculate_screening_metrics(make_price_frame())
    result = scoring.calculate_research_priority_score(metrics)

    assert result == {"研究优先级评分": 65, "无法评分原因": ""}
    assert legacy_app.calculate_research_priority_score(metrics) == result


def test_research_priority_score_handles_empty_and_bad_input():
    assert scoring.calculate_research_priority_score(None)["研究优先级评分"] == "无法评分"
    assert scoring.calculate_research_priority_score({})["研究优先级评分"] == "无法评分"


def test_fundamental_quality_score_and_composite_are_stable():
    fundamental_data = {
        "market_cap": 1000,
        "pe_ttm": 20,
        "pb": 2,
        "roe": 0.20,
        "revenue_yoy": 0.20,
        "net_profit_yoy": 0.20,
        "gross_margin": 0.40,
        "net_margin": 0.15,
        "debt_asset_ratio": 0.40,
        "dividend_yield": 0.03,
    }

    fundamental_score = scoring.calculate_fundamental_quality_score(fundamental_data)

    assert fundamental_score == 75
    assert scoring.calculate_composite_research_score(65, fundamental_score) == 69.0
    assert legacy_app.calculate_fundamental_quality_score(fundamental_data) == fundamental_score

