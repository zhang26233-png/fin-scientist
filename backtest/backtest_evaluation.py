"""Read-only backtest evaluation built on return analysis fields."""

from __future__ import annotations

import copy

import pandas as pd


BACKTEST_EVALUATION_FIELDS = [
    "backtest_evaluation_available",
    "backtest_evaluation_status",
    "risk_score",
    "risk_level",
    "return_risk_ratio",
    "drawdown_risk_level",
    "volatility_risk_level",
    "performance_label",
    "performance_summary",
    "backtest_quality_label",
    "backtest_evaluation_warnings",
]

STATUS_AVAILABLE = "Available"
STATUS_INCOMPLETE = "Incomplete"
LEVEL_HIGH = "High"
LEVEL_MEDIUM = "Medium"
LEVEL_LOW = "Low"
LEVEL_UNAVAILABLE = "Unavailable"


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
    for field in BACKTEST_EVALUATION_FIELDS:
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


def _safe_number(row, field, warnings):
    if field not in row.index:
        warnings.append(f"{field} column missing.")
        return None
    value = pd.to_numeric(pd.Series([row[field]]), errors="coerce").iloc[0]
    if pd.isna(value):
        warnings.append(f"{field} value missing or invalid.")
        return None
    return float(value)


def _incomplete(warnings, quality_label=LEVEL_UNAVAILABLE):
    return {
        "backtest_evaluation_available": False,
        "backtest_evaluation_status": STATUS_INCOMPLETE,
        "risk_score": None,
        "risk_level": LEVEL_UNAVAILABLE,
        "return_risk_ratio": None,
        "drawdown_risk_level": LEVEL_UNAVAILABLE,
        "volatility_risk_level": LEVEL_UNAVAILABLE,
        "performance_label": LEVEL_UNAVAILABLE,
        "performance_summary": "Backtest evaluation is incomplete because required return-analysis fields are unavailable.",
        "backtest_quality_label": quality_label,
        "backtest_evaluation_warnings": warnings,
    }


def _drawdown_level(max_drawdown):
    drawdown_abs = abs(max_drawdown)
    if drawdown_abs >= 0.25:
        return LEVEL_HIGH
    if drawdown_abs >= 0.10:
        return LEVEL_MEDIUM
    return LEVEL_LOW


def _volatility_level(volatility):
    if volatility >= 0.40:
        return LEVEL_HIGH
    if volatility >= 0.20:
        return LEVEL_MEDIUM
    return LEVEL_LOW


def _risk_score(period_return, max_drawdown, volatility):
    drawdown_component = min(abs(max_drawdown) * 120, 60)
    volatility_component = min(volatility * 80, 35)
    negative_return_component = 15 if period_return < 0 else 0
    return round(min(100, drawdown_component + volatility_component + negative_return_component), 2)


def _risk_level(risk_score):
    if risk_score >= 60:
        return LEVEL_HIGH
    if risk_score >= 30:
        return LEVEL_MEDIUM
    return LEVEL_LOW


def _performance_label(period_return, max_drawdown, volatility):
    if period_return < 0:
        return "Weak"
    if abs(period_return) <= 0.02:
        return "Normal"
    if abs(max_drawdown) <= 0.15 and volatility <= 0.35:
        return "Strong"
    return "Normal"


def _quality_label(period_return, max_drawdown, volatility, warnings):
    valid_count = sum(value is not None for value in [period_return, max_drawdown, volatility])
    if valid_count == 3:
        return "Good" if not warnings else "Watch"
    if valid_count >= 2:
        return "Watch"
    return "Poor"


def _evaluate_row(row):
    warnings = []
    if "return_analysis_available" not in row.index:
        warnings.append("return_analysis_available column missing.")
        return _incomplete(warnings)
    if not _as_bool(row["return_analysis_available"]):
        warnings.append("Return analysis is unavailable.")
        return _incomplete(warnings)

    period_return = _safe_number(row, "period_return", warnings)
    max_drawdown = _safe_number(row, "max_drawdown", warnings)
    volatility = _safe_number(row, "volatility", warnings)
    quality_label = _quality_label(period_return, max_drawdown, volatility, warnings)

    if period_return is None or max_drawdown is None or volatility is None:
        return _incomplete(warnings, quality_label=quality_label)

    return_risk_ratio = None
    if max_drawdown == 0:
        warnings.append("max_drawdown is zero; return_risk_ratio is unavailable.")
    else:
        return_risk_ratio = float(period_return / abs(max_drawdown))

    if period_return < 0:
        warnings.append("period_return is negative; review downside and data-quality context.")

    risk_score = _risk_score(period_return, max_drawdown, volatility)
    performance_label = _performance_label(period_return, max_drawdown, volatility)
    performance_summary = (
        f"Backtest evaluation uses historical return {period_return:.4f}, "
        f"volatility {volatility:.4f}, and max drawdown {max_drawdown:.4f} "
        "for read-only research review."
    )

    return {
        "backtest_evaluation_available": True,
        "backtest_evaluation_status": STATUS_AVAILABLE,
        "risk_score": risk_score,
        "risk_level": _risk_level(risk_score),
        "return_risk_ratio": return_risk_ratio,
        "drawdown_risk_level": _drawdown_level(max_drawdown),
        "volatility_risk_level": _volatility_level(volatility),
        "performance_label": performance_label,
        "performance_summary": performance_summary,
        "backtest_quality_label": _quality_label(period_return, max_drawdown, volatility, warnings),
        "backtest_evaluation_warnings": warnings,
    }


def build_backtest_evaluation(return_analysis_df):
    """Append read-only backtest evaluation fields to return-analysis rows."""
    source = _safe_copy_frame(return_analysis_df)
    if source.empty:
        return _empty_like(source)

    result = source.copy(deep=True)
    output_rows = [_evaluate_row(result.loc[index]) for index in result.index]
    output = pd.DataFrame(output_rows, index=result.index)
    for field in BACKTEST_EVALUATION_FIELDS:
        result[field] = output[field].astype(object) if field == "backtest_evaluation_available" else output[field]
    return result


__all__ = [
    "BACKTEST_EVALUATION_FIELDS",
    "build_backtest_evaluation",
]
