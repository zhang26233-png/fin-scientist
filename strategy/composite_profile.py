"""Read-only composite research profile helpers."""

import copy
import math

import pandas as pd


COMPOSITE_PROFILE_FIELDS = [
    "composite_research_grade",
    "composite_research_style",
    "composite_research_level",
    "composite_risk_level",
    "composite_confidence_level",
    "composite_summary",
    "composite_strength_points",
    "composite_risk_points",
    "composite_followup_focus",
    "composite_data_quality_note",
]

FORBIDDEN_COMPOSITE_WORDS = (
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
    "\u76ee\u6807\u4ef7",
    "\u63a8\u8350\u4e70\u5165",
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


def _sanitize_text(value):
    text = str(value)
    for word in FORBIDDEN_COMPOSITE_WORDS:
        text = text.replace(word, "研究")
    return text


def _clean_list(items, limit):
    output = []
    for item in items:
        if not item or item in output:
            continue
        output.append(_sanitize_text(item))
        if len(output) >= limit:
            break
    return output


def _safe_score(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return max(0, min(100, int(round(number))))


def _as_list(value):
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _has_data(row):
    fields = (
        "technical_grade",
        "fundamental_grade",
        "strategy_score",
        "confluence_label",
        "fundamental_research_level",
    )
    return any(row.get(field) not in (None, "", [], {}) for field in fields)


def _technical_strong(row):
    return row.get("technical_grade") in {"A", "B"} or row.get("technical_strength") in {"strong", "moderate"}


def _technical_weak(row):
    return row.get("technical_grade") in {"C", "D"} or row.get("technical_strength") == "weak"


def _fundamental_strong(row):
    return row.get("fundamental_grade") in {"A", "B"} or row.get("fundamental_research_level") in {
        "strong_candidate",
        "worth_tracking",
    }


def _fundamental_weak(row):
    return row.get("fundamental_grade") == "D" or row.get("fundamental_research_level") in {
        "weak_or_risky",
        "insufficient_data",
    }


def _risk_label_count(row):
    return len(_as_list(row.get("risk_labels")))


def _data_quality_issue_count(row):
    return len(_as_list(row.get("data_quality_labels"))) + len(_as_list(row.get("warnings")))


def _composite_risk_level(row):
    if not _has_data(row):
        return "unknown"
    if (
        row.get("technical_risk_level") == "high"
        or row.get("fundamental_risk_level") == "high"
        or row.get("confluence_label") == "high_risk_speculation"
        or _risk_label_count(row) >= 3
        or row.get("fundamental_research_level") == "weak_or_risky"
    ):
        return "high"
    if _risk_label_count(row) >= 1 or row.get("technical_risk_level") == "medium":
        return "medium"
    return "low"


def _composite_confidence_level(row):
    if not _has_data(row):
        return "insufficient"
    fundamental_confidence = row.get("fundamental_confidence_level")
    if fundamental_confidence in {"insufficient", "low"}:
        return "low" if fundamental_confidence == "low" else "insufficient"
    if _data_quality_issue_count(row) >= 3 or row.get("industry_relative_quality_label") == "insufficient_industry_data":
        return "low"
    if fundamental_confidence == "high" and row.get("consensus_level") in {"high", "medium", ""}:
        return "high"
    return "medium"


def _composite_grade(row, risk_level, confidence_level):
    strategy_score = _safe_score(row.get("strategy_score"))
    confluence_score = _safe_score(row.get("confluence_score"))
    if confidence_level == "insufficient" or not _has_data(row):
        return "insufficient_data"
    if confidence_level == "low" or risk_level == "high":
        return "C" if _technical_strong(row) or _fundamental_strong(row) else "D"
    if (
        _technical_strong(row)
        and _fundamental_strong(row)
        and row.get("confluence_label") == "fundamental_technical_resonance"
        and (strategy_score is None or strategy_score >= 65)
        and (confluence_score is None or confluence_score >= 70)
    ):
        return "A"
    if _technical_strong(row) and _fundamental_weak(row):
        return "C"
    if _fundamental_strong(row) and _technical_weak(row):
        return "B"
    if _technical_strong(row) or _fundamental_strong(row):
        return "B"
    return "C"


def _composite_style(row, grade, risk_level):
    if grade == "insufficient_data":
        return "insufficient_data"
    if risk_level == "high" and _fundamental_weak(row):
        return "weak_or_high_risk"
    if row.get("confluence_label") == "fundamental_technical_resonance" and _technical_strong(row) and _fundamental_strong(row):
        return "high_quality_resonance"
    if _technical_strong(row) and _fundamental_strong(row):
        return "technical_momentum_with_fundamental_support"
    if _fundamental_strong(row) and _technical_weak(row):
        return "fundamental_value_waiting_technical_confirmation"
    if _technical_strong(row) and _fundamental_weak(row):
        return "technical_speculation_with_weak_fundamental"
    if row.get("dominant_style") in {"high_elasticity_watch", "volume_breakout"}:
        return "event_or_theme_watch"
    if risk_level == "high":
        return "weak_or_high_risk"
    return "mixed_signal_watch"


def _composite_level(grade, style, risk_level, confidence_level):
    if grade == "insufficient_data" or confidence_level == "insufficient":
        return "insufficient_data"
    if grade == "A" and risk_level == "low" and confidence_level in {"high", "medium"}:
        return "priority_research"
    if grade in {"A", "B"} and risk_level in {"low", "medium"}:
        return "worth_tracking"
    if style in {"technical_speculation_with_weak_fundamental", "mixed_signal_watch"} or risk_level == "high":
        return "watch_with_caution"
    if grade == "D":
        return "low_priority"
    return "watch_with_caution"


def _strength_points(row):
    points = []
    if _technical_strong(row):
        points.append("技术结构较强")
    if _fundamental_strong(row):
        points.append("基本面质量具备一定支撑")
    if row.get("industry_relative_quality_label") == "industry_relative_strong":
        points.append("行业内相对优势较好")
    if (_safe_score(row.get("strategy_score")) or 0) >= 70:
        points.append("策略评分较高")
    if row.get("confluence_label") == "fundamental_technical_resonance":
        points.append("技术与基本面形成共振")
    if _composite_risk_level(row) == "low":
        points.append("风险观察相对可控")
    return _clean_list(points, 4)


def _risk_points(row, risk_level, confidence_level):
    points = []
    if row.get("technical_risk_level") == "high":
        points.append("技术风险偏高")
    if row.get("fundamental_confidence_level") in {"low", "insufficient"}:
        points.append("基本面可信度不足")
    for item in _as_list(row.get("fundamental_core_risk")):
        points.append(item)
    if row.get("industry_relative_quality_label") == "industry_relative_weak":
        points.append("行业相对优势不明显")
    if row.get("consensus_level") in {"low", "divergent"}:
        points.append("策略分歧较大")
    if _data_quality_issue_count(row) > 0 or confidence_level in {"low", "insufficient"}:
        points.append("数据质量或字段完整度需要复核")
    if risk_level == "high" and not points:
        points.append("综合风险偏高")
    return _clean_list(points, 4)


def _followup_focus(row, risks):
    focus = []
    if row.get("fundamental_confidence_level") in {"low", "insufficient"}:
        focus.append("核查基本面数据来源和财报持续性")
    if row.get("technical_grade") in {"A", "B"}:
        focus.append("观察技术结构是否延续")
    if any("估值" in str(item) for item in risks):
        focus.append("检查估值是否有成长支撑")
    if row.get("volume_price_structure_label") == "volume_price_confirmed":
        focus.append("关注量价是否继续确认")
    focus.extend(_as_list(row.get("confluence_followup_focus")))
    focus.extend(_as_list(row.get("technical_watch_points")))
    focus.extend(_as_list(row.get("fundamental_followup_focus")))
    if not focus:
        focus.append("补充事件催化和行业景气度信息")
        focus.append("继续核查技术与基本面是否同步改善")
    if len(focus) == 1:
        focus.append("继续核查技术与基本面是否同步改善")
    return _clean_list(focus, 4)


def _data_quality_note(row, confidence_level):
    notes = []
    if _data_quality_issue_count(row) > 0:
        notes.append("存在数据质量标签或预警，综合结论需结合原始字段复核。")
    if row.get("industry_relative_quality_label") == "insufficient_industry_data":
        notes.append("行业样本或行业字段不足，行业相对结论可信度有限。")
    if confidence_level in {"low", "insufficient"}:
        notes.append("基本面可信度偏低，综合画像仅适合作为粗略研究观察。")
    if not notes:
        notes.append("当前字段完整度可支持基础综合研究画像。")
    return _sanitize_text(" ".join(notes))


def _summary(grade, style, level, risk_level, confidence_level):
    if grade == "insufficient_data":
        return "技术、基本面或策略字段不足，暂不能形成稳定综合研究画像。"
    if style == "high_quality_resonance":
        return "技术结构、基本面质量与共振结果较一致，可作为较高优先级研究观察对象。"
    if style == "technical_speculation_with_weak_fundamental":
        return "技术结构相对更强，但基本面支撑偏弱，需要优先复核质量和风险字段。"
    if style == "fundamental_value_waiting_technical_confirmation":
        return "基本面观察相对更强，但技术结构仍需进一步确认。"
    if risk_level == "high":
        return "综合画像存在较高风险信号，当前更适合做风险与数据质量复核。"
    return f"综合研究画像为 {grade}，研究层级为 {level}，可信度为 {confidence_level}，适合继续做中性研究观察。"


def build_composite_profile_row(row):
    row_data = _row_dict(row)
    risk_level = _composite_risk_level(row_data)
    confidence_level = _composite_confidence_level(row_data)
    grade = _composite_grade(row_data, risk_level, confidence_level)
    style = _composite_style(row_data, grade, risk_level)
    level = _composite_level(grade, style, risk_level, confidence_level)
    strengths = _strength_points(row_data)
    risks = _risk_points(row_data, risk_level, confidence_level)
    followup = _followup_focus(row_data, risks)
    return {
        "composite_research_grade": grade,
        "composite_research_style": style,
        "composite_research_level": level,
        "composite_risk_level": risk_level,
        "composite_confidence_level": confidence_level,
        "composite_summary": _sanitize_text(_summary(grade, style, level, risk_level, confidence_level)),
        "composite_strength_points": strengths,
        "composite_risk_points": risks,
        "composite_followup_focus": followup,
        "composite_data_quality_note": _data_quality_note(row_data, confidence_level),
    }


def build_composite_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=COMPOSITE_PROFILE_FIELDS)
    rows = [build_composite_profile_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=COMPOSITE_PROFILE_FIELDS)


__all__ = [
    "COMPOSITE_PROFILE_FIELDS",
    "build_composite_profile",
    "build_composite_profile_row",
]
