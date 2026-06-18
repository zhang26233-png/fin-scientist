"""Real research-result data checks for calibrated Scheduler output."""

from __future__ import annotations

from typing import Any

import pandas as pd


REAL_DATA_AUDIT_COLUMNS = ["check_name", "status", "value", "audit_note"]


def _copy(df: pd.DataFrame | None) -> pd.DataFrame:
    return df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame()


def _row(check_name: str, status: str, value: Any, audit_note: str) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "status": status,
        "value": value,
        "audit_note": audit_note,
    }


def run_real_data_audit(research_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Validate final research_df availability without producing trading conclusions."""
    source = _copy(research_df)
    rows = len(source)
    score_non_null = (
        int(pd.to_numeric(source["activated_composite_score"], errors="coerce").notna().sum())
        if "activated_composite_score" in source.columns
        else 0
    )
    bucket = source["research_bucket"].fillna("").astype(str) if "research_bucket" in source.columns else pd.Series(dtype=object)
    bucket_non_null = int(bucket.ne("").sum()) if len(bucket) else 0
    core_count = int(bucket.eq("Core Research").sum()) if len(bucket) else 0
    watch_count = int(bucket.eq("Watch Research").sum()) if len(bucket) else 0
    active_count = core_count + watch_count

    result = [
        _row("research_df rows > 0", "PASS" if rows > 0 else "FAIL", rows, "research_df must contain final research rows."),
        _row(
            "activated_composite_score non-null > 0",
            "PASS" if score_non_null > 0 else "FAIL",
            score_non_null,
            "activated_composite_score must be populated for final ranking.",
        ),
        _row(
            "research_bucket non-null > 0",
            "PASS" if bucket_non_null > 0 else "FAIL",
            bucket_non_null,
            "research_bucket must be populated with final research layers.",
        ),
        _row(
            "Core + Watch > 0",
            "PASS" if active_count > 0 else "FAIL",
            active_count,
            "At least one Core or Watch research object is expected when rows are available.",
        ),
        _row(
            "Core count",
            "FAIL" if rows > 0 and core_count == 0 else "PASS",
            core_count,
            "Core cannot be empty when research_df has valid final rows.",
        ),
        _row(
            "Watch count",
            "WARN" if rows > 0 and watch_count == 0 else "PASS",
            watch_count,
            "Watch should normally be present when research_df has final rows.",
        ),
    ]
    return pd.DataFrame(result, columns=REAL_DATA_AUDIT_COLUMNS)


__all__ = ["REAL_DATA_AUDIT_COLUMNS", "run_real_data_audit"]
