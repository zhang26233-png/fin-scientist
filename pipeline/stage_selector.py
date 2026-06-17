"""Stage selectors for the v7 research pipeline scheduler.

The selectors are deterministic, additive, and research-only. They never emit
operational trading language and they never mutate caller DataFrames.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


SCHEDULER_FIELDS = [
    "research_bucket",
    "research_rank",
    "research_pipeline_stage",
    "research_selected_reason",
    "research_exclude_reason",
    "research_scheduler_warning",
]


def _copy(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    return df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame(df).copy(deep=True)


def _num(series: pd.Series | Any, index: pd.Index) -> pd.Series:
    if isinstance(series, pd.Series):
        return pd.to_numeric(series, errors="coerce")
    return pd.Series([None] * len(index), index=index, dtype="float64")


def _text(series: pd.Series | Any, index: pd.Index) -> pd.Series:
    if isinstance(series, pd.Series):
        return series.fillna("").astype(str)
    return pd.Series([""] * len(index), index=index, dtype="object")


def _bool_series(value: pd.Series | Any, index: pd.Index) -> pd.Series:
    if not isinstance(value, pd.Series):
        return pd.Series([False] * len(index), index=index)
    text = value.fillna(False)
    if text.dtype == bool:
        return text.astype(bool)
    return text.astype(str).str.lower().isin({"true", "1", "yes", "y", "是"})


def _normalized_turnover(df: pd.DataFrame) -> pd.Series:
    turnover = _num(df.get("turnover"), df.index)
    return turnover.where(~((turnover > 0) & (turnover < 10_000_000)), turnover * 10_000)


def _quality_available(df: pd.DataFrame) -> pd.Series:
    status_fields = [
        "data_status",
        "status",
        "universe_status",
        "fundamental_data_status",
        "capital_flow_status",
        "news_status",
    ]
    unavailable = pd.Series(False, index=df.index)
    for field in status_fields:
        if field in df.columns:
            unavailable = unavailable | _text(df[field], df.index).str.contains(
                "Error|Unavailable|Suspended|退市|停牌",
                case=False,
                regex=True,
            )
    quote_quality = _num(df.get("quote_quality_score"), df.index)
    if "quote_quality_score" in df.columns:
        unavailable = unavailable | quote_quality.lt(20).fillna(False)
    return ~unavailable


def _stable_top(df: pd.DataFrame, score: pd.Series, limit: int) -> pd.DataFrame:
    result = df.copy(deep=True)
    result["_scheduler_sort_score"] = score.fillna(-1_000_000)
    result["_scheduler_input_order"] = range(len(result))
    result = result.sort_values(
        ["_scheduler_sort_score", "_scheduler_input_order"],
        ascending=[False, True],
        kind="mergesort",
    )
    if limit is not None and int(limit) >= 0:
        result = result.head(int(limit))
    return result.drop(columns=["_scheduler_sort_score", "_scheduler_input_order"])


def select_stage1_candidates(df: pd.DataFrame | None, limit: int = 800) -> pd.DataFrame:
    """Select the full-market quick-scan candidates."""
    source = _copy(df)
    if source.empty:
        return source

    idx = source.index
    name = _text(source.get("name"), idx)
    status = _text(source.get("status"), idx) + " " + _text(source.get("data_status"), idx)
    latest_price = _num(source.get("latest_price"), idx)
    turnover = _normalized_turnover(source)

    valid = pd.Series(True, index=idx)
    valid = valid & ~_bool_series(source.get("is_suspended"), idx)
    valid = valid & ~_bool_series(source.get("is_st"), idx)
    valid = valid & ~name.str.contains("ST|退", case=False, regex=True)
    valid = valid & ~status.str.contains("Suspended|Error|退市|停牌", case=False, regex=True)
    if "latest_price" in source.columns:
        valid = valid & latest_price.gt(0).fillna(False)
    if "turnover" in source.columns:
        valid = valid & turnover.ge(10_000_000).fillna(False)

    filtered = source[valid].copy(deep=True)
    if filtered.empty:
        return filtered

    score = (
        _normalized_turnover(filtered).rank(pct=True).fillna(0) * 35
        + _num(filtered.get("turnover_rate"), filtered.index).rank(pct=True).fillna(0) * 20
        + _num(filtered.get("pct_change"), filtered.index).abs().rank(pct=True).fillna(0) * 15
        + _num(filtered.get("volume_ratio"), filtered.index).rank(pct=True).fillna(0) * 15
        + _num(filtered.get("quote_quality_score"), filtered.index).fillna(50) * 0.15
    )
    result = _stable_top(filtered, score, limit)
    result["research_pipeline_stage"] = "Stage 1"
    return result


def select_stage2_candidates(df: pd.DataFrame | None, limit: int = 300) -> pd.DataFrame:
    """Select technical candidates from Stage 1 output."""
    source = _copy(df)
    if source.empty:
        return source
    score = (
        _num(source.get("real_technical_score"), source.index).fillna(50) * 0.45
        + _num(source.get("momentum_score"), source.index).fillna(50) * 0.20
        + _num(source.get("liquidity_score"), source.index).fillna(50) * 0.15
        + _num(source.get("price_position_score"), source.index).fillna(50) * 0.10
        + _num(source.get("activated_technical_score"), source.index).fillna(50) * 0.10
    )
    result = _stable_top(source, score, limit)
    result["research_pipeline_stage"] = "Stage 2"
    return result


def select_stage3_candidates(df: pd.DataFrame | None, limit: int = 100) -> pd.DataFrame:
    """Select research candidates from technical candidates."""
    source = _copy(df)
    if source.empty:
        return source
    score = (
        _num(source.get("fundamental_research_score"), source.index).fillna(50) * 0.35
        + _num(source.get("capital_flow_score"), source.index).fillna(50) * 0.30
        + _num(source.get("real_technical_score"), source.index).fillna(50) * 0.25
        + _num(source.get("liquidity_score"), source.index).fillna(50) * 0.10
    )
    result = _stable_top(source, score, limit)
    result["research_pipeline_stage"] = "Stage 3"
    return result


def _final_score(df: pd.DataFrame) -> pd.Series:
    activated = _num(df.get("activated_composite_score"), df.index)
    fallback = (
        _num(df.get("fundamental_research_score"), df.index).fillna(50) * 0.30
        + _num(df.get("real_technical_score"), df.index).fillna(50) * 0.30
        + _num(df.get("capital_flow_score"), df.index).fillna(50) * 0.25
        + _num(df.get("news_event_score"), df.index).fillna(50) * 0.10
        + _num(df.get("quote_quality_score"), df.index).fillna(50) * 0.05
    )
    return activated.where(activated.notna(), fallback)


def assign_final_buckets(df: pd.DataFrame | None, core_limit: int = 20, watch_limit: int = 50) -> pd.DataFrame:
    """Assign Core Research, Watch Research, and Excluded / Low Priority buckets."""
    source = _copy(df)
    if source.empty:
        for field in SCHEDULER_FIELDS:
            source[field] = pd.Series(dtype="object")
        return source

    score = _final_score(source)
    ranked = _stable_top(source, score, len(source)).copy(deep=True)
    ranked["research_rank"] = range(1, len(ranked) + 1)
    ranked["research_pipeline_stage"] = "Stage 4"

    final_score = _final_score(ranked)
    quality_ok = _quality_available(ranked)
    warning = []
    bucket = []
    selected_reason = []
    exclude_reason = []
    core_limit = int(core_limit)
    watch_end = int(core_limit) + int(watch_limit)
    for rank, score_value, usable in zip(ranked["research_rank"], final_score, quality_ok):
        if not usable:
            bucket.append("Excluded / Low Priority")
            selected_reason.append("")
            exclude_reason.append("Data quality unavailable or risk status is too high.")
            warning.append("Scheduler excluded this row because required data quality was unavailable.")
        elif rank <= core_limit and score_value >= 70:
            bucket.append("Core Research")
            selected_reason.append("Final research score is above 70 and rank is within the Core research limit.")
            exclude_reason.append("")
            warning.append("")
        elif rank <= watch_end or 55 <= score_value < 70:
            bucket.append("Watch Research")
            selected_reason.append("Research score or rank keeps this object in the Watch research layer.")
            exclude_reason.append("")
            warning.append("")
        else:
            bucket.append("Excluded / Low Priority")
            selected_reason.append("")
            exclude_reason.append("Final research score is below the active research threshold or rank is outside Watch.")
            warning.append("")

    ranked["research_bucket"] = bucket
    ranked["research_selected_reason"] = selected_reason
    ranked["research_exclude_reason"] = exclude_reason
    ranked["research_scheduler_warning"] = warning
    return ranked


__all__ = [
    "SCHEDULER_FIELDS",
    "assign_final_buckets",
    "select_stage1_candidates",
    "select_stage2_candidates",
    "select_stage3_candidates",
]
