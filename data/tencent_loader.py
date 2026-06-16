"""Tencent realtime A-share quote loader with bounded requests."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any
import json
import re
import time

import pandas as pd
import requests


TENCENT_RANK_URL = "https://web.ifzq.gtimg.cn/appstock/app/getRankList"
TENCENT_QUOTE_URL = "https://qt.gtimg.cn/q="
OUTPUT_COLUMNS = [
    "ticker",
    "name",
    "latest_price",
    "pct_change",
    "change_amount",
    "volume",
    "turnover",
    "turnover_rate",
    "volume_ratio",
    "market_cap",
    "float_market_cap",
    "pe_ttm",
    "pb",
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


def _empty(started: datetime, warning: str, attempts: list[dict[str, Any]] | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(columns=OUTPUT_COLUMNS)
    return _attach_attrs(frame, started=started, status="Error", warning=warning, attempts=attempts or [])


def _attach_attrs(
    frame: pd.DataFrame,
    *,
    started: datetime,
    status: str,
    warning: str = "",
    attempts: list[dict[str, Any]] | None = None,
) -> pd.DataFrame:
    frame.attrs["data_source"] = "Tencent Realtime"
    frame.attrs["data_status"] = status
    frame.attrs["load_time"] = (datetime.now() - started).total_seconds()
    frame.attrs["updated_at"] = _now_text()
    frame.attrs["last_error"] = warning
    frame.attrs["endpoint_attempts"] = list(attempts or [])
    return frame


def _extract_json(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return json.loads(stripped)
    match = re.search(r"=\s*(\{.*\})\s*;?\s*$", stripped, flags=re.S)
    if not match:
        raise ValueError("Tencent response does not contain JSON payload.")
    return json.loads(match.group(1))


def _find_rank_rows(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("rankash", "rankasz", "rank"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        for value in data.values():
            if isinstance(value, list):
                return value
    for value in payload.values():
        if isinstance(value, list):
            return value
    return []


def _field(item: Any, *names: str, index: int | None = None) -> Any:
    if isinstance(item, dict):
        for name in names:
            if name in item:
                return item[name]
    if isinstance(item, (list, tuple)) and index is not None and len(item) > index:
        return item[index]
    return None


def _normalize_row(item: Any, timestamp: str) -> tuple[dict[str, Any] | None, str]:
    symbol = str(_field(item, "symbol", "code", "stock_code", "market_code", index=0) or "").strip()
    digits = "".join(ch for ch in symbol if ch.isdigit())
    ticker = digits[-6:] if len(digits) >= 6 else ""
    name = str(_field(item, "name", "stock_name", "chs", index=1) or "").strip()
    if not ticker:
        return None, "missing ticker"
    if not name:
        return None, f"{ticker}: missing name"
    return (
        {
            "ticker": ticker,
            "name": name,
            "latest_price": _to_number(_field(item, "price", "now", "close", "latest_price", index=2)),
            "pct_change": _to_number(_field(item, "change_percent", "pct_change", "zf", index=4)),
            "change_amount": _to_number(_field(item, "change", "change_amount", "zd", index=3)),
            "volume": _to_number(_field(item, "volume", "vol", index=5)),
            "turnover": _to_number(_field(item, "amount", "turnover", index=6)),
            "turnover_rate": _to_number(_field(item, "turnover_rate")),
            "volume_ratio": _to_number(_field(item, "volume_ratio")),
            "market_cap": _to_number(_field(item, "market_cap")),
            "float_market_cap": _to_number(_field(item, "float_market_cap")),
            "pe_ttm": _to_number(_field(item, "pe_ttm", "pe")),
            "pb": _to_number(_field(item, "pb")),
            "open": _to_number(_field(item, "open", index=7)),
            "high": _to_number(_field(item, "high", index=8)),
            "low": _to_number(_field(item, "low", index=9)),
            "prev_close": _to_number(_field(item, "prev_close", "yestclose", index=10)),
            "market": _market_from_ticker(ticker),
            "data_source": "Tencent Realtime",
            "data_status": "Live",
            "data_timestamp": timestamp,
            "data_warning": "",
        },
        "",
    )


def _quote_symbols() -> list[str]:
    ranges = [
        ("sh", 600000, 606999),
        ("sh", 688000, 689999),
        ("sz", 0, 3999),
        ("sz", 300000, 302999),
        ("bj", 830000, 839999),
        ("bj", 870000, 879999),
        ("bj", 920000, 920999),
    ]
    symbols: list[str] = []
    for prefix, start, stop in ranges:
        symbols.extend(f"{prefix}{number:06d}" for number in range(start, stop + 1))
    return symbols


def _parse_quote_text(text: str, timestamp: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in re.finditer(r'v_[^=]+="([^"]*)";', text):
        parts = match.group(1).split("~")
        if len(parts) < 35:
            continue
        ticker = str(parts[2]).strip()
        name = str(parts[1]).strip()
        if not re.fullmatch(r"\d{6}", ticker) or not name:
            continue
        rows.append(
            {
                "ticker": ticker,
                "name": name,
                "latest_price": _to_number(parts[3]),
                "pct_change": _to_number(parts[32]),
                "change_amount": _to_number(parts[31]),
                "volume": _to_number(parts[36] if len(parts) > 36 else parts[6]),
                "turnover": _to_number(parts[37] if len(parts) > 37 else None),
                "turnover_rate": None,
                "volume_ratio": None,
                "market_cap": None,
                "float_market_cap": None,
                "pe_ttm": None,
                "pb": None,
                "open": _to_number(parts[5]),
                "high": _to_number(parts[33]),
                "low": _to_number(parts[34]),
                "prev_close": _to_number(parts[4]),
                "market": _market_from_ticker(ticker),
                "data_source": "Tencent Realtime",
                "data_status": "Live",
                "data_timestamp": timestamp,
                "data_warning": "",
            }
        )
    return rows


def _load_quote_scan(*, timeout: int, deadline: float, headers: dict[str, str], attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    symbols = _quote_symbols()
    chunk_size = 300
    chunks = [(index, symbols[index : index + chunk_size]) for index in range(0, len(symbols), chunk_size)]

    def fetch_chunk(index: int, chunk: list[str]) -> dict[str, Any]:
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return {"chunk": index // chunk_size + 1, "error": f"timeout after {timeout}s", "rows": []}
        try:
            response = requests.get(
                TENCENT_QUOTE_URL + ",".join(chunk),
                timeout=min(float(timeout), remaining),
                headers=headers,
            )
            status_code = getattr(response, "status_code", "")
            response.raise_for_status()
            parsed = _parse_quote_text(getattr(response, "text", ""), _now_text())
        except Exception as exc:
            return {"chunk": index // chunk_size + 1, "error": repr(exc), "rows": []}
        return {"chunk": index // chunk_size + 1, "http_status": status_code, "rows": parsed}

    executor = ThreadPoolExecutor(max_workers=12)
    futures = [executor.submit(fetch_chunk, index, chunk) for index, chunk in chunks]
    try:
        for future in as_completed(futures, timeout=max(deadline - time.perf_counter(), 0.1)):
            result = future.result()
            parsed = result.get("rows", [])
            if result.get("error"):
                attempts.append({"type": "qt_quote_scan", "chunk": result.get("chunk"), "error": result.get("error")})
                continue
            added = 0
            for row in parsed:
                ticker = row["ticker"]
                if ticker in seen:
                    continue
                seen.add(ticker)
                rows.append(row)
                added += 1
            attempts.append({"type": "qt_quote_scan", "chunk": result.get("chunk"), "http_status": result.get("http_status"), "raw_rows": len(parsed), "added_rows": added})
            if len(rows) >= 4000:
                break
    except TimeoutError:
        attempts.append({"type": "qt_quote_scan", "error": f"timeout after {timeout}s"})
    finally:
        for future in futures:
            future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
    return rows


def load_tencent_a_share_spot(timeout: int = 10) -> pd.DataFrame:
    """Load realtime A-share quotes from Tencent rank endpoints."""
    started = datetime.now()
    deadline = time.perf_counter() + max(float(timeout), 0.1)
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    attempts: list[dict[str, Any]] = []

    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"}
    rows = _load_quote_scan(timeout=timeout, deadline=deadline, headers=headers, attempts=attempts)

    for rank_type in ("rankash/chr", "rankasz/chr"):
        if len(rows) > 1000:
            break
        for page in range(1, 81):
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                warnings.append(f"timeout after {timeout}s")
                break
            params = {"type": rank_type, "p": str(page), "o": "0", "l": "80", "v": "rank_data"}
            try:
                response = requests.get(TENCENT_RANK_URL, params=params, timeout=min(float(timeout), remaining), headers=headers)
                status_code = getattr(response, "status_code", "")
                text = getattr(response, "text", "")
                response.raise_for_status()
                payload = _extract_json(text)
                raw_rows = _find_rank_rows(payload)
                if isinstance(payload, dict) and payload.get("code") not in (None, 0, "0") and not raw_rows:
                    raise ValueError(f"Tencent response code={payload.get('code')} msg={payload.get('msg')}")
            except Exception as exc:
                attempts.append({"type": rank_type, "page": page, "error": repr(exc)})
                break

            attempts.append({"type": rank_type, "page": page, "http_status": status_code, "raw_rows": len(raw_rows)})
            if page == 1 and not raw_rows:
                warnings.append(f"{rank_type} page 1 returned no rows")
                break
            if not raw_rows:
                break
            timestamp = _now_text()
            for item in raw_rows:
                normalized, warning = _normalize_row(item, timestamp)
                if warning:
                    warnings.append(warning)
                    continue
                rows.append(normalized)
        if deadline - time.perf_counter() <= 0:
            break

    frame = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    if not frame.empty:
        frame = frame[frame["ticker"].astype(str).str.fullmatch(r"\d{6}", na=False)].copy(deep=True)
        frame = frame.drop_duplicates(subset=["ticker"], keep="first")
    status = "Live" if len(frame) > 1000 else "Error"
    warning = "" if status == "Live" else f"Tencent Realtime returned {len(frame)} mapped rows; warnings={warnings[:5]}"
    return _attach_attrs(frame, started=started, status=status, warning=warning, attempts=attempts)


__all__ = ["OUTPUT_COLUMNS", "TENCENT_QUOTE_URL", "TENCENT_RANK_URL", "load_tencent_a_share_spot"]
