import copy
from pathlib import Path

from strategy.explanations import REASON_FIELDS, build_strategy_explanations, build_strategy_reason_fields


FORBIDDEN_EXPLANATION_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_EXPLANATION_WORDS:
        assert word not in text


def make_score_row():
    return {
        "identity": {"symbol": "RISK1", "name": "风险解释样本"},
        "trend_score": 65,
        "momentum_score": 55,
        "volume_price_score": 40,
        "liquidity_score": 30,
        "risk_penalty": 38,
        "data_quality_penalty": 22,
        "strategy_score": 20,
        "risk_labels": [
            "high_volatility",
            "extreme_upside_return",
            "volume_downside_risk",
            "overheated_turnover",
            "low_liquidity",
        ],
        "data_quality_labels": [
            "missing_price_fields",
            "missing_volume_fields",
            "missing_turnover_fields",
            "invalid_numeric_fields",
            "insufficient_factor_data",
        ],
    }


def test_strategy_explanations_import_and_empty_input_safe_return():
    result = build_strategy_explanations(None)

    assert result["status"] == "empty"
    assert result["items"] == []
    assert result["warnings"]
    assert result["metadata"]["read_only"] is True
    assert result["metadata"]["ui_connected"] is False
    assert_no_forbidden_words(result)


def test_strategy_explanations_handles_missing_fields_safely():
    result = build_strategy_explanations({"identity": {"symbol": "MISS1"}})

    assert result["status"] == "ok"
    assert result["items"]
    assert result["warnings"]
    assert result["penalty_breakdown"]["total_penalty"] == 0
    assert_no_forbidden_words(result)


def test_strategy_reason_fields_empty_and_missing_input_safe_return():
    empty = build_strategy_reason_fields(None)
    missing = build_strategy_reason_fields({"symbol": "MISS1"})

    assert set(REASON_FIELDS).issubset(empty)
    assert set(REASON_FIELDS).issubset(missing)
    assert empty["confidence_note"]
    assert missing["strategy_reason"]
    assert_no_forbidden_words(empty)
    assert_no_forbidden_words(missing)


def test_strategy_reason_fields_explain_trend_strength():
    result = build_strategy_reason_fields(
        {
            "strategy_score": 72,
            "trend_score": 82,
            "momentum_score": 68,
            "volume_price_score": 60,
            "liquidity_score": 62,
            "return_20d": 0.18,
            "close": 118,
            "ma5": 112,
            "ma10": 108,
            "ma20": 101,
            "dominant_style": "trend_momentum",
            "consensus_level": "broad_consensus_high",
        }
    )

    assert "趋势" in result["strategy_reason"]
    assert "20日/近期收益 18.0%" in result["trend_reason"]
    assert "均线" in result["trend_reason"]
    assert "可信度较高" in result["confidence_note"]
    assert_no_forbidden_words(result)


def test_strategy_reason_fields_explain_volume_price_confirmation():
    result = build_strategy_reason_fields(
        {
            "volume_price_score": 78,
            "amount": 150_000_000,
            "volume": 1_500_000,
            "volume_ratio": 1.6,
            "turnover": 0.04,
            "preset_bonus_reasons": ["volume_price_confirmed"],
            "best_preset": "volume_breakout",
        }
    )

    assert "量价互相确认" in result["volume_price_reason"]
    assert "volume_breakout" in result["preset_reason"]
    assert_no_forbidden_words(result)


def test_strategy_reason_fields_explain_risk_and_data_quality():
    result = build_strategy_reason_fields(
        {
            "risk_penalty": 38,
            "data_quality_penalty": 22,
            "risk_labels": ["high_volatility", "overheated_turnover"],
            "data_quality_labels": ["missing_price_fields", "invalid_numeric_fields"],
            "warnings": ["field warning"],
            "consensus_level": "mixed_signal",
        }
    )

    assert "高波动" in result["risk_reason"]
    assert "数值字段" in result["data_quality_reason"]
    assert "可信度有限" in result["confidence_note"]
    assert_no_forbidden_words(result)


def test_strategy_reason_fields_confidence_detects_preset_divergence():
    result = build_strategy_reason_fields({"consensus_level": "mixed_signal"})

    assert "分歧" in result["confidence_note"]
    assert_no_forbidden_words(result)


def test_strategy_explanations_generates_all_risk_label_explanations():
    result = build_strategy_explanations(make_score_row())
    labels = {item["label"] for item in result["risk_explanations"]}

    assert "high_volatility" in labels
    assert "extreme_upside_return" in labels
    assert "volume_downside_risk" in labels
    assert "overheated_turnover" in labels
    assert "low_liquidity" in labels
    assert all(item["message"] for item in result["risk_explanations"])
    assert_no_forbidden_words(result)


def test_strategy_explanations_generates_all_data_quality_label_explanations():
    result = build_strategy_explanations(make_score_row())
    labels = {item["label"] for item in result["data_quality_explanations"]}

    assert "missing_price_fields" in labels
    assert "missing_volume_fields" in labels
    assert "missing_turnover_fields" in labels
    assert "invalid_numeric_fields" in labels
    assert "insufficient_factor_data" in labels
    assert all(item["message"] for item in result["data_quality_explanations"])
    assert_no_forbidden_words(result)


def test_strategy_explanations_penalty_breakdown_is_auditable():
    row = make_score_row()
    row["preset_name"] = "volume_breakout"
    result = build_strategy_explanations(row)
    item = result["items"][0]

    assert item["penalty_breakdown"]["risk_penalty"]["value"] == 38
    assert item["penalty_breakdown"]["risk_penalty"]["level"] == "high"
    assert item["penalty_breakdown"]["data_quality_penalty"]["value"] == 22
    assert item["penalty_breakdown"]["data_quality_penalty"]["level"] == "medium"
    assert item["penalty_breakdown"]["total_penalty"] == 60
    assert result["penalty_breakdown"]["total_penalty"] == 60
    assert any(note["factor"] == "preset" for note in result["factor_notes"])


def test_strategy_explanations_accepts_score_result_and_does_not_modify_source():
    source = {"scores": [make_score_row()]}
    before = copy.deepcopy(source)

    result = build_strategy_explanations(source)

    assert result["status"] == "ok"
    assert len(result["items"]) == 1
    assert source == before


def test_strategy_explanations_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.explanations" not in legacy_text
    assert "build_strategy_explanations" not in legacy_text
    assert "strategy.explanations" not in screening_text
    assert "build_strategy_explanations" not in screening_text
