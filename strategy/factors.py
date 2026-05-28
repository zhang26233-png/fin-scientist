"""Low-risk factor helpers for research-priority quantification."""

import math

import pandas as pd

INSUFFICIENT = "数据不足"


def to_number(value):
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").replace("%", "").strip()
    try:
        return float(text)
    except ValueError:
        return math.nan


def _empty_result(name, reason=INSUFFICIENT):
    return {
        "factor": name,
        "score": "无法计算",
        "label": reason,
        "details": {},
    }


def _get_numeric_series(price_df, column):
    if not isinstance(price_df, pd.DataFrame) or column not in price_df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(price_df[column], errors="coerce").dropna()


def calculate_trend_factor(price_df, price_col="Close", short_window=20, long_window=60):
    close = _get_numeric_series(price_df, price_col)
    if len(close) < short_window:
        return _empty_result("trend", "收盘价数据不足，无法计算趋势因子。")

    latest = close.iloc[-1]
    short_ma = close.tail(short_window).mean()
    long_ma = close.tail(long_window).mean() if len(close) >= long_window else math.nan

    score = 0
    if latest > short_ma:
        score += 40
    if not pd.isna(long_ma) and latest > long_ma:
        score += 30
    if not pd.isna(long_ma) and short_ma > long_ma:
        score += 30

    return {
        "factor": "trend",
        "score": int(score),
        "label": "趋势结构观察",
        "details": {
            "latest": float(latest),
            "short_ma": float(short_ma),
            "long_ma": None if pd.isna(long_ma) else float(long_ma),
        },
    }


def calculate_momentum_factor(price_df, price_col="Close", window=20):
    close = _get_numeric_series(price_df, price_col)
    if len(close) <= window:
        return _empty_result("momentum", "收盘价数据不足，无法计算动量因子。")

    start = close.iloc[-window - 1]
    end = close.iloc[-1]
    if start == 0:
        return _empty_result("momentum", "起始价格为 0，无法计算动量因子。")

    period_return = end / start - 1
    if period_return > 0.20:
        score = 80
    elif period_return > 0.10:
        score = 65
    elif period_return > 0:
        score = 50
    else:
        score = 30

    return {
        "factor": "momentum",
        "score": score,
        "label": "阶段表现观察",
        "details": {"window": window, "return": float(period_return)},
    }


def calculate_volatility_factor(price_df, price_col="Close", window=60):
    close = _get_numeric_series(price_df, price_col)
    if len(close) < 3:
        return _empty_result("volatility", "收盘价数据不足，无法计算波动因子。")

    returns = close.pct_change().dropna()
    if returns.empty:
        return _empty_result("volatility", "收益率序列为空，无法计算波动因子。")

    recent_returns = returns.tail(window)
    annual_volatility = recent_returns.std() * math.sqrt(252)
    if pd.isna(annual_volatility):
        return _empty_result("volatility", "波动率结果为空，无法计算波动因子。")

    if annual_volatility < 0.30:
        score = 80
    elif annual_volatility < 0.60:
        score = 60
    elif annual_volatility < 0.90:
        score = 40
    else:
        score = 20

    return {
        "factor": "volatility",
        "score": score,
        "label": "波动约束观察",
        "details": {"annual_volatility": float(annual_volatility)},
    }


def calculate_volume_factor(price_df, volume_col="Volume", short_window=5, long_window=20):
    volume = _get_numeric_series(price_df, volume_col)
    if len(volume) < long_window:
        return _empty_result("volume", "成交量数据不足，无法计算量能因子。")

    short_average = volume.tail(short_window).mean()
    long_average = volume.tail(long_window).mean()
    if long_average <= 0:
        return _empty_result("volume", "长期平均成交量无效，无法计算量能因子。")

    ratio = short_average / long_average
    if ratio > 1.8:
        score = 80
    elif ratio > 1.3:
        score = 65
    elif ratio > 0.8:
        score = 50
    else:
        score = 30

    return {
        "factor": "volume",
        "score": score,
        "label": "量能变化观察",
        "details": {"volume_ratio": float(ratio)},
    }


def build_factor_snapshot(price_df):
    return {
        "trend": calculate_trend_factor(price_df),
        "momentum": calculate_momentum_factor(price_df),
        "volatility": calculate_volatility_factor(price_df),
        "volume": calculate_volume_factor(price_df),
    }


__all__ = [
    "build_factor_snapshot",
    "calculate_momentum_factor",
    "calculate_trend_factor",
    "calculate_volatility_factor",
    "calculate_volume_factor",
]
