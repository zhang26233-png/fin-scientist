import copy
import importlib

import pandas as pd

from strategy.event_confluence import (
    EVENT_CONFLUENCE_FIELDS,
    build_event_confluence_profile,
    build_event_confluence_row,
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


def assert_no_forbidden_words(value):
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
        "event_available": True,
        "event_type": "earnings",
        "event_reliability_label": "High",
        "event_diagnostic_level": "Strong",
        "event_confidence_score": 86,
        "event_diagnostic_summary": "Event evidence is complete enough for structured follow-up research.",
        "event_followup_questions": ["How does this earnings context connect to existing evidence?"],
        "event_evidence_gaps": [],
        "event_quality_warnings": [],
        "technical_grade": "A",
        "fundamental_grade": "A",
        "industry_relative_quality_label": "industry_relative_strong",
        "composite_research_grade": "A",
        "composite_research_level": "priority_research",
        "composite_risk_level": "low",
    }


def test_empty_input_safe_return():
    result = build_event_confluence_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == EVENT_CONFLUENCE_FIELDS
    assert_no_forbidden_words(result.to_dict())


def test_missing_event_fields_return_unavailable():
    result = build_event_confluence_row({"symbol": "MISS"})

    assert result["event_confluence_label"] == "Unavailable"
    assert result["event_confluence_score"] == 0
    assert result["event_support_points"] == []
    assert result["event_confluence_warnings"]
    assert_no_forbidden_words(result)


def test_high_quality_event_generates_confluence_fields():
    result = build_event_confluence_row(complete_row())

    assert result["event_confluence_label"] == "Supportive"
    assert result["event_confluence_score"] >= 70
    assert result["event_confluence_summary"]
    assert result["event_support_points"]
    assert isinstance(result["event_conflict_points"], list)
    assert result["event_followup_focus"]
    assert_no_forbidden_words(result)


def test_low_quality_event_outputs_warnings():
    row = complete_row()
    row["event_diagnostic_level"] = "Weak"
    row["event_confidence_score"] = 32
    row["event_reliability_label"] = "Low"
    row["event_quality_warnings"] = ["event reliability needs review"]

    result = build_event_confluence_row(row)

    assert result["event_confluence_label"] in {"Mixed", "Conflicting"}
    assert "event quality limits confluence review" in result["event_confluence_warnings"]
    assert result["event_confluence_score"] < build_event_confluence_row(complete_row())["event_confluence_score"]
    assert_no_forbidden_words(result)


def test_support_points_generated():
    result = build_event_confluence_row(complete_row())

    assert any("aligns" in point or "verify" in point for point in result["event_support_points"])
    assert_no_forbidden_words(result)


def test_conflict_points_generated():
    row = complete_row()
    row["event_type"] = "risk"

    result = build_event_confluence_row(row)

    assert result["event_confluence_label"] in {"Conflicting", "Mixed"}
    assert result["event_conflict_points"]
    assert_no_forbidden_words(result)


def test_input_object_is_not_modified():
    row = complete_row()
    before = copy.deepcopy(row)

    build_event_confluence_row(row)

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([complete_row("A"), complete_row("B"), complete_row("C")])
    result = build_event_confluence_profile(frame)

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["event_confluence_label"]) == ["Supportive", "Supportive", "Supportive"]


def test_scores_are_not_changed_by_event_confluence():
    row = complete_row()
    before = copy.deepcopy(row)

    build_event_confluence_row(row)

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]
    assert row["priority_stability_score"] == before["priority_stability_score"]
    assert row["architecture_audit_score"] == before["architecture_audit_score"]
    assert row["event_confidence_score"] == before["event_confidence_score"]


def test_neutral_wording():
    result = build_event_confluence_row(complete_row())

    assert_no_forbidden_words(result)


def test_module_importable():
    assert importlib.import_module("strategy.event_confluence")
