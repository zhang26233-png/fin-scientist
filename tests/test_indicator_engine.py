import importlib

import pandas as pd

from technical.indicator_engine import REAL_TECHNICAL_INDICATOR_FIELDS, build_real_technical_indicators


def base_frame():
    return pd.DataFrame(
        [
            {"ticker": "600001", "activated_technical_score": 72},
            {"ticker": "600002", "activated_technical_score": 55},
        ]
    )


def make_history(days=260, start=10.0, step=0.05, volume=1_000_000, turnover=20_000_000):
    dates = pd.date_range("2025-01-01", periods=days, freq="D")
    close = [start + (index * step) for index in range(days)]
    return pd.DataFrame(
        {
            "date": dates,
            "open": [value * 0.99 for value in close],
            "high": [value * 1.02 for value in close],
            "low": [value * 0.98 for value in close],
            "close": close,
            "volume": [volume + (index % 20) * 10_000 for index in range(days)],
            "turnover": [turnover + (index % 20) * 100_000 for index in range(days)],
        }
    )


def test_empty_dataframe_safe_return():
    result = build_real_technical_indicators(pd.DataFrame())

    assert result.empty
    for field in REAL_TECHNICAL_INDICATOR_FIELDS:
        assert field in result.columns


def test_input_object_is_not_mutated():
    source = base_frame()
    original = source.copy(deep=True)

    build_real_technical_indicators(source, {"600001": make_history()})

    pd.testing.assert_frame_equal(source, original)


def test_no_price_history_dict_degrades_gracefully():
    result = build_real_technical_indicators(base_frame(), price_history_dict=None)

    assert result["technical_history_available"].eq(False).all()
    assert result["real_technical_score"].tolist() == [72.0, 55.0]


def test_history_under_60_days_adds_warning():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history(days=40)})

    assert result.iloc[0]["technical_history_available"] is False
    assert "历史行情不足" in result.iloc[0]["technical_indicator_warnings"]


def test_ma5_ma20_ma60_are_correct():
    history = make_history()
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": history})

    assert result.iloc[0]["ma5"] == round(history["close"].tail(5).mean(), 4)
    assert result.iloc[0]["ma20"] == round(history["close"].tail(20).mean(), 4)
    assert result.iloc[0]["ma60"] == round(history["close"].tail(60).mean(), 4)


def test_rsi14_is_between_0_and_100():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history()})

    assert 0 <= result.iloc[0]["rsi14"] <= 100


def test_macd_output_fields_exist():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history()})

    for field in ["macd_dif", "macd_dea", "macd_hist", "macd_signal"]:
        assert field in result.columns


def test_atr14_output_field_exists():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history()})

    assert "atr14" in result.columns
    assert result.iloc[0]["atr14"] is not None


def test_volatility_20d_is_non_negative():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history()})

    assert result.iloc[0]["volatility_20d"] >= 0


def test_max_drawdown_60d_is_not_positive():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history(step=-0.01, start=20)})

    assert result.iloc[0]["max_drawdown_60d"] <= 0


def test_volume_ratio_20d_is_correct():
    history = make_history()
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": history})
    expected = round(history["volume"].iloc[-1] / history["volume"].tail(20).mean(), 4)

    assert result.iloc[0]["volume_ratio_20d"] == expected


def test_turnover_ratio_20d_is_correct():
    history = make_history()
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": history})
    expected = round(history["turnover"].iloc[-1] / history["turnover"].tail(20).mean(), 4)

    assert result.iloc[0]["turnover_ratio_20d"] == expected


def test_position_52w_is_between_0_and_1():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history()})

    assert 0 <= result.iloc[0]["position_52w"] <= 1


def test_bullish_alignment_improves_trend_score():
    bullish = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history(step=0.08)})
    flat = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history(step=0)})

    assert bullish.iloc[0]["ma_bullish_alignment"] is True
    assert bullish.iloc[0]["technical_trend_score"] > flat.iloc[0]["technical_trend_score"]


def test_bearish_macd_lowers_momentum_score():
    bullish = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history(step=0.05)})
    bearish_history = make_history(start=30, step=0.0)
    bearish_history["close"] = [30.0 if index < 210 else 30.0 - ((index - 209) * 0.25) for index in range(len(bearish_history))]
    bearish_history["open"] = bearish_history["close"] * 1.01
    bearish_history["high"] = bearish_history["close"] * 1.02
    bearish_history["low"] = bearish_history["close"] * 0.98
    bearish = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": bearish_history})

    assert bearish.iloc[0]["macd_signal"] == "Bearish"
    assert bearish.iloc[0]["technical_momentum_score"] < bullish.iloc[0]["technical_momentum_score"]


def test_rsi_overheat_generates_risk_flag():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history(step=0.2)})

    assert "RSI过热" in result.iloc[0]["technical_risk_flags"]


def test_abnormal_volume_generates_risk_flag():
    history = make_history()
    history.loc[history.index[-1], "volume"] = history["volume"].tail(20).mean() * 8
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": history})

    assert "异常放量" in result.iloc[0]["technical_risk_flags"]


def test_real_technical_score_is_between_0_and_100():
    result = build_real_technical_indicators(base_frame().iloc[[0]], {"600001": make_history()})

    assert 0 <= result.iloc[0]["real_technical_score"] <= 100


def test_output_order_is_preserved():
    frame = base_frame()
    histories = {"600001": make_history(), "600002": make_history(start=20, step=-0.03)}

    result = build_real_technical_indicators(frame, histories)

    assert result["ticker"].tolist() == frame["ticker"].tolist()


def test_module_importable():
    assert importlib.import_module("technical.indicator_engine")
