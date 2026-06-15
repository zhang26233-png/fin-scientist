"""Build real technical indicator fields from historical price data.

The module is additive and research-only. It does not emit trading
instructions or modify legacy scoring columns.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


REAL_TECHNICAL_INDICATOR_FIELDS = [
    "technical_history_available",
    "technical_history_days",
    "ma5",
    "ma10",
    "ma20",
    "ma60",
    "ma120",
    "above_ma5",
    "above_ma20",
    "above_ma60",
    "ma_bullish_alignment",
    "ma_bearish_alignment",
    "return_20d",
    "return_60d",
    "rsi14",
    "macd_dif",
    "macd_dea",
    "macd_hist",
    "macd_signal",
    "atr14",
    "volatility_20d",
    "max_drawdown_60d",
    "volume_ma20",
    "volume_ratio_20d",
    "turnover_ma20",
    "turnover_ratio_20d",
    "high_52w",
    "low_52w",
    "position_52w",
    "near_52w_high",
    "near_52w_low",
    "technical_trend_score",
    "technical_momentum_score",
    "technical_volume_score",
    "technical_volatility_score",
    "technical_position_score",
    "real_technical_score",
    "technical_signal_summary",
    "technical_risk_flags",
    "technical_indicator_warnings",
]

BOOLEAN_INDICATOR_FIELDS = {
    "technical_history_available",
    "above_ma5",
    "above_ma20",
    "above_ma60",
    "ma_bullish_alignment",
    "ma_bearish_alignment",
    "near_52w_high",
    "near_52w_low",
}


def _to_number(value: Any) -> float | None:
    if value is None or pd.isna(value) or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value).strip().replace(",", "")
        if not text or text in {"-", "--", "None", "nan"}:
            return None
        try:
            number = float(text)
        except ValueError:
            return None
    if pd.isna(number) or math.isinf(number):
        return None
    return number


def _clip_score(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 2)


def _round(value: Any, digits: int = 4) -> float | None:
    number = _to_number(value)
    if number is None:
        return None
    return round(number, digits)


def _normalize_ticker(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else text


def _history_for_ticker(ticker: str, price_history_dict: dict[str, pd.DataFrame] | None) -> pd.DataFrame:
    if not isinstance(price_history_dict, dict) or not ticker:
        return pd.DataFrame()
    candidates = [ticker, ticker.zfill(6), f"sh{ticker}", f"sz{ticker}", f"{ticker}.SH", f"{ticker}.SZ"]
    for key in candidates:
        value = price_history_dict.get(key)
        if isinstance(value, pd.DataFrame):
            return value.copy(deep=True)
    return pd.DataFrame()


def _normalize_history(history: pd.DataFrame) -> pd.DataFrame:
    if history is None or history.empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume", "turnover"])
    source = history.copy(deep=True)
    source.columns = [str(column).strip().lower() for column in source.columns]
    aliases = {
        "trade_date": "date",
        "time": "date",
        "datetime": "date",
        "收盘": "close",
        "close_price": "close",
        "最新价": "close",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "turnover",
        "amount": "turnover",
    }
    source = source.rename(columns={key: value for key, value in aliases.items() if key in source.columns})
    for field in ["open", "high", "low", "close", "volume", "turnover"]:
        if field in source.columns:
            source[field] = pd.to_numeric(source[field], errors="coerce")
    if "date" in source.columns:
        source["date"] = pd.to_datetime(source["date"], errors="coerce")
        source = source.sort_values("date", kind="mergesort")
    return source.dropna(subset=["close"]).reset_index(drop=True)


def _last_valid(series: pd.Series) -> float | None:
    valid = series.dropna()
    if valid.empty:
        return None
    return _round(valid.iloc[-1])


def _rolling_last(close: pd.Series, window: int, warnings: list[str]) -> float | None:
    if close.count() < window:
        warnings.append(f"历史不足{window}日，MA{window}不可用")
        return None
    return _last_valid(close.rolling(window).mean())


def _rsi14(close: pd.Series) -> float | None:
    if close.count() < 15:
        return None
    delta = close.diff().dropna().tail(14)
    gain = delta.clip(lower=0).mean()
    loss = (-delta.clip(upper=0)).mean()
    if loss == 0:
        return 100.0 if gain > 0 else 0.0
    if gain == 0:
        return 0.0
    rs = gain / loss
    return _round(100 - (100 / (1 + rs)))


def _macd(close: pd.Series) -> tuple[float | None, float | None, float | None, str]:
    if close.count() < 35:
        return None, None, None, "Unknown"
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9, adjust=False).mean()
    hist = dif - dea
    dif_value = _last_valid(dif)
    dea_value = _last_valid(dea)
    hist_value = _last_valid(hist)
    if dif_value is None or dea_value is None or hist_value is None:
        return dif_value, dea_value, hist_value, "Unknown"
    if dif_value > dea_value and hist_value > 0:
        signal = "Bullish"
    elif dif_value < dea_value and hist_value < 0:
        signal = "Bearish"
    else:
        signal = "Neutral"
    return dif_value, dea_value, hist_value, signal


def _atr14(history: pd.DataFrame) -> float | None:
    if len(history) < 15 or not {"high", "low", "close"}.issubset(history.columns):
        return None
    high = history["high"]
    low = history["low"]
    prev_close = history["close"].shift(1)
    tr = pd.concat([(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return _last_valid(tr.rolling(14).mean())


def _max_drawdown_60d(close: pd.Series) -> float | None:
    if close.count() < 2:
        return None
    window = close.tail(60)
    drawdown = (window / window.cummax()) - 1
    return _round(drawdown.min())


def _score_trend(close: float, ma20: float | None, ma60: float | None, bullish: bool, bearish: bool) -> float:
    score = 50.0
    if ma20 is not None:
        score += 10 if close > ma20 else -10
    if ma60 is not None:
        score += 10 if close > ma60 else -10
    if ma20 is not None and ma60 is not None and ma20 > ma60:
        score += 10
    if bullish:
        score += 15
    if bearish:
        score -= 15
    return _clip_score(score)


def _score_momentum(rsi: float | None, macd_signal: str, return_20d: float | None, risks: list[str]) -> float:
    score = 50.0
    if rsi is not None:
        if 40 <= rsi <= 70:
            score += 15
        elif 70 < rsi <= 80:
            score += 5
            risks.append("RSI偏高")
        elif rsi > 80:
            score -= 10
            risks.append("RSI过热")
        elif 30 <= rsi < 40:
            score -= 5
        elif rsi < 30:
            score -= 10
            risks.append("RSI偏弱")
    if macd_signal == "Bullish":
        score += 15
    elif macd_signal == "Bearish":
        score -= 15
    if return_20d is not None:
        if 0 <= return_20d <= 0.15:
            score += 10
        elif return_20d > 0.25:
            score -= 5
            risks.append("短期涨幅较高")
        elif return_20d < -0.1:
            score -= 10
    return _clip_score(score)


def _score_volume(volume_ratio: float | None, turnover_ratio: float | None, risks: list[str]) -> float:
    score = 50.0
    if volume_ratio is not None:
        if 1.0 <= volume_ratio <= 2.5:
            score += 20
        elif 2.5 < volume_ratio <= 5:
            score += 10
            risks.append("阶段性放量")
        elif volume_ratio > 5:
            score -= 5
            risks.append("异常放量")
        elif 0.5 <= volume_ratio < 1:
            score += 5
        elif volume_ratio < 0.5:
            score -= 10
    if turnover_ratio is not None:
        if 1.0 <= turnover_ratio <= 3:
            score += 15
        elif turnover_ratio > 5:
            score -= 5
            risks.append("成交额异常放大")
    return _clip_score(score)


def _score_volatility(volatility: float | None, drawdown: float | None, risks: list[str]) -> float:
    score = 70.0
    if volatility is not None:
        if volatility <= 0.25:
            score += 10
        elif 0.45 < volatility <= 0.7:
            score -= 10
        elif volatility > 0.7:
            score -= 20
            risks.append("波动率较高")
    if drawdown is not None:
        if drawdown > -0.1:
            score += 10
        elif -0.35 <= drawdown < -0.2:
            score -= 10
        elif drawdown < -0.35:
            score -= 20
            risks.append("阶段回撤较大")
    return _clip_score(score)


def _score_position(position: float | None, risks: list[str]) -> float:
    score = 50.0
    if position is not None:
        if 0.3 <= position <= 0.75:
            score += 20
        elif 0.75 < position <= 0.9:
            score += 10
        elif position > 0.9:
            risks.append("接近52周高位")
        elif position < 0.1:
            score -= 10
            risks.append("接近52周低位")
    return _clip_score(score)


def _ratio(latest: float | None, average: float | None) -> float | None:
    if latest is None or average is None or average == 0:
        return None
    return _round(latest / average)


def _fallback_row(row: pd.Series, history_days: int) -> dict[str, Any]:
    fallback = _to_number(row.get("activated_technical_score"))
    score = _clip_score(fallback) if fallback is not None and fallback > 0 else 50.0
    values = {field: None for field in REAL_TECHNICAL_INDICATOR_FIELDS}
    values.update(
        {
            "technical_history_available": False,
            "technical_history_days": int(history_days),
            "macd_signal": "Unknown",
            "technical_trend_score": 50.0,
            "technical_momentum_score": 50.0,
            "technical_volume_score": 50.0,
            "technical_volatility_score": 50.0,
            "technical_position_score": 50.0,
            "real_technical_score": score,
            "technical_signal_summary": "历史行情不足，使用实时快照研究评分降级。",
            "technical_risk_flags": [],
            "technical_indicator_warnings": ["历史行情不足"],
        }
    )
    return values


def _build_indicator_row(row: pd.Series, history: pd.DataFrame) -> dict[str, Any]:
    normalized = _normalize_history(history)
    history_days = int(normalized["close"].count()) if "close" in normalized.columns else 0
    if history_days < 60:
        return _fallback_row(row, history_days)

    warnings: list[str] = []
    risks: list[str] = []
    close = normalized["close"]
    latest_close = _to_number(close.iloc[-1]) or 0.0
    ma5 = _rolling_last(close, 5, warnings)
    ma10 = _rolling_last(close, 10, warnings)
    ma20 = _rolling_last(close, 20, warnings)
    ma60 = _rolling_last(close, 60, warnings)
    ma120 = _rolling_last(close, 120, warnings)

    bullish = all(value is not None for value in [ma5, ma10, ma20, ma60]) and bool(ma5 > ma10 > ma20 > ma60)
    bearish = all(value is not None for value in [ma5, ma10, ma20, ma60]) and bool(ma5 < ma10 < ma20 < ma60)
    return_20d = _round((latest_close / close.iloc[-21]) - 1) if history_days >= 21 and close.iloc[-21] else None
    return_60d = _round((latest_close / close.iloc[-61]) - 1) if history_days >= 61 and close.iloc[-61] else None
    rsi = _rsi14(close)
    macd_dif, macd_dea, macd_hist, macd_signal = _macd(close)
    atr = _atr14(normalized)
    if atr is None:
        warnings.append("ATR14字段不足或历史不足")
    volatility = _last_valid(close.pct_change().rolling(20).std() * math.sqrt(252))
    drawdown = _max_drawdown_60d(close)

    volume_ma20 = volume_ratio = None
    if "volume" in normalized.columns and normalized["volume"].dropna().count() >= 20:
        volume_ma20 = _last_valid(normalized["volume"].rolling(20).mean())
        volume_ratio = _ratio(_to_number(normalized["volume"].iloc[-1]), volume_ma20)
    else:
        warnings.append("volume历史字段不足")

    turnover_ma20 = turnover_ratio = None
    if "turnover" in normalized.columns and normalized["turnover"].dropna().count() >= 20:
        turnover_ma20 = _last_valid(normalized["turnover"].rolling(20).mean())
        turnover_ratio = _ratio(_to_number(normalized["turnover"].iloc[-1]), turnover_ma20)
    else:
        warnings.append("turnover历史字段不足")

    if history_days < 252:
        warnings.append("历史不足252日，52周位置为近似值")
    window_52w = normalized.tail(min(252, history_days))
    high_source = window_52w["high"] if "high" in window_52w.columns else window_52w["close"]
    low_source = window_52w["low"] if "low" in window_52w.columns else window_52w["close"]
    high_52w = _round(high_source.max())
    low_52w = _round(low_source.min())
    position_52w = None
    if high_52w is None or low_52w is None or high_52w == low_52w:
        warnings.append("52周高低区间不足，位置不可用")
    else:
        position_52w = _round((latest_close - low_52w) / (high_52w - low_52w))
        position_52w = _round(max(0.0, min(1.0, position_52w)))

    trend_score = _score_trend(latest_close, ma20, ma60, bullish, bearish)
    momentum_score = _score_momentum(rsi, macd_signal, return_20d, risks)
    volume_score = _score_volume(volume_ratio, turnover_ratio, risks)
    volatility_score = _score_volatility(volatility, drawdown, risks)
    position_score = _score_position(position_52w, risks)
    real_score = _clip_score(
        (0.30 * trend_score)
        + (0.25 * momentum_score)
        + (0.20 * volume_score)
        + (0.15 * volatility_score)
        + (0.10 * position_score)
    )
    summary_parts = [
        f"Trend {trend_score}",
        f"Momentum {momentum_score}",
        f"Volume {volume_score}",
        f"MACD {macd_signal}",
    ]
    return {
        "technical_history_available": True,
        "technical_history_days": history_days,
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "ma60": ma60,
        "ma120": ma120,
        "above_ma5": bool(ma5 is not None and latest_close > ma5),
        "above_ma20": bool(ma20 is not None and latest_close > ma20),
        "above_ma60": bool(ma60 is not None and latest_close > ma60),
        "ma_bullish_alignment": bool(bullish),
        "ma_bearish_alignment": bool(bearish),
        "return_20d": return_20d,
        "return_60d": return_60d,
        "rsi14": rsi,
        "macd_dif": macd_dif,
        "macd_dea": macd_dea,
        "macd_hist": macd_hist,
        "macd_signal": macd_signal,
        "atr14": atr,
        "volatility_20d": volatility,
        "max_drawdown_60d": drawdown,
        "volume_ma20": volume_ma20,
        "volume_ratio_20d": volume_ratio,
        "turnover_ma20": turnover_ma20,
        "turnover_ratio_20d": turnover_ratio,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "position_52w": position_52w,
        "near_52w_high": bool(position_52w is not None and position_52w >= 0.9),
        "near_52w_low": bool(position_52w is not None and position_52w <= 0.1),
        "technical_trend_score": trend_score,
        "technical_momentum_score": momentum_score,
        "technical_volume_score": volume_score,
        "technical_volatility_score": volatility_score,
        "technical_position_score": position_score,
        "real_technical_score": real_score,
        "technical_signal_summary": " | ".join(summary_parts),
        "technical_risk_flags": list(dict.fromkeys(risks)),
        "technical_indicator_warnings": list(dict.fromkeys(warnings)),
    }


def build_real_technical_indicators(
    df: pd.DataFrame | None,
    price_history_dict: dict[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """Append real technical indicator fields without mutating inputs."""
    if df is None:
        result = pd.DataFrame()
    elif isinstance(df, pd.DataFrame):
        result = df.copy(deep=True)
    else:
        result = pd.DataFrame(df).copy(deep=True)

    if result.empty:
        for field in REAL_TECHNICAL_INDICATOR_FIELDS:
            result[field] = pd.Series(dtype="object")
        return result

    attrs = dict(getattr(df, "attrs", {}))
    rows: list[dict[str, Any]] = []
    for _, row in result.iterrows():
        ticker = _normalize_ticker(row.get("ticker", row.get("symbol", "")))
        history = _history_for_ticker(ticker, price_history_dict)
        rows.append(_build_indicator_row(row, history))
    output = pd.DataFrame(rows, index=result.index)
    for field in REAL_TECHNICAL_INDICATOR_FIELDS:
        result[field] = output[field].astype(object) if field in BOOLEAN_INDICATOR_FIELDS else output[field]
    result.attrs.update(attrs)
    return result


__all__ = [
    "REAL_TECHNICAL_INDICATOR_FIELDS",
    "build_real_technical_indicators",
]
