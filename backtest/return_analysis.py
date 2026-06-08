"""Read-only return analysis built on validated backtest foundation data."""

from __future__ import annotations

import copy
import math

import pandas as pd


RETURN_ANALYSIS_FIELDS = [
    "return_analysis_available",
    "return_analysis_status",
    "holding_period_days",
    "entry_price",
    "exit_price",
    "period_return",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "win_rate",
    "return_analysis_summary",
    "return_analysis_warnings",
]

STATUS_AVAILABLE = "Available"
STATUS_INCOMPLETE = "Incomplete"
MIN_RETURN_ANALYSIS_DAYS = 60


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
    for field in RETURN_ANALYSIS_FIELDS:
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


def _copy_price_history_dict(price_history_dict):
    if not isinstance(price_history_dict, dict):
        return {}
    copied = {}
    for ticker, history in price_history_dict.items():
        key = _normalize_ticker(ticker)
        if key:
            copied[key] = _safe_copy_frame(history)
    return copied


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if value is None or pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def _incomplete(warnings):
    return {
        "return_analysis_available": False,
        "return_analysis_status": STATUS_INCOMPLETE,
        "holding_period_days": 0,
        "entry_price": None,
        "exit_price": None,
        "period_return": None,
        "annualized_return": None,
        "volatility": None,
        "max_drawdown": None,
        "win_rate": None,
        "return_analysis_summary": "Return analysis is incomplete because required price-history inputs are unavailable.",
        "return_analysis_warnings": warnings,
    }


def _prepare_history(history):
    warnings = []
    if history is None or history.empty:
        warnings.append("Price history missing.")
        return pd.DataFrame(), warnings

    if "date" not in history.columns:
        warnings.append("date column missing.")
    if "close" not in history.columns:
        warnings.append("close column missing.")

    dates = pd.to_datetime(history["date"], errors="coerce") if "date" in history.columns else pd.Series(dtype="datetime64[ns]")
    closes = pd.to_numeric(history["close"], errors="coerce") if "close" in history.columns else pd.Series(dtype="float64")
    valid_mask = dates.notna() & closes.notna()
    valid = pd.DataFrame({"date": dates.loc[valid_mask], "close": closes.loc[valid_mask]})
    if valid.empty:
        warnings.append("No valid date and close rows.")
        return valid, warnings

    valid = valid[valid["close"] > 0].sort_values("date").reset_index(drop=True)
    if valid.empty:
        warnings.append("No positive close prices available.")
        return valid, warnings
    if len(valid) < MIN_RETURN_ANALYSIS_DAYS:
        warnings.append("Price history has fewer than 60 valid rows.")
    return valid, warnings


def _analyze_history(history):
    valid, warnings = _prepare_history(history)
    if len(valid) < MIN_RETURN_ANALYSIS_DAYS:
        return _incomplete(warnings)

    closes = valid["close"].astype(float)
    entry_price = float(closes.iloc[0])
    exit_price = float(closes.iloc[-1])
    holding_period_days = int(len(valid))
    period_return = exit_price / entry_price - 1
    daily_return = closes.pct_change().dropna()

    if daily_return.empty:
        warnings.append("Daily return series unavailable.")
        return _incomplete(warnings)

    annualized_return = (1 + period_return) ** (252 / holding_period_days) - 1
    volatility = float(daily_return.std() * math.sqrt(252))
    drawdown = closes / closes.cummax() - 1
    max_drawdown = float(drawdown.min())
    win_rate = float((daily_return > 0).mean())
    start_date = valid["date"].iloc[0].date().isoformat()
    end_date = valid["date"].iloc[-1].date().isoformat()

    return {
        "return_analysis_available": True,
        "return_analysis_status": STATUS_AVAILABLE,
        "holding_period_days": holding_period_days,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "period_return": float(period_return),
        "annualized_return": float(annualized_return),
        "volatility": volatility,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "return_analysis_summary": (
            f"Return analysis available for {holding_period_days} valid rows "
            f"from {start_date} to {end_date}."
        ),
        "return_analysis_warnings": warnings,
    }


def build_return_analysis(backtest_df, price_history_dict=None):
    """Append read-only return-analysis fields to a backtest foundation frame."""
    source = _safe_copy_frame(backtest_df)
    if source.empty:
        return _empty_like(source)

    result = source.copy(deep=True)
    histories = _copy_price_history_dict(price_history_dict)
    keys = _row_key_series(result)
    has_backtest_available = "backtest_available" in result.columns

    output_rows = []
    for index in result.index:
        warnings = []
        if not has_backtest_available:
            warnings.append("backtest_available column missing.")
            output_rows.append(_incomplete(warnings))
            continue
        if not _as_bool(result.at[index, "backtest_available"]):
            warnings.append("Backtest foundation is unavailable.")
            output_rows.append(_incomplete(warnings))
            continue

        key = keys.loc[index]
        if not key:
            warnings.append("ticker missing.")
            output_rows.append(_incomplete(warnings))
            continue

        analysis = _analyze_history(histories.get(key))
        if warnings:
            analysis["return_analysis_warnings"] = warnings + analysis["return_analysis_warnings"]
        output_rows.append(analysis)

    output = pd.DataFrame(output_rows, index=result.index)
    for field in RETURN_ANALYSIS_FIELDS:
        result[field] = output[field].astype(object) if field == "return_analysis_available" else output[field]
    return result


__all__ = [
    "MIN_RETURN_ANALYSIS_DAYS",
    "RETURN_ANALYSIS_FIELDS",
    "build_return_analysis",
]
