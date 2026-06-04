import copy
from pathlib import Path

import pandas as pd

from strategy.preview import (
    PREVIEW_COLUMNS,
    build_strategy_preview,
    build_strategy_preview_row,
    export_strategy_preview_to_csv,
    export_strategy_preview_to_json_like,
)


FORBIDDEN_STRATEGY_PREVIEW_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_STRATEGY_PREVIEW_WORDS:
        assert word not in text


def make_candidate_pool():
    return pd.DataFrame(
        [
            {
                "symbol": "LOW1",
                "name": "Low Sample",
                "Close": 100,
                "return_20d": -0.08,
                "return_10d": -0.04,
                "return_5d": -0.02,
                "volume": 60_000,
                "amount": 3_000_000,
                "turnover": 0.001,
                "volume_ratio": 0.7,
                "volatility": 0.35,
                "valid_trading_days": 90,
                "score": 42,
                "industry": "制造业",
                "roe": 0.08,
                "gross_margin": "20%",
                "net_profit": 20_000_000,
                "operating_cashflow": 10_000_000,
                "revenue_growth": "3%",
                "profit_growth": "1%",
                "pe": 24,
                "pb": 2.8,
                "ps": 5,
                "debt_ratio": "60%",
            },
            {
                "symbol": "HIGH1",
                "name": "High Sample",
                "Close": 100,
                "return_20d": 0.16,
                "return_10d": 0.09,
                "return_5d": 0.04,
                "volume": 1_500_000,
                "amount": 160_000_000,
                "turnover": 0.04,
                "volume_ratio": 1.4,
                "volatility": 0.25,
                "valid_trading_days": 90,
                "score": 66,
                "MA5": 98,
                "MA10": 95,
                "MA20": 90,
                "recent_high": 101,
                "revenue": "1.2亿",
                "net_profit": "3,500万",
                "gross_margin": "35%",
                "roe": 0.18,
                "pe": 18,
                "pb": 2.1,
                "ps": 4.2,
                "debt_ratio": "45%",
                "operating_cashflow": "2,000万",
                "revenue_growth": "12%",
                "profit_growth": "8%",
                "market_cap": "360亿",
                "industry": "制造业",
            },
            {
                "symbol": "RISK1",
                "name": "Risk Sample",
                "Close": 100,
                "return_20d": 0.42,
                "return_10d": 0.28,
                "return_5d": 0.18,
                "volume": 1_800_000,
                "amount": 200_000_000,
                "turnover": 0.18,
                "volume_ratio": 2.2,
                "volatility": 0.95,
                "valid_trading_days": 90,
                "score": 72,
                "industry": "制造业",
                "roe": -0.02,
                "gross_margin": "12%",
                "net_profit": -10_000_000,
                "operating_cashflow": -20_000_000,
                "revenue_growth": "-5%",
                "profit_growth": "-12%",
                "pe": -6,
                "pb": 8,
                "ps": 10,
                "debt_ratio": "88%",
            },
        ]
    )


def test_strategy_preview_import_and_empty_dataframe_safe_return():
    preview = build_strategy_preview(pd.DataFrame())

    assert list(preview.columns) == PREVIEW_COLUMNS
    assert preview.empty
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_missing_fields_safe_return():
    preview = build_strategy_preview(pd.DataFrame([{"symbol": "MISSING"}]))

    assert len(preview) == 1
    assert preview.iloc[0]["symbol"] == "MISSING"
    assert preview.iloc[0]["strategy_score"] == 0
    assert preview.iloc[0]["dominant_style"]
    assert isinstance(preview.iloc[0]["data_quality_labels"], list)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_row_contains_core_fields():
    row = build_strategy_preview_row(make_candidate_pool().iloc[1])

    assert row["symbol"] == "HIGH1"
    assert row["strategy_score"] is not None
    assert row["best_preset"]
    assert row["dominant_style"]
    assert row["consensus_level"]
    assert row["balanced_research_score"] is not None
    assert row["trend_momentum_score"] is not None
    assert row["volume_breakout_score"] is not None
    assert row["low_risk_quality_score"] is not None
    assert row["high_elasticity_watch_score"] is not None
    assert row["strategy_reason"]
    assert row["trend_reason"]
    assert row["volume_price_reason"]
    assert row["confidence_note"]
    assert row["ma_structure_label"] == "bullish_alignment"
    assert row["trend_quality_label"]
    assert row["volume_price_structure_label"]
    assert row["technical_profile_summary"]
    assert row["technical_grade"] in {"A", "B", "C", "D"}
    assert row["technical_style"]
    assert row["technical_strength"]
    assert row["technical_risk_level"]
    assert isinstance(row["technical_watch_points"], list)
    assert row["technical_summary_short"]
    assert row["fundamental_available"] is True
    assert row["fundamental_data_quality_label"] == "sufficient_fundamental_data"
    assert "fundamental_summary_base" in row
    assert row["fundamental_quality_score"] is not None
    assert row["fundamental_grade"] in {"A", "B", "C", "D"}
    assert row["fundamental_style"]
    assert row["fundamental_risk_level"]
    assert row["fundamental_reason"]
    assert row["industry_relative_quality_label"] == "insufficient_industry_data"
    assert row["fundamental_diagnostics_summary"]
    assert isinstance(row["profitability_diagnostics"], dict)
    assert isinstance(row["growth_diagnostics"], dict)
    assert isinstance(row["valuation_diagnostics"], dict)
    assert isinstance(row["financial_risk_diagnostics"], dict)
    assert isinstance(row["fundamental_strength_points"], list)
    assert isinstance(row["fundamental_weakness_points"], list)
    assert isinstance(row["fundamental_watch_points"], list)
    assert row["confluence_label"]
    assert 0 <= row["confluence_score"] <= 100
    assert row["confluence_summary"]
    assert row["composite_research_grade"]
    assert row["composite_research_style"]
    assert row["composite_summary"]
    assert row["research_priority_level"]
    assert 0 <= row["research_priority_score"] <= 100
    assert row["priority_stability_label"] in {"Stable", "Watch", "Unavailable"}
    assert 0 <= row["priority_stability_score"] <= 100
    assert isinstance(row["priority_drift_detected"], bool)
    assert row["architecture_audit_label"] in {"Pass", "Review", "Unavailable"}
    assert 0 <= row["architecture_audit_score"] <= 100
    assert isinstance(row["architecture_audit_warnings"], list)
    assert row["event_available"] is False
    assert row["event_type"] == "unknown"
    assert row["event_recency_label"] == "Unknown"
    assert row["event_source_quality_label"] == "Unknown"
    assert row["event_reliability_label"] == "Unknown"
    assert isinstance(row["event_research_tags"], list)
    assert isinstance(row["event_warnings"], list)
    assert row["event_diagnostic_level"] == "Unavailable"
    assert row["event_completeness_score"] == 0
    assert row["event_confidence_score"] == 0
    assert isinstance(row["event_followup_questions"], list)
    assert isinstance(row["event_evidence_gaps"], list)
    assert isinstance(row["event_quality_warnings"], list)
    assert row["event_confluence_label"] == "Unavailable"
    assert row["event_confluence_score"] == 0
    assert isinstance(row["event_support_points"], list)
    assert isinstance(row["event_conflict_points"], list)
    assert isinstance(row["event_followup_focus"], list)
    assert isinstance(row["event_confluence_warnings"], list)
    assert row["event_research_level"] == "Unavailable"
    assert row["event_research_summary"]
    assert isinstance(row["event_key_evidence"], list)
    assert isinstance(row["event_key_risks"], list)
    assert isinstance(row["event_validation_focus"], list)
    assert row["event_agent_note"]
    assert isinstance(row["event_summary_warnings"], list)
    assert row["research_pipeline_status"] in {"Healthy", "Watch", "Conflict", "Incomplete"}
    assert isinstance(row["research_pipeline_conflicts"], list)
    assert isinstance(row["research_pipeline_warnings"], list)
    assert row["research_pipeline_summary"]
    assert row["project_assessment_status"] in {"Ready", "Watch", "Not Ready"}
    assert 0 <= row["project_assessment_score"] <= 100
    assert row["architecture_assessment_note"]
    assert row["field_registry_assessment_note"]
    assert row["test_coverage_assessment_note"]
    assert row["ui_readability_assessment_note"]
    assert row["data_source_assessment_note"]
    assert row["scoring_boundary_assessment_note"]
    assert row["pre_v2_readiness_level"] in {"High", "Medium", "Low"}
    assert isinstance(row["pre_v2_blockers"], list)
    assert isinstance(row["pre_v2_recommendations"], list)
    assert_no_forbidden_words(row)


def test_strategy_preview_does_not_modify_source_dataframe():
    frame = make_candidate_pool()
    before = copy.deepcopy(frame)

    build_strategy_preview(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_strategy_preview_preserves_input_order_by_default():
    frame = make_candidate_pool()
    preview = build_strategy_preview(frame)

    assert list(preview["symbol"]) == ["LOW1", "HIGH1", "RISK1"]
    assert {"strategy_reason", "risk_reason", "data_quality_reason", "preset_reason", "confidence_note"}.issubset(
        preview.columns
    )
    assert {
        "ma_structure_label",
        "trend_quality_label",
        "breakout_pullback_label",
        "volume_price_structure_label",
        "short_term_overheat_label",
        "volatility_risk_label",
        "technical_profile_summary",
        "technical_grade",
        "technical_style",
        "technical_strength",
        "technical_risk_level",
        "technical_watch_points",
        "technical_summary_short",
        "fundamental_available",
        "fundamental_fields_detected",
        "missing_fundamental_fields",
        "fundamental_data_quality_label",
        "fundamental_summary_base",
        "profitability_score",
        "growth_score",
        "valuation_score",
        "financial_risk_score",
        "fundamental_quality_score",
        "fundamental_grade",
        "fundamental_style",
        "fundamental_risk_level",
        "fundamental_reason",
        "relative_profitability_label",
        "relative_growth_label",
        "relative_valuation_label",
        "relative_financial_risk_label",
        "industry_relative_quality_label",
        "industry_relative_summary",
        "fundamental_diagnostics",
        "profitability_diagnostics",
        "growth_diagnostics",
        "valuation_diagnostics",
        "financial_risk_diagnostics",
        "fundamental_watch_points",
        "fundamental_strength_points",
        "fundamental_weakness_points",
        "fundamental_diagnostics_summary",
        "confluence_label",
        "confluence_score",
        "confluence_summary",
        "confluence_strength_points",
        "confluence_risk_points",
        "confluence_followup_focus",
        "composite_research_grade",
        "composite_research_style",
        "composite_research_level",
        "composite_risk_level",
        "composite_confidence_level",
        "composite_summary",
        "composite_strength_points",
        "composite_risk_points",
        "composite_followup_focus",
        "composite_data_quality_note",
        "research_priority_score",
        "research_priority_level",
        "research_priority_reasons",
        "research_priority_warnings",
        "priority_stability_label",
        "priority_stability_score",
        "priority_stability_note",
        "priority_drift_detected",
        "priority_drift_reason",
        "architecture_audit_label",
        "architecture_audit_score",
        "architecture_audit_note",
        "architecture_audit_warnings",
        "field_contract_warnings",
        "module_contract_warnings",
        "boundary_contract_warnings",
        "event_available",
        "event_type",
        "event_recency_label",
        "event_source_quality_label",
        "event_reliability_label",
        "event_context_note",
        "event_research_tags",
        "event_warnings",
        "event_completeness_score",
        "event_clarity_score",
        "event_consistency_score",
        "event_confidence_score",
        "event_diagnostic_level",
        "event_diagnostic_summary",
        "event_followup_questions",
        "event_evidence_gaps",
        "event_quality_warnings",
        "event_confluence_label",
        "event_confluence_score",
        "event_confluence_summary",
        "event_support_points",
        "event_conflict_points",
        "event_followup_focus",
        "event_confluence_warnings",
        "event_research_summary",
        "event_research_level",
        "event_key_evidence",
        "event_key_risks",
        "event_validation_focus",
        "event_agent_note",
        "event_summary_warnings",
        "research_pipeline_status",
        "research_pipeline_conflicts",
        "research_pipeline_warnings",
        "research_pipeline_summary",
        "project_assessment_status",
        "project_assessment_score",
        "architecture_assessment_note",
        "field_registry_assessment_note",
        "test_coverage_assessment_note",
        "ui_readability_assessment_note",
        "data_source_assessment_note",
        "scoring_boundary_assessment_note",
        "pre_v2_readiness_level",
        "pre_v2_blockers",
        "pre_v2_recommendations",
    }.issubset(preview.columns)
    high_row = preview[preview["symbol"] == "HIGH1"].iloc[0]
    assert high_row["industry_relative_quality_label"] in {"industry_relative_strong", "industry_relative_neutral"}
    assert high_row["fundamental_diagnostics_summary"]
    assert len(high_row["fundamental_strength_points"]) <= 3
    assert len(high_row["fundamental_weakness_points"]) <= 3
    assert len(high_row["fundamental_watch_points"]) <= 3
    assert list(preview["symbol"]) == ["LOW1", "HIGH1", "RISK1"]
    assert all(0 <= score <= 100 for score in preview["confluence_score"])
    assert all(0 <= score <= 100 for score in preview["priority_stability_score"])
    assert all(0 <= score <= 100 for score in preview["architecture_audit_score"])
    assert list(preview["symbol"]) == ["LOW1", "HIGH1", "RISK1"]
    assert high_row["composite_research_grade"] in {"A", "B", "C", "D", "insufficient_data"}
    assert high_row["composite_summary"]
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_sort_by_strategy_only_changes_preview_order():
    frame = make_candidate_pool()
    before = copy.deepcopy(frame)
    preview = build_strategy_preview(frame, sort_by_strategy=True)

    assert list(preview["symbol"]) != ["LOW1", "HIGH1", "RISK1"]
    assert preview.iloc[0]["strategy_score"] >= preview.iloc[-1]["strategy_score"]
    pd.testing.assert_frame_equal(frame, before)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_keeps_risk_and_data_quality_labels():
    preview = build_strategy_preview(make_candidate_pool())
    risk_row = preview[preview["symbol"] == "RISK1"].iloc[0]

    assert isinstance(risk_row["risk_labels"], list)
    assert "high_volatility" in risk_row["risk_labels"]
    assert isinstance(risk_row["data_quality_labels"], list)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_json_like_export_is_stable():
    preview = build_strategy_preview(make_candidate_pool())
    payload = export_strategy_preview_to_json_like(preview)

    assert payload["schema_version"] == "strategy_preview.v1"
    assert payload["metadata"]["record_count"] == 3
    assert payload["metadata"]["uses_real_data_source"] is False
    assert payload["metadata"]["ui_connected"] is False
    assert payload["records"][0]["symbol"] == "LOW1"
    assert "strategy_score" in payload["records"][0]
    assert_no_forbidden_words(payload)


def test_strategy_preview_csv_export_writes_temp_file(tmp_path):
    preview = build_strategy_preview(make_candidate_pool())
    output_path = tmp_path / "strategy_preview.csv"

    result = export_strategy_preview_to_csv(preview, output_path)
    saved = pd.read_csv(output_path)

    assert result["row_count"] == 3
    assert Path(result["path"]).exists()
    assert len(saved) == 3
    assert "strategy_score" in saved.columns
    assert_no_forbidden_words(result)


def test_strategy_preview_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")

    assert "strategy.preview" not in legacy_text
    assert "build_strategy_preview" not in legacy_text
