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


def _extract_comparisons(source):
    if isinstance(source, pd.DataFrame):
        return compare_strategy_scores(source).get("comparisons", [])
    if isinstance(source, dict):
        comparisons = source.get("comparisons")
        return copy.deepcopy(comparisons) if isinstance(comparisons, list) else []
    if isinstance(source, list):
        return copy.deepcopy(source)
    return []


def _average(values):
    clean_values = [value for value in values if isinstance(value, (int, float)) and not math.isnan(value)]
    if not clean_values:
        return None
    return round(sum(clean_values) / len(clean_values), 2)


def summarize_score_alignment(source):
    comparisons = _extract_comparisons(source)
    if not comparisons:
        return {
            "total_count": 0,
            "valid_count": 0,
            "missing_original_score_count": 0,
            "missing_strategy_score_count": 0,
            "average_original_score": None,
            "average_strategy_score": None,
            "average_score_gap": None,
            "alignment_counts": {},
            "alignment_ratios": {},
            "high_consensus_count": 0,
            "research_high_strategy_low_count": 0,
            "strategy_high_research_low_count": 0,
            "low_consensus_count": 0,
            "insufficient_data_count": 0,
            "summary_text": "输入为空，未生成评分一致性汇总。",
            "warnings": ["评分对比汇总仅用于内部研究解释，不构成投资建议。"],
        }

    total_count = len(comparisons)
    original_scores = []
    strategy_scores = []
    score_gaps = []
    alignment_counts = {}
    missing_original = 0
    missing_strategy = 0

    for item in comparisons:
        if not isinstance(item, dict):
            continue
        label = item.get("alignment_label", "insufficient_data")
        alignment_counts[label] = alignment_counts.get(label, 0) + 1
        original_score = item.get("original_score")
        strategy_score = item.get("strategy_score")
        score_gap = item.get("score_gap")
        if isinstance(original_score, (int, float)):
            original_scores.append(float(original_score))
        else:
            missing_original += 1
        if isinstance(strategy_score, (int, float)):
            strategy_scores.append(float(strategy_score))
        else:
            missing_strategy += 1
        if isinstance(score_gap, (int, float)):
            score_gaps.append(float(score_gap))

    alignment_ratios = {
        label: round(count / total_count, 4) if total_count else 0
        for label, count in alignment_counts.items()
    }
    valid_count = total_count - alignment_counts.get("insufficient_data", 0)
    high_consensus_count = alignment_counts.get("high_consensus", 0)
    research_high_strategy_low_count = alignment_counts.get("research_high_strategy_low", 0)
    strategy_high_research_low_count = alignment_counts.get("strategy_high_research_low", 0)
    low_consensus_count = alignment_counts.get("low_consensus", 0)
    insufficient_data_count = alignment_counts.get("insufficient_data", 0)
    summary_text = (
        f"本批次共 {total_count} 条评分对比，其中有效对比 {valid_count} 条；"
        f"高一致性 {high_consensus_count} 条，分歧样本 "
        f"{research_high_strategy_low_count + strategy_high_research_low_count} 条，"
        f"数据不足 {insufficient_data_count} 条。"
    )
    warnings = ["评分对比汇总仅用于内部研究解释，不构成投资建议。"]
    if missing_original:
        warnings.append(f"缺失原研究优先级评分 {missing_original} 条。")
    if missing_strategy:
        warnings.append(f"缺失 strategy_score {missing_strategy} 条。")

    return {
        "total_count": total_count,
        "valid_count": valid_count,
        "missing_original_score_count": missing_original,
        "missing_strategy_score_count": missing_strategy,
        "average_original_score": _average(original_scores),
        "average_strategy_score": _average(strategy_scores),
        "average_score_gap": _average(score_gaps),
        "alignment_counts": alignment_counts,
        "alignment_ratios": alignment_ratios,
        "high_consensus_count": high_consensus_count,
        "research_high_strategy_low_count": research_high_strategy_low_count,
        "strategy_high_research_low_count": strategy_high_research_low_count,
        "low_consensus_count": low_consensus_count,
        "insufficient_data_count": insufficient_data_count,
        "summary_text": summary_text,
        "warnings": warnings,
    }


__all__ = [
    "compare_strategy_scores",
    "summarize_score_alignment",
]
