"""Read-only architecture and contract audit helpers for strategy preview."""

import copy
import importlib
import math

import pandas as pd


ARCHITECTURE_AUDIT_FIELDS = [
    "architecture_audit_label",
    "architecture_audit_score",
    "architecture_audit_note",
    "architecture_audit_warnings",
    "field_contract_warnings",
    "module_contract_warnings",
    "boundary_contract_warnings",
]

REQUIRED_MODULES = [
    "strategy.technical",
    "strategy.fundamental",
    "strategy.fundamental_relative",
    "strategy.fundamental_diagnostics",
    "strategy.confluence",
    "strategy.composite_profile",
    "strategy.priority_stability",
    "strategy.event_context",
    "strategy.event_diagnostics",
    "strategy.preview",
]

FIELD_GROUPS = {
    "technical": [
        "technical_grade",
        "technical_style",
        "technical_strength",
        "technical_risk_level",
    ],
    "fundamental": [
        "fundamental_available",
        "fundamental_data_quality_label",
        "fundamental_quality_score",
        "fundamental_grade",
    ],
    "relative": [
        "relative_profitability_label",
        "relative_growth_label",
        "relative_valuation_label",
        "relative_financial_risk_label",
        "industry_relative_quality_label",
    ],
    "diagnostics": [
        "fundamental_diagnostics",
        "profitability_diagnostics",
        "growth_diagnostics",
        "valuation_diagnostics",
        "financial_risk_diagnostics",
        "fundamental_diagnostics_summary",
    ],
    "confluence": [
        "confluence_label",
        "confluence_score",
        "confluence_summary",
    ],
    "composite": [
        "composite_research_grade",
        "composite_research_style",
        "composite_research_level",
        "composite_risk_level",
        "composite_confidence_level",
    ],
    "research_priority": [
        "research_priority_score",
        "research_priority_level",
        "research_priority_reasons",
        "research_priority_warnings",
    ],
    "priority_stability": [
        "priority_stability_label",
        "priority_stability_score",
        "priority_stability_note",
        "priority_drift_detected",
        "priority_drift_reason",
    ],
    "event_context": [
        "event_available",
        "event_type",
        "event_recency_label",
        "event_source_quality_label",
        "event_reliability_label",
        "event_context_note",
        "event_research_tags",
        "event_warnings",
    ],
    "event_diagnostics": [
        "event_completeness_score",
        "event_clarity_score",
        "event_consistency_score",
        "event_confidence_score",
        "event_diagnostic_level",
        "event_diagnostic_summary",
        "event_followup_questions",
        "event_evidence_gaps",
        "event_quality_warnings",
    ],
}

BOUNDARY_FIELDS = [
    "strategy_score",
    "original_score",
    "research_priority_score",
    "priority_stability_score",
]


def _source_to_frame(source):
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, pd.Series):
        return pd.DataFrame([copy.deepcopy(source.to_dict())])
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    return pd.DataFrame()


def _row_dict(row):
    if hasattr(row, "to_dict"):
        return copy.deepcopy(row.to_dict())
    if isinstance(row, dict):
        return copy.deepcopy(row)
    return {}


def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def audit_module_presence(module_names=None):
    names = list(module_names or REQUIRED_MODULES)
    warnings = []
    for module_name in names:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            warnings.append(f"{module_name} import unavailable: {exc.__class__.__name__}")
    return warnings


def audit_field_registry(row):
    row_data = _row_dict(row)
    warnings = []
    for group_name, fields in FIELD_GROUPS.items():
        missing = [field for field in fields if field not in row_data]
        if missing:
            warnings.append(f"{group_name} fields missing: {', '.join(missing)}")
    return warnings


def audit_boundary_contract(row):
    row_data = _row_dict(row)
    warnings = []
    for field in BOUNDARY_FIELDS:
        if field not in row_data:
            warnings.append(f"{field} boundary field missing")
            continue
        if field.endswith("_score") and _is_missing(row_data.get(field)):
            warnings.append(f"{field} boundary field unavailable")
    return warnings


def build_architecture_audit_row(row):
    row_data = _row_dict(row)
    field_warnings = audit_field_registry(row_data)
    module_warnings = audit_module_presence()
    boundary_warnings = audit_boundary_contract(row_data)
    all_warnings = field_warnings + module_warnings + boundary_warnings

    if not row_data:
        label = "Unavailable"
        score = 0
        note = "Architecture audit input is empty; contract review is unavailable."
    elif all_warnings:
        label = "Review"
        score = max(0, 100 - min(80, len(all_warnings) * 8))
        note = "Architecture audit found contract items for research review."
    else:
        label = "Pass"
        score = 100
        note = "Architecture audit passed for the current research preview contract."

    return {
        "architecture_audit_label": label,
        "architecture_audit_score": score,
        "architecture_audit_note": note,
        "architecture_audit_warnings": all_warnings,
        "field_contract_warnings": field_warnings,
        "module_contract_warnings": module_warnings,
        "boundary_contract_warnings": boundary_warnings,
    }


def build_architecture_audit_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=ARCHITECTURE_AUDIT_FIELDS)
    rows = [build_architecture_audit_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=ARCHITECTURE_AUDIT_FIELDS)


__all__ = [
    "ARCHITECTURE_AUDIT_FIELDS",
    "BOUNDARY_FIELDS",
    "FIELD_GROUPS",
    "REQUIRED_MODULES",
    "audit_boundary_contract",
    "audit_field_registry",
    "audit_module_presence",
    "build_architecture_audit_profile",
    "build_architecture_audit_row",
]
