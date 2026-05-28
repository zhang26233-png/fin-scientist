"""Risk-label helpers for research-candidate review."""

import math

import pandas as pd


def _to_number(value):
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").replace("%", "").strip()
    try:
        return float(text)
    except ValueError:
        return math.nan


def _get_metric(metrics, key):
    return metrics.get(key) if isinstance(metrics, dict) else None


def detect_high_volatility_risk(metrics, threshold=0.80):
    value = _to_number(_get_metric(metrics, "年化波动率"))
    if math.isnan(value) or value <= threshold:
        return []
    return [{"tag": "高波动风险", "message": "年化波动率较高，需评估样本区间和风险承受能力。"}]


def detect_consecutive_rise_risk(metrics, threshold=0.40):
    value = _to_number(_get_metric(metrics, "近 20 日涨跌幅"))
    if math.isnan(value) or value <= threshold:
        return []
    return [{"tag": "短期涨幅风险", "message": "近 20 日涨幅较高，需核查事件驱动和回撤压力。"}]


def detect_missing_data_risk(metrics):
    if not isinstance(metrics, dict):
        return [{"tag": "数据缺失风险", "message": "指标输入为空，当前风险识别不完整。"}]

    risks = []
    if metrics.get("成交量数据缺失"):
        risks.append({"tag": "数据缺失风险", "message": "成交量字段缺失，量能观察不完整。"})
    if metrics.get("有效交易日数量", 0) < 60:
        risks.append({"tag": "样本不足风险", "message": "有效交易日数量不足，指标稳定性有限。"})
    if metrics.get("基本面字段缺失较多"):
        risks.append({"tag": "基本面缺失风险", "message": "基本面字段缺失较多，需进一步核验财务数据。"})
    return risks


def detect_liquidity_risk(metrics, min_volume_ratio=0.8):
    value = _to_number(_get_metric(metrics, "成交量放大倍数"))
    if math.isnan(value):
        return [{"tag": "流动性观察不足", "message": "成交量放大倍数字段缺失，流动性观察不完整。"}]
    if value < min_volume_ratio:
        return [{"tag": "流动性风险", "message": "近期成交活跃度偏低，需核查成交连续性。"}]
    return []


def build_risk_labels(metrics):
    risks = []
    risks.extend(detect_high_volatility_risk(metrics))
    risks.extend(detect_consecutive_rise_risk(metrics))
    risks.extend(detect_missing_data_risk(metrics))
    risks.extend(detect_liquidity_risk(metrics))
    if not risks:
        risks.append({"tag": "常规核验", "message": "未触发主要风险阈值，仍需结合数据质量和基本面继续研究。"})
    return risks


def risk_tags_to_text(risks):
    if not isinstance(risks, list):
        return ""
    return "；".join(item.get("message", "") for item in risks if isinstance(item, dict) and item.get("message"))


__all__ = [
    "build_risk_labels",
    "detect_consecutive_rise_risk",
    "detect_high_volatility_risk",
    "detect_liquidity_risk",
    "detect_missing_data_risk",
    "risk_tags_to_text",
]
