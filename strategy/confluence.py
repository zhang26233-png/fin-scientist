"""Read-only technical and fundamental confluence helpers."""

import copy
import math

import pandas as pd


CONFLUENCE_FIELDS = [
    "confluence_label",
    "confluence_score",
    "confluence_summary",
    "confluence_strength_points",
    "confluence_risk_points",
    "confluence_followup_focus",
]

FORBIDDEN_CONFLUENCE_WORDS = (
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
    "\u76ee\u6807\u4ef7",
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


def _clean_list(items, limit=3):
    output = []
    for item in items:
        if not item or item in output:
            continue
        output.append(_sanitize_text(item))
        if len(output) >= limit:
            break
    return output


def _sanitize_text(value):
    text = str(value)
    for word in FORBIDDEN_CONFLUENCE_WORDS:
        text = text.replace(word, "研究")
    return text


def _safe_score(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return max(0, min(100, int(round(number))))


def _technical_state(row):
    grade = str(row.get("technical_grade") or "")
    strength = str(row.get("technical_strength") or "")
    risk = str(row.get("technical_risk_level") or "")
    style = str(row.get("technical_style") or "")
    strong = grade in {"A", "B"} or strength in {"strong", "moderate"}
    weak = grade in {"C", "D"} or strength == "weak" or style == "weak_or_choppy"
    high_risk = risk == "high"
    available = bool(grade or strength or risk or style)
    return {"strong": strong, "weak": weak, "high_risk": high_risk, "available": available}


def _fundamental_state(row):
    grade = str(row.get("fundamental_grade") or "")
    research_level = str(row.get("fundamental_research_level") or "")
    profile = str(row.get("fundamental_profile_type") or "")
    confidence = str(row.get("fundamental_confidence_level") or "")
    consistency = str(row.get("fundamental_consistency_label") or "")
    strong = grade in {"A", "B"} or research_level in {"strong_candidate", "worth_tracking"}
    weak = grade == "D" or research_level in {"weak_or_risky", "insufficient_data"} or profile in {
        "weak_fundamental",
        "cashflow_risk",
        "leverage_pressure",
        "insufficient_data",
    }
    high_risk = research_level == "weak_or_risky" or profile in {"cashflow_risk", "leverage_pressure", "weak_fundamental"}
    low_confidence = confidence in {"low", "insufficient"}
    inconsistent = consistency in {"inconsistent", "low_consistency"}
    available = bool(grade or research_level or profile or confidence)
    return {
        "strong": strong,
        "weak": weak,
        "high_risk": high_risk,
        "low_confidence": low_confidence,
        "inconsistent": inconsistent,
        "available": available,
        "profile": profile,
    }


def _label(technical, fundamental):
    if not technical["available"] or not fundamental["available"]:
        return "insufficient_data"
    if technical["strong"] and fundamental["strong"] and not technical["high_risk"] and not fundamental["high_risk"]:
        return "fundamental_technical_resonance"
    if technical["strong"] and fundamental["high_risk"] and fundamental.get("profile") in {"cashflow_risk", "leverage_pressure"}:
        return "high_risk_speculation"
    if fundamental["strong"] and technical["weak"]:
        return "fundamental_strong_technical_weak"
    if technical["strong"] and fundamental["weak"]:
        return "technical_strong_fundamental_weak"
    if technical["high_risk"] or fundamental["low_confidence"] or fundamental["inconsistent"]:
        return "mixed_signal"
    return "mixed_signal"


def _score(label, technical, fundamental):
    base = {
        "fundamental_technical_resonance": 82,
        "fundamental_strong_technical_weak": 58,
        "technical_strong_fundamental_weak": 48,
        "mixed_signal": 45,
        "high_risk_speculation": 35,
        "insufficient_data": 20,
    }.get(label, 40)
    if technical["high_risk"]:
        base -= 10
    if fundamental["low_confidence"]:
        base -= 10
    if fundamental["inconsistent"]:
        base -= 8
    return max(0, min(100, int(round(base))))


def _strength_points(row, label):
    points = []
    if label == "fundamental_technical_resonance":
        points.append("技术结构与基本面观察存在共振")
    if row.get("technical_grade") in {"A", "B"}:
        points.append("技术等级相对较好")
    if row.get("fundamental_grade") in {"A", "B"} or row.get("fundamental_research_level") in {
        "strong_candidate",
        "worth_tracking",
    }:
        points.append("基本面研究结论具备一定支撑")
    if row.get("fundamental_confidence_level") in {"high", "medium"}:
        points.append("基本面诊断可信度可用于继续观察")
    return _clean_list(points)


def _risk_points(row, label):
    points = []
    if label == "high_risk_speculation":
        points.append("技术强度与基本面风险存在错配")
    if row.get("technical_risk_level") == "high":
        points.append("技术面短期风险偏高")
    if row.get("fundamental_research_level") in {"weak_or_risky", "insufficient_data"}:
        points.append("基本面结论存在风险或数据不足")
    if row.get("fundamental_confidence_level") in {"low", "insufficient"}:
        points.append("基本面诊断可信度不足")
    if row.get("fundamental_consistency_label") in {"inconsistent", "low_consistency"}:
        points.append("基本面内部一致性需要复核")
    return _clean_list(points)


def _followup_focus(row, label, risks):
    focus = []
    if label == "fundamental_technical_resonance":
        focus.append("继续核查技术结构与基本面结论是否保持同步")
    elif label == "fundamental_strong_technical_weak":
        focus.append("重点观察技术结构是否改善")
    elif label == "technical_strong_fundamental_weak":
        focus.append("重点复核基本面薄弱字段")
    elif label == "high_risk_speculation":
        focus.append("优先核查基本面风险是否与技术强度错配")
    else:
        focus.append("补充验证技术面与基本面分歧来源")
    focus.extend(risks)
    if row.get("fundamental_confidence_level") in {"low", "insufficient"}:
        focus.append("补充基本面字段后再判断共振稳定性")
    return _clean_list(focus)


def _summary(label, score):
    if label == "fundamental_technical_resonance":
        return f"技术面与基本面观察方向较一致，共振评分为 {score}，适合继续做研究跟踪。"
    if label == "fundamental_strong_technical_weak":
        return f"基本面观察相对更强，但技术结构仍偏弱，共振评分为 {score}，需要继续验证技术改善。"
    if label == "technical_strong_fundamental_weak":
        return f"技术结构相对更强，但基本面支撑不足，共振评分为 {score}，需要复核基本面质量。"
    if label == "high_risk_speculation":
        return f"技术强度与基本面风险存在错配，共振评分为 {score}，仅适合做风险复核观察。"
    if label == "insufficient_data":
        return "技术或基本面字段不足，暂不能形成稳定共振判断。"
    return f"技术面与基本面信号存在分歧，共振评分为 {score}，需要补充验证。"


def build_confluence_row(row):
    row_data = _row_dict(row)
    technical = _technical_state(row_data)
    fundamental = _fundamental_state(row_data)
    label = _label(technical, fundamental)
    score = _score(label, technical, fundamental)
    strengths = _strength_points(row_data, label)
    risks = _risk_points(row_data, label)
    return {
        "confluence_label": label,
        "confluence_score": score,
        "confluence_summary": _sanitize_text(_summary(label, score)),
        "confluence_strength_points": strengths,
        "confluence_risk_points": risks,
        "confluence_followup_focus": _followup_focus(row_data, label, risks),
    }


def build_confluence_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=CONFLUENCE_FIELDS)
    rows = [build_confluence_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=CONFLUENCE_FIELDS)


__all__ = [
    "CONFLUENCE_FIELDS",
    "build_confluence_profile",
    "build_confluence_row",
]
