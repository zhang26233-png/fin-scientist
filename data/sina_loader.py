"""Sina realtime A-share quote loader with bounded requests."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import json
import re
import time

import pandas as pd
import requests


SINA_HQ_URL = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
OUTPUT_COLUMNS = [
    "ticker",
    "name",
    "latest_price",
    "pct_change",
    "change_amount",
    "volume",
    "turnover",
    "open",
    "high",
    "low",
    "prev_close",
    "market",
    "data_source",
    "data_status",
    "data_timestamp",
    "data_warning",
]


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _to_number(value: Any) -> float | None:
    if value in (None, "", "-", "--"):
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


def _attach_attrs(
    frame: pd.DataFrame,
    *,
    started: datetime,
    status: str,
    warning: str = "",
    attempts: list[dict[str, Any]] | None = None,
) -> pd.DataFrame:
    frame.attrs["data_source"] = "Sina Realtime"
    frame.attrs["data_status"] = status
    frame.attrs["load_time"] = (datetime.now() - started).total_seconds()
    frame.attrs["updated_at"] = _now_text()
    frame.attrs["last_error"] = warning
    frame.attrs["endpoint_attempts"] = list(attempts or [])
    return frame


def _empty(started: datetime, warning: str, attempts: list[dict[str, Any]] | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(columns=OUTPUT_COLUMNS)
    return _attach_attrs(frame, started=started, status="Error", warning=warning, attempts=attempts or [])


def _parse_sina_payload(text: str) -> list[Any]:
    stripped = text.strip()
    if not stripped:
        return []
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    normalized = re.sub(r"([{,])\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', stripped)
    normalized = normalized.replace("'", '"')
    return json.loads(normalized)


def _normalize_row(item: dict[str, Any], timestamp: str) -> tuple[dict[str, Any] | None, str]:
    symbol = str(item.get("symbol") or item.get("code") or "").strip()
    digits = "".join(ch for ch in symbol if ch.isdigit())
    ticker = digits[-6:] if len(digits) >= 6 else ""
    name = str(item.get("name") or "").strip()
    if not ticker:
        return None, "missing symbol ticker"
    if not name:
        return None, f"{ticker}: missing name"
    latest = _to_number(item.get("trade") or item.get("price") or item.get("settlement"))
    prev_close = _to_number(item.get("settlement") or item.get("prev_close"))
    change_amount = _to_number(item.get("pricechange") or item.get("change_amount"))
    pct_change = _to_number(item.get("changepercent") or item.get("pct_change"))
    return (
        {
            "ticker": ticker,
            "name": name,
            "latest_price": latest,
            "pct_change": pct_change,
            "change_amount": change_amount,
            "volume": _to_number(item.get("volume")),
            "turnover": _to_number(item.get("amount") or item.get("turnover")),
            "open": _to_number(item.get("open")),
            "high": _to_number(item.get("high")),
            "low": _to_number(item.get("low")),
            "prev_close": prev_close,
            "market": _market_from_ticker(ticker),
            "data_source": "Sina Realtime",
            "data_status": "Live",
            "data_timestamp": timestamp,
            "data_warning": "",
        },
        "",
    )


def load_sina_a_share_spot(timeout: int = 10) -> pd.DataFrame:
    """Load realtime A-share quotes from Sina Market Center."""
    started = datetime.now()
    deadline = time.perf_counter() + max(float(timeout), 0.1)
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    attempts: list[dict[str, Any]] = []
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"}

    for page in range(1, 101):
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            warnings.append(f"timeout after {timeout}s")
            break
        params = {"page": str(page), "num": "80", "sort": "symbol", "asc": "1", "node": "hs_a", "symbol": "", "_s_r_a": "page"}
        try:
            response = requests.get(SINA_HQ_URL, params=params, timeout=min(float(timeout), remaining), headers=headers)
            status_code = getattr(response, "status_code", "")
            text = getattr(response, "text", "")
            response.raise_for_status()
            raw_rows = _parse_sina_payload(text)
        except Exception as exc:
            attempts.append({"page": page, "error": repr(exc)})
            break

        if not isinstance(raw_rows, list):
            return _empty(started, "Sina response payload is not a list.", attempts)
        attempts.append({"page": page, "http_status": status_code, "raw_rows": len(raw_rows)})
        if page == 1 and not raw_rows:
            warnings.append("page 1 returned no rows")
            break
        if not raw_rows:
            break
        timestamp = _now_text()
        for item in raw_rows:
            if not isinstance(item, dict):
                warnings.append(f"page {page}: row is not dict")
                continue
            normalized, warning = _normalize_row(item, timestamp)
            if warning:
                warnings.append(warning)
                continue
            rows.append(normalized)

    frame = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    if not frame.empty:
        frame = frame[frame["ticker"].astype(str).str.fullmatch(r"\d{6}", na=False)].copy(deep=True)
        frame = frame.drop_duplicates(subset=["ticker"], keep="first")
    status = "Live" if len(frame) > 1000 else "Error"
    warning = "" if status == "Live" else f"Sina Realtime returned {len(frame)} mapped rows; warnings={warnings[:5]}"
    return _attach_attrs(frame, started=started, status=status, warning=warning, attempts=attempts)


__all__ = ["OUTPUT_COLUMNS", "SINA_HQ_URL", "load_sina_a_share_spot"]
