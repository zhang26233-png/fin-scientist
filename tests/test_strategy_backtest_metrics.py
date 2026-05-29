import copy
from pathlib import Path

import pandas as pd

from strategy.backtest import (
    bucket_strategy_score,
    build_backtest_metrics_summary,
    summarize_backtest_by_consensus_level,
    summarize_backtest_by_dominant_style,
    summarize_backtest_by_preset,
    summarize_backtest_by_score_bucket,
)


FORBIDDEN_BACKTEST_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_BACKTEST_WORDS:
        assert word not in text


def metric_samples():
    return [
        {
            "symbol": "BT001",
            "preset_name": "balanced_research",
            "strategy_score": 82,
            "dominant_style": "trend_momentum",
            "consensus_level": "style_specific_high",
            "forward_return_1d": 0.01,
            "forward_return_3d": 0.03,
            "forward_return_5d": 0.05,
            "forward_return_10d": 0.08,
            "max_drawdown_forward": -0.02,
            "outcome_label": "positive_follow_through",
            "warnings": [],
        },
        {
            "symbol": "BT002",
            "preset_name": "balanced_research",
            "strategy_score": 60,
            "dominant_style": "trend_momentum",
            "consensus_level": "mixed",
            "forward_return_1d": -0.01,
            "forward_return_3d": -0.02,
            "forward_return_5d": -0.03,
            "forward_return_10d": -0.04,
            "max_drawdown_forward": -0.06,
            "outcome_label": "failed_follow_through",
            "warnings": [],
        },
        {
            "symbol": "BT003",
            "preset_name": "quality_research",
            "strategy_score": 40,
            "dominant_style": "quality_value",
            "consensus_level": "style_specific_high",
            "forward_return_1d": 0.0,
            "forward_return_3d": 0.004,
            "forward_return_5d": 0.008,
            "forward_return_10d": 0.01,
            "max_drawdown_forward": -0.01,
            "outcome_label": "weak_follow_through",
            "warnings": [],
        },
        {
            "symbol": "BT004",
            "preset_name": "quality_research",
            "strategy_score": None,
            "dominant_style": "quality_value",
            "consensus_level": "",
            "forward_return_1d": None,
            "forward_return_3d": None,
            "forward_return_5d": None,
            "forward_return_10d": None,
            "max_drawdown_forward": None,
            "outcome_label": "insufficient_data",
            "warnings": ["forward return data is insufficient"],
        },
    ]


def test_strategy_backtest_metrics_empty_input_safe_return():
    summary = build_backtest_metrics_summary([])

    assert summary["total_count"] == 0
    assert summary["valid_count"] == 0
    assert summary["insufficient_data_count"] == 0
    assert summary["outcome_counts"]["insufficient_data"] == 0
    assert summary["outcome_ratios"]["positive_follow_through"] == 0.0
    assert summary["average_forward_return_1d"] is None
    assert summary["by_preset"] == {}
    assert summary["by_score_bucket"]["high_score"]["total_count"] == 0
    assert summary["metadata"]["uses_real_data_source"] is False
    assert_no_forbidden_words(summary)


def test_strategy_backtest_metrics_missing_fields_safe_return():
    summary = build_backtest_metrics_summary([{"symbol": "BT005"}])

    assert summary["total_count"] == 1
    assert summary["valid_count"] == 0
    assert summary["insufficient_data_count"] == 1
    assert summary["by_preset"]["unknown_preset"]["total_count"] == 1
    assert summary["by_score_bucket"]["insufficient_score"]["total_count"] == 1
    assert summary["by_dominant_style"]["unknown_dominant_style"]["total_count"] == 1
    assert summary["by_consensus_level"]["unknown_consensus_level"]["total_count"] == 1
    assert_no_forbidden_words(summary)


def test_strategy_score_bucket_boundaries_are_stable():
    assert bucket_strategy_score(75) == "high_score"
    assert bucket_strategy_score(50) == "mid_score"
    assert bucket_strategy_score(49.99) == "low_score"
    assert bucket_strategy_score(None) == "insufficient_score"
    assert bucket_strategy_score("bad-score") == "insufficient_score"


def test_strategy_backtest_metrics_group_by_preset():
    by_preset = summarize_backtest_by_preset(metric_samples())

    assert by_preset["balanced_research"]["total_count"] == 2
    assert by_preset["balanced_research"]["outcome_counts"]["positive_follow_through"] == 1
    assert by_preset["quality_research"]["insufficient_data_count"] == 1
    assert by_preset["balanced_research"]["average_forward_return_10d"] == 0.02
    assert_no_forbidden_words(by_preset)


def test_strategy_backtest_metrics_group_by_score_bucket():
    by_bucket = summarize_backtest_by_score_bucket(metric_samples())

    assert by_bucket["high_score"]["total_count"] == 1
    assert by_bucket["mid_score"]["total_count"] == 1
    assert by_bucket["low_score"]["total_count"] == 1
    assert by_bucket["insufficient_score"]["total_count"] == 1
    assert by_bucket["high_score"]["outcome_ratios"]["positive_follow_through"] == 1.0
    assert_no_forbidden_words(by_bucket)


def test_strategy_backtest_metrics_group_by_dominant_style():
    by_style = summarize_backtest_by_dominant_style(metric_samples())

    assert by_style["trend_momentum"]["total_count"] == 2
    assert by_style["quality_value"]["total_count"] == 2
    assert by_style["quality_value"]["insufficient_data_count"] == 1
    assert_no_forbidden_words(by_style)


def test_strategy_backtest_metrics_group_by_consensus_level():
    by_consensus = summarize_backtest_by_consensus_level(metric_samples())

    assert by_consensus["style_specific_high"]["total_count"] == 2
    assert by_consensus["mixed"]["total_count"] == 1
    assert by_consensus["unknown_consensus_level"]["total_count"] == 1
    assert_no_forbidden_words(by_consensus)


def test_strategy_backtest_metrics_average_returns_and_drawdown_are_stable():
    summary = build_backtest_metrics_summary(metric_samples())

    assert summary["outcome_counts"]["positive_follow_through"] == 1
    assert summary["outcome_counts"]["failed_follow_through"] == 1
    assert summary["outcome_counts"]["weak_follow_through"] == 1
    assert summary["outcome_counts"]["insufficient_data"] == 1
    assert summary["outcome_ratios"]["positive_follow_through"] == 0.25
    assert summary["average_forward_return_1d"] == 0.0
    assert summary["average_forward_return_3d"] == 0.004667
    assert summary["average_forward_return_5d"] == 0.009333
    assert summary["average_forward_return_10d"] == 0.016667
    assert summary["average_max_drawdown_forward"] == -0.03
    assert summary["warnings"] == ["forward return data is insufficient"]
    assert_no_forbidden_words(summary)


def test_strategy_backtest_metrics_do_not_modify_source_dataframe():
    frame = pd.DataFrame(metric_samples())
    frame_before = copy.deepcopy(frame)

    build_backtest_metrics_summary(frame)

    pd.testing.assert_frame_equal(frame, frame_before)


def test_strategy_backtest_metrics_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.backtest" not in legacy_text
    assert "build_backtest_metrics_summary" not in legacy_text
    assert "strategy.backtest" not in screening_text
    assert "build_backtest_metrics_summary" not in screening_text
