"""Audit the persisted Scheduler research result cache."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from pipeline.scheduler import SCHEDULER_RESULT_CACHE


RESEARCH_RESULT_AUDIT_CACHE = Path("cache/audit/latest_research_result_audit.csv")
RESEARCH_RESULT_REQUIRED_FIELDS = [
    "ticker",
    "name",
    "activated_composite_score",
    "research_rank",
    "research_bucket",
]


def _load_result(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype={"ticker": str})
    except Exception:
        return pd.DataFrame()


def audit_research_result(path: str | Path | None = None, research_df: pd.DataFrame | None = None) -> dict[str, Any]:
    """Check latest_research_result.csv and write a one-row audit CSV."""
    target = Path(path) if path is not None else SCHEDULER_RESULT_CACHE
    source = research_df.copy(deep=True) if isinstance(research_df, pd.DataFrame) else _load_result(target)
    missing_fields = [field for field in RESEARCH_RESULT_REQUIRED_FIELDS if field not in source.columns]
    bucket_distribution = (
        source["research_bucket"].fillna("").astype(str).value_counts().to_dict()
        if not source.empty and "research_bucket" in source.columns
        else {}
    )
    result = {
        "path": str(target),
        "exists": bool(target.exists()) if research_df is None else True,
        "rows": int(len(source)),
        "missing_fields": ", ".join(missing_fields),
        "bucket_distribution": str(bucket_distribution),
    }
    RESEARCH_RESULT_AUDIT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result]).to_csv(RESEARCH_RESULT_AUDIT_CACHE, index=False, encoding="utf-8-sig")
    return result


__all__ = ["RESEARCH_RESULT_AUDIT_CACHE", "RESEARCH_RESULT_REQUIRED_FIELDS", "audit_research_result"]
