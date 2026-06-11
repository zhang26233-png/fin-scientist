"""Direct EastMoney realtime A-share quote loader."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import requests


EASTMONEY_URL = "https://push2.eastmoney.com/api/qt/clist/get"
EASTMONEY_FIELDS = "f12,f14,f2,f3,f4,f5,f6,f7,f15,f16,f17,f18"
OUTPUT_COLUMNS = [
    "ticker",
    "name",
    "latest_price",
    "pct_change",
    "change_amount",
    "volume",
    "turnover",
    "amplitude",
    "high",
    "low",
    "open",
    "prev_close",
    "market",
    "data_source",
    "data_status",
    "data_timestamp",
    "data_warning",
]


def _empty(status: str = "Error", warning: str = "", load_time: float = 0.0) -> pd.DataFrame:
    frame = pd.DataFrame(columns=OUTPUT_COLUMNS)
    frame.attrs["data_source"] = "EastMoney Direct"
    frame.attrs["data_status"] = status
    frame.attrs["last_error"] = warning
    frame.attrs["load_time"] = float(load_time)
    frame.attrs["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return frame


def _to_number(value: Any) -> float | None:
    if value in (None, "", "-"):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(number):
        return None
    return number


def _market_from_ticker(ticker: str) -> str:
    if ticker.startswith("688"):
        return "科创板"
    if ticker.startswith("6"):
        return "沪市"
    if ticker.startswith("300"):
        return "创业板"
    if ticker.startswith(("0", "2")):
        return "深市"
    if ticker.startswith(("4", "8", "9")):
        return "北交所"
    return "A股"


def _normalize_row(item: dict[str, Any], timestamp: str) -> dict[str, Any]:
    ticker = str(item.get("f12") or "").strip()
    return {
        "ticker": ticker,
        "name": str(item.get("f14") or "").strip(),
        "latest_price": _to_number(item.get("f2")),
        "pct_change": _to_number(item.get("f3")),
        "change_amount": _to_number(item.get("f4")),
        "volume": _to_number(item.get("f5")),
        "turnover": _to_number(item.get("f6")),
        "amplitude": _to_number(item.get("f7")),
        "high": _to_number(item.get("f15")),
        "low": _to_number(item.get("f16")),
        "open": _to_number(item.get("f17")),
        "prev_close": _to_number(item.get("f18")),
        "market": _market_from_ticker(ticker),
        "data_source": "EastMoney Direct",
        "data_status": "Live",
        "data_timestamp": timestamp,
        "data_warning": "",
    }


def load_eastmoney_a_share_spot(timeout: int = 30) -> pd.DataFrame:
    """Load realtime A-share quotes directly from EastMoney push2."""
    started = datetime.now()
    params = {
        "pn": "1",
        "pz": "6000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": EASTMONEY_FIELDS,
    }
    try:
        response = requests.get(
            EASTMONEY_URL,
            params=params,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 FinScientist/1.0"},
        )
        response.raise_for_status()
        payload = response.json()
        diff = (payload.get("data") or {}).get("diff") or []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = [_normalize_row(item, timestamp) for item in diff if isinstance(item, dict)]
        frame = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
        frame = frame[frame["ticker"].astype(str).str.fullmatch(r"\d{6}", na=False)].copy(deep=True)
        frame = frame.drop_duplicates(subset=["ticker"], keep="first")
        load_time = (datetime.now() - started).total_seconds()
        frame.attrs["data_source"] = "EastMoney Direct"
        frame.attrs["data_status"] = "Live" if len(frame) > 0 else "Error"
        frame.attrs["last_error"] = "" if len(frame) > 0 else "EastMoney returned empty quote rows."
        frame.attrs["load_time"] = load_time
        frame.attrs["updated_at"] = timestamp
        return frame
    except Exception as exc:
        return _empty(warning=repr(exc), load_time=(datetime.now() - started).total_seconds())


__all__ = [
    "EASTMONEY_URL",
    "OUTPUT_COLUMNS",
    "load_eastmoney_a_share_spot",
]
