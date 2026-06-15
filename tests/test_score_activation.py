import importlib

import pandas as pd

from research.score_activation import ACTIVATED_RESEARCH_FIELDS, activate_research_scores


def quote_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600001",
                "latest_price": 10.0,
                "pct_change": 2.5,
                "volume": 20_000_000,
                "turnover": 1_200_000_000,
                "open": 9.8,
                "high": 10.2,
                "low": 9.4,
                "prev_close": 9.75,
                "composite_score": 0,
                "selection_score": 0,
            },
            {
                "ticker": "600002",
                "latest_price": 10.0,
                "pct_change": 7.0,
                "volume": 5_000_000,
                "turnover": 70_000_000,
                "open": 9.5,
                "high": 10.5,
                "low": 9.0,
                "prev_close": 9.3,
                "composite_score": 0,
                "selection_score": 0,
            },
            {
                "ticker": "600003",
                "latest_price": 10.0,
                "pct_change": -8.0,
                "volume": 1_000_000,
                "turnover": 10_000_000,
                "open": 10.8,
                "high": 11.0,
                "low": 9.8,
                "prev_close": 10.9,
                "composite_score": 0,
                "selection_score": 0,
            },
        ]
    )


def test_empty_dataframe_safe_return():
    result = activate_research_scores(pd.DataFrame())

    assert result.empty
    for field in ACTIVATED_RESEARCH_FIELDS:
        assert field in result.columns


def test_input_dataframe_is_not_mutated():
    source = quote_frame()
    original = source.copy(deep=True)

    activate_research_scores(source)

    pd.testing.assert_frame_equal(source, original)


def test_quote_available_correct():
    frame = pd.DataFrame([{"ticker": "A", "latest_price": 10, "pct_change": None, "volume": None, "turnover": None}])

    result = activate_research_scores(frame)

    assert result.iloc[0]["quote_available"] is False
    assert result.iloc[0]["activated_research_bucket"] == "Unavailable"


def test_quote_quality_score_correct():
    frame = pd.DataFrame(
        [{"latest_price": 10, "pct_change": 1, "volume": 100, "turnover": 200, "open": 9, "high": 11}]
    )

    result = activate_research_scores(frame)

    assert result.iloc[0]["quote_quality_score"] == 100


def test_liquidity_score_correct():
    frame = pd.DataFrame([{"latest_price": 10, "pct_change": 1, "turnover": 500_000_000}])

    result = activate_research_scores(frame)

    assert result.iloc[0]["liquidity_score"] == 85


def test_momentum_score_correct():
    frame = pd.DataFrame([{"latest_price": 10, "pct_change": 3, "turnover": 100}])

    result = activate_research_scores(frame)

    assert result.iloc[0]["momentum_score"] == 80


def test_high_pct_change_generates_warning():
    frame = pd.DataFrame([{"latest_price": 10, "pct_change": 10.5, "turnover": 100}])

    result = activate_research_scores(frame)

    assert "涨幅过高，可能存在追高风险" in result.iloc[0]["activated_research_warnings"]


def test_large_decline_generates_warning():
    frame = pd.DataFrame([{"latest_price": 10, "pct_change": -7, "turnover": 100}])

    result = activate_research_scores(frame)

    assert "跌幅较大，短期波动风险较高" in result.iloc[0]["activated_research_warnings"]


def test_price_position_score_correct():
    frame = pd.DataFrame(
        [{"latest_price": 10.2, "pct_change": 1, "turnover": 100, "open": 9.8, "high": 10.5, "low": 9.5}]
    )

    result = activate_research_scores(frame)

    assert result.iloc[0]["price_position_score"] == 80


def test_activated_selection_score_is_clipped_to_0_100():
    frame = quote_frame()

    result = activate_research_scores(frame)

    assert result["activated_selection_score"].between(0, 100).all()


def test_high_score_enters_core():
    result = activate_research_scores(quote_frame().iloc[[0]])

    assert result.iloc[0]["activated_research_level"] == "High"
    assert result.iloc[0]["activated_research_bucket"] == "Core"
    assert result.iloc[0]["activated_research_status"] == "Selected"


def test_medium_score_enters_watch():
    result = activate_research_scores(quote_frame().iloc[[1]])

    assert result.iloc[0]["activated_research_bucket"] == "Watch"
    assert result.iloc[0]["activated_research_status"] == "Watch"


def test_low_score_enters_exclude():
    frame = pd.DataFrame(
        [
            {
                "ticker": "600004",
                "latest_price": 10.0,
                "pct_change": -9,
                "volume": 1,
                "turnover": 1,
                "open": 11,
                "high": 11,
                "low": 9,
                "prev_close": 10,
                "risk_score": 90,
            }
        ]
    )

    result = activate_research_scores(frame)

    assert result.iloc[0]["activated_research_bucket"] == "Exclude"
    assert result.iloc[0]["activated_research_status"] == "Excluded"


def test_high_risk_score_deducts_points():
    base = quote_frame().iloc[[0]].copy(deep=True)
    high_risk = base.copy(deep=True)
    high_risk["risk_score"] = 90

    base_result = activate_research_scores(base)
    risk_result = activate_research_scores(high_risk)

    assert risk_result.iloc[0]["activated_selection_score"] == base_result.iloc[0]["activated_selection_score"] - 20


def test_old_zero_selection_score_still_activates_score():
    frame = quote_frame().iloc[[0]].copy(deep=True)
    frame["selection_score"] = 0
    frame["composite_score"] = 0

    result = activate_research_scores(frame)

    assert result.iloc[0]["selection_score"] == 0
    assert result.iloc[0]["activated_selection_score"] > 0


def test_output_order_is_preserved():
    frame = quote_frame()

    result = activate_research_scores(frame)

    assert result["ticker"].tolist() == frame["ticker"].tolist()


def test_module_importable():
    assert importlib.import_module("research.score_activation")
