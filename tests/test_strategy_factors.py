import pandas as pd

from strategy.factors import (
    build_factor_snapshot,
    calculate_data_quality_factor,
    calculate_liquidity_factor,
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
    assert calculate_liquidity_factor(empty)["score"] == "无法计算"
    assert calculate_moving_average_position_factor(empty)["score"] == "无法计算"
    assert calculate_momentum_profile_factor(empty)["score"] == "无法计算"
    assert calculate_data_quality_factor(empty)["score"] == 0


def test_strategy_factor_modules_handle_missing_fields():
    frame = pd.DataFrame({"Open": [1, 2, 3]})

    assert calculate_trend_factor(frame)["label"]
    assert calculate_volume_factor(frame)["label"]
    assert calculate_liquidity_factor(frame)["score"] <= 50
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


def test_volume_price_factor_labels_confirmation_weakness_and_risks():
    confirmed = make_price_frame()
    confirmed["amount"] = 120_000_000
    confirmed["volume_ratio"] = 1.5
    confirmed["turnover"] = 0.03
    confirmed["return_20d"] = 0.12
    weak = confirmed.copy(deep=True)
    weak["volume_ratio"] = 0.55
    downside = confirmed.copy(deep=True)
    downside["return_20d"] = -0.08
    downside["volume_ratio"] = 1.8
    low_liquidity = confirmed.copy(deep=True)
    low_liquidity["amount"] = 2_000_000
    overheated = confirmed.copy(deep=True)
    overheated["turnover"] = 0.20

    confirmed_result = calculate_volume_price_factor(confirmed)
    weak_result = calculate_volume_price_factor(weak)
    downside_result = calculate_volume_price_factor(downside)
    low_result = calculate_volume_price_factor(low_liquidity)
    overheated_result = calculate_volume_price_factor(overheated)

    assert "volume_price_confirmed" in confirmed_result["details"]["volume_price_labels"]
    assert "volume_price_weak" in weak_result["details"]["volume_price_labels"]
    assert "volume_downside_risk" in downside_result["details"]["volume_price_labels"]
    assert "low_liquidity" in low_result["details"]["volume_price_labels"]
    assert "overheated_turnover" in overheated_result["details"]["volume_price_labels"]
    assert confirmed_result["score"] > weak_result["score"]
    assert confirmed_result["score"] > downside_result["score"]


def test_liquidity_factor_distinguishes_active_and_low_liquidity():
    active = make_price_frame()
    active["amount"] = 160_000_000
    active["turnover"] = 0.04
    low = active.copy(deep=True)
    low["amount"] = 1_000_000
    low["turnover"] = 0.001
    overheated = active.copy(deep=True)
    overheated["turnover"] = 0.20

    active_result = calculate_liquidity_factor(active)
    low_result = calculate_liquidity_factor(low)
    overheated_result = calculate_liquidity_factor(overheated)

    assert active_result["score"] > low_result["score"]
    assert "low_liquidity" in low_result["details"]["liquidity_labels"]
    assert "overheated_turnover" in overheated_result["details"]["liquidity_labels"]


def test_volume_price_and_liquidity_factors_handle_aliases_and_extreme_values():
    frame = make_price_frame()
    frame["turnover_amount"] = float("inf")
    frame["量比"] = float("inf")
    frame["turnover_rate"] = 0.04
    frame["return_20d"] = 0.08

    volume_price = calculate_volume_price_factor(frame)
    liquidity = calculate_liquidity_factor(frame)

    assert volume_price["factor"] == "volume_price"
    assert 0 <= volume_price["score"] <= 100
    assert liquidity["factor"] == "liquidity"
    assert 0 <= liquidity["score"] <= 100
