"""Read-only event evidence quality diagnostics for research preview."""

import copy
import math

import pandas as pd


EVENT_DIAGNOSTIC_FIELDS = [
    "event_completeness_score",
    "event_clarity_score",
    "event_consistency_score",
    "event_confidence_score",
    "event_diagnostic_level",
    "event_diagnostic_summary",
    "event_followup_questions",
    "event_evidence_gaps",
    "event_quality_warnings",
]

_RAW_EVENT_FIELDS = [
    "event_title",
    "event_summary",
    "event_type",
    "event_date",
    "event_source",
    "event_source_type",
    "event_confidence",
]

_KNOWN_TYPES = {"earnings", "policy", "industry", "macro", "product", "risk", "news_only"}
_SOURCE_QUALITY_SCORES = {
    "Official": 95,
    "Reliable Media": 75,
    "Unverified": 35,
    "Unknown": 45,
}
_RELIABILITY_SCORES = {
    "High": 90,
    "Medium": 65,
    "Low": 30,
    "Unknown": 45,
}


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
    return any(not _is_missing(row.get(field)) for field in _RAW_EVENT_FIELDS if field != "event_type")


def _score_from_present(row, fields):
    present = sum(1 for field in fields if not _is_missing(row.get(field)))
    return int(round(100 * present / len(fields)))


def _completeness_score(row):
    score = _score_from_present(
        row,
        [
            "event_title",
            "event_summary",
            "event_type",
            "event_date",
            "event_source",
            "event_source_type",
            "event_confidence",
        ],
    )
    if _text(row.get("event_recency_label")) not in {"", "Unknown"}:
        score = min(100, score + 5)
    if _text(row.get("event_source_quality_label")) not in {"", "Unknown"}:
        score = min(100, score + 5)
    return score


def _clarity_score(row):
    event_type = _text(row.get("event_type")).lower()
    summary = _text(row.get("event_summary"))
    title = _text(row.get("event_title"))
    note = _text(row.get("event_context_note"))
    score = 40
    if event_type in _KNOWN_TYPES:
        score += 25
    elif event_type == "unknown":
        score -= 15
    if len(summary) >= 30:
        score += 20
    elif summary:
        score += 10
    if title:
        score += 10
    if note and "unavailable" not in note.lower():
        score += 5
    return max(0, min(100, score))


def _consistency_score(row):
    event_type = _text(row.get("event_type")).lower()
    source_quality = _text(row.get("event_source_quality_label"))
    reliability = _text(row.get("event_reliability_label"))
    warnings = " ".join(_as_list(row.get("event_warnings"))).lower()
    score = 90
    if event_type in {"", "unknown"} and "type" in warnings:
        score -= 20
    if source_quality == "Unverified" and reliability == "High":
        score -= 35
    if source_quality == "Official" and reliability == "Low":
        score -= 30
    if source_quality == "Unknown" and reliability == "High":
        score -= 20
    if "date" in warnings and _text(row.get("event_recency_label")) == "Recent":
        score -= 20
    if _as_list(row.get("event_warnings")):
        score -= min(20, len(_as_list(row.get("event_warnings"))) * 5)
    return max(0, min(100, score))


def _confidence_score(completeness, clarity, consistency, row):
    source_quality = _text(row.get("event_source_quality_label")) or "Unknown"
    reliability = _text(row.get("event_reliability_label")) or "Unknown"
    source_score = _SOURCE_QUALITY_SCORES.get(source_quality, 45)
    reliability_score = _RELIABILITY_SCORES.get(reliability, 45)
    weighted = (
        completeness * 0.25
        + clarity * 0.25
        + consistency * 0.20
        + source_score * 0.15
        + reliability_score * 0.15
    )
    return int(round(max(0, min(100, weighted))))


def _evidence_gaps(row, available):
    if not available:
        return ["event evidence unavailable"]
    gaps = []
    if _is_missing(row.get("event_title")):
        gaps.append("event title missing")
    if _is_missing(row.get("event_summary")):
        gaps.append("event summary missing")
    if _text(row.get("event_type")).lower() in {"", "unknown", "news_only"}:
        gaps.append("event type needs clearer classification")
    if _is_missing(row.get("event_date")) or _text(row.get("event_recency_label")) == "Unknown":
        gaps.append("event date missing or invalid")
    if _is_missing(row.get("event_source")):
        gaps.append("event source missing")
    if _text(row.get("event_source_quality_label")) == "Unknown":
        gaps.append("event source quality unclear")
    if _text(row.get("event_reliability_label")) == "Unknown":
        gaps.append("event reliability unclear")
    return list(dict.fromkeys(gaps))


def _quality_warnings(row, available, confidence):
    if not available:
        return ["event diagnostics unavailable"]
    warnings = []
    source_quality = _text(row.get("event_source_quality_label"))
    reliability = _text(row.get("event_reliability_label"))
    if source_quality in {"Unknown", "Unverified"}:
        warnings.append("event source needs validation")
    if reliability in {"Unknown", "Low"}:
        warnings.append("event reliability needs review")
    if confidence < 50:
        warnings.append("event evidence quality is weak")
    warnings.extend(str(item) for item in _as_list(row.get("event_warnings")) if item)
    return list(dict.fromkeys(warnings))


def _level(available, confidence, completeness, clarity):
    if not available:
        return "Unavailable"
    if confidence >= 78 and completeness >= 70 and clarity >= 70:
        return "Strong"
    if confidence >= 58:
        return "Usable"
    return "Weak"


def _summary(level, gaps):
    if level == "Unavailable":
        return "Event diagnostics are unavailable because usable event evidence is not present."
    if level == "Strong":
        return "Event evidence is complete enough for structured follow-up research."
    if level == "Usable":
        return "Event evidence can support follow-up research after reviewing the listed gaps."
    return "Event evidence is weak and needs validation before use in deeper research."


def _followup_questions(row, level, gaps):
    if level == "Unavailable":
        return ["What event evidence should be collected before research review?"]
    questions = []
    event_type = _text(row.get("event_type")).lower() or "event"
    questions.append(f"How does this {event_type} context connect to existing technical and fundamental evidence?")
    if "event date missing or invalid" in gaps:
        questions.append("What is the confirmed event date for recency review?")
    if "event source missing" in gaps or "event source quality unclear" in gaps:
        questions.append("Which primary or reliable source can validate this event?")
    if "event type needs clearer classification" in gaps:
        questions.append("Which event category best describes the research context?")
    if _text(row.get("event_reliability_label")) in {"Low", "Unknown"}:
        questions.append("What additional evidence can improve event reliability review?")
    return list(dict.fromkeys(questions))[:4]


def build_event_diagnostics_row(row):
    row_data = _row_dict(row)
    available = _event_available(row_data)
    if not available:
        gaps = _evidence_gaps(row_data, available)
        return {
            "event_completeness_score": 0,
            "event_clarity_score": 0,
            "event_consistency_score": 0,
            "event_confidence_score": 0,
            "event_diagnostic_level": "Unavailable",
            "event_diagnostic_summary": _summary("Unavailable", gaps),
            "event_followup_questions": _followup_questions(row_data, "Unavailable", gaps),
            "event_evidence_gaps": gaps,
            "event_quality_warnings": _quality_warnings(row_data, available, 0),
        }

    completeness = _completeness_score(row_data)
    clarity = _clarity_score(row_data)
    consistency = _consistency_score(row_data)
    confidence = _confidence_score(completeness, clarity, consistency, row_data)
    gaps = _evidence_gaps(row_data, available)
    level = _level(available, confidence, completeness, clarity)

    return {
        "event_completeness_score": completeness,
        "event_clarity_score": clarity,
        "event_consistency_score": consistency,
        "event_confidence_score": confidence,
        "event_diagnostic_level": level,
        "event_diagnostic_summary": _summary(level, gaps),
        "event_followup_questions": _followup_questions(row_data, level, gaps),
        "event_evidence_gaps": gaps,
        "event_quality_warnings": _quality_warnings(row_data, available, confidence),
    }


def build_event_diagnostics_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=EVENT_DIAGNOSTIC_FIELDS)
    rows = [build_event_diagnostics_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=EVENT_DIAGNOSTIC_FIELDS)


__all__ = [
    "EVENT_DIAGNOSTIC_FIELDS",
    "build_event_diagnostics_profile",
    "build_event_diagnostics_row",
]
