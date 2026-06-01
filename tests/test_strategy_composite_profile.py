import copy
import importlib

import pandas as pd

from strategy.composite_profile import (
    COMPOSITE_PROFILE_FIELDS,
    build_composite_profile,
    build_composite_profile_row,
    derive_research_priority,
)


FORBIDDEN_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
    "\u76ee\u6807\u4ef7",
    "\u63a8\u8350\u4e70\u5165",
    "\u6284\u5e95",
    "\u6b62\u76c8",
    "\u6b62\u635f",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_WORDS:
        assert word not in text


def strong_sample():
    return {
        "technical_grade": "A",
        "technical_strength": "strong",
        "technical_risk_level": "low",
        "fundamental_grade": "A",
        "fundamental_quality_score": 82,
        "fundamental_research_level": "strong_candidate",
        "fundamental_profile_type": "quality_growth",
        "fundamental_risk_level": "low",
        "fundamental_confidence_level": "high",
        "industry_relative_quality_label": "industry_relative_strong",
        "strategy_score": 78,
        "consensus_level": "high",
        "risk_labels": [],
        "data_quality_labels": [],
        "warnings": [],
        "confluence_label": "fundamental_technical_resonance",
        "confluence_score": 84,
    }


def test_composite_module_imports():
    assert importlib.import_module("strategy.composite_profile")


def test_empty_input_safe_return():
    result = build_composite_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == COMPOSITE_PROFILE_FIELDS
    assert "research_priority_score" in COMPOSITE_PROFILE_FIELDS
    assert "research_priority_level" in COMPOSITE_PROFILE_FIELDS


def test_missing_technical_fields_safe_return():
    row = build_composite_profile_row({"fundamental_grade": "A", "fundamental_research_level": "strong_candidate"})

    assert row["composite_research_grade"] in {"B", "C", "insufficient_data"}
    assert row["composite_summary"]
    assert_no_forbidden_words(row)


def test_missing_fundamental_fields_safe_return():
    row = build_composite_profile_row({"technical_grade": "A", "technical_strength": "strong"})

    assert row["composite_research_grade"] in {"B", "C", "insufficient_data"}
    assert row["composite_summary"]
    assert_no_forbidden_words(row)


def test_strong_technical_fundamental_confluence_outputs_high_quality_or_priority():
    row = build_composite_profile_row(strong_sample())

    assert row["composite_research_style"] == "high_quality_resonance"
    assert row["composite_research_level"] in {"priority_research", "worth_tracking"}
    assert row["composite_research_grade"] in {"A", "B"}
    assert row["composite_strength_points"]
    assert row["research_priority_level"] == "priority_research"
    assert 0 <= row["research_priority_score"] <= 100


def test_technical_strong_fundamental_weak_outputs_speculation_watch():
    sample = strong_sample()
    sample.update(
        {
            "fundamental_grade": "D",
            "fundamental_research_level": "weak_or_risky",
            "fundamental_profile_type": "weak_fundamental",
            "fundamental_confidence_level": "medium",
            "confluence_label": "technical_strong_fundamental_weak",
        }
    )

    row = build_composite_profile_row(sample)

    assert row["composite_research_style"] in {"technical_speculation_with_weak_fundamental", "weak_or_high_risk"}
    assert row["composite_research_level"] in {"watch_with_caution", "low_priority"}
    assert row["composite_risk_points"]


def test_fundamental_strong_technical_weak_outputs_waiting_confirmation():
    sample = strong_sample()
    sample.update(
        {
            "technical_grade": "D",
            "technical_strength": "weak",
            "technical_risk_level": "medium",
            "confluence_label": "fundamental_strong_technical_weak",
            "confluence_score": 58,
        }
    )

    row = build_composite_profile_row(sample)

    assert row["composite_research_style"] == "fundamental_value_waiting_technical_confirmation"
    assert row["composite_research_grade"] in {"B", "C"}


def test_many_risk_labels_outputs_high_risk():
    sample = strong_sample()
    sample["risk_labels"] = ["high_volatility", "volume_downside_risk", "overheated_turnover"]

    row = build_composite_profile_row(sample)

    assert row["composite_risk_level"] == "high"


def test_bad_data_quality_lowers_confidence():
    sample = strong_sample()
    sample["data_quality_labels"] = ["missing_price_fields", "invalid_numeric_fields"]
    sample["warnings"] = ["field missing"]

    row = build_composite_profile_row(sample)

    assert row["composite_confidence_level"] == "low"
    assert row["composite_data_quality_note"]
    assert row["research_priority_level"] in {"watch_with_caution", "low_priority"}


def test_insufficient_data_outputs_insufficient():
    row = build_composite_profile_row({"symbol": "EMPTY"})

    assert row["composite_research_grade"] == "insufficient_data"
    assert row["composite_research_level"] == "insufficient_data"
    assert row["composite_confidence_level"] == "insufficient"
    assert row["research_priority_level"] == "insufficient_data"


def test_list_limits_source_immutability_and_neutral_wording():
    frame = pd.DataFrame([strong_sample(), {"symbol": "EMPTY"}])
    before = copy.deepcopy(frame)

    result = build_composite_profile(frame)

    pd.testing.assert_frame_equal(frame, before)
    assert len(result) == 2
    for _, row in result.iterrows():
        assert len(row["composite_strength_points"]) <= 4
        assert len(row["composite_risk_points"]) <= 4
        assert 2 <= len(row["composite_followup_focus"]) <= 4
        assert 0 <= row["research_priority_score"] <= 100
    assert_no_forbidden_words(result.to_dict())


def test_derive_research_priority_worth_tracking_case():
    priority = derive_research_priority(
        {
            "composite_research_grade": "B",
            "composite_research_style": "technical_momentum_with_fundamental_support",
            "composite_risk_level": "medium",
            "composite_confidence_level": "medium",
            "composite_strength_points": ["技术结构较强"],
            "composite_risk_points": [],
            "strategy_score": 63,
            "confluence_score": 62,
        }
    )

    assert priority["research_priority_level"] == "worth_tracking"
    assert priority["research_priority_reasons"]
    assert_no_forbidden_words(priority)


def test_derive_research_priority_high_risk_downgrade():
    priority = derive_research_priority(
        {
            "composite_research_grade": "A",
            "composite_research_style": "high_quality_resonance",
            "composite_risk_level": "high",
            "composite_confidence_level": "medium",
            "composite_risk_points": ["综合风险偏高"],
        }
    )

    assert priority["research_priority_level"] == "watch_with_caution"
    assert priority["research_priority_warnings"]


def test_strategy_score_is_not_changed_by_priority_derivation():
    profile = {
        "strategy_score": 72,
        "composite_research_grade": "A",
        "composite_research_style": "high_quality_resonance",
        "composite_risk_level": "low",
        "composite_confidence_level": "high",
    }
    before = copy.deepcopy(profile)

    derive_research_priority(profile)

    assert profile == before
    assert profile["strategy_score"] == 72
