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
    "research_score",
    "bucket_generation_reason",
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
    ]
    unavailable = pd.Series(False, index=df.index)
    name = _text(df.get("name"), df.index)
    latest_price = _num(df.get("latest_price"), df.index)
    unavailable = unavailable | _bool_series(df.get("is_suspended"), df.index)
    unavailable = unavailable | _bool_series(df.get("is_st"), df.index)
    unavailable = unavailable | name.str.contains("ST|退|退市", case=False, regex=True)
    if "latest_price" in df.columns:
        unavailable = unavailable | latest_price.le(0).fillna(True)
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


def _component_phrase(label: str, value: Any, neutral_message: str | None = None) -> str:
    score = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(score) or 45 <= float(score) <= 55:
        return neutral_message or f"{label} score is neutral due to limited available data."
    if float(score) >= 70:
        return f"{label} score strong."
    if float(score) >= 55:
        return f"{label} score constructive."
    if float(score) >= 40:
        return f"{label} score neutral."
    return f"{label} score weak or requires review."


def _selected_reason(row: pd.Series) -> str:
    return " ".join(
        [
            "Ranked in top research candidates by composite score.",
            _component_phrase(
                "fundamental",
                row.get("fundamental_research_score"),
                "fundamental score is neutral due to limited available fundamental data.",
            ),
            _component_phrase("technical", row.get("real_technical_score")),
            _component_phrase("capital flow", row.get("capital_flow_score")),
        ]
    )


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
    ranked["activated_composite_score"] = final_score
    ranked["research_score"] = final_score
    quality_ok = _quality_available(ranked)
    warning = []
    bucket = []
    bucket_generation_reason = []
    selected_reason = []
    exclude_reason = []
    core_limit = max(0, int(core_limit))
    watch_limit = max(0, int(watch_limit))
    watch_end = core_limit + watch_limit
    core_mask = ranked["research_rank"].le(core_limit) & final_score.ge(55) & quality_ok
    watch_mask = ranked["research_rank"].gt(core_limit) & ranked["research_rank"].le(watch_end) & final_score.ge(50) & quality_ok
    fallback_warning = "Core generated by relative ranking fallback because absolute threshold was too strict."
    usable_count = int(quality_ok.sum())
    fallback_core_indexes: set[Any] = set()
    fallback_watch_indexes: set[Any] = set()
    zero_core_relative_fallback = False
    if usable_count > 0 and int(core_mask.sum()) == 0:
        zero_core_relative_fallback = True
        usable_ranked = ranked[quality_ok]
        fallback_core_count = max(1, int(len(usable_ranked) * 0.10))
        fallback_watch_end = max(fallback_core_count + 1, int(len(usable_ranked) * 0.30)) if len(usable_ranked) > 1 else fallback_core_count
        fallback_core_indexes = set(usable_ranked.head(fallback_core_count).index.tolist())
        fallback_watch_indexes = set(usable_ranked.iloc[fallback_core_count:fallback_watch_end].index.tolist())
    elif usable_count > 0 and int(core_mask.sum()) < min(5, core_limit, usable_count):
        fallback_core_indexes = set(ranked[quality_ok].head(min(core_limit, len(ranked))).index.tolist())

    for row_index, row in ranked.iterrows():
        usable = bool(quality_ok.loc[row_index])
        is_core = bool(core_mask.loc[row_index]) or row_index in fallback_core_indexes
        is_watch = (row_index in fallback_watch_indexes) if zero_core_relative_fallback else bool(watch_mask.loc[row_index])
        if not usable:
            bucket.append("Excluded / Low Priority")
            bucket_generation_reason.append("Absolute Threshold")
            selected_reason.append("")
            exclude_reason.append("Data quality unavailable, severe risk status, suspension/ST/delisting risk, or invalid price.")
            warning.append("Scheduler excluded this row because required data quality was unavailable.")
        elif is_core:
            bucket.append("Core Research")
            bucket_generation_reason.append("Relative Ranking Fallback" if row_index in fallback_core_indexes and not bool(core_mask.loc[row_index]) else "Absolute Threshold")
            selected_reason.append(_selected_reason(row))
            exclude_reason.append("")
            warning.append(fallback_warning if row_index in fallback_core_indexes and not bool(core_mask.loc[row_index]) else "")
        elif is_watch or row_index in fallback_watch_indexes:
            bucket.append("Watch Research")
            bucket_generation_reason.append("Relative Ranking Fallback" if row_index in fallback_watch_indexes else "Absolute Threshold")
            selected_reason.append(_selected_reason(row))
            exclude_reason.append("")
            warning.append(fallback_warning if row_index in fallback_watch_indexes else "")
        else:
            bucket.append("Excluded / Low Priority")
            bucket_generation_reason.append("Relative Ranking Fallback" if fallback_core_indexes else "Absolute Threshold")
            selected_reason.append("")
            exclude_reason.append("Lower relative ranking or insufficient composite score.")
            warning.append("")

    ranked["research_bucket"] = bucket
    ranked["bucket_generation_reason"] = bucket_generation_reason
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
