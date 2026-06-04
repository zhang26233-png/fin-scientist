import copy
import importlib

import pandas as pd

from strategy.event_research_summary import (
    EVENT_RESEARCH_SUMMARY_FIELDS,
    build_event_research_summary_profile,
    build_event_research_summary_row,
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
        "event_confidence_score": 86,
        "event_confluence_score": 82,
        "event_available": True,
        "event_type": "earnings",
        "event_context_note": "earnings event context is available; recent timing may support follow-up evidence review.",
        "event_research_tags": ["earnings_check", "source_validation"],
        "event_diagnostic_level": "Strong",
        "event_diagnostic_summary": "Event evidence is complete enough for structured follow-up research.",
        "event_followup_questions": ["How does this earnings context connect to existing evidence?"],
        "event_evidence_gaps": [],
        "event_confluence_label": "Supportive",
        "event_confluence_summary": "Event context is broadly aligned with the current research profile.",
        "event_support_points": ["earnings context can help verify the fundamental profile"],
        "event_conflict_points": [],
        "event_followup_focus": ["Verify whether event evidence is reflected in fundamental fields."],
        "event_confluence_warnings": [],
    }


def test_empty_input_safe_return():
    result = build_event_research_summary_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == EVENT_RESEARCH_SUMMARY_FIELDS
    assert_no_forbidden_words(result.to_dict())


def test_missing_event_fields_return_unavailable():
    result = build_event_research_summary_row({"symbol": "MISS"})

    assert result["event_research_level"] == "Unavailable"
    assert result["event_key_evidence"] == []
    assert "event research summary unavailable" in result["event_summary_warnings"]
    assert_no_forbidden_words(result)


def test_complete_event_generates_summary_fields():
    result = build_event_research_summary_row(complete_row())

    assert result["event_research_level"] == "High"
    assert result["event_research_summary"]
    assert result["event_key_evidence"]
    assert isinstance(result["event_key_risks"], list)
    assert result["event_validation_focus"]
    assert result["event_agent_note"].startswith("Agent note:")
    assert_no_forbidden_words(result)


def test_key_evidence_generated():
    result = build_event_research_summary_row(complete_row())

    assert any("event type classified" in item for item in result["event_key_evidence"])
    assert any("earnings context" in item for item in result["event_key_evidence"])


def test_key_risks_generated():
    row = complete_row()
    row["event_conflict_points"] = ["event context differs from the current research profile"]
    row["event_evidence_gaps"] = ["event source missing"]

    result = build_event_research_summary_row(row)

    assert "event context differs from the current research profile" in result["event_key_risks"]
    assert "event source missing" in result["event_key_risks"]
    assert_no_forbidden_words(result)


def test_validation_focus_generated():
    result = build_event_research_summary_row(complete_row())

    assert any("Verify" in item or "connect" in item for item in result["event_validation_focus"])
    assert_no_forbidden_words(result)


def test_agent_note_generated():
    result = build_event_research_summary_row(complete_row())

    assert "confluence=Supportive" in result["event_agent_note"]
    assert "evidence_count=" in result["event_agent_note"]
    assert_no_forbidden_words(result)


def test_input_object_is_not_modified():
    row = complete_row()
    before = copy.deepcopy(row)

    build_event_research_summary_row(row)

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([complete_row("A"), complete_row("B"), complete_row("C")])
    result = build_event_research_summary_profile(frame)

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["event_research_level"]) == ["High", "High", "High"]


def test_scores_are_not_changed_by_event_research_summary():
    row = complete_row()
    before = copy.deepcopy(row)

    build_event_research_summary_row(row)

    assert row["event_confidence_score"] == before["event_confidence_score"]
    assert row["event_confluence_score"] == before["event_confluence_score"]
    assert row["strategy_score"] == before["strategy_score"]


def test_neutral_wording():
    result = build_event_research_summary_row(complete_row())

    assert_no_forbidden_words(result)


def test_module_importable():
    assert importlib.import_module("strategy.event_research_summary")
