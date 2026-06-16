"""Unified data-source status center for Fin-Scientist."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from capital_flow.capital_engine import CAPITAL_SCORE_CACHE_FILE
from data.capital_flow_loader import CACHE_FILE as CAPITAL_FLOW_CACHE_FILE
from data.fundamental_loader import CACHE_FILE as FUNDAMENTAL_CACHE_FILE
from data.industry_loader import CACHE_FILE as INDUSTRY_CACHE_FILE
from data.kline_loader import KLINE_CACHE_DIR
from data.local_cache import A_SHARE_QUOTES_CACHE, A_SHARE_UNIVERSE_CACHE, cache_metadata
from data.news_loader import CACHE_FILE as NEWS_CACHE_FILE
from news.event_engine import NEWS_EVENT_CACHE_FILE


SOURCE_STATUS_COLUMNS = [
    "source_name",
    "source_type",
    "status",
    "rows",
    "last_updated",
    "last_error",
    "cache_status",
    "capital_flow_coverage",
    "capital_flow_rows",
    "capital_cache_status",
    "capital_updated_time",
    "news_source_status",
    "news_rows",
    "news_cache_status",
    "news_updated_time",
    "news_last_error",
    "priority",
    "used_in_model",
]


def _mtime(path: Path) -> str:
    if not path.exists():
        return ""
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _cache_status(path: Path) -> str:
    if path.is_dir():
        try:
            return "Available" if any(path.iterdir()) else "Missing"
        except OSError:
            return "Error"
    return "Available" if path.exists() else "Missing"


def _attr_rows(df: pd.DataFrame | None, key: str) -> int:
    if df is None:
        return 0
    try:
        value = getattr(df, "attrs", {}).get(key)
        return int(value) if value is not None else len(df)
    except (TypeError, ValueError):
        return len(df)


def _source_attempt_map(df: pd.DataFrame | None) -> dict[str, dict[str, Any]]:
    attempts = []
    if isinstance(df, pd.DataFrame):
        attempts = list(df.attrs.get("source_attempts", []))
    result: dict[str, dict[str, Any]] = {}
    for item in attempts:
        if isinstance(item, dict):
            result[str(item.get("data_source", ""))] = item
    return result


def _capital_coverage(df: pd.DataFrame) -> float:
    if df.empty or "capital_flow_score" not in df.columns:
        return 0.0
    covered = pd.to_numeric(df["capital_flow_score"], errors="coerce").notna().sum()
    return round(float(covered) / max(len(df), 1), 4)


def _news_rows(df: pd.DataFrame, attrs: dict[str, Any]) -> int:
    if attrs.get("news_rows") is not None:
        try:
            return int(attrs.get("news_rows") or 0)
        except (TypeError, ValueError):
            pass
    if df.empty or "news_event_score" not in df.columns:
        return 0
    return int(pd.to_numeric(df["news_event_score"], errors="coerce").notna().sum())


def _status_row(
    *,
    source_name: str,
    source_type: str,
    status: str,
    rows: int = 0,
    last_updated: str = "",
    last_error: str = "",
    cache_status: str = "Missing",
    capital_flow_coverage: float = 0.0,
    capital_flow_rows: int = 0,
    capital_cache_status: str = "",
    capital_updated_time: str = "",
    news_source_status: str = "",
    news_rows: int = 0,
    news_cache_status: str = "",
    news_updated_time: str = "",
    news_last_error: str = "",
    priority: int = 0,
    used_in_model: bool = False,
) -> dict[str, Any]:
    return {
        "source_name": source_name,
        "source_type": source_type,
        "status": status or "Unavailable",
        "rows": int(rows or 0),
        "last_updated": last_updated,
        "last_error": last_error or "",
        "cache_status": cache_status or "Missing",
        "capital_flow_coverage": float(capital_flow_coverage or 0.0),
        "capital_flow_rows": int(capital_flow_rows or 0),
        "capital_cache_status": capital_cache_status or "",
        "capital_updated_time": capital_updated_time or "",
        "news_source_status": news_source_status or "",
        "news_rows": int(news_rows or 0),
        "news_cache_status": news_cache_status or "",
        "news_updated_time": news_updated_time or "",
        "news_last_error": news_last_error or "",
        "priority": int(priority),
        "used_in_model": bool(used_in_model),
    }


def build_data_source_status(research_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Return the unified data-source status table.

    The function reads only local result metadata and cache metadata; it does
    not call external sources.
    """
    df = research_df if isinstance(research_df, pd.DataFrame) else pd.DataFrame()
    attrs = getattr(df, "attrs", {})
    attempts = _source_attempt_map(df)
    cache = cache_metadata()
    updated_at = str(attrs.get("updated_at", ""))
    capital_rows = int(attrs.get("capital_flow_rows", 0) or 0)
    capital_updated_at = str(
        attrs.get("capital_flow_updated_at")
        or attrs.get("capital_score_cache_updated_at")
        or updated_at
    )
    capital_cache_status = str(attrs.get("capital_score_cache_status") or _cache_status(CAPITAL_SCORE_CACHE_FILE))
    news_rows = _news_rows(df, attrs)
    news_updated_at = str(
        attrs.get("news_updated_at")
        or attrs.get("news_event_cache_updated_at")
        or updated_at
    )
    news_cache_status = str(
        attrs.get("news_event_cache_status")
        or attrs.get("cache_status")
        or _cache_status(NEWS_EVENT_CACHE_FILE)
        or _cache_status(NEWS_CACHE_FILE)
    )
    news_last_error = str(attrs.get("news_warning", ""))

    realtime_rows = len(df) if not df.empty else 0
    rows = []
    realtime_specs = [
        ("Tencent Realtime", 1),
        ("EastMoney Realtime", 2),
        ("Sina Realtime", 3),
    ]
    for source_name, priority in realtime_specs:
        attempt = attempts.get(source_name) or attempts.get("EastMoney Direct" if source_name == "EastMoney Realtime" else source_name) or {}
        is_current = source_name in {attrs.get("data_source"), "EastMoney Realtime" if attrs.get("data_source") == "EastMoney Direct" else ""}
        rows.append(
            _status_row(
                source_name=source_name,
                source_type="Realtime Quote",
                status=str(attempt.get("data_status") or ("Live" if is_current else "Not Tried")),
                rows=int(attempt.get("rows", realtime_rows if is_current else 0) or 0),
                last_updated=updated_at,
                last_error=str(attempt.get("last_error", "")),
                cache_status=str(cache.get("cache_status", "Missing")),
                priority=priority,
                used_in_model=bool(is_current),
            )
        )

    rows.extend(
        [
            _status_row(
                source_name="AkShare Kline",
                source_type="K-Line",
                status=str(attrs.get("kline_status", "Unavailable")),
                rows=int(attrs.get("kline_loaded", 0) or 0),
                last_updated=updated_at,
                last_error="",
                cache_status=_cache_status(KLINE_CACHE_DIR),
                priority=1,
                used_in_model=bool(attrs.get("kline_loaded", 0)),
            ),
            _status_row(
                source_name="EastMoney Fundamental",
                source_type="Fundamental",
                status=str(attrs.get("fundamental_data_status", "Unavailable")),
                rows=_attr_rows(df, "fundamental_rows"),
                last_updated=str(attrs.get("fundamental_updated_at", updated_at)),
                last_error="",
                cache_status=_cache_status(FUNDAMENTAL_CACHE_FILE),
                priority=1,
                used_in_model="fundamental_research_score" in df.columns,
            ),
            _status_row(
                source_name="Capital Flow",
                source_type="Capital Flow",
                status=str(attrs.get("capital_flow_status", "Unavailable")),
                rows=int(attrs.get("capital_flow_rows", 0) or 0),
                last_updated=str(attrs.get("capital_flow_updated_at", updated_at)),
                last_error=str(attrs.get("capital_flow_warning", attrs.get("capital_flow_warnings", ""))),
                cache_status=_cache_status(CAPITAL_FLOW_CACHE_FILE),
                capital_flow_coverage=_capital_coverage(df),
                capital_flow_rows=capital_rows,
                capital_cache_status=capital_cache_status,
                capital_updated_time=capital_updated_at,
                priority=1,
                used_in_model="capital_flow_score" in df.columns,
            ),
            _status_row(
                source_name="News",
                source_type="News/Event",
                status=str(attrs.get("news_status", "Unavailable")),
                rows=int(attrs.get("news_rows", 0) or 0),
                last_updated=str(attrs.get("news_updated_at", updated_at)),
                last_error=news_last_error,
                cache_status=_cache_status(NEWS_CACHE_FILE),
                news_source_status=str(attrs.get("news_status", "Unavailable")),
                news_rows=news_rows,
                news_cache_status=news_cache_status,
                news_updated_time=news_updated_at,
                news_last_error=news_last_error,
                priority=1,
                used_in_model="news_event_score" in df.columns,
            ),
            _status_row(
                source_name="Industry",
                source_type="Industry/Concept",
                status=str(attrs.get("industry_status", "Unavailable")),
                rows=int(attrs.get("industry_rows", 0) or 0),
                last_updated=str(attrs.get("industry_updated_at", updated_at)),
                last_error=str(attrs.get("industry_warning", "")),
                cache_status=_cache_status(INDUSTRY_CACHE_FILE),
                priority=1,
                used_in_model="industry_strength_score" in df.columns,
            ),
            _status_row(
                source_name="Local Cache",
                source_type="Cache",
                status=str(cache.get("cache_status", "Missing")),
                rows=0,
                last_updated=str(cache.get("cache_updated_at", "")),
                last_error="",
                cache_status=str(cache.get("cache_status", "Missing")),
                priority=9,
                used_in_model=attrs.get("data_source") == "Local Cache",
            ),
        ]
    )
    frame = pd.DataFrame(rows, columns=SOURCE_STATUS_COLUMNS)
    frame.attrs["source_status_cache_dir"] = "cache/source_status"
    Path("cache/source_status").mkdir(parents=True, exist_ok=True)
    try:
        frame.to_csv(Path("cache/source_status") / "source_status_latest.csv", index=False, encoding="utf-8-sig")
    except Exception:
        pass
    return frame


__all__ = ["SOURCE_STATUS_COLUMNS", "build_data_source_status"]
