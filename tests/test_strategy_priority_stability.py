import copy
from pathlib import Path

import pandas as pd

from strategy.priority_stability import (
    PRIORITY_STABILITY_FIELDS,
    build_priority_stability_profile,
    build_priority_stability_row,
)


FORBIDDEN_WORDS = [
    "buy",
    "sell",
    "hold",
    "target price",
    "recommend",
    "strong buy",
    "\u6295\u8d44\u5efa\u8bae",
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6301\u6709",
    "\u76ee\u6807\u4ef7",
]


def assert_no_forbidden_words(value):
    text = str(value).lower()
    for word in FORBIDDEN_WORDS:
        assert word.lower() not in text


def stable_row(symbol="A"):
    return {
        "symbol": symbol,
        "strategy_score": 72,
        "research_priority_score": 68,
        "research_priority_level": "worth_tracking",
        "research_priority_reasons": ["field evidence available"],
        "research_priority_warnings": [],
    }


def test_empty_input_safe_return():
    result = build_priority_stability_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == PRIORITY_STABILITY_FIELDS
    assert_no_forbidden_words(result.to_dict())


def test_complete_priority_fields_generate_stability_fields():
    result = build_priority_stability_row(stable_row())

    assert result["priority_stability_label"] == "Stable"
    assert 0 <= result["priority_stability_score"] <= 100
    assert result["priority_stability_note"]
    assert result["priority_drift_detected"] is False
    assert result["priority_drift_reason"] == ""
    assert_no_forbidden_words(result)


def test_missing_priority_fields_outputs_unavailable():
    result = build_priority_stability_row({"symbol": "MISSING", "strategy_score": 50})

    assert result["priority_stability_label"] == "Unavailable"
    assert result["priority_stability_score"] == 0
    assert result["priority_drift_detected"] is True
    assert "research_priority_score" in result["priority_drift_reason"]
    assert_no_forbidden_words(result)


def test_input_object_is_not_modified():
    row = stable_row()
    before = copy.deepcopy(row)

    build_priority_stability_row(row)

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([stable_row("A"), stable_row("B"), stable_row("C")])
    result = build_priority_stability_profile(frame)

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["priority_stability_label"]) == ["Stable", "Stable", "Stable"]


def test_repeated_runs_are_idempotent():
    frame = pd.DataFrame([stable_row("A"), stable_row("B")])

    first = build_priority_stability_profile(frame)
    second = build_priority_stability_profile(frame)

    pd.testing.assert_frame_equal(first, second)


def test_stability_layer_does_not_change_strategy_or_priority_scores():
    row = stable_row()
    before = copy.deepcopy(row)

    build_priority_stability_row(row)

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]


def test_score_level_mismatch_marks_watch_without_overwriting_priority():
    row = stable_row()
    row["research_priority_score"] = 82
    row["research_priority_level"] = "low_priority"
    before = copy.deepcopy(row)

    result = build_priority_stability_row(row)

    assert result["priority_stability_label"] == "Watch"
    assert result["priority_drift_detected"] is True
    assert row == before
    assert_no_forbidden_words(result)


def test_reference_snapshot_drift_is_detected():
    row = stable_row()
    reference = stable_row()
    reference["research_priority_score"] = 58

    result = build_priority_stability_row(row, reference=reference)

    assert result["priority_stability_label"] == "Watch"
    assert result["priority_drift_detected"] is True
    assert "reference snapshot" in result["priority_drift_reason"]


def test_core_scoring_is_not_imported_or_modified_by_module():
    module_text = Path("strategy/priority_stability.py").read_text(encoding="utf-8")
    core_scoring_text = Path("core/scoring.py").read_text(encoding="utf-8")

    assert "core.scoring" not in module_text
    assert "priority_stability" not in core_scoring_text
    assert_no_forbidden_words(module_text)
