import copy
import importlib

import pandas as pd

from screening.technical_screening import TECHNICAL_SCREENING_FIELDS, build_technical_screening


def universe_frame():
    return pd.DataFrame(
        [
            {"ticker": "600000", "name": "Sample A", "fundamental_score": 82, "strategy_score": 42},
            {"ticker": "600001", "name": "Sample B", "fundamental_score": 35, "strategy_score": 66},
        ]
    )


def strong_price_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "close": 120,
                "ma20": 110,
                "ma60": 95,
                "rsi14": 55,
                "macd_signal": "Bullish",
                "volume_ratio": 1.4,
            }
        ]
    )


def weak_price_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "close": 80,
                "ma20": 90,
                "ma60": 100,
                "rsi14": 25,
                "macd_signal": "Bearish",
                "volume_ratio": 0.7,
            }
        ]
    )


def test_empty_universe_safe_return():
    output = build_technical_screening(pd.DataFrame())

    assert output.empty
    assert set(TECHNICAL_SCREENING_FIELDS).issubset(output.columns)


def test_no_price_data_returns_incomplete():
    output = build_technical_screening(universe_frame())

    assert output["technical_available"].tolist() == [False, False]
    assert output["technical_level"].tolist() == ["Unavailable", "Unavailable"]
    assert output["technical_screening_status"].tolist() == ["Incomplete", "Incomplete"]


def test_single_stock_generates_fields():
    output = build_technical_screening(universe_frame().iloc[[0]], strong_price_frame())

    assert len(output) == 1
    assert set(TECHNICAL_SCREENING_FIELDS).issubset(output.columns)
    assert output.iloc[0]["close"] == 120
    assert output.iloc[0]["above_ma20"] is True
    assert output.iloc[0]["technical_available"] is True


def test_strong_trend_outputs_high_pass():
    output = build_technical_screening(universe_frame().iloc[[0]], strong_price_frame())

    row = output.iloc[0]
    assert row["technical_level"] == "High"
    assert row["technical_screening_status"] == "Pass"
    assert row["technical_score"] >= 75


def test_weak_trend_outputs_low_watch_or_exclude():
    output = build_technical_screening(universe_frame().iloc[[0]], weak_price_frame())

    row = output.iloc[0]
    assert row["technical_level"] == "Low"
    assert row["technical_screening_status"] in {"Watch", "Exclude"}
    assert row["technical_score"] < 50


def test_rsi_abnormal_generates_warning():
    output = build_technical_screening(
        universe_frame().iloc[[0]],
        pd.DataFrame(
            [
                {
                    "ticker": "600000",
                    "close": 120,
                    "ma20": 110,
                    "ma60": 95,
                    "rsi14": 85,
                    "macd_signal": "Bullish",
                    "volume_ratio": 1.2,
                }
            ]
        ),
    )

    warnings = output.iloc[0]["technical_warnings"]
    assert any("RSI14 is abnormal" in warning for warning in warnings)


def test_macd_bearish_downgrades_score():
    bullish = build_technical_screening(universe_frame().iloc[[0]], strong_price_frame())
    bearish_input = strong_price_frame()
    bearish_input.loc[0, "macd_signal"] = "Bearish"
    bearish = build_technical_screening(universe_frame().iloc[[0]], bearish_input)

    assert bearish.iloc[0]["technical_score"] < bullish.iloc[0]["technical_score"]
    assert any("MACD signal is bearish" in warning for warning in bearish.iloc[0]["technical_warnings"])


def test_missing_fields_generate_warnings():
    output = build_technical_screening(
        universe_frame().iloc[[0]],
        pd.DataFrame([{"ticker": "600000", "close": 100, "macd_signal": "Neutral"}]),
    )

    warnings = output.iloc[0]["technical_warnings"]
    assert any("MA20 missing" in warning for warning in warnings)
    assert any("Volume ratio missing" in warning for warning in warnings)
    assert output.iloc[0]["technical_available"] is True


def test_input_objects_are_not_modified():
    universe = universe_frame()
    prices = strong_price_frame()
    universe_before = copy.deepcopy(universe)
    prices_before = copy.deepcopy(prices)

    build_technical_screening(universe, prices)

    pd.testing.assert_frame_equal(universe, universe_before)
    pd.testing.assert_frame_equal(prices, prices_before)


def test_output_order_unchanged_for_multiple_stocks():
    output = build_technical_screening(
        universe_frame(),
        pd.DataFrame(
            [
                {"ticker": "600001", "close": 130, "ma20": 120, "ma60": 110, "rsi14": 50, "macd_signal": "Bullish"},
                {"ticker": "600000", "close": 120, "ma20": 110, "ma60": 100, "rsi14": 50, "macd_signal": "Bullish"},
            ]
        ),
    )

    assert output["ticker"].tolist() == ["600000", "600001"]


def test_fundamental_score_is_preserved():
    output = build_technical_screening(universe_frame(), strong_price_frame())

    assert output["fundamental_score"].tolist() == [82, 35]
    assert output["strategy_score"].tolist() == [42, 66]


def test_price_history_dict_supported_and_module_importable():
    history = pd.DataFrame({"close": list(range(61, 126)), "volume": [100] * 64 + [160]})
    output = build_technical_screening(universe_frame().iloc[[0]], {"600000": history})

    assert importlib.import_module("screening.technical_screening")
    assert output.iloc[0]["technical_available"] is True
    assert output.iloc[0]["ma20"] > output.iloc[0]["ma60"]
