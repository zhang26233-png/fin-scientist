"""Read-only research snapshot schema for v2 memory foundation."""

import copy
import hashlib
import math
from datetime import datetime, timezone

import pandas as pd


SNAPSHOT_FIELDS = [
    "snapshot_id",
    "snapshot_timestamp",
    "snapshot_ticker",
    "snapshot_name",
    "snapshot_version",
    "snapshot_stage",
    "snapshot_summary",
    "snapshot_status",
    "technical_snapshot",
    "fundamental_snapshot",
    "industry_snapshot",
    "composite_snapshot",
    "priority_snapshot",
    "event_snapshot",
    "pipeline_snapshot",
    "project_snapshot",
]

TECHNICAL_FIELDS = [
    "technical_grade",
    "technical_style",
    "technical_strength",
    "technical_risk_level",
    "technical_summary_short",
    "technical_watch_points",
]

FUNDAMENTAL_FIELDS = [
    "fundamental_available",
    "fundamental_grade",
    "fundamental_quality_score",
    "fundamental_style",
    "fundamental_risk_level",
    "fundamental_reason",
    "fundamental_diagnostics_summary",
]

INDUSTRY_FIELDS = [
    "industry_relative_quality_label",
    "relative_profitability_label",
    "relative_growth_label",
    "relative_valuation_label",
    "relative_financial_risk_label",
    "industry_relative_summary",
]

COMPOSITE_FIELDS = [
    "composite_research_grade",
    "composite_research_style",
    "composite_research_level",
    "composite_risk_level",
    "composite_confidence_level",
    "composite_summary",
]

PRIORITY_FIELDS = [
    "research_priority_score",
    "research_priority_level",
    "research_priority_reasons",
    "research_priority_warnings",
    "priority_stability_label",
    "priority_stability_score",
    "priority_stability_note",
]

EVENT_FIELDS = [
    "event_available",
    "event_type",
    "event_diagnostic_level",
    "event_confidence_score",
    "event_confluence_label",
    "event_confluence_score",
    "event_research_level",
    "event_research_summary",
    "event_key_evidence",
    "event_key_risks",
    "event_validation_focus",
    "event_summary_warnings",
]

PIPELINE_FIELDS = [
    "architecture_audit_label",
    "architecture_audit_score",
    "architecture_audit_note",
    "research_pipeline_status",
    "research_pipeline_conflicts",
    "research_pipeline_warnings",
    "research_pipeline_summary",
]

PROJECT_FIELDS = [
    "project_assessment_status",
    "project_assessment_score",
    "pre_v2_readiness_level",
    "pre_v2_blockers",
    "pre_v2_recommendations",
    "scoring_boundary_assessment_note",
    "data_source_assessment_note",
]

REQUIRED_SNAPSHOT_FIELDS = [
    "symbol",
    "name",
    "technical_grade",
    "fundamental_grade",
    "composite_research_grade",
    "research_priority_level",
    "research_pipeline_status",
    "project_assessment_status",
]

DEFAULT_SNAPSHOT_VERSION = "v2.0.0"
DEFAULT_SNAPSHOT_STAGE = "Research Memory Foundation"


def _row_dict(source):
    if isinstance(source, pd.DataFrame):
        if source.empty:
            return {}
        return copy.deepcopy(source.iloc[0].to_dict())
    if isinstance(source, pd.Series):
        return copy.deepcopy(source.to_dict())
    if isinstance(source, dict):
        return copy.deepcopy(source)
    if isinstance(source, list):
        if not source:
            return {}
        first = source[0]
        if isinstance(first, dict):
            return copy.deepcopy(first)
    return {}


def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _clean_value(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (list, dict)):
        return copy.deepcopy(value)
    if pd.isna(value):
        return None
    return value


def _pick(row, fields):
    return {field: _clean_value(row.get(field)) for field in fields}


def _missing_required(row):
    return [field for field in REQUIRED_SNAPSHOT_FIELDS if _is_missing(row.get(field))]


def _snapshot_status(row):
    return "Incomplete" if _missing_required(row) else "Available"


def _snapshot_summary(row, status):
    symbol = str(row.get("symbol") or row.get("snapshot_ticker") or "unknown")
    name = str(row.get("name") or row.get("snapshot_name") or "")
    composite = str(row.get("composite_research_grade") or "unknown")
    pipeline = str(row.get("research_pipeline_status") or "unknown")
    project = str(row.get("project_assessment_status") or "unknown")
    if status == "Incomplete":
        missing = ", ".join(_missing_required(row))
        return f"Research snapshot for {symbol} {name} is incomplete; missing fields: {missing}."
    return (
        f"Research snapshot for {symbol} {name} is available; "
        f"composite grade={composite}; pipeline status={pipeline}; project assessment={project}."
    )


def _snapshot_id(row, timestamp, version):
    symbol = str(row.get("symbol") or row.get("snapshot_ticker") or "unknown")
    basis = f"{symbol}|{timestamp}|{version}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]
    return f"snapshot-{symbol}-{digest}"


def build_research_snapshot(source, snapshot_version=DEFAULT_SNAPSHOT_VERSION, snapshot_stage=DEFAULT_SNAPSHOT_STAGE):
    row = _row_dict(source)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    status = _snapshot_status(row)
    snapshot = {
        "snapshot_id": _snapshot_id(row, timestamp, snapshot_version),
        "snapshot_timestamp": timestamp,
        "snapshot_ticker": _clean_value(row.get("symbol") or row.get("snapshot_ticker")),
        "snapshot_name": _clean_value(row.get("name") or row.get("snapshot_name")),
        "snapshot_version": snapshot_version,
        "snapshot_stage": snapshot_stage,
        "snapshot_summary": _snapshot_summary(row, status),
        "snapshot_status": status,
        "technical_snapshot": _pick(row, TECHNICAL_FIELDS),
        "fundamental_snapshot": _pick(row, FUNDAMENTAL_FIELDS),
        "industry_snapshot": _pick(row, INDUSTRY_FIELDS),
        "composite_snapshot": _pick(row, COMPOSITE_FIELDS),
        "priority_snapshot": _pick(row, PRIORITY_FIELDS),
        "event_snapshot": _pick(row, EVENT_FIELDS),
        "pipeline_snapshot": _pick(row, PIPELINE_FIELDS),
        "project_snapshot": _pick(row, PROJECT_FIELDS),
    }
    return {field: snapshot[field] for field in SNAPSHOT_FIELDS}


__all__ = [
    "COMPOSITE_FIELDS",
    "DEFAULT_SNAPSHOT_STAGE",
    "DEFAULT_SNAPSHOT_VERSION",
    "EVENT_FIELDS",
    "FUNDAMENTAL_FIELDS",
    "INDUSTRY_FIELDS",
    "PIPELINE_FIELDS",
    "PRIORITY_FIELDS",
    "PROJECT_FIELDS",
    "REQUIRED_SNAPSHOT_FIELDS",
    "SNAPSHOT_FIELDS",
    "TECHNICAL_FIELDS",
    "build_research_snapshot",
]
