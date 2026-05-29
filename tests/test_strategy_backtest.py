import copy
from pathlib import Path

import pandas as pd

from strategy.backtest import (
    build_backtest_metrics_summary,
    build_backtest_sample,
    calculate_forward_return,
    classify_backtest_outcome,
    summarize_backtest_samples,
    validate_backtest_input,
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


def candidate():
    return {
        "symbol": "BT001",
        "name": "Backtest Sample",
        "preset_name": "balanced_research",
        "strategy_score": 68,
        "dominant_style": "trend_momentum",
        "consensus_level": "style_specific_high",
    }


def test_strategy_backtest_empty_and_missing_input_safe_return():
    validation = validate_backtest_input({}, [])
    sample = build_backtest_sample({}, [])

    assert validation["valid"] is False
    assert sample["outcome_label"] == "insufficient_data"
    assert sample["warnings"]
    assert_no_forbidden_words(sample)


def test_strategy_backtest_forward_returns_are_stable():
    prices = [100, 102, 101, 103, 104, 105, 106, 107, 108, 109, 110]

    assert calculate_forward_return(prices, 1) == 0.02
    assert calculate_forward_return(prices, 3) == 0.03
    assert calculate_forward_return(prices, 5) == 0.05
    assert calculate_forward_return(prices, 10) == 0.10
    assert calculate_forward_return(prices, 11) is None


def test_strategy_backtest_builds_typical_sample():
    prices = [100, 101, 102, 103, 104, 106, 107, 108, 109, 110, 112]
    sample = build_backtest_sample(candidate(), prices, snapshot_date="2026-05-28", metadata={"run_id": "unit"})

    assert sample["symbol"] == "BT001"
    assert sample["snapshot_date"] == "2026-05-28"
    assert sample["preset_name"] == "balanced_research"
    assert sample["strategy_score"] == 68
    assert sample["forward_return_1d"] == 0.01
    assert sample["forward_return_10d"] == 0.12
    assert sample["outcome_label"] == "positive_follow_through"
    assert sample["metadata"]["run_id"] == "unit"
    assert_no_forbidden_words(sample)


def test_strategy_backtest_outcome_classification():
    assert classify_backtest_outcome(0.05, -0.02) == "positive_follow_through"
    assert classify_backtest_outcome(0.002, -0.01) == "weak_follow_through"
    assert classify_backtest_outcome(-0.03, -0.02) == "failed_follow_through"
    assert classify_backtest_outcome(0.04, -0.12) == "high_drawdown_risk"
    assert classify_backtest_outcome(None, None) == "insufficient_data"


def test_strategy_backtest_high_drawdown_overrides_positive_return():
    prices = [100, 112, 96, 98, 99, 104]
    sample = build_backtest_sample(candidate(), prices)

    assert sample["max_drawdown_forward"] <= -0.08
    assert sample["outcome_label"] == "high_drawdown_risk"


def test_strategy_backtest_insufficient_data_sample():
    sample = build_backtest_sample(candidate(), [100])

    assert sample["outcome_label"] == "insufficient_data"
    assert sample["forward_return_1d"] is None
    assert sample["warnings"]


def test_strategy_backtest_summarizes_outcome_distribution():
    samples = [
        build_backtest_sample(candidate(), [100, 102, 103, 104, 105, 106]),
        build_backtest_sample(candidate(), [100, 99, 98, 97, 96, 95]),
        build_backtest_sample(candidate(), [100]),
        build_backtest_sample(candidate(), [100, 112, 96, 98, 100, 102]),
    ]
    summary = summarize_backtest_samples(samples)

    assert summary["total_count"] == 4
    assert summary["outcome_label_counts"]["positive_follow_through"] == 1
    assert summary["outcome_label_counts"]["failed_follow_through"] == 1
    assert summary["outcome_label_counts"]["insufficient_data"] == 1
    assert summary["outcome_label_counts"]["high_drawdown_risk"] == 1
    assert summary["metadata"]["uses_real_data_source"] is False
    assert_no_forbidden_words(summary)


def test_strategy_backtest_builds_metrics_summary_by_research_dimensions():
    samples = [
        build_backtest_sample(candidate(), [100, 102, 103, 104, 105, 106]),
        build_backtest_sample({**candidate(), "strategy_score": 82}, [100, 99, 98, 97, 96, 95]),
        build_backtest_sample({**candidate(), "dominant_style": "quality_value"}, [100]),
    ]
    summary = build_backtest_metrics_summary(samples)

    assert summary["total_count"] == 3
    assert summary["by_preset"]["balanced_research"]["total_count"] == 3
    assert summary["by_score_bucket"]["high_score"]["total_count"] == 1
    assert summary["by_score_bucket"]["mid_score"]["total_count"] == 2
    assert summary["by_dominant_style"]["trend_momentum"]["total_count"] == 2
    assert summary["by_consensus_level"]["style_specific_high"]["total_count"] == 3
    assert summary["metadata"]["uses_real_data_source"] is False
    assert_no_forbidden_words(summary)


def test_strategy_backtest_does_not_modify_source_dataframe():
    frame = pd.DataFrame([candidate()])
    prices = pd.DataFrame({"close": [100, 102, 103, 104, 105, 106]})
    frame_before = copy.deepcopy(frame)
    prices_before = copy.deepcopy(prices)

    build_backtest_sample(frame.iloc[0], prices)

    pd.testing.assert_frame_equal(frame, frame_before)
    pd.testing.assert_frame_equal(prices, prices_before)


def test_strategy_backtest_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.backtest" not in legacy_text
    assert "build_backtest_sample" not in legacy_text
    assert "strategy.backtest" not in screening_text
    assert "build_backtest_sample" not in screening_text
