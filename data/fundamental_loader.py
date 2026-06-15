"""Real A-share fundamental data loading and cache helpers.

This module standardizes free/public fundamental fields for research-only
analysis. It does not require API keys and never connects to trading services.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests


CACHE_DIR = Path("cache/fundamental")
CACHE_FILE = CACHE_DIR / "fundamental_latest.csv"
MIN_CACHE_ROWS = 100
EASTMONEY_CLIST_URL = "https://push2.eastmoney.com/api/qt/clist/get"

FUNDAMENTAL_OUTPUT_COLUMNS = [
    "ticker",
    "name",
    "pe_ttm",
    "pb",
    "ps_ttm",
    "market_cap",
    "float_market_cap",
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "debt_to_asset",
    "operating_cash_flow",
    "ocf_to_net_profit",
    "dividend_yield",
    "fundamental_data_source",
    "fundamental_data_status",
    "fundamental_data_warning",
    "fundamental_updated_at",
]

NUMERIC_COLUMNS = [
    "pe_ttm",
    "pb",
    "ps_ttm",
    "market_cap",
    "float_market_cap",
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "debt_to_asset",
    "operating_cash_flow",
    "ocf_to_net_profit",
    "dividend_yield",
]

PERCENT_COLUMNS = {
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "debt_to_asset",
    "dividend_yield",
}

FIELD_ALIASES = {
    "ticker": ["ticker", "code", "symbol", "f12", "SECURITY_CODE", "股票代码", "代码"],
    "name": ["name", "stock_name", "code_name", "f14", "SECURITY_NAME_ABBR", "股票简称", "名称"],
    "pe_ttm": ["pe_ttm", "pe", "f9", "PE_TTM", "市盈率", "市盈率TTM"],
    "pb": ["pb", "f23", "PB", "市净率"],
    "ps_ttm": ["ps_ttm", "ps", "PS_TTM", "市销率"],
    "market_cap": ["market_cap", "total_market_cap", "f20", "TOTAL_MARKET_CAP", "总市值"],
    "float_market_cap": ["float_market_cap", "circulating_market_cap", "f21", "FREE_MARKET_CAP", "流通市值"],
    "roe": ["roe", "ROE", "净资产收益率"],
    "roa": ["roa", "ROA", "总资产收益率"],
    "gross_margin": ["gross_margin", "GROSS_MARGIN", "毛利率"],
    "net_margin": ["net_margin", "NET_MARGIN", "净利率"],
    "revenue_growth_yoy": ["revenue_growth_yoy", "revenue_growth", "YOY_SALES", "营业收入同比增长", "营收同比"],
    "net_profit_growth_yoy": ["net_profit_growth_yoy", "net_profit_growth", "profit_growth", "YOY_NETPROFIT", "净利润同比"],
    "debt_to_asset": ["debt_to_asset", "debt_ratio", "DEBT_ASSET_RATIO", "资产负债率"],
    "operating_cash_flow": ["operating_cash_flow", "operating_cashflow", "OPERATE_CASH_FLOW", "经营现金流"],
    "ocf_to_net_profit": ["ocf_to_net_profit", "OCF_TO_NET_PROFIT", "经营现金流净利润比"],
    "dividend_yield": ["dividend_yield", "DIVIDEND_YIELD", "股息率"],
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


def _to_number(value: Any, *, percent: bool = False) -> float | None:
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
    if percent and abs(number) <= 1:
        number *= 100
    return round(number, 4)


def _first_existing(row: dict[str, Any], field: str) -> Any:
    for name in FIELD_ALIASES.get(field, [field]):
        if name in row:
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
    frame = pd.DataFrame(columns=FUNDAMENTAL_OUTPUT_COLUMNS)
    frame.attrs["fundamental_data_status"] = status
    frame.attrs["fundamental_data_source"] = "Unavailable"
    frame.attrs["fundamental_data_warning"] = warning
    frame.attrs["fundamental_updated_at"] = _now_text()
    return frame


def _standardize_frame(source: pd.DataFrame | None, *, data_source: str, data_status: str = "Available", warning: str = "") -> pd.DataFrame:
    if source is None or source.empty:
        return _empty(status="Unavailable", warning=warning)
    rows: list[dict[str, Any]] = []
    for _, item in source.iterrows():
        raw = item.to_dict()
        ticker = _normalize_ticker(_first_existing(raw, "ticker"))
        if not ticker:
            continue
        row: dict[str, Any] = {
            "ticker": ticker,
            "name": _first_existing(raw, "name") or "",
            "fundamental_data_source": raw.get("fundamental_data_source", data_source),
            "fundamental_data_status": raw.get("fundamental_data_status", data_status),
            "fundamental_data_warning": raw.get("fundamental_data_warning", warning),
            "fundamental_updated_at": raw.get("fundamental_updated_at", _now_text()),
        }
        for field in NUMERIC_COLUMNS:
            row[field] = _to_number(_first_existing(raw, field), percent=field in PERCENT_COLUMNS)
        rows.append(row)
    if not rows:
        return _empty(status="Unavailable", warning=warning or "No mappable fundamental rows.")
    frame = pd.DataFrame(rows, columns=FUNDAMENTAL_OUTPUT_COLUMNS)
    frame = frame.drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    frame.attrs["fundamental_data_source"] = data_source
    frame.attrs["fundamental_data_status"] = data_status
    frame.attrs["fundamental_data_warning"] = warning
    frame.attrs["fundamental_updated_at"] = _now_text()
    frame.attrs["fundamental_rows"] = len(frame)
    return frame


def load_fundamental_from_existing_df(df: pd.DataFrame | None) -> pd.DataFrame:
    """Extract fundamental fields already present in a realtime/pipeline DataFrame."""
    return _standardize_frame(df, data_source="Existing DataFrame", data_status="Available", warning="")


def _extract_payload_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    data = payload.get("data", payload)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("diff", "data", "list", "rows"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    for value in payload.values():
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def load_fundamental_from_eastmoney(tickers: list[str] | None = None, timeout: int = 10) -> pd.DataFrame:
    """Load public EastMoney valuation-style fundamental fields.

    The endpoint mainly provides valuation and market-cap fields. The parser is
    intentionally flexible so tests and future endpoint variants can feed richer
    ROE/growth/debt rows through the same standardizer.
    """
    params = {
        "pn": "1",
        "pz": "10000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f9,f23,f20,f21",
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(EASTMONEY_CLIST_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        rows = _extract_payload_rows(response.json())
        frame = _standardize_frame(pd.DataFrame(rows), data_source="EastMoney Fundamental", data_status="Available")
        if tickers and not frame.empty:
            wanted = {_normalize_ticker(ticker) for ticker in tickers}
            frame = frame[frame["ticker"].isin(wanted)].copy(deep=True)
        return frame
    except Exception as exc:
        return _empty(status="Error", warning=repr(exc))


def load_fundamental_from_akshare(tickers: list[str] | None = None, timeout: int = 10) -> pd.DataFrame:
    """Load AkShare fallback data when the optional dependency is available."""
    _ = timeout
    try:
        import akshare as ak

        if hasattr(ak, "stock_zh_a_spot_em"):
            raw = ak.stock_zh_a_spot_em()
        else:
            return _empty(status="Error", warning="akshare stock_zh_a_spot_em is unavailable.")
        frame = _standardize_frame(raw, data_source="AkShare Fundamental", data_status="Available")
        if tickers and not frame.empty:
            wanted = {_normalize_ticker(ticker) for ticker in tickers}
            frame = frame[frame["ticker"].isin(wanted)].copy(deep=True)
        return frame
    except Exception as exc:
        return _empty(status="Error", warning=repr(exc))


def save_cached_fundamental(df: pd.DataFrame | None) -> dict[str, Any]:
    """Persist standardized fundamental data when it is large enough."""
    if df is None or df.empty or len(df) < MIN_CACHE_ROWS:
        return {"cache_status": "Skipped", "cache_path": str(CACHE_FILE), "cache_updated_at": ""}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frame = df.reindex(columns=FUNDAMENTAL_OUTPUT_COLUMNS).copy(deep=True)
    frame.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
    updated_at = _now_text()
    return {"cache_status": "Available", "cache_path": str(CACHE_FILE), "cache_updated_at": updated_at}


def load_cached_fundamental() -> pd.DataFrame:
    """Read cached fundamental data without raising on missing/corrupt files."""
    if not CACHE_FILE.exists():
        return _empty(status="Unavailable", warning="Fundamental cache is missing.")
    try:
        raw = pd.read_csv(CACHE_FILE, dtype={"ticker": str})
        frame = _standardize_frame(raw, data_source="Fundamental Cache", data_status="Cache")
        frame.attrs["cache_status"] = "Available"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        frame.attrs["cache_updated_at"] = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return frame
    except Exception as exc:
        frame = _empty(status="Error", warning=repr(exc))
        frame.attrs["cache_status"] = "Error"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        frame.attrs["cache_updated_at"] = ""
        return frame


def _merge_by_ticker(base: pd.DataFrame, overlay: pd.DataFrame) -> pd.DataFrame:
    if base.empty:
        return overlay.copy(deep=True)
    if overlay.empty:
        return base.copy(deep=True)
    overlay_map = overlay.set_index("ticker").to_dict(orient="index")
    rows: list[dict[str, Any]] = []
    for _, item in base.iterrows():
        row = item.to_dict()
        extra = overlay_map.get(str(row.get("ticker")), {})
        for field, value in extra.items():
            if field == "ticker":
                continue
            if field in NUMERIC_COLUMNS and row.get(field) is not None:
                continue
            if field not in NUMERIC_COLUMNS and row.get(field) not in (None, ""):
                continue
            row[field] = value
        rows.append(row)
    existing = set(base["ticker"].astype(str).tolist()) if "ticker" in base.columns else set()
    for _, item in overlay.iterrows():
        if str(item.get("ticker")) not in existing:
            rows.append(item.to_dict())
    return pd.DataFrame(rows, columns=FUNDAMENTAL_OUTPUT_COLUMNS)


def build_fundamental_dataset(
    existing_df: pd.DataFrame | None = None,
    tickers: list[str] | None = None,
    *,
    timeout: int = 10,
    use_external: bool = True,
) -> pd.DataFrame:
    """Build standardized fundamental data using existing fields, free sources, and cache fallback."""
    base = load_fundamental_from_existing_df(existing_df)
    source_attempts: list[dict[str, Any]] = [
        {
            "data_source": "Existing DataFrame",
            "rows": len(base),
            "data_status": base.attrs.get("fundamental_data_status", "Unavailable"),
            "warning": base.attrs.get("fundamental_data_warning", ""),
        }
    ]
    result = base
    external = pd.DataFrame(columns=FUNDAMENTAL_OUTPUT_COLUMNS)
    if use_external:
        for loader in (load_fundamental_from_eastmoney, load_fundamental_from_akshare):
            external = loader(tickers=tickers, timeout=timeout)
            source_attempts.append(
                {
                    "data_source": external.attrs.get("fundamental_data_source", loader.__name__),
                    "rows": len(external),
                    "data_status": external.attrs.get("fundamental_data_status", "Unavailable"),
                    "warning": external.attrs.get("fundamental_data_warning", ""),
                }
            )
            if not external.empty:
                result = _merge_by_ticker(result, external)
                if len(external) >= MIN_CACHE_ROWS:
                    result.attrs.update(save_cached_fundamental(external))
                break
    if (result.empty or result[NUMERIC_COLUMNS].notna().sum(axis=1).max() < 3) and use_external:
        cached = load_cached_fundamental()
        source_attempts.append(
            {
                "data_source": "Fundamental Cache",
                "rows": len(cached),
                "data_status": cached.attrs.get("fundamental_data_status", "Unavailable"),
                "warning": cached.attrs.get("fundamental_data_warning", ""),
            }
        )
        if not cached.empty:
            result = _merge_by_ticker(result, cached)
            result.attrs.update(cached.attrs)
    result = result.reindex(columns=FUNDAMENTAL_OUTPUT_COLUMNS)
    result.attrs["fundamental_source_attempts"] = source_attempts
    result.attrs["fundamental_data_source"] = result.attrs.get("fundamental_data_source", "Mixed Fundamental")
    result.attrs["fundamental_data_status"] = "Available" if not result.empty else "Unavailable"
    result.attrs["fundamental_rows"] = len(result)
    return result


__all__ = [
    "CACHE_DIR",
    "CACHE_FILE",
    "FUNDAMENTAL_OUTPUT_COLUMNS",
    "build_fundamental_dataset",
    "load_cached_fundamental",
    "load_fundamental_from_akshare",
    "load_fundamental_from_eastmoney",
    "load_fundamental_from_existing_df",
    "save_cached_fundamental",
]
