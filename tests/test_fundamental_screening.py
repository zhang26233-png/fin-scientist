import copy
import importlib

import pandas as pd

from screening.fundamental_screening import FUNDAMENTAL_SCREENING_FIELDS, build_fundamental_screening


def universe_frame():
    return pd.DataFrame(
        [
            {"ticker": "600000", "name": "Sample A", "strategy_score": 42},
            {"ticker": "600001", "name": "Sample B", "strategy_score": 66},
        ]
    )


def high_fundamental_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "roe": 0.18,
                "revenue_growth": 0.20,
                "profit_growth": 0.22,
                "gross_margin": 0.42,
                "debt_ratio": 0.35,
                "operating_cashflow": 10_000_000,
                "pe": 25,
                "pb": 3,
            }
        ]
    )


def weak_fundamental_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "roe": 0.02,
                "revenue_growth": -0.05,
                "profit_growth": -0.10,
                "gross_margin": 0.08,
                "debt_ratio": 0.82,
                "operating_cashflow": -1_000_000,
                "pe": 120,
                "pb": 12,
            }
        ]
    )


def test_empty_universe_safe_return():
    output = build_fundamental_screening(pd.DataFrame())

    assert output.empty
    assert set(FUNDAMENTAL_SCREENING_FIELDS).issubset(output.columns)


def test_no_fundamental_data_returns_incomplete():
    output = build_fundamental_screening(universe_frame())

    assert output["fundamental_available"].tolist() == [False, False]
    assert output["fundamental_level"].tolist() == ["Unavailable", "Unavailable"]
    assert output["fundamental_screening_status"].tolist() == ["Incomplete", "Incomplete"]


def test_single_stock_generates_fields():
    output = build_fundamental_screening(universe_frame().iloc[[0]], high_fundamental_frame())

    assert len(output) == 1
    assert set(FUNDAMENTAL_SCREENING_FIELDS).issubset(output.columns)
    assert output.iloc[0]["roe"] == 0.18
    assert output.iloc[0]["fundamental_available"] is True


def test_high_quality_fundamental_outputs_high_pass():
    output = build_fundamental_screening(universe_frame().iloc[[0]], high_fundamental_frame())

    row = output.iloc[0]
    assert row["fundamental_level"] == "High"
    assert row["fundamental_screening_status"] == "Pass"
    assert row["fundamental_score"] >= 75


def test_weak_fundamental_outputs_low_watch_or_exclude():
    output = build_fundamental_screening(universe_frame().iloc[[0]], weak_fundamental_frame())

    row = output.iloc[0]
    assert row["fundamental_level"] == "Low"
    assert row["fundamental_screening_status"] in {"Watch", "Exclude"}
    assert row["fundamental_score"] < 50


def test_missing_fields_generate_warnings():
    output = build_fundamental_screening(
        universe_frame().iloc[[0]],
        pd.DataFrame([{"ticker": "600000", "roe": 0.16, "operating_cashflow": 1}]),
    )

    warnings = output.iloc[0]["fundamental_warnings"]
    assert any("Revenue growth missing" in warning for warning in warnings)
    assert any("PE missing" in warning for warning in warnings)
    assert output.iloc[0]["fundamental_available"] is True


def test_input_objects_are_not_modified():
    universe = universe_frame()
    fundamentals = high_fundamental_frame()
    universe_before = copy.deepcopy(universe)
    fundamentals_before = copy.deepcopy(fundamentals)

    build_fundamental_screening(universe, fundamentals)

    pd.testing.assert_frame_equal(universe, universe_before)
    pd.testing.assert_frame_equal(fundamentals, fundamentals_before)


def test_output_order_unchanged():
    output = build_fundamental_screening(
        universe_frame(),
        pd.DataFrame(
            [
                {"ticker": "600001", "roe": 0.20},
                {"ticker": "600000", "roe": 0.20},
            ]
        ),
    )

    assert output["ticker"].tolist() == ["600000", "600001"]


def test_old_strategy_score_field_is_preserved():
    output = build_fundamental_screening(universe_frame(), high_fundamental_frame())

    assert output["strategy_score"].tolist() == [42, 66]


def test_module_importable():
    assert importlib.import_module("screening.fundamental_screening")
