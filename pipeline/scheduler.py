"""Research pipeline scheduler for staged A-share research runs."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Callable
import importlib

import pandas as pd

from pipeline.runtime_monitor import PipelineRunReport, SCHEDULER_REPORT_COLUMNS
from pipeline.stage_selector import (
    SCHEDULER_FIELDS,
    assign_final_buckets,
    select_stage1_candidates,
    select_stage2_candidates,
    select_stage3_candidates,
)
from research.research_explainer import build_research_explanation
from research.score_activation import activate_research_scores
from research.unified_ranking_engine import build_unified_research_score
from technical.indicator_engine import REAL_TECHNICAL_INDICATOR_FIELDS
from fundamental.fundamental_engine import FUNDAMENTAL_RESEARCH_FIELDS
from capital_flow.capital_engine import CAPITAL_ENGINE_FIELDS


SCHEDULER_CACHE_DIR = Path("cache/scheduler")
SCHEDULER_REPORT_CACHE = SCHEDULER_CACHE_DIR / "latest_scheduler_report.csv"
SCHEDULER_RESULT_CACHE = SCHEDULER_CACHE_DIR / "latest_research_result.csv"
REQUIRED_RESULT_CACHE_FIELDS = [
    "ticker",
    "name",
    "activated_composite_score",
    "unified_research_score",
    "research_summary",
    "research_rank",
    "research_score",
    "research_bucket",
]


def _copy(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    return df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame(df).copy(deep=True)


def _ensure_scheduler_fields(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)
    for field in SCHEDULER_FIELDS:
        if field not in result.columns:
            result[field] = None
    return result


def _save_cache(result: pd.DataFrame, report: pd.DataFrame) -> None:
    try:
        SCHEDULER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        result.to_csv(SCHEDULER_RESULT_CACHE, index=False, encoding="utf-8-sig")
        report.to_csv(SCHEDULER_REPORT_CACHE, index=False, encoding="utf-8-sig")
    except Exception:
        pass


def _final_summary(df: pd.DataFrame) -> dict[str, object]:
    source = _copy(df)
    bucket = source["research_bucket"].fillna("").astype(str) if "research_bucket" in source.columns else pd.Series(dtype=object)
    score_field = "unified_research_score" if "unified_research_score" in source.columns else "activated_composite_score"
    score = pd.to_numeric(source[score_field], errors="coerce") if score_field in source.columns else pd.Series(dtype=float)
    distribution = bucket.value_counts().to_dict() if len(bucket) else {}
    return {
        "rows": int(len(source)),
        "final_rows": int(len(source)),
        "core_count": int(bucket.eq("Core Research").sum()) if len(bucket) else 0,
        "watch_count": int(bucket.eq("Watch Research").sum()) if len(bucket) else 0,
        "exclude_count": int(bucket.eq("Excluded / Low Priority").sum()) if len(bucket) else 0,
        "max_score": round(float(score.max()), 4) if not score.dropna().empty else None,
        "min_score": round(float(score.min()), 4) if not score.dropna().empty else None,
        "mean_score": round(float(score.mean()), 4) if not score.dropna().empty else None,
        "bucket_distribution": str(distribution),
    }


def _overlay_by_ticker(target: pd.DataFrame, overlay: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if target.empty or overlay.empty or "ticker" not in target.columns or "ticker" not in overlay.columns:
        return target
    result = target.copy(deep=True)
    value_columns = [column for column in columns if column in overlay.columns and column != "ticker"]
    if not value_columns:
        return result
    right = overlay[["ticker", *value_columns]].drop_duplicates(subset=["ticker"], keep="first").copy(deep=True)
    merged = result.merge(right, on="ticker", how="left", suffixes=("", "_scheduler_stage"))
    for column in value_columns:
        stage_column = f"{column}_scheduler_stage"
        if stage_column not in merged.columns:
            continue
        if column in merged.columns:
            merged[column] = merged[stage_column].combine_first(merged[column])
            if column == "technical_history_available":
                merged[column] = merged[stage_column].where(merged[stage_column].notna(), merged[column])
        else:
            merged[column] = merged[stage_column]
        merged = merged.drop(columns=[stage_column])
    return merged


def load_scheduler_cache() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the latest scheduler result and report cache if available."""
    result = pd.DataFrame()
    report = pd.DataFrame(columns=SCHEDULER_REPORT_COLUMNS)
    cache_valid = True
    try:
        if SCHEDULER_RESULT_CACHE.exists():
            result = pd.read_csv(SCHEDULER_RESULT_CACHE, dtype={"ticker": str})
            missing = [field for field in REQUIRED_RESULT_CACHE_FIELDS if field not in result.columns]
            if missing:
                result = pd.DataFrame()
                cache_valid = False
    except Exception:
        result = pd.DataFrame()
        cache_valid = False
    try:
        if cache_valid and SCHEDULER_REPORT_CACHE.exists():
            report = pd.read_csv(SCHEDULER_REPORT_CACHE)
    except Exception:
        report = pd.DataFrame(columns=SCHEDULER_REPORT_COLUMNS)
    return result, report


def _run_stage(
    report: PipelineRunReport,
    stage_name: str,
    source: pd.DataFrame,
    fn: Callable[[pd.DataFrame], pd.DataFrame],
    *,
    timeout_per_stage: int,
) -> pd.DataFrame:
    started = perf_counter()
    input_rows = len(source)
    warning = ""
    status = "OK"
    try:
        result = fn(source.copy(deep=True))
        if not isinstance(result, pd.DataFrame):
            result = pd.DataFrame(result)
    except Exception as exc:
        result = source.copy(deep=True)
        status = "Warning"
        warning = f"{stage_name} failed and degraded to prior stage output: {exc}"
    seconds = perf_counter() - started
    if timeout_per_stage and seconds > float(timeout_per_stage):
        status = "Warning" if status == "OK" else status
        extra = f"{stage_name} exceeded timeout target {timeout_per_stage}s."
        warning = f"{warning} {extra}".strip()
    report.add_stage(stage_name, input_rows, len(result), seconds, status, warning)
    if warning:
        result = result.copy(deep=True)
        existing = result.get("research_scheduler_warning")
        if isinstance(existing, pd.Series):
            result["research_scheduler_warning"] = existing.fillna("").astype(str).map(
                lambda value: f"{value}; {warning}".strip("; ") if value else warning
            )
        else:
            result["research_scheduler_warning"] = warning
    return result


def _scheduled_full_run(
    source: pd.DataFrame,
    *,
    enable_kline: bool,
    enable_fundamental: bool,
    enable_capital_flow: bool,
    enable_news: bool,
    enable_industry: bool,
    stage_limit: int,
) -> pd.DataFrame:
    """Run the existing rich pipeline on a bounded scheduler subset."""
    live_runner = importlib.import_module("pipeline.live_runner")

    return live_runner._run_pipeline(
        source,
        fundamental_df=None,
        price_history_dict=None,
        kline_enabled=enable_kline,
        max_kline_stocks=max(0, int(stage_limit)),
        fundamental_enabled=enable_fundamental,
        capital_flow_enabled=enable_capital_flow,
        news_enabled=enable_news,
        news_event_enabled=enable_news,
        industry_enabled=enable_industry,
        max_news_stocks=max(0, int(stage_limit)),
        max_capital_flow_stocks=max(0, int(stage_limit)),
        max_industry_stocks=max(0, int(stage_limit)),
    )


def run_scheduled_pipeline(
    universe_df,
    stage1_limit=800,
    stage2_limit=300,
    stage3_limit=100,
    core_limit=20,
    watch_limit=50,
    enable_kline=True,
    enable_fundamental=True,
    enable_capital_flow=True,
    enable_news=True,
    enable_industry=True,
    max_kline_stocks=None,
    timeout_per_stage=60,
):
    """Run the staged v7 scheduler and return the final research DataFrame."""
    source = _copy(universe_df)
    source_attrs = dict(getattr(universe_df, "attrs", {}))
    report = PipelineRunReport()

    if source.empty:
        empty = assign_final_buckets(source, core_limit=core_limit, watch_limit=watch_limit)
        report.add_stage("Stage 1: Full Market Quick Scan", 0, 0, 0.0, "OK", "Input universe is empty.")
        report.add_stage("Stage 2: Technical Filter", 0, 0, 0.0, "OK", "Skipped because prior stage is empty.")
        report.add_stage("Stage 3: Research Scoring", 0, 0, 0.0, "OK", "Skipped because prior stage is empty.")
        report.add_stage("Stage 4: Deep Event Layer", 0, 0, 0.0, "OK", "Skipped because prior stage is empty.")
        report.finish("Empty input universe.")
        report.set_final_summary(_final_summary(empty))
        scheduler_report_df = report.to_dataframe()
        empty.attrs.update(source_attrs)
        empty.attrs["scheduler_report_df"] = scheduler_report_df
        empty.attrs["pipeline_mode"] = "Scheduler"
        empty.attrs["scheduler_status"] = "OK"
        empty.attrs["scheduler_total_seconds"] = report.total_seconds
        return empty

    stage1 = _run_stage(
        report,
        "Stage 1: Full Market Quick Scan",
        source,
        lambda frame: select_stage1_candidates(activate_research_scores(frame), limit=stage1_limit),
        timeout_per_stage=timeout_per_stage,
    )

    stage2_input = stage1
    stage2 = _run_stage(
        report,
        "Stage 2: Technical Filter",
        stage2_input,
        lambda frame: select_stage2_candidates(
            _scheduled_full_run(
                frame,
                enable_kline=enable_kline,
                enable_fundamental=False,
                enable_capital_flow=False,
                enable_news=False,
                enable_industry=False,
                stage_limit=max_kline_stocks if max_kline_stocks is not None else stage2_limit,
            ),
            limit=stage2_limit,
        ),
        timeout_per_stage=timeout_per_stage,
    )

    stage3 = _run_stage(
        report,
        "Stage 3: Research Scoring",
        stage2,
        lambda frame: select_stage3_candidates(
            _scheduled_full_run(
                frame,
                enable_kline=False,
                enable_fundamental=enable_fundamental,
                enable_capital_flow=enable_capital_flow,
                enable_news=False,
                enable_industry=enable_industry,
                stage_limit=stage3_limit,
            ),
            limit=stage3_limit,
        ),
        timeout_per_stage=timeout_per_stage,
    )

    stage4 = _run_stage(
        report,
        "Stage 4: Deep Event Layer",
        stage3,
        lambda frame: assign_final_buckets(
            _scheduled_full_run(
                frame,
                enable_kline=False,
                enable_fundamental=enable_fundamental,
                enable_capital_flow=False,
                enable_news=enable_news,
                enable_industry=False,
                stage_limit=stage3_limit,
            ),
            core_limit=core_limit,
            watch_limit=watch_limit,
        ),
        timeout_per_stage=timeout_per_stage,
    )

    final_result = _overlay_by_ticker(stage4, stage2, REAL_TECHNICAL_INDICATOR_FIELDS)
    final_result = _overlay_by_ticker(final_result, stage3, FUNDAMENTAL_RESEARCH_FIELDS + CAPITAL_ENGINE_FIELDS)
    final_result = _ensure_scheduler_fields(final_result)
    final_result = build_unified_research_score(final_result)
    final_result = build_research_explanation(final_result)
    final_result = assign_final_buckets(final_result, core_limit=core_limit, watch_limit=watch_limit)
    final_result.attrs.update(source_attrs)
    for key in [
        "kline_enabled",
        "kline_max_stocks",
        "kline_requested",
        "kline_loaded",
        "kline_cache_hits",
        "kline_failures",
        "kline_status",
        "kline_attempts",
    ]:
        if key in stage2.attrs:
            final_result.attrs[key] = stage2.attrs.get(key)
    for key in [
        "fundamental_enabled",
        "fundamental_data_source",
        "fundamental_data_status",
        "fundamental_rows",
        "fundamental_source_attempts",
        "capital_flow_enabled",
        "capital_flow_source",
        "capital_flow_status",
        "capital_flow_rows",
        "capital_flow_attempts",
        "industry_enabled",
        "industry_source",
        "industry_status",
        "industry_rows",
        "industry_attempts",
    ]:
        if key in stage3.attrs:
            final_result.attrs[key] = stage3.attrs.get(key)
    for key in ["news_enabled", "news_event_enabled", "news_source", "news_status", "news_rows", "news_warning", "news_updated_at", "news_event_cache_status", "news_event_cache_path", "news_attempts"]:
        if key in stage4.attrs:
            final_result.attrs[key] = stage4.attrs.get(key)
    report.set_final_summary(_final_summary(final_result))
    report.finish(
        f"source={source_attrs.get('data_source', 'Unknown')}; status={source_attrs.get('data_status', 'Unknown')}; input_rows={len(source)}"
    )
    scheduler_report_df = report.to_dataframe()
    final_result.attrs["pipeline_mode"] = "Scheduler"
    final_result.attrs["scheduler_status"] = "OK"
    final_result.attrs["scheduler_run_id"] = report.run_id
    final_result.attrs["scheduler_total_seconds"] = report.total_seconds
    final_result.attrs["scheduler_report_df"] = scheduler_report_df
    final_result.attrs["scheduler_stage1_rows"] = len(stage1)
    final_result.attrs["scheduler_stage2_rows"] = len(stage2)
    final_result.attrs["scheduler_stage3_rows"] = len(stage3)
    summary = _final_summary(final_result)
    final_result.attrs["scheduler_core_count"] = int(summary["core_count"])
    final_result.attrs["scheduler_watch_count"] = int(summary["watch_count"])
    final_result.attrs["scheduler_exclude_count"] = int(summary["exclude_count"])
    final_result.attrs["scheduler_final_summary"] = summary
    _save_cache(final_result, scheduler_report_df)
    return final_result


__all__ = [
    "SCHEDULER_CACHE_DIR",
    "SCHEDULER_REPORT_CACHE",
    "SCHEDULER_RESULT_CACHE",
    "load_scheduler_cache",
    "run_scheduled_pipeline",
]
