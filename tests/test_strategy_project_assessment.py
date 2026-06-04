import copy
import importlib

import pandas as pd

from strategy.project_assessment import (
    PROJECT_ASSESSMENT_FIELDS,
    build_project_assessment_profile,
    build_project_assessment_row,
)


FORBIDDEN_WORDS = [
    "buy",
    "sell",
    "hold",
    "target price",
    "recommend",
    "strong buy",
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6301\u6709",
    "\u76ee\u6807\u4ef7",
    "\u6295\u8d44\u5efa\u8bae",
]


def assert_no_forbidden_output_values(result):
    for value in result.values():
        text = str(value).lower()
        for word in FORBIDDEN_WORDS:
            assert word.lower() not in text


def complete_row(symbol="A"):
    return {
        "symbol": symbol,
        "strategy_score": 73,
        "research_priority_score": 81,
        "priority_stability_score": 95,
        "architecture_audit_score": 100,
        "event_confidence_score": 86,
        "event_confluence_score": 82,
        "technical_grade": "A",
        "fundamental_grade": "A",
        "industry_relative_quality_label": "industry_relative_strong",
        "composite_research_grade": "A",
        "research_priority_level": "priority_research",
        "priority_stability_label": "Stable",
        "architecture_audit_label": "Pass",
        "event_diagnostic_level": "Strong",
        "event_confluence_label": "Supportive",
        "event_research_level": "High",
        "research_pipeline_status": "Healthy",
    }


def test_empty_input_safe_return():
    result = build_project_assessment_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == PROJECT_ASSESSMENT_FIELDS


def test_single_candidate_generates_assessment_fields():
    result = build_project_assessment_row(complete_row())

    assert result["project_assessment_status"] in {"Ready", "Watch", "Not Ready"}
    assert 0 <= result["project_assessment_score"] <= 100
    assert result["architecture_assessment_note"]
    assert result["field_registry_assessment_note"]
    assert result["test_coverage_assessment_note"]
    assert result["ui_readability_assessment_note"]
    assert result["data_source_assessment_note"]
    assert result["scoring_boundary_assessment_note"]
    assert result["pre_v2_readiness_level"] in {"High", "Medium", "Low"}
    assert isinstance(result["pre_v2_blockers"], list)
    assert isinstance(result["pre_v2_recommendations"], list)
    assert_no_forbidden_output_values(result)


def test_missing_fields_output_blocker_or_warning():
    result = build_project_assessment_row({"symbol": "MISS"})

    assert result["project_assessment_status"] in {"Watch", "Not Ready"}
    assert result["pre_v2_blockers"] or "missing" in str(result).lower()
    assert_no_forbidden_output_values(result)


def test_input_object_is_not_modified():
    row = complete_row()
    before = copy.deepcopy(row)

    build_project_assessment_row(row)

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([complete_row("A"), complete_row("B"), complete_row("C")])
    result = build_project_assessment_profile(frame)

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["pre_v2_readiness_level"])


def test_scores_are_not_changed_by_project_assessment():
    row = complete_row()
    before = copy.deepcopy(row)

    build_project_assessment_row(row)

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]
    assert row["event_confluence_score"] == before["event_confluence_score"]
    assert row["priority_stability_score"] == before["priority_stability_score"]
    assert row["architecture_audit_score"] == before["architecture_audit_score"]
    assert row["event_confidence_score"] == before["event_confidence_score"]


def test_neutral_wording():
    result = build_project_assessment_row(complete_row())

    assert_no_forbidden_output_values(result)


def test_module_importable():
    assert importlib.import_module("strategy.project_assessment")
