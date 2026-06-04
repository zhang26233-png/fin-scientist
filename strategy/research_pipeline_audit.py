"""Read-only validation checks for the end-to-end research pipeline."""

import copy
import math

import pandas as pd


RESEARCH_PIPELINE_AUDIT_FIELDS = [
    "research_pipeline_status",
    "research_pipeline_conflicts",
    "research_pipeline_warnings",
    "research_pipeline_summary",
]

REQUIRED_PIPELINE_FIELDS = [
    "technical_grade",
    "fundamental_grade",
    "industry_relative_quality_label",
    "composite_research_grade",
    "research_priority_level",
    "priority_stability_label",
    "architecture_audit_label",
    "event_diagnostic_level",
    "event_confluence_label",
    "event_research_level",
]

_STRONG_GRADES = {"A", "B"}
_WEAK_GRADES = {"D", "insufficient_data"}
_HIGH_PRIORITY = {"priority_research", "high", "High"}
_LOW_PRIORITY = {"low_priority", "insufficient_data", "low", "Low"}


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


def _text(value):
    return "" if _is_missing(value) else str(value).strip()


def _missing_fields(row):
    return [field for field in REQUIRED_PIPELINE_FIELDS if _is_missing(row.get(field))]


def _conflicts(row):
    conflicts = []
    composite = _text(row.get("composite_research_grade"))
    priority = _text(row.get("research_priority_level"))
    event_diagnostic = _text(row.get("event_diagnostic_level"))
    event_confluence = _text(row.get("event_confluence_label"))
    event_research = _text(row.get("event_research_level"))

    if priority in _HIGH_PRIORITY and composite in _WEAK_GRADES:
        conflicts.append("research priority is high while composite research grade is weak or insufficient")
    if priority in _LOW_PRIORITY and composite in _STRONG_GRADES:
        conflicts.append("research priority is low while composite research grade is strong")
    if event_diagnostic == "Strong" and event_confluence == "Unavailable":
        conflicts.append("event diagnostics are strong but event confluence is unavailable")
    if event_diagnostic == "Unavailable" and event_confluence == "Supportive":
        conflicts.append("event confluence is supportive while event diagnostics are unavailable")
    if event_confluence == "Conflicting" and event_research == "High":
        conflicts.append("event research level is high while event confluence is conflicting")
    return conflicts


def _warnings(row, missing):
    warnings = []
    architecture = _text(row.get("architecture_audit_label"))
    stability = _text(row.get("priority_stability_label"))
    event_diagnostic = _text(row.get("event_diagnostic_level"))
    event_confluence = _text(row.get("event_confluence_label"))
    event_research = _text(row.get("event_research_level"))

    if missing:
        warnings.append("research pipeline fields incomplete: " + ", ".join(missing))
    if architecture in {"Review", "Watch", "Warning"}:
        warnings.append("architecture audit requires review")
    if architecture == "Unavailable":
        warnings.append("architecture audit is unavailable")
    if stability in {"Watch", "Unavailable"}:
        warnings.append("priority stability requires review")
    if event_diagnostic in {"Weak", "Unavailable"}:
        warnings.append("event diagnostics limit pipeline completeness")
    if event_confluence in {"Mixed", "Unavailable"}:
        warnings.append("event confluence requires follow-up review")
    if event_confluence == "Supportive" and event_research == "Unavailable":
        warnings.append("event research summary is unavailable while event confluence is supportive")
    if event_research in {"Low", "Unavailable"}:
        warnings.append("event research summary requires follow-up review")
    return list(dict.fromkeys(warnings))


def _status(conflicts, warnings, missing):
    if conflicts:
        return "Conflict"
    if missing:
        return "Incomplete"
    if any("unavailable while event confluence is supportive" in item for item in warnings):
        return "Incomplete"
    if warnings:
        return "Watch"
    return "Healthy"


def _summary(status, conflicts, warnings):
    if status == "Healthy":
        return "Research pipeline appears complete and internally consistent for read-only review."
    if status == "Conflict":
        return f"Research pipeline found {len(conflicts)} conflict item(s) requiring review."
    if status == "Incomplete":
        return "Research pipeline is incomplete because required module fields are missing."
    return f"Research pipeline is complete but has {len(warnings)} warning item(s) for review."


def build_research_pipeline_audit_row(row):
    row_data = _row_dict(row)
    missing = _missing_fields(row_data)
    conflicts = _conflicts(row_data)
    warnings = _warnings(row_data, missing)
    status = _status(conflicts, warnings, missing)
    return {
        "research_pipeline_status": status,
        "research_pipeline_conflicts": conflicts,
        "research_pipeline_warnings": warnings,
        "research_pipeline_summary": _summary(status, conflicts, warnings),
    }


def build_research_pipeline_audit_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=RESEARCH_PIPELINE_AUDIT_FIELDS)
    rows = [build_research_pipeline_audit_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=RESEARCH_PIPELINE_AUDIT_FIELDS)


__all__ = [
    "REQUIRED_PIPELINE_FIELDS",
    "RESEARCH_PIPELINE_AUDIT_FIELDS",
    "build_research_pipeline_audit_profile",
    "build_research_pipeline_audit_row",
]
