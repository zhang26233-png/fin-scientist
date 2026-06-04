import copy
from datetime import date

import pandas as pd

from strategy.event_context import (
    EVENT_CONTEXT_FIELDS,
    build_event_context_profile,
    build_event_context_row,
)
from strategy.preview import build_strategy_preview


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


def event_row(symbol="A"):
    return {
        "symbol": symbol,
        "name": f"Sample {symbol}",
        "score": 66,
        "strategy_score": 73,
        "research_priority_score": 81,
        "priority_stability_score": 95,
        "architecture_audit_score": 100,
        "event_title": "Quarter earnings update",
        "event_summary": "Revenue and profit data were disclosed for research verification.",
        "event_type": "earnings",
        "event_date": "2026-06-01",
        "event_source": "Official company announcement",
        "event_source_type": "official",
        "event_confidence": 0.86,
    }


def test_empty_input_safe_return():
    result = build_event_context_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == EVENT_CONTEXT_FIELDS
    assert_no_forbidden_words(result.to_dict())


def test_missing_event_fields_return_unavailable_unknown():
    result = build_event_context_row({"symbol": "MISS"})

    assert result["event_available"] is False
    assert result["event_type"] == "unknown"
    assert result["event_recency_label"] == "Unknown"
    assert result["event_source_quality_label"] == "Unknown"
    assert result["event_reliability_label"] == "Unknown"
    assert result["event_warnings"] == ["event input unavailable"]
    assert_no_forbidden_words(result)


def test_event_fields_generate_context():
    result = build_event_context_row(event_row(), today=date(2026, 6, 4))

    assert result["event_available"] is True
    assert result["event_type"] == "earnings"
    assert result["event_recency_label"] == "Recent"
    assert result["event_source_quality_label"] == "Official"
    assert result["event_reliability_label"] == "High"
    assert "earnings_check" in result["event_research_tags"]
    assert result["event_context_note"]
    assert_no_forbidden_words(result)


def test_input_object_is_not_modified():
    row = event_row()
    before = copy.deepcopy(row)

    build_event_context_row(row, today=date(2026, 6, 4))

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([event_row("A"), event_row("B"), event_row("C")])
    result = build_event_context_profile(frame, today=date(2026, 6, 4))

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["event_type"]) == ["earnings", "earnings", "earnings"]


def test_scores_are_not_changed_by_event_context():
    row = event_row()
    before = copy.deepcopy(row)

    build_event_context_row(row, today=date(2026, 6, 4))

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]
    assert row["priority_stability_score"] == before["priority_stability_score"]
    assert row["architecture_audit_score"] == before["architecture_audit_score"]


def test_preview_preserves_scores_when_event_fields_exist():
    frame = pd.DataFrame([event_row("EVT1"), event_row("EVT2")])
    preview = build_strategy_preview(frame)

    assert list(preview["symbol"]) == ["EVT1", "EVT2"]
    assert "event_available" in preview.columns
    assert preview["event_available"].tolist() == [True, True]
    assert preview["event_type"].tolist() == ["earnings", "earnings"]
    assert all(preview["strategy_score"].notna())
    assert all(preview["research_priority_score"].notna())
    assert all(preview["priority_stability_score"].notna())
    assert all(preview["architecture_audit_score"].notna())
    assert_no_forbidden_words(preview.to_dict())


def test_event_type_recognition_from_summary():
    cases = [
        ("Policy regulator guidance was released.", "policy"),
        ("Industry supply chain capacity changed.", "industry"),
        ("Macro inflation and rate data changed.", "macro"),
        ("Product launch and approval update.", "product"),
        ("Risk investigation disclosed.", "risk"),
        ("General company update.", "news_only"),
    ]

    for summary, expected in cases:
        result = build_event_context_row({"event_summary": summary})
        assert result["event_type"] == expected
        assert_no_forbidden_words(result)


def test_source_quality_recognition():
    assert build_event_context_row({"event_summary": "x", "event_source_type": "filing"})[
        "event_source_quality_label"
    ] == "Official"
    assert build_event_context_row({"event_summary": "x", "event_source_type": "media"})[
        "event_source_quality_label"
    ] == "Reliable Media"
    assert build_event_context_row({"event_summary": "x", "event_source_type": "social"})[
        "event_source_quality_label"
    ] == "Unverified"


def test_reliability_recognition():
    assert build_event_context_row({"event_summary": "x", "event_confidence": 0.9})[
        "event_reliability_label"
    ] == "High"
    assert build_event_context_row({"event_summary": "x", "event_confidence": 0.5})[
        "event_reliability_label"
    ] == "Medium"
    assert build_event_context_row({"event_summary": "x", "event_confidence": 0.2})[
        "event_reliability_label"
    ] == "Low"


def test_neutral_wording():
    result = build_event_context_row(event_row(), today=date(2026, 6, 4))

    assert_no_forbidden_words(result)
