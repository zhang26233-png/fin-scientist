"""Read-only research priority stability diagnostics."""

import copy
import math

import pandas as pd


PRIORITY_STABILITY_FIELDS = [
    "priority_stability_label",
    "priority_stability_score",
    "priority_stability_note",
    "priority_drift_detected",
    "priority_drift_reason",
]

_PRIORITY_LEVELS = {
    "priority_research",
    "worth_tracking",
    "watch_with_caution",
    "low_priority",
    "insufficient_data",
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


def _safe_score(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return max(0, min(100, int(round(number))))


def _safe_level(value):
    if value is None:
        return ""
    text = str(value).strip()
    return text if text else ""


def _expected_level(score):
    if score is None:
        return ""
    if score >= 75:
        return "priority_research"
    if score >= 58:
        return "worth_tracking"
    if score >= 35:
        return "watch_with_caution"
    if score <= 20:
        return "insufficient_data"
    return "low_priority"


def _priority_available(score, level):
    return score is not None and bool(level) and level in _PRIORITY_LEVELS


def _reference_drift(row, reference):
    if not isinstance(reference, dict):
        return []
    reasons = []
    for field in (
        "research_priority_score",
        "research_priority_level",
        "research_priority_reasons",
        "research_priority_warnings",
    ):
        if row.get(field) != reference.get(field):
            reasons.append(f"{field} differs from reference snapshot")
    return reasons


def build_priority_stability_row(row, reference=None):
    """Build read-only stability diagnostics for one priority row."""
    row_data = _row_dict(row)
    reference_data = _row_dict(reference) if reference is not None else None
    score = _safe_score(row_data.get("research_priority_score"))
    level = _safe_level(row_data.get("research_priority_level"))

    missing = []
    if score is None:
        missing.append("research_priority_score missing or invalid")
    if not level:
        missing.append("research_priority_level missing")
    elif level not in _PRIORITY_LEVELS:
        missing.append("research_priority_level outside known labels")

    if not _priority_available(score, level):
        return {
            "priority_stability_label": "Unavailable",
            "priority_stability_score": 0,
            "priority_stability_note": "Priority fields are incomplete; use source fields for research review.",
            "priority_drift_detected": True,
            "priority_drift_reason": "; ".join(missing) if missing else "priority fields unavailable",
        }

    expected = _expected_level(score)
    drift_reasons = []
    if level != expected:
        drift_reasons.append(f"level {level} does not match score band {expected}")
    if reference_data is not None:
        drift_reasons.extend(_reference_drift(row_data, reference_data))

    if drift_reasons:
        return {
            "priority_stability_label": "Watch",
            "priority_stability_score": 55,
            "priority_stability_note": "Priority fields are available but need consistency review.",
            "priority_drift_detected": True,
            "priority_drift_reason": "; ".join(drift_reasons),
        }

    stability_score = 95
    if level == "insufficient_data":
        stability_score = 70
    elif row_data.get("research_priority_warnings"):
        stability_score = 85

    return {
        "priority_stability_label": "Stable",
        "priority_stability_score": stability_score,
        "priority_stability_note": "Priority fields are complete and internally consistent for research review.",
        "priority_drift_detected": False,
        "priority_drift_reason": "",
    }


def build_priority_stability_profile(source, reference_source=None):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=PRIORITY_STABILITY_FIELDS)

    reference_frame = _source_to_frame(reference_source)
    references = []
    if not reference_frame.empty:
        references = [row.to_dict() for _, row in reference_frame.iterrows()]

    rows = []
    for index, (_, row) in enumerate(frame.iterrows()):
        reference = references[index] if index < len(references) else None
        rows.append(build_priority_stability_row(row, reference=reference))
    return pd.DataFrame(rows, columns=PRIORITY_STABILITY_FIELDS)


__all__ = [
    "PRIORITY_STABILITY_FIELDS",
    "build_priority_stability_profile",
    "build_priority_stability_row",
]
