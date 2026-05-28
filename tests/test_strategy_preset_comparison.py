import copy
from pathlib import Path

import pandas as pd

from strategy.preset_comparison import compare_strategy_presets, summarize_preset_scores


FORBIDDEN_PRESET_COMPARISON_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


EXPECTED_PRESETS = {
    "balanced_research",
    "trend_momentum",
    "volume_breakout",
    "low_risk_quality",
    "high_elasticity_watch",
}


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_PRESET_COMPARISON_WORDS:
        assert word not in text


def make_row(**overrides):
    row = {
        "symbol": "SAMPLE",
        "Close": 100,
        "return_20d": 0.12,
        "return_10d": 0.06,
        "return_5d": 0.02,
        "amount": 120_000_000,
        "volume": 1_200_000,
        "turnover": 0.04,
        "volume_ratio": 1.3,
        "volatility": 0.35,
        "valid_trading_days": 90,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_preset_comparison_import_and_empty_input_safe_return():
    result = compare_strategy_presets(pd.DataFrame())

    assert result["status"] == "empty"
    assert result["preset_scores"] == []
    assert result["consensus_level"] == "insufficient_data"
    assert result["dominant_style"] == "insufficient_data"
    assert_no_forbidden_words(result)


def test_preset_comparison_missing_fields_safe_return():
    result = compare_strategy_presets(pd.DataFrame([{"symbol": "MISSING"}]))

    assert result["status"] == "ok"
    assert EXPECTED_PRESETS == {item["preset_name"] for item in result["preset_scores"]}
    assert result["score_spread"] is not None
    assert_no_forbidden_words(result)


def test_preset_comparison_generates_scores_for_all_default_presets():
    result = compare_strategy_presets(make_row())

    assert result["status"] == "ok"
    assert EXPECTED_PRESETS == {item["preset_name"] for item in result["preset_scores"]}
    assert all(0 <= item["strategy_score"] <= 100 for item in result["preset_scores"])
    assert result["best_preset"]["preset_name"] in EXPECTED_PRESETS
    assert result["worst_preset"]["preset_name"] in EXPECTED_PRESETS
    assert isinstance(result["average_preset_score"], float)


def test_preset_comparison_trend_momentum_dominant_style():
    result = compare_strategy_presets(
        make_row(return_20d=0.18, return_10d=0.10, return_5d=0.04, volume_ratio=1.4, amount=120_000_000)
    )

    assert result["dominant_style"] == "trend_momentum"
    assert result["best_preset"]["preset_name"] == "trend_momentum"


def test_preset_comparison_volume_breakout_dominant_style():
    result = compare_strategy_presets(
        make_row(return_20d=0.10, return_10d=0.04, return_5d=0.02, volume_ratio=1.8, amount=220_000_000, turnover=0.04)
    )

    assert result["dominant_style"] == "volume_breakout"
    assert result["best_preset"]["preset_name"] == "volume_breakout"


def test_preset_comparison_low_risk_quality_dominant_style():
    result = compare_strategy_presets(
        make_row(return_20d=0.02, return_10d=0.01, return_5d=0.0, volume_ratio=1.0, amount=180_000_000, volatility=0.18)
    )

    assert result["dominant_style"] == "low_risk_quality"
    assert result["best_preset"]["preset_name"] == "low_risk_quality"


def test_preset_comparison_high_elasticity_dominant_style():
    result = compare_strategy_presets(
        make_row(return_20d=0.24, return_10d=0.14, return_5d=0.06, volume_ratio=1.7, amount=180_000_000, volatility=0.70)
    )

    assert result["dominant_style"] == "high_elasticity"
    assert result["best_preset"]["preset_name"] == "high_elasticity_watch"


def test_preset_summary_consensus_levels_and_spread():
    broad_high = summarize_preset_scores(
        [
            {"preset_name": "balanced_research", "strategy_score": 72},
            {"preset_name": "trend_momentum", "strategy_score": 74},
            {"preset_name": "volume_breakout", "strategy_score": 70},
            {"preset_name": "low_risk_quality", "strategy_score": 68},
            {"preset_name": "high_elasticity_watch", "strategy_score": 73},
        ]
    )
    broad_low = summarize_preset_scores(
        [
            {"preset_name": "balanced_research", "strategy_score": 28},
            {"preset_name": "trend_momentum", "strategy_score": 35},
            {"preset_name": "volume_breakout", "strategy_score": 32},
            {"preset_name": "low_risk_quality", "strategy_score": 30},
            {"preset_name": "high_elasticity_watch", "strategy_score": 34},
        ]
    )
    mixed = summarize_preset_scores(
        [
            {"preset_name": "balanced_research", "strategy_score": 52},
            {"preset_name": "trend_momentum", "strategy_score": 76},
            {"preset_name": "volume_breakout", "strategy_score": 44},
            {"preset_name": "low_risk_quality", "strategy_score": 40},
            {"preset_name": "high_elasticity_watch", "strategy_score": 72},
        ]
    )

    assert broad_high["consensus_level"] == "broad_consensus_high"
    assert broad_low["consensus_level"] == "broad_consensus_low"
    assert mixed["consensus_level"] == "mixed_signal"
    assert mixed["score_spread"] == 36


def test_preset_comparison_does_not_modify_source():
    frame = make_row(symbol="IMMUTABLE")
    before = copy.deepcopy(frame)

    compare_strategy_presets(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_preset_comparison_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.preset_comparison" not in legacy_text
    assert "compare_strategy_presets" not in legacy_text
    assert "strategy.preset_comparison" not in screening_text
    assert "compare_strategy_presets" not in screening_text
