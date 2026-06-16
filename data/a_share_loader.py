"""A-share universe loader with multi-source realtime fallback."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import date, datetime
from typing import Any, Callable

import pandas as pd

from data.eastmoney_loader import load_eastmoney_a_share_spot
from data.local_cache import cache_metadata, read_a_share_universe_cache, write_a_share_cache
from data.sina_loader import load_sina_a_share_spot
from data.tencent_loader import load_tencent_a_share_spot


OUTPUT_COLUMNS = [
    "ticker",
    "name",
    "market",
    "industry",
    "list_date",
    "status",
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
    "data_source",
    "data_status",
    "data_timestamp",
    "data_warning",
]
DEFAULT_MIN_LISTING_DAYS = 180
DEFAULT_TIMEOUT_SECONDS = 10
MIN_REAL_UNIVERSE_ROWS = 1000
TARGET_REAL_UNIVERSE_ROWS = 4000

DEMO_STOCKS = [
    ("600519", "Demo 600519", "Consumer"),
    ("300750", "Demo 300750", "New Energy"),
    ("600036", "Demo 600036", "Financial"),
    ("601138", "Demo 601138", "Electronics"),
    ("300308", "Demo 300308", "Communication"),
    ("300476", "Demo 300476", "Electronics"),
    ("002594", "Demo 002594", "Auto"),
    ("000333", "Demo 000333", "Home Appliance"),
    ("601318", "Demo 601318", "Financial"),
    ("000858", "Demo 000858", "Consumer"),
    ("300059", "Demo 300059", "Financial"),
    ("600030", "Demo 600030", "Financial"),
    ("002475", "Demo 002475", "Electronics"),
    ("002415", "Demo 002415", "Computer"),
    ("300760", "Demo 300760", "Medical"),
    ("601899", "Demo 601899", "Resource"),
    ("688256", "Demo 688256", "Semiconductor"),
    ("002230", "Demo 002230", "AI"),
    ("603501", "Demo 603501", "Semiconductor"),
    ("601012", "Demo 601012", "New Energy"),
]


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _market_from_ticker(ticker: str) -> str:
    if ticker.startswith("688"):
        return "STAR"
    if ticker.startswith("6"):
        return "SH"
    if ticker.startswith("300"):
        return "ChiNext"
    if ticker.startswith(("0", "2")):
        return "SZ"
    if ticker.startswith(("4", "8", "9")):
        return "BSE"
    return "A-share"


def _normalize_ticker(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else None


def _parse_date(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    parsed = pd.to_datetime(pd.Series([text]), errors="coerce").iloc[0]
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def _days_since_listing(value: Any, today: date) -> int | None:
    parsed = _parse_date(value)
    if not parsed:
        return None
    return max((today - datetime.strptime(parsed, "%Y-%m-%d").date()).days, 0)


def _first_existing(row: dict[str, Any], fields: list[str], default: Any = None) -> Any:
    for field in fields:
        if field not in row:
            continue
        value = row[field]
        if value is None or pd.isna(value):
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return default


def _attach_attrs(
    frame: pd.DataFrame,
    *,
    data_source: str,
    data_status: str,
    raw_count: int,
    filtered_count: int,
    final_count: int,
    load_time: float = 0.0,
    last_error: str = "",
    filtered_breakdown: dict[str, int] | None = None,
    source_attempts: list[dict[str, Any]] | None = None,
    cache_attrs: dict[str, Any] | None = None,
) -> pd.DataFrame:
    frame.attrs["data_source"] = data_source
    frame.attrs["data_status"] = data_status
    frame.attrs["raw_count"] = int(raw_count)
    frame.attrs["filtered_count"] = int(filtered_count)
    frame.attrs["final_count"] = int(final_count)
    frame.attrs["universe_size"] = int(final_count)
    frame.attrs["load_time"] = float(load_time)
    frame.attrs["updated_at"] = _now_text()
    frame.attrs["last_error"] = last_error
    frame.attrs["filtered_breakdown"] = dict(filtered_breakdown or {})
    frame.attrs["source_attempts"] = list(source_attempts or [])
    frame.attrs.update(cache_attrs or cache_metadata())
    return frame


def _call_with_timeout(fetcher: Callable[[], pd.DataFrame], timeout: int) -> tuple[pd.DataFrame, str]:
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fetcher)
    try:
        return future.result(timeout=timeout), ""
    except TimeoutError:
        future.cancel()
        return pd.DataFrame(), f"timeout after {timeout}s"
    except Exception as exc:
        return pd.DataFrame(), repr(exc)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _normalize_source_frame(source: pd.DataFrame, *, data_source: str = "Provided", data_status: str = "Live") -> pd.DataFrame:
    if source is None or source.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    rows: list[dict[str, Any]] = []
    for _, row in source.iterrows():
        raw = row.to_dict()
        ticker = _normalize_ticker(
            _first_existing(raw, ["ticker", "code", "代码", "证券代码", "symbol", "股票代码"])
        )
        if not ticker:
            continue
        name = str(_first_existing(raw, ["name", "名称", "证券简称", "股票简称", "code_name"], "")).strip()
        rows.append(
            {
                "ticker": ticker,
                "name": name,
                "market": _first_existing(raw, ["market", "市场"], _market_from_ticker(ticker)),
                "industry": _first_existing(raw, ["industry", "行业", "所属行业"], ""),
                "list_date": _parse_date(
                    _first_existing(raw, ["list_date", "上市日期", "ipoDate", "ipo_date", "上市时间"])
                ),
                "status": _first_existing(raw, ["status", "状态", "outDate"], "Available"),
                "latest_price": _first_existing(raw, ["latest_price", "最新价"]),
                "pct_change": _first_existing(raw, ["pct_change", "涨跌幅"]),
                "change_amount": _first_existing(raw, ["change_amount", "涨跌额"]),
                "volume": _first_existing(raw, ["volume", "成交量"]),
                "turnover": _first_existing(raw, ["turnover", "成交额"]),
                "open": _first_existing(raw, ["open", "今开"]),
                "high": _first_existing(raw, ["high", "最高"]),
                "low": _first_existing(raw, ["low", "最低"]),
                "prev_close": _first_existing(raw, ["prev_close", "昨收"]),
                "data_source": _first_existing(raw, ["data_source"], data_source),
                "data_status": _first_existing(raw, ["data_status"], data_status),
                "data_timestamp": _first_existing(raw, ["data_timestamp"], _now_text()),
                "data_warning": _first_existing(raw, ["data_warning"], ""),
            }
        )
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def _merge_source_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    valid = [frame for frame in frames if isinstance(frame, pd.DataFrame) and not frame.empty]
    if not valid:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    merged = pd.concat(valid, ignore_index=True)
    normalized = _normalize_source_frame(merged, data_source="Multi Realtime", data_status="Live")
    if normalized.empty:
        return normalized
    return normalized.drop_duplicates(subset=["ticker"], keep="first").reindex(columns=OUTPUT_COLUMNS)


def _apply_filters(frame: pd.DataFrame, *, today: date, min_listing_days: int) -> tuple[pd.DataFrame, dict[str, int]]:
    source = frame.copy(deep=True)
    name = source["name"].fillna("").astype(str).str.strip()
    status = source["status"].fillna("").astype(str)
    days = source["list_date"].map(lambda value: _days_since_listing(value, today))

    empty_name = name.eq("")
    st_mask = name.str.upper().str.contains(r"(?:^ST|\*ST|ST)", regex=True, na=False)
    delisted_mask = name.str.contains("退", na=False) | status.str.contains("退市|delist", case=False, regex=True, na=False) | status.eq("0")
    suspended_mask = status.str.contains("停牌|暂停|suspend", case=False, regex=True, na=False)
    new_mask = days.map(lambda value: value is not None and value < min_listing_days)
    duplicate_mask = source["ticker"].duplicated()

    remove = empty_name | st_mask | delisted_mask | suspended_mask | new_mask | duplicate_mask
    filtered = source.loc[~remove].copy(deep=True)
    filtered["market"] = filtered["ticker"].map(_market_from_ticker)

    breakdown = {
        "empty_name": int(empty_name.sum()),
        "st": int(st_mask.sum()),
        "delisted": int(delisted_mask.sum()),
        "suspended": int(suspended_mask.sum()),
        "new_listing": int(new_mask.sum()),
        "duplicates": int(duplicate_mask.sum()),
    }
    return filtered.reindex(columns=OUTPUT_COLUMNS), breakdown


def _build_demo_universe(last_error: str = "") -> pd.DataFrame:
    rows = [
        {
            "ticker": ticker,
            "name": name,
            "market": _market_from_ticker(ticker),
            "industry": industry,
            "list_date": "2010-01-01",
            "status": "Available",
            "latest_price": None,
            "pct_change": None,
            "change_amount": None,
            "volume": None,
            "turnover": None,
            "open": None,
            "high": None,
            "low": None,
            "prev_close": None,
            "data_source": "Demo",
            "data_status": "Fallback",
            "data_timestamp": _now_text(),
            "data_warning": "Demo fallback data; not realtime quotes.",
        }
        for ticker, name, industry in DEMO_STOCKS
    ]
    frame = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    return _attach_attrs(
        frame,
        data_source="Demo",
        data_status="Fallback",
        raw_count=len(frame),
        filtered_count=0,
        final_count=len(frame),
        last_error=last_error,
        cache_attrs=cache_metadata(),
    )


def _fetch_akshare_universe(timeout: int) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        import akshare as ak

        return ak.stock_zh_a_spot_em()

    raw, error = _call_with_timeout(fetch, timeout)
    frame = _normalize_source_frame(raw, data_source="AkShare", data_status="Live")
    frame.attrs["data_source"] = "AkShare"
    frame.attrs["data_status"] = "Live" if len(frame) > MIN_REAL_UNIVERSE_ROWS else "Error"
    frame.attrs["last_error"] = error or ("" if len(frame) > MIN_REAL_UNIVERSE_ROWS else f"AkShare returned {len(frame)} rows.")
    return frame


def _fetch_baostock_universe(timeout: int) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        import baostock as bs

        rows = []
        login = bs.login()
        try:
            if getattr(login, "error_code", "1") != "0":
                return pd.DataFrame()
            result = bs.query_stock_basic()
            while getattr(result, "error_code", "1") == "0" and result.next():
                item = result.get_row_data()
                rows.append(
                    {
                        "code": item[0] if len(item) > 0 else "",
                        "name": item[1] if len(item) > 1 else "",
                        "ipoDate": item[2] if len(item) > 2 else "",
                        "status": item[5] if len(item) > 5 else "",
                    }
                )
            return pd.DataFrame(rows)
        finally:
            try:
                bs.logout()
            except Exception:
                pass

    raw, error = _call_with_timeout(fetch, timeout)
    frame = _normalize_source_frame(raw, data_source="BaoStock", data_status="Live")
    frame.attrs["data_source"] = "BaoStock"
    frame.attrs["data_status"] = "Live" if len(frame) > MIN_REAL_UNIVERSE_ROWS else "Error"
    frame.attrs["last_error"] = error or ("" if len(frame) > MIN_REAL_UNIVERSE_ROWS else f"BaoStock returned {len(frame)} rows.")
    return frame


def _attempt_source(name: str, fetcher: Callable[..., pd.DataFrame], timeout: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    started = datetime.now()
    try:
        frame = fetcher(timeout=timeout)
    except Exception as exc:
        frame = pd.DataFrame(columns=OUTPUT_COLUMNS)
        frame.attrs["data_source"] = name
        frame.attrs["data_status"] = "Error"
        frame.attrs["last_error"] = repr(exc)
    rows = len(frame) if isinstance(frame, pd.DataFrame) else 0
    status = "Live" if rows > MIN_REAL_UNIVERSE_ROWS else "Error"
    last_error = str(getattr(frame, "attrs", {}).get("last_error", ""))
    if status != "Live" and not last_error:
        last_error = f"{name} returned {rows} rows; minimum required is {MIN_REAL_UNIVERSE_ROWS + 1}."
    attempt = {
        "data_source": name,
        "rows": rows,
        "data_status": status,
        "last_error": last_error,
        "load_time": (datetime.now() - started).total_seconds(),
    }
    return frame if isinstance(frame, pd.DataFrame) else pd.DataFrame(columns=OUTPUT_COLUMNS), attempt


def _load_realtime_sources(timeout: int) -> tuple[pd.DataFrame, str, str, list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    live_frames: list[pd.DataFrame] = []
    sources: list[tuple[str, Callable[..., pd.DataFrame]]] = [
        ("Tencent Realtime", load_tencent_a_share_spot),
        ("Sina Realtime", load_sina_a_share_spot),
        ("EastMoney Direct", load_eastmoney_a_share_spot),
        ("AkShare", _fetch_akshare_universe),
        ("BaoStock", _fetch_baostock_universe),
    ]
    for index, (name, fetcher) in enumerate(sources):
        frame, attempt = _attempt_source(name, fetcher, timeout)
        attempts.append(attempt)
        if attempt["rows"] > MIN_REAL_UNIVERSE_ROWS:
            live_frames.append(_normalize_source_frame(frame, data_source=name, data_status="Live"))
        merged = _merge_source_frames(live_frames)
        if len(merged) >= TARGET_REAL_UNIVERSE_ROWS:
            for skipped_name, _ in sources[index + 1 :]:
                attempts.append(
                    {
                        "data_source": skipped_name,
                        "rows": 0,
                        "data_status": "Not Tried",
                        "last_error": f"Skipped because accumulated realtime rows reached {len(merged)}.",
                        "load_time": 0.0,
                    }
                )
            return merged, "Multi Realtime" if len(live_frames) > 1 else name, "", attempts
    merged = _merge_source_frames(live_frames)
    if len(merged) > MIN_REAL_UNIVERSE_ROWS:
        return merged, "Multi Realtime" if len(live_frames) > 1 else str(merged["data_source"].iloc[0]), "", attempts
    last_error = "; ".join(f"{item['data_source']}: {item['last_error'] or item['rows']}" for item in attempts)
    return pd.DataFrame(columns=OUTPUT_COLUMNS), "Demo", last_error, attempts


def _load_cache_source() -> tuple[pd.DataFrame, dict[str, Any], str]:
    cache_attrs = cache_metadata()
    cached = read_a_share_universe_cache()
    cache_attrs.update(cached.attrs)
    if cached.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS), cache_attrs, cached.attrs.get("last_error", "Local cache is empty.")
    normalized = _normalize_source_frame(cached, data_source="Local Cache", data_status="Cache")
    if normalized.empty:
        return normalized, cache_attrs, "Local cache could not be normalized."
    return normalized, cache_attrs, ""


def load_a_share_universe(
    *,
    min_listing_days: int = DEFAULT_MIN_LISTING_DAYS,
    today: date | None = None,
    source_df: pd.DataFrame | None = None,
    metadata_df: pd.DataFrame | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> pd.DataFrame:
    """Load A-share universe using Tencent, Sina, EastMoney, AkShare, BaoStock, then Demo."""
    _ = metadata_df
    today_value = today or date.today()
    started = datetime.now()
    last_error = ""
    source_attempts: list[dict[str, Any]] = []
    cache_attrs = cache_metadata()

    if source_df is not None:
        raw = _normalize_source_frame(source_df, data_source="Provided", data_status="Live")
        data_source = "Provided"
    else:
        raw, data_source, last_error, source_attempts = _load_realtime_sources(timeout)
        if raw.empty:
            raw, cache_attrs, cache_error = _load_cache_source()
            if not raw.empty:
                data_source = "Local Cache"
                last_error = last_error or cache_error
                source_attempts.append(
                    {
                        "data_source": "Local Cache",
                        "rows": len(raw),
                        "data_status": "Cache",
                        "last_error": cache_error,
                        "load_time": 0.0,
                    }
                )
            else:
                source_attempts.append(
                    {
                        "data_source": "Local Cache",
                        "rows": 0,
                        "data_status": "Error",
                        "last_error": cache_error,
                        "load_time": 0.0,
                    }
                )
                demo = _build_demo_universe(last_error=last_error or "All realtime A-share data sources failed.")
                demo.attrs["source_attempts"] = source_attempts
                return demo
        else:
            cache_attrs = cache_metadata()

    raw_count = len(raw)
    filtered, breakdown = _apply_filters(raw, today=today_value, min_listing_days=min_listing_days)
    if data_source != "Local Cache" and len(filtered) < MIN_REAL_UNIVERSE_ROWS:
        cached_raw, cached_attrs, cache_error = _load_cache_source()
        if not cached_raw.empty:
            cached_filtered, cached_breakdown = _apply_filters(cached_raw, today=today_value, min_listing_days=min_listing_days)
            if len(cached_filtered) > len(filtered):
                raw = cached_raw
                raw_count = len(raw)
                filtered = cached_filtered
                breakdown = cached_breakdown
                data_source = "Local Cache"
                cache_attrs = cached_attrs
                last_error = (last_error + "; " if last_error else "") + "Realtime filtered rows were insufficient; loaded local cache."
                source_attempts.append(
                    {
                        "data_source": "Local Cache",
                        "rows": len(raw),
                        "data_status": "Cache",
                        "last_error": cache_error,
                        "load_time": 0.0,
                    }
                )
    if data_source != "Local Cache" and raw_count > MIN_REAL_UNIVERSE_ROWS:
        cache_attrs = write_a_share_cache(universe=filtered, quotes=raw)
    elif data_source == "Local Cache":
        cache_attrs = cache_metadata()
    load_time = (datetime.now() - started).total_seconds()
    data_status = "Cache" if data_source == "Local Cache" else "Live"
    final_last_error = last_error
    if len(filtered) < MIN_REAL_UNIVERSE_ROWS:
        final_last_error = (final_last_error + "; " if final_last_error else "") + "真实数据不足，仅用于结构验证"
    return _attach_attrs(
        filtered,
        data_source=data_source,
        data_status=data_status,
        raw_count=raw_count,
        filtered_count=raw_count - len(filtered),
        final_count=len(filtered),
        load_time=load_time,
        last_error=final_last_error,
        filtered_breakdown=breakdown,
        source_attempts=source_attempts,
        cache_attrs=cache_attrs,
    )


__all__ = [
    "DEFAULT_MIN_LISTING_DAYS",
    "DEFAULT_TIMEOUT_SECONDS",
    "MIN_REAL_UNIVERSE_ROWS",
    "OUTPUT_COLUMNS",
    "TARGET_REAL_UNIVERSE_ROWS",
    "load_a_share_universe",
]
