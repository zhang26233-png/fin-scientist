import copy
import importlib

import pandas as pd

from screening.composite_score_engine import COMPOSITE_QUANT_SCORE_FIELDS, build_composite_quant_score


def universe_frame():
    return pd.DataFrame(
        [
            {"ticker": "600000", "name": "Sample A", "strategy_score": 42},
            {"ticker": "600001", "name": "Sample B", "strategy_score": 66},
        ]
    )


def fundamental_frame(score=78, ticker="600000"):
    return pd.DataFrame(
        [
            {
                "ticker": ticker,
                "fundamental_score": score,
                "fundamental_level": "Medium",
                "fundamental_screening_status": "Watch",
            }
        ]
    )


def technical_frame(score=82, ticker="600000"):
    return pd.DataFrame(
        [
            {
                "ticker": ticker,
                "technical_score": score,
                "technical_level": "High",
                "technical_screening_status": "Pass",
            }
        ]
    )


def test_empty_universe_safe_return():
    output = build_composite_quant_score(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    assert output.empty
    assert set(COMPOSITE_QUANT_SCORE_FIELDS).issubset(output.columns)


def test_missing_fundamental_returns_incomplete():
    output = build_composite_quant_score(universe_frame().iloc[[0]], None, technical_frame())

    row = output.iloc[0]
    assert row["composite_available"] is False
    assert row["composite_level"] == "Unavailable"
    assert row["composite_screening_status"] == "Incomplete"
    assert any("Fundamental screening row missing" in warning for warning in row["composite_warnings"])


def test_missing_technical_returns_incomplete():
    output = build_composite_quant_score(universe_frame().iloc[[0]], fundamental_frame(), None)

    row = output.iloc[0]
    assert row["composite_available"] is False
    assert row["composite_level"] == "Unavailable"
    assert row["composite_screening_status"] == "Incomplete"
    assert any("Technical screening row missing" in warning for warning in row["composite_warnings"])


def test_single_stock_generates_fields():
    output = build_composite_quant_score(universe_frame().iloc[[0]], fundamental_frame(), technical_frame())

    assert len(output) == 1
    assert set(COMPOSITE_QUANT_SCORE_FIELDS).issubset(output.columns)
    assert output.iloc[0]["composite_score"] == 80
    assert output.iloc[0]["composite_available"] is True


def test_high_score_outputs_high_pass():
    output = build_composite_quant_score(universe_frame().iloc[[0]], fundamental_frame(88), technical_frame(92))

    row = output.iloc[0]
    assert row["composite_score"] == 90
    assert row["composite_level"] == "High"
    assert row["composite_screening_status"] == "Pass"


def test_medium_score_outputs_medium_watch():
    output = build_composite_quant_score(universe_frame().iloc[[0]], fundamental_frame(62), technical_frame(70))

    row = output.iloc[0]
    assert row["composite_score"] == 66
    assert row["composite_level"] == "Medium"
    assert row["composite_screening_status"] == "Watch"


def test_low_score_outputs_low_watch():
    output = build_composite_quant_score(universe_frame().iloc[[0]], fundamental_frame(42), technical_frame(56))

    row = output.iloc[0]
    assert row["composite_score"] == 49
    assert row["composite_level"] == "Low"
    assert row["composite_screening_status"] == "Watch"


def test_exclude_output_correct():
    output = build_composite_quant_score(universe_frame().iloc[[0]], fundamental_frame(20), technical_frame(30))

    row = output.iloc[0]
    assert row["composite_score"] == 25
    assert row["composite_level"] == "Low"
    assert row["composite_screening_status"] == "Exclude"


def test_score_breakdown_generated_correctly():
    output = build_composite_quant_score(universe_frame().iloc[[0]], fundamental_frame(78), technical_frame(82))

    assert output.iloc[0]["score_breakdown"] == "Fundamental: 78; Technical: 82; Composite: 80"


def test_warnings_generated_for_missing_score_fields():
    output = build_composite_quant_score(
        universe_frame().iloc[[0]],
        pd.DataFrame([{"ticker": "600000"}]),
        technical_frame(82),
    )

    warnings = output.iloc[0]["composite_warnings"]
    assert any("fundamental_score missing or invalid" in warning for warning in warnings)
    assert output.iloc[0]["composite_screening_status"] == "Incomplete"


def test_input_objects_are_not_modified():
    universe = universe_frame()
    fundamental = fundamental_frame()
    technical = technical_frame()
    universe_before = copy.deepcopy(universe)
    fundamental_before = copy.deepcopy(fundamental)
    technical_before = copy.deepcopy(technical)

    build_composite_quant_score(universe, fundamental, technical)

    pd.testing.assert_frame_equal(universe, universe_before)
    pd.testing.assert_frame_equal(fundamental, fundamental_before)
    pd.testing.assert_frame_equal(technical, technical_before)


def test_output_order_unchanged():
    output = build_composite_quant_score(
        universe_frame(),
        pd.DataFrame([{"ticker": "600001", "fundamental_score": 90}, {"ticker": "600000", "fundamental_score": 80}]),
        pd.DataFrame([{"ticker": "600001", "technical_score": 90}, {"ticker": "600000", "technical_score": 80}]),
    )

    assert output["ticker"].tolist() == ["600000", "600001"]
    assert output["composite_score"].tolist() == [80, 90]


def test_fundamental_score_is_not_changed():
    universe = pd.DataFrame([{"ticker": "600000", "fundamental_score": 11}])
    output = build_composite_quant_score(universe, fundamental_frame(78), technical_frame(82))

    assert output.iloc[0]["fundamental_score"] == 11
    assert output.iloc[0]["composite_score"] == 80


def test_technical_score_is_not_changed():
    universe = pd.DataFrame([{"ticker": "600000", "technical_score": 22}])
    output = build_composite_quant_score(universe, fundamental_frame(78), technical_frame(82))

    assert output.iloc[0]["technical_score"] == 22
    assert output.iloc[0]["composite_score"] == 80


def test_module_importable():
    assert importlib.import_module("screening.composite_score_engine")
