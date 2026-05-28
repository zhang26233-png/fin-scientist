import copy
from pathlib import Path

import pandas as pd

from strategy.preset_comparison import compare_strategy_presets, summarize_preset_comparison_pool


FORBIDDEN_POOL_SUMMARY_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_POOL_SUMMARY_WORDS:
        assert word not in text


def make_pool_frame():
    return pd.DataFrame(
        [
            {
                "symbol": "TREND",
                "Close": 100,
                "return_20d": 0.18,
                "return_10d": 0.10,
                "return_5d": 0.04,
                "amount": 120_000_000,
                "volume": 1_200_000,
                "turnover": 0.04,
                "volume_ratio": 1.4,
                "volatility": 0.35,
                "valid_trading_days": 90,
            },
            {
                "symbol": "VOLUME",
                "Close": 100,
                "return_20d": 0.10,
                "return_10d": 0.04,
                "return_5d": 0.02,
                "amount": 220_000_000,
                "volume": 2_200_000,
                "turnover": 0.04,
                "volume_ratio": 1.8,
                "volatility": 0.32,
                "valid_trading_days": 90,
            },
            {
                "symbol": "LOWRISK",
                "Close": 100,
                "return_20d": 0.02,
                "return_10d": 0.01,
                "return_5d": 0.0,
                "amount": 180_000_000,
                "volume": 1_800_000,
                "turnover": 0.04,
                "volume_ratio": 1.0,
                "volatility": 0.18,
                "valid_trading_days": 90,
            },
            {
                "symbol": "ELASTIC",
                "Close": 100,
                "return_20d": 0.24,
                "return_10d": 0.14,
                "return_5d": 0.06,
                "amount": 180_000_000,
                "volume": 1_800_000,
                "turnover": 0.05,
                "volume_ratio": 1.7,
                "volatility": 0.70,
                "valid_trading_days": 90,
            },
            {"symbol": "MISSING"},
        ]
    )


def manual_counts(frame):
    style_counts = {}
    consensus_counts = {}
    spreads = []
    for _, row in frame.iterrows():
        comparison = compare_strategy_presets(pd.DataFrame([row.to_dict()]))
        style = comparison["dominant_style"]
        consensus = comparison["consensus_level"]
        style_counts[style] = style_counts.get(style, 0) + 1
        consensus_counts[consensus] = consensus_counts.get(consensus, 0) + 1
        if comparison["score_spread"] is not None:
            spreads.append(comparison["score_spread"])
    return style_counts, consensus_counts, spreads


def test_preset_pool_summary_empty_dataframe_safe_return():
    result = summarize_preset_comparison_pool(pd.DataFrame())

    assert result["status"] == "empty"
    assert result["total_count"] == 0
    assert result["valid_count"] == 0
    assert result["insufficient_data_count"] == 0
    assert result["warnings"]
    assert_no_forbidden_words(result)


def test_preset_pool_summary_missing_fields_safe_return():
    result = summarize_preset_comparison_pool(pd.DataFrame([{"symbol": "MISSING"}]))

    assert result["status"] == "ok"
    assert result["total_count"] == 1
    assert result["insufficient_data_count"] >= 0
    assert set(result["average_scores_by_preset"])
    assert_no_forbidden_words(result)


def test_preset_pool_summary_counts_and_ratios_are_stable():
    frame = make_pool_frame()
    result = summarize_preset_comparison_pool(frame)
    expected_styles, expected_consensus, spreads = manual_counts(frame)

    assert result["total_count"] == len(frame)
    assert result["valid_count"] + result["insufficient_data_count"] == len(frame)
    for style, count in expected_styles.items():
        assert result["dominant_style_counts"][style] == count
        assert result["dominant_style_ratios"][style] == round(count / len(frame), 4)
    for level, count in expected_consensus.items():
        assert result["consensus_level_counts"][level] == count
        assert result["consensus_level_ratios"][level] == round(count / len(frame), 4)
    assert result["average_score_spread"] == round(sum(spreads) / len(spreads), 2)
    assert result["max_score_spread"] == max(spreads)


def test_preset_pool_summary_average_scores_by_preset_are_stable():
    frame = make_pool_frame()
    result = summarize_preset_comparison_pool(frame)

    for preset_name, average in result["average_scores_by_preset"].items():
        values = []
        for _, row in frame.iterrows():
            comparison = compare_strategy_presets(pd.DataFrame([row.to_dict()]))
            match = [item for item in comparison["preset_scores"] if item["preset_name"] == preset_name]
            if match and isinstance(match[0]["strategy_score"], int):
                values.append(match[0]["strategy_score"])
        assert average == round(sum(values) / len(values), 2)


def test_preset_pool_summary_consensus_shortcut_counts():
    result = summarize_preset_comparison_pool(make_pool_frame())

    assert result["broad_consensus_high_count"] == result["consensus_level_counts"]["broad_consensus_high"]
    assert result["style_specific_high_count"] == result["consensus_level_counts"]["style_specific_high"]
    assert result["mixed_signal_count"] == result["consensus_level_counts"]["mixed_signal"]
    assert result["broad_consensus_low_count"] == result["consensus_level_counts"]["broad_consensus_low"]
    assert "summary_text" in result


def test_preset_pool_summary_does_not_modify_source_dataframe():
    frame = make_pool_frame()
    before = copy.deepcopy(frame)

    summarize_preset_comparison_pool(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_preset_pool_summary_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "summarize_preset_comparison_pool" not in legacy_text
    assert "summarize_preset_comparison_pool" not in screening_text
