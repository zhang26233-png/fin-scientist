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


def build_fundamental_profile(row):
    profile = build_fundamental_data_quality(row)
    profile["fundamental_summary_base"] = build_fundamental_base_summary(row)
    return profile


__all__ = [
    "FUNDAMENTAL_FIELDS",
    "FUNDAMENTAL_PROFILE_FIELDS",
    "build_fundamental_base_summary",
    "build_fundamental_data_quality",
    "build_fundamental_profile",
    "detect_fundamental_fields",
    "normalize_fundamental_value",
]
