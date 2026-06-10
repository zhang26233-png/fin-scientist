import copy
import importlib

import pandas as pd

from factor.factor_lab import (
    FACTOR_OUTPUT_COLUMNS,
    build_factor_dataset,
    build_factor_groups,
    normalize_factor,
)
from factor.factor_report import build_factor_research_report


def factor_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "fundamental_score": 80,
                "technical_score": 70,
                "composite_score": 75,
                "selection_score": 90,
                "risk_score": 20,
                "return_risk_ratio": 1.2,
                "period_return": 0.12,
                "selection_bucket": "Core",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "fundamental_score": 60,
                "technical_score": 65,
                "composite_score": 62,
                "selection_score": 70,
                "risk_score": 40,
                "return_risk_ratio": 0.7,
                "period_return": 0.04,
                "selection_bucket": "Watch",
            },
            {
                "ticker": "600002",
                "name": "Sample C",
                "fundamental_score": 40,
                "technical_score": 45,
                "composite_score": 42,
                "selection_score": 50,
                "risk_score": 70,
                "return_risk_ratio": -0.2,
                "period_return": -0.03,
                "selection_bucket": "Exclude",
            },
        ]
    )


def test_factor_modules_importable():
    assert importlib.import_module("factor")
    assert importlib.import_module("factor.factor_lab")
    assert importlib.import_module("factor.factor_report")


def test_empty_input_returns_safe_dataframe():
    result = build_factor_dataset(pd.DataFrame())

    assert result.empty
    assert set(FACTOR_OUTPUT_COLUMNS).issubset(result.columns)


def test_missing_factor_field_does_not_raise():
    frame = factor_frame().drop(columns=["selection_score", "risk_score", "return_risk_ratio"])

    result = build_factor_dataset(frame)

    assert not result.empty
    assert "factor_name" in result.columns


def test_missing_return_field_does_not_raise_and_warns():
    frame = factor_frame().drop(columns=["period_return"])

    result = build_factor_dataset(frame)

    assert not result.empty
    assert any("future_return or period_return" in warning for warnings in result["factor_warnings"] for warning in warnings)


def test_zscore_calculation():
    result = normalize_factor(factor_frame(), ["selection_score"])

    values = result["selection_score_zscore"].round(6).tolist()
    assert values == [1.0, 0.0, -1.0]


def test_factor_group_generation():
    result = build_factor_groups(factor_frame(), "selection_score", n_groups=3)

    assert result["factor_group"].tolist() == ["Q3", "Q2", "Q1"]


def test_factor_dataset_contains_expected_fields():
    result = build_factor_dataset(factor_frame())

    assert set(FACTOR_OUTPUT_COLUMNS).issubset(result.columns)
    assert result["factor_name"].nunique() == 6
    assert result.iloc[0]["factor_effectiveness_label"] in {"Positive", "Weak", "Negative", "Unavailable"}


def test_factor_research_report_outputs_summary():
    report = build_factor_research_report(factor_frame(), "selection_score")

    assert report["factor_name"] == "selection_score"
    assert report["factor_effectiveness_label"] == "Positive"
    assert "neutral research observation" in report["factor_research_summary"]


def test_factor_research_report_handles_missing_factor():
    report = build_factor_research_report(factor_frame(), "missing_factor")

    assert report["factor_effectiveness_label"] == "Unavailable"
    assert report["factor_available"] is False


def test_input_object_not_modified():
    frame = factor_frame()
    before = copy.deepcopy(frame)

    build_factor_dataset(frame)
    normalize_factor(frame, ["selection_score"])
    build_factor_groups(frame, "selection_score")
    build_factor_research_report(frame, "selection_score")

    pd.testing.assert_frame_equal(frame, before)


def test_report_uses_neutral_wording():
    report = build_factor_research_report(factor_frame(), "selection_score")
    text = str(report)

    assert "买入" not in text
    assert "卖出" not in text
    assert "目标价" not in text
