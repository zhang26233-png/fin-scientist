"""Independent strategy scoring for research-priority diagnostics."""

import copy
import math

import pandas as pd

from strategy.adapter import build_strategy_diagnostics, infer_field_mapping, to_number


def _clamp_score(value):
    if value is None:
        return 0
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0
    if math.isnan(number):
        return 0
    return max(0, min(100, int(round(number))))


def _read_mapped(row, mapping, key):
    column = mapping.get(key)
    if column is None:
        return None
    return row.get(column)


def _read_any(row, candidates):
    for column in candidates:
        if column in row:
            return row.get(column)
    lowered = {str(column).lower(): column for column in row.index}
    for column in candidates:
        matched = lowered.get(str(column).lower())
        if matched is not None:
            return row.get(matched)
    return None


def _source_metrics_from_frame(source, diagnostics):
    if not isinstance(source, pd.DataFrame) or not diagnostics:
        return diagnostics

    mapping = infer_field_mapping(source)
    enriched = copy.deepcopy(diagnostics)
    for diagnostic, (_, row) in zip(enriched, source.iterrows()):
        if not isinstance(diagnostic, dict):
            continue
        diagnostic["_source_metrics"] = {
            "close": to_number(_read_mapped(row, mapping, "close")),
            "amount": to_number(_read_mapped(row, mapping, "amount")),
            "volume": to_number(_read_mapped(row, mapping, "volume")),
            "return_20d": to_number(_read_mapped(row, mapping, "return_20d")),
            "return_10d": to_number(_read_any(row, ("return_10d", "10d_return", "近 10 日涨跌幅"))),
            "return_5d": to_number(_read_any(row, ("return_5d", "5d_return", "近 5 日涨跌幅", "pct_chg", "recent_return"))),
            "volatility": to_number(_read_mapped(row, mapping, "volatility")),
            "valid_days": to_number(_read_mapped(row, mapping, "valid_days")),
        }
    return enriched


def _extract_diagnostics(source):
    if isinstance(source, pd.DataFrame):
        source_copy = source.copy(deep=True)
        diagnostics = build_strategy_diagnostics(source_copy).get("diagnostics", [])
        return _source_metrics_from_frame(source_copy, diagnostics)
    if isinstance(source, dict):
        if isinstance(source.get("diagnostics"), list):
            return copy.deepcopy(source["diagnostics"])
        if isinstance(source.get("strategy_diagnostics"), list):
            return copy.deepcopy(source["strategy_diagnostics"])
    if isinstance(source, list):
        return copy.deepcopy(source)
    return []


def _factor_score(factor_scores, key):
    if not isinstance(factor_scores, dict):
        return 0
    result = factor_scores.get(key, {})
    if not isinstance(result, dict):
        return 0
    return _clamp_score(result.get("score"))


def _risk_penalty(item):
    penalty = 0
    risk_tags = item.get("risk_tags", []) if isinstance(item, dict) else []
    if not isinstance(risk_tags, list):
        risk_tags = []
    tag_text = " ".join(str(risk.get("tag", "")) for risk in risk_tags if isinstance(risk, dict))
    if "高波动风险" in tag_text:
        penalty += 15
    if "短期涨幅风险" in tag_text:
        penalty += 10
    if "流动性风险" in tag_text or "流动性观察不足" in tag_text:
        penalty += 10
    if "样本不足风险" in tag_text:
        penalty += 10
    if "数据缺失风险" in tag_text or "基本面缺失风险" in tag_text:
        penalty += 10

    source_metrics = item.get("_source_metrics", {}) if isinstance(item, dict) else {}
    if isinstance(source_metrics, dict):
        return_20d = source_metrics.get("return_20d")
        return_10d = source_metrics.get("return_10d")
        return_5d = source_metrics.get("return_5d")
        volatility = source_metrics.get("volatility")
        if isinstance(return_20d, (int, float)) and return_20d > 0.35:
            penalty += 10
        if isinstance(return_10d, (int, float)) and return_10d > 0.25:
            penalty += 10
        if isinstance(return_5d, (int, float)) and return_5d > 0.15:
            penalty += 8
        if isinstance(volatility, (int, float)) and volatility > 0.80:
            penalty += 10

    volatility_score = _factor_score(item.get("factor_scores", {}), "volatility")
    if volatility_score and volatility_score < 40:
        penalty += 10
    return min(50, penalty)


def _data_quality_penalty(item):
    penalty = 0
    factor_scores = item.get("factor_scores", {}) if isinstance(item, dict) else {}
    if isinstance(factor_scores, dict):
        unavailable_count = sum(
            1
            for result in factor_scores.values()
            if not isinstance(result, dict) or result.get("score") == "无法计算"
        )
        penalty += unavailable_count * 8

    filter_flags = item.get("filter_flags", {}) if isinstance(item, dict) else {}
    if isinstance(filter_flags, dict) and filter_flags.get("passed") is False:
        penalty += 15
    return min(45, penalty)


def _liquidity_score(item):
    volume_score = _factor_score(item.get("factor_scores", {}), "volume")
    source_metrics = item.get("_source_metrics", {}) if isinstance(item, dict) else {}
    if isinstance(source_metrics, dict):
        amount = source_metrics.get("amount")
        volume = source_metrics.get("volume")
        if not isinstance(amount, (int, float)) or math.isnan(amount):
            return max(0, volume_score - 20)
        if amount < 5_000_000:
            return min(volume_score, 20)
        if amount < 30_000_000:
            return min(volume_score, 40)
        if isinstance(volume, (int, float)) and not math.isnan(volume) and volume < 100_000:
            return min(volume_score, 35)
        return volume_score

    filter_flags = item.get("filter_flags", {}) if isinstance(item, dict) else {}
    if isinstance(filter_flags, dict) and filter_flags.get("passed") is False:
        return max(0, volume_score - 20)
    return volume_score


def _source_return(source_metrics, *keys):
    if not isinstance(source_metrics, dict):
        return math.nan
    for key in keys:
        value = source_metrics.get(key)
        if isinstance(value, (int, float)) and not math.isnan(value):
            return value
    return math.nan


def _trend_score(item, base_score):
    source_metrics = item.get("_source_metrics", {}) if isinstance(item, dict) else {}
    return_20d = _source_return(source_metrics, "return_20d")
    volatility = _source_return(source_metrics, "volatility")
    score = base_score
    if not math.isnan(return_20d):
        if return_20d > 0.35:
            score = min(max(score, 70), 80)
        elif return_20d > 0.05:
            score = max(score, 75)
        elif return_20d >= -0.05:
            score = min(max(score, 50), 65)
        else:
            score = min(score, 35)
    if not math.isnan(volatility) and volatility > 0.80:
        score = min(score, 70)
    return _clamp_score(score)


def _momentum_score(item, base_score):
    source_metrics = item.get("_source_metrics", {}) if isinstance(item, dict) else {}
    return_20d = _source_return(source_metrics, "return_20d")
    return_10d = _source_return(source_metrics, "return_10d")
    return_5d = _source_return(source_metrics, "return_5d")
    available = [value for value in (return_20d, return_10d, return_5d) if not math.isnan(value)]
    score = base_score
    if available:
        strongest = max(available)
        weakest = min(available)
        if strongest > 0.35:
            score = min(max(score, 55), 65)
        elif strongest > 0.08:
            score = max(score, 70)
        elif strongest >= -0.03:
            score = min(max(score, 45), 60)
        else:
            score = min(score, 30)
        if len(available) >= 2 and weakest < -0.03 and strongest < 0.03:
            score = min(score, 30)
        if return_5d < -0.05 and return_10d < -0.03:
            score = min(score, 25)
    return _clamp_score(score)


def _score_item(item):
    item = item if isinstance(item, dict) else {}
    factor_scores = item.get("factor_scores", {})
    trend_score = _trend_score(item, _factor_score(factor_scores, "trend"))
    momentum_score = _momentum_score(item, _factor_score(factor_scores, "momentum"))
    volume_price_score = _factor_score(factor_scores, "volume")
    liquidity_score = _liquidity_score(item)
    risk_penalty = _risk_penalty(item)
    data_quality_penalty = _data_quality_penalty(item)

    raw_score = (
        trend_score * 0.30
        + momentum_score * 0.25
        + volume_price_score * 0.20
        + liquidity_score * 0.15
        + 50 * 0.10
    )
    strategy_score = _clamp_score(raw_score - risk_penalty - data_quality_penalty)

    return {
        "identity": copy.deepcopy(item.get("identity", {})),
        "trend_score": trend_score,
        "momentum_score": momentum_score,
        "volume_price_score": volume_price_score,
        "liquidity_score": liquidity_score,
        "risk_penalty": risk_penalty,
        "data_quality_penalty": data_quality_penalty,
        "strategy_score": strategy_score,
        "score_note": "策略评分仅用于研究优先级辅助，不构成投资建议。",
    }


def calculate_strategy_scores(source):
    diagnostics = _extract_diagnostics(source)
    if not diagnostics:
        return {
            "status": "empty",
            "scores": [],
            "summary": "输入为空或缺少可识别诊断，未生成策略评分。",
            "metadata": {
                "score_range": "0-100",
                "read_only": True,
                "ranking_changed": False,
                "scoring_changed": False,
            },
        }

    scores = [_score_item(item) for item in diagnostics]
    return {
        "status": "ok",
        "scores": scores,
        "summary": f"已生成 {len(scores)} 条内部策略评分，仅用于研究优先级辅助。",
        "metadata": {
            "score_range": "0-100",
            "read_only": True,
            "ranking_changed": False,
            "scoring_changed": False,
        },
    }


__all__ = [
    "calculate_strategy_scores",
]
