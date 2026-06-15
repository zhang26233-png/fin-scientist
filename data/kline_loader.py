"""A-share historical daily K-line loader with local CSV cache fallback."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Any, Callable

import pandas as pd


KLINE_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "turnover",
    "ticker",
    "data_source",
    "data_status",
    "data_warning",
]
KLINE_CACHE_DIR = Path("cache") / "kline"
MIN_CACHE_ROWS = 60


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_ticker(value: Any) -> str:
    """Normalize common ticker formats to a six-digit A-share code."""
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else ""


def _cache_path(ticker: str) -> Path:
    return KLINE_CACHE_DIR / f"{ticker}.csv"


def _empty(ticker: str = "", *, last_error: str = "", cache_path: Path | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(columns=KLINE_COLUMNS)
    frame.attrs.update(
        {
            "data_source": "Unavailable",
            "data_status": "Error",
            "cache_status": "Missing",
            "cache_path": str(cache_path or (_cache_path(ticker) if ticker else KLINE_CACHE_DIR)),
            "cache_updated_at": "",
            "last_error": last_error,
        }
    )
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


def _normalize_kline_frame(source: pd.DataFrame, ticker: str, *, data_source: str, data_status: str) -> pd.DataFrame:
    warnings: list[str] = []
    if source is None or source.empty:
        frame = pd.DataFrame(columns=KLINE_COLUMNS)
        frame.attrs["last_error"] = "empty kline data"
        return frame

    rows: list[dict[str, Any]] = []
    for _, row in source.iterrows():
        raw = row.to_dict()
        date_value = _first_existing(raw, ["date", "日期", "trade_date", "datetime", "time"])
        close_value = _first_existing(raw, ["close", "收盘", "收盘价", "latest_price"])
        mapped = {
            "date": date_value,
            "open": _first_existing(raw, ["open", "开盘", "开盘价"]),
            "high": _first_existing(raw, ["high", "最高", "最高价"]),
            "low": _first_existing(raw, ["low", "最低", "最低价"]),
            "close": close_value,
            "volume": _first_existing(raw, ["volume", "成交量"]),
            "turnover": _first_existing(raw, ["turnover", "成交额", "amount"]),
        }
        if mapped["date"] is None or close_value is None:
            warnings.append("missing date or close")
            continue
        rows.append(
            {
                **mapped,
                "ticker": ticker,
                "data_source": data_source,
                "data_status": data_status,
                "data_warning": "",
            }
        )

    frame = pd.DataFrame(rows, columns=KLINE_COLUMNS)
    if frame.empty:
        return _empty(ticker, last_error="kline normalization returned no rows")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for field in ["open", "high", "low", "close", "volume", "turnover"]:
        if field in frame.columns:
            frame[field] = pd.to_numeric(frame[field], errors="coerce")
            if frame[field].isna().all():
                warnings.append(f"{field} missing")
    frame = frame.dropna(subset=["date", "close"])
    frame = frame.drop_duplicates(subset=["date"], keep="last")
    frame = frame.sort_values("date", kind="mergesort").reset_index(drop=True)
    frame = frame.reindex(columns=KLINE_COLUMNS)
    warning_text = "; ".join(dict.fromkeys(warnings))
    if warning_text:
        frame["data_warning"] = warning_text
    frame.attrs.update(
        {
            "data_source": data_source,
            "data_status": data_status,
            "cache_status": "Unavailable",
            "cache_path": str(_cache_path(ticker)),
            "cache_updated_at": "",
            "last_error": warning_text,
        }
    )
    return frame


def _fetch_akshare_kline(ticker: str, start_date: str | None, end_date: str | None, adjust: str, timeout: int) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        import akshare as ak

        return ak.stock_zh_a_hist(
            symbol=ticker,
            period="daily",
            start_date=(start_date or "").replace("-", ""),
            end_date=(end_date or "").replace("-", ""),
            adjust=adjust,
        )

    raw, error = _call_with_timeout(fetch, timeout)
    frame = _normalize_kline_frame(raw, ticker, data_source="AkShare K-Line", data_status="Live")
    if error:
        frame.attrs["last_error"] = error
    return frame


def load_cached_kline(ticker: Any) -> pd.DataFrame:
    """Read one ticker K-line CSV cache if available."""
    normalized = normalize_ticker(ticker)
    if not normalized:
        return _empty("", last_error="empty ticker")
    path = _cache_path(normalized)
    if not path.exists():
        return _empty(normalized, last_error="cache not found", cache_path=path)
    try:
        raw = pd.read_csv(path)
        frame = _normalize_kline_frame(raw, normalized, data_source="Local K-Line Cache", data_status="Cache")
        updated_at = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        frame.attrs.update(
            {
                "data_source": "Local K-Line Cache",
                "data_status": "Cache",
                "cache_status": "Hit",
                "cache_path": str(path),
                "cache_updated_at": updated_at,
                "last_error": "",
            }
        )
        return frame
    except Exception as exc:
        return _empty(normalized, last_error=repr(exc), cache_path=path)


def save_cached_kline(ticker: Any, df: pd.DataFrame) -> dict[str, Any]:
    """Persist one ticker K-line cache when the normalized frame is usable."""
    normalized = normalize_ticker(ticker)
    path = _cache_path(normalized) if normalized else KLINE_CACHE_DIR
    attrs = {
        "cache_status": "Skipped",
        "cache_path": str(path),
        "cache_updated_at": "",
        "last_error": "",
    }
    if not normalized:
        attrs["last_error"] = "empty ticker"
        return attrs
    frame = _normalize_kline_frame(df, normalized, data_source=str(df.attrs.get("data_source", "Provided")), data_status=str(df.attrs.get("data_status", "Live")))
    if len(frame) < MIN_CACHE_ROWS:
        attrs["last_error"] = f"rows {len(frame)} below {MIN_CACHE_ROWS}"
        return attrs
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        attrs.update(
            {
                "cache_status": "Saved",
                "cache_updated_at": _now_text(),
            }
        )
        return attrs
    except Exception as exc:
        attrs["cache_status"] = "Error"
        attrs["last_error"] = repr(exc)
        return attrs


def load_a_share_kline(
    ticker: Any,
    start_date: str | None = None,
    end_date: str | None = None,
    adjust: str = "qfq",
    timeout: int = 10,
) -> pd.DataFrame:
    """Load one A-share daily K-line with external-source then cache fallback."""
    normalized = normalize_ticker(ticker)
    if not normalized:
        return _empty("", last_error="empty ticker")
    frame = _fetch_akshare_kline(normalized, start_date, end_date, adjust, timeout)
    if len(frame) >= MIN_CACHE_ROWS:
        cache_attrs = save_cached_kline(normalized, frame)
        frame.attrs.update(cache_attrs)
        return frame

    external_error = frame.attrs.get("last_error", f"external rows={len(frame)}")
    cached = load_cached_kline(normalized)
    if not cached.empty:
        cached.attrs["last_error"] = external_error
        return cached
    empty = _empty(normalized, last_error=str(external_error), cache_path=_cache_path(normalized))
    return empty


def load_batch_a_share_klines(
    tickers: list[Any] | pd.Series,
    start_date: str | None = None,
    end_date: str | None = None,
    adjust: str = "qfq",
    max_stocks: int | None = None,
    timeout: int = 10,
    sleep_seconds: float = 0.05,
) -> dict[str, pd.DataFrame]:
    """Load multiple K-lines sequentially; one ticker failure does not stop the batch."""
    values = [] if tickers is None else list(tickers)
    normalized: list[str] = []
    for ticker in values:
        code = normalize_ticker(ticker)
        if code and code not in normalized:
            normalized.append(code)
    if max_stocks is not None:
        normalized = normalized[: max(int(max_stocks), 0)]

    histories: dict[str, pd.DataFrame] = {}
    attempts: list[dict[str, Any]] = []
    cache_hits = 0
    failures = 0
    for index, ticker in enumerate(normalized):
        try:
            frame = load_a_share_kline(ticker, start_date=start_date, end_date=end_date, adjust=adjust, timeout=timeout)
            if not frame.empty:
                histories[ticker] = frame
            if frame.attrs.get("data_status") == "Cache" or frame.attrs.get("cache_status") == "Hit":
                cache_hits += 1
            if frame.empty:
                failures += 1
            attempts.append(
                {
                    "ticker": ticker,
                    "rows": len(frame),
                    "data_source": frame.attrs.get("data_source", "Unavailable"),
                    "data_status": frame.attrs.get("data_status", "Error"),
                    "cache_status": frame.attrs.get("cache_status", "Missing"),
                    "last_error": frame.attrs.get("last_error", ""),
                }
            )
        except Exception as exc:
            failures += 1
            attempts.append({"ticker": ticker, "rows": 0, "data_source": "Unavailable", "data_status": "Error", "cache_status": "Missing", "last_error": repr(exc)})
        if sleep_seconds and index < len(normalized) - 1:
            sleep(float(sleep_seconds))
    histories["_attrs"] = {
        "requested": len(normalized),
        "loaded": len([key for key in histories if key != "_attrs"]),
        "cache_hits": cache_hits,
        "failures": failures,
        "attempts": attempts,
    }
    return histories


def build_price_history_dict(
    tickers: list[Any] | pd.Series,
    max_stocks: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Build the pipeline price_history_dict for the requested ticker list."""
    if start_date is None:
        start_date = (datetime.today() - timedelta(days=420)).strftime("%Y-%m-%d")
    return load_batch_a_share_klines(
        tickers,
        start_date=start_date,
        end_date=end_date,
        max_stocks=max_stocks,
    )


__all__ = [
    "KLINE_CACHE_DIR",
    "KLINE_COLUMNS",
    "build_price_history_dict",
    "load_a_share_kline",
    "load_batch_a_share_klines",
    "load_cached_kline",
    "normalize_ticker",
    "save_cached_kline",
]
