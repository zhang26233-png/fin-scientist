"""Pure screening filters for research-candidate preprocessing."""

import math

import pandas as pd


def _safe_latest(series):
    if not isinstance(series, pd.Series):
        return math.nan
    values = pd.to_numeric(series, errors="coerce").dropna()
    return math.nan if values.empty else float(values.iloc[-1])


def check_required_columns(price_df, required_columns=("Close",)):
    missing = []
    if not isinstance(price_df, pd.DataFrame):
        missing = list(required_columns)
    else:
        missing = [column for column in required_columns if column not in price_df.columns]
    return {
        "passed": not missing,
        "filter": "required_columns",
        "reason": "" if not missing else "缺少必要字段：" + "、".join(missing),
    }


def check_min_rows(price_df, min_rows=20):
    row_count = len(price_df) if isinstance(price_df, pd.DataFrame) else 0
    return {
        "passed": row_count >= min_rows,
        "filter": "min_rows",
        "reason": "" if row_count >= min_rows else f"有效行数不足 {min_rows} 行。",
    }


def check_min_price(price_df, min_price=1.0, price_col="Close"):
    if not isinstance(price_df, pd.DataFrame) or price_col not in price_df.columns:
        return {"passed": False, "filter": "min_price", "reason": "价格字段缺失。"}
    latest_price = _safe_latest(price_df[price_col])
    passed = not math.isnan(latest_price) and latest_price >= min_price
    return {
        "passed": passed,
        "filter": "min_price",
        "reason": "" if passed else f"最新价格低于最小观察阈值 {min_price}。",
    }


def check_min_turnover(price_df, min_average_turnover=None, price_col="Close", volume_col="Volume", window=20):
    if min_average_turnover is None:
        return {"passed": True, "filter": "min_turnover", "reason": ""}
    if not isinstance(price_df, pd.DataFrame) or price_col not in price_df.columns or volume_col not in price_df.columns:
        return {"passed": False, "filter": "min_turnover", "reason": "价格或成交量字段缺失。"}

    price = pd.to_numeric(price_df[price_col], errors="coerce")
    volume = pd.to_numeric(price_df[volume_col], errors="coerce")
    turnover = (price * volume).dropna().tail(window)
    average_turnover = math.nan if turnover.empty else float(turnover.mean())
    passed = not math.isnan(average_turnover) and average_turnover >= min_average_turnover
    return {
        "passed": passed,
        "filter": "min_turnover",
        "reason": "" if passed else f"平均成交额低于最小观察阈值 {min_average_turnover}。",
    }


def check_extreme_return(price_df, max_abs_return=0.30, price_col="Close", window=1):
    if not isinstance(price_df, pd.DataFrame) or price_col not in price_df.columns:
        return {"passed": False, "filter": "extreme_return", "reason": "价格字段缺失。"}
    close = pd.to_numeric(price_df[price_col], errors="coerce").dropna()
    if len(close) <= window:
        return {"passed": False, "filter": "extreme_return", "reason": "价格数据不足。"}

    start = close.iloc[-window - 1]
    end = close.iloc[-1]
    if start == 0:
        return {"passed": False, "filter": "extreme_return", "reason": "起始价格为 0。"}
    period_return = end / start - 1
    passed = bool(abs(period_return) <= max_abs_return)
    return {
        "passed": passed,
        "filter": "extreme_return",
        "reason": "" if passed else f"阶段涨跌幅超过异常波动阈值 {max_abs_return:.0%}。",
    }


def apply_basic_filters(price_df, min_rows=20, min_price=1.0):
    checks = [
        check_required_columns(price_df, required_columns=("Close",)),
        check_min_rows(price_df, min_rows=min_rows),
        check_min_price(price_df, min_price=min_price),
        check_extreme_return(price_df),
    ]
    return {
        "passed": all(item["passed"] for item in checks),
        "checks": checks,
    }


__all__ = [
    "apply_basic_filters",
    "check_extreme_return",
    "check_min_price",
    "check_min_rows",
    "check_min_turnover",
    "check_required_columns",
]
