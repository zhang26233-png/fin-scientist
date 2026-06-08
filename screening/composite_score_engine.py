"""Read-only composite quant score engine for screening outputs."""

from __future__ import annotations

import copy
import math

import pandas as pd


COMPOSITE_QUANT_SCORE_FIELDS = [
    "composite_available",
    "composite_score",
    "composite_level",
    "composite_screening_status",
    "composite_reasons",
    "composite_warnings",
    "score_breakdown",
]

STATUS_INCOMPLETE = "Incomplete"
STATUS_PASS = "Pass"
STATUS_WATCH = "Watch"
STATUS_EXCLUDE = "Exclude"

LEVEL_HIGH = "High"
LEVEL_MEDIUM = "Medium"
LEVEL_LOW = "Low"
LEVEL_UNAVAILABLE = "Unavailable"

FUNDAMENTAL_WEIGHT = 0.5
TECHNICAL_WEIGHT = 0.5


def _safe_copy_frame(source):
    if source is None:
        return None
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    return pd.DataFrame()


def _empty_like(universe):
    base = universe.copy(deep=True) if isinstance(universe, pd.DataFrame) else pd.DataFrame()
    for field in COMPOSITE_QUANT_SCORE_FIELDS:
        base[field] = pd.Series(dtype="object")
    return base


def _normalize_ticker(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else text


def _row_key_series(frame):
    if "ticker" in frame.columns:
        return frame["ticker"].map(_normalize_ticker)
    if "symbol" in frame.columns:
        return frame["symbol"].map(_normalize_ticker)
    return pd.Series([None] * len(frame), index=frame.index)


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


def _score_map(frame, score_field):
    if frame is None or frame.empty:
        return {}
    keys = _row_key_series(frame)
    rows = {}
    for index, row in frame.iterrows():
        key = keys.loc[index]
        if key and key not in rows:
            rows[key] = row.to_dict()
    return rows


def _attach_non_conflicting_columns(result, source):
    if source is None or source.empty:
        return result
    keys = _row_key_series(result)
    source_keys = _row_key_series(source)
    source_by_ticker = {}
    for index, row in source.iterrows():
        key = source_keys.loc[index]
        if key and key not in source_by_ticker:
            source_by_ticker[key] = row.to_dict()

    for column in source.columns:
        if column in result.columns or column in {"ticker", "symbol"}:
            continue
        result[column] = [source_by_ticker.get(keys.loc[index], {}).get(column) for index in result.index]
    return result


def _level_and_status(score):
    if score >= 80:
        return LEVEL_HIGH, STATUS_PASS
    if score >= 60:
        return LEVEL_MEDIUM, STATUS_WATCH
    if score >= 40:
        return LEVEL_LOW, STATUS_WATCH
    return LEVEL_LOW, STATUS_EXCLUDE


def _breakdown(fundamental_score, technical_score, composite_score):
    if fundamental_score is None or technical_score is None or composite_score is None:
        return "Fundamental: unavailable; Technical: unavailable; Composite: unavailable"
    return (
        f"Fundamental: {fundamental_score:g}; "
        f"Technical: {technical_score:g}; "
        f"Composite: {composite_score:g}"
    )


def _build_row(fundamental_row, technical_row):
    warnings = []
    reasons = []
    fundamental_score = _to_score(fundamental_row.get("fundamental_score")) if fundamental_row else None
    technical_score = _to_score(technical_row.get("technical_score")) if technical_row else None

    if not fundamental_row:
        warnings.append("Fundamental screening row missing.")
    elif fundamental_score is None:
        warnings.append("fundamental_score missing or invalid.")
    if not technical_row:
        warnings.append("Technical screening row missing.")
    elif technical_score is None:
        warnings.append("technical_score missing or invalid.")

    if fundamental_score is None or technical_score is None:
        return {
            "composite_available": False,
            "composite_score": 0,
            "composite_level": LEVEL_UNAVAILABLE,
            "composite_screening_status": STATUS_INCOMPLETE,
            "composite_reasons": [],
            "composite_warnings": warnings or ["Composite inputs unavailable."],
            "score_breakdown": _breakdown(None, None, None),
        }

    composite_score = int(round((fundamental_score * FUNDAMENTAL_WEIGHT) + (technical_score * TECHNICAL_WEIGHT)))
    composite_score = max(0, min(100, composite_score))
    level, status = _level_and_status(composite_score)
    reasons.append("Composite score uses 50% fundamental score and 50% technical score.")
    reasons.append(f"Composite level is {level}.")

    return {
        "composite_available": True,
        "composite_score": composite_score,
        "composite_level": level,
        "composite_screening_status": status,
        "composite_reasons": reasons,
        "composite_warnings": warnings,
        "score_breakdown": _breakdown(fundamental_score, technical_score, composite_score),
    }


def build_composite_quant_score(universe_df, fundamental_screening_df=None, technical_screening_df=None):
    """Append read-only composite quant score fields to Universe rows."""
    universe = _safe_copy_frame(universe_df)
    if universe is None:
        universe = pd.DataFrame()
    if universe.empty:
        return _empty_like(universe)

    result = universe.copy(deep=True)
    fundamental = _safe_copy_frame(fundamental_screening_df)
    technical = _safe_copy_frame(technical_screening_df)

    result = _attach_non_conflicting_columns(result, fundamental)
    result = _attach_non_conflicting_columns(result, technical)

    universe_keys = _row_key_series(result)
    fundamental_by_ticker = _score_map(fundamental, "fundamental_score")
    technical_by_ticker = _score_map(technical, "technical_score")

    output_rows = []
    for index in result.index:
        key = universe_keys.loc[index]
        output_rows.append(_build_row(fundamental_by_ticker.get(key), technical_by_ticker.get(key)))

    output = pd.DataFrame(output_rows, index=result.index)
    for field in COMPOSITE_QUANT_SCORE_FIELDS:
        result[field] = output[field].astype(object) if field == "composite_available" else output[field]
    return result


__all__ = [
    "COMPOSITE_QUANT_SCORE_FIELDS",
    "FUNDAMENTAL_WEIGHT",
    "TECHNICAL_WEIGHT",
    "build_composite_quant_score",
]
