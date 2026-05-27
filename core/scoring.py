"""Scoring rules for research-priority and quality observations."""

import math

import pandas as pd

MISSING = "??????"


def is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() in {"", MISSING, "??????", "N/A", "None", "nan"}


def to_number(value):
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        return value
    text = str(value).replace(",", "").replace("%", "").strip()
    try:
        return float(text)
    except ValueError:
        return math.nan


def calculate_research_priority_score(metrics):
    if not isinstance(metrics, dict):
        return {"研究优先级评分": "无法评分", "无法评分原因": "指标为空"}
    if metrics.get("无法评分原因"):
        return {"研究优先级评分": "无法评分", "无法评分原因": metrics["无法评分原因"]}
    if metrics.get("有效交易日数量", 0) < 20 or pd.isna(to_number(metrics.get("最新价格"))):
        return {"研究优先级评分": "无法评分", "无法评分原因": "核心价格数据不足"}

    score = 0
    if metrics.get("当前价格是否高于 MA20") is True:
        score += 15
    if metrics.get("当前价格是否高于 MA60") is True:
        score += 15
    if metrics.get("MA20 是否高于 MA60") is True:
        score += 15

    return_20d = to_number(metrics.get("近 20 日涨跌幅"))
    return_60d = to_number(metrics.get("近 60 日涨跌幅"))
    volume_ratio = to_number(metrics.get("成交量放大倍数"))
    max_drawdown = to_number(metrics.get("最大回撤"))
    annual_volatility = to_number(metrics.get("年化波动率"))

    if not pd.isna(return_20d) and return_20d > 0.10:
        score += 10
    if not pd.isna(return_60d) and return_60d > 0.20:
        score += 10
    if not pd.isna(volume_ratio) and volume_ratio > 1.3:
        score += 10
    if not pd.isna(volume_ratio) and volume_ratio > 1.8:
        score += 5

    if not pd.isna(return_20d) and return_20d > 0.40:
        score -= 15
    if not pd.isna(max_drawdown) and abs(max_drawdown) > 0.35:
        score -= 15
    if not pd.isna(annual_volatility) and annual_volatility > 0.80:
        score -= 10
    if metrics.get("有效交易日数量", 0) < 60:
        score -= 30
    if metrics.get("成交量数据缺失"):
        score -= 20
    if metrics.get("数据质量") == "数据不足，请谨慎使用":
        score -= 20

    return {"研究优先级评分": max(0, min(100, int(score))), "无法评分原因": ""}


FUNDAMENTAL_FIELDS = [
    "market_cap",
    "pe_ttm",
    "pb",
    "roe",
    "revenue_yoy",
    "net_profit_yoy",
    "gross_margin",
    "net_margin",
    "debt_asset_ratio",
    "dividend_yield",
]


def calculate_fundamental_quality_score(fundamental_data):
    if not isinstance(fundamental_data, dict):
        return "无法评分"
    available_count = sum(0 if is_missing(fundamental_data.get(field)) else 1 for field in FUNDAMENTAL_FIELDS)
    if available_count == 0:
        return "无法评分"

    score = 0
    roe = to_number(fundamental_data.get("roe"))
    revenue_yoy = to_number(fundamental_data.get("revenue_yoy"))
    net_profit_yoy = to_number(fundamental_data.get("net_profit_yoy"))
    gross_margin = to_number(fundamental_data.get("gross_margin"))
    net_margin = to_number(fundamental_data.get("net_margin"))
    debt_asset_ratio = to_number(fundamental_data.get("debt_asset_ratio"))
    pe_ttm = to_number(fundamental_data.get("pe_ttm"))
    pb = to_number(fundamental_data.get("pb"))
    dividend_yield = to_number(fundamental_data.get("dividend_yield"))

    if not pd.isna(roe) and roe >= 0.15:
        score += 20
    elif not pd.isna(roe) and roe >= 0.10:
        score += 10
    elif not pd.isna(roe) and roe < 0.05:
        score -= 10
    if not pd.isna(revenue_yoy) and revenue_yoy > 0.15:
        score += 10
    elif not pd.isna(revenue_yoy) and revenue_yoy < 0:
        score -= 10
    if not pd.isna(net_profit_yoy) and net_profit_yoy > 0.15:
        score += 10
    elif not pd.isna(net_profit_yoy) and net_profit_yoy < 0:
        score -= 10
    if not pd.isna(gross_margin) and gross_margin > 0.30:
        score += 10
    if not pd.isna(net_margin) and net_margin > 0.10:
        score += 10
    if not pd.isna(debt_asset_ratio) and debt_asset_ratio < 0.50:
        score += 10
    elif not pd.isna(debt_asset_ratio) and debt_asset_ratio > 0.70:
        score -= 10
    if not pd.isna(pe_ttm) and pe_ttm > 80:
        score -= 10
    if not pd.isna(pb) and pb > 10:
        score -= 10
    if not pd.isna(dividend_yield) and dividend_yield > 0.02:
        score += 5
    if available_count < len(FUNDAMENTAL_FIELDS) / 2:
        score -= 20
    return max(0, min(100, int(score)))


def calculate_composite_research_score(research_score, fundamental_score):
    research_number = to_number(research_score)
    fundamental_number = to_number(fundamental_score)
    if not pd.isna(research_number) and not pd.isna(fundamental_number):
        return round(research_number * 0.6 + fundamental_number * 0.4, 1)
    if not pd.isna(research_number):
        return int(research_number)
    if not pd.isna(fundamental_number):
        return int(fundamental_number)
    return "无法评分"



__all__ = [
    "FUNDAMENTAL_FIELDS",
    "calculate_composite_research_score",
    "calculate_fundamental_quality_score",
    "calculate_research_priority_score",
]
