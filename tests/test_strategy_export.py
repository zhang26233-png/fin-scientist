import copy
from pathlib import Path

import pandas as pd

from strategy.export import (
    build_strategy_snapshot_payload,
    export_preset_comparison_snapshot,
    export_preset_pool_summary_snapshot,
)
from strategy.preset_comparison import compare_strategy_presets, summarize_preset_comparison_pool


FORBIDDEN_EXPORT_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_EXPORT_WORDS:
        assert word not in text


def make_frame():
    return pd.DataFrame(
        [
            {
                "symbol": "SNAP1",
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
            {"symbol": "MISS1"},
        ]
    )


def test_strategy_export_empty_inputs_safe_return():
    comparison_snapshot = export_preset_comparison_snapshot(None, generated_at="2026-05-28T00:00:00+00:00")
    summary_snapshot = export_preset_pool_summary_snapshot(None, generated_at="2026-05-28T00:00:00+00:00")

    assert comparison_snapshot["snapshot_type"] == "preset_comparison"
    assert summary_snapshot["snapshot_type"] == "preset_pool_summary"
    assert comparison_snapshot["schema_version"] == "1.0"
    assert summary_snapshot["warnings"]
    assert_no_forbidden_words({"comparison": comparison_snapshot, "summary": summary_snapshot})


def test_export_preset_comparison_snapshot_has_stable_fields():
    comparison = compare_strategy_presets(make_frame().iloc[[0]])
    snapshot = export_preset_comparison_snapshot(
        comparison,
        schema_version="1.0",
        generated_at="2026-05-28T00:00:00+00:00",
        metadata={"run_id": "unit"},
    )

    assert snapshot["schema_version"] == "1.0"
    assert snapshot["snapshot_type"] == "preset_comparison"
    assert snapshot["preset_scores"]
    assert snapshot["best_preset"]
    assert snapshot["worst_preset"]
    assert "score_spread" in snapshot
    assert "average_preset_score" in snapshot
    assert snapshot["metadata"]["run_id"] == "unit"
    assert snapshot["metadata"]["generated_at"] == "2026-05-28T00:00:00+00:00"
    assert_no_forbidden_words(snapshot)


def test_export_pool_summary_snapshot_has_stable_fields():
    summary = summarize_preset_comparison_pool(make_frame())
    snapshot = export_preset_pool_summary_snapshot(
        summary,
        schema_version="1.0",
        generated_at="2026-05-28T00:00:00+00:00",
        metadata={"batch_id": "pool"},
    )

    assert snapshot["schema_version"] == "1.0"
    assert snapshot["snapshot_type"] == "preset_pool_summary"
    assert snapshot["total_count"] == 2
    assert snapshot["valid_count"] + snapshot["insufficient_data_count"] == 2
    assert snapshot["dominant_style_counts"]
    assert snapshot["consensus_level_counts"]
    assert snapshot["average_scores_by_preset"]
    assert "summary_text" in snapshot
    assert snapshot["metadata"]["batch_id"] == "pool"
    assert_no_forbidden_words(snapshot)


def test_build_strategy_snapshot_payload_combines_snapshots():
    comparison = compare_strategy_presets(make_frame().iloc[[0]])
    summary = summarize_preset_comparison_pool(make_frame())
    payload = build_strategy_snapshot_payload(
        comparison=comparison,
        pool_summary=summary,
        metadata={"source": "unit-test"},
        generated_at="2026-05-28T00:00:00+00:00",
    )

    assert payload["snapshot_type"] == "strategy_snapshot_payload"
    assert payload["comparison"]["snapshot_type"] == "preset_comparison"
    assert payload["pool_summary"]["snapshot_type"] == "preset_pool_summary"
    assert payload["metadata"]["source"] == "unit-test"
    assert payload["metadata"]["generated_at"] == "2026-05-28T00:00:00+00:00"
    assert_no_forbidden_words(payload)


def test_strategy_export_does_not_modify_inputs():
    comparison = compare_strategy_presets(make_frame().iloc[[0]])
    summary = summarize_preset_comparison_pool(make_frame())
    comparison_before = copy.deepcopy(comparison)
    summary_before = copy.deepcopy(summary)

    export_preset_comparison_snapshot(comparison)
    export_preset_pool_summary_snapshot(summary)
    build_strategy_snapshot_payload(comparison=comparison, pool_summary=summary)

    assert comparison == comparison_before
    assert summary == summary_before


def test_strategy_export_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.export" not in legacy_text
    assert "strategy.export" not in screening_text
    assert "build_strategy_snapshot_payload" not in legacy_text
    assert "build_strategy_snapshot_payload" not in screening_text
