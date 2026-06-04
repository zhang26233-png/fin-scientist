import copy
import importlib

import pandas as pd

from strategy.event_context import build_event_context_row
from strategy.event_diagnostics import (
    EVENT_DIAGNOSTIC_FIELDS,
    build_event_diagnostics_profile,
    build_event_diagnostics_row,
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


def complete_event_row(symbol="A"):
    row = {
        "symbol": symbol,
        "strategy_score": 73,
        "research_priority_score": 81,
        "priority_stability_score": 95,
        "architecture_audit_score": 100,
        "event_title": "Quarter earnings update",
        "event_summary": "Revenue and profit data were disclosed for follow-up research verification.",
        "event_type": "earnings",
        "event_date": "2026-06-01",
        "event_source": "Official company announcement",
        "event_source_type": "official",
        "event_confidence": 0.86,
    }
    row.update(build_event_context_row(row))
    return row


def test_empty_input_safe_return():
    result = build_event_diagnostics_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == EVENT_DIAGNOSTIC_FIELDS
    assert_no_forbidden_words(result.to_dict())


def test_missing_event_fields_return_unavailable():
    result = build_event_diagnostics_row({"symbol": "MISS"})

    assert result["event_diagnostic_level"] == "Unavailable"
    assert result["event_completeness_score"] == 0
    assert result["event_confidence_score"] == 0
    assert "event evidence unavailable" in result["event_evidence_gaps"]
    assert_no_forbidden_words(result)


def test_complete_event_generates_diagnostic_fields():
    result = build_event_diagnostics_row(complete_event_row())

    assert result["event_diagnostic_level"] in {"Strong", "Usable"}
    assert result["event_completeness_score"] >= 85
    assert result["event_clarity_score"] >= 70
    assert result["event_consistency_score"] >= 80
    assert result["event_confidence_score"] >= 75
    assert result["event_diagnostic_summary"]
    assert isinstance(result["event_followup_questions"], list)
    assert isinstance(result["event_evidence_gaps"], list)
    assert isinstance(result["event_quality_warnings"], list)
    assert_no_forbidden_words(result)


def test_missing_event_source_creates_evidence_gap():
    row = complete_event_row()
    row.pop("event_source")
    row["event_source_quality_label"] = "Unknown"

    result = build_event_diagnostics_row(row)

    assert "event source missing" in result["event_evidence_gaps"]
    assert "event source needs validation" in result["event_quality_warnings"]
    assert result["event_confidence_score"] < 90
    assert_no_forbidden_words(result)


def test_missing_event_date_creates_evidence_gap():
    row = complete_event_row()
    row.pop("event_date")
    row["event_recency_label"] = "Unknown"

    result = build_event_diagnostics_row(row)

    assert "event date missing or invalid" in result["event_evidence_gaps"]
    assert result["event_completeness_score"] < 100
    assert_no_forbidden_words(result)


def test_unknown_event_type_lowers_clarity_or_level():
    row = complete_event_row()
    row["event_type"] = "unknown"
    row["event_warnings"] = ["event type needs classification review"]

    result = build_event_diagnostics_row(row)

    assert "event type needs clearer classification" in result["event_evidence_gaps"]
    assert result["event_clarity_score"] < build_event_diagnostics_row(complete_event_row())["event_clarity_score"]
    assert result["event_diagnostic_level"] in {"Usable", "Weak"}
    assert_no_forbidden_words(result)


def test_unreliable_source_lowers_confidence():
    strong = build_event_diagnostics_row(complete_event_row())
    row = complete_event_row()
    row["event_source_type"] = "social"
    row["event_source_quality_label"] = "Unverified"
    row["event_reliability_label"] = "Low"
    row["event_confidence"] = 0.2

    result = build_event_diagnostics_row(row)

    assert result["event_confidence_score"] < strong["event_confidence_score"]
    assert "event source needs validation" in result["event_quality_warnings"]
    assert "event reliability needs review" in result["event_quality_warnings"]
    assert_no_forbidden_words(result)


def test_input_object_is_not_modified():
    row = complete_event_row()
    before = copy.deepcopy(row)

    build_event_diagnostics_row(row)

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([complete_event_row("A"), complete_event_row("B"), complete_event_row("C")])
    result = build_event_diagnostics_profile(frame)

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["event_diagnostic_level"]) == ["Strong", "Strong", "Strong"]


def test_scores_are_not_changed_by_event_diagnostics():
    row = complete_event_row()
    before = copy.deepcopy(row)

    build_event_diagnostics_row(row)

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]
    assert row["priority_stability_score"] == before["priority_stability_score"]
    assert row["architecture_audit_score"] == before["architecture_audit_score"]


def test_neutral_wording():
    result = build_event_diagnostics_row(complete_event_row())

    assert_no_forbidden_words(result)


def test_module_importable():
    assert importlib.import_module("strategy.event_diagnostics")
