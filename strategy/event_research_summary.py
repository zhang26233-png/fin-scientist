"""Read-only event research summaries for Agent-ready context."""

import copy
import math

import pandas as pd


EVENT_RESEARCH_SUMMARY_FIELDS = [
    "event_research_summary",
    "event_research_level",
    "event_key_evidence",
    "event_key_risks",
    "event_validation_focus",
    "event_agent_note",
    "event_summary_warnings",
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


def _text(value):
    return "" if _is_missing(value) else str(value).strip()


def _as_list(value):
    if isinstance(value, list):
        return copy.deepcopy(value)
    if isinstance(value, tuple):
        return list(value)
    if _is_missing(value):
        return []
    return [str(value)]


def _clean_list(items, limit=4):
    output = []
    for item in items:
        text = _text(item)
        if not text or text in output:
            continue
        output.append(text)
        if len(output) >= limit:
            break
    return output


def _safe_score(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return max(0, min(100, int(round(number))))


def _event_available(row):
    value = row.get("event_available")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return False


def _summary_level(row, available):
    if not available:
        return "Unavailable"
    diagnostic = _text(row.get("event_diagnostic_level"))
    confluence = _text(row.get("event_confluence_label"))
    confidence = _safe_score(row.get("event_confidence_score"))
    confluence_score = _safe_score(row.get("event_confluence_score"))
    if diagnostic == "Strong" and confluence == "Supportive" and (confidence is None or confidence >= 70):
        return "High"
    if diagnostic in {"Strong", "Usable"} and confluence in {"Supportive", "Mixed"}:
        if confluence_score is None or confluence_score >= 45:
            return "Medium"
    if diagnostic == "Unavailable" or confluence == "Unavailable":
        return "Unavailable"
    return "Low"


def _key_evidence(row, level):
    if level == "Unavailable":
        return []
    evidence = []
    event_type = _text(row.get("event_type"))
    if event_type and event_type != "unknown":
        evidence.append(f"event type classified as {event_type}")
    context_note = _text(row.get("event_context_note"))
    if context_note and "unavailable" not in context_note.lower():
        evidence.append(context_note)
    evidence.extend(_as_list(row.get("event_support_points")))
    tags = _as_list(row.get("event_research_tags"))
    if tags:
        evidence.append("research tags: " + ", ".join(tags[:3]))
    return _clean_list(evidence)


def _key_risks(row, level):
    risks = []
    if level == "Unavailable":
        risks.append("event summary unavailable due to missing event context")
    risks.extend(_as_list(row.get("event_conflict_points")))
    risks.extend(_as_list(row.get("event_evidence_gaps")))
    risks.extend(_as_list(row.get("event_confluence_warnings")))
    return _clean_list(risks)


def _validation_focus(row, level):
    focus = []
    focus.extend(_as_list(row.get("event_followup_focus")))
    focus.extend(_as_list(row.get("event_followup_questions")))
    if level in {"Low", "Unavailable"}:
        focus.append("Collect stronger event evidence before deeper synthesis.")
    if not focus:
        focus.append("Validate event context against technical, fundamental, and industry evidence.")
    return _clean_list(focus)


def _warnings(row, level, risks):
    warnings = []
    if level == "Unavailable":
        warnings.append("event research summary unavailable")
    if level == "Low":
        warnings.append("event research summary has limited evidence quality")
    if _text(row.get("event_confluence_label")) == "Conflicting":
        warnings.append("event confluence conflict needs review")
    warnings.extend(_as_list(row.get("event_quality_warnings")))
    warnings.extend(_as_list(row.get("event_confluence_warnings")))
    if risks and level in {"Low", "Unavailable"}:
        warnings.append("event risks should be resolved before Agent synthesis")
    return _clean_list(warnings)


def _summary_text(row, level, evidence, risks):
    if level == "Unavailable":
        return "Event research summary is unavailable because usable event context is not present."
    event_type = _text(row.get("event_type")) or "event"
    confluence = _text(row.get("event_confluence_label")) or "Mixed"
    evidence_count = len(evidence)
    risk_count = len(risks)
    return (
        f"{event_type} context has {level.lower()} research value for follow-up review; "
        f"event confluence is {confluence}; evidence items: {evidence_count}; risk or uncertainty items: {risk_count}."
    )


def _agent_note(row, level, evidence, risks, focus):
    if level == "Unavailable":
        return "Agent note: event context is unavailable; request source evidence before synthesis."
    event_type = _text(row.get("event_type")) or "event"
    confluence = _text(row.get("event_confluence_label")) or "Mixed"
    return (
        f"Agent note: use this {event_type} context as {level.lower()}-level evidence; "
        f"confluence={confluence}; evidence_count={len(evidence)}; risk_count={len(risks)}; "
        f"validation_focus_count={len(focus)}."
    )


def build_event_research_summary_row(row):
    row_data = _row_dict(row)
    available = _event_available(row_data)
    level = _summary_level(row_data, available)
    evidence = _key_evidence(row_data, level)
    risks = _key_risks(row_data, level)
    focus = _validation_focus(row_data, level)
    warnings = _warnings(row_data, level, risks)
    return {
        "event_research_summary": _summary_text(row_data, level, evidence, risks),
        "event_research_level": level,
        "event_key_evidence": evidence,
        "event_key_risks": risks,
        "event_validation_focus": focus,
        "event_agent_note": _agent_note(row_data, level, evidence, risks, focus),
        "event_summary_warnings": warnings,
    }


def build_event_research_summary_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=EVENT_RESEARCH_SUMMARY_FIELDS)
    rows = [build_event_research_summary_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=EVENT_RESEARCH_SUMMARY_FIELDS)


__all__ = [
    "EVENT_RESEARCH_SUMMARY_FIELDS",
    "build_event_research_summary_profile",
    "build_event_research_summary_row",
]
