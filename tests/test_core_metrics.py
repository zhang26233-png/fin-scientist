import importlib
import math
import os

import pandas as pd


os.environ["FINSCIENTIST_SKIP_UI"] = "1"
app = importlib.import_module("app")


def make_price_frame(values):
    return pd.DataFrame(
        {
            "Close": values,
            "Volume": [1000] * len(values),
        },
        index=pd.date_range("2024-01-01", periods=len(values), freq="D"),
    )


def test_calculate_indicators_with_normal_data():
    data = make_price_frame(range(100, 170))
    metrics = app.calculate_indicators(data)

    assert metrics["data_points"] == 70
    assert metrics["latest_close"] == 169
    assert math.isfinite(metrics["return_20d"])
    assert math.isfinite(metrics["annual_volatility"])
    assert metrics["max_drawdown"] == 0


def test_calculate_indicators_with_empty_data():
    metrics = app.calculate_indicators(pd.DataFrame())

    assert metrics["data_points"] == 0
    assert math.isnan(metrics["latest_close"])
    assert math.isnan(metrics["return_20d"])
    assert math.isnan(metrics["annual_volatility"])


def test_calculate_indicators_with_missing_values():
    data = make_price_frame([100, None, 102, None, 104, 105] * 12)
    metrics = app.calculate_indicators(data)

    assert metrics["data_points"] == 48
    assert metrics["latest_close"] == 105
    assert math.isfinite(metrics["return_20d"])
    assert math.isnan(metrics["ma_60d"])


def test_extreme_drawdown_and_quality_check():
    data = make_price_frame([100, 130, 65, 70, 140, 30, 35])
    metrics = app.calculate_indicators(data)
    quality = app.check_price_data_quality(data)

    assert metrics["max_drawdown"] <= -0.75
    assert quality["异常日涨跌幅数量"] >= 3


def test_backtest_signals_empty_when_data_is_insufficient():
    data = make_price_frame(range(100, 115))
    result = app.generate_backtest_signals(data, "均线趋势策略", 0.001)

    assert result.empty


def test_backtest_signals_and_metrics_with_valid_data():
    data = make_price_frame(range(100, 180))
    result = app.generate_backtest_signals(data, "均线趋势策略", 0.001)
    metrics = app.calculate_backtest_metrics(result)

    assert not result.empty
    assert {
        "Close",
        "return",
        "signal",
        "position",
        "strategy_return",
        "benchmark_return",
        "strategy_nav",
        "benchmark_nav",
    }.issubset(result.columns)
    assert math.isfinite(metrics["strategy_total_return"])
    assert math.isfinite(metrics["strategy_max_drawdown"])
