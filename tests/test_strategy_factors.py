import pandas as pd

from strategy.factors import (
    build_factor_snapshot,
    calculate_data_quality_factor,
    calculate_momentum_factor,
    calculate_trend_factor,
    calculate_trend_direction_factor,
    calculate_volatility_factor,
    calculate_volume_factor,
    calculate_volume_price_factor,
)


def make_price_frame(rows=80):
    return pd.DataFrame(
        {
            "Close": [100 + index for index in range(rows)],
            "Volume": [1000 + index * 20 for index in range(rows)],
        },
        index=pd.date_range("2024-01-01", periods=rows, freq="D"),
    )


def test_strategy_factor_modules_handle_empty_dataframe():
    empty = pd.DataFrame()

    assert calculate_trend_factor(empty)["score"] == "无法计算"
    assert calculate_momentum_factor(empty)["score"] == "无法计算"
    assert calculate_volatility_factor(empty)["score"] == "无法计算"
    assert calculate_volume_factor(empty)["score"] == "无法计算"
    assert calculate_trend_direction_factor(empty)["score"] == "无法计算"
    assert calculate_volume_price_factor(empty)["score"] == "无法计算"
    assert calculate_data_quality_factor(empty)["score"] == 0


def test_strategy_factor_modules_handle_missing_fields():
    frame = pd.DataFrame({"Open": [1, 2, 3]})

    assert calculate_trend_factor(frame)["label"]
    assert calculate_volume_factor(frame)["label"]
    assert calculate_data_quality_factor(frame)["details"]["missing_columns"] == ["Close", "Volume"]


def test_strategy_factor_modules_return_stable_typical_results():
    frame = make_price_frame()

    trend = calculate_trend_factor(frame)
    momentum = calculate_momentum_factor(frame)
    volatility = calculate_volatility_factor(frame)
    volume = calculate_volume_factor(frame)
    trend_direction = calculate_trend_direction_factor(frame)
    volume_price = calculate_volume_price_factor(frame)
    data_quality = calculate_data_quality_factor(frame)
    snapshot = build_factor_snapshot(frame)

    assert trend["factor"] == "trend"
    assert trend["score"] == 100
    assert momentum["factor"] == "momentum"
    assert isinstance(momentum["details"]["return"], float)
    assert volatility["factor"] == "volatility"
    assert isinstance(volatility["score"], int)
    assert volume["factor"] == "volume"
    assert isinstance(volume["details"]["volume_ratio"], float)
    assert trend_direction["factor"] == "trend_direction"
    assert isinstance(trend_direction["score"], int)
    assert volume_price["factor"] == "volume_price"
    assert isinstance(volume_price["score"], int)
    assert data_quality["factor"] == "data_quality"
    assert data_quality["score"] == 100
    assert set(snapshot) == {"trend", "momentum", "volatility", "volume"}
