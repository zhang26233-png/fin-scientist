"""Internal comparison helpers for original and strategy scores."""

import copy
import math

import pandas as pd

ORIGINAL_SCORE_COLUMNS = ("研究优先级评分", "original_score", "research_priority_score")
STRATEGY_SCORE_COLUMNS = ("strategy_score", "策略评分")


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


def _find_column(columns, candidates):
    for candidate in candidates:
        if candidate in columns:
            return candidate
    lowered = {str(column).lower(): column for column in columns}
    for candidate in candidates:
        matched = lowered.get(str(candidate).lower())
        if matched is not None:
            return matched
    return None


def _alignment_label(original_score, strategy_score, high_threshold=60, low_threshold=40):
    if math.isnan(original_score) or math.isnan(strategy_score):
        return "insufficient_data"
    original_high = original_score >= high_threshold
    strategy_high = strategy_score >= high_threshold
    original_low = original_score <= low_threshold
    strategy_low = strategy_score <= low_threshold

    if original_high and strategy_high:
        return "high_consensus"
    if original_high and strategy_low:
        return "research_high_strategy_low"
    if strategy_high and original_low:
        return "strategy_high_research_low"
    if original_low and strategy_low:
        return "low_consensus"
    return "mixed_observation"


def _interpretation(label):
    return {
        "high_consensus": "研究与策略维度一致性较高，适合作为进一步研究对象观察。",
        "research_high_strategy_low": "研究优先级较高，但策略侧表现偏弱或数据不足，需要核验量价、流动性和风险约束。",
        "strategy_high_research_low": "策略侧表现较强，但仍需补充基本面、行业和数据质量验证。",
        "low_consensus": "当前研究优先级较低，后续可先观察数据改善或风险变化。",
        "insufficient_data": "评分数据不足，暂不判断一致性。",
        "mixed_observation": "两套评分未形成明确一致性，需要结合分项因子继续观察。",
    }.get(label, "评分对比结果需要进一步核验。")


def _priority_type(label):
    return {
        "high_consensus": "一致性较高",
        "research_high_strategy_low": "研究强于策略",
        "strategy_high_research_low": "策略强于研究",
        "low_consensus": "一致性较低",
        "insufficient_data": "数据不足",
        "mixed_observation": "分歧观察",
    }.get(label, "待核验")


def _warnings(original_score, strategy_score):
    warnings = []
    if math.isnan(original_score):
        warnings.append("原研究优先级评分缺失。")
    if math.isnan(strategy_score):
        warnings.append("strategy_score 缺失。")
    if not warnings and abs(original_score - strategy_score) >= 30:
        warnings.append("两套评分差异较大，需要复核因子、风险和数据质量。")
    if not warnings:
        warnings.append("评分对比仅用于内部研究解释，不构成投资建议。")
    return warnings


def compare_strategy_scores(score_frame):
    if not isinstance(score_frame, pd.DataFrame) or score_frame.empty:
        return {
            "status": "empty",
            "comparisons": [],
            "summary": "输入为空，未生成评分对比。",
            "metadata": {"read_only": True, "ranking_changed": False, "scoring_changed": False},
        }

    source = score_frame.copy(deep=True)
    original_column = _find_column(source.columns, ORIGINAL_SCORE_COLUMNS)
    strategy_column = _find_column(source.columns, STRATEGY_SCORE_COLUMNS)

    comparisons = []
    for index, row in source.iterrows():
        original_score = _to_number(row.get(original_column)) if original_column else math.nan
        strategy_score = _to_number(row.get(strategy_column)) if strategy_column else math.nan
        label = _alignment_label(original_score, strategy_score)
        score_gap = None if math.isnan(original_score) or math.isnan(strategy_score) else round(strategy_score - original_score, 2)
        comparisons.append(
            {
                "row_index": int(index) if isinstance(index, int) else str(index),
                "original_score": None if math.isnan(original_score) else original_score,
                "strategy_score": None if math.isnan(strategy_score) else strategy_score,
                "score_gap": score_gap,
                "alignment_label": label,
                "interpretation": _interpretation(label),
                "research_priority_type": _priority_type(label),
                "warnings": _warnings(original_score, strategy_score),
            }
        )

    return {
        "status": "ok",
        "comparisons": copy.deepcopy(comparisons),
        "summary": f"已生成 {len(comparisons)} 条内部评分对比，未改变排序或评分。",
        "metadata": {
            "original_score_column": original_column,
            "strategy_score_column": strategy_column,
            "read_only": True,
            "ranking_changed": False,
            "scoring_changed": False,
        },
    }


__all__ = [
    "compare_strategy_scores",
]
