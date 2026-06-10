import copy
import importlib

import pandas as pd

from ui.workstation_components import format_value, safe_get
from ui.workstation_theme import get_workstation_css
from ui.workstation_ui import (
    build_compare_workspace,
    build_dashboard_metrics,
    build_factor_breakdown,
    build_navigator_groups,
    build_pipeline_status,
    get_selected_row,
    render_research_workstation,
)


def workstation_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "selection_bucket": "Core",
                "selection_level": "High",
                "selection_rank": 1,
                "selection_score": 88,
                "selection_status": "Selected",
                "selection_quality_label": "Strong",
                "selection_thesis": "Quality Growth",
                "selection_summary": "Quality Growth, risk moderate",
                "selection_strengths": ["Strong Fundamental", "Strong Technical"],
                "selection_risks": ["High Volatility"],
                "selection_factor_breakdown": {
                    "fundamental_score": 82,
                    "technical_score": 90,
                    "return_risk_ratio": 0.75,
                    "risk_score": 22,
                    "selection_quality_label": "Strong",
                },
                "fundamental_score": 82,
                "technical_score": 90,
                "composite_score": 86,
                "risk_score": 22,
                "risk_level": "Medium",
                "drawdown_risk_level": "Medium",
                "volatility_risk_level": "Medium",
                "return_risk_ratio": 0.75,
                "period_return": 0.12,
                "annualized_return": 0.18,
                "win_rate": 0.55,
                "max_drawdown": -0.16,
                "volatility": 0.36,
                "holding_period_days": 260,
                "explain_status": "Available",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "selection_bucket": "Watch",
                "selection_level": "Medium",
                "selection_score": 62,
                "selection_status": "Watch",
                "selection_quality_label": "Normal",
                "annualized_return": -0.08,
                "risk_score": 70,
                "risk_level": "High",
                "explain_status": "Unavailable",
            },
        ]
    )


def test_workstation_modules_importable():
    assert importlib.import_module("ui.workstation_ui")
    assert importlib.import_module("ui.workstation_components")
    assert importlib.import_module("ui.workstation_theme")


def test_workstation_theme_css_returns_string():
    css = get_workstation_css()

    assert isinstance(css, str)
    assert "#0E1117" in css


def test_safe_get_missing_returns_dash():
    row = pd.Series({"ticker": "600000"})

    assert safe_get(row, "missing") == "—"


def test_navigator_groups_are_generated():
    groups = build_navigator_groups(workstation_frame())

    assert len(groups["CORE"]) == 1
    assert len(groups["WATCH"]) == 1


def test_dashboard_metrics_are_generated():
    metrics = build_dashboard_metrics(workstation_frame())

    assert metrics["candidate_count"] == 2
    assert metrics["core_candidates"] == 1


def test_explain_missing_does_not_crash():
    frame = workstation_frame().drop(columns=["selection_thesis", "selection_strengths", "selection_risks", "selection_factor_breakdown"])
    row = get_selected_row(frame, "600000")

    factors = build_factor_breakdown(row)

    assert set(factors) == {"Fundamental", "Technical", "Backtest", "Risk", "Quality"}


def test_risk_missing_does_not_crash():
    frame = workstation_frame().drop(columns=["risk_score", "risk_level", "max_drawdown", "volatility"])
    row = get_selected_row(frame, "600000")
    pipeline = build_pipeline_status(row)

    assert pipeline[-1]["stage"] == "Explain Engine"


def test_compare_workspace_can_be_generated():
    compare = build_compare_workspace(workstation_frame(), ["600000", "600001"])

    assert len(compare) == 2
    assert "selection_score" in compare.columns


def test_report_preview_can_be_generated():
    payload = render_research_workstation(workstation_frame())

    assert isinstance(payload["report"], str)
    assert "研究报告预览" in payload["report"]


def test_empty_dataframe_does_not_crash():
    payload = render_research_workstation(pd.DataFrame())

    assert payload["metrics"]["candidate_count"] == 0


def test_format_value_handles_missing_and_percentages():
    assert format_value(None) == "—"
    assert format_value(0.12, "annualized_return") == "12.00%"


def test_input_dataframe_is_not_modified():
    frame = workstation_frame()
    before = copy.deepcopy(frame)

    build_dashboard_metrics(frame)
    build_navigator_groups(frame)
    build_compare_workspace(frame, ["600000", "600001"])
    render_research_workstation(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_app_importable():
    assert importlib.import_module("app")
