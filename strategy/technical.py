"""Read-only technical structure labels for strategy preview rows."""

import copy
import math


TECHNICAL_PROFILE_FIELDS = [
    "ma_structure_label",
    "trend_quality_label",
    "breakout_pullback_label",
    "volume_price_structure_label",
    "short_term_overheat_label",
    "volatility_risk_label",
    "technical_profile_summary",
    "technical_grade",
    "technical_style",
    "technical_strength",
    "technical_risk_level",
    "technical_watch_points",
    "technical_summary_short",
]


def _finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _read_any(row, keys):
    if not isinstance(row, dict):
        return None
    lowered = {str(key).lower(): key for key in row}
    for key in keys:
        if key in row:
            return row.get(key)
        matched = lowered.get(str(key).lower())
        if matched is not None:
            return row.get(matched)
    return None


def _number(row, keys):
    return _finite_number(_read_any(row, keys))


def _label(row, keys):
    value = _read_any(row, keys)
    return "" if value is None else str(value)


def _copy_row(row):
    if hasattr(row, "to_dict"):
        return copy.deepcopy(row.to_dict())
    if isinstance(row, dict):
        return copy.deepcopy(row)
    return {}


def analyze_moving_average_structure(row):
    data = _copy_row(row)
    close = _number(data, ("close", "Close", "price"))
    ma5 = _number(data, ("ma5", "MA5"))
    ma10 = _number(data, ("ma10", "MA10"))
    ma20 = _number(data, ("ma20", "MA20"))
    if None in (close, ma5, ma10, ma20):
        return "insufficient_ma_data"
    if close > ma5 > ma10 > ma20:
        return "bullish_alignment"
    if close < ma5 < ma10 < ma20:
        return "bearish_alignment"
    above_count = sum(close > value for value in (ma5, ma10, ma20))
    if above_count >= 2 and ma5 >= ma10:
        return "partial_bullish"
    return "neutral_ma"


def analyze_trend_quality(row):
    data = _copy_row(row)
    trend_score = _number(data, ("trend_score",))
    momentum_score = _number(data, ("momentum_score",))
    return_20d = _number(data, ("return_20d", "recent_return", "pct_chg"))
    volatility = _number(data, ("volatility", "annual_volatility"))
    ma_label = _label(data, ("ma_structure_label",)) or analyze_moving_average_structure(data)

    if trend_score is None and return_20d is None:
        return "insufficient_trend_data"
    if ma_label == "bullish_alignment" and (trend_score or 0) >= 70 and (momentum_score or 0) >= 60:
        return "strong_trend"
    if trend_score is not None and trend_score >= 75 and return_20d is not None and return_20d >= 0.08:
        return "strong_trend"
    if return_20d is not None and return_20d < -0.05:
        return "weak_trend"
    if trend_score is not None and trend_score < 40:
        return "weak_trend"
    if ma_label in {"partial_bullish", "bullish_alignment"} or (return_20d is not None and return_20d > 0.03):
        return "improving_trend"
    if volatility is not None and volatility >= 0.55:
        return "choppy_trend"
    return "choppy_trend"


def analyze_breakout_pullback_state(row):
    data = _copy_row(row)
    close = _number(data, ("close", "Close", "price"))
    recent_high = _number(data, ("recent_high", "high_20d", "highest_20d"))
    support = _number(data, ("support_price", "ma20", "MA20", "recent_low", "low_20d"))
    return_20d = _number(data, ("return_20d", "recent_return"))
    return_5d = _number(data, ("return_5d", "pct_chg"))
    volume_ratio = _number(data, ("volume_ratio",))

    if close is None:
        return "insufficient_price_data"
    if recent_high is not None and close >= recent_high * 0.98 and (return_20d or 0) > 0.03 and (volume_ratio or 0) >= 1.2:
        return "breakout_confirmed"
    if support is not None and support > 0 and 0 <= (close - support) / support <= 0.04 and (return_20d or 0) >= 0:
        return "pullback_near_support"
    if (return_20d or 0) > 0.05 and (return_5d or 0) < -0.04 and (volume_ratio or 0) >= 1.1:
        return "failed_breakout"
    return "no_clear_breakout"


def analyze_volume_price_structure(row):
    data = _copy_row(row)
    volume_ratio = _number(data, ("volume_ratio",))
    amount = _number(data, ("amount", "turnover_amount"))
    volume = _number(data, ("volume", "Volume"))
    return_20d = _number(data, ("return_20d", "recent_return"))
    return_5d = _number(data, ("return_5d", "pct_chg"))

    if volume_ratio is None and amount is None and volume is None:
        return "insufficient_volume_data"
    if volume_ratio is not None and ((return_5d is not None and return_5d < -0.05) or (return_20d is not None and return_20d < 0)):
        if volume_ratio >= 1.3:
            return "volume_downside_risk"
    if volume_ratio is not None and volume_ratio >= 1.2 and max(return_20d or 0, return_5d or 0) > 0.03:
        return "volume_price_confirmed"
    if volume_ratio is not None and volume_ratio < 0.8 and max(return_20d or 0, return_5d or 0) > 0.03:
        return "volume_price_divergence"
    if volume_ratio is not None and volume_ratio < 0.8:
        return "low_volume_uncertain"
    return "low_volume_uncertain"


def analyze_short_term_overheat(row):
    data = _copy_row(row)
    return_5d = _number(data, ("return_5d", "pct_chg"))
    return_10d = _number(data, ("return_10d", "10d_return"))
    return_20d = _number(data, ("return_20d", "recent_return"))
    turnover = _number(data, ("turnover", "turnover_rate"))

    if return_5d is None and return_10d is None and return_20d is None:
        return "insufficient_return_data"
    if (return_5d is not None and return_5d >= 0.15) or (return_10d is not None and return_10d >= 0.25) or (return_20d is not None and return_20d >= 0.35):
        return "severe_overheat"
    if (return_5d is not None and return_5d >= 0.08) or (return_10d is not None and return_10d >= 0.15) or (turnover is not None and turnover >= 0.15):
        return "moderate_overheat"
    if (return_5d is not None and return_5d <= -0.05) or (return_10d is not None and return_10d <= -0.08):
        return "short_term_weakness"
    return "normal_temperature"


def analyze_volatility_risk(row):
    data = _copy_row(row)
    volatility = _number(data, ("volatility", "annual_volatility"))
    amplitude = _number(data, ("amplitude",))
    if volatility is None and amplitude is None:
        return "insufficient_volatility_data"
    if (volatility is not None and volatility >= 0.80) or (amplitude is not None and amplitude >= 0.12):
        return "high_volatility"
    if volatility is not None and volatility >= 0.35:
        return "moderate_volatility"
    if amplitude is not None and amplitude >= 0.06:
        return "moderate_volatility"
    return "low_volatility"


def _summary(profile):
    labels = [profile.get(field) for field in TECHNICAL_PROFILE_FIELDS if field.endswith("_label")]
    if any(str(label).startswith("insufficient") for label in labels):
        return "技术结构字段不完整，当前技术判断可信度有限，仅用于研究优先级观察。"
    if (
        profile["ma_structure_label"] == "bullish_alignment"
        and profile["trend_quality_label"] == "strong_trend"
        and profile["short_term_overheat_label"] in {"normal_temperature", "moderate_overheat"}
    ):
        return "均线、趋势和动量结构较强，适合作为进一步研究对象观察。"
    if profile["short_term_overheat_label"] in {"severe_overheat", "moderate_overheat"} and profile["volatility_risk_label"] == "high_volatility":
        return "短期涨幅或换手热度较高，同时波动风险偏高，需要优先核查风险标签。"
    if profile["volume_price_structure_label"] in {"volume_price_divergence", "volume_downside_risk"}:
        return "量价结构存在背离或放量走弱，需要结合原始成交字段谨慎观察。"
    if profile["ma_structure_label"] == "bearish_alignment" or profile["trend_quality_label"] == "weak_trend":
        return "均线或趋势结构偏弱，当前更适合做风险和数据质量复核。"
    return "技术结构未形成单一强特征，建议结合趋势、量价、波动和数据质量标签综合观察。"


def _insufficient_count(profile):
    return sum(
        1
        for field in (
            "ma_structure_label",
            "trend_quality_label",
            "breakout_pullback_label",
            "volume_price_structure_label",
            "short_term_overheat_label",
            "volatility_risk_label",
        )
        if str(profile.get(field, "")).startswith("insufficient")
    )


def _technical_risk_level(profile):
    if _insufficient_count(profile) >= 3:
        return "unknown"
    if (
        profile.get("volatility_risk_label") == "high_volatility"
        or profile.get("short_term_overheat_label") == "severe_overheat"
        or profile.get("volume_price_structure_label") == "volume_downside_risk"
    ):
        return "high"
    if (
        profile.get("volatility_risk_label") == "moderate_volatility"
        or profile.get("short_term_overheat_label") == "moderate_overheat"
        or profile.get("volume_price_structure_label") == "volume_price_divergence"
    ):
        return "medium"
    return "low"


def _technical_strength(profile):
    insufficient_count = _insufficient_count(profile)
    if insufficient_count >= 2:
        return "uncertain"
    if profile.get("ma_structure_label") == "bullish_alignment" and profile.get("trend_quality_label") == "strong_trend":
        return "strong"
    if profile.get("trend_quality_label") in {"improving_trend", "strong_trend"}:
        return "moderate"
    if profile.get("ma_structure_label") == "bearish_alignment" or profile.get("trend_quality_label") == "weak_trend":
        return "weak"
    return "uncertain"


def _technical_risk_adjusted_grade(profile):
    insufficient_count = _insufficient_count(profile)
    risk_level = profile.get("technical_risk_level") or _technical_risk_level(profile)
    strength = profile.get("technical_strength") or _technical_strength(profile)
    strong_structure = (
        profile.get("ma_structure_label") == "bullish_alignment"
        and profile.get("trend_quality_label") == "strong_trend"
        and profile.get("volume_price_structure_label") == "volume_price_confirmed"
    )
    if insufficient_count >= 4:
        return "D"
    if insufficient_count >= 2:
        return "C"
    if strong_structure and risk_level != "high" and profile.get("short_term_overheat_label") != "severe_overheat":
        return "A"
    if risk_level == "high":
        return "D" if strength == "weak" else "C"
    if strength == "moderate" or profile.get("trend_quality_label") == "improving_trend":
        return "B"
    if strength == "weak" or profile.get("volume_price_structure_label") in {"volume_downside_risk", "volume_price_divergence"}:
        return "D"
    return "C"


def _technical_style(profile):
    if _insufficient_count(profile) >= 3:
        return "insufficient_data"
    if profile.get("volatility_risk_label") == "high_volatility" or profile.get("short_term_overheat_label") == "severe_overheat":
        return "high_volatility_watch"
    if profile.get("breakout_pullback_label") == "pullback_near_support":
        return "pullback_watch"
    if profile.get("volume_price_structure_label") == "volume_price_confirmed" and profile.get("breakout_pullback_label") == "breakout_confirmed":
        return "volume_breakout"
    if profile.get("trend_quality_label") in {"strong_trend", "improving_trend"} and profile.get("ma_structure_label") in {"bullish_alignment", "partial_bullish"}:
        return "trend_momentum"
    if profile.get("trend_quality_label") in {"weak_trend", "choppy_trend"} or profile.get("ma_structure_label") == "bearish_alignment":
        return "weak_or_choppy"
    return "weak_or_choppy"


def _technical_watch_points(profile):
    points = []
    if _insufficient_count(profile) >= 2:
        points.append("数据不足，需补充行情字段后再判断。")
    if profile.get("trend_quality_label") in {"strong_trend", "improving_trend"}:
        points.append("观察趋势结构是否延续。")
    if profile.get("volume_price_structure_label") == "volume_price_confirmed":
        points.append("观察放量后是否继续获得量价确认。")
    if profile.get("breakout_pullback_label") == "pullback_near_support":
        points.append("观察回踩位置附近的量价稳定性。")
    if profile.get("volume_price_structure_label") in {"volume_price_divergence", "volume_downside_risk"}:
        points.append("观察量价背离或放量走弱是否延续。")
    if profile.get("short_term_overheat_label") in {"severe_overheat", "moderate_overheat"} or profile.get("volatility_risk_label") == "high_volatility":
        points.append("观察短期过热后的波动风险。")
    if not points:
        points.append("观察技术结构是否形成更清晰方向。")
    return points[:3]


def _technical_summary_short(profile):
    grade = profile.get("technical_grade")
    style = profile.get("technical_style")
    strength = profile.get("technical_strength")
    risk = profile.get("technical_risk_level")
    if strength == "uncertain":
        return "技术结构信息不足，当前仅适合做粗略研究观察。"
    if grade == "A":
        return "技术结构偏强，趋势与量价存在一定共振，但仍需持续观察风险标签。"
    if risk == "high":
        return "技术结构存在较高波动或过热风险，需要结合原始行情字段继续观察。"
    if style == "weak_or_choppy" or grade == "D":
        return "技术结构偏弱或波动较杂，当前更适合做风险与数据质量复核。"
    if grade == "B":
        return "技术结构有所改善或局部较强，但仍需要观察量价和波动变化。"
    return "技术结构分歧较大，需要结合趋势、量价和波动标签综合观察。"


def _add_technical_conclusion(profile):
    profile["technical_risk_level"] = _technical_risk_level(profile)
    profile["technical_strength"] = _technical_strength(profile)
    profile["technical_grade"] = _technical_risk_adjusted_grade(profile)
    profile["technical_style"] = _technical_style(profile)
    profile["technical_watch_points"] = _technical_watch_points(profile)
    profile["technical_summary_short"] = _technical_summary_short(profile)
    return profile


def build_technical_profile(row):
    data = _copy_row(row)
    profile = {
        "ma_structure_label": analyze_moving_average_structure(data),
        "trend_quality_label": analyze_trend_quality(data),
        "breakout_pullback_label": analyze_breakout_pullback_state(data),
        "volume_price_structure_label": analyze_volume_price_structure(data),
        "short_term_overheat_label": analyze_short_term_overheat(data),
        "volatility_risk_label": analyze_volatility_risk(data),
    }
    profile["technical_profile_summary"] = _summary(profile)
    return _add_technical_conclusion(profile)


__all__ = [
    "TECHNICAL_PROFILE_FIELDS",
    "analyze_moving_average_structure",
    "analyze_trend_quality",
    "analyze_breakout_pullback_state",
    "analyze_volume_price_structure",
    "analyze_short_term_overheat",
    "analyze_volatility_risk",
    "build_technical_profile",
]
