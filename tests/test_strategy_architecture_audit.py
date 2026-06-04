import copy
import importlib
from pathlib import Path

import pandas as pd

from strategy.architecture_audit import (
    ARCHITECTURE_AUDIT_FIELDS,
    REQUIRED_MODULES,
    audit_module_presence,
    build_architecture_audit_profile,
    build_architecture_audit_row,
)


FORBIDDEN_WORDS = [
    "buy",
    "sell",
    "hold",
    "target price",
    "recommend",
    "strong buy",
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6301\u6709",
    "\u76ee\u6807\u4ef7",
    "\u6295\u8d44\u5efa\u8bae",
]


def assert_no_forbidden_words(value):
    text = str(value).lower()
    for word in FORBIDDEN_WORDS:
        assert word.lower() not in text


def complete_row(symbol="A"):
    return {
        "symbol": symbol,
        "original_score": 66,
        "strategy_score": 72,
        "technical_grade": "A",
        "technical_style": "trend_momentum",
        "technical_strength": "strong",
        "technical_risk_level": "low",
        "fundamental_available": True,
        "fundamental_data_quality_label": "sufficient_fundamental_data",
        "fundamental_quality_score": 76,
        "fundamental_grade": "A",
        "relative_profitability_label": "industry_leading",
        "relative_growth_label": "high_relative_growth",
        "relative_valuation_label": "relatively_reasonable",
        "relative_financial_risk_label": "lower_than_industry_risk",
        "industry_relative_quality_label": "industry_relative_strong",
        "fundamental_diagnostics": {},
        "profitability_diagnostics": {},
        "growth_diagnostics": {},
        "valuation_diagnostics": {},
        "financial_risk_diagnostics": {},
        "fundamental_diagnostics_summary": "research diagnostics available",
        "confluence_label": "fundamental_technical_resonance",
        "confluence_score": 82,
        "confluence_summary": "research confluence available",
        "composite_research_grade": "A",
        "composite_research_style": "high_quality_resonance",
        "composite_research_level": "priority_research",
        "composite_risk_level": "low",
        "composite_confidence_level": "high",
        "research_priority_score": 82,
        "research_priority_level": "priority_research",
        "research_priority_reasons": ["research evidence available"],
        "research_priority_warnings": [],
        "priority_stability_label": "Stable",
        "priority_stability_score": 95,
        "priority_stability_note": "Priority fields are complete.",
        "priority_drift_detected": False,
        "priority_drift_reason": "",
        "event_available": False,
        "event_type": "unknown",
        "event_recency_label": "Unknown",
        "event_source_quality_label": "Unknown",
        "event_reliability_label": "Unknown",
        "event_context_note": "No usable event context is available for the current research preview.",
        "event_research_tags": [],
        "event_warnings": ["event input unavailable"],
    }


def test_empty_input_safe_return():
    result = build_architecture_audit_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == ARCHITECTURE_AUDIT_FIELDS
    assert_no_forbidden_words(result.to_dict())


def test_single_candidate_generates_audit_fields():
    result = build_architecture_audit_row(complete_row())

    assert result["architecture_audit_label"] == "Pass"
    assert result["architecture_audit_score"] == 100
    assert result["architecture_audit_note"]
    assert result["architecture_audit_warnings"] == []
    assert result["field_contract_warnings"] == []
    assert result["module_contract_warnings"] == []
    assert result["boundary_contract_warnings"] == []
    assert_no_forbidden_words(result)


def test_input_object_is_not_modified():
    row = complete_row()
    before = copy.deepcopy(row)

    build_architecture_audit_row(row)

    assert row == before


def test_output_order_is_stable():
    frame = pd.DataFrame([complete_row("A"), complete_row("B"), complete_row("C")])
    result = build_architecture_audit_profile(frame)

    assert len(result) == 3
    assert list(frame["symbol"]) == ["A", "B", "C"]
    assert list(result["architecture_audit_label"]) == ["Pass", "Pass", "Pass"]


def test_boundary_scores_are_not_changed():
    row = complete_row()
    before = copy.deepcopy(row)

    build_architecture_audit_row(row)

    assert row["strategy_score"] == before["strategy_score"]
    assert row["research_priority_score"] == before["research_priority_score"]
    assert row["priority_stability_score"] == before["priority_stability_score"]


def test_missing_fields_generate_warnings_without_error():
    result = build_architecture_audit_row({"symbol": "MISS", "strategy_score": 50})

    assert result["architecture_audit_label"] == "Review"
    assert result["architecture_audit_warnings"]
    assert result["field_contract_warnings"]
    assert result["boundary_contract_warnings"]
    assert_no_forbidden_words(result)


def test_key_modules_are_importable():
    assert audit_module_presence() == []
    for module_name in REQUIRED_MODULES:
        assert importlib.import_module(module_name)


def test_core_scoring_is_not_modified_by_architecture_audit():
    module_text = Path("strategy/architecture_audit.py").read_text(encoding="utf-8")
    core_scoring_text = Path("core/scoring.py").read_text(encoding="utf-8")

    assert "core.scoring" not in module_text
    assert "architecture_audit" not in core_scoring_text
    assert_no_forbidden_words(module_text)
