"""System-level release candidate checks for Fin-Scientist."""

from __future__ import annotations

from typing import Any

import pandas as pd

from audit.module_audit import run_module_audit
from audit.ui_audit import run_ui_audit
from data.source_center import build_data_source_status
from pipeline.runtime_monitor import SCHEDULER_REPORT_COLUMNS
from pipeline.scheduler import load_scheduler_cache


REQUIRED_RESEARCH_FIELDS = [
    "ticker",
    "name",
    "latest_price",
    "pct_change",
    "turnover",
    "turnover_rate",
    "volume_ratio",
    "real_technical_score",
    "fundamental_research_score",
    "capital_flow_score",
    "news_event_score",
    "industry_strength_score",
    "activated_composite_score",
    "research_bucket",
    "research_rank",
    "research_selected_reason",
    "research_scheduler_warning",
]

DATA_FIELD_AUDIT_COLUMNS = ["field_name", "status", "present", "non_null_rows", "audit_note"]
PIPELINE_AUDIT_COLUMNS = ["stage_name", "input_rows", "output_rows", "stage_seconds", "status", "warning"]


def _copy(df: pd.DataFrame | None) -> pd.DataFrame:
    return df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame()


def _normalize_status(value: Any) -> str:
    text = str(value or "").upper()
    if text in {"OK", "PASS"}:
        return "PASS"
    if text in {"WARNING", "WARN", "CACHE FALLBACK"}:
        return "WARN"
    if text in {"FAIL", "FAILED", "ERROR"}:
        return "FAIL"
    return "WARN" if text else "WARN"


def _overall_status(frames: list[pd.DataFrame], status_column: str = "status") -> str:
    statuses: list[str] = []
    for frame in frames:
        if isinstance(frame, pd.DataFrame) and status_column in frame.columns:
            statuses.extend(str(value).upper() for value in frame[status_column].tolist())
    if any(value == "FAIL" for value in statuses):
        return "FAIL"
    if any(value == "WARN" for value in statuses):
        return "WARN"
    return "PASS"


def run_data_field_audit(research_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Check the final research DataFrame field contract without crashing on gaps."""
    source = _copy(research_df)
    rows: list[dict[str, Any]] = []
    for field in REQUIRED_RESEARCH_FIELDS:
        present = field in source.columns
        non_null = int(source[field].notna().sum()) if present and not source.empty else 0
        if present and (source.empty or non_null > 0):
            status = "PASS"
            note = "Field is present."
        elif present:
            status = "WARN"
            note = "Field exists but has no non-null values."
        else:
            status = "WARN"
            note = "Required release-check field is missing."
        rows.append(
            {
                "field_name": field,
                "status": status,
                "present": bool(present),
                "non_null_rows": non_null,
                "audit_note": note,
            }
        )
    return pd.DataFrame(rows, columns=DATA_FIELD_AUDIT_COLUMNS)


def _pipeline_report_from_attrs(source: pd.DataFrame) -> pd.DataFrame:
    report = getattr(source, "attrs", {}).get("scheduler_report_df")
    if isinstance(report, pd.DataFrame) and not report.empty:
        return report.copy(deep=True)
    return pd.DataFrame(columns=SCHEDULER_REPORT_COLUMNS)


def _build_stage_rows(report: pd.DataFrame, warning_prefix: str = "") -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in report.iterrows():
        stage_input = int(row.get("stage_input_rows", 0) or 0)
        stage_output = int(row.get("stage_output_rows", 0) or 0)
        warning = str(row.get("stage_warning", "") or "")
        if stage_input > 0 and stage_output == stage_input:
            warning = f"{warning}; output_rows equals input_rows, verify selector narrowing." if warning else "output_rows equals input_rows, verify selector narrowing."
        rows.append(
            {
                "stage_name": row.get("stage_name", ""),
                "input_rows": stage_input,
                "output_rows": stage_output,
                "stage_seconds": row.get("stage_seconds", 0),
                "status": _normalize_status(row.get("stage_status", "OK")) if not warning_prefix else "WARN",
                "warning": f"{warning_prefix}{warning}".strip(),
            }
        )
    return pd.DataFrame(rows, columns=PIPELINE_AUDIT_COLUMNS)


def _empty_pipeline_report(message: str) -> pd.DataFrame:
    stages = [
        "Stage 1: Full Market Quick Scan",
        "Stage 2: Technical Filter",
        "Stage 3: Research Scoring",
        "Stage 4: Deep Event Layer",
    ]
    return pd.DataFrame(
        [
            {
                "stage_name": stage,
                "input_rows": 0,
                "output_rows": 0,
                "stage_seconds": 0.0,
                "status": "WARN",
                "warning": message,
            }
            for stage in stages
        ],
        columns=PIPELINE_AUDIT_COLUMNS,
    )


def run_pipeline_audit(research_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Validate Scheduler stages, cache fallback, and final bucket generation."""
    source = _copy(research_df)
    report = _pipeline_report_from_attrs(source)
    warning_prefix = ""
    if report.empty:
        cached_result, cached_report = load_scheduler_cache()
        if not cached_report.empty:
            source = cached_result
            report = cached_report
            warning_prefix = "Scheduler report loaded from cache. "
        else:
            return _empty_pipeline_report("Scheduler report is unavailable and no cache fallback was found.")

    result = _build_stage_rows(report, warning_prefix=warning_prefix)
    bucket = source["research_bucket"].fillna("") if "research_bucket" in source.columns else pd.Series(dtype=object)
    has_core = bool(bucket.eq("Core Research").any())
    has_watch = bool(bucket.eq("Watch Research").any())
    has_exclude = bool(bucket.eq("Excluded / Low Priority").any())
    if not (has_core and has_watch and has_exclude):
        note = "Core / Watch / Exclude buckets are not all present."
        result.loc[:, "status"] = result["status"].map(lambda value: "FAIL" if value == "FAIL" else "WARN")
        result.loc[:, "warning"] = result["warning"].map(lambda value: f"{value}; {note}".strip("; ") if value else note)
    return result


def run_system_audit(research_df: pd.DataFrame | None = None) -> dict[str, Any]:
    """Run module, field, pipeline, UI, and data-source audits."""
    source = _copy(research_df)
    module_audit = run_module_audit(source)
    field_audit = run_data_field_audit(source)
    pipeline_audit = run_pipeline_audit(source)
    ui_audit = run_ui_audit(source)
    data_source_status = build_data_source_status(source)
    overall = _overall_status([module_audit, field_audit, pipeline_audit, ui_audit])
    result_status = "Unavailable"
    if not source.empty and {"research_bucket", "research_rank"}.issubset(source.columns):
        result_status = "Available"
    elif not source.empty:
        result_status = "Partial"
    return {
        "system_status": overall,
        "research_result_status": result_status,
        "module_audit": module_audit,
        "data_field_audit": field_audit,
        "pipeline_audit": pipeline_audit,
        "ui_audit": ui_audit,
        "data_source_status": data_source_status,
    }


__all__ = [
    "DATA_FIELD_AUDIT_COLUMNS",
    "PIPELINE_AUDIT_COLUMNS",
    "REQUIRED_RESEARCH_FIELDS",
    "run_data_field_audit",
    "run_pipeline_audit",
    "run_system_audit",
]
