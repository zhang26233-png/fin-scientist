"""Read-only fundamental field normalization and quality checks."""

import copy
import math


FUNDAMENTAL_FIELDS = [
    "revenue",
    "net_profit",
    "gross_margin",
    "roe",
    "pe",
    "pb",
    "ps",
    "debt_ratio",
    "operating_cashflow",
    "revenue_growth",
    "profit_growth",
    "market_cap",
    "industry",
]

FUNDAMENTAL_PROFILE_FIELDS = [
    "fundamental_available",
    "fundamental_fields_detected",
    "missing_fundamental_fields",
    "fundamental_data_quality_label",
    "fundamental_summary_base",
    "profitability_score",
    "growth_score",
    "valuation_score",
    "financial_risk_score",
    "fundamental_quality_score",
    "fundamental_grade",
    "fundamental_style",
    "fundamental_risk_level",
    "fundamental_reason",
]

FIELD_ALIASES = {
    "revenue": ("revenue", "operating_revenue", "营业收入", "营收"),
    "net_profit": ("net_profit", "profit", "归母净利润", "净利润"),
    "gross_margin": ("gross_margin", "gross_profit_margin", "毛利率"),
    "roe": ("roe", "return_on_equity", "净资产收益率", "ROE"),
    "pe": ("pe", "pe_ratio", "市盈率", "PE"),
    "pb": ("pb", "pb_ratio", "市净率", "PB"),
    "ps": ("ps", "ps_ratio", "市销率", "PS"),
    "debt_ratio": ("debt_ratio", "asset_liability_ratio", "资产负债率"),
    "operating_cashflow": ("operating_cashflow", "operating_cash_flow", "经营现金流"),
    "revenue_growth": ("revenue_growth", "revenue_yoy", "营收增长率"),
    "profit_growth": ("profit_growth", "net_profit_growth", "净利润增长率"),
    "market_cap": ("market_cap", "total_market_cap", "总市值"),
    "industry": ("industry", "行业"),
}

_EMPTY_VALUES = {"", "-", "--", "nan", "none", "null", "n/a", "na"}


def _copy_row(row):
    if hasattr(row, "to_dict"):
        return copy.deepcopy(row.to_dict())
    if isinstance(row, dict):
        return copy.deepcopy(row)
    return {}


def normalize_fundamental_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None

    text = str(value).strip()
    if text.lower() in _EMPTY_VALUES:
        return None

    multiplier = 1.0
    if "%" in text:
        multiplier *= 0.01
    if "亿" in text:
        multiplier *= 100_000_000
    elif "万" in text:
        multiplier *= 10_000

    cleaned = (
        text.replace(",", "")
        .replace("%", "")
        .replace("人民币", "")
        .replace("元", "")
        .replace("亿元", "")
        .replace("万元", "")
        .replace("亿", "")
        .replace("万", "")
        .strip()
    )
    if cleaned.lower() in _EMPTY_VALUES:
        return None
    try:
        number = float(cleaned)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return round(number * multiplier, 12)


def _find_alias(row, aliases):
    if not isinstance(row, dict):
        return None
    lowered = {str(key).lower(): key for key in row}
    for alias in aliases:
        if alias in row:
            return alias
        matched = lowered.get(str(alias).lower())
        if matched is not None:
            return matched
    return None


def _normalize_field(field, value):
    if field == "industry":
        if value is None:
            return None
        text = str(value).strip()
        return text if text and text.lower() not in _EMPTY_VALUES else None
    return normalize_fundamental_value(value)


def detect_fundamental_fields(row):
    data = _copy_row(row)
    detected = {}
    for field in FUNDAMENTAL_FIELDS:
        source_key = _find_alias(data, FIELD_ALIASES[field])
        if source_key is None:
            continue
        value = _normalize_field(field, data.get(source_key))
        if value is not None:
            detected[field] = value
    return detected


def build_fundamental_data_quality(row):
    detected = detect_fundamental_fields(row)
    detected_fields = sorted(detected)
    missing_fields = [field for field in FUNDAMENTAL_FIELDS if field not in detected]
    detected_count = len(detected_fields)

    if detected_count == 0:
        quality_label = "no_fundamental_data"
    elif detected_count >= 9:
        quality_label = "sufficient_fundamental_data"
    elif detected_count >= 4:
        quality_label = "partial_fundamental_data"
    else:
        quality_label = "insufficient_fundamental_data"

    return {
        "fundamental_available": detected_count > 0,
        "fundamental_fields_detected": detected_fields,
        "missing_fundamental_fields": missing_fields,
        "fundamental_data_quality_label": quality_label,
    }


def build_fundamental_base_summary(row):
    quality = build_fundamental_data_quality(row)
    label = quality["fundamental_data_quality_label"]
    if label == "sufficient_fundamental_data":
        return "基本面字段较完整，可支持后续盈利能力、成长性、估值和财务风险分析。"
    if label == "partial_fundamental_data":
        return "基本面字段部分缺失，当前仅适合做粗略基本面观察。"
    if label == "insufficient_fundamental_data":
        return "基本面字段较少，当前基本面判断可信度有限。"
    return "未检测到有效基本面字段，暂不能支持基本面分析。"


def _score_value(value):
    if isinstance(value, (int, float)) and math.isfinite(value):
        return value
    return None


def _clamp_score(value):
    return max(0, min(100, int(round(value))))


def _detected(row):
    return detect_fundamental_fields(row)


def build_profitability_score(row):
    data = _detected(row)
    if not any(field in data for field in ("roe", "gross_margin", "net_profit", "operating_cashflow")):
        return None
    score = 50
    roe = _score_value(data.get("roe"))
    gross_margin = _score_value(data.get("gross_margin"))
    net_profit = _score_value(data.get("net_profit"))
    cashflow = _score_value(data.get("operating_cashflow"))
    if roe is not None:
        score += 15 if roe >= 0.15 else 8 if roe >= 0.08 else -15 if roe < 0 else 0
    if gross_margin is not None:
        score += 12 if gross_margin >= 0.35 else 6 if gross_margin >= 0.20 else -8 if gross_margin < 0.10 else 0
    if net_profit is not None:
        score += 10 if net_profit > 0 else -20
    if cashflow is not None:
        score += 10 if cashflow > 0 else -18
    return _clamp_score(score)


def build_growth_score(row):
    data = _detected(row)
    if not any(field in data for field in ("revenue_growth", "profit_growth")):
        return None
    score = 50
    revenue_growth = _score_value(data.get("revenue_growth"))
    profit_growth = _score_value(data.get("profit_growth"))
    if revenue_growth is not None:
        score += 15 if revenue_growth >= 0.15 else 8 if revenue_growth > 0 else -15
    if profit_growth is not None:
        score += 18 if profit_growth >= 0.20 else 10 if profit_growth > 0 else -20
    if revenue_growth is not None and profit_growth is not None and revenue_growth > 0 and profit_growth > 0:
        score += 8
    return _clamp_score(score)


def build_valuation_score(row):
    data = _detected(row)
    if not any(field in data for field in ("pe", "pb", "ps")):
        return None
    score = 55
    pe = _score_value(data.get("pe"))
    pb = _score_value(data.get("pb"))
    ps = _score_value(data.get("ps"))
    if pe is not None:
        score += 12 if 0 < pe <= 25 else 4 if 25 < pe <= 45 else -18 if pe <= 0 or pe > 80 else -8
    if pb is not None:
        score += 8 if 0 < pb <= 3 else -10 if pb <= 0 or pb > 8 else 0
    if ps is not None:
        score += 8 if 0 < ps <= 5 else -10 if ps <= 0 or ps > 15 else 0
    return _clamp_score(score)


def build_financial_risk_score(row):
    data = _detected(row)
    if not any(field in data for field in ("debt_ratio", "operating_cashflow", "net_profit")):
        return None
    score = 55
    debt_ratio = _score_value(data.get("debt_ratio"))
    cashflow = _score_value(data.get("operating_cashflow"))
    net_profit = _score_value(data.get("net_profit"))
    if debt_ratio is not None:
        score += 15 if 0 <= debt_ratio <= 0.55 else -10 if debt_ratio <= 0.75 else -25
    if cashflow is not None:
        score += 12 if cashflow > 0 else -22
    if net_profit is not None:
        score += 8 if net_profit > 0 else -20
    return _clamp_score(score)


def _quality_cap(quality_label):
    if quality_label == "sufficient_fundamental_data":
        return 100
    if quality_label == "partial_fundamental_data":
        return 75
    if quality_label == "insufficient_fundamental_data":
        return 55
    return None


def _average(scores):
    values = [score for score in scores if isinstance(score, int)]
    if not values:
        return None
    return sum(values) / len(values)


def _fundamental_risk_level(profile):
    if profile["fundamental_data_quality_label"] == "no_fundamental_data":
        return "unknown"
    risk_score = profile.get("financial_risk_score")
    profitability = profile.get("profitability_score")
    if risk_score is not None and risk_score < 40:
        return "high"
    if profitability is not None and profitability < 35:
        return "high"
    if profile["fundamental_data_quality_label"] == "insufficient_fundamental_data":
        return "unknown"
    if risk_score is not None and risk_score >= 70:
        return "low"
    return "medium"


def _fundamental_quality_score(profile):
    cap = _quality_cap(profile["fundamental_data_quality_label"])
    if cap is None:
        return None
    base = _average(
        [
            profile.get("profitability_score"),
            profile.get("growth_score"),
            profile.get("valuation_score"),
            profile.get("financial_risk_score"),
        ]
    )
    if base is None:
        return None
    if profile["fundamental_data_quality_label"] == "partial_fundamental_data":
        base -= 5
    elif profile["fundamental_data_quality_label"] == "insufficient_fundamental_data":
        base -= 15
    return min(cap, _clamp_score(base))


def _fundamental_grade(profile):
    score = profile.get("fundamental_quality_score")
    if score is None:
        return "D"
    if score >= 75 and profile.get("fundamental_risk_level") != "high":
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    return "D"


def _fundamental_style(profile, row):
    if profile["fundamental_data_quality_label"] in {"no_fundamental_data", "insufficient_fundamental_data"}:
        return "insufficient_data"
    data = _detected(row)
    pe = _score_value(data.get("pe"))
    pb = _score_value(data.get("pb"))
    revenue_growth = _score_value(data.get("revenue_growth"))
    profit_growth = _score_value(data.get("profit_growth"))
    profitability = profile.get("profitability_score")
    growth = profile.get("growth_score")
    valuation = profile.get("valuation_score")
    risk = profile.get("fundamental_risk_level")
    high_growth = any(value is not None and value >= 0.20 for value in (revenue_growth, profit_growth))
    high_valuation = (pe is not None and pe > 60) or (pb is not None and pb > 8)
    if high_growth and high_valuation:
        return "high_growth_high_valuation"
    if profitability is not None and profitability >= 70 and growth is not None and growth >= 65:
        return "quality_growth"
    if profitability is not None and profitability >= 65 and valuation is not None and valuation >= 60:
        return "profitable_value"
    if risk == "low" and profitability is not None and profitability >= 60:
        return "stable_quality"
    if profile.get("fundamental_quality_score") is not None and profile["fundamental_quality_score"] < 45:
        return "weak_fundamental"
    return "stable_quality"


def _fundamental_reason(profile):
    if profile["fundamental_data_quality_label"] == "no_fundamental_data":
        return "未检测到有效基本面字段，当前不能形成稳定的基本面观察。"
    if profile["fundamental_data_quality_label"] == "insufficient_fundamental_data":
        return "基本面字段不足，当前仅适合做低可信度的初步观察。"
    if profile.get("fundamental_risk_level") == "high":
        return "基本面存在盈利、现金流或负债压力，需结合原始财务字段继续核查。"
    if profile.get("fundamental_style") == "high_growth_high_valuation":
        return "成长性字段较强，但估值水平偏高，当前适合做基本面观察对比。"
    if profile.get("fundamental_grade") == "A":
        return "盈利能力、成长性和财务风险字段整体较好，可支持后续基本面研究。"
    if profile.get("fundamental_grade") == "B":
        return "基本面存在部分支撑项，但仍有估值、成长或风险观察点。"
    return "基本面表现一般或字段存在缺口，当前适合做基础质量复核。"


def build_fundamental_profile(row):
    profile = build_fundamental_data_quality(row)
    profile["fundamental_summary_base"] = build_fundamental_base_summary(row)
    profile["profitability_score"] = build_profitability_score(row)
    profile["growth_score"] = build_growth_score(row)
    profile["valuation_score"] = build_valuation_score(row)
    profile["financial_risk_score"] = build_financial_risk_score(row)
    profile["fundamental_risk_level"] = _fundamental_risk_level(profile)
    profile["fundamental_quality_score"] = _fundamental_quality_score(profile)
    profile["fundamental_grade"] = _fundamental_grade(profile)
    profile["fundamental_style"] = _fundamental_style(profile, row)
    profile["fundamental_reason"] = _fundamental_reason(profile)
    return profile


__all__ = [
    "FUNDAMENTAL_FIELDS",
    "FUNDAMENTAL_PROFILE_FIELDS",
    "build_fundamental_base_summary",
    "build_fundamental_data_quality",
    "build_fundamental_profile",
    "build_financial_risk_score",
    "build_growth_score",
    "build_profitability_score",
    "build_valuation_score",
    "detect_fundamental_fields",
    "normalize_fundamental_value",
]
