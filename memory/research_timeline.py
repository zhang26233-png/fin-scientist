"""Read-only research timeline schema for v2.1 memory layer."""

import copy
import hashlib
import math

import pandas as pd


TIMELINE_FIELDS = [
    "timeline_id",
    "timeline_ticker",
    "timeline_name",
    "timeline_snapshot_count",
    "timeline_start_time",
    "timeline_end_time",
    "timeline_status",
    "timeline_direction",
    "timeline_change_summary",
    "timeline_key_changes",
    "timeline_priority_trend",
    "timeline_event_trend",
    "timeline_pipeline_trend",
    "timeline_warnings",
]

DEFAULT_TIMELINE_STATUS_INCOMPLETE = "Incomplete"
DEFAULT_TIMELINE_STATUS_AVAILABLE = "Available"
DEFAULT_TIMELINE_DIRECTION_UNAVAILABLE = "Unavailable"

PRIORITY_COMPARE_FIELDS = [
    "research_priority_score",
    "research_priority_level",
    "priority_stability_label",
    "priority_stability_score",
]

EVENT_COMPARE_FIELDS = [
    "event_available",
    "event_diagnostic_level",
    "event_confidence_score",
    "event_confluence_label",
    "event_confluence_score",
    "event_research_level",
]

PIPELINE_COMPARE_FIELDS = [
    "architecture_audit_label",
    "architecture_audit_score",
    "research_pipeline_status",
]

IMPROVING_LABELS = {
    "High",
    "Strong",
    "Supportive",
    "Healthy",
    "Pass",
    "Stable",
    "Ready",
    "priority_research",
}

DETERIORATING_LABELS = {
    "Low",
    "Weak",
    "Conflicting",
    "Conflict",
    "Incomplete",
    "Fail",
    "Not Ready",
}


def _empty_timeline(warnings=None):
    timeline = {
        "timeline_id": None,
        "timeline_ticker": None,
        "timeline_name": None,
        "timeline_snapshot_count": 0,
        "timeline_start_time": None,
        "timeline_end_time": None,
        "timeline_status": DEFAULT_TIMELINE_STATUS_INCOMPLETE,
        "timeline_direction": DEFAULT_TIMELINE_DIRECTION_UNAVAILABLE,
        "timeline_change_summary": "No research snapshots available for timeline review.",
        "timeline_key_changes": [],
        "timeline_priority_trend": _empty_trend("priority_snapshot"),
        "timeline_event_trend": _empty_trend("event_snapshot"),
        "timeline_pipeline_trend": _empty_trend("pipeline_snapshot"),
        "timeline_warnings": warnings or ["No snapshots provided."],
    }
    return {field: timeline[field] for field in TIMELINE_FIELDS}


def _empty_trend(section):
    return {
        "section": section,
        "direction": DEFAULT_TIMELINE_DIRECTION_UNAVAILABLE,
        "changed_fields": [],
        "start": {},
        "end": {},
        "warnings": [],
    }


def _snapshot_list(source):
    if source is None:
        return []
    if isinstance(source, pd.DataFrame):
        return [copy.deepcopy(row.to_dict()) for _, row in source.iterrows()]
    if isinstance(source, pd.Series):
        return [copy.deepcopy(source.to_dict())]
    if isinstance(source, dict):
        return [copy.deepcopy(source)]
    if isinstance(source, (list, tuple)):
        return [copy.deepcopy(item) for item in source if isinstance(item, dict)]
    return []


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


def _sort_key(snapshot):
    timestamp = snapshot.get("snapshot_timestamp")
    if _is_missing(timestamp):
        return ""
    return str(timestamp)


def _timeline_id(ticker, start_time, end_time, count):
    ticker_part = str(ticker or "unknown")
    basis = f"{ticker_part}|{start_time}|{end_time}|{count}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]
    return f"timeline-{ticker_part}-{digest}"


def _section(snapshot, section_name):
    value = snapshot.get(section_name)
    if isinstance(value, dict):
        return value
    return {}


def _value_direction(start, end):
    if _is_missing(start) and _is_missing(end):
        return "Stable"
    if _is_missing(start) and not _is_missing(end):
        return "Improving"
    if not _is_missing(start) and _is_missing(end):
        return "Deteriorating"
    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        if end > start:
            return "Improving"
        if end < start:
            return "Deteriorating"
        return "Stable"
    if start == end:
        return "Stable"
    if str(end) in IMPROVING_LABELS and str(start) not in IMPROVING_LABELS:
        return "Improving"
    if str(end) in DETERIORATING_LABELS and str(start) not in DETERIORATING_LABELS:
        return "Deteriorating"
    return "Mixed"


def _summarize_direction(directions):
    active = [direction for direction in directions if direction != "Stable"]
    if not directions:
        return DEFAULT_TIMELINE_DIRECTION_UNAVAILABLE
    if not active:
        return "Stable"
    if all(direction == "Improving" for direction in active):
        return "Improving"
    if all(direction == "Deteriorating" for direction in active):
        return "Deteriorating"
    return "Mixed"


def _build_trend(start_snapshot, end_snapshot, section_name, fields):
    start_section = _section(start_snapshot, section_name)
    end_section = _section(end_snapshot, section_name)
    warnings = []
    if not start_section:
        warnings.append(f"Missing start {section_name}.")
    if not end_section:
        warnings.append(f"Missing end {section_name}.")

    changed_fields = []
    field_directions = []
    for field in fields:
        start_value = _clean_value(start_section.get(field))
        end_value = _clean_value(end_section.get(field))
        direction = _value_direction(start_value, end_value)
        if start_value != end_value:
            changed_fields.append(
                {
                    "field": field,
                    "from": start_value,
                    "to": end_value,
                    "direction": direction,
                }
            )
            field_directions.append(direction)

    return {
        "section": section_name,
        "direction": _summarize_direction(field_directions),
        "changed_fields": changed_fields,
        "start": {field: _clean_value(start_section.get(field)) for field in fields},
        "end": {field: _clean_value(end_section.get(field)) for field in fields},
        "warnings": warnings,
    }


def _key_changes(*trends):
    changes = []
    for trend in trends:
        section = trend["section"]
        for change in trend["changed_fields"]:
            changes.append(
                {
                    "section": section,
                    "field": change["field"],
                    "from": change["from"],
                    "to": change["to"],
                    "direction": change["direction"],
                }
            )
    return changes


def _timeline_summary(ticker, name, count, direction, key_changes):
    display_name = f" {name}" if name else ""
    if count <= 1:
        return f"Research timeline for {ticker or 'unknown'}{display_name} is incomplete; at least two snapshots are needed for change review."
    if not key_changes:
        return f"Research timeline for {ticker or 'unknown'}{display_name} is available; tracked sections are stable across {count} snapshots."
    return (
        f"Research timeline for {ticker or 'unknown'}{display_name} is available; "
        f"overall direction={direction}; tracked changes={len(key_changes)}."
    )


def build_research_timeline(snapshots):
    """Build a read-only timeline from Research Snapshot dictionaries."""
    snapshot_rows = _snapshot_list(snapshots)
    if not snapshot_rows:
        return _empty_timeline()

    sorted_snapshots = sorted(snapshot_rows, key=_sort_key)
    warnings = []
    missing_timestamps = [item for item in sorted_snapshots if _is_missing(item.get("snapshot_timestamp"))]
    if missing_timestamps:
        warnings.append("One or more snapshots are missing snapshot_timestamp.")

    tickers = [item.get("snapshot_ticker") for item in sorted_snapshots if not _is_missing(item.get("snapshot_ticker"))]
    unique_tickers = []
    for ticker in tickers:
        if ticker not in unique_tickers:
            unique_tickers.append(ticker)
    if len(unique_tickers) > 1:
        warnings.append("Snapshots contain inconsistent snapshot_ticker values.")

    base_ticker = unique_tickers[0] if unique_tickers else None
    same_ticker_snapshots = [
        item for item in sorted_snapshots if _is_missing(item.get("snapshot_ticker")) or item.get("snapshot_ticker") == base_ticker
    ]
    if len(same_ticker_snapshots) != len(sorted_snapshots):
        warnings.append("Timeline comparison used snapshots matching the first available ticker only.")
    if not base_ticker and sorted_snapshots:
        warnings.append("Timeline ticker is unavailable.")

    start_snapshot = same_ticker_snapshots[0] if same_ticker_snapshots else sorted_snapshots[0]
    end_snapshot = same_ticker_snapshots[-1] if same_ticker_snapshots else sorted_snapshots[-1]
    count = len(same_ticker_snapshots)
    ticker = _clean_value(start_snapshot.get("snapshot_ticker") or base_ticker)
    name = _clean_value(start_snapshot.get("snapshot_name") or end_snapshot.get("snapshot_name"))
    start_time = _clean_value(start_snapshot.get("snapshot_timestamp"))
    end_time = _clean_value(end_snapshot.get("snapshot_timestamp"))

    priority_trend = _build_trend(start_snapshot, end_snapshot, "priority_snapshot", PRIORITY_COMPARE_FIELDS)
    event_trend = _build_trend(start_snapshot, end_snapshot, "event_snapshot", EVENT_COMPARE_FIELDS)
    pipeline_trend = _build_trend(start_snapshot, end_snapshot, "pipeline_snapshot", PIPELINE_COMPARE_FIELDS)
    key_changes = _key_changes(priority_trend, event_trend, pipeline_trend)

    if count <= 1:
        warnings.append("At least two snapshots are needed for timeline change review.")
        status = DEFAULT_TIMELINE_STATUS_INCOMPLETE
        direction = DEFAULT_TIMELINE_DIRECTION_UNAVAILABLE
    else:
        status = DEFAULT_TIMELINE_STATUS_AVAILABLE
        direction = _summarize_direction(
            [
                priority_trend["direction"],
                event_trend["direction"],
                pipeline_trend["direction"],
            ]
        )

    timeline = {
        "timeline_id": _timeline_id(ticker, start_time, end_time, count),
        "timeline_ticker": ticker,
        "timeline_name": name,
        "timeline_snapshot_count": count,
        "timeline_start_time": start_time,
        "timeline_end_time": end_time,
        "timeline_status": status,
        "timeline_direction": direction,
        "timeline_change_summary": _timeline_summary(ticker, name, count, direction, key_changes),
        "timeline_key_changes": key_changes,
        "timeline_priority_trend": priority_trend,
        "timeline_event_trend": event_trend,
        "timeline_pipeline_trend": pipeline_trend,
        "timeline_warnings": warnings,
    }
    return {field: timeline[field] for field in TIMELINE_FIELDS}


__all__ = [
    "DEFAULT_TIMELINE_DIRECTION_UNAVAILABLE",
    "DEFAULT_TIMELINE_STATUS_AVAILABLE",
    "DEFAULT_TIMELINE_STATUS_INCOMPLETE",
    "EVENT_COMPARE_FIELDS",
    "PIPELINE_COMPARE_FIELDS",
    "PRIORITY_COMPARE_FIELDS",
    "TIMELINE_FIELDS",
    "build_research_timeline",
]
