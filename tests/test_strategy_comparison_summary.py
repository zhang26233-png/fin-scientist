import copy
from pathlib import Path

import pandas as pd

from strategy.comparison import compare_strategy_scores, summarize_score_alignment


FORBIDDEN_SUMMARY_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def make_comparison_frame():
    return pd.DataFrame(
        [
            {"股票代码": "A001", "研究优先级评分": 75, "strategy_score": 72},
            {"股票代码": "A002", "研究优先级评分": 72, "strategy_score": 35},
            {"股票代码": "A003", "研究优先级评分": 32, "strategy_score": 70},
            {"股票代码": "A004", "研究优先级评分": 30, "strategy_score": 25},
            {"股票代码": "A005", "研究优先级评分": None, "strategy_score": 55},
            {"股票代码": "A006", "研究优先级评分": 55, "strategy_score": None},
        ]
    )


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_SUMMARY_WORDS:
        assert word not in text


def test_strategy_comparison_summary_empty_dataframe_safe_return():
    summary = summarize_score_alignment(pd.DataFrame())

    assert summary["total_count"] == 0
    assert summary["valid_count"] == 0
    assert summary["alignment_counts"] == {}
    assert summary["warnings"]
    assert_no_forbidden_words(summary)


def test_strategy_comparison_summary_single_result():
    result = compare_strategy_scores(pd.DataFrame([{"研究优先级评分": 75, "strategy_score": 72}]))
    summary = summarize_score_alignment(result)

    assert summary["total_count"] == 1
    assert summary["valid_count"] == 1
    assert summary["high_consensus_count"] == 1
    assert summary["average_original_score"] == 75
    assert summary["average_strategy_score"] == 72
    assert summary["average_score_gap"] == -3
    assert_no_forbidden_words(summary)


def test_strategy_comparison_summary_multiple_results_counts_and_averages():
    summary = summarize_score_alignment(make_comparison_frame())

    assert summary["total_count"] == 6
    assert summary["valid_count"] == 4
    assert summary["high_consensus_count"] == 1
    assert summary["research_high_strategy_low_count"] == 1
    assert summary["strategy_high_research_low_count"] == 1
    assert summary["low_consensus_count"] == 1
    assert summary["insufficient_data_count"] == 2
    assert summary["missing_original_score_count"] == 1
    assert summary["missing_strategy_score_count"] == 1
    assert summary["average_original_score"] == 52.8
    assert summary["average_strategy_score"] == 51.4
    assert summary["average_score_gap"] == -1.75
    assert_no_forbidden_words(summary)


def test_strategy_comparison_summary_ratios_are_reasonable():
    summary = summarize_score_alignment(make_comparison_frame())
    ratio_sum = sum(summary["alignment_ratios"].values())

    assert 0.999 <= ratio_sum <= 1.001
    assert summary["alignment_ratios"]["high_consensus"] == round(1 / 6, 4)
    assert summary["alignment_ratios"]["insufficient_data"] == round(2 / 6, 4)


def test_strategy_comparison_summary_accepts_comparison_list_and_does_not_modify_frame():
    frame = make_comparison_frame()
    before = copy.deepcopy(frame)
    comparisons = compare_strategy_scores(frame)["comparisons"]

    summary = summarize_score_alignment(comparisons)

    pd.testing.assert_frame_equal(frame, before)
    assert summary["total_count"] == 6
    assert_no_forbidden_words(summary)


def test_strategy_comparison_summary_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "summarize_score_alignment" not in legacy_text
    assert "summarize_score_alignment" not in screening_text
