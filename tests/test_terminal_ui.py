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


def terminal_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "candidate_pool": "Core",
                "selection_bucket": "Core",
                "selection_rank": 1,
                "selection_score": 88,
                "selection_status": "Selected",
                "selection_quality_label": "Strong",
                "selection_thesis": "Quality Growth",
                "selection_summary": "Quality Growth, risk moderate",
                "selection_strengths": ["Strong Fundamental", "Strong Technical"],
                "selection_risks": ["High Volatility"],
                "selection_risk_notes": ["Risk level is Medium"],
                "selection_reasons": ["Composite score is strong"],
                "selection_factor_breakdown": {"fundamental_score": 82, "technical_score": 90},
                "candidate_risk_flags": ["Volatility Watch"],
                "fundamental_score": 82,
                "technical_score": 90,
                "composite_score": 86,
                "risk_score": 22,
                "period_return": 0.12,
                "annualized_return": 0.18,
                "volatility": 0.36,
                "max_drawdown": -0.16,
                "win_rate": 0.55,
                "return_risk_ratio": 0.75,
                "risk_level": "Medium",
                "performance_label": "Strong",
                "backtest_quality_label": "Good",
                "return_analysis_warnings": ["Price history has fewer than 60 valid rows."],
                "explain_status": "Available",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "selection_bucket": "Watch",
                "selection_rank": 2,
                "selection_score": 62,
                "selection_status": "Incomplete",
                "composite_score": 58,
                "fundamental_score": 55,
                "technical_score": 60,
                "period_return": -0.08,
                "annualized_return": -0.12,
                "max_drawdown": -0.28,
                "volatility": 0.48,
                "risk_level": "High",
                "performance_label": "Weak",
                "backtest_quality_label": "Watch",
                "selection_warnings": ["Selection fields incomplete."],
                "explain_status": "Unavailable",
            },
        ]
    )


def test_terminal_ui_module_importable():
    assert importlib.import_module("ui.terminal_ui")


def test_terminal_components_module_importable():
    assert importlib.import_module("ui.terminal_components")


def test_report_builder_module_importable():
    assert importlib.import_module("ui.report_builder")


def test_empty_dataframe_does_not_raise():
    summary = build_dashboard_summary(pd.DataFrame())
    compare = build_compare_frame(pd.DataFrame())
    risks = build_risk_center_tables(pd.DataFrame())

    assert summary["research_count"] == 0
    assert compare.empty
    assert risks["high_risk"].empty


def test_missing_selection_fields_does_not_raise():
    frame = pd.DataFrame([{"ticker": "600000", "name": "Missing Selection"}])

    summary = build_dashboard_summary(frame)
    compare = build_compare_frame(frame)

    assert summary["research_count"] == 1
    assert "ticker" in compare.columns


def test_missing_explain_fields_does_not_raise():
    frame = terminal_frame().drop(columns=["selection_thesis", "selection_summary", "selection_strengths", "selection_risks"])

    report = build_stock_research_report(frame.iloc[0])

    assert "研究报告预览" in report


def test_list_field_can_be_formatted():
    assert format_list_field(["A", "B"]) == "- A\n- B"


def test_dict_field_can_be_formatted():
    formatted = format_dict_field({"fundamental_score": 82, "technical_score": 90})

    assert "fundamental_score: 82.00" in formatted
    assert "technical_score: 90.00" in formatted


def test_warning_fields_can_be_collected():
    warnings = collect_warning_fields(terminal_frame().iloc[1])

    assert "Selection fields incomplete." in warnings
    assert "selection_status: Incomplete" in warnings
    assert "explain_status: Unavailable" in warnings


def test_build_stock_research_report_outputs_text():
    report = build_stock_research_report(terminal_frame().iloc[0])

    assert isinstance(report, str)
    assert "一、研究摘要" in report
    assert "七、后续观察问题" in report


def test_report_text_does_not_contain_buy_word():
    report = build_stock_research_report(terminal_frame().iloc[0])

    assert "买入" not in report


def test_report_text_does_not_contain_sell_word():
    report = build_stock_research_report(terminal_frame().iloc[0])

    assert "卖出" not in report


def test_report_text_does_not_contain_target_price_word():
    report = build_stock_research_report(terminal_frame().iloc[0])

    assert "目标价" not in report


def test_input_dataframe_is_not_modified():
    frame = terminal_frame()
    before = copy.deepcopy(frame)

    build_dashboard_summary(frame)
    build_compare_frame(frame, ["600000", "600001"])
    build_risk_center_tables(frame)
    build_stock_research_report(frame.iloc[0])

    pd.testing.assert_frame_equal(frame, before)


def test_app_importable():
    assert importlib.import_module("app")
