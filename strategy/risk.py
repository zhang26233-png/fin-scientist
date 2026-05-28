"""Risk-label helpers for research-candidate review."""

import math

import pandas as pd


def _to_number(value):
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
    if "%" in str(value):
        number = number / 100
    return number if math.isfinite(number) else math.nan


def _get_metric(metrics, key):
    return metrics.get(key) if isinstance(metrics, dict) else None


def _metric_any(metrics, keys):
    if not isinstance(metrics, dict):
        return math.nan
    for key in keys:
        value = _to_number(metrics.get(key))
        if not math.isnan(value):
            return value
    return math.nan


def detect_high_volatility_risk(metrics, threshold=0.80):
    volatility = _metric_any(metrics, ("年化波动率", "volatility", "annual_volatility"))
    amplitude = _metric_any(metrics, ("振幅", "amplitude"))
    if (math.isnan(volatility) or volatility <= threshold) and (math.isnan(amplitude) or amplitude <= 0.12):
        return []
    return [{"tag": "高波动风险", "code": "high_volatility", "message": "波动或振幅较高，需评估样本区间和风险承受能力。"}]


def detect_consecutive_rise_risk(metrics, threshold=0.40):
    value = _metric_any(metrics, ("近 20 日涨跌幅", "return_20d", "20d_return"))
    short_return = _metric_any(metrics, ("近 5 日涨跌幅", "pct_chg", "recent_return", "return_5d"))
    if (math.isnan(value) or value <= threshold) and (math.isnan(short_return) or short_return <= 0.12):
        return []
    return [{"tag": "短期涨幅风险", "code": "extreme_upside_return", "message": "短期涨幅较高，需核查事件驱动和回撤压力。"}]


def detect_volume_downside_risk(metrics, downside_threshold=-0.05, volume_ratio_threshold=1.3):
    recent_return = _metric_any(metrics, ("近 5 日涨跌幅", "pct_chg", "recent_return", "return_5d", "近 20 日涨跌幅"))
    volume_ratio = _metric_any(metrics, ("成交量放大倍数", "量比", "volume_ratio"))
    if math.isnan(recent_return) or math.isnan(volume_ratio):
        return []
    if recent_return <= downside_threshold and volume_ratio >= volume_ratio_threshold:
        return [{"tag": "放量下跌风险", "code": "volume_downside_risk", "message": "下跌伴随成交放大，需核查量价背离和数据口径。"}]
    return []


def detect_turnover_overheat_risk(metrics, high_threshold=0.15):
    turnover = _metric_any(metrics, ("换手率", "turnover", "turnover_rate"))
    if math.isnan(turnover) or turnover <= high_threshold:
        return []
    return [{"tag": "换手过热风险", "code": "overheated_turnover", "message": "换手率较高，需区分适度活跃与短线过热。"}]


def detect_missing_data_risk(metrics):
    if not isinstance(metrics, dict):
        return [{"tag": "数据缺失风险", "code": "insufficient_factor_data", "message": "指标输入为空，当前风险识别不完整。"}]

    risks = []
    if metrics.get("成交量数据缺失"):
        risks.append({"tag": "数据缺失风险", "code": "missing_volume_fields", "message": "成交量字段缺失，量能观察不完整。"})
    if metrics.get("有效交易日数量", 0) < 60:
        risks.append({"tag": "样本不足风险", "code": "insufficient_factor_data", "message": "有效交易日数量不足，指标稳定性有限。"})
    if metrics.get("基本面字段缺失较多"):
        risks.append({"tag": "基本面缺失风险", "code": "insufficient_factor_data", "message": "基本面字段缺失较多，需进一步核验财务数据。"})
    return risks


def detect_liquidity_risk(metrics, min_volume_ratio=0.8):
    value = _metric_any(metrics, ("成交量放大倍数", "量比", "volume_ratio"))
    amount = _metric_any(metrics, ("成交额", "amount", "turnover_amount"))
    volume = _metric_any(metrics, ("成交量", "volume"))
    turnover = _metric_any(metrics, ("换手率", "turnover", "turnover_rate"))
    if math.isnan(value):
        return [{"tag": "流动性观察不足", "code": "missing_volume_fields", "message": "成交量放大倍数字段缺失，流动性观察不完整。"}]
    if value < min_volume_ratio or (not math.isnan(amount) and amount < 5_000_000) or (not math.isnan(volume) and volume < 100_000) or (not math.isnan(turnover) and turnover < 0.003):
        return [{"tag": "流动性风险", "code": "low_liquidity", "message": "近期成交活跃度偏低，需核查成交连续性。"}]
    return []


def build_risk_labels(metrics):
    risks = []
    risks.extend(detect_high_volatility_risk(metrics))
    risks.extend(detect_consecutive_rise_risk(metrics))
    risks.extend(detect_volume_downside_risk(metrics))
    risks.extend(detect_turnover_overheat_risk(metrics))
    risks.extend(detect_missing_data_risk(metrics))
    risks.extend(detect_liquidity_risk(metrics))
    if not risks:
        risks.append({"tag": "常规核验", "code": "routine_review", "message": "未触发主要风险阈值，仍需结合数据质量和基本面继续研究。"})
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
    "detect_turnover_overheat_risk",
    "detect_volume_downside_risk",
    "risk_tags_to_text",
]
