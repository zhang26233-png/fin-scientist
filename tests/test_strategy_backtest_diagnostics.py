import copy
from pathlib import Path

from strategy.backtest import build_backtest_metrics_summary
from strategy.backtest_diagnostics import (
    build_backtest_diagnostics_report,
    diagnose_consensus_performance,
    diagnose_preset_performance,
    diagnose_score_bucket_performance,
    diagnose_style_performance,
    validate_backtest_metrics_schema,
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


def sample_summary(high_return=0.08, low_return=0.0):
    samples = [
        {
            "symbol": "BT001",
            "preset_name": "balanced_research",
            "strategy_score": 82,
            "dominant_style": "trend_momentum",
            "consensus_level": "broad_consensus_high",
            "forward_return_1d": high_return / 4,
            "forward_return_3d": high_return / 2,
            "forward_return_5d": high_return,
            "forward_return_10d": high_return,
            "max_drawdown_forward": -0.02,
            "outcome_label": "positive_follow_through",
            "warnings": [],
        },
        {
            "symbol": "BT002",
            "preset_name": "balanced_research",
            "strategy_score": 78,
            "dominant_style": "trend_momentum",
            "consensus_level": "broad_consensus_high",
            "forward_return_1d": high_return / 5,
            "forward_return_3d": high_return / 2,
            "forward_return_5d": high_return,
            "forward_return_10d": high_return,
            "max_drawdown_forward": -0.03,
            "outcome_label": "positive_follow_through",
            "warnings": [],
        },
        {
            "symbol": "BT003",
            "preset_name": "low_risk_quality",
            "strategy_score": 45,
            "dominant_style": "low_risk_quality",
            "consensus_level": "mixed_signal",
            "forward_return_1d": low_return,
            "forward_return_3d": low_return,
            "forward_return_5d": low_return,
            "forward_return_10d": low_return,
            "max_drawdown_forward": -0.01,
            "outcome_label": "weak_follow_through",
            "warnings": [],
        },
        {
            "symbol": "BT004",
            "preset_name": "low_risk_quality",
            "strategy_score": 42,
            "dominant_style": "low_risk_quality",
            "consensus_level": "mixed_signal",
            "forward_return_1d": low_return,
            "forward_return_3d": low_return,
            "forward_return_5d": low_return,
            "forward_return_10d": low_return,
            "max_drawdown_forward": -0.015,
            "outcome_label": "weak_follow_through",
            "warnings": [],
        },
    ]
    return build_backtest_metrics_summary(samples)


def test_strategy_backtest_diagnostics_imports_and_empty_summary_safe_return():
    summary = build_backtest_metrics_summary([])
    report = build_backtest_diagnostics_report(summary)

    assert report["schema_valid"] is True
    assert report["missing_fields"] == []
    assert "sample_count_insufficient" in report["data_quality_warnings"]
    assert report["score_bucket_diagnostics"]["distinction"] == "insufficient_sample"
    assert report["metadata"]["uses_real_data_source"] is False
    assert_no_forbidden_words(report)


def test_strategy_backtest_diagnostics_missing_fields_are_reported():
    validation = validate_backtest_metrics_schema({"total_count": 1})
    report = build_backtest_diagnostics_report({"total_count": 1})

    assert validation["schema_valid"] is False
    assert "valid_count" in validation["missing_fields"]
    assert "outcome_counts" in validation["missing_fields"]
    assert "by_score_bucket" in validation["missing_fields"]
    assert report["schema_valid"] is False
    assert_no_forbidden_words(report)


def test_strategy_backtest_diagnostics_complete_summary_schema_valid():
    summary = sample_summary()
    validation = validate_backtest_metrics_schema(summary)

    assert validation["schema_valid"] is True
    assert validation["missing_fields"] == []
    assert validation["metadata"]["ui_connected"] is False
    assert_no_forbidden_words(validation)


def test_strategy_backtest_diagnostics_detects_stronger_high_score_bucket():
    diagnostics = diagnose_score_bucket_performance(sample_summary(high_return=0.08, low_return=0.0))

    assert diagnostics["distinction"] == "high_score_stronger"
    assert diagnostics["high_score_average_forward_return"] == 0.08
    assert diagnostics["low_score_average_forward_return"] == 0.0
    assert "高分组在样本中表现相对更强" in diagnostics["observation"]
    assert_no_forbidden_words(diagnostics)


def test_strategy_backtest_diagnostics_detects_limited_score_bucket_distinction():
    diagnostics = diagnose_score_bucket_performance(sample_summary(high_return=0.012, low_return=0.0))

    assert diagnostics["distinction"] == "limited_distinction"
    assert "当前样本中高低分组区分度有限" in diagnostics["observation"]
    assert_no_forbidden_words(diagnostics)


def test_strategy_backtest_diagnostics_warns_when_score_bucket_samples_insufficient():
    summary = build_backtest_metrics_summary(
        [
            {
                "symbol": "BT001",
                "strategy_score": 80,
                "forward_return_5d": 0.03,
                "forward_return_10d": 0.04,
                "outcome_label": "positive_follow_through",
            }
        ]
    )
    diagnostics = diagnose_score_bucket_performance(summary)

    assert diagnostics["distinction"] == "insufficient_sample"
    assert "score_bucket_sample_insufficient" in diagnostics["warnings"]
    assert_no_forbidden_words(diagnostics)


def test_strategy_backtest_diagnostics_preset_observation_is_neutral():
    diagnostics = diagnose_preset_performance(sample_summary())

    assert diagnostics["diagnostic_type"] == "preset"
    assert diagnostics["group_count"] == 2
    assert diagnostics["ranked_groups"][0]["group"] == "balanced_research"
    assert "研究验证" in diagnostics["observation"]
    assert_no_forbidden_words(diagnostics)


def test_strategy_backtest_diagnostics_style_observation_is_neutral():
    diagnostics = diagnose_style_performance(sample_summary())

    assert diagnostics["diagnostic_type"] == "dominant_style"
    assert diagnostics["group_count"] == 2
    assert diagnostics["ranked_groups"][0]["group"] == "trend_momentum"
    assert_no_forbidden_words(diagnostics)


def test_strategy_backtest_diagnostics_consensus_observation_is_neutral():
    diagnostics = diagnose_consensus_performance(sample_summary())

    assert diagnostics["diagnostic_type"] == "consensus_level"
    assert diagnostics["group_count"] == 2
    assert diagnostics["ranked_groups"][0]["group"] == "broad_consensus_high"
    assert_no_forbidden_words(diagnostics)


def test_strategy_backtest_diagnostics_report_combines_sections():
    report = build_backtest_diagnostics_report(sample_summary())

    assert report["schema_valid"] is True
    assert report["score_bucket_diagnostics"]["distinction"] == "high_score_stronger"
    assert report["preset_diagnostics"]["group_count"] == 2
    assert report["style_diagnostics"]["group_count"] == 2
    assert report["consensus_diagnostics"]["group_count"] == 2
    assert report["summary_text"] == "Backtest metrics diagnostics completed for internal research validation."
    assert_no_forbidden_words(report)


def test_strategy_backtest_diagnostics_do_not_modify_source_object():
    summary = sample_summary()
    before = copy.deepcopy(summary)

    build_backtest_diagnostics_report(summary)

    assert summary == before


def test_strategy_backtest_diagnostics_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.backtest_diagnostics" not in legacy_text
    assert "build_backtest_diagnostics_report" not in legacy_text
    assert "strategy.backtest_diagnostics" not in screening_text
    assert "build_backtest_diagnostics_report" not in screening_text
