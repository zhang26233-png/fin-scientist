import pandas as pd

from strategy.factors import (
    build_factor_snapshot,
    calculate_data_quality_factor,
    calculate_momentum_profile_factor,
    calculate_momentum_factor,
    calculate_moving_average_position_factor,
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
    assert calculate_moving_average_position_factor(empty)["score"] == "无法计算"
    assert calculate_momentum_profile_factor(empty)["score"] == "无法计算"
    assert calculate_data_quality_factor(empty)["score"] == 0


def test_strategy_factor_modules_handle_missing_fields():
    frame = pd.DataFrame({"Open": [1, 2, 3]})

    assert calculate_trend_factor(frame)["label"]
    assert calculate_volume_factor(frame)["label"]
    assert calculate_moving_average_position_factor(frame)["score"] == "无法计算"
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


def test_moving_average_position_factor_distinguishes_above_and_below_ma():
    above = pd.DataFrame({"Close": [120], "MA5": [110], "MA10": [105], "MA20": [100]})
    below = pd.DataFrame({"Close": [90], "MA5": [100], "MA10": [105], "MA20": [110]})

    above_result = calculate_moving_average_position_factor(above)
    below_result = calculate_moving_average_position_factor(below)

    assert above_result["score"] > below_result["score"]
    assert above_result["details"]["trend_direction_label"] == "短期趋势向上"
    assert below_result["details"]["trend_direction_label"] == "短期趋势向下"


def test_momentum_profile_factor_labels_moderate_overheated_and_weak_momentum():
    moderate = pd.DataFrame({"Close": list(range(100, 112)), "return_5d": [0.10] * 12})
    overheated = pd.DataFrame({"Close": list(range(100, 112)), "return_5d": [0.42] * 12})
    weak = pd.DataFrame({"Close": list(range(112, 100, -1)), "return_5d": [-0.08] * 12})

    moderate_result = calculate_momentum_profile_factor(moderate)
    overheated_result = calculate_momentum_profile_factor(overheated)
    weak_result = calculate_momentum_profile_factor(weak)

    assert moderate_result["details"]["momentum_label"] == "温和动量"
    assert overheated_result["details"]["momentum_label"] == "过热动量"
    assert weak_result["details"]["momentum_label"] in {"动量转弱", "连续走弱"}
    assert moderate_result["score"] > overheated_result["score"] > weak_result["score"]
