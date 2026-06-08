"""Read-only candidate pool engine for composite screening outputs."""

from __future__ import annotations

import copy
import math

import pandas as pd


CANDIDATE_POOL_FIELDS = [
    "candidate_pool",
    "candidate_rank",
    "candidate_level",
    "candidate_status",
    "candidate_reasons",
    "candidate_risk_flags",
    "candidate_warnings",
]

POOL_CORE = "Core"
POOL_WATCH = "Watch"
POOL_EXCLUDE = "Exclude"
POOL_UNAVAILABLE = "Unavailable"

LEVEL_A = "A"
LEVEL_B = "B"
LEVEL_C = "C"
LEVEL_UNAVAILABLE = "Unavailable"

STATUS_SELECTED = "Selected"
STATUS_WATCH = "Watch"
STATUS_EXCLUDED = "Excluded"
STATUS_INCOMPLETE = "Incomplete"


def _safe_copy_frame(source):
    if source is None:
        return pd.DataFrame()
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    return pd.DataFrame()


def _empty_like(source):
    base = source.copy(deep=True) if isinstance(source, pd.DataFrame) else pd.DataFrame()
    for field in CANDIDATE_POOL_FIELDS:
        base[field] = pd.Series(dtype="object")
    return base


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def _to_score(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def _classify_row(row):
    warnings = []
    reasons = []
    risk_flags = []

    if "composite_available" not in row:
        warnings.append("composite_available missing.")
        risk_flags.append("Missing Data")
        return _unavailable(warnings, risk_flags)

    composite_available = _to_bool(row.get("composite_available"))
    composite_score = _to_score(row.get("composite_score")) if "composite_score" in row else None
    composite_level = row.get("composite_level") if "composite_level" in row else None
    composite_status = row.get("composite_screening_status") if "composite_screening_status" in row else None

    if composite_available is not True:
        warnings.append("Composite score unavailable.")
        risk_flags.append("Missing Data")
        return _unavailable(warnings, risk_flags)
    if composite_score is None:
        warnings.append("composite_score missing or invalid.")
        risk_flags.append("Missing Data")
        return _unavailable(warnings, risk_flags)
    if composite_level is None or pd.isna(composite_level):
        warnings.append("composite_level missing.")
    if composite_status is None or pd.isna(composite_status):
        warnings.append("composite_screening_status missing.")

    level_text = str(composite_level or "").strip()
    status_text = str(composite_status or "").strip()

    if level_text == "High" and status_text == "Pass":
        reasons.append("Composite level is High and status is Pass.")
        return {
            "candidate_pool": POOL_CORE,
            "candidate_rank": None,
            "candidate_level": LEVEL_A,
            "candidate_status": STATUS_SELECTED,
            "candidate_reasons": reasons,
            "candidate_risk_flags": risk_flags,
            "candidate_warnings": warnings,
        }

    if level_text == "Medium" or status_text == "Watch":
        reasons.append("Composite result is suitable for watch-list research review.")
        if composite_score < 60:
            risk_flags.append("Low Score")
        return {
            "candidate_pool": POOL_WATCH,
            "candidate_rank": None,
            "candidate_level": LEVEL_B,
            "candidate_status": STATUS_WATCH,
            "candidate_reasons": reasons,
            "candidate_risk_flags": risk_flags,
            "candidate_warnings": warnings,
        }

    if level_text == "Low" or status_text == "Exclude":
        reasons.append("Composite result indicates weak research-priority structure.")
        risk_flags.append("Low Score")
        if composite_score < 40:
            risk_flags.append("Weak Technical")
            risk_flags.append("Weak Fundamental")
        return {
            "candidate_pool": POOL_EXCLUDE,
            "candidate_rank": None,
            "candidate_level": LEVEL_C,
            "candidate_status": STATUS_EXCLUDED,
            "candidate_reasons": reasons,
            "candidate_risk_flags": risk_flags,
            "candidate_warnings": warnings,
        }

    warnings.append("Composite level or status is not recognized.")
    risk_flags.append("Missing Data")
    return _unavailable(warnings, risk_flags)


def _unavailable(warnings, risk_flags):
    return {
        "candidate_pool": POOL_UNAVAILABLE,
        "candidate_rank": None,
        "candidate_level": LEVEL_UNAVAILABLE,
        "candidate_status": STATUS_INCOMPLETE,
        "candidate_reasons": [],
        "candidate_risk_flags": risk_flags,
        "candidate_warnings": warnings or ["Candidate pool inputs unavailable."],
    }


def _apply_ranks(result):
    rankable = result[result["candidate_pool"].isin([POOL_CORE, POOL_WATCH])].copy()
    if rankable.empty or "composite_score" not in result.columns:
        return result
    rankable["_score"] = rankable["composite_score"].map(_to_score)
    rankable["_input_order"] = range(len(rankable))
    rankable = rankable.sort_values(by=["_score", "_input_order"], ascending=[False, True])
    for rank, index in enumerate(rankable.index, start=1):
        result.at[index, "candidate_rank"] = rank
    return result


def build_candidate_pool(composite_df):
    """Append read-only candidate-pool fields without changing row order."""
    source = _safe_copy_frame(composite_df)
    if source.empty:
        return _empty_like(source)

    result = source.copy(deep=True)
    output = pd.DataFrame([_classify_row(row.to_dict()) for _, row in result.iterrows()], index=result.index)
    for field in CANDIDATE_POOL_FIELDS:
        result[field] = output[field]
    result = _apply_ranks(result)
    return result


__all__ = [
    "CANDIDATE_POOL_FIELDS",
    "build_candidate_pool",
]
