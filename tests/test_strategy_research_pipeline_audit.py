import copy
import importlib

import pandas as pd

from strategy.research_pipeline_audit import (
    RESEARCH_PIPELINE_AUDIT_FIELDS,
    build_research_pipeline_audit_profile,
    build_research_pipeline_audit_row,
)


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
    }


def test_empty_input_safe_return():
    result = build_research_pipeline_audit_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == RESEARCH_PIPELINE_AUDIT_FIELDS


def test_missing_fields_return_incomplete():
    result = build_research_pipeline_audit_row({"symbol": "MISS"})

    assert result["research_pipeline_status"] == "Incomplete"
    assert result["research_pipeline_conflicts"] == []
    assert result["research_pipeline_warnings"]
    assert "technical_grade" in result["research_pipeline_warnings"][0]


def test_conflict_detection_composite_priority():
    row = complete_row()
    row["composite_research_grade"] = "D"
    row["research_priority_level"] = "priority_research"

    result = build_research_pipeline_audit_row(row)

    assert result["research_pipeline_status"] == "Conflict"
    assert any("priority" in item and "composite" in item for item in result["research_pipeline_conflicts"])


def test_incomplete_detection_event_confluence_summary():
    row = complete_row()
    row["event_confluence_label"] = "Supportive"
    row["event_research_level"] = "Unavailable"

    result = build_research_pipeline_audit_row(row)

    assert result["research_pipeline_status"] == "Incomplete"
    assert any("event confluence" in item for item in result["research_pipeline_warnings"])


def test_architecture_watch_status():
    row = complete_row()
    row["architecture_audit_label"] = "Review"

    result = build_research_pipeline_audit_row(row)

    assert result["research_pipeline_status"] == "Watch"
    assert "architecture audit requires review" in result["research_pipeline_warnings"]


def test_healthy_status():
    result = build_research_pipeline_audit_row(complete_row())

    assert result["research_pipeline_status"] == "Healthy"
    assert result["research_pipeline_conflicts"] == []
    assert result["research_pipeline_warnings"] == []


def test_input_object_is_not_modified():
    row = complete_row()
    before = copy.deepcopy(row)

    build_research_pipeline_audit_row(row)

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([complete_row("A"), complete_row("B"), complete_row("C")])
    result = build_research_pipeline_audit_profile(frame)

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["research_pipeline_status"]) == ["Healthy", "Healthy", "Healthy"]


def test_module_importable():
    assert importlib.import_module("strategy.research_pipeline_audit")


def test_scores_are_not_changed_by_research_pipeline_audit():
    row = complete_row()
    before = copy.deepcopy(row)

    build_research_pipeline_audit_row(row)

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]
    assert row["priority_stability_score"] == before["priority_stability_score"]
    assert row["architecture_audit_score"] == before["architecture_audit_score"]
    assert row["event_confidence_score"] == before["event_confidence_score"]
    assert row["event_confluence_score"] == before["event_confluence_score"]
