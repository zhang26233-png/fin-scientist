import copy
from pathlib import Path

import pandas as pd

from strategy.comparison import compare_strategy_scores


FORBIDDEN_COMPARISON_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_COMPARISON_WORDS:
        assert word not in text


def make_comparison_frame():
    return pd.DataFrame(
        [
            {"股票代码": "A001", "研究优先级评分": 75, "strategy_score": 72},
            {"股票代码": "A002", "研究优先级评分": 72, "strategy_score": 35},
            {"股票代码": "A003", "研究优先级评分": 32, "strategy_score": 70},
            {"股票代码": "A004", "研究优先级评分": 30, "strategy_score": 25},
            {"股票代码": "A005", "研究优先级评分": None, "strategy_score": 55},
        ]
    )


def test_strategy_comparison_empty_dataframe_safe_return():
    result = compare_strategy_scores(pd.DataFrame())

    assert result["status"] == "empty"
    assert result["comparisons"] == []
    assert result["metadata"]["read_only"] is True
    assert_no_forbidden_words(result)


def test_strategy_comparison_missing_original_score_safe_return():
    result = compare_strategy_scores(pd.DataFrame([{"strategy_score": 60}]))
    item = result["comparisons"][0]

    assert item["alignment_label"] == "insufficient_data"
    assert item["original_score"] is None
    assert item["strategy_score"] == 60
    assert item["score_gap"] is None
    assert_no_forbidden_words(result)


def test_strategy_comparison_missing_strategy_score_safe_return():
    result = compare_strategy_scores(pd.DataFrame([{"研究优先级评分": 60}]))
    item = result["comparisons"][0]

    assert item["alignment_label"] == "insufficient_data"
    assert item["original_score"] == 60
    assert item["strategy_score"] is None
    assert item["score_gap"] is None
    assert_no_forbidden_words(result)


def test_strategy_comparison_alignment_labels_and_gaps():
    result = compare_strategy_scores(make_comparison_frame())
    labels = [item["alignment_label"] for item in result["comparisons"]]
    gaps = [item["score_gap"] for item in result["comparisons"]]

    assert labels == [
        "high_consensus",
        "research_high_strategy_low",
        "strategy_high_research_low",
        "low_consensus",
        "insufficient_data",
    ]
    assert gaps[:4] == [-3, -37, 38, -5]
    assert result["metadata"]["ranking_changed"] is False
    assert result["metadata"]["scoring_changed"] is False
    assert_no_forbidden_words(result)


def test_strategy_comparison_does_not_modify_source_dataframe():
    frame = make_comparison_frame()
    before = copy.deepcopy(frame)

    compare_strategy_scores(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_strategy_comparison_is_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.comparison" not in legacy_text
    assert "compare_strategy_scores" not in legacy_text
    assert "strategy.comparison" not in screening_text
    assert "compare_strategy_scores" not in screening_text
