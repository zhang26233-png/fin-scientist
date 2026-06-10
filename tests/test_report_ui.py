import copy
import importlib

import pandas as pd

from ui.report_ui import (
    build_report_overview,
    build_report_tables,
    collect_warning_summary,
    format_report_value,
)


def report_frame():
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
                "selection_explanation": "Research explanation only.",
                "fundamental_score": 82,
                "technical_score": 90,
                "composite_score": 86,
                "risk_score": 22,
                "selection_factor_breakdown": {"fundamental_score": 82, "technical_score": 90},
                "period_return": 0.12,
                "annualized_return": 0.18,
                "volatility": 0.36,
                "max_drawdown": -0.16,
                "win_rate": 0.55,
                "return_risk_ratio": 0.75,
                "performance_label": "Strong",
                "backtest_quality_label": "Good",
                "selection_risk_notes": ["Risk level is Medium"],
                "backtest_evaluation_warnings": [],
                "return_analysis_warnings": ["Price history has fewer than 60 valid rows."],
                "explain_warnings": [],
                "explain_available": True,
                "explain_status": "Available",
            }
        ]
    )


def test_ui_module_importable():
    assert importlib.import_module("ui.report_ui")


def test_empty_dataframe_does_not_raise():
    overview = build_report_overview(pd.DataFrame())
    tables = build_report_tables(pd.DataFrame())

    assert overview["research_count"] == 0
    assert tables["candidate_overview"].empty
    assert tables["data_quality"].empty


def test_missing_selection_fields_does_not_raise():
    frame = pd.DataFrame([{"ticker": "600000", "name": "Missing Selection"}])

    overview = build_report_overview(frame)
    tables = build_report_tables(frame)

    assert overview["research_count"] == 1
    assert "ticker" in tables["candidate_overview"].columns


def test_missing_explain_fields_does_not_raise():
    frame = report_frame().drop(columns=["selection_thesis", "selection_summary", "selection_explanation"])

    tables = build_report_tables(frame)

    assert not tables["candidate_overview"].empty


def test_list_field_can_be_formatted():
    assert format_report_value(["A", "B"]) == "- A\n- B"


def test_dict_field_can_be_formatted():
    formatted = format_report_value({"fundamental_score": 82, "technical_score": 90})

    assert "fundamental_score: 82" in formatted
    assert "technical_score: 90" in formatted


def test_warnings_can_be_summarized():
    warnings = collect_warning_summary(report_frame())

    assert not warnings.empty
    assert "return_analysis_warnings" in warnings["field"].tolist()


def test_incomplete_and_unavailable_statuses_are_summarized():
    frame = report_frame()
    frame.loc[frame.index[0], "explain_status"] = "Incomplete"

    warnings = collect_warning_summary(frame)

    assert "explain_status" in warnings["field"].tolist()


def test_input_dataframe_is_not_modified():
    frame = report_frame()
    before = copy.deepcopy(frame)

    build_report_overview(frame)
    build_report_tables(frame)
    collect_warning_summary(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_app_importable():
    assert importlib.import_module("app")
