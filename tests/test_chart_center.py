import copy
import importlib

import pandas as pd

from ui.chart_center import (
    render_chart_center,
    render_score_profile,
)
from ui.chart_components import (
    build_candidate_ranking_data,
    build_return_risk_scatter_data,
    build_score_profile_data,
    safe_chart_df,
    safe_numeric,
)


def chart_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "fundamental_score": 82,
                "technical_score": 90,
                "composite_score": 86,
                "selection_score": 88,
                "risk_score": 22,
                "volatility": 0.36,
                "period_return": 0.12,
                "annualized_return": 0.18,
                "max_drawdown": -0.16,
                "risk_level": "Medium",
                "selection_bucket": "Core",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "fundamental_score": 55,
                "technical_score": 60,
                "composite_score": 58,
                "selection_score": 62,
                "risk_score": 70,
                "volatility": 0.48,
                "period_return": -0.08,
                "annualized_return": -0.12,
                "max_drawdown": -0.28,
                "risk_level": "High",
                "selection_bucket": "Watch",
            },
        ]
    )


def test_chart_center_importable():
    assert importlib.import_module("ui.chart_center")


def test_chart_components_importable():
    assert importlib.import_module("ui.chart_components")


def test_empty_dataframe_does_not_raise():
    payload = render_chart_center(pd.DataFrame())

    assert payload["candidate_ranking"].empty


def test_missing_score_fields_does_not_raise():
    frame = chart_frame().drop(columns=["fundamental_score", "technical_score", "composite_score", "selection_score"])

    profile = build_score_profile_data(frame.iloc[0])

    assert len(profile) == 5


def test_missing_return_fields_does_not_raise():
    frame = chart_frame().drop(columns=["period_return", "annualized_return"])

    scatter = build_return_risk_scatter_data(frame)

    assert scatter.empty


def test_safe_numeric_handles_none_string_and_number():
    assert safe_numeric(None) is None
    assert safe_numeric("12.5") == 12.5
    assert safe_numeric(8) == 8.0


def test_safe_chart_df_does_not_modify_input():
    frame = chart_frame()
    before = copy.deepcopy(frame)

    result = safe_chart_df(frame, ["ticker", "selection_score"])

    assert list(result.columns) == ["ticker", "selection_score"]
    pd.testing.assert_frame_equal(frame, before)


def test_ranking_data_can_be_generated():
    ranking = build_candidate_ranking_data(chart_frame(), top_n=1)

    assert len(ranking) == 1
    assert ranking.iloc[0]["label"] == "600000"


def test_scatter_data_can_be_generated():
    scatter = build_return_risk_scatter_data(chart_frame())

    assert len(scatter) == 2
    assert {"x_risk", "y_return"}.issubset(scatter.columns)


def test_score_profile_handles_single_row_data():
    profile = render_score_profile(chart_frame().iloc[0])

    assert len(profile) == 5
    assert "score_value" in profile.columns


def test_app_importable():
    assert importlib.import_module("app")
