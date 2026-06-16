"""Capital-flow data foundation with local cache fallback.

The loader is research-only. It uses free/public fields when available and
never requires API keys or trading-account access.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests


CACHE_DIR = Path("cache/capital_flow")
CACHE_FILE = CACHE_DIR / "capital_flow_latest.csv"
MIN_CACHE_ROWS = 50
EASTMONEY_CAPITAL_FLOW_URL = "https://push2.eastmoney.com/api/qt/clist/get"

CAPITAL_FLOW_COLUMNS = [
    "ticker",
    "name",
    "turnover",
    "turnover_rate",
    "volume_ratio",
    "amount_rank",
    "turnover_rank",
    "capital_activity_score",
    "northbound_hold",
    "northbound_change",
    "main_net_inflow",
    "main_net_inflow_ratio",
    "sector_capital_rank",
    "capital_flow_score",
    "capital_flow_summary",
    "capital_flow_warnings",
    "capital_flow_source",
    "capital_flow_status",
    "capital_flow_updated_at",
]

NUMERIC_COLUMNS = [
    "turnover",
    "turnover_rate",
    "volume_ratio",
    "amount_rank",
    "turnover_rank",
    "capital_activity_score",
    "northbound_hold",
    "northbound_change",
    "main_net_inflow",
    "main_net_inflow_ratio",
    "sector_capital_rank",
    "capital_flow_score",
]

FIELD_ALIASES = {
    "ticker": ["ticker", "code", "symbol", "f12", "SECURITY_CODE"],
    "name": ["name", "stock_name", "f14", "SECURITY_NAME_ABBR"],
    "turnover": ["turnover", "amount", "f6", "AMOUNT"],
    "turnover_rate": ["turnover_rate", "f8", "TURNOVERRATE"],
    "volume_ratio": ["volume_ratio", "f10", "VOLUME_RATIO"],
    "main_net_inflow": ["main_net_inflow", "f62", "MAIN_NET_INFLOW"],
    "main_net_inflow_ratio": ["main_net_inflow_ratio", "f184", "MAIN_NET_INFLOW_RATIO"],
    "northbound_hold": ["northbound_hold", "NORTH_HOLD"],
    "northbound_change": ["northbound_change", "NORTH_HOLD_CHANGE"],
    "sector_capital_rank": ["sector_capital_rank", "SECTOR_CAPITAL_RANK"],
}


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
    if value is None or isinstance(value, bool):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value).strip().replace(",", "").replace("%", "")
        if not text or text in {"-", "--", "None", "nan"}:
            return None
        try:
            number = float(text)
        except ValueError:
            return None
    if pd.isna(number):
        return None
    return round(number, 4)


def _first_existing(row: dict[str, Any], field: str) -> Any:
    for name in FIELD_ALIASES.get(field, [field]):
        if name not in row:
            continue
        value = row.get(name)
        if value is None:
            continue
        try:
            if pd.isna(value):
                continue
        except (TypeError, ValueError):
            pass
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _empty(status: str = "Unavailable", warning: str = "") -> pd.DataFrame:
    frame = pd.DataFrame(columns=CAPITAL_FLOW_COLUMNS)
    frame.attrs.update(
        {
            "capital_flow_source": "Unavailable",
            "capital_flow_status": status,
            "capital_flow_warning": warning,
            "capital_flow_rows": 0,
            "capital_flow_updated_at": _now_text(),
        }
    )
    return frame


def _activity_score(turnover: float | None, turnover_rate: float | None, volume_ratio: float | None) -> float:
    score = 50.0
    if turnover is not None:
        normalized = turnover * 10_000 if 0 < turnover < 10_000_000 else turnover
        if normalized >= 1_000_000_000:
            score += 25
        elif normalized >= 300_000_000:
            score += 15
        elif normalized > 0:
            score += 5
    if turnover_rate is not None:
        if turnover_rate >= 8:
            score += 15
        elif turnover_rate >= 3:
            score += 8
    if volume_ratio is not None:
        if volume_ratio >= 2:
            score += 10
        elif volume_ratio >= 1:
            score += 5
    return round(max(0.0, min(100.0, score)), 2)


def _flow_score(activity_score: float, main_net_inflow: float | None, main_net_inflow_ratio: float | None) -> float:
    score = activity_score
    if main_net_inflow is not None:
        if main_net_inflow > 0:
            score += 8
        elif main_net_inflow < 0:
            score -= 8
    if main_net_inflow_ratio is not None:
        score += max(-15.0, min(15.0, main_net_inflow_ratio))
    return round(max(0.0, min(100.0, score)), 2)


def _standardize_frame(source: pd.DataFrame | None, *, data_source: str, data_status: str = "Available", warning: str = "") -> pd.DataFrame:
    if source is None or source.empty:
        return _empty(status="Unavailable", warning=warning)
    rows: list[dict[str, Any]] = []
    for _, item in source.iterrows():
        raw = item.to_dict()
        ticker = _normalize_ticker(_first_existing(raw, "ticker"))
        if not ticker:
            continue
        turnover = _to_number(_first_existing(raw, "turnover"))
        turnover_rate = _to_number(_first_existing(raw, "turnover_rate"))
        volume_ratio = _to_number(_first_existing(raw, "volume_ratio"))
        main_net_inflow = _to_number(_first_existing(raw, "main_net_inflow"))
        main_net_inflow_ratio = _to_number(_first_existing(raw, "main_net_inflow_ratio"))
        activity_score = _to_number(raw.get("capital_activity_score")) or _activity_score(turnover, turnover_rate, volume_ratio)
        flow_score = _to_number(raw.get("capital_flow_score")) or _flow_score(activity_score, main_net_inflow, main_net_inflow_ratio)
        warnings = raw.get("capital_flow_warnings", warning) or ""
        rows.append(
            {
                "ticker": ticker,
                "name": _first_existing(raw, "name") or "",
                "turnover": turnover,
                "turnover_rate": turnover_rate,
                "volume_ratio": volume_ratio,
                "amount_rank": _to_number(raw.get("amount_rank")),
                "turnover_rank": _to_number(raw.get("turnover_rank")),
                "capital_activity_score": activity_score,
                "northbound_hold": _to_number(_first_existing(raw, "northbound_hold")),
                "northbound_change": _to_number(_first_existing(raw, "northbound_change")),
                "main_net_inflow": main_net_inflow,
                "main_net_inflow_ratio": main_net_inflow_ratio,
                "sector_capital_rank": _to_number(_first_existing(raw, "sector_capital_rank")),
                "capital_flow_score": flow_score,
                "capital_flow_summary": raw.get("capital_flow_summary") or "Capital-flow fields are standardized for research review.",
                "capital_flow_warnings": warnings,
                "capital_flow_source": raw.get("capital_flow_source", data_source),
                "capital_flow_status": raw.get("capital_flow_status", data_status),
                "capital_flow_updated_at": raw.get("capital_flow_updated_at", _now_text()),
            }
        )
    if not rows:
        return _empty(status="Unavailable", warning=warning or "No mappable capital-flow rows.")
    frame = pd.DataFrame(rows, columns=CAPITAL_FLOW_COLUMNS).drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    if not frame.empty:
        frame["amount_rank"] = pd.to_numeric(frame["turnover"], errors="coerce").rank(ascending=False, method="min")
        frame["turnover_rank"] = pd.to_numeric(frame["turnover_rate"], errors="coerce").rank(ascending=False, method="min")
    frame.attrs.update(
        {
            "capital_flow_source": data_source,
            "capital_flow_status": data_status,
            "capital_flow_warning": warning,
            "capital_flow_rows": len(frame),
            "capital_flow_updated_at": _now_text(),
        }
    )
    return frame.reindex(columns=CAPITAL_FLOW_COLUMNS)


def load_capital_flow_from_existing_df(df: pd.DataFrame | None) -> pd.DataFrame:
    return _standardize_frame(df, data_source="Existing Realtime Fields", data_status="Available")


def load_capital_flow_from_eastmoney(tickers: list[str] | None = None, timeout: int = 10) -> pd.DataFrame:
    params = {
        "pn": "1",
        "pz": "10000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f62",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f6,f8,f10,f62,f184",
    }
    try:
        response = requests.get(EASTMONEY_CAPITAL_FLOW_URL, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("data", {}).get("diff", []) if isinstance(payload, dict) else []
        frame = _standardize_frame(pd.DataFrame(rows), data_source="EastMoney Capital Flow", data_status="Available")
        if tickers and not frame.empty:
            wanted = {_normalize_ticker(ticker) for ticker in tickers}
            frame = frame[frame["ticker"].isin(wanted)].copy(deep=True)
        return frame
    except Exception as exc:
        return _empty(status="Error", warning=repr(exc))


def load_capital_flow_from_akshare(tickers: list[str] | None = None, timeout: int = 10) -> pd.DataFrame:
    _ = timeout
    try:
        import akshare as ak

        if hasattr(ak, "stock_individual_fund_flow_rank"):
            raw = ak.stock_individual_fund_flow_rank(indicator="今日")
        elif hasattr(ak, "stock_zh_a_spot_em"):
            raw = ak.stock_zh_a_spot_em()
        else:
            return _empty(status="Error", warning="akshare capital-flow interface is unavailable.")
        frame = _standardize_frame(raw, data_source="AkShare Capital Flow", data_status="Available")
        if tickers and not frame.empty:
            wanted = {_normalize_ticker(ticker) for ticker in tickers}
            frame = frame[frame["ticker"].isin(wanted)].copy(deep=True)
        return frame
    except Exception as exc:
        return _empty(status="Error", warning=repr(exc))


def save_cached_capital_flow(df: pd.DataFrame | None) -> dict[str, Any]:
    if df is None or df.empty or len(df) < MIN_CACHE_ROWS:
        return {"cache_status": "Skipped", "cache_path": str(CACHE_FILE), "cache_updated_at": ""}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.reindex(columns=CAPITAL_FLOW_COLUMNS).to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
    return {"cache_status": "Available", "cache_path": str(CACHE_FILE), "cache_updated_at": _now_text()}


def load_cached_capital_flow() -> pd.DataFrame:
    if not CACHE_FILE.exists():
        return _empty(status="Unavailable", warning="Capital-flow cache is missing.")
    try:
        raw = pd.read_csv(CACHE_FILE, dtype={"ticker": str})
        frame = _standardize_frame(raw, data_source="Capital Flow Cache", data_status="Cache")
        frame.attrs["cache_status"] = "Available"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        frame.attrs["cache_updated_at"] = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return frame
    except Exception as exc:
        frame = _empty(status="Error", warning=repr(exc))
        frame.attrs["cache_status"] = "Error"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        return frame


def _merge_by_ticker(base: pd.DataFrame, overlay: pd.DataFrame) -> pd.DataFrame:
    if base.empty:
        return overlay.copy(deep=True)
    if overlay.empty:
        return base.copy(deep=True)
    merged = base.set_index("ticker").combine_first(overlay.set_index("ticker")).reset_index()
    return merged.reindex(columns=CAPITAL_FLOW_COLUMNS)


def build_capital_flow_dataset(
    existing_df: pd.DataFrame | None = None,
    tickers: list[str] | None = None,
    *,
    timeout: int = 10,
    use_external: bool = True,
) -> pd.DataFrame:
    base = load_capital_flow_from_existing_df(existing_df)
    attempts = [
        {
            "data_source": "Existing Realtime Fields",
            "rows": len(base),
            "data_status": base.attrs.get("capital_flow_status", "Unavailable"),
            "warning": base.attrs.get("capital_flow_warning", ""),
        }
    ]
    result = base
    if use_external:
        for loader in (load_capital_flow_from_eastmoney, load_capital_flow_from_akshare):
            external = loader(tickers=tickers, timeout=timeout)
            attempts.append(
                {
                    "data_source": external.attrs.get("capital_flow_source", loader.__name__),
                    "rows": len(external),
                    "data_status": external.attrs.get("capital_flow_status", "Unavailable"),
                    "warning": external.attrs.get("capital_flow_warning", ""),
                }
            )
            if not external.empty:
                result = _merge_by_ticker(result, external)
                result.attrs.update(save_cached_capital_flow(external))
                break
        if result.empty:
            cached = load_cached_capital_flow()
            attempts.append(
                {
                    "data_source": "Capital Flow Cache",
                    "rows": len(cached),
                    "data_status": cached.attrs.get("capital_flow_status", "Unavailable"),
                    "warning": cached.attrs.get("capital_flow_warning", ""),
                }
            )
            if not cached.empty:
                result = cached
    result = result.reindex(columns=CAPITAL_FLOW_COLUMNS)
    result.attrs["capital_flow_attempts"] = attempts
    result.attrs["capital_flow_rows"] = len(result)
    result.attrs["capital_flow_status"] = "Available" if not result.empty else "Unavailable"
    result.attrs["capital_flow_source"] = result.attrs.get("capital_flow_source", "Mixed Capital Flow")
    return result


__all__ = [
    "CACHE_DIR",
    "CACHE_FILE",
    "CAPITAL_FLOW_COLUMNS",
    "build_capital_flow_dataset",
    "load_cached_capital_flow",
    "load_capital_flow_from_akshare",
    "load_capital_flow_from_eastmoney",
    "load_capital_flow_from_existing_df",
    "save_cached_capital_flow",
]
