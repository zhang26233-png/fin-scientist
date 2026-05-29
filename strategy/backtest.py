"""Internal backtest sample helpers for strategy research validation."""

import copy
import math

import pandas as pd


OUTCOME_LABELS = (
    "positive_follow_through",
    "weak_follow_through",
    "failed_follow_through",
    "high_drawdown_risk",
    "insufficient_data",
)

SCORE_BUCKETS = (
    "high_score",
    "mid_score",
    "low_score",
    "insufficient_score",
)


def _to_number(value):
    if value is None:
        return math.nan
    try:
        number = float(value)
    except (TypeError, ValueError):
        return math.nan
    return number if math.isfinite(number) else math.nan


def _read_any(mapping, keys):
    if not isinstance(mapping, dict):
        return None
    lowered = {str(key).lower(): key for key in mapping}
    for key in keys:
        if key in mapping:
            return mapping.get(key)
        matched = lowered.get(str(key).lower())
        if matched is not None:
            return mapping.get(matched)
    return None


def _safe_text(value):
    return "" if value is None else str(value)


def _extract_candidate(candidate):
    if isinstance(candidate, pd.Series):
        return copy.deepcopy(candidate.to_dict())
    if isinstance(candidate, dict):
        return copy.deepcopy(candidate)
    return {}


def _samples_to_records(samples):
    if isinstance(samples, pd.DataFrame):
        return copy.deepcopy(samples.to_dict(orient="records"))
    if isinstance(samples, pd.Series):
        return [copy.deepcopy(samples.to_dict())]
    if isinstance(samples, list):
        return copy.deepcopy(samples)
    if isinstance(samples, tuple):
        return copy.deepcopy(list(samples))
    return []


def _price_series(forward_prices=None, price_col="close"):
    if isinstance(forward_prices, pd.DataFrame):
        if price_col in forward_prices.columns:
            series = pd.to_numeric(forward_prices[price_col], errors="coerce")
        elif "Close" in forward_prices.columns:
            series = pd.to_numeric(forward_prices["Close"], errors="coerce")
        else:
            return pd.Series(dtype=float)
        return series[series.map(lambda value: math.isfinite(value) if not pd.isna(value) else False)].reset_index(
            drop=True
        )
    if isinstance(forward_prices, pd.Series):
        series = pd.to_numeric(forward_prices, errors="coerce")
        return series[series.map(lambda value: math.isfinite(value) if not pd.isna(value) else False)].reset_index(
            drop=True
        )
    if isinstance(forward_prices, (list, tuple)):
        series = pd.to_numeric(pd.Series(list(forward_prices)), errors="coerce")
        return series[series.map(lambda value: math.isfinite(value) if not pd.isna(value) else False)].reset_index(
            drop=True
        )
    return pd.Series(dtype=float)


def bucket_strategy_score(score):
    value = _to_number(score)
    if math.isnan(value):
        return "insufficient_score"
    if value >= 75:
        return "high_score"
    if value >= 50:
        return "mid_score"
    return "low_score"


def _normalize_outcome_label(value):
    return value if value in OUTCOME_LABELS else "insufficient_data"


def _group_text(value, fallback):
    text = _safe_text(value).strip()
    return text if text else fallback


def _average_numeric(records, key):
    values = []
    for record in records:
        if not isinstance(record, dict):
            continue
        value = _to_number(record.get(key))
        if not math.isnan(value):
            values.append(value)
    return None if not values else round(sum(values) / len(values), 6)


def _summarize_metric_records(records):
    normalized = [record if isinstance(record, dict) else {} for record in records]
    total = len(normalized)
    outcome_counts = {label: 0 for label in OUTCOME_LABELS}
    warnings = []
    for record in normalized:
        label = _normalize_outcome_label(record.get("outcome_label"))
        outcome_counts[label] += 1
        warnings.extend(str(item) for item in record.get("warnings", []) if item)

    insufficient_data_count = outcome_counts["insufficient_data"]
    return {
        "total_count": total,
        "valid_count": total - insufficient_data_count,
        "insufficient_data_count": insufficient_data_count,
        "outcome_counts": outcome_counts,
        "outcome_ratios": {
            key: (round(value / total, 4) if total else 0.0) for key, value in outcome_counts.items()
        },
        "average_forward_return_1d": _average_numeric(normalized, "forward_return_1d"),
        "average_forward_return_3d": _average_numeric(normalized, "forward_return_3d"),
        "average_forward_return_5d": _average_numeric(normalized, "forward_return_5d"),
        "average_forward_return_10d": _average_numeric(normalized, "forward_return_10d"),
        "average_max_drawdown_forward": _average_numeric(normalized, "max_drawdown_forward"),
        "warnings": list(dict.fromkeys(warnings)),
        "metadata": {
            "read_only": True,
            "uses_real_data_source": False,
            "ui_connected": False,
            "metric_scope": "internal_research_validation",
        },
    }


def _summarize_by_key(samples, key, fallback):
    records = _samples_to_records(samples)
    grouped = {}
    for record in records:
        group_key = _group_text(record.get(key), fallback) if isinstance(record, dict) else fallback
        grouped.setdefault(group_key, []).append(record)
    return {group_key: _summarize_metric_records(group_records) for group_key, group_records in grouped.items()}


def summarize_backtest_by_preset(samples):
    return _summarize_by_key(samples, "preset_name", "unknown_preset")


def summarize_backtest_by_score_bucket(samples):
    records = _samples_to_records(samples)
    grouped = {bucket: [] for bucket in SCORE_BUCKETS}
    for record in records:
        score = record.get("strategy_score") if isinstance(record, dict) else None
        grouped[bucket_strategy_score(score)].append(record)
    return {bucket: _summarize_metric_records(grouped[bucket]) for bucket in SCORE_BUCKETS}


def summarize_backtest_by_dominant_style(samples):
    return _summarize_by_key(samples, "dominant_style", "unknown_dominant_style")


def summarize_backtest_by_consensus_level(samples):
    return _summarize_by_key(samples, "consensus_level", "unknown_consensus_level")


def build_backtest_metrics_summary(samples):
    records = _samples_to_records(samples)
    summary = _summarize_metric_records(records)
    summary.update(
        {
            "by_preset": summarize_backtest_by_preset(records),
            "by_score_bucket": summarize_backtest_by_score_bucket(records),
            "by_dominant_style": summarize_backtest_by_dominant_style(records),
            "by_consensus_level": summarize_backtest_by_consensus_level(records),
        }
    )
    return summary


def validate_backtest_input(candidate, forward_prices=None, required_fields=("symbol", "strategy_score")):
    row = _extract_candidate(candidate)
    warnings = []
    missing_fields = [field for field in required_fields if row.get(field) in (None, "")]
    if missing_fields:
        warnings.append("missing required fields: " + ", ".join(missing_fields))
    score = _to_number(row.get("strategy_score"))
    if math.isnan(score):
        warnings.append("strategy_score is missing or invalid")
    prices = _price_series(forward_prices)
    if forward_prices is not None and len(prices) < 2:
        warnings.append("forward price data is insufficient")
    return {
        "valid": not warnings,
        "missing_fields": missing_fields,
        "warnings": warnings,
    }


def calculate_forward_return(forward_prices, horizon, price_col="close"):
    prices = _price_series(forward_prices, price_col=price_col)
    if horizon <= 0 or len(prices) <= horizon:
        return None
    start = _to_number(prices.iloc[0])
    end = _to_number(prices.iloc[horizon])
    if math.isnan(start) or math.isnan(end) or start == 0:
        return None
    return round(end / start - 1, 6)


def _max_drawdown_forward(forward_prices, price_col="close"):
    prices = _price_series(forward_prices, price_col=price_col)
    if len(prices) < 2:
        return None
    peak = _to_number(prices.iloc[0])
    max_drawdown = 0.0
    if math.isnan(peak) or peak == 0:
        return None
    for value in prices:
        number = _to_number(value)
        if math.isnan(number):
            continue
        peak = max(peak, number)
        if peak != 0:
            max_drawdown = min(max_drawdown, number / peak - 1)
    return round(max_drawdown, 6)


def classify_backtest_outcome(forward_return=None, max_drawdown_forward=None, positive_threshold=0.02, weak_band=0.01):
    drawdown = _to_number(max_drawdown_forward)
    if not math.isnan(drawdown) and drawdown <= -0.08:
        return "high_drawdown_risk"
    value = _to_number(forward_return)
    if math.isnan(value):
        return "insufficient_data"
    if value >= positive_threshold:
        return "positive_follow_through"
    if value < -weak_band:
        return "failed_follow_through"
    return "weak_follow_through"


def build_backtest_sample(candidate, forward_prices=None, snapshot_date=None, preset_name=None, metadata=None):
    row = _extract_candidate(candidate)
    validation = validate_backtest_input(row, forward_prices)
    forward_return_1d = calculate_forward_return(forward_prices, 1)
    forward_return_3d = calculate_forward_return(forward_prices, 3)
    forward_return_5d = calculate_forward_return(forward_prices, 5)
    forward_return_10d = calculate_forward_return(forward_prices, 10)
    max_drawdown = _max_drawdown_forward(forward_prices)
    outcome_return = next(
        (
            value
            for value in (forward_return_10d, forward_return_5d, forward_return_3d, forward_return_1d)
            if value is not None
        ),
        None,
    )
    outcome_label = classify_backtest_outcome(outcome_return, max_drawdown)
    warnings = list(validation["warnings"])
    if outcome_label == "insufficient_data" and "forward return data is insufficient" not in warnings:
        warnings.append("forward return data is insufficient")
    return {
        "symbol": _safe_text(_read_any(row, ("symbol", "股票代码", "code"))),
        "name": _safe_text(_read_any(row, ("name", "股票名称"))),
        "snapshot_date": snapshot_date or _safe_text(row.get("snapshot_date")),
        "preset_name": preset_name or _safe_text(row.get("preset_name")),
        "strategy_score": None if math.isnan(_to_number(row.get("strategy_score"))) else _to_number(row.get("strategy_score")),
        "dominant_style": _safe_text(row.get("dominant_style")),
        "consensus_level": _safe_text(row.get("consensus_level")),
        "forward_return_1d": forward_return_1d,
        "forward_return_3d": forward_return_3d,
        "forward_return_5d": forward_return_5d,
        "forward_return_10d": forward_return_10d,
        "max_drawdown_forward": max_drawdown,
        "outcome_label": outcome_label,
        "warnings": warnings,
        "metadata": copy.deepcopy(metadata) if isinstance(metadata, dict) else {},
    }


def summarize_backtest_samples(samples):
    sample_list = _samples_to_records(samples)
    counts = {label: 0 for label in OUTCOME_LABELS}
    valid_returns = []
    warnings = []
    for sample in sample_list:
        if not isinstance(sample, dict):
            counts["insufficient_data"] += 1
            warnings.append("sample is not a dictionary")
            continue
        label = sample.get("outcome_label") if sample.get("outcome_label") in counts else "insufficient_data"
        counts[label] += 1
        for key in ("forward_return_10d", "forward_return_5d", "forward_return_3d", "forward_return_1d"):
            value = _to_number(sample.get(key))
            if not math.isnan(value):
                valid_returns.append(value)
                break
        warnings.extend(str(item) for item in sample.get("warnings", []) if item)
    total = len(sample_list)
    average_return = None if not valid_returns else round(sum(valid_returns) / len(valid_returns), 6)
    return {
        "total_count": total,
        "outcome_label_counts": counts,
        "outcome_label_ratios": {key: (round(value / total, 4) if total else 0.0) for key, value in counts.items()},
        "outcome_counts": counts,
        "outcome_ratios": {key: (round(value / total, 4) if total else 0.0) for key, value in counts.items()},
        "average_forward_return": average_return,
        "warnings": list(dict.fromkeys(warnings)),
        "metadata": {
            "read_only": True,
            "uses_real_data_source": False,
            "ui_connected": False,
        },
    }


__all__ = [
    "bucket_strategy_score",
    "build_backtest_metrics_summary",
    "build_backtest_sample",
    "calculate_forward_return",
    "classify_backtest_outcome",
    "summarize_backtest_by_consensus_level",
    "summarize_backtest_by_dominant_style",
    "summarize_backtest_by_preset",
    "summarize_backtest_by_score_bucket",
    "summarize_backtest_samples",
    "validate_backtest_input",
]
