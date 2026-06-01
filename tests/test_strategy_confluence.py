import copy
import importlib

import pandas as pd

from strategy.confluence import CONFLUENCE_FIELDS, build_confluence_profile, build_confluence_row


FORBIDDEN_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
    "\u76ee\u6807\u4ef7",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_WORDS:
        assert word not in text


def test_confluence_module_imports():
    assert importlib.import_module("strategy.confluence")


def test_empty_input_safe_return():
    result = build_confluence_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == CONFLUENCE_FIELDS


def test_technical_and_fundamental_strong_outputs_resonance():
    row = build_confluence_row(
        {
            "technical_grade": "A",
            "technical_strength": "strong",
            "technical_risk_level": "low",
            "fundamental_grade": "A",
            "fundamental_research_level": "strong_candidate",
            "fundamental_profile_type": "quality_growth",
            "fundamental_confidence_level": "high",
        }
    )

    assert row["confluence_label"] == "fundamental_technical_resonance"
    assert 0 <= row["confluence_score"] <= 100
    assert row["confluence_strength_points"]
    assert_no_forbidden_words(row)


def test_fundamental_strong_technical_weak_label():
    row = build_confluence_row(
        {
            "technical_grade": "D",
            "technical_strength": "weak",
            "technical_risk_level": "medium",
            "fundamental_grade": "A",
            "fundamental_research_level": "strong_candidate",
            "fundamental_profile_type": "quality_growth",
            "fundamental_confidence_level": "high",
        }
    )

    assert row["confluence_label"] == "fundamental_strong_technical_weak"
    assert row["confluence_followup_focus"]


def test_technical_strong_fundamental_weak_label():
    row = build_confluence_row(
        {
            "technical_grade": "A",
            "technical_strength": "strong",
            "technical_risk_level": "low",
            "fundamental_grade": "D",
            "fundamental_research_level": "weak_or_risky",
            "fundamental_profile_type": "weak_fundamental",
            "fundamental_confidence_level": "medium",
        }
    )

    assert row["confluence_label"] == "technical_strong_fundamental_weak"
    assert row["confluence_risk_points"]


def test_technical_strong_with_high_fundamental_risk_label():
    row = build_confluence_row(
        {
            "technical_grade": "A",
            "technical_strength": "strong",
            "technical_risk_level": "medium",
            "fundamental_grade": "B",
            "fundamental_research_level": "weak_or_risky",
            "fundamental_profile_type": "cashflow_risk",
            "fundamental_confidence_level": "medium",
        }
    )

    assert row["confluence_label"] in {"high_risk_speculation", "mixed_signal"}
    assert row["confluence_risk_points"]


def test_insufficient_data_safe_return():
    row = build_confluence_row({"symbol": "EMPTY"})

    assert row["confluence_label"] == "insufficient_data"
    assert 0 <= row["confluence_score"] <= 100
    assert_no_forbidden_words(row)


def test_score_bounds_and_source_immutability():
    frame = pd.DataFrame(
        [
            {
                "technical_grade": "A",
                "technical_strength": "strong",
                "fundamental_grade": "A",
                "fundamental_research_level": "strong_candidate",
            },
            {
                "technical_grade": "D",
                "fundamental_grade": "D",
                "fundamental_research_level": "weak_or_risky",
            },
        ]
    )
    before = copy.deepcopy(frame)

    result = build_confluence_profile(frame)

    pd.testing.assert_frame_equal(frame, before)
    assert len(result) == 2
    assert all(0 <= score <= 100 for score in result["confluence_score"])
    assert_no_forbidden_words(result.to_dict())
