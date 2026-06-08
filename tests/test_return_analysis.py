import copy
import importlib
import math

import pandas as pd
import pytest

from backtest.return_analysis import RETURN_ANALYSIS_FIELDS, build_return_analysis


def backtest_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "candidate_rank": 1,
                "composite_score": 85,
                "backtest_available": True,
                "backtest_status": "Available",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "candidate_rank": 2,
                "composite_score": 66,
                "backtest_available": True,
                "backtest_status": "Available",
            },
        ]
    )


def price_history(closes, start="2026-01-01"):
    dates = pd.date_range(start=start, periods=len(closes), freq="D")
    return pd.DataFrame({"date": dates, "close": closes})


def metric_history():
    closes = [100, 102, 101, 104, 103, 107, 106, 110, 108, 112] * 6
    return price_history(closes)


def expected_metrics(history):
    closes = history["close"].astype(float)
    daily_return = closes.pct_change().dropna()
    period_return = closes.iloc[-1] / closes.iloc[0] - 1
    holding_days = len(closes)
    return {
        "holding_period_days": holding_days,
        "entry_price": float(closes.iloc[0]),
        "exit_price": float(closes.iloc[-1]),
        "period_return": float(period_return),
        "annualized_return": float((1 + period_return) ** (252 / holding_days) - 1),
        "volatility": float(daily_return.std() * math.sqrt(252)),
        "max_drawdown": float((closes / closes.cummax() - 1).min()),
        "win_rate": float((daily_return > 0).mean()),
    }


def test_empty_input_safe_return():
    output = build_return_analysis(pd.DataFrame(), {})

    assert output.empty
    assert set(RETURN_ANALYSIS_FIELDS).issubset(output.columns)


def test_no_price_history_returns_incomplete():
    output = build_return_analysis(backtest_frame().iloc[[0]], {})

    row = output.iloc[0]
    assert row["return_analysis_available"] is False
    assert row["return_analysis_status"] == "Incomplete"
    assert any("Price history missing" in warning for warning in row["return_analysis_warnings"])


def test_backtest_unavailable_does_not_calculate_returns():
    frame = backtest_frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "backtest_available"] = False

    output = build_return_analysis(frame, {"600000": metric_history()})

    row = output.iloc[0]
    assert row["return_analysis_available"] is False
    assert row["return_analysis_status"] == "Incomplete"
    assert row["period_return"] is None
    assert any("Backtest foundation is unavailable" in warning for warning in row["return_analysis_warnings"])


def test_single_stock_generates_fields():
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": metric_history()})

    assert len(output) == 1
    assert set(RETURN_ANALYSIS_FIELDS).issubset(output.columns)
    assert output.iloc[0]["return_analysis_available"] is True
    assert output.iloc[0]["return_analysis_status"] == "Available"


def test_multiple_stocks_generate_fields():
    output = build_return_analysis(
        backtest_frame(),
        {"600000": metric_history(), "600001": price_history([20 + index for index in range(60)])},
    )

    assert output["ticker"].tolist() == ["600000", "600001"]
    assert output["return_analysis_status"].tolist() == ["Available", "Available"]


def test_period_return_calculated_correctly():
    history = metric_history()
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": history})

    assert output.iloc[0]["period_return"] == pytest.approx(expected_metrics(history)["period_return"])


def test_annualized_return_calculated_correctly():
    history = metric_history()
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": history})

    assert output.iloc[0]["annualized_return"] == pytest.approx(expected_metrics(history)["annualized_return"])


def test_volatility_calculated_correctly():
    history = metric_history()
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": history})

    assert output.iloc[0]["volatility"] == pytest.approx(expected_metrics(history)["volatility"])


def test_max_drawdown_calculated_correctly():
    history = metric_history()
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": history})

    assert output.iloc[0]["max_drawdown"] == pytest.approx(expected_metrics(history)["max_drawdown"])


def test_win_rate_calculated_correctly():
    history = metric_history()
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": history})

    assert output.iloc[0]["win_rate"] == pytest.approx(expected_metrics(history)["win_rate"])


def test_missing_close_generates_warning():
    history = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=60, freq="D")})
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": history})

    warnings = output.iloc[0]["return_analysis_warnings"]
    assert output.iloc[0]["return_analysis_status"] == "Incomplete"
    assert any("close column missing" in warning for warning in warnings)


def test_missing_date_generates_warning():
    history = pd.DataFrame({"close": [100 + index for index in range(60)]})
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": history})

    warnings = output.iloc[0]["return_analysis_warnings"]
    assert output.iloc[0]["return_analysis_status"] == "Incomplete"
    assert any("date column missing" in warning for warning in warnings)


def test_input_objects_are_not_modified():
    frame = backtest_frame()
    history = metric_history()
    histories = {"600000": history}
    frame_before = copy.deepcopy(frame)
    history_before = copy.deepcopy(history)

    build_return_analysis(frame, histories)

    pd.testing.assert_frame_equal(frame, frame_before)
    pd.testing.assert_frame_equal(history, history_before)


def test_output_order_unchanged():
    output = build_return_analysis(
        backtest_frame(),
        {"600001": metric_history(), "600000": metric_history()},
    )

    assert output["ticker"].tolist() == ["600000", "600001"]


def test_existing_score_fields_are_not_modified():
    output = build_return_analysis(backtest_frame().iloc[[0]], {"600000": metric_history()})

    assert output.iloc[0]["composite_score"] == 85
    assert output.iloc[0]["candidate_rank"] == 1


def test_module_importable():
    assert importlib.import_module("backtest.return_analysis")
