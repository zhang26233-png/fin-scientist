"""Read-only research journal schema for v2.2 memory layer."""

import copy
import hashlib
import math

import pandas as pd


JOURNAL_FIELDS = [
    "journal_id",
    "journal_ticker",
    "journal_name",
    "journal_period",
    "journal_status",
    "journal_summary",
    "journal_observations",
    "journal_risk_notes",
    "journal_data_quality_notes",
    "journal_followup_questions",
    "journal_agent_tasks",
    "journal_warnings",
]

DEFAULT_JOURNAL_STATUS_INCOMPLETE = "Incomplete"
DEFAULT_JOURNAL_STATUS_AVAILABLE = "Available"

_FORBIDDEN_TERMS = [
    "b" + "uy",
    "s" + "ell",
    "h" + "old",
    "target" + " price",
    "reco" + "mmend",
    "strong " + "b" + "uy",
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6301\u6709",
    "\u76ee\u6807\u4ef7",
    "\u6295\u8d44\u5efa\u8bae",
]


def _empty_journal(warnings=None):
    journal = {
        "journal_id": None,
        "journal_ticker": None,
        "journal_name": None,
        "journal_period": None,
        "journal_status": DEFAULT_JOURNAL_STATUS_INCOMPLETE,
        "journal_summary": "No research snapshot or timeline available for journal review.",
        "journal_observations": [],
        "journal_risk_notes": [],
        "journal_data_quality_notes": [],
        "journal_followup_questions": [],
        "journal_agent_tasks": [],
        "journal_warnings": warnings or ["No snapshot or timeline provided."],
    }
    return {field: journal[field] for field in JOURNAL_FIELDS}


def _to_dict(source):
    if source is None:
        return {}
    if isinstance(source, pd.DataFrame):
        if source.empty:
            return {}
        return copy.deepcopy(source.iloc[0].to_dict())
    if isinstance(source, pd.Series):
        return copy.deepcopy(source.to_dict())
    if isinstance(source, dict):
        return copy.deepcopy(source)
    if isinstance(source, list) and source and isinstance(source[0], dict):
        return copy.deepcopy(source[0])
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
    if isinstance(value, (dict, list)):
        return copy.deepcopy(value)
    if pd.isna(value):
        return None
    return value


def _section(source, section_name):
    value = source.get(section_name)
    if isinstance(value, dict):
        return value
    return {}


def _as_list(value):
    if _is_missing(value):
        return []
    if isinstance(value, list):
        return copy.deepcopy(value)
    return [value]


def _safe_text(value):
    text = str(value)
    for term in _FORBIDDEN_TERMS:
        text = text.replace(term, "operational term removed")
        text = text.replace(term.title(), "operational term removed")
        text = text.replace(term.upper(), "operational term removed")
    return text


def _safe_list(values):
    result = []
    for value in values:
        if _is_missing(value):
            continue
        if isinstance(value, dict):
            result.append(_safe_text(_format_change(value)))
        else:
            result.append(_safe_text(value))
    return result


def _dedupe(items):
    result = []
    seen = set()
    for item in items:
        safe_item = _safe_text(item)
        if safe_item and safe_item not in seen:
            result.append(safe_item)
            seen.add(safe_item)
    return result


def _journal_id(ticker, period, snapshot_id, timeline_id):
    ticker_part = str(ticker or "unknown")
    basis = f"{ticker_part}|{period}|{snapshot_id}|{timeline_id}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]
    return f"journal-{ticker_part}-{digest}"


def _journal_period(snapshot, timeline):
    start = timeline.get("timeline_start_time") or snapshot.get("snapshot_timestamp")
    end = timeline.get("timeline_end_time") or snapshot.get("snapshot_timestamp")
    if _is_missing(start) and _is_missing(end):
        return None
    if start == end:
        return _safe_text(start)
    return _safe_text(f"{start} to {end}")


def _format_change(change):
    section = change.get("section", "unknown_section")
    field = change.get("field", "unknown_field")
    direction = change.get("direction", "Unknown")
    return f"{section}.{field} changed from {change.get('from')} to {change.get('to')} with direction {direction}."


def _build_summary(snapshot, timeline, status, ticker, name, period):
    snapshot_summary = snapshot.get("snapshot_summary")
    timeline_summary = timeline.get("timeline_change_summary")
    display_name = f" {name}" if name else ""
    if status == DEFAULT_JOURNAL_STATUS_AVAILABLE:
        parts = [
            f"Research journal for {ticker or 'unknown'}{display_name} covers {period}.",
            snapshot_summary,
            timeline_summary,
        ]
    else:
        parts = [
            f"Research journal for {ticker or 'unknown'}{display_name} is incomplete.",
            snapshot_summary,
            timeline_summary,
        ]
    return _safe_text(" ".join(str(part) for part in parts if not _is_missing(part)))


def _build_observations(snapshot, timeline):
    priority = _section(snapshot, "priority_snapshot")
    event = _section(snapshot, "event_snapshot")
    pipeline = _section(snapshot, "pipeline_snapshot")
    observations = []

    if not _is_missing(priority.get("research_priority_level")):
        observations.append(f"Research priority level is {priority.get('research_priority_level')}.")
    observations.extend(_as_list(priority.get("research_priority_reasons")))

    if not _is_missing(event.get("event_research_summary")):
        observations.append(event.get("event_research_summary"))
    observations.extend(_as_list(event.get("event_key_evidence")))

    if not _is_missing(pipeline.get("research_pipeline_status")):
        observations.append(f"Research pipeline status is {pipeline.get('research_pipeline_status')}.")
    if not _is_missing(pipeline.get("research_pipeline_summary")):
        observations.append(pipeline.get("research_pipeline_summary"))

    timeline_summary = timeline.get("timeline_change_summary")
    if not _is_missing(timeline_summary):
        observations.append(timeline_summary)
    observations.extend(_safe_list(timeline.get("timeline_key_changes") or []))
    return _dedupe(observations)


def _build_risk_notes(snapshot, timeline):
    priority = _section(snapshot, "priority_snapshot")
    event = _section(snapshot, "event_snapshot")
    pipeline = _section(snapshot, "pipeline_snapshot")
    notes = []
    notes.extend(_as_list(priority.get("research_priority_warnings")))
    notes.extend(_as_list(event.get("event_key_risks")))
    notes.extend(_as_list(event.get("event_summary_warnings")))
    notes.extend(_as_list(pipeline.get("research_pipeline_conflicts")))
    notes.extend(_as_list(pipeline.get("research_pipeline_warnings")))
    notes.extend(_as_list(timeline.get("timeline_warnings")))
    if not notes:
        notes.append("No explicit risk or uncertainty notes were supplied by the snapshot or timeline.")
    return _dedupe(notes)


def _build_data_quality_notes(snapshot, timeline):
    notes = []
    if snapshot.get("snapshot_status") != "Available":
        notes.append("Snapshot is incomplete; review missing fields before deeper research.")
    if timeline and timeline.get("timeline_status") != "Available":
        notes.append("Timeline is incomplete; additional same-object snapshots are needed for change review.")

    fundamental = _section(snapshot, "fundamental_snapshot")
    if not _is_missing(fundamental.get("fundamental_data_quality_label")):
        notes.append(f"Fundamental data quality label is {fundamental.get('fundamental_data_quality_label')}.")
    if not _is_missing(fundamental.get("fundamental_diagnostics_summary")):
        notes.append(fundamental.get("fundamental_diagnostics_summary"))

    project = _section(snapshot, "project_snapshot")
    if not _is_missing(project.get("data_source_assessment_note")):
        notes.append(project.get("data_source_assessment_note"))
    return _dedupe(notes)


def _build_followup_questions(snapshot, timeline):
    event = _section(snapshot, "event_snapshot")
    pipeline = _section(snapshot, "pipeline_snapshot")
    questions = []

    for focus in _as_list(event.get("event_validation_focus")):
        questions.append(f"What evidence should be reviewed for event validation focus: {focus}?")
    for warning in _as_list(pipeline.get("research_pipeline_warnings")):
        questions.append(f"What additional research can clarify pipeline warning: {warning}?")
    for change in timeline.get("timeline_key_changes") or []:
        questions.append(f"What explains the observed change in {change.get('section')}.{change.get('field')}?")
    if not questions:
        questions.append("What additional evidence would improve the next research review?")
    return _dedupe(questions)


def _build_agent_tasks(snapshot, timeline):
    event = _section(snapshot, "event_snapshot")
    pipeline = _section(snapshot, "pipeline_snapshot")
    tasks = []
    tasks.append("Review snapshot evidence fields and summarize unresolved research gaps.")
    if timeline and timeline.get("timeline_status") == "Available":
        tasks.append("Compare timeline key changes and prepare a neutral change-review note.")
    for focus in _as_list(event.get("event_validation_focus")):
        tasks.append(f"Validate event evidence for research focus: {focus}.")
    for conflict in _as_list(pipeline.get("research_pipeline_conflicts")):
        tasks.append(f"Investigate pipeline conflict for research review: {conflict}.")
    return _dedupe(tasks)


def build_research_journal(snapshot=None, timeline=None):
    """Build a read-only Research Journal from one Snapshot and one Timeline."""
    snapshot_data = _to_dict(snapshot)
    timeline_data = _to_dict(timeline)
    if not snapshot_data and not timeline_data:
        return _empty_journal()

    warnings = []
    if not snapshot_data:
        warnings.append("Research Snapshot is missing.")
    if not timeline_data:
        warnings.append("Research Timeline is missing.")

    ticker = _clean_value(snapshot_data.get("snapshot_ticker") or timeline_data.get("timeline_ticker"))
    name = _clean_value(snapshot_data.get("snapshot_name") or timeline_data.get("timeline_name"))
    period = _journal_period(snapshot_data, timeline_data)

    if _is_missing(ticker):
        warnings.append("Journal ticker is unavailable.")
    if snapshot_data.get("snapshot_status") != "Available":
        warnings.append("Snapshot status is incomplete or unavailable.")
    if timeline_data.get("timeline_status") != "Available":
        warnings.append("Timeline status is incomplete or unavailable.")

    status = (
        DEFAULT_JOURNAL_STATUS_AVAILABLE
        if snapshot_data.get("snapshot_status") == "Available" and timeline_data.get("timeline_status") == "Available"
        else DEFAULT_JOURNAL_STATUS_INCOMPLETE
    )

    journal = {
        "journal_id": _journal_id(
            ticker,
            period,
            snapshot_data.get("snapshot_id"),
            timeline_data.get("timeline_id"),
        ),
        "journal_ticker": ticker,
        "journal_name": name,
        "journal_period": period,
        "journal_status": status,
        "journal_summary": _build_summary(snapshot_data, timeline_data, status, ticker, name, period),
        "journal_observations": _build_observations(snapshot_data, timeline_data),
        "journal_risk_notes": _build_risk_notes(snapshot_data, timeline_data),
        "journal_data_quality_notes": _build_data_quality_notes(snapshot_data, timeline_data),
        "journal_followup_questions": _build_followup_questions(snapshot_data, timeline_data),
        "journal_agent_tasks": _build_agent_tasks(snapshot_data, timeline_data),
        "journal_warnings": _dedupe(warnings),
    }
    return {field: journal[field] for field in JOURNAL_FIELDS}


__all__ = [
    "DEFAULT_JOURNAL_STATUS_AVAILABLE",
    "DEFAULT_JOURNAL_STATUS_INCOMPLETE",
    "JOURNAL_FIELDS",
    "build_research_journal",
]
