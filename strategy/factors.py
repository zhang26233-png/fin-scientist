"""Low-risk factor helpers for research-priority quantification."""

import math

import pandas as pd

AMOUNT_COLUMNS = ("amount", "turnover_amount", "成交额")
TURNOVER_COLUMNS = ("turnover", "turnover_rate", "换手率")
VOLUME_RATIO_COLUMNS = ("volume_ratio", "量比", "成交量放大倍数")
RETURN_COLUMNS = ("return_20d", "recent_return", "pct_chg")

INSUFFICIENT = "数据不足"


def to_number(value):
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else math.nan
    text = str(value).replace(",", "").replace("%", "").strip()
    try:
        number = float(text)
    except ValueError:
        return math.nan
    return number if math.isfinite(number) else math.nan


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
    series = pd.to_numeric(price_df[column], errors="coerce")
    return series[series.map(math.isfinite)].dropna()


def _latest_number(price_df, column):
    series = _get_numeric_series(price_df, column)
    return math.nan if series.empty else float(series.iloc[-1])


def _latest_from_any(price_df, columns):
    if not isinstance(price_df, pd.DataFrame):
        return math.nan
    lowered = {str(column).lower(): column for column in price_df.columns}
    for column in columns:
        if column in price_df.columns:
            return _latest_number(price_df, column)
        matched = lowered.get(str(column).lower())
        if matched is not None:
            return _latest_number(price_df, matched)
    return math.nan


def _derive_period_return(price_df, close, window):
    explicit_return = _latest_from_any(price_df, RETURN_COLUMNS)
    if not pd.isna(explicit_return):
        return explicit_return
    if len(close) <= window:
        return math.nan
    start = close.iloc[-window - 1]
    end = close.iloc[-1]
    if start == 0:
        return math.nan
    return end / start - 1


def _derive_volume_ratio(price_df, volume, window):
    explicit_ratio = _latest_from_any(price_df, VOLUME_RATIO_COLUMNS)
    if not pd.isna(explicit_ratio):
        return explicit_ratio
    if len(volume) < window:
        return math.nan
    short_volume = volume.tail(min(5, len(volume))).mean()
    long_volume = volume.tail(window).mean()
    if long_volume <= 0:
        return math.nan
    return short_volume / long_volume


def _volume_price_profile(period_return, volume_ratio, amount, turnover):
    score = 50
    labels = []

    if not pd.isna(amount):
        if amount < 5_000_000:
            labels.append("low_liquidity")
            score = min(score, 25)
        elif amount >= 50_000_000:
            score += 10

    if not pd.isna(volume_ratio):
        if volume_ratio > 1.3 and not pd.isna(period_return) and period_return > 0:
            labels.append("volume_price_confirmed")
            score += 15
        elif volume_ratio < 0.8 and not pd.isna(period_return) and period_return > 0:
            labels.append("volume_price_weak")
            score -= 15
        elif volume_ratio > 1.3 and not pd.isna(period_return) and period_return < 0:
            labels.append("volume_downside_risk")
            score -= 20

    if not pd.isna(turnover):
        if turnover < 0.003:
            labels.append("low_liquidity")
            score = min(score, 30)
        elif turnover > 0.15:
            labels.append("overheated_turnover")
            score = min(score, 55)
        elif 0.005 <= turnover <= 0.08 and "volume_price_confirmed" in labels:
            score += 5

    if not labels:
        labels.append("volume_price_neutral")
    return max(0, min(100, int(round(score)))), labels


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

    period_return = latest / close.iloc[-short_window] - 1 if close.iloc[-short_window] else math.nan
    if pd.isna(period_return):
        trend_direction_label = "方向暂缺"
        trend_quality_label = "趋势质量待核验"
    elif period_return > 0.30:
        trend_direction_label = "短期趋势向上"
        trend_quality_label = "拉升较快，需核验过热风险"
    elif period_return > 0.05:
        trend_direction_label = "短期趋势向上"
        trend_quality_label = "趋势相对平稳"
    elif period_return >= -0.05:
        trend_direction_label = "短期趋势走平"
        trend_quality_label = "趋势方向不明显"
    else:
        trend_direction_label = "短期趋势向下"
        trend_quality_label = "趋势转弱"

    return {
        "factor": "trend",
        "score": int(score),
        "label": "趋势结构观察",
        "details": {
            "latest": float(latest),
            "short_ma": float(short_ma),
            "long_ma": None if pd.isna(long_ma) else float(long_ma),
            "trend_direction_label": trend_direction_label,
            "trend_quality_label": trend_quality_label,
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

    explicit_returns = [
        _latest_number(price_df, column)
        for column in ("pct_chg", "recent_return", "return_5d", "return_10d")
        if isinstance(price_df, pd.DataFrame) and column in price_df.columns
    ]
    explicit_returns = [value for value in explicit_returns if not pd.isna(value)]
    period_return = end / start - 1
    if explicit_returns:
        period_return = max(explicit_returns)

    recent_returns = close.pct_change().dropna().tail(min(5, len(close) - 1))
    consecutive_up_count = 0
    consecutive_down_count = 0
    for value in reversed(recent_returns.tolist()):
        if value > 0:
            consecutive_up_count += 1
            if consecutive_down_count:
                break
        elif value < 0:
            consecutive_down_count += 1
            if consecutive_up_count:
                break
        else:
            break

    if period_return > 0.20:
        score = 65 if period_return > 0.35 or consecutive_up_count >= 5 else 80
        momentum_label = "过热动量" if period_return > 0.35 or consecutive_up_count >= 5 else "强动量"
    elif period_return > 0.10:
        score = 65
        momentum_label = "温和动量"
    elif period_return > 0:
        score = 50
        momentum_label = "弱动量"
    else:
        score = 30
        momentum_label = "动量转弱"
    if consecutive_down_count >= 3:
        score = min(score, 25)
        momentum_label = "连续走弱"

    return {
        "factor": "momentum",
        "score": score,
        "label": "阶段表现观察",
        "details": {
            "window": window,
            "return": float(period_return),
            "momentum_label": momentum_label,
            "consecutive_up_count": consecutive_up_count,
            "consecutive_down_count": consecutive_down_count,
        },
    }


def calculate_moving_average_position_factor(price_df, price_col="Close", ma_columns=("MA5", "MA10", "MA20")):
    close = _get_numeric_series(price_df, price_col)
    if close.empty:
        return _empty_result("moving_average_position", "收盘价数据不足，无法计算均线位置因子。")

    latest = float(close.iloc[-1])
    available_ma = {}
    for column in ma_columns:
        value = _latest_number(price_df, column)
        if not pd.isna(value):
            available_ma[column] = value
    if not available_ma:
        return _empty_result("moving_average_position", "均线字段缺失，无法计算均线位置因子。")

    above_count = sum(1 for value in available_ma.values() if latest > value)
    below_count = sum(1 for value in available_ma.values() if latest < value)
    score = 50 + above_count * 15 - below_count * 15
    if below_count == len(available_ma):
        trend_direction_label = "短期趋势向下"
    elif above_count == len(available_ma):
        trend_direction_label = "短期趋势向上"
    else:
        trend_direction_label = "短期趋势走平"
    return {
        "factor": "moving_average_position",
        "score": max(0, min(100, int(score))),
        "label": "均线位置观察",
        "details": {
            "latest": latest,
            "available_ma": available_ma,
            "above_count": above_count,
            "below_count": below_count,
            "trend_direction_label": trend_direction_label,
        },
    }


def calculate_momentum_profile_factor(price_df, price_col="Close"):
    close = _get_numeric_series(price_df, price_col)
    if len(close) < 3:
        return _empty_result("momentum_profile", "收盘价数据不足，无法计算动量画像因子。")

    returns = {
        column: _latest_number(price_df, column)
        for column in ("pct_chg", "recent_return", "return_5d", "return_10d")
        if isinstance(price_df, pd.DataFrame) and column in price_df.columns
    }
    if not returns:
        for window in (5, 10):
            if len(close) > window and close.iloc[-window - 1] != 0:
                returns[f"return_{window}d"] = close.iloc[-1] / close.iloc[-window - 1] - 1
    if not returns:
        return _empty_result("momentum_profile", "动量字段缺失，无法计算动量画像因子。")

    latest_return = max(value for value in returns.values() if not pd.isna(value))
    recent_changes = close.pct_change().dropna().tail(min(5, len(close) - 1))
    up_days = int((recent_changes > 0).sum())
    down_days = int((recent_changes < 0).sum())
    if latest_return > 0.35:
        score = 55
        momentum_label = "过热动量"
    elif latest_return > 0.08:
        score = 70
        momentum_label = "温和动量"
    elif latest_return >= -0.03:
        score = 50
        momentum_label = "中性动量"
    else:
        score = 30
        momentum_label = "动量转弱"
    if down_days >= 4:
        score = min(score, 25)
        momentum_label = "连续走弱"
    return {
        "factor": "momentum_profile",
        "score": score,
        "label": "动量画像观察",
        "details": {
            "returns": returns,
            "up_days": up_days,
            "down_days": down_days,
            "momentum_label": momentum_label,
        },
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


def calculate_trend_direction_factor(price_df, price_col="Close", window=20):
    close = _get_numeric_series(price_df, price_col)
    if len(close) <= window:
        return _empty_result("trend_direction", "收盘价数据不足，无法计算趋势方向因子。")

    start = close.iloc[-window - 1]
    end = close.iloc[-1]
    if start == 0:
        return _empty_result("trend_direction", "起始价格为 0，无法计算趋势方向因子。")

    period_return = end / start - 1
    if period_return > 0.20:
        score = 70
        direction = "阶段上行较快"
    elif period_return > 0.05:
        score = 65
        direction = "阶段上行"
    elif period_return >= -0.05:
        score = 50
        direction = "阶段震荡"
    else:
        score = 30
        direction = "阶段走弱"
    return {
        "factor": "trend_direction",
        "score": score,
        "label": "趋势方向观察",
        "details": {"window": window, "return": float(period_return), "direction": direction},
    }


def calculate_volume_price_factor(price_df, price_col="Close", volume_col="Volume", window=20):
    close = _get_numeric_series(price_df, price_col)
    volume = _get_numeric_series(price_df, volume_col)
    if close.empty or volume.empty:
        return _empty_result("volume_price", "价格或成交量数据不足，无法计算量价因子。")

    period_return = _derive_period_return(price_df, close, window)
    volume_ratio = _derive_volume_ratio(price_df, volume, window)
    if pd.isna(period_return) or pd.isna(volume_ratio):
        return _empty_result("volume_price", "volume-price data is insufficient")

    amount = _latest_from_any(price_df, AMOUNT_COLUMNS)
    turnover = _latest_from_any(price_df, TURNOVER_COLUMNS)
    score, profile_labels = _volume_price_profile(period_return, volume_ratio, amount, turnover)

    return {
        "factor": "volume_price",
        "score": score,
        "label": "量价配合观察",
        "details": {
            "window": window,
            "return": float(period_return),
            "volume_ratio": float(volume_ratio),
            "amount": None if pd.isna(amount) else float(amount),
            "turnover": None if pd.isna(turnover) else float(turnover),
            "volume_price_labels": profile_labels,
        },
    }


def calculate_liquidity_factor(price_df):
    if not isinstance(price_df, pd.DataFrame) or price_df.empty:
        return _empty_result("liquidity", "liquidity data is insufficient")

    amount = _latest_from_any(price_df, AMOUNT_COLUMNS)
    volume = _latest_from_any(price_df, ("Volume", "volume", "成交量"))
    turnover = _latest_from_any(price_df, TURNOVER_COLUMNS)
    score = 50
    labels = []

    if pd.isna(amount):
        score -= 20
    elif amount < 5_000_000:
        labels.append("low_liquidity")
        score = 20
    elif amount < 30_000_000:
        score = 40
    elif amount < 200_000_000:
        score = 65
    else:
        score = 75

    if not pd.isna(volume) and volume < 100_000:
        labels.append("low_liquidity")
        score = min(score, 35)
    if not pd.isna(turnover):
        if turnover < 0.003:
            labels.append("low_liquidity")
            score = min(score, 30)
        elif turnover > 0.15:
            labels.append("overheated_turnover")
            score = min(score, 55)
        elif 0.005 <= turnover <= 0.08:
            score = min(100, score + 5)
    if not labels:
        labels.append("liquidity_observable")

    return {
        "factor": "liquidity",
        "score": max(0, min(100, int(round(score)))),
        "label": "liquidity observation",
        "details": {
            "amount": None if pd.isna(amount) else float(amount),
            "volume": None if pd.isna(volume) else float(volume),
            "turnover": None if pd.isna(turnover) else float(turnover),
            "liquidity_labels": labels,
        },
    }


def calculate_data_quality_factor(price_df, required_columns=("Close", "Volume")):
    if not isinstance(price_df, pd.DataFrame) or price_df.empty:
        return {
            "factor": "data_quality",
            "score": 0,
            "label": "数据质量观察",
            "details": {"missing_columns": list(required_columns), "null_ratio": 1.0, "row_count": 0},
        }

    missing_columns = [column for column in required_columns if column not in price_df.columns]
    available_columns = [column for column in required_columns if column in price_df.columns]
    if available_columns:
        null_count = price_df[available_columns].isna().sum().sum()
        total_count = len(price_df) * len(available_columns)
        null_ratio = float(null_count / total_count) if total_count else 1.0
    else:
        null_ratio = 1.0

    score = 100
    score -= len(missing_columns) * 30
    score -= int(null_ratio * 40)
    if len(price_df) < 20:
        score -= 30
    elif len(price_df) < 60:
        score -= 10

    return {
        "factor": "data_quality",
        "score": max(0, min(100, int(score))),
        "label": "数据质量观察",
        "details": {
            "missing_columns": missing_columns,
            "null_ratio": null_ratio,
            "row_count": int(len(price_df)),
        },
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
    "calculate_data_quality_factor",
    "calculate_liquidity_factor",
    "calculate_momentum_profile_factor",
    "calculate_momentum_factor",
    "calculate_moving_average_position_factor",
    "calculate_trend_factor",
    "calculate_trend_direction_factor",
    "calculate_volatility_factor",
    "calculate_volume_factor",
    "calculate_volume_price_factor",
]
