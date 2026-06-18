"""Audit final Scheduler bucket counts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from pipeline.scheduler import SCHEDULER_RESULT_CACHE


SCHEDULER_BUCKET_AUDIT_CACHE = Path("cache/audit/latest_scheduler_bucket_audit.csv")


def _load_result(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype={"ticker": str})
    except Exception:
        return pd.DataFrame()


def audit_scheduler_buckets(path: str | Path | None = None, research_df: pd.DataFrame | None = None) -> dict[str, Any]:
    """Count Core, Watch, and Excluded rows from final research_bucket."""
    target = Path(path) if path is not None else SCHEDULER_RESULT_CACHE
    source = research_df.copy(deep=True) if isinstance(research_df, pd.DataFrame) else _load_result(target)
    bucket = source["research_bucket"].fillna("").astype(str) if "research_bucket" in source.columns else pd.Series(dtype=object)
    result = {
        "rows": int(len(source)),
        "core_count": int(bucket.eq("Core Research").sum()) if len(bucket) else 0,
        "watch_count": int(bucket.eq("Watch Research").sum()) if len(bucket) else 0,
        "exclude_count": int(bucket.isin(["Excluded", "Excluded / Low Priority"]).sum()) if len(bucket) else 0,
    }
    SCHEDULER_BUCKET_AUDIT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result]).to_csv(SCHEDULER_BUCKET_AUDIT_CACHE, index=False, encoding="utf-8-sig")
    return result


__all__ = ["SCHEDULER_BUCKET_AUDIT_CACHE", "audit_scheduler_buckets"]
