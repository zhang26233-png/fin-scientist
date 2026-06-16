"""Industry and concept data foundation with cache fallback."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


CACHE_DIR = Path("cache/industry")
CACHE_FILE = CACHE_DIR / "industry_latest.csv"
MIN_CACHE_ROWS = 50

INDUSTRY_COLUMNS = [
    "ticker",
    "name",
    "industry",
    "concepts",
    "industry_strength_score",
    "concept_heat_score",
    "industry_rank",
    "concept_rank",
    "industry_source",
    "industry_status",
    "industry_updated_at",
]


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _normalize_ticker(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else None


def _to_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return round(float(str(value).replace(",", "").replace("%", "")), 4)
    except (TypeError, ValueError):
        return None


def _empty(status: str = "Unavailable", warning: str = "") -> pd.DataFrame:
    frame = pd.DataFrame(columns=INDUSTRY_COLUMNS)
    frame.attrs.update({"industry_source": "Unavailable", "industry_status": status, "industry_warning": warning, "industry_rows": 0, "industry_updated_at": _now_text()})
    return frame


def _concept_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        pass
    return [part.strip() for part in str(value).replace(";", ",").replace("|", ",").split(",") if part.strip()]


def _standardize_frame(source: pd.DataFrame | None, *, data_source: str, data_status: str = "Available", warning: str = "") -> pd.DataFrame:
    if source is None or source.empty:
        return _empty(status="Unavailable", warning=warning)
    rows: list[dict[str, Any]] = []
    for _, item in source.iterrows():
        raw = item.to_dict()
        ticker = _normalize_ticker(raw.get("ticker") or raw.get("code") or raw.get("symbol") or raw.get("f12"))
        if not ticker:
            continue
        industry = raw.get("industry") or raw.get("板块") or raw.get("行业") or raw.get("f100") or ""
        concepts = _concept_list(raw.get("concepts") or raw.get("概念") or raw.get("concept"))
        turnover_rate = _to_number(raw.get("turnover_rate"))
        pct_change = _to_number(raw.get("pct_change"))
        strength = _to_number(raw.get("industry_strength_score"))
        if strength is None:
            strength = max(0.0, min(100.0, 50.0 + (pct_change or 0.0) * 2.0 + (turnover_rate or 0.0)))
        heat = _to_number(raw.get("concept_heat_score"))
        if heat is None:
            heat = max(0.0, min(100.0, 50.0 + min(len(concepts), 5) * 5.0))
        rows.append(
            {
                "ticker": ticker,
                "name": raw.get("name") or raw.get("stock_name") or raw.get("f14") or "",
                "industry": industry,
                "concepts": concepts,
                "industry_strength_score": round(strength, 2),
                "concept_heat_score": round(heat, 2),
                "industry_rank": _to_number(raw.get("industry_rank")),
                "concept_rank": _to_number(raw.get("concept_rank")),
                "industry_source": raw.get("industry_source", data_source),
                "industry_status": raw.get("industry_status", data_status),
                "industry_updated_at": raw.get("industry_updated_at", _now_text()),
            }
        )
    if not rows:
        return _empty(status="Unavailable", warning=warning or "No mappable industry rows.")
    frame = pd.DataFrame(rows, columns=INDUSTRY_COLUMNS).drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    frame["industry_rank"] = pd.to_numeric(frame["industry_strength_score"], errors="coerce").rank(ascending=False, method="min")
    frame["concept_rank"] = pd.to_numeric(frame["concept_heat_score"], errors="coerce").rank(ascending=False, method="min")
    frame.attrs.update({"industry_source": data_source, "industry_status": data_status, "industry_warning": warning, "industry_rows": len(frame), "industry_updated_at": _now_text()})
    return frame


def load_industry_from_existing_df(df: pd.DataFrame | None) -> pd.DataFrame:
    return _standardize_frame(df, data_source="Existing Industry Fields", data_status="Available")


def load_industry_from_eastmoney(tickers: list[str] | None = None, timeout: int = 10) -> pd.DataFrame:
    _ = tickers, timeout
    return _empty(status="Unavailable", warning="EastMoney industry source is not available in this local run.")


def load_industry_from_akshare(tickers: list[str] | None = None, timeout: int = 10) -> pd.DataFrame:
    _ = timeout
    try:
        import akshare as ak

        if hasattr(ak, "stock_zh_a_spot_em"):
            raw = ak.stock_zh_a_spot_em()
        else:
            return _empty(status="Error", warning="akshare stock_zh_a_spot_em is unavailable.")
        frame = _standardize_frame(raw, data_source="AkShare Industry", data_status="Available")
        if tickers and not frame.empty:
            wanted = {_normalize_ticker(ticker) for ticker in tickers}
            frame = frame[frame["ticker"].isin(wanted)].copy(deep=True)
        return frame
    except Exception as exc:
        return _empty(status="Error", warning=repr(exc))


def save_cached_industry(df: pd.DataFrame | None) -> dict[str, Any]:
    if df is None or df.empty or len(df) < MIN_CACHE_ROWS:
        return {"cache_status": "Skipped", "cache_path": str(CACHE_FILE), "cache_updated_at": ""}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frame = df.reindex(columns=INDUSTRY_COLUMNS).copy(deep=True)
    frame["concepts"] = frame["concepts"].map(lambda value: ",".join(value) if isinstance(value, list) else value)
    frame.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
    return {"cache_status": "Available", "cache_path": str(CACHE_FILE), "cache_updated_at": _now_text()}


def load_cached_industry() -> pd.DataFrame:
    if not CACHE_FILE.exists():
        return _empty(status="Unavailable", warning="Industry cache is missing.")
    try:
        raw = pd.read_csv(CACHE_FILE, dtype={"ticker": str})
        frame = _standardize_frame(raw, data_source="Industry Cache", data_status="Cache")
        frame.attrs["cache_status"] = "Available"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        frame.attrs["cache_updated_at"] = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return frame
    except Exception as exc:
        frame = _empty(status="Error", warning=repr(exc))
        frame.attrs["cache_status"] = "Error"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        return frame


def build_industry_dataset(existing_df: pd.DataFrame | None = None, tickers: list[str] | None = None, *, timeout: int = 10, use_external: bool = True) -> pd.DataFrame:
    result = load_industry_from_existing_df(existing_df)
    attempts = [{"data_source": "Existing Industry Fields", "rows": len(result), "data_status": result.attrs.get("industry_status", "Unavailable"), "warning": result.attrs.get("industry_warning", "")}]
    if use_external and result.empty:
        for loader in (load_industry_from_eastmoney, load_industry_from_akshare):
            external = loader(tickers=tickers, timeout=timeout)
            attempts.append({"data_source": external.attrs.get("industry_source", loader.__name__), "rows": len(external), "data_status": external.attrs.get("industry_status", "Unavailable"), "warning": external.attrs.get("industry_warning", "")})
            if not external.empty:
                result = external
                result.attrs.update(save_cached_industry(external))
                break
        if result.empty:
            cached = load_cached_industry()
            attempts.append({"data_source": "Industry Cache", "rows": len(cached), "data_status": cached.attrs.get("industry_status", "Unavailable"), "warning": cached.attrs.get("industry_warning", "")})
            if not cached.empty:
                result = cached
    result = result.reindex(columns=INDUSTRY_COLUMNS)
    result.attrs["industry_attempts"] = attempts
    result.attrs["industry_rows"] = len(result)
    result.attrs["industry_status"] = "Available" if not result.empty else "Unavailable"
    result.attrs["industry_source"] = result.attrs.get("industry_source", "Mixed Industry")
    return result


__all__ = [
    "CACHE_DIR",
    "CACHE_FILE",
    "INDUSTRY_COLUMNS",
    "build_industry_dataset",
    "load_cached_industry",
    "load_industry_from_akshare",
    "load_industry_from_eastmoney",
    "load_industry_from_existing_df",
    "save_cached_industry",
]
