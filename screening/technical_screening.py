"""Read-only technical screening for the A-share research universe."""

from __future__ import annotations

import copy
import math

import pandas as pd


TECHNICAL_SCREENING_FIELDS = [
    "technical_available",
    "close",
    "ma20",
    "ma60",
    "above_ma20",
    "above_ma60",
    "ma_trend",
    "rsi14",
    "macd_signal",
    "volume_ratio",
    "technical_score",
    "technical_level",
    "technical_screening_status",
    "technical_reasons",
    "technical_warnings",
]

METRIC_FIELDS = [
    "close",
    "ma20",
    "ma60",
    "above_ma20",
    "above_ma60",
    "ma_trend",
    "rsi14",
    "macd_signal",
    "volume_ratio",
]

KEY_ALIASES = {
    "ticker": ["ticker", "symbol", "code", "stock_code"],
}

FIELD_ALIASES = {
    "close": ["close", "latest_close", "收盘价", "最新收盘价"],
    "ma20": ["ma20", "MA20"],
    "ma60": ["ma60", "MA60"],
    "rsi14": ["rsi14", "RSI14", "rsi"],
    "macd_signal": ["macd_signal", "MACD", "macd"],
    "volume_ratio": ["volume_ratio", "volume_multiple", "volume_ratio_20d"],
    "volume": ["volume", "成交量"],
}

STATUS_INCOMPLETE = "Incomplete"
STATUS_PASS = "Pass"
STATUS_WATCH = "Watch"
STATUS_EXCLUDE = "Exclude"

LEVEL_HIGH = "High"
LEVEL_MEDIUM = "Medium"
LEVEL_LOW = "Low"
LEVEL_UNAVAILABLE = "Unavailable"

TREND_UP = "Uptrend"
TREND_DOWN = "Downtrend"
TREND_MIXED = "Mixed"
TREND_UNKNOWN = "Unknown"

MACD_BULLISH = "Bullish"
MACD_BEARISH = "Bearish"
MACD_NEUTRAL = "Neutral"
MACD_UNKNOWN = "Unknown"


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
    for field in TECHNICAL_SCREENING_FIELDS:
        base[field] = pd.Series(dtype="object")
    return base


def _first_existing(row, names):
    for name in names:
        if name in row:
            value = row[name]
            if pd.isna(value):
                continue
            if isinstance(value, str) and not value.strip():
                continue
            return value
    return None


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


def _to_number(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _to_signal(value):
    if value is None or pd.isna(value):
        return MACD_UNKNOWN
    text = str(value).strip().lower()
    if text in {"bullish", "golden", "positive", "up", "1"}:
        return MACD_BULLISH
    if text in {"bearish", "dead", "negative", "down", "-1"}:
        return MACD_BEARISH
    if text in {"neutral", "flat", "0"}:
        return MACD_NEUTRAL
    number = _to_number(value)
    if number is None:
        return MACD_UNKNOWN
    if number > 0:
        return MACD_BULLISH
    if number < 0:
        return MACD_BEARISH
    return MACD_NEUTRAL


def _derive_trend(close, ma20, ma60):
    if close is None or ma20 is None or ma60 is None:
        return TREND_UNKNOWN
    if close > ma20 > ma60:
        return TREND_UP
    if close < ma20 < ma60:
        return TREND_DOWN
    return TREND_MIXED


def _compute_rsi(close_series, period=14):
    if close_series.size < period + 1:
        return None
    delta = close_series.diff()
    gains = delta.clip(lower=0).tail(period)
    losses = -delta.clip(upper=0).tail(period)
    average_gain = gains.mean()
    average_loss = losses.mean()
    if average_loss == 0:
        return 100.0 if average_gain > 0 else 50.0
    rs = average_gain / average_loss
    return float(100 - (100 / (1 + rs)))


def _compute_macd_signal(close_series):
    if close_series.size < 35:
        return MACD_UNKNOWN
    ema12 = close_series.ewm(span=12, adjust=False).mean()
    ema26 = close_series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    latest_hist = macd.iloc[-1] - signal.iloc[-1]
    if latest_hist > 0:
        return MACD_BULLISH
    if latest_hist < 0:
        return MACD_BEARISH
    return MACD_NEUTRAL


def _normalize_history_frame(history):
    frame = _safe_copy_frame(history)
    if frame is None or frame.empty:
        return {}
    close_col = next((name for name in FIELD_ALIASES["close"] if name in frame.columns), None)
    if close_col is None:
        return {}
    volume_col = next((name for name in FIELD_ALIASES["volume"] if name in frame.columns), None)

    close_series = pd.to_numeric(frame[close_col], errors="coerce").dropna()
    if close_series.empty:
        return {}

    volume_ratio = None
    if volume_col is not None:
        volume_series = pd.to_numeric(frame[volume_col], errors="coerce").dropna()
        if not volume_series.empty:
            average_volume = volume_series.tail(20).mean()
            if average_volume and not pd.isna(average_volume):
                volume_ratio = float(volume_series.iloc[-1] / average_volume)

    close = float(close_series.iloc[-1])
    ma20 = float(close_series.tail(20).mean()) if close_series.size >= 20 else None
    ma60 = float(close_series.tail(60).mean()) if close_series.size >= 60 else None
    return {
        "close": close,
        "ma20": ma20,
        "ma60": ma60,
        "above_ma20": close > ma20 if ma20 is not None else None,
        "above_ma60": close > ma60 if ma60 is not None else None,
        "ma_trend": _derive_trend(close, ma20, ma60),
        "rsi14": _compute_rsi(close_series),
        "macd_signal": _compute_macd_signal(close_series),
        "volume_ratio": volume_ratio,
    }


def _normalize_price_snapshot(price):
    if price is None or price.empty:
        return pd.DataFrame(columns=["ticker", *METRIC_FIELDS])

    rows = []
    for _, row in price.iterrows():
        row_dict = row.to_dict()
        close = _to_number(_first_existing(row_dict, FIELD_ALIASES["close"]))
        ma20 = _to_number(_first_existing(row_dict, FIELD_ALIASES["ma20"]))
        ma60 = _to_number(_first_existing(row_dict, FIELD_ALIASES["ma60"]))
        macd_signal = _to_signal(_first_existing(row_dict, FIELD_ALIASES["macd_signal"]))
        normalized = {
            "ticker": _normalize_ticker(_first_existing(row_dict, KEY_ALIASES["ticker"])),
            "close": close,
            "ma20": ma20,
            "ma60": ma60,
            "above_ma20": close > ma20 if close is not None and ma20 is not None else None,
            "above_ma60": close > ma60 if close is not None and ma60 is not None else None,
            "ma_trend": _derive_trend(close, ma20, ma60),
            "rsi14": _to_number(_first_existing(row_dict, FIELD_ALIASES["rsi14"])),
            "macd_signal": macd_signal,
            "volume_ratio": _to_number(_first_existing(row_dict, FIELD_ALIASES["volume_ratio"])),
        }
        if normalized["ticker"]:
            rows.append(normalized)
    if not rows:
        return pd.DataFrame(columns=["ticker", *METRIC_FIELDS])
    return pd.DataFrame(rows).drop_duplicates(subset=["ticker"], keep="first")


def _normalize_price_input(price_data):
    if isinstance(price_data, dict):
        rows = []
        for ticker, history in copy.deepcopy(price_data).items():
            metrics = _normalize_history_frame(history)
            if metrics:
                rows.append({"ticker": _normalize_ticker(ticker), **metrics})
        if not rows:
            return pd.DataFrame(columns=["ticker", *METRIC_FIELDS])
        return pd.DataFrame(rows).drop_duplicates(subset=["ticker"], keep="first")
    return _normalize_price_snapshot(_safe_copy_frame(price_data))


def _score_row(row):
    values = {field: row.get(field) for field in METRIC_FIELDS}
    usable = {
        key: value
        for key, value in values.items()
        if value is not None and not pd.isna(value) and value not in {TREND_UNKNOWN, MACD_UNKNOWN}
    }
    if not usable:
        return {
            "technical_available": False,
            "technical_score": 0,
            "technical_level": LEVEL_UNAVAILABLE,
            "technical_screening_status": STATUS_INCOMPLETE,
            "technical_reasons": [],
            "technical_warnings": ["No usable technical data."],
        }

    score = 0
    reasons = []
    warnings = []

    close = values["close"]
    ma20 = values["ma20"]
    ma60 = values["ma60"]
    if close is None or pd.isna(close):
        warnings.append("Close missing.")
    if ma20 is None or pd.isna(ma20):
        warnings.append("MA20 missing.")
    if ma60 is None or pd.isna(ma60):
        warnings.append("MA60 missing.")

    if close is not None and ma20 is not None and not pd.isna(close) and not pd.isna(ma20):
        if close > ma20:
            score += 25
            reasons.append("Close is above MA20.")
        else:
            warnings.append("Close is not above MA20.")
    if close is not None and ma60 is not None and not pd.isna(close) and not pd.isna(ma60):
        if close > ma60:
            score += 20
            reasons.append("Close is above MA60.")
        else:
            warnings.append("Close is not above MA60.")
    if ma20 is not None and ma60 is not None and not pd.isna(ma20) and not pd.isna(ma60):
        if ma20 > ma60:
            score += 20
            reasons.append("MA20 is above MA60.")
        else:
            warnings.append("MA structure is weak.")

    rsi14 = values["rsi14"]
    if rsi14 is None or pd.isna(rsi14):
        warnings.append("RSI14 missing.")
    elif 40 <= rsi14 <= 70:
        score += 15
        reasons.append("RSI14 is in a moderate range.")
    elif rsi14 > 80 or rsi14 < 30:
        score -= 5
        warnings.append("RSI14 is abnormal.")
    else:
        warnings.append("RSI14 needs attention.")

    macd_signal = values["macd_signal"]
    if macd_signal == MACD_BULLISH:
        score += 15
        reasons.append("MACD signal is bullish.")
    elif macd_signal == MACD_BEARISH:
        score -= 15
        warnings.append("MACD signal is bearish.")
    elif macd_signal == MACD_UNKNOWN:
        warnings.append("MACD signal missing.")

    volume_ratio = values["volume_ratio"]
    if volume_ratio is None or pd.isna(volume_ratio):
        warnings.append("Volume ratio missing.")
    elif volume_ratio > 1:
        score += 10
        reasons.append("Volume ratio is above 1.")

    score = int(max(0, min(100, score)))
    if score >= 75:
        level = LEVEL_HIGH
        status = STATUS_PASS
    elif score >= 50:
        level = LEVEL_MEDIUM
        status = STATUS_WATCH
    else:
        level = LEVEL_LOW
        status = STATUS_EXCLUDE if score < 30 else STATUS_WATCH

    return {
        "technical_available": True,
        "technical_score": score,
        "technical_level": level,
        "technical_screening_status": status,
        "technical_reasons": reasons,
        "technical_warnings": warnings,
    }


def build_technical_screening(universe_df, price_data=None):
    """Append read-only technical screening fields to an A-share universe."""
    universe = _safe_copy_frame(universe_df)
    if universe is None:
        universe = pd.DataFrame()
    if universe.empty:
        return _empty_like(universe)

    result = universe.copy(deep=True)
    prices = _normalize_price_input(price_data)

    if "ticker" in result.columns:
        universe_keys = result["ticker"].map(_normalize_ticker)
    elif "symbol" in result.columns:
        universe_keys = result["symbol"].map(_normalize_ticker)
    else:
        universe_keys = pd.Series([None] * len(result), index=result.index)

    prices_by_ticker = prices.set_index("ticker").to_dict(orient="index") if not prices.empty else {}
    output_rows = []
    for index, row in result.iterrows():
        metrics = prices_by_ticker.get(universe_keys.loc[index], {})
        scored_input = row.to_dict()
        for field in METRIC_FIELDS:
            scored_input[field] = metrics.get(field)
        scored = _score_row(scored_input)
        output_rows.append({**{field: scored_input.get(field) for field in METRIC_FIELDS}, **scored})

    output = pd.DataFrame(output_rows, index=result.index)
    for field in TECHNICAL_SCREENING_FIELDS:
        result[field] = output[field].astype(object) if field in {"technical_available", "above_ma20", "above_ma60"} else output[field]
    return result


__all__ = [
    "TECHNICAL_SCREENING_FIELDS",
    "build_technical_screening",
]
