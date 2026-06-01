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
    "fundamental_profile_type",
    "fundamental_conflict_flags",
    "fundamental_conflict_summary",
    "industry_relative_detail",
    "relative_advantage_points",
    "relative_disadvantage_points",
    "relative_position_summary",
    "fundamental_research_questions",
    "fundamental_detail_view",
    "profitability_detail",
    "growth_detail",
    "valuation_detail",
    "financial_risk_detail",
    "fundamental_key_evidence",
    "fundamental_uncertainty_notes",
    "fundamental_confidence_level",
    "fundamental_confidence_score",
    "fundamental_confidence_reasons",
    "fundamental_data_completeness_score",
    "fundamental_industry_comparability_label",
    "fundamental_anomaly_flags",
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


def _limited_questions(items):
    return _clean_list(items, limit=4)[:4]


def _sanitize_text(text):
    output = str(text)
    for word in FORBIDDEN_DIAGNOSTIC_WORDS:
        output = output.replace(word, "研究")
    return output


def _detected_value(row, key):
    return detect_fundamental_fields(_row_dict(row)).get(key)


def _is_high(value, threshold):
    return value is not None and value >= threshold


def _is_low(value, threshold):
    return value is not None and value <= threshold


def build_fundamental_profile_type(row):
    row_data = _row_dict(row)
    data = detect_fundamental_fields(row_data)
    quality_label = row_data.get("fundamental_data_quality_label")
    profitability = _score(row_data, "profitability_score")
    growth = _score(row_data, "growth_score")
    valuation = _score(row_data, "valuation_score")
    risk = _score(row_data, "financial_risk_score")
    quality = _score(row_data, "fundamental_quality_score")
    roe = data.get("roe")
    debt = data.get("debt_ratio")
    cashflow = data.get("operating_cashflow")
    net_profit = data.get("net_profit")
    pe = data.get("pe")
    pb = data.get("pb")
    relative_valuation = row_data.get("relative_valuation_label")

    if quality_label in {"no_fundamental_data", "insufficient_fundamental_data", None}:
        return "insufficient_data"
    if isinstance(cashflow, (int, float)) and cashflow < 0 and (
        (profitability is not None and profitability >= 60) or (isinstance(net_profit, (int, float)) and net_profit > 0)
    ):
        return "cashflow_risk"
    if isinstance(debt, (int, float)) and debt >= 0.75 and (
        (isinstance(roe, (int, float)) and roe >= 0.15) or (profitability is not None and profitability >= 65)
    ):
        return "leverage_pressure"
    if growth is not None and growth >= 75 and (
        relative_valuation == "relatively_expensive"
        or (isinstance(pe, (int, float)) and pe > 60)
        or (isinstance(pb, (int, float)) and pb > 8)
    ):
        return "high_growth_high_valuation"
    if quality is not None and quality < 40:
        return "weak_fundamental"
    if profitability is not None and profitability < 45 and growth is not None and growth >= 55:
        return "turnaround_watch"
    if profitability is not None and profitability >= 70 and growth is not None and growth >= 65 and risk is not None and risk >= 55:
        return "quality_growth"
    if profitability is not None and profitability >= 65 and valuation is not None and valuation >= 60 and growth is not None and growth < 70:
        return "profitable_value"
    if risk is not None and risk < 35:
        return "weak_fundamental"
    return "weak_fundamental" if quality is not None and quality < 50 else "profitable_value"


def build_fundamental_conflicts(row):
    row_data = _row_dict(row)
    data = detect_fundamental_fields(row_data)
    flags = []
    profitability = _score(row_data, "profitability_score")
    growth = _score(row_data, "growth_score")
    valuation = _score(row_data, "valuation_score")
    revenue_growth = data.get("revenue_growth")
    profit_growth = data.get("profit_growth")
    roe = data.get("roe")
    debt = data.get("debt_ratio")
    net_profit = data.get("net_profit")
    cashflow = data.get("operating_cashflow")
    pe = data.get("pe")
    pb = data.get("pb")
    relative_valuation = row_data.get("relative_valuation_label")

    high_valuation = relative_valuation == "relatively_expensive" or _is_high(pe, 60) or _is_high(pb, 8)
    low_valuation = relative_valuation == "relatively_cheap_but_needs_check" or (
        valuation is not None and valuation >= 70 and not high_valuation
    )

    if row_data.get("fundamental_data_quality_label") in {"no_fundamental_data", "insufficient_fundamental_data", None}:
        flags.append("insufficient_data_for_conflict_check")
    if growth is not None and growth >= 75 and high_valuation:
        flags.append("high_growth_high_valuation")
    if (
        (profitability is not None and profitability >= 70) or (isinstance(net_profit, (int, float)) and net_profit > 0)
    ) and isinstance(cashflow, (int, float)) and cashflow < 0:
        flags.append("high_profit_negative_cashflow")
    if low_valuation and growth is not None and growth < 45:
        flags.append("low_valuation_weak_growth")
    if isinstance(roe, (int, float)) and roe >= 0.15 and isinstance(debt, (int, float)) and debt >= 0.75:
        flags.append("high_roe_high_debt")
    if isinstance(revenue_growth, (int, float)) and revenue_growth > 0 and isinstance(profit_growth, (int, float)) and profit_growth <= 0:
        flags.append("revenue_growth_without_profit_growth")
    if isinstance(profit_growth, (int, float)) and profit_growth > 0 and isinstance(revenue_growth, (int, float)) and revenue_growth <= 0:
        flags.append("profit_growth_without_revenue_growth")
    return _clean_list(flags, limit=8)


def build_fundamental_conflict_summary(flags):
    if not flags:
        return "未识别到明显的基本面内部矛盾，仍需结合原始字段持续核查。"
    if "insufficient_data_for_conflict_check" in flags and len(flags) == 1:
        return "基本面字段不足，暂不能稳定判断内部矛盾。"
    messages = {
        "high_growth_high_valuation": "成长性与估值水平同时偏高",
        "high_profit_negative_cashflow": "利润表现与经营现金流存在背离",
        "low_valuation_weak_growth": "低估值同时伴随成长偏弱",
        "high_roe_high_debt": "较高ROE同时伴随较高负债",
        "revenue_growth_without_profit_growth": "营收增长未同步转化为利润增长",
        "profit_growth_without_revenue_growth": "利润增长缺少营收增长同步支撑",
        "insufficient_data_for_conflict_check": "部分字段不足",
    }
    parts = [messages.get(flag, flag) for flag in flags[:3]]
    return _sanitize_text("；".join(parts) + "，需要在后续研究中重点复核。")


def build_industry_relative_detail(row):
    row_data = _row_dict(row)
    quality = row_data.get("industry_relative_quality_label")
    profitability = row_data.get("relative_profitability_label")
    growth = row_data.get("relative_growth_label")
    valuation = row_data.get("relative_valuation_label")
    risk = row_data.get("relative_financial_risk_label")
    advantages = []
    disadvantages = []

    if profitability in {"industry_leading", "above_industry_average"}:
        advantages.append("盈利能力在同行内相对靠前")
    elif profitability == "below_industry_average":
        disadvantages.append("盈利能力低于同行观察水平")
    if growth == "high_relative_growth":
        advantages.append("成长性在同行内相对靠前")
    elif growth in {"weak_relative_growth", "negative_relative_growth"}:
        disadvantages.append("成长性弱于同行观察水平")
    if valuation == "relatively_reasonable":
        advantages.append("估值相对位置较为平衡")
    elif valuation == "relatively_expensive":
        disadvantages.append("估值水平在同行中偏高")
    elif valuation in {"relatively_cheap_but_needs_check", "abnormal_valuation_data"}:
        disadvantages.append("估值可比性需要进一步核查")
    if risk == "lower_than_industry_risk":
        advantages.append("财务风险低于同行观察水平")
    elif risk == "higher_than_industry_risk":
        disadvantages.append("财务风险高于同行观察水平")

    if quality == "insufficient_industry_data" or not quality:
        summary = "行业相对字段不足，暂不能形成稳定同行位置诊断。"
    elif quality == "industry_relative_strong":
        summary = "行业相对位置具备一定优势，但仍需结合估值和现金流继续核查。"
    elif quality == "industry_relative_weak":
        summary = "行业相对位置存在弱项，需要优先复核盈利、成长或财务风险字段。"
    else:
        summary = "行业相对位置整体中性，需要结合具体字段继续比较。"
    return {
        "relative_profitability_label": profitability,
        "relative_growth_label": growth,
        "relative_valuation_label": valuation,
        "relative_financial_risk_label": risk,
        "industry_relative_quality_label": quality,
        "advantages": _clean_list(advantages),
        "disadvantages": _clean_list(disadvantages),
        "summary": _sanitize_text(summary),
    }


def build_fundamental_research_questions(row, strengths, weaknesses, conflicts, industry_detail):
    row_data = _row_dict(row)
    questions = []
    if strengths:
        questions.append("这些基本面强项是否具备连续多个报告期的稳定性？")
    if "high_growth_high_valuation" in conflicts:
        questions.append("当前成长速度是否足以支撑偏高的估值水平？")
    if "high_profit_negative_cashflow" in conflicts:
        questions.append("经营现金流与利润背离是否来自一次性因素或回款节奏？")
    if "low_valuation_weak_growth" in conflicts:
        questions.append("低估值是否反映了成长放缓或行业景气度压力？")
    if "high_roe_high_debt" in conflicts or row_data.get("fundamental_profile_type") == "leverage_pressure":
        questions.append("较高ROE是否依赖较高负债水平推动？")
    if weaknesses:
        questions.append("主要弱项是否会持续影响基本面质量稳定性？")
    if industry_detail.get("industry_relative_quality_label") == "insufficient_industry_data":
        questions.append("行业分类和同行样本是否足以支持相对比较？")
    elif industry_detail.get("disadvantages"):
        questions.append("同行相对弱项是否来自行业结构差异或公司自身质量差异？")
    if len(detect_fundamental_fields(row_data)) < 4:
        questions.append("是否需要补充更多基本面字段后再形成诊断结论？")
    if not questions:
        questions.append("后续应优先核查哪些字段会改变当前基本面画像？")
        questions.append("行业相对位置是否能在更多同行样本中保持稳定？")
    return [_sanitize_text(item) for item in _limited_questions(questions)]


def _detail_block(title, diagnostics, focus):
    positives = diagnostics.get("positive_signals", []) if isinstance(diagnostics, dict) else []
    negatives = diagnostics.get("negative_signals", []) if isinstance(diagnostics, dict) else []
    missing = diagnostics.get("missing_fields", []) if isinstance(diagnostics, dict) else []
    explanation = diagnostics.get("explanation", "") if isinstance(diagnostics, dict) else ""
    evidence = positives[:3]
    if not evidence and negatives:
        evidence = negatives[:2]
    if not evidence and missing:
        evidence = ["关键字段不足"]
    return {
        "title": title,
        "score": diagnostics.get("score") if isinstance(diagnostics, dict) else None,
        "level": diagnostics.get("level") if isinstance(diagnostics, dict) else "insufficient_data",
        "focus": focus,
        "evidence": evidence,
        "risk_or_gap": negatives[:3] + [f"缺失字段:{field}" for field in missing[:2]],
        "explanation": _sanitize_text(explanation),
    }


def build_profitability_detail(profitability):
    return _detail_block("profitability", profitability, "盈利质量、利润规模与现金流匹配度")


def build_growth_detail(growth):
    return _detail_block("growth", growth, "营收增长、利润增长与成长延续性")


def build_valuation_detail(valuation):
    detail = _detail_block("valuation", valuation, "估值可比性、估值压力与质量匹配度")
    if valuation.get("level") in {"valuation_expensive", "valuation_abnormal"}:
        detail["risk_or_gap"] = _clean_list(["估值压力需要结合盈利和成长质量复核"] + detail["risk_or_gap"], limit=5)
    return detail


def build_financial_risk_detail(financial_risk):
    detail = _detail_block("financial_risk", financial_risk, "负债、现金流与利润稳定性")
    if financial_risk.get("level") in {"high_debt_pressure", "weak_cashflow", "loss_or_negative_profit"}:
        detail["risk_or_gap"] = _clean_list(["财务风险字段存在压力"] + detail["risk_or_gap"], limit=5)
    return detail


def build_fundamental_key_evidence(diagnostics, strengths, industry_detail):
    evidence = []
    for item in strengths:
        evidence.append(item)
    for key in ("profitability", "growth", "valuation", "financial_risk"):
        block = diagnostics.get(key, {})
        for signal in block.get("positive_signals", [])[:2]:
            evidence.append(signal)
    for item in industry_detail.get("advantages", []):
        evidence.append(item)
    if not evidence:
        evidence.append("基本面有效支撑证据有限")
    return [_sanitize_text(item) for item in _clean_list(evidence, limit=5)]


def build_fundamental_uncertainty_notes(row, diagnostics, conflicts, industry_detail):
    row_data = _row_dict(row)
    notes = []
    if row_data.get("fundamental_data_quality_label") in {"no_fundamental_data", "insufficient_fundamental_data", None}:
        notes.append("基本面字段不足，诊断可信度有限")
    for key in ("profitability", "growth", "valuation", "financial_risk"):
        block = diagnostics.get(key, {})
        if block.get("missing_fields"):
            notes.append(f"{key}存在缺失字段")
    if industry_detail.get("industry_relative_quality_label") in {"insufficient_industry_data", None}:
        notes.append("行业或同行样本不足，行业相对结论有限")
    if diagnostics.get("valuation", {}).get("level") in {"valuation_abnormal", "insufficient_valuation_data"}:
        notes.append("估值字段异常或不足，估值可比性有限")
    if diagnostics.get("financial_risk", {}).get("level") in {"weak_cashflow", "high_debt_pressure"}:
        notes.append("现金流或负债字段存在异常观察点")
    if conflicts:
        notes.append("基本面内部存在需要复核的矛盾信号")
    if not notes:
        notes.append("当前不确定性主要来自单期字段稳定性，仍需结合后续数据核查")
    return [_sanitize_text(item) for item in _clean_list(notes, limit=6)]


def build_fundamental_detail_view(
    row,
    profitability_detail,
    growth_detail,
    valuation_detail,
    financial_risk_detail,
    key_evidence,
    uncertainty_notes,
):
    row_data = _row_dict(row)
    return {
        "profile_type": row_data.get("fundamental_profile_type"),
        "profitability": profitability_detail,
        "growth": growth_detail,
        "valuation": valuation_detail,
        "financial_risk": financial_risk_detail,
        "key_evidence": key_evidence,
        "uncertainty_notes": uncertainty_notes,
        "research_boundary": "仅用于基本面研究辅助，不构成操作结论。",
        "metadata": {
            "read_only": True,
            "uses_real_data_source": False,
            "ranking_changed": False,
            "strategy_score_changed": False,
        },
    }


def build_fundamental_data_completeness_score(row):
    detected = detect_fundamental_fields(_row_dict(row))
    total_fields = 13
    return max(0, min(100, int(round(len(detected) / total_fields * 100))))


def build_fundamental_industry_comparability_label(row):
    row_data = _row_dict(row)
    quality = row_data.get("industry_relative_quality_label")
    relative_labels = [
        row_data.get("relative_profitability_label"),
        row_data.get("relative_growth_label"),
        row_data.get("relative_valuation_label"),
        row_data.get("relative_financial_risk_label"),
    ]
    if quality is None and not any(relative_labels):
        return "no_industry_comparison"
    if quality == "insufficient_industry_data":
        return "insufficient_industry_comparison"
    if quality in {"industry_relative_strong", "industry_relative_neutral", "industry_relative_weak"}:
        if any(label in {None, "insufficient_data"} for label in relative_labels):
            return "partial_industry_comparison"
        return "sufficient_industry_comparison"
    if any(label and label != "insufficient_data" for label in relative_labels):
        return "partial_industry_comparison"
    return "no_industry_comparison"


def build_fundamental_anomaly_flags(row, diagnostics=None, conflicts=None):
    row_data = _row_dict(row)
    data = detect_fundamental_fields(row_data)
    diagnostics = diagnostics or {}
    conflicts = conflicts or []
    flags = []
    pe = data.get("pe")
    pb = data.get("pb")
    ps = data.get("ps")
    net_profit = data.get("net_profit")
    cashflow = data.get("operating_cashflow")
    debt = data.get("debt_ratio")
    valuation_level = diagnostics.get("valuation", {}).get("level") if isinstance(diagnostics, dict) else None

    if valuation_level == "valuation_abnormal" or row_data.get("relative_valuation_label") == "abnormal_valuation_data":
        flags.append("abnormal_valuation")
    if any(isinstance(value, (int, float)) and (value <= 0 or value > 120) for value in (pe, pb, ps)):
        flags.append("abnormal_valuation")
    if isinstance(net_profit, (int, float)) and net_profit < 0:
        flags.append("negative_profit")
    if isinstance(cashflow, (int, float)) and cashflow < 0:
        flags.append("negative_cashflow")
    if isinstance(debt, (int, float)) and debt > 0.75:
        flags.append("high_debt")
    invalid_fields = row_data.get("invalid_numeric_fields")
    if invalid_fields:
        flags.append("invalid_numeric_fields")
    if row_data.get("fundamental_data_quality_label") in {"no_fundamental_data", "insufficient_fundamental_data", None}:
        flags.append("insufficient_data")
    if "insufficient_data_for_conflict_check" in conflicts:
        flags.append("insufficient_data")
    return _clean_list(flags, limit=8)


def build_fundamental_confidence(row, diagnostics=None, conflicts=None):
    row_data = _row_dict(row)
    diagnostics = diagnostics or {}
    conflicts = conflicts or []
    completeness = build_fundamental_data_completeness_score(row_data)
    comparability = build_fundamental_industry_comparability_label(row_data)
    anomalies = build_fundamental_anomaly_flags(row_data, diagnostics=diagnostics, conflicts=conflicts)
    comparability_score = {
        "sufficient_industry_comparison": 25,
        "partial_industry_comparison": 15,
        "insufficient_industry_comparison": 5,
        "no_industry_comparison": 0,
    }.get(comparability, 0)
    score = int(round(completeness * 0.70 + comparability_score))
    score -= min(30, len(anomalies) * 8)
    score -= min(15, len([flag for flag in conflicts if flag != "insufficient_data_for_conflict_check"]) * 4)
    score = max(0, min(100, score))

    if completeness < 20 or row_data.get("fundamental_data_quality_label") == "no_fundamental_data":
        level = "insufficient"
    elif score >= 75:
        level = "high"
    elif score >= 55:
        level = "medium"
    elif score >= 30:
        level = "low"
    else:
        level = "insufficient"

    reasons = []
    if completeness >= 70:
        reasons.append("基本面字段完整度较高")
    elif completeness >= 35:
        reasons.append("基本面字段完整度一般")
    else:
        reasons.append("基本面字段缺失较多")
    if comparability == "sufficient_industry_comparison":
        reasons.append("行业相对比较信息较完整")
    elif comparability == "partial_industry_comparison":
        reasons.append("行业相对比较信息部分可用")
    else:
        reasons.append("行业相对比较信息不足")
    if anomalies:
        reasons.append("存在异常字段或数据质量提示")
    if conflicts:
        reasons.append("存在基本面内部矛盾需要复核")

    return {
        "fundamental_confidence_level": level,
        "fundamental_confidence_score": score,
        "fundamental_confidence_reasons": [_sanitize_text(item) for item in _clean_list(reasons, limit=5)],
        "fundamental_data_completeness_score": completeness,
        "fundamental_industry_comparability_label": comparability,
        "fundamental_anomaly_flags": anomalies,
    }


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
    profile_type = build_fundamental_profile_type(row_data)
    row_data["fundamental_profile_type"] = profile_type
    conflict_flags = build_fundamental_conflicts(row_data)
    conflict_summary = build_fundamental_conflict_summary(conflict_flags)
    industry_detail = build_industry_relative_detail(row_data)
    relative_advantages = industry_detail["advantages"]
    relative_disadvantages = industry_detail["disadvantages"]
    relative_summary = industry_detail["summary"]
    research_questions = build_fundamental_research_questions(
        row_data, strengths, weaknesses, conflict_flags, industry_detail
    )
    profitability_detail = build_profitability_detail(profitability)
    growth_detail = build_growth_detail(growth)
    valuation_detail = build_valuation_detail(valuation)
    financial_risk_detail = build_financial_risk_detail(financial_risk)
    key_evidence = build_fundamental_key_evidence(diagnostics, strengths, industry_detail)
    uncertainty_notes = build_fundamental_uncertainty_notes(row_data, diagnostics, conflict_flags, industry_detail)
    confidence = build_fundamental_confidence(row_data, diagnostics=diagnostics, conflicts=conflict_flags)
    detail_view = build_fundamental_detail_view(
        row_data,
        profitability_detail,
        growth_detail,
        valuation_detail,
        financial_risk_detail,
        key_evidence,
        uncertainty_notes,
    )
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
            "detail": industry_detail,
        },
        "profile_type": profile_type,
        "conflict_flags": conflict_flags,
        "conflict_summary": conflict_summary,
        "relative_advantage_points": relative_advantages,
        "relative_disadvantage_points": relative_disadvantages,
        "relative_position_summary": relative_summary,
        "research_questions": research_questions,
        "detail_view": detail_view,
        "key_evidence": key_evidence,
        "uncertainty_notes": uncertainty_notes,
        "confidence": confidence,
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
        "fundamental_profile_type": profile_type,
        "fundamental_conflict_flags": conflict_flags,
        "fundamental_conflict_summary": conflict_summary,
        "industry_relative_detail": industry_detail,
        "relative_advantage_points": relative_advantages,
        "relative_disadvantage_points": relative_disadvantages,
        "relative_position_summary": relative_summary,
        "fundamental_research_questions": research_questions,
        "fundamental_detail_view": detail_view,
        "profitability_detail": profitability_detail,
        "growth_detail": growth_detail,
        "valuation_detail": valuation_detail,
        "financial_risk_detail": financial_risk_detail,
        "fundamental_key_evidence": key_evidence,
        "fundamental_uncertainty_notes": uncertainty_notes,
        "fundamental_confidence_level": confidence["fundamental_confidence_level"],
        "fundamental_confidence_score": confidence["fundamental_confidence_score"],
        "fundamental_confidence_reasons": confidence["fundamental_confidence_reasons"],
        "fundamental_data_completeness_score": confidence["fundamental_data_completeness_score"],
        "fundamental_industry_comparability_label": confidence["fundamental_industry_comparability_label"],
        "fundamental_anomaly_flags": confidence["fundamental_anomaly_flags"],
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
    "build_fundamental_conflict_summary",
    "build_fundamental_conflicts",
    "build_fundamental_anomaly_flags",
    "build_fundamental_confidence",
    "build_fundamental_data_completeness_score",
    "build_fundamental_diagnostics_profile",
    "build_fundamental_diagnostics_row",
    "build_fundamental_detail_view",
    "build_fundamental_key_evidence",
    "build_fundamental_industry_comparability_label",
    "build_fundamental_profile_type",
    "build_fundamental_research_questions",
    "build_fundamental_uncertainty_notes",
    "build_financial_risk_detail",
    "build_growth_detail",
    "build_growth_diagnostics",
    "build_industry_relative_detail",
    "build_profitability_detail",
    "build_profitability_diagnostics",
    "build_valuation_detail",
    "build_valuation_diagnostics",
]
