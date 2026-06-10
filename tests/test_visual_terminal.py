import copy
import importlib

import pandas as pd

from ui.report_builder import build_stock_research_report
from ui.terminal_components import (
    build_compare_frame,
    build_dashboard_summary,
    build_risk_center_tables,
    collect_warning_fields,
    format_dict_field,
    format_list_field,
)
from ui.visual_theme import get_risk_badge, get_score_badge, get_status_badge, get_terminal_css


def visual_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "selection_bucket": "Core",
                "selection_rank": 1,
                "selection_score": 88,
                "selection_status": "Selected",
                "selection_thesis": "Quality Growth",
                "selection_summary": "Quality Growth, risk moderate",
                "selection_strengths": ["Strong Fundamental", "Strong Technical"],
                "selection_risks": ["High Volatility"],
                "fundamental_score": 82,
                "technical_score": 90,
                "composite_score": 86,
                "risk_score": 22,
                "period_return": 0.12,
                "annualized_return": 0.18,
                "volatility": 0.36,
                "max_drawdown": -0.16,
                "risk_level": "Medium",
                "performance_label": "Strong",
                "return_analysis_warnings": ["Price history has fewer than 60 valid rows."],
                "explain_status": "Available",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "selection_bucket": "Watch",
                "selection_rank": 2,
                "selection_status": "Incomplete",
                "risk_level": "High",
                "max_drawdown": -0.28,
                "volatility": 0.48,
                "selection_warnings": ["Selection fields incomplete."],
                "explain_status": "Unavailable",
            },
        ]
    )


def test_visual_theme_importable():
    assert importlib.import_module("ui.visual_theme")


def test_visual_components_importable():
    assert importlib.import_module("ui.visual_components")


def test_get_terminal_css_returns_string():
    css = get_terminal_css()

    assert isinstance(css, str)
    assert ".fs-terminal-header" in css


def test_badge_functions_handle_expected_levels():
    for value in ["High", "Medium", "Low", "Unavailable"]:
        assert isinstance(get_score_badge(value), str)
        assert isinstance(get_risk_badge(value), str)
        assert isinstance(get_status_badge(value), str)


def test_list_field_can_be_formatted():
    assert format_list_field(["A", "B"]) == "- A\n- B"


def test_dict_field_can_be_formatted():
    formatted = format_dict_field({"fundamental_score": 82, "technical_score": 90})

    assert "fundamental_score: 82.00" in formatted
    assert "technical_score: 90.00" in formatted


def test_warning_summary_does_not_raise():
    warnings = collect_warning_fields(visual_frame().iloc[1])

    assert "Selection fields incomplete." in warnings
    assert "selection_status: Incomplete" in warnings


def test_empty_dataframe_does_not_raise():
    summary = build_dashboard_summary(pd.DataFrame())
    risks = build_risk_center_tables(pd.DataFrame())
    compare = build_compare_frame(pd.DataFrame())

    assert summary["research_count"] == 0
    assert risks["high_risk"].empty
    assert compare.empty


def test_missing_selection_fields_does_not_raise():
    frame = pd.DataFrame([{"ticker": "600000", "name": "Missing Selection"}])

    summary = build_dashboard_summary(frame)
    compare = build_compare_frame(frame)

    assert summary["research_count"] == 1
    assert "ticker" in compare.columns


def test_missing_explain_fields_does_not_raise():
    frame = visual_frame().drop(columns=["selection_thesis", "selection_summary", "selection_strengths", "selection_risks"])

    report = build_stock_research_report(frame.iloc[0])

    assert "研究报告预览" in report


def test_report_text_does_not_contain_buy_word():
    report = build_stock_research_report(visual_frame().iloc[0])

    assert "买入" not in report


def test_report_text_does_not_contain_sell_word():
    report = build_stock_research_report(visual_frame().iloc[0])

    assert "卖出" not in report


def test_report_text_does_not_contain_target_price_word():
    report = build_stock_research_report(visual_frame().iloc[0])

    assert "目标价" not in report


def test_input_dataframe_is_not_modified():
    frame = visual_frame()
    before = copy.deepcopy(frame)

    build_dashboard_summary(frame)
    build_compare_frame(frame, ["600000", "600001"])
    build_risk_center_tables(frame)
    build_stock_research_report(frame.iloc[0])

    pd.testing.assert_frame_equal(frame, before)


def test_app_importable():
    assert importlib.import_module("app")
