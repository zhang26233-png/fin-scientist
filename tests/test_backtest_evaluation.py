import copy
import importlib

import pandas as pd
import pytest

from backtest.backtest_evaluation import BACKTEST_EVALUATION_FIELDS, build_backtest_evaluation


def return_analysis_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "candidate_rank": 1,
                "composite_score": 85,
                "return_analysis_available": True,
                "return_analysis_status": "Available",
                "period_return": 0.12,
                "volatility": 0.18,
                "max_drawdown": -0.08,
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "candidate_rank": 2,
                "composite_score": 66,
                "return_analysis_available": True,
                "return_analysis_status": "Available",
                "period_return": -0.04,
                "volatility": 0.45,
                "max_drawdown": -0.30,
            },
        ]
    )


def expected_risk_score(period_return, max_drawdown, volatility):
    return round(min(100, min(abs(max_drawdown) * 120, 60) + min(volatility * 80, 35) + (15 if period_return < 0 else 0)), 2)


def test_empty_input_safe_return():
    output = build_backtest_evaluation(pd.DataFrame())

    assert output.empty
    assert set(BACKTEST_EVALUATION_FIELDS).issubset(output.columns)


def test_return_analysis_unavailable_returns_incomplete():
    frame = return_analysis_frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "return_analysis_available"] = False

    output = build_backtest_evaluation(frame)

    row = output.iloc[0]
    assert row["backtest_evaluation_available"] is False
    assert row["backtest_evaluation_status"] == "Incomplete"
    assert row["risk_score"] is None
    assert any("Return analysis is unavailable" in warning for warning in row["backtest_evaluation_warnings"])


def test_single_stock_generates_fields():
    output = build_backtest_evaluation(return_analysis_frame().iloc[[0]])

    assert len(output) == 1
    assert set(BACKTEST_EVALUATION_FIELDS).issubset(output.columns)
    assert output.iloc[0]["backtest_evaluation_available"] is True
    assert output.iloc[0]["backtest_evaluation_status"] == "Available"


def test_multiple_stocks_generate_fields():
    output = build_backtest_evaluation(return_analysis_frame())

    assert output["ticker"].tolist() == ["600000", "600001"]
    assert output["backtest_evaluation_status"].tolist() == ["Available", "Available"]


def test_risk_score_generated_correctly():
    output = build_backtest_evaluation(return_analysis_frame().iloc[[0]])

    assert output.iloc[0]["risk_score"] == pytest.approx(expected_risk_score(0.12, -0.08, 0.18))


def test_risk_level_generated_correctly():
    output = build_backtest_evaluation(return_analysis_frame())

    assert output["risk_level"].tolist() == ["Low", "High"]


def test_return_risk_ratio_calculated_correctly():
    output = build_backtest_evaluation(return_analysis_frame().iloc[[0]])

    assert output.iloc[0]["return_risk_ratio"] == pytest.approx(0.12 / 0.08)


def test_zero_max_drawdown_generates_warning():
    frame = return_analysis_frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "max_drawdown"] = 0.0

    output = build_backtest_evaluation(frame)

    row = output.iloc[0]
    assert row["return_risk_ratio"] is None
    assert any("max_drawdown is zero" in warning for warning in row["backtest_evaluation_warnings"])


def test_performance_label_generated_correctly():
    output = build_backtest_evaluation(return_analysis_frame())

    assert output["performance_label"].tolist() == ["Strong", "Weak"]


def test_backtest_quality_label_generated_correctly():
    good = build_backtest_evaluation(return_analysis_frame().iloc[[0]])
    watch_frame = return_analysis_frame().iloc[[0]].copy()
    watch_frame = watch_frame.drop(columns=["volatility"])
    poor_frame = return_analysis_frame().iloc[[0]].copy()
    poor_frame = poor_frame.drop(columns=["period_return", "max_drawdown"])

    watch = build_backtest_evaluation(watch_frame)
    poor = build_backtest_evaluation(poor_frame)

    assert good.iloc[0]["backtest_quality_label"] == "Good"
    assert watch.iloc[0]["backtest_quality_label"] == "Watch"
    assert poor.iloc[0]["backtest_quality_label"] == "Poor"


def test_missing_field_generates_warning():
    frame = return_analysis_frame().iloc[[0]].copy().drop(columns=["volatility"])

    output = build_backtest_evaluation(frame)

    row = output.iloc[0]
    assert row["backtest_evaluation_status"] == "Incomplete"
    assert any("volatility column missing" in warning for warning in row["backtest_evaluation_warnings"])


def test_input_object_is_not_modified():
    frame = return_analysis_frame()
    frame_before = copy.deepcopy(frame)

    build_backtest_evaluation(frame)

    pd.testing.assert_frame_equal(frame, frame_before)


def test_output_order_unchanged():
    output = build_backtest_evaluation(return_analysis_frame())

    assert output["ticker"].tolist() == ["600000", "600001"]


def test_existing_score_fields_are_not_modified():
    output = build_backtest_evaluation(return_analysis_frame().iloc[[0]])

    assert output.iloc[0]["composite_score"] == 85
    assert output.iloc[0]["candidate_rank"] == 1


def test_module_importable():
    assert importlib.import_module("backtest.backtest_evaluation")
