"""Read-only fundamental diagnostics built from preview fields."""

import copy
import math

import pandas as pd

from strategy.fundamental import detect_fundamental_fields, normalize_fundamental_value


FUNDAMENTAL_DIAGNOSTIC_FIELDS = [
    "fundamental_diagnostics",
    "profitability_diagnostics",
    "growth_diagnostics",
    "valuation_diagnostics",
    "financial_risk_diagnostics",
    "fundamental_watch_points",
    "fundamental_strength_points",
    "fundamental_weakness_points",
    "fundamental_diagnostics_summary",
]

FORBIDDEN_DIAGNOSTIC_WORDS = (
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
    "\u63a8\u8350\u4e70\u5165",
    "\u76ee\u6807\u4ef7",
    "\u77ed\u7ebf\u4ecb\u5165",
    "\u6284\u5e95",
    "\u6b62\u76c8",
    "\u6b62\u635f",
)


def _source_to_frame(source):
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, pd.Series):
        return pd.DataFrame([copy.deepcopy(source.to_dict())])
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    return pd.DataFrame()


def _row_dict(row):
    if hasattr(row, "to_dict"):
        return copy.deepcopy(row.to_dict())
    if isinstance(row, dict):
        return copy.deepcopy(row)
    return {}


def _safe_number(value):
    number = normalize_fundamental_value(value)
    if number is None:
        return None
    try:
        number = float(number)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _score(row, key):
    value = _safe_number(row.get(key))
    if value is None:
        return None
    return max(0, min(100, int(round(value))))


def _level_from_score(score, high="strong", middle="moderate", low="weak", missing="insufficient_data"):
    if score is None:
        return missing
    if score >= 70:
        return high
    if score >= 45:
        return middle
    return low


def _missing(data, fields):
    return [field for field in fields if field not in data]


def _clean_list(items, limit=3):
    result = []
    for item in items:
        if not item or item in result:
            continue
        result.append(item)
        if len(result) >= limit:
            break
    return result


def _sanitize_text(text):
    output = str(text)
    for word in FORBIDDEN_DIAGNOSTIC_WORDS:
        output = output.replace(word, "研究")
    return output


def build_profitability_diagnostics(row):
    row_data = _row_dict(row)
    data = detect_fundamental_fields(row_data)
    fields = ("roe", "gross_margin", "net_profit", "operating_cashflow")
    score = _score(row_data, "profitability_score")
    relative = row_data.get("relative_profitability_label")
    positives = []
    negatives = []

    roe = data.get("roe")
    gross_margin = data.get("gross_margin")
    net_profit = data.get("net_profit")
    cashflow = data.get("operating_cashflow")
    if isinstance(roe, (int, float)) and roe >= 0.12:
        positives.append("ROE表现较好")
    elif isinstance(roe, (int, float)) and roe < 0:
        negatives.append("ROE为负")
    if isinstance(gross_margin, (int, float)) and gross_margin >= 0.30:
        positives.append("毛利率表现较好")
    elif isinstance(gross_margin, (int, float)) and gross_margin < 0.10:
        negatives.append("毛利率偏低")
    if isinstance(net_profit, (int, float)) and net_profit > 0:
        positives.append("净利润为正")
    elif isinstance(net_profit, (int, float)) and net_profit < 0:
        negatives.append("净利润为负")
    if isinstance(cashflow, (int, float)) and cashflow > 0:
        positives.append("经营现金流为正")
    elif isinstance(cashflow, (int, float)) and cashflow < 0:
        negatives.append("经营现金流为负")
    if relative in {"industry_leading", "above_industry_average"}:
        positives.append("盈利能力在同行内相对靠前")
    elif relative == "below_industry_average":
        negatives.append("盈利能力低于同行平均观察水平")

    level = _level_from_score(score, high="high_profitability", middle="normal_profitability", low="weak_profitability")
    missing = _missing(data, fields)
    if score is None and not positives and not negatives:
        explanation = "盈利能力字段不足，当前只能形成低可信度观察。"
    elif positives:
        explanation = "盈利能力评分具备一定支撑，主要来自" + "、".join(positives[:2]) + "。"
    else:
        explanation = "盈利能力评分承压，主要受" + "、".join(negatives[:2] or ["关键字段不足"]) + "影响。"
    if missing:
        explanation += " 部分字段缺失，结论仍需进一步确认。"
    return {
        "score": score,
        "level": level,
        "positive_signals": positives,
        "negative_signals": negatives,
        "missing_fields": missing,
        "explanation": _sanitize_text(explanation),
    }


def build_growth_diagnostics(row):
    row_data = _row_dict(row)
    data = detect_fundamental_fields(row_data)
    score = _score(row_data, "growth_score")
    relative = row_data.get("relative_growth_label")
    positives = []
    negatives = []
    revenue_growth = data.get("revenue_growth")
    profit_growth = data.get("profit_growth")

    if isinstance(revenue_growth, (int, float)) and revenue_growth > 0:
        positives.append("营收增长为正")
    elif isinstance(revenue_growth, (int, float)) and revenue_growth < 0:
        negatives.append("营收增长为负")
    if isinstance(profit_growth, (int, float)) and profit_growth > 0:
        positives.append("利润增长为正")
    elif isinstance(profit_growth, (int, float)) and profit_growth < 0:
        negatives.append("利润增长为负")
    if relative == "high_relative_growth":
        positives.append("成长性在同行内相对靠前")
    elif relative in {"weak_relative_growth", "negative_relative_growth"}:
        negatives.append("成长性在同行内相对偏弱")

    if not any(field in data for field in ("revenue_growth", "profit_growth")):
        level = "insufficient_growth_data"
    elif any(value is not None and value < 0 for value in (revenue_growth, profit_growth)):
        level = "negative_growth"
    elif score is not None and score >= 70:
        level = "high_growth"
    elif score is not None and score >= 50:
        level = "stable_growth"
    else:
        level = "weak_growth"

    if level == "insufficient_growth_data":
        explanation = "成长性字段不足，当前不能形成稳定成长观察。"
    elif positives:
        explanation = "成长性具备一定支撑，主要来自" + "、".join(positives[:2]) + "。"
    else:
        explanation = "成长性表现偏弱，主要受" + "、".join(negatives[:2] or ["增长字段不足"]) + "影响。"
    return {
        "score": score,
        "level": level,
        "positive_signals": positives,
        "negative_signals": negatives,
        "missing_fields": _missing(data, ("revenue_growth", "profit_growth")),
        "explanation": _sanitize_text(explanation),
    }


def build_valuation_diagnostics(row):
    row_data = _row_dict(row)
    data = detect_fundamental_fields(row_data)
    score = _score(row_data, "valuation_score")
    relative = row_data.get("relative_valuation_label")
    positives = []
    negatives = []
    pe = data.get("pe")
    pb = data.get("pb")
    ps = data.get("ps")

    if relative == "relatively_expensive":
        level = "valuation_expensive"
        negatives.append("估值水平在同行中偏高")
    elif relative == "relatively_cheap_but_needs_check":
        level = "valuation_low_but_needs_quality_check"
        negatives.append("估值偏低但需要核查盈利和成长质量")
    elif relative == "abnormal_valuation_data" or any(isinstance(value, (int, float)) and value <= 0 for value in (pe, pb, ps)):
        level = "valuation_abnormal"
        negatives.append("估值字段存在异常或不可直接比较")
    elif not any(field in data for field in ("pe", "pb", "ps")):
        level = "insufficient_valuation_data"
    elif score is not None and score >= 55:
        level = "valuation_reasonable"
        positives.append("估值字段处于可比较区间")
    else:
        level = "valuation_expensive"
        negatives.append("估值评分偏低")

    if level == "insufficient_valuation_data":
        explanation = "估值字段不足，当前不能形成稳定估值观察。"
    elif positives:
        explanation = "估值观察相对平衡，主要来自" + "、".join(positives[:2]) + "。"
    else:
        explanation = "估值观察存在压力，主要来自" + "、".join(negatives[:2]) + "。"
    return {
        "score": score,
        "level": level,
        "positive_signals": positives,
        "negative_signals": negatives,
        "missing_fields": _missing(data, ("pe", "pb", "ps")),
        "explanation": _sanitize_text(explanation),
    }


def build_financial_risk_diagnostics(row):
    row_data = _row_dict(row)
    data = detect_fundamental_fields(row_data)
    score = _score(row_data, "financial_risk_score")
    relative = row_data.get("relative_financial_risk_label")
    positives = []
    negatives = []
    debt = data.get("debt_ratio")
    cashflow = data.get("operating_cashflow")
    profit = data.get("net_profit")

    if isinstance(debt, (int, float)) and debt <= 0.55:
        positives.append("负债水平相对可控")
    elif isinstance(debt, (int, float)) and debt > 0.75:
        negatives.append("负债水平偏高")
    if isinstance(cashflow, (int, float)) and cashflow > 0:
        positives.append("经营现金流为正")
    elif isinstance(cashflow, (int, float)) and cashflow < 0:
        negatives.append("经营现金流偏弱")
    if isinstance(profit, (int, float)) and profit > 0:
        positives.append("净利润为正")
    elif isinstance(profit, (int, float)) and profit < 0:
        negatives.append("净利润为负")
    if relative == "higher_than_industry_risk":
        negatives.append("财务风险在同行中相对偏高")
    elif relative == "lower_than_industry_risk":
        positives.append("财务风险低于同行观察水平")

    if not any(field in data for field in ("debt_ratio", "operating_cashflow", "net_profit")):
        level = "insufficient_risk_data"
    elif isinstance(debt, (int, float)) and debt > 0.75:
        level = "high_debt_pressure"
    elif isinstance(cashflow, (int, float)) and cashflow < 0:
        level = "weak_cashflow"
    elif isinstance(profit, (int, float)) and profit < 0:
        level = "loss_or_negative_profit"
    elif score is not None and score >= 70:
        level = "low_financial_risk"
    else:
        level = "normal_financial_risk"

    if level == "insufficient_risk_data":
        explanation = "财务风险字段不足，当前只能做基础风险观察。"
    elif negatives:
        explanation = "财务风险需要继续核查，主要来自" + "、".join(negatives[:2]) + "。"
    else:
        explanation = "财务风险观察相对平稳，主要来自" + "、".join(positives[:2] or ["风险字段未见明显压力"]) + "。"
    return {
        "score": score,
        "level": level,
        "positive_signals": positives,
        "negative_signals": negatives,
        "missing_fields": _missing(data, ("debt_ratio", "operating_cashflow", "net_profit")),
        "explanation": _sanitize_text(explanation),
    }


def _strength_points(row, diagnostics):
    row_data = _row_dict(row)
    points = []
    if diagnostics["profitability"]["level"] in {"high_profitability", "normal_profitability"} and row_data.get(
        "relative_profitability_label"
    ) in {"industry_leading", "above_industry_average", None, ""}:
        points.append("盈利能力具备一定支撑")
    if diagnostics["growth"]["level"] in {"high_growth", "stable_growth"}:
        points.append("成长性表现较好")
    if row_data.get("industry_relative_quality_label") == "industry_relative_strong":
        points.append("行业内相对质量较好")
    if diagnostics["valuation"]["level"] == "valuation_reasonable":
        points.append("估值与基本面字段相对匹配")
    return _clean_list(points)


def _weakness_points(row, diagnostics):
    row_data = _row_dict(row)
    points = []
    if diagnostics["valuation"]["level"] in {"valuation_expensive", "valuation_abnormal"}:
        points.append("估值相对偏高或可比性不足")
    if diagnostics["financial_risk"]["level"] in {"high_debt_pressure", "weak_cashflow", "loss_or_negative_profit"}:
        points.append("财务风险字段存在压力")
    if diagnostics["growth"]["level"] in {"weak_growth", "negative_growth", "insufficient_growth_data"}:
        points.append("成长数据偏弱或不足")
    if row_data.get("industry_relative_quality_label") == "industry_relative_weak":
        points.append("行业相对优势不明显")
    return _clean_list(points)


def _watch_points(row, diagnostics):
    data = detect_fundamental_fields(_row_dict(row))
    points = []
    if diagnostics["growth"]["level"] in {"high_growth", "stable_growth"}:
        points.append("需要进一步核查利润增长是否可持续")
    if diagnostics["valuation"]["level"] in {"valuation_expensive", "valuation_low_but_needs_quality_check"}:
        points.append("需要结合行业景气度判断估值合理性")
    if "operating_cashflow" in data or "net_profit" in data:
        points.append("需要关注经营现金流与净利润是否匹配")
    if _row_dict(row).get("industry_relative_quality_label") == "insufficient_industry_data":
        points.append("需要确认行业分类是否准确")
    if len(detect_fundamental_fields(_row_dict(row))) < 4:
        points.append("需要补充更多基本面字段")
    return _clean_list(points)


def _summary(row, strengths, weaknesses, watch_points):
    row_data = _row_dict(row)
    if row_data.get("fundamental_data_quality_label") in {"no_fundamental_data", "insufficient_fundamental_data"}:
        return "基本面字段不足，当前诊断仅适合做低可信度研究观察。"
    if strengths and weaknesses:
        return "该标的基本面具备一定支撑，但" + weaknesses[0] + "，后续需要继续核查关键字段。"
    if strengths:
        return "该标的基本面存在相对支撑点，可结合行业相对位置和原始财务字段继续观察。"
    if weaknesses:
        return "该标的基本面存在需要复核的薄弱点，当前更适合做质量和风险核查。"
    if watch_points:
        return "该标的基本面结论较中性，后续重点在于补充字段和核查数据一致性。"
    return "基本面诊断信息有限，当前仅能形成基础研究观察。"


def build_fundamental_diagnostics_row(row):
    row_data = _row_dict(row)
    profitability = build_profitability_diagnostics(row_data)
    growth = build_growth_diagnostics(row_data)
    valuation = build_valuation_diagnostics(row_data)
    financial_risk = build_financial_risk_diagnostics(row_data)
    diagnostics = {
        "profitability": profitability,
        "growth": growth,
        "valuation": valuation,
        "financial_risk": financial_risk,
    }
    strengths = _strength_points(row_data, diagnostics)
    weaknesses = _weakness_points(row_data, diagnostics)
    watch_points = _watch_points(row_data, diagnostics)
    summary = _sanitize_text(_summary(row_data, strengths, weaknesses, watch_points))
    warnings = []
    if row_data.get("industry_relative_quality_label") == "insufficient_industry_data":
        warnings.append("industry_relative_data_insufficient")
    if row_data.get("fundamental_data_quality_label") in {"no_fundamental_data", "insufficient_fundamental_data", None}:
        warnings.append("fundamental_data_insufficient")

    full = {
        "profitability": profitability,
        "growth": growth,
        "valuation": valuation,
        "financial_risk": financial_risk,
        "industry_relative": {
            "relative_profitability_label": row_data.get("relative_profitability_label"),
            "relative_growth_label": row_data.get("relative_growth_label"),
            "relative_valuation_label": row_data.get("relative_valuation_label"),
            "relative_financial_risk_label": row_data.get("relative_financial_risk_label"),
            "industry_relative_quality_label": row_data.get("industry_relative_quality_label"),
            "industry_relative_summary": row_data.get("industry_relative_summary"),
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "watch_points": watch_points,
        "summary": summary,
        "warnings": warnings,
        "metadata": {
            "read_only": True,
            "uses_real_data_source": False,
            "ranking_changed": False,
        },
    }
    return {
        "fundamental_diagnostics": full,
        "profitability_diagnostics": profitability,
        "growth_diagnostics": growth,
        "valuation_diagnostics": valuation,
        "financial_risk_diagnostics": financial_risk,
        "fundamental_watch_points": watch_points,
        "fundamental_strength_points": strengths,
        "fundamental_weakness_points": weaknesses,
        "fundamental_diagnostics_summary": summary,
    }


def build_fundamental_diagnostics_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=FUNDAMENTAL_DIAGNOSTIC_FIELDS)
    rows = [build_fundamental_diagnostics_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=FUNDAMENTAL_DIAGNOSTIC_FIELDS)


__all__ = [
    "FUNDAMENTAL_DIAGNOSTIC_FIELDS",
    "build_financial_risk_diagnostics",
    "build_fundamental_diagnostics_profile",
    "build_fundamental_diagnostics_row",
    "build_growth_diagnostics",
    "build_profitability_diagnostics",
    "build_valuation_diagnostics",
]
