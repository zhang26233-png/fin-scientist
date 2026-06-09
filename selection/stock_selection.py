"""Read-only stock selection research layer."""

from __future__ import annotations

import copy

import pandas as pd


STOCK_SELECTION_FIELDS = [
    "selection_available",
    "selection_score",
    "selection_level",
    "selection_status",
    "selection_bucket",
    "selection_rank",
    "selection_reasons",
    "selection_risk_notes",
    "selection_quality_label",
    "selection_warnings",
]

LEVEL_HIGH = "High"
LEVEL_MEDIUM = "Medium"
LEVEL_LOW = "Low"
LEVEL_UNAVAILABLE = "Unavailable"
STATUS_SELECTED = "Selected"
STATUS_WATCH = "Watch"
STATUS_EXCLUDED = "Excluded"
STATUS_INCOMPLETE = "Incomplete"
BUCKET_CORE = "Core"
BUCKET_WATCH = "Watch"
BUCKET_EXCLUDE = "Exclude"
BUCKET_UNAVAILABLE = "Unavailable"


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
    for field in STOCK_SELECTION_FIELDS:
        base[field] = pd.Series(dtype="object")
    return base


def _safe_number(row, field, warnings):
    if field not in row.index:
        warnings.append(f"{field} column missing.")
        return None
    value = pd.to_numeric(pd.Series([row[field]]), errors="coerce").iloc[0]
    if pd.isna(value):
        warnings.append(f"{field} value missing or invalid.")
        return None
    return float(value)


def _safe_text(row, field, warnings, default=LEVEL_UNAVAILABLE):
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


def _candidate_pool_points(candidate_pool, reasons, risk_notes):
    if candidate_pool == BUCKET_CORE:
        reasons.append("Candidate Pool is Core, adding research-priority support.")
        return 20
    if candidate_pool == BUCKET_WATCH:
        reasons.append("Candidate Pool is Watch, keeping the row in follow-up research scope.")
        return 15
    if candidate_pool == BUCKET_EXCLUDE:
        risk_notes.append("Candidate Pool is Exclude, reducing stock-selection layer.")
        return -20
    risk_notes.append("Candidate Pool is unavailable or unrecognized.")
    return 0


def _performance_points(performance_label, reasons, risk_notes):
    if performance_label == "Strong":
        reasons.append("Backtest performance label is Strong, adding historical evaluation support.")
        return 20
    if performance_label == "Normal":
        reasons.append("Backtest performance label is Normal, adding neutral historical context.")
        return 15
    if performance_label == "Weak":
        risk_notes.append("Backtest performance label is Weak, reducing stock-selection layer.")
        return -10
    risk_notes.append("Backtest performance label is unavailable or unrecognized.")
    return 0


def _risk_penalty(risk_level, risk_notes):
    if risk_level == LEVEL_HIGH:
        risk_notes.append("Risk level is High, applying the maximum risk penalty.")
        return 10
    if risk_level == LEVEL_MEDIUM:
        risk_notes.append("Risk level is Medium, applying a moderate risk penalty.")
        return 5
    if risk_level == LEVEL_LOW:
        risk_notes.append("Risk level is Low based on available backtest evaluation fields.")
        return 0
    risk_notes.append("Risk level is unavailable or unrecognized.")
    return 0


def _quality_adjustment(backtest_quality_label, risk_notes):
    if backtest_quality_label == "Good":
        return 0
    if backtest_quality_label == "Watch":
        risk_notes.append("Backtest quality label is Watch, reducing confidence in the selection layer.")
        return -5
    if backtest_quality_label == "Poor":
        risk_notes.append("Backtest quality label is Poor, applying a quality downgrade.")
        return -20
    risk_notes.append("Backtest quality label is unavailable or unrecognized.")
    return 0


def _layer_from_score(selection_score):
    if selection_score >= 80:
        return LEVEL_HIGH, STATUS_SELECTED, BUCKET_CORE
    if selection_score >= 60:
        return LEVEL_MEDIUM, STATUS_WATCH, BUCKET_WATCH
    if selection_score >= 40:
        return LEVEL_LOW, STATUS_WATCH, BUCKET_WATCH
    return LEVEL_LOW, STATUS_EXCLUDED, BUCKET_EXCLUDE


def _quality_label(selection_score, warnings, risk_notes):
    if warnings:
        return LEVEL_UNAVAILABLE
    if selection_score >= 80 and not any("High" in note or "Poor" in note for note in risk_notes):
        return "Strong"
    if selection_score >= 40:
        return "Normal"
    return "Weak"


def _incomplete(warnings):
    return {
        "selection_available": False,
        "selection_score": None,
        "selection_level": LEVEL_UNAVAILABLE,
        "selection_status": STATUS_INCOMPLETE,
        "selection_bucket": BUCKET_UNAVAILABLE,
        "selection_rank": None,
        "selection_reasons": [],
        "selection_risk_notes": [],
        "selection_quality_label": LEVEL_UNAVAILABLE,
        "selection_warnings": warnings,
    }


def _select_row(row):
    warnings = []
    reasons = []
    risk_notes = []

    composite_score = _safe_number(row, "composite_score", warnings)
    candidate_pool = _safe_text(row, "candidate_pool", warnings, default=BUCKET_UNAVAILABLE)
    performance_label = _safe_text(row, "performance_label", warnings, default=LEVEL_UNAVAILABLE)
    risk_level = _safe_text(row, "risk_level", warnings, default=LEVEL_UNAVAILABLE)
    backtest_quality_label = _safe_text(row, "backtest_quality_label", warnings, default=LEVEL_UNAVAILABLE)

    if composite_score is None:
        return _incomplete(warnings)

    clipped_composite = min(100, max(0, composite_score))
    score = clipped_composite * 0.50
    reasons.append(f"Composite score contributes {clipped_composite * 0.50:.2f} points under the 50% selection weight.")
    score += _candidate_pool_points(candidate_pool, reasons, risk_notes)
    score += _performance_points(performance_label, reasons, risk_notes)
    score -= _risk_penalty(risk_level, risk_notes)
    score += _quality_adjustment(backtest_quality_label, risk_notes)
    score = round(min(100, max(0, score)), 2)

    level, status, bucket = _layer_from_score(score)
    if candidate_pool == BUCKET_EXCLUDE:
        level, status, bucket = LEVEL_LOW, STATUS_EXCLUDED, BUCKET_EXCLUDE
    if backtest_quality_label == "Poor" and status == STATUS_SELECTED:
        level, status, bucket = LEVEL_MEDIUM, STATUS_WATCH, BUCKET_WATCH
    if risk_level == LEVEL_HIGH and status == STATUS_SELECTED:
        level, status, bucket = LEVEL_MEDIUM, STATUS_WATCH, BUCKET_WATCH

    return {
        "selection_available": True,
        "selection_score": score,
        "selection_level": level,
        "selection_status": status,
        "selection_bucket": bucket,
        "selection_rank": None,
        "selection_reasons": reasons,
        "selection_risk_notes": risk_notes,
        "selection_quality_label": _quality_label(score, warnings, risk_notes),
        "selection_warnings": warnings,
    }


def _assign_selection_rank(result):
    if "selection_score" not in result.columns:
        return result
    available = result[result["selection_available"].map(bool)]
    if available.empty:
        return result

    sorted_index = available.sort_values(
        by=["selection_score"],
        ascending=False,
        kind="mergesort",
    ).index
    ranks = {index: rank for rank, index in enumerate(sorted_index, start=1)}
    result["selection_rank"] = [ranks.get(index) for index in result.index]
    return result


def build_stock_selection(selection_input_df):
    """Append read-only stock-selection research fields without changing row order."""
    source = _safe_copy_frame(selection_input_df)
    if source.empty:
        return _empty_like(source)

    result = source.copy(deep=True)
    output_rows = [_select_row(result.loc[index]) for index in result.index]
    output = pd.DataFrame(output_rows, index=result.index)
    for field in STOCK_SELECTION_FIELDS:
        result[field] = output[field].astype(object) if field == "selection_available" else output[field]
    return _assign_selection_rank(result)


__all__ = [
    "STOCK_SELECTION_FIELDS",
    "build_stock_selection",
]
