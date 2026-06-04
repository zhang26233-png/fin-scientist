"""Read-only event confluence checks against the current research profile."""

import copy
import math

import pandas as pd


EVENT_CONFLUENCE_FIELDS = [
    "event_confluence_label",
    "event_confluence_score",
    "event_confluence_summary",
    "event_support_points",
    "event_conflict_points",
    "event_followup_focus",
    "event_confluence_warnings",
]

_POSITIVE_GRADES = {"A", "B"}
_WEAK_GRADES = {"C", "D", "insufficient_data"}
_SUPPORTIVE_EVENT_TYPES = {"earnings", "industry", "product", "policy"}
_RISK_EVENT_TYPES = {"risk", "macro"}


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


def _profile_positive(row):
    technical = _text(row.get("technical_grade"))
    fundamental = _text(row.get("fundamental_grade"))
    composite = _text(row.get("composite_research_grade"))
    relative = _text(row.get("industry_relative_quality_label"))
    level = _text(row.get("composite_research_level"))
    positive_count = sum(
        [
            technical in _POSITIVE_GRADES,
            fundamental in _POSITIVE_GRADES,
            composite in _POSITIVE_GRADES,
            relative in {"industry_relative_strong", "industry_relative_neutral"},
            level in {"priority_research", "worth_tracking"},
        ]
    )
    return positive_count >= 3


def _profile_weak_or_risky(row):
    technical = _text(row.get("technical_grade"))
    fundamental = _text(row.get("fundamental_grade"))
    composite = _text(row.get("composite_research_grade"))
    risk = _text(row.get("composite_risk_level"))
    relative = _text(row.get("industry_relative_quality_label"))
    weak_count = sum(
        [
            technical in _WEAK_GRADES,
            fundamental in _WEAK_GRADES,
            composite in _WEAK_GRADES,
            risk in {"high", "elevated"},
            relative in {"industry_relative_weak", "insufficient_industry_data"},
        ]
    )
    return weak_count >= 2


def _event_quality(row):
    level = _text(row.get("event_diagnostic_level"))
    confidence = _safe_score(row.get("event_confidence_score"))
    reliability = _text(row.get("event_reliability_label"))
    high = level == "Strong" and (confidence is None or confidence >= 70) and reliability in {"High", "Medium"}
    low = level in {"Weak", "Unavailable"} or (confidence is not None and confidence < 50) or reliability in {"Low", "Unknown"}
    return {"level": level, "confidence": confidence, "reliability": reliability, "high": high, "low": low}


def _support_points(row, quality):
    if not quality["high"]:
        return []
    points = []
    event_type = _text(row.get("event_type")).lower()
    if event_type in _SUPPORTIVE_EVENT_TYPES and _profile_positive(row):
        points.append("high-quality event context aligns with the stronger parts of the current research profile")
    if event_type == "earnings" and _text(row.get("fundamental_grade")) in _POSITIVE_GRADES:
        points.append("earnings context can help verify the fundamental profile")
    if event_type in {"industry", "policy"} and _text(row.get("industry_relative_quality_label")) in {
        "industry_relative_strong",
        "industry_relative_neutral",
    }:
        points.append("event category is relevant to industry-relative research review")
    if event_type == "product" and _text(row.get("composite_research_grade")) in _POSITIVE_GRADES:
        points.append("product context can extend composite profile follow-up research")
    return list(dict.fromkeys(points))[:3]


def _conflict_points(row, quality):
    points = []
    event_type = _text(row.get("event_type")).lower()
    if event_type in _RISK_EVENT_TYPES and _profile_positive(row):
        points.append("risk-oriented event context needs review against the stronger research profile")
    if event_type in _SUPPORTIVE_EVENT_TYPES and _profile_weak_or_risky(row):
        points.append("supportive event category contrasts with weak or higher-risk profile fields")
    if quality["low"]:
        points.append("event evidence quality is not strong enough to support profile confluence")
    if _text(row.get("composite_risk_level")) in {"high", "elevated"} and event_type != "risk":
        points.append("composite risk level needs separate validation alongside the event context")
    return list(dict.fromkeys(points))[:3]


def _warnings(row, available, quality):
    if not available:
        return ["event confluence unavailable because event context is not available"]
    warnings = []
    if quality["low"]:
        warnings.append("event quality limits confluence review")
    warnings.extend(str(item) for item in _as_list(row.get("event_quality_warnings")) if item)
    warnings.extend(str(item) for item in _as_list(row.get("event_evidence_gaps")) if item)
    missing_profile = [
        field
        for field in (
            "technical_grade",
            "fundamental_grade",
            "industry_relative_quality_label",
            "composite_research_grade",
            "composite_research_level",
            "composite_risk_level",
        )
        if _is_missing(row.get(field))
    ]
    if missing_profile:
        warnings.append("research profile fields incomplete for event confluence review")
    return list(dict.fromkeys(warnings))[:6]


def _label(available, supports, conflicts, quality):
    if not available:
        return "Unavailable"
    if quality["low"] and not supports:
        return "Unavailable" if quality["level"] == "Unavailable" else "Mixed"
    if supports and conflicts:
        return "Mixed"
    if supports:
        return "Supportive"
    if conflicts:
        return "Conflicting"
    return "Mixed"


def _score(label, supports, conflicts, quality):
    if label == "Unavailable":
        return 0
    base = {
        "Supportive": 78,
        "Mixed": 55,
        "Conflicting": 35,
    }.get(label, 45)
    confidence = quality["confidence"]
    if confidence is not None:
        base = int(round(base * 0.7 + confidence * 0.3))
    base += min(10, len(supports) * 4)
    base -= min(18, len(conflicts) * 6)
    if quality["low"]:
        base -= 12
    return max(0, min(100, int(round(base))))


def _summary(label, score):
    if label == "Unavailable":
        return "Event confluence is unavailable because event context or event quality is insufficient."
    if label == "Supportive":
        return f"Event context is broadly aligned with the current research profile; confluence score is {score}."
    if label == "Conflicting":
        return f"Event context conflicts with parts of the current research profile; confluence score is {score}."
    return f"Event context provides mixed or supplementary evidence for the current research profile; confluence score is {score}."


def _followup_focus(row, supports, conflicts, warnings):
    focus = []
    focus.extend(_as_list(row.get("event_followup_questions")))
    if supports:
        focus.append("Verify whether event evidence is reflected in technical, fundamental, or industry-relative fields.")
    if conflicts:
        focus.append("Review why event context differs from the current research profile.")
    if warnings:
        focus.append("Resolve event evidence gaps before using this context in deeper research synthesis.")
    if not focus:
        focus.append("Collect stronger event and profile evidence before confluence review.")
    return list(dict.fromkeys(focus))[:4]


def build_event_confluence_row(row):
    row_data = _row_dict(row)
    available = _event_available(row_data)
    quality = _event_quality(row_data)
    supports = _support_points(row_data, quality)
    conflicts = _conflict_points(row_data, quality)
    warnings = _warnings(row_data, available, quality)
    label = _label(available, supports, conflicts, quality)
    score = _score(label, supports, conflicts, quality)
    return {
        "event_confluence_label": label,
        "event_confluence_score": score,
        "event_confluence_summary": _summary(label, score),
        "event_support_points": supports,
        "event_conflict_points": conflicts,
        "event_followup_focus": _followup_focus(row_data, supports, conflicts, warnings),
        "event_confluence_warnings": warnings,
    }


def build_event_confluence_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=EVENT_CONFLUENCE_FIELDS)
    rows = [build_event_confluence_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=EVENT_CONFLUENCE_FIELDS)


__all__ = [
    "EVENT_CONFLUENCE_FIELDS",
    "build_event_confluence_profile",
    "build_event_confluence_row",
]
