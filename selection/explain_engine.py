"""Explainable selection layer for read-only stock selection research."""

from __future__ import annotations

import copy

import pandas as pd


EXPLAIN_SELECTION_FIELDS = [
    "explain_available",
    "explain_status",
    "selection_thesis",
    "selection_strengths",
    "selection_risks",
    "selection_factor_breakdown",
    "selection_reason_score",
    "selection_explanation",
    "selection_summary",
    "explain_warnings",
]

STATUS_AVAILABLE = "Available"
STATUS_INCOMPLETE = "Incomplete"
UNAVAILABLE = "Unavailable"


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
    for field in EXPLAIN_SELECTION_FIELDS:
        base[field] = pd.Series(dtype="object")
    return base


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if value is None or pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def _safe_text(row, field, warnings, default=UNAVAILABLE):
    if field not in row.index:
        warnings.append(f"{field} column missing.")
        return default
    value = row[field]
    if value is None or pd.isna(value):
        warnings.append(f"{field} value missing.")
        return default
    text = str(value).strip()
    if not text:
        warnings.append(f"{field} value missing.")
        return default
    return text


def _safe_number(row, field, warnings, required=False):
    if field not in row.index:
        if required:
            warnings.append(f"{field} column missing.")
        return None
    value = pd.to_numeric(pd.Series([row[field]]), errors="coerce").iloc[0]
    if pd.isna(value):
        if required:
            warnings.append(f"{field} value missing or invalid.")
        return None
    return float(value)


def _incomplete(warnings):
    return {
        "explain_available": False,
        "explain_status": STATUS_INCOMPLETE,
        "selection_thesis": UNAVAILABLE,
        "selection_strengths": [],
        "selection_risks": [],
        "selection_factor_breakdown": {},
        "selection_reason_score": 0,
        "selection_explanation": "Selection explanation is incomplete because required selection fields are unavailable.",
        "selection_summary": "Explanation unavailable",
        "explain_warnings": warnings,
    }


def _choose_thesis(bucket, strengths, risks):
    if bucket == "Core":
        if "Strong Fundamental" in strengths:
            return "Quality Growth"
        if "Strong Technical" in strengths:
            return "Momentum Trend"
        return "High ROE Compounder"
    if bucket == "Watch":
        if "Weak Historical Performance" in risks:
            return "Potential Turnaround"
        if "Strong Fundamental" in strengths:
            return "Value Recovery"
        return "Watch Candidate"
    if bucket == "Exclude":
        return "Weak Candidate"
    return UNAVAILABLE


def _identify_strengths(row):
    warnings = []
    strengths = []
    fundamental_score = _safe_number(row, "fundamental_score", warnings)
    technical_score = _safe_number(row, "technical_score", warnings)
    composite_score = _safe_number(row, "composite_score", warnings)
    performance_label = _safe_text(row, "performance_label", warnings)

    if fundamental_score is not None and fundamental_score >= 80:
        strengths.append("Strong Fundamental")
    if technical_score is not None and technical_score >= 80:
        strengths.append("Strong Technical")
    if composite_score is not None and composite_score >= 80:
        strengths.append("Strong Composite")
    if performance_label == "Strong":
        strengths.append("Strong Historical Performance")
    return strengths


def _identify_risks(row):
    warnings = []
    risks = []
    risk_level = _safe_text(row, "risk_level", warnings)
    max_drawdown = _safe_number(row, "max_drawdown", warnings)
    volatility = _safe_number(row, "volatility", warnings)
    performance_label = _safe_text(row, "performance_label", warnings)

    if risk_level == "High":
        risks.append("High Risk")
    if max_drawdown is not None and abs(max_drawdown) > 0.30:
        risks.append("Large Drawdown Risk")
    if volatility is not None and volatility > 0.35:
        risks.append("High Volatility")
    if performance_label == "Weak":
        risks.append("Weak Historical Performance")
    return risks


def _factor_breakdown(row):
    warnings = []
    fields = [
        "fundamental_score",
        "technical_score",
        "composite_score",
        "risk_score",
    ]
    return {field: _safe_number(row, field, warnings) for field in fields if field in row.index}


def _reason_score(row, strengths, risks, warnings):
    required_fields = [
        "selection_bucket",
        "selection_score",
        "selection_rank",
        "fundamental_score",
        "technical_score",
        "composite_score",
        "risk_score",
    ]
    present = sum(field in row.index and not pd.isna(row[field]) for field in required_fields)
    base = int(round((present / len(required_fields)) * 70))
    evidence = min(30, (len(strengths) + len(risks)) * 6)
    penalty = min(30, len(warnings) * 10)
    return max(0, min(100, base + evidence - penalty))


def _explanation(bucket, status, rank, score, thesis, strengths, risks):
    strength_text = ", ".join(strengths) if strengths else "no major strengths detected from available fields"
    risk_text = ", ".join(risks) if risks else "no major risk flags detected from available fields"
    rank_text = "unavailable" if rank is None else str(int(rank))
    score_text = "unavailable" if score is None else f"{score:.2f}"
    return (
        f"This candidate is in the {bucket} selection bucket with status {status}. "
        f"Its selection rank is {rank_text} and selection score is {score_text}. "
        f"The current thesis is {thesis}. "
        f"Main strengths: {strength_text}. "
        f"Main risks: {risk_text}. "
        "This explanation is for research review only and does not constitute investment advice."
    )


def _summary(thesis, risks):
    if thesis == UNAVAILABLE:
        return "Explanation unavailable"
    if risks:
        summary = f"{thesis}, risks noted"
    else:
        summary = f"{thesis}, risk moderate"
    return summary[:30]


def _explain_row(row):
    warnings = []
    if "selection_available" not in row.index:
        warnings.append("selection_available column missing.")
        return _incomplete(warnings)
    if not _as_bool(row["selection_available"]):
        warnings.append("Stock selection layer is unavailable.")
        return _incomplete(warnings)

    bucket = _safe_text(row, "selection_bucket", warnings)
    status = _safe_text(row, "selection_status", warnings)
    rank = _safe_number(row, "selection_rank", warnings, required=True)
    score = _safe_number(row, "selection_score", warnings, required=True)
    strengths = _identify_strengths(row)
    risks = _identify_risks(row)
    breakdown = _factor_breakdown(row)
    thesis = _choose_thesis(bucket, strengths, risks)
    reason_score = _reason_score(row, strengths, risks, warnings)

    return {
        "explain_available": True,
        "explain_status": STATUS_AVAILABLE,
        "selection_thesis": thesis,
        "selection_strengths": strengths,
        "selection_risks": risks,
        "selection_factor_breakdown": breakdown,
        "selection_reason_score": reason_score,
        "selection_explanation": _explanation(bucket, status, rank, score, thesis, strengths, risks),
        "selection_summary": _summary(thesis, risks),
        "explain_warnings": warnings,
    }


def build_explainable_selection(stock_selection_df):
    """Append explainable selection fields without changing upstream fields or row order."""
    source = _safe_copy_frame(stock_selection_df)
    if source.empty:
        return _empty_like(source)

    result = source.copy(deep=True)
    output_rows = [_explain_row(result.loc[index]) for index in result.index]
    output = pd.DataFrame(output_rows, index=result.index)
    for field in EXPLAIN_SELECTION_FIELDS:
        result[field] = output[field].astype(object) if field == "explain_available" else output[field]
    return result


__all__ = [
    "EXPLAIN_SELECTION_FIELDS",
    "build_explainable_selection",
]
