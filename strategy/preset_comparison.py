"""Internal cross-preset comparison helpers for strategy scores."""

import copy
import math

import pandas as pd

from strategy.presets import get_strategy_preset
from strategy.scoring import calculate_strategy_scores


DEFAULT_COMPARISON_PRESETS = (
    "balanced_research",
    "trend_momentum",
    "volume_breakout",
    "low_risk_quality",
    "high_elasticity_watch",
)

STYLE_BY_PRESET = {
    "balanced_research": "balanced",
    "trend_momentum": "trend_momentum",
    "volume_breakout": "volume_breakout",
    "low_risk_quality": "low_risk_quality",
    "high_elasticity_watch": "high_elasticity",
}


def _score_value(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return int(round(number))


def _source_to_frame(source):
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, pd.Series):
        return pd.DataFrame([copy.deepcopy(source.to_dict())])
    if isinstance(source, dict):
        if isinstance(source.get("scores"), list):
            return copy.deepcopy(source)
        return pd.DataFrame([copy.deepcopy(source)])
    return pd.DataFrame()


def _preset_score_item(source, preset_name):
    result = calculate_strategy_scores(source, preset_name=preset_name)
    scores = result.get("scores", []) if isinstance(result, dict) else []
    if not scores:
        preset = get_strategy_preset(preset_name)
        return {
            "preset_name": preset.get("preset_name", preset_name),
            "preset_display_name": preset.get("display_name", ""),
            "strategy_score": None,
            "risk_penalty": None,
            "data_quality_penalty": None,
            "warnings": ["preset score unavailable"],
        }
    row = copy.deepcopy(scores[0])
    return {
        "preset_name": row.get("preset_name", preset_name),
        "preset_display_name": row.get("preset_display_name", ""),
        "strategy_score": _score_value(row.get("strategy_score")),
        "risk_penalty": _score_value(row.get("risk_penalty")),
        "data_quality_penalty": _score_value(row.get("data_quality_penalty")),
        "risk_labels": list(row.get("risk_labels", [])) if isinstance(row.get("risk_labels"), list) else [],
        "data_quality_labels": list(row.get("data_quality_labels", []))
        if isinstance(row.get("data_quality_labels"), list)
        else [],
        "strategy_score_components": copy.deepcopy(row.get("strategy_score_components", {})),
    }


def _valid_scores(preset_scores):
    return [item for item in preset_scores if isinstance(item.get("strategy_score"), int)]


def _consensus_level(valid_scores):
    if not valid_scores:
        return "insufficient_data"
    values = [item["strategy_score"] for item in valid_scores]
    high_count = sum(value >= 65 for value in values)
    low_count = sum(value < 40 for value in values)
    spread = max(values) - min(values)
    majority = len(values) // 2 + 1
    if high_count >= majority and spread <= 25:
        return "broad_consensus_high"
    if low_count >= majority and max(values) < 55:
        return "broad_consensus_low"
    if spread >= 18:
        return "mixed_signal"
    if max(values) >= 65 and high_count < majority:
        return "style_specific_high"
    return "mixed_signal"


def _dominant_style(valid_scores, consensus_level):
    if not valid_scores:
        return "insufficient_data"
    if consensus_level == "broad_consensus_low":
        return "mixed"
    best = max(valid_scores, key=lambda item: (item["strategy_score"], item.get("preset_name", "")))
    best_score = best["strategy_score"]
    near_best = [item for item in valid_scores if best_score - item["strategy_score"] <= 1]
    styles = {STYLE_BY_PRESET.get(item.get("preset_name"), "mixed") for item in near_best}
    if len(styles) == 1:
        return next(iter(styles))
    if consensus_level == "broad_consensus_high":
        return "balanced" if "balanced" in styles else "mixed"
    return "mixed"


def _style_notes(consensus_level, dominant_style, best_preset, worst_preset):
    if consensus_level == "insufficient_data":
        return ["关键数据不足，当前只能形成有限比较。"]
    notes = [f"最高预设为 {best_preset.get('preset_name', '')}。", f"最低预设为 {worst_preset.get('preset_name', '')}。"]
    if dominant_style != "mixed":
        notes.append(f"当前更接近 {dominant_style} 风格。")
    else:
        notes.append("不同预设之间存在分歧，需结合原始指标继续研究。")
    return notes


def summarize_preset_scores(preset_scores):
    scores = copy.deepcopy(preset_scores) if isinstance(preset_scores, list) else []
    valid_scores = _valid_scores(scores)
    if not valid_scores:
        return {
            "best_preset": None,
            "worst_preset": None,
            "score_spread": None,
            "average_preset_score": None,
            "consensus_level": "insufficient_data",
            "dominant_style": "insufficient_data",
            "style_notes": ["关键数据不足，无法有效比较多策略预设。"],
            "warnings": ["preset scores are empty or invalid"],
        }

    best = max(valid_scores, key=lambda item: (item["strategy_score"], item.get("preset_name", "")))
    worst = min(valid_scores, key=lambda item: (item["strategy_score"], item.get("preset_name", "")))
    values = [item["strategy_score"] for item in valid_scores]
    spread = max(values) - min(values)
    average = round(sum(values) / len(values), 2)
    consensus = _consensus_level(valid_scores)
    dominant = _dominant_style(valid_scores, consensus)
    warnings = []
    if len(valid_scores) < len(scores):
        warnings.append("部分 preset 分数缺失。")
    return {
        "best_preset": copy.deepcopy(best),
        "worst_preset": copy.deepcopy(worst),
        "score_spread": spread,
        "average_preset_score": average,
        "consensus_level": consensus,
        "dominant_style": dominant,
        "style_notes": _style_notes(consensus, dominant, best, worst),
        "warnings": warnings,
    }


def compare_strategy_presets(source, preset_names=None):
    source_copy = _source_to_frame(source)
    if isinstance(source_copy, dict):
        return {
            "status": "unsupported",
            "preset_scores": [],
            **summarize_preset_scores([]),
            "metadata": {
                "read_only": True,
                "ui_connected": False,
                "ranking_changed": False,
                "scoring_changed": False,
            },
        }
    preset_names = tuple(preset_names or DEFAULT_COMPARISON_PRESETS)
    if source_copy.empty:
        summary = summarize_preset_scores([])
        return {
            "status": "empty",
            "preset_scores": [],
            **summary,
            "metadata": {
                "read_only": True,
                "ui_connected": False,
                "ranking_changed": False,
                "scoring_changed": False,
            },
        }

    first_row = source_copy.iloc[[0]].copy(deep=True)
    preset_scores = [_preset_score_item(first_row, preset_name) for preset_name in preset_names]
    summary = summarize_preset_scores(preset_scores)
    return {
        "status": "ok",
        "preset_scores": preset_scores,
        **summary,
        "metadata": {
            "read_only": True,
            "ui_connected": False,
            "ranking_changed": False,
            "scoring_changed": False,
            "preset_count": len(preset_scores),
        },
    }


def _ratio_map(counts, denominator):
    if denominator <= 0:
        return {key: 0.0 for key in counts}
    return {key: round(value / denominator, 4) for key, value in counts.items()}


def _average(values):
    clean_values = [value for value in values if isinstance(value, (int, float)) and math.isfinite(value)]
    if not clean_values:
        return None
    return round(sum(clean_values) / len(clean_values), 2)


def _empty_pool_summary(status="empty", warning="candidate pool is empty"):
    style_counts = {
        "balanced": 0,
        "trend_momentum": 0,
        "volume_breakout": 0,
        "low_risk_quality": 0,
        "high_elasticity": 0,
        "mixed": 0,
        "insufficient_data": 0,
    }
    consensus_counts = {
        "broad_consensus_high": 0,
        "style_specific_high": 0,
        "mixed_signal": 0,
        "broad_consensus_low": 0,
        "insufficient_data": 0,
    }
    return {
        "status": status,
        "total_count": 0,
        "valid_count": 0,
        "insufficient_data_count": 0,
        "dominant_style_counts": style_counts,
        "dominant_style_ratios": _ratio_map(style_counts, 0),
        "consensus_level_counts": consensus_counts,
        "consensus_level_ratios": _ratio_map(consensus_counts, 0),
        "average_scores_by_preset": {},
        "average_score_spread": None,
        "max_score_spread": None,
        "broad_consensus_high_count": 0,
        "style_specific_high_count": 0,
        "mixed_signal_count": 0,
        "broad_consensus_low_count": 0,
        "summary_text": "候选池为空，未生成多策略预设横向汇总。",
        "warnings": [warning],
        "metadata": {
            "read_only": True,
            "ui_connected": False,
            "ranking_changed": False,
            "scoring_changed": False,
        },
    }


def summarize_preset_comparison_pool(source, preset_names=None):
    source_frame = _source_to_frame(source)
    if isinstance(source_frame, dict):
        return _empty_pool_summary(status="unsupported", warning="candidate pool structure is unsupported")
    if source_frame.empty:
        return _empty_pool_summary()

    preset_names = tuple(preset_names or DEFAULT_COMPARISON_PRESETS)
    comparisons = []
    for _, row in source_frame.iterrows():
        comparisons.append(compare_strategy_presets(pd.DataFrame([copy.deepcopy(row.to_dict())]), preset_names))

    style_keys = ("balanced", "trend_momentum", "volume_breakout", "low_risk_quality", "high_elasticity", "mixed", "insufficient_data")
    consensus_keys = (
        "broad_consensus_high",
        "style_specific_high",
        "mixed_signal",
        "broad_consensus_low",
        "insufficient_data",
    )
    style_counts = {key: 0 for key in style_keys}
    consensus_counts = {key: 0 for key in consensus_keys}
    preset_score_values = {preset_name: [] for preset_name in preset_names}
    spreads = []
    warnings = []

    for comparison in comparisons:
        style = comparison.get("dominant_style", "insufficient_data")
        consensus = comparison.get("consensus_level", "insufficient_data")
        if style not in style_counts:
            style = "mixed"
        if consensus not in consensus_counts:
            consensus = "insufficient_data"
        style_counts[style] += 1
        consensus_counts[consensus] += 1
        spread = comparison.get("score_spread")
        if isinstance(spread, (int, float)) and math.isfinite(spread):
            spreads.append(spread)
        for item in comparison.get("preset_scores", []):
            preset_name = item.get("preset_name")
            score = item.get("strategy_score")
            if preset_name in preset_score_values and isinstance(score, (int, float)):
                preset_score_values[preset_name].append(score)
        warnings.extend(comparison.get("warnings", []))

    total_count = len(comparisons)
    insufficient_data_count = consensus_counts["insufficient_data"] + sum(
        1
        for comparison in comparisons
        if comparison.get("consensus_level") != "insufficient_data"
        and all((item.get("strategy_score") in (None, 0)) for item in comparison.get("preset_scores", []))
    )
    valid_count = max(0, total_count - insufficient_data_count)
    average_scores = {preset_name: _average(values) for preset_name, values in preset_score_values.items()}
    average_spread = _average(spreads)
    max_spread = max(spreads) if spreads else None
    summary_text = (
        f"已汇总 {total_count} 个候选对象的内部多策略预设比较；"
        f"有效比较 {valid_count} 个，数据不足 {insufficient_data_count} 个，"
        f"平均分歧 {average_spread if average_spread is not None else '无'}。"
        "该汇总仅用于学习和研究，不构成投资建议。"
    )

    return {
        "status": "ok",
        "total_count": total_count,
        "valid_count": valid_count,
        "insufficient_data_count": insufficient_data_count,
        "dominant_style_counts": style_counts,
        "dominant_style_ratios": _ratio_map(style_counts, total_count),
        "consensus_level_counts": consensus_counts,
        "consensus_level_ratios": _ratio_map(consensus_counts, total_count),
        "average_scores_by_preset": average_scores,
        "average_score_spread": average_spread,
        "max_score_spread": max_spread,
        "broad_consensus_high_count": consensus_counts["broad_consensus_high"],
        "style_specific_high_count": consensus_counts["style_specific_high"],
        "mixed_signal_count": consensus_counts["mixed_signal"],
        "broad_consensus_low_count": consensus_counts["broad_consensus_low"],
        "summary_text": summary_text,
        "warnings": list(dict.fromkeys(warnings)),
        "metadata": {
            "read_only": True,
            "ui_connected": False,
            "ranking_changed": False,
            "scoring_changed": False,
            "preset_count": len(preset_names),
        },
    }


__all__ = [
    "DEFAULT_COMPARISON_PRESETS",
    "compare_strategy_presets",
    "summarize_preset_scores",
    "summarize_preset_comparison_pool",
]
