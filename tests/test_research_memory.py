import copy
import importlib

import pandas as pd

from memory.research_memory import SNAPSHOT_FIELDS, build_research_snapshot


def complete_preview_row():
    return {
        "symbol": "AAA",
        "name": "Alpha Sample",
        "strategy_score": 73,
        "research_priority_score": 81,
        "priority_stability_score": 95,
        "architecture_audit_score": 100,
        "event_confidence_score": 86,
        "event_confluence_score": 82,
        "technical_grade": "A",
        "technical_style": "trend_momentum",
        "technical_strength": "strong",
        "technical_risk_level": "low",
        "technical_summary_short": "technical context available",
        "technical_watch_points": ["watch volume confirmation"],
        "fundamental_available": True,
        "fundamental_grade": "A",
        "fundamental_quality_score": 78,
        "fundamental_style": "quality_growth",
        "fundamental_risk_level": "low",
        "fundamental_reason": "fundamental context available",
        "fundamental_diagnostics_summary": "diagnostics available",
        "industry_relative_quality_label": "industry_relative_strong",
        "relative_profitability_label": "industry_leading",
        "relative_growth_label": "high_relative_growth",
        "relative_valuation_label": "relatively_reasonable",
        "relative_financial_risk_label": "lower_than_industry_risk",
        "industry_relative_summary": "industry context available",
        "composite_research_grade": "A",
        "composite_research_style": "high_quality_resonance",
        "composite_research_level": "priority_research",
        "composite_risk_level": "low",
        "composite_confidence_level": "high",
        "composite_summary": "composite context available",
        "research_priority_level": "priority_research",
        "research_priority_reasons": ["evidence chain complete"],
        "research_priority_warnings": [],
        "priority_stability_label": "Stable",
        "priority_stability_note": "priority stable",
        "event_available": True,
        "event_type": "earnings",
        "event_diagnostic_level": "Strong",
        "event_confluence_label": "Supportive",
        "event_research_level": "High",
        "event_research_summary": "event context available",
        "event_key_evidence": ["event evidence available"],
        "event_key_risks": [],
        "event_validation_focus": ["validate event in source fields"],
        "event_summary_warnings": [],
        "architecture_audit_label": "Pass",
        "architecture_audit_note": "architecture pass",
        "research_pipeline_status": "Healthy",
        "research_pipeline_conflicts": [],
        "research_pipeline_warnings": [],
        "research_pipeline_summary": "pipeline healthy",
        "project_assessment_status": "Ready",
        "project_assessment_score": 82,
        "pre_v2_readiness_level": "High",
        "pre_v2_blockers": [],
        "pre_v2_recommendations": ["schema first"],
        "scoring_boundary_assessment_note": "scoring boundary intact",
        "data_source_assessment_note": "data source boundary intact",
    }


def test_empty_input_safe_return():
    snapshot = build_research_snapshot({})

    assert list(snapshot.keys()) == SNAPSHOT_FIELDS
    assert snapshot["snapshot_status"] == "Incomplete"
    assert snapshot["snapshot_ticker"] is None


def test_normal_snapshot_generation():
    snapshot = build_research_snapshot(complete_preview_row())

    assert list(snapshot.keys()) == SNAPSHOT_FIELDS
    assert snapshot["snapshot_status"] == "Available"
    assert snapshot["snapshot_ticker"] == "AAA"
    assert snapshot["snapshot_name"] == "Alpha Sample"
    assert snapshot["snapshot_version"] == "v2.0.0"
    assert snapshot["snapshot_stage"] == "Research Memory Foundation"
    assert snapshot["technical_snapshot"]["technical_grade"] == "A"
    assert snapshot["event_snapshot"]["event_confluence_score"] == 82


def test_missing_fields_mark_incomplete():
    row = complete_preview_row()
    row.pop("technical_grade")

    snapshot = build_research_snapshot(row)

    assert snapshot["snapshot_status"] == "Incomplete"
    assert "technical_grade" in snapshot["snapshot_summary"]


def test_input_is_not_modified():
    row = complete_preview_row()
    before = copy.deepcopy(row)

    build_research_snapshot(row)

    assert row == before


def test_output_order_is_fixed():
    snapshot = build_research_snapshot(complete_preview_row())

    assert list(snapshot.keys()) == SNAPSHOT_FIELDS


def test_status_available_and_incomplete():
    assert build_research_snapshot(complete_preview_row())["snapshot_status"] == "Available"
    assert build_research_snapshot(pd.DataFrame())["snapshot_status"] == "Incomplete"


def test_module_importable():
    assert importlib.import_module("memory.research_memory")


def test_scores_are_not_changed_by_snapshot_builder():
    row = complete_preview_row()
    before = copy.deepcopy(row)

    build_research_snapshot(row)

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]
    assert row["priority_stability_score"] == before["priority_stability_score"]
    assert row["architecture_audit_score"] == before["architecture_audit_score"]
    assert row["event_confidence_score"] == before["event_confidence_score"]
    assert row["event_confluence_score"] == before["event_confluence_score"]
