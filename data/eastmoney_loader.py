"""Direct EastMoney realtime A-share quote loader with debug metadata."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import pandas as pd
import requests


EASTMONEY_ENDPOINTS = [
    "https://push2.eastmoney.com/api/qt/clist/get",
    "https://push2his.eastmoney.com/api/qt/clist/get",
    "https://82.push2.eastmoney.com/api/qt/clist/get",
]
EASTMONEY_URL = EASTMONEY_ENDPOINTS[0]
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


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_time(started: datetime) -> float:
    return (datetime.now() - started).total_seconds()


def _params(page: int) -> dict[str, str]:
    return {
        "pn": str(page),
        "pz": "100",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": EASTMONEY_FIELDS,
    }


def _headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://quote.eastmoney.com/",
        "Accept": "application/json,text/plain,*/*",
    }


def _empty(
    *,
    started: datetime,
    status: str = "Error",
    warning: str = "",
    request_url: str = "",
    http_status: int | str | None = None,
    raw_preview: str = "",
    active_endpoint: str = "",
    endpoint_attempts: list[dict[str, Any]] | None = None,
) -> pd.DataFrame:
    frame = pd.DataFrame(columns=OUTPUT_COLUMNS)
    _attach_debug_attrs(
        frame,
        started=started,
        status=status,
        warning=warning,
        request_url=request_url,
        http_status=http_status,
        raw_preview=raw_preview,
        active_endpoint=active_endpoint,
        endpoint_attempts=endpoint_attempts or [],
        json_keys=[],
        diff_exists=False,
        diff_length=0,
    )
    return frame


def _attach_debug_attrs(
    frame: pd.DataFrame,
    *,
    started: datetime,
    status: str,
    warning: str,
    request_url: str,
    http_status: int | str | None,
    raw_preview: str,
    active_endpoint: str,
    endpoint_attempts: list[dict[str, Any]],
    json_keys: list[str],
    diff_exists: bool,
    diff_length: int,
) -> pd.DataFrame:
    frame.attrs["data_source"] = "EastMoney Direct"
    frame.attrs["data_status"] = status
    frame.attrs["load_time"] = _load_time(started)
    frame.attrs["last_error"] = warning
    frame.attrs["request_url"] = request_url
    frame.attrs["http_status"] = http_status if http_status is not None else ""
    frame.attrs["raw_preview"] = raw_preview[:300] if isinstance(raw_preview, str) else str(raw_preview)[:300]
    frame.attrs["active_endpoint"] = active_endpoint
    frame.attrs["endpoint_attempts"] = list(endpoint_attempts)
    frame.attrs["json_keys"] = json_keys
    frame.attrs["diff_exists"] = bool(diff_exists)
    frame.attrs["diff_length"] = int(diff_length)
    frame.attrs["updated_at"] = _now_text()
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


def _normalize_row(item: dict[str, Any], timestamp: str) -> tuple[dict[str, Any] | None, str]:
    ticker = str(item.get("f12") or "").strip()
    name = str(item.get("f14") or "").strip()
    if not ticker:
        return None, "missing f12 ticker"
    if not name:
        return None, f"{ticker}: missing f14 name"
    return (
        {
            "ticker": ticker,
            "name": name,
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
        },
        "",
    )


def _extract_diff(payload: Any) -> tuple[list[Any], list[str], bool]:
    if not isinstance(payload, dict):
        return [], [], False
    keys = list(payload.keys())
    data = payload.get("data")
    if not isinstance(data, dict):
        return [], keys, False
    diff = data.get("diff")
    if not isinstance(diff, list):
        return [], keys, diff is not None
    return diff, keys, True


def load_eastmoney_a_share_spot(timeout: int = 30) -> pd.DataFrame:
    """Load realtime A-share quotes directly from EastMoney push2."""
    started = datetime.now()
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    last_request_url = ""
    last_http_status: int | str | None = ""
    last_raw_preview = ""
    last_json_keys: list[str] = []
    last_diff_exists = False
    total_diff_length = 0
    active_endpoint = ""
    endpoint_attempts: list[dict[str, Any]] = []

    for endpoint in EASTMONEY_ENDPOINTS:
        endpoint_rows: list[dict[str, Any]] = []
        endpoint_warnings: list[str] = []
        endpoint_diff_length = 0
        endpoint_error = ""

        for page in range(1, 101):
            params = _params(page)
            last_request_url = endpoint
            try:
                response = requests.get(
                    endpoint,
                    params=params,
                    timeout=timeout,
                    headers=_headers(),
                )
                last_http_status = getattr(response, "status_code", "")
                last_raw_preview = getattr(response, "text", "")[:300]
                if last_http_status == 502:
                    endpoint_error = f"page {page} HTTP 502 Bad Gateway"
                    break
                response.raise_for_status()
                payload = response.json()
            except Exception as exc:
                endpoint_error = f"page {page} request/json failed: {repr(exc)}"
                break

            diff, json_keys, diff_exists = _extract_diff(payload)
            last_json_keys = json_keys
            last_diff_exists = diff_exists
            endpoint_diff_length += len(diff)

            if page == 1 and not diff:
                endpoint_error = f"page 1 diff missing or empty; json_keys={json_keys}; diff_exists={diff_exists}"
                break
            if not diff:
                break

            timestamp = _now_text()
            for item in diff:
                if not isinstance(item, dict):
                    endpoint_warnings.append(f"page {page}: diff item is not dict")
                    continue
                normalized, warning = _normalize_row(item, timestamp)
                if warning:
                    endpoint_warnings.append(warning)
                    continue
                endpoint_rows.append(normalized)

        endpoint_attempts.append(
            {
                "endpoint": endpoint,
                "http_status": last_http_status,
                "diff_length": endpoint_diff_length,
                "mapped_rows": len(endpoint_rows),
                "error": endpoint_error,
                "raw_preview": last_raw_preview[:120],
            }
        )

        if len(endpoint_rows) > 1000:
            active_endpoint = endpoint
            rows = endpoint_rows
            warnings = endpoint_warnings
            total_diff_length = endpoint_diff_length
            break

    if not rows:
        last_error = "All EastMoney endpoints failed or returned too few rows: " + str(endpoint_attempts)
        return _empty(
            started=started,
            warning=last_error,
            request_url=last_request_url,
            http_status=last_http_status,
            raw_preview=last_raw_preview,
            active_endpoint=active_endpoint,
            endpoint_attempts=endpoint_attempts,
        )

    frame = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    if not frame.empty:
        frame = frame[frame["ticker"].astype(str).str.fullmatch(r"\d{6}", na=False)].copy(deep=True)
        frame = frame.drop_duplicates(subset=["ticker"], keep="first")

    status = "Live" if len(frame) > 1000 else "Error"
    last_error = ""
    if status != "Live":
        last_error = (
            f"EastMoney Direct returned {len(frame)} mapped rows from {total_diff_length} raw diff rows; "
            f"json_keys={last_json_keys}; diff_exists={last_diff_exists}; "
            f"mapping_warnings={warnings[:5]}"
        )
    elif warnings:
        last_error = f"mapping_warnings={warnings[:5]}"

    return _attach_debug_attrs(
        frame,
        started=started,
        status=status,
        warning=last_error,
        request_url=last_request_url,
        http_status=last_http_status,
        raw_preview=last_raw_preview,
        active_endpoint=active_endpoint,
        endpoint_attempts=endpoint_attempts,
        json_keys=last_json_keys,
        diff_exists=last_diff_exists,
        diff_length=total_diff_length,
    )


__all__ = [
    "EASTMONEY_URL",
    "OUTPUT_COLUMNS",
    "load_eastmoney_a_share_spot",
]
