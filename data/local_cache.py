"""Local CSV cache helpers for A-share realtime/universe data."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


CACHE_DIR = Path("cache")
A_SHARE_UNIVERSE_CACHE = CACHE_DIR / "a_share_universe_latest.csv"
A_SHARE_QUOTES_CACHE = CACHE_DIR / "a_share_quotes_latest.csv"


def _cache_path(cache_type: str) -> Path:
    normalized = str(cache_type).strip().lower()
    if normalized in {"universe", "a_share_universe"}:
        return A_SHARE_UNIVERSE_CACHE
    if normalized in {"quotes", "quote", "a_share_quotes"}:
        return A_SHARE_QUOTES_CACHE
    raise ValueError(f"Unsupported cache_type: {cache_type}")


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _mtime_text(path: Path) -> str:
    if not path.exists():
        return ""
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def cache_metadata() -> dict[str, Any]:
    """Return lightweight cache status for UI display."""
    universe_exists = A_SHARE_UNIVERSE_CACHE.exists()
    quotes_exists = A_SHARE_QUOTES_CACHE.exists()
    updated_at = max(
        [value for value in [_mtime_text(A_SHARE_UNIVERSE_CACHE), _mtime_text(A_SHARE_QUOTES_CACHE)] if value],
        default="",
    )
    return {
        "cache_status": "Available" if universe_exists or quotes_exists else "Missing",
        "cache_updated_at": updated_at,
        "cache_universe_path": str(A_SHARE_UNIVERSE_CACHE),
        "cache_quotes_path": str(A_SHARE_QUOTES_CACHE),
    }


def get_cache_status(cache_type: str) -> dict[str, Any]:
    """Return cache metadata for one cache type."""
    path = _cache_path(cache_type)
    return {
        "cache_status": "Available" if path.exists() else "Missing",
        "cache_updated_at": _mtime_text(path),
        "cache_path": str(path),
    }


def write_frame_cache(frame: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame cache atomically enough for local single-user use."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def write_a_share_cache(*, universe: pd.DataFrame | None = None, quotes: pd.DataFrame | None = None) -> dict[str, Any]:
    """Persist latest A-share universe/quote frames when available."""
    if quotes is not None and not quotes.empty:
        write_frame_cache(quotes, A_SHARE_QUOTES_CACHE)
    if universe is not None and not universe.empty:
        write_frame_cache(universe, A_SHARE_UNIVERSE_CACHE)
    metadata = cache_metadata()
    metadata["cache_written_at"] = _now_text()
    return metadata


def save_a_share_cache(df: pd.DataFrame, cache_type: str) -> dict[str, Any]:
    """Save one A-share cache file by type: universe or quotes."""
    path = _cache_path(cache_type)
    write_frame_cache(df, path)
    status = get_cache_status(cache_type)
    status["cache_written_at"] = _now_text()
    return status


def load_a_share_cache(cache_type: str) -> pd.DataFrame:
    """Load one A-share cache file by type, returning empty on miss/failure."""
    path = _cache_path(cache_type)
    if not path.exists():
        frame = pd.DataFrame()
        frame.attrs.update(get_cache_status(cache_type))
        frame.attrs["last_error"] = "Local cache file is missing."
        return frame
    try:
        frame = pd.read_csv(path, dtype={"ticker": str, "code": str})
    except Exception as exc:
        frame = pd.DataFrame()
        frame.attrs["last_error"] = repr(exc)
    frame.attrs.update(get_cache_status(cache_type))
    return frame


def read_a_share_universe_cache() -> pd.DataFrame:
    """Read the latest cached A-share universe, returning empty on miss/failure."""
    frame = load_a_share_cache("universe")
    frame.attrs.update(cache_metadata())
    return frame


__all__ = [
    "A_SHARE_QUOTES_CACHE",
    "A_SHARE_UNIVERSE_CACHE",
    "CACHE_DIR",
    "cache_metadata",
    "get_cache_status",
    "load_a_share_cache",
    "read_a_share_universe_cache",
    "save_a_share_cache",
    "write_a_share_cache",
    "write_frame_cache",
]
