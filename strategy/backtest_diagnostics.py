"""Diagnostics for internal backtest metric summaries."""

import copy
import math


REQUIRED_SUMMARY_FIELDS = (
    "total_count",
    "valid_count",
    "insufficient_data_count",
    "outcome_counts",
    "outcome_ratios",
    "average_forward_return_1d",
    "average_forward_return_3d",
    "average_forward_return_5d",
    "average_forward_return_10d",
    "average_max_drawdown_forward",
    "by_preset",
    "by_score_bucket",
    "by_dominant_style",
    "by_consensus_level",
    "warnings",
    "metadata",
)

REQUIRED_GROUP_FIELDS = (
    "total_count",
    "valid_count",
    "insufficient_data_count",
    "outcome_counts",
    "outcome_ratios",
    "average_forward_return_5d",
    "average_forward_return_10d",
    "average_max_drawdown_forward",
)

SCORE_BUCKETS = (
    "high_score",
    "mid_score",
    "low_score",
    "insufficient_score",
)


def _as_summary(summary):
    return copy.deepcopy(summary) if isinstance(summary, dict) else {}


def _to_number(value):
    if value is None:
        return math.nan
    try:
        number = float(value)
    except (TypeError, ValueError):
        return math.nan
    return number if math.isfinite(number) else math.nan


def _safe_count(group):
    if not isinstance(group, dict):
        return 0
    value = _to_number(group.get("total_count"))
    return 0 if math.isnan(value) else int(value)


def _metric_value(group):
    if not isinstance(group, dict):
        return math.nan
    for key in ("average_forward_return_10d", "average_forward_return_5d"):
        value = _to_number(group.get(key))
        if not math.isnan(value):
            return value
    return math.nan


def _drawdown_value(group):
    if not isinstance(group, dict):
        return math.nan
    return _to_number(group.get("average_max_drawdown_forward"))


def _missing_fields(mapping, required_fields, prefix=""):
    if not isinstance(mapping, dict):
        return list(required_fields)
    missing = []
    for field in required_fields:
        if field not in mapping:
            missing.append(f"{prefix}{field}")
    return missing


def _validate_group_mapping(mapping, prefix):
    missing = []
    if not isinstance(mapping, dict):
        return [prefix.rstrip(".")]
    for group_name, group in mapping.items():
        if not isinstance(group, dict):
            missing.append(f"{prefix}{group_name}")
            continue
        missing.extend(_missing_fields(group, REQUIRED_GROUP_FIELDS, prefix=f"{prefix}{group_name}."))
    return missing


def _format_group_observation(group_name, group):
    count = _safe_count(group)
    metric = _metric_value(group)
    drawdown = _drawdown_value(group)
    text = f"{group_name}: sample_count={count}"
    if not math.isnan(metric):
        text += f", average_forward_return={round(metric, 6)}"
    if not math.isnan(drawdown):
        text += f", average_max_drawdown_forward={round(drawdown, 6)}"
    return text


def _rank_groups(group_mapping):
    ranked = []
    if not isinstance(group_mapping, dict):
        return ranked
    for group_name, group in group_mapping.items():
        metric = _metric_value(group)
        if math.isnan(metric) or _safe_count(group) <= 0:
            continue
        ranked.append((group_name, metric, _drawdown_value(group), _safe_count(group)))
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked


def validate_backtest_metrics_schema(summary):
    data = _as_summary(summary)
    missing_fields = _missing_fields(data, REQUIRED_SUMMARY_FIELDS)
    missing_fields.extend(_validate_group_mapping(data.get("by_preset"), "by_preset."))
    missing_fields.extend(_validate_group_mapping(data.get("by_score_bucket"), "by_score_bucket."))
    missing_fields.extend(_validate_group_mapping(data.get("by_dominant_style"), "by_dominant_style."))
    missing_fields.extend(_validate_group_mapping(data.get("by_consensus_level"), "by_consensus_level."))
    missing_fields = list(dict.fromkeys(missing_fields))

    data_quality_warnings = []
    total = _to_number(data.get("total_count"))
    valid = _to_number(data.get("valid_count"))
    insufficient = _to_number(data.get("insufficient_data_count"))
    if math.isnan(total) or total <= 0:
        data_quality_warnings.append("sample_count_insufficient")
    if not math.isnan(total) and not math.isnan(valid) and valid <= 0 and total > 0:
        data_quality_warnings.append("valid_sample_count_is_zero")
    if not math.isnan(total) and not math.isnan(insufficient) and total > 0 and insufficient / total >= 0.5:
        data_quality_warnings.append("insufficient_data_ratio_high")

    for key in ("by_preset", "by_dominant_style", "by_consensus_level"):
        value = data.get(key)
        if not isinstance(value, dict) or len(value) < 2:
            data_quality_warnings.append(f"{key}_group_count_low")

    score_buckets = data.get("by_score_bucket")
    if not isinstance(score_buckets, dict):
        data_quality_warnings.append("score_bucket_group_missing")
    else:
        populated = [bucket for bucket in SCORE_BUCKETS if _safe_count(score_buckets.get(bucket)) > 0]
        if len(populated) < 2:
            data_quality_warnings.append("score_bucket_group_count_low")

    return {
        "schema_valid": not missing_fields,
        "missing_fields": missing_fields,
        "data_quality_warnings": list(dict.fromkeys(data_quality_warnings)),
        "warnings": list(dict.fromkeys(data.get("warnings", []) if isinstance(data.get("warnings"), list) else [])),
        "metadata": {
            "read_only": True,
            "uses_real_data_source": False,
            "ui_connected": False,
            "diagnostic_scope": "internal_research_validation",
        },
    }


def diagnose_score_bucket_performance(summary):
    data = _as_summary(summary)
    buckets = data.get("by_score_bucket", {})
    high = buckets.get("high_score", {}) if isinstance(buckets, dict) else {}
    low = buckets.get("low_score", {}) if isinstance(buckets, dict) else {}
    high_count = _safe_count(high)
    low_count = _safe_count(low)
    high_metric = _metric_value(high)
    low_metric = _metric_value(low)
    warnings = []

    if high_count == 0 or low_count == 0 or math.isnan(high_metric) or math.isnan(low_metric):
        warnings.append("score_bucket_sample_insufficient")
        observation = "样本量不足，暂不判断。"
        distinction = "insufficient_sample"
    else:
        spread = round(high_metric - low_metric, 6)
        if spread >= 0.02:
            observation = "高分组在样本中表现相对更强。"
            distinction = "high_score_stronger"
        else:
            observation = "当前样本中高低分组区分度有限。"
            distinction = "limited_distinction"

    return {
        "diagnostic_type": "score_bucket",
        "observation": observation,
        "distinction": distinction,
        "high_score_count": high_count,
        "low_score_count": low_count,
        "high_score_average_forward_return": None if math.isnan(high_metric) else round(high_metric, 6),
        "low_score_average_forward_return": None if math.isnan(low_metric) else round(low_metric, 6),
        "warnings": warnings,
    }


def _diagnose_group_performance(summary, group_key, diagnostic_type):
    data = _as_summary(summary)
    groups = data.get(group_key, {})
    warnings = []
    if not isinstance(groups, dict) or not groups:
        return {
            "diagnostic_type": diagnostic_type,
            "observation": "样本量不足，暂不判断。",
            "group_count": 0,
            "ranked_groups": [],
            "group_observations": [],
            "warnings": [f"{diagnostic_type}_sample_insufficient"],
        }

    ranked = _rank_groups(groups)
    if len(ranked) < 2:
        warnings.append(f"{diagnostic_type}_group_count_low")
        observation = "样本量不足，暂不判断。"
    else:
        top_name, top_metric, top_drawdown, top_count = ranked[0]
        bottom_name, bottom_metric, bottom_drawdown, bottom_count = ranked[-1]
        spread = top_metric - bottom_metric
        if spread >= 0.02:
            observation = (
                f"{diagnostic_type} 分组中 {top_name} 的样本后续表现相对更强，"
                "该观察仅用于研究验证。"
            )
        else:
            observation = f"{diagnostic_type} 分组之间的后续表现差异有限。"
        if top_count < 2 or bottom_count < 2:
            warnings.append(f"{diagnostic_type}_small_group_sample")
        if not math.isnan(top_drawdown) and not math.isnan(bottom_drawdown) and top_drawdown < bottom_drawdown:
            warnings.append(f"{diagnostic_type}_drawdown_needs_review")

    return {
        "diagnostic_type": diagnostic_type,
        "observation": observation,
        "group_count": len(groups),
        "ranked_groups": [
            {
                "group": name,
                "average_forward_return": round(metric, 6),
                "average_max_drawdown_forward": None if math.isnan(drawdown) else round(drawdown, 6),
                "sample_count": count,
            }
            for name, metric, drawdown, count in ranked
        ],
        "group_observations": [_format_group_observation(name, group) for name, group in groups.items()],
        "warnings": warnings,
    }


def diagnose_preset_performance(summary):
    return _diagnose_group_performance(summary, "by_preset", "preset")


def diagnose_style_performance(summary):
    return _diagnose_group_performance(summary, "by_dominant_style", "dominant_style")


def diagnose_consensus_performance(summary):
    return _diagnose_group_performance(summary, "by_consensus_level", "consensus_level")


def build_backtest_diagnostics_report(summary):
    data = _as_summary(summary)
    schema = validate_backtest_metrics_schema(data)
    score_bucket = diagnose_score_bucket_performance(data)
    preset = diagnose_preset_performance(data)
    style = diagnose_style_performance(data)
    consensus = diagnose_consensus_performance(data)

    warnings = []
    warnings.extend(schema["data_quality_warnings"])
    warnings.extend(schema["warnings"])
    for section in (score_bucket, preset, style, consensus):
        warnings.extend(section.get("warnings", []))

    if not schema["schema_valid"]:
        summary_text = "Backtest metrics summary schema is incomplete; diagnostics are limited."
    elif _safe_count(data) == 0:
        summary_text = "Backtest metrics summary has no samples; diagnostics are limited."
    else:
        summary_text = "Backtest metrics diagnostics completed for internal research validation."

    return {
        "schema_valid": schema["schema_valid"],
        "missing_fields": schema["missing_fields"],
        "data_quality_warnings": schema["data_quality_warnings"],
        "score_bucket_diagnostics": score_bucket,
        "preset_diagnostics": preset,
        "style_diagnostics": style,
        "consensus_diagnostics": consensus,
        "summary_text": summary_text,
        "warnings": list(dict.fromkeys(warnings)),
        "metadata": {
            "read_only": True,
            "uses_real_data_source": False,
            "ui_connected": False,
            "diagnostic_scope": "internal_research_validation",
        },
    }


__all__ = [
    "build_backtest_diagnostics_report",
    "diagnose_consensus_performance",
    "diagnose_preset_performance",
    "diagnose_score_bucket_performance",
    "diagnose_style_performance",
    "validate_backtest_metrics_schema",
]
