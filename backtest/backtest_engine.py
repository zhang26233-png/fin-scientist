"""Read-only backtest dataset foundation for candidate pools."""

from __future__ import annotations

import copy

import pandas as pd


BACKTEST_FOUNDATION_FIELDS = [
    "backtest_available",
    "backtest_status",
    "backtest_start_date",
    "backtest_end_date",
    "backtest_days",
    "backtest_price_available",
    "backtest_warnings",
]

STATUS_AVAILABLE = "Available"
STATUS_INCOMPLETE = "Incomplete"
MIN_BACKTEST_DAYS = 60


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
    for field in BACKTEST_FOUNDATION_FIELDS:
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


def _analyze_history(history):
    warnings = []
    if history is None or history.empty:
        return {
            "backtest_available": False,
            "backtest_status": STATUS_INCOMPLETE,
            "backtest_start_date": None,
            "backtest_end_date": None,
            "backtest_days": 0,
            "backtest_price_available": False,
            "backtest_warnings": ["Price history missing."],
        }

    if "date" not in history.columns:
        warnings.append("date column missing.")
    if "close" not in history.columns:
        warnings.append("close column missing.")

    dates = pd.to_datetime(history["date"], errors="coerce") if "date" in history.columns else pd.Series(dtype="datetime64[ns]")
    closes = pd.to_numeric(history["close"], errors="coerce") if "close" in history.columns else pd.Series(dtype="float64")
    valid_mask = dates.notna() & closes.notna()
    valid = history.loc[valid_mask].copy()

    if valid.empty:
        warnings.append("No valid date and close rows.")
        return {
            "backtest_available": False,
            "backtest_status": STATUS_INCOMPLETE,
            "backtest_start_date": None,
            "backtest_end_date": None,
            "backtest_days": 0,
            "backtest_price_available": False,
            "backtest_warnings": warnings,
        }

    valid_dates = dates.loc[valid.index].sort_values()
    backtest_days = int(len(valid_dates))
    if backtest_days < MIN_BACKTEST_DAYS:
        warnings.append("Price history has fewer than 60 valid rows.")

    return {
        "backtest_available": True,
        "backtest_status": STATUS_AVAILABLE if backtest_days >= MIN_BACKTEST_DAYS else STATUS_INCOMPLETE,
        "backtest_start_date": valid_dates.iloc[0].date().isoformat(),
        "backtest_end_date": valid_dates.iloc[-1].date().isoformat(),
        "backtest_days": backtest_days,
        "backtest_price_available": True,
        "backtest_warnings": warnings,
    }


def build_backtest_dataset(candidate_pool_df, price_history_dict=None):
    """Append backtest dataset availability fields to a candidate-pool frame.

    This foundation layer only validates price-history availability and date
    coverage. It intentionally does not calculate returns or performance.
    """
    source = _safe_copy_frame(candidate_pool_df)
    if source.empty:
        return _empty_like(source)

    result = source.copy(deep=True)
    histories = _copy_price_history_dict(price_history_dict)
    keys = _row_key_series(result)

    output_rows = []
    for index in result.index:
        key = keys.loc[index]
        if not key:
            output_rows.append(
                {
                    "backtest_available": False,
                    "backtest_status": STATUS_INCOMPLETE,
                    "backtest_start_date": None,
                    "backtest_end_date": None,
                    "backtest_days": 0,
                    "backtest_price_available": False,
                    "backtest_warnings": ["ticker missing."],
                }
            )
            continue
        output_rows.append(_analyze_history(histories.get(key)))

    output = pd.DataFrame(output_rows, index=result.index)
    for field in BACKTEST_FOUNDATION_FIELDS:
        result[field] = output[field].astype(object) if field in {"backtest_available", "backtest_price_available"} else output[field]
    return result


__all__ = [
    "BACKTEST_FOUNDATION_FIELDS",
    "MIN_BACKTEST_DAYS",
    "build_backtest_dataset",
]
