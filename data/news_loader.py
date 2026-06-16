"""News data loading and standardization boundary.

This module keeps external/public source access separate from the news event
research engine. It uses simple keyword helpers for backward compatibility and
always returns a standardized DataFrame or a safe empty frame.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from news.event_engine import NEWS_EVENT_FIELDS, classify_news_event


CACHE_DIR = Path("cache/news")
CACHE_FILE = CACHE_DIR / "news_latest.csv"
MIN_CACHE_ROWS = 10

NEWS_COLUMNS = list(NEWS_EVENT_FIELDS)

FIELD_ALIASES = {
    "ticker": ["ticker", "code", "symbol", "SECURITY_CODE", "security_code"],
    "name": ["name", "stock_name", "SECURITY_NAME_ABBR", "security_name"],
    "news_title": ["news_title", "title", "TITLE", "content", "notice_title"],
    "news_time": ["news_time", "time", "datetime", "NOTICE_DATE", "PUBLISH_TIME", "publish_time"],
    "news_source": ["news_source", "source", "SOURCE", "media_name"],
    "news_url": ["news_url", "url", "URL", "art_code"],
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


def _string(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def _first_existing(row: dict[str, Any], field: str) -> Any:
    for name in FIELD_ALIASES.get(field, [field]):
        if name not in row:
            continue
        value = row.get(name)
        if _string(value):
            return value
    return None


def _as_keywords(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple) or isinstance(value, set):
        return [str(item).strip() for item in value if str(item).strip()]
    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if not text:
        return []
    for separator in [";", "；", "|", "，"]:
        text = text.replace(separator, ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def classify_news_keywords(title: Any, summary: Any = "") -> list[str]:
    return list(classify_news_event(title, summary).get("news_keywords", []))


def infer_news_sentiment(keywords: list[str] | str | None) -> str:
    values = _as_keywords(keywords)
    if not values:
        return "Unknown"
    joined = " ".join(values)
    return str(classify_news_event(joined).get("news_sentiment_label", "Unknown"))


def news_event_score(sentiment_label: str) -> int:
    if sentiment_label == "Positive":
        return 80
    if sentiment_label == "Negative":
        return 30
    if sentiment_label == "Neutral":
        return 50
    return 50


def _empty(status: str = "Unavailable", warning: str = "") -> pd.DataFrame:
    frame = pd.DataFrame(columns=NEWS_COLUMNS)
    frame.attrs.update(
        {
            "news_source": "Unavailable",
            "news_status": status,
            "news_warning": warning,
            "news_rows": 0,
            "news_updated_at": _now_text(),
            "cache_status": "Missing",
            "cache_path": str(CACHE_FILE),
        }
    )
    return frame


def _standardize_frame(
    source: pd.DataFrame | None,
    *,
    data_source: str,
    data_status: str = "Available",
    warning: str = "",
) -> pd.DataFrame:
    if source is None or source.empty:
        return _empty(status="Unavailable", warning=warning)

    rows: list[dict[str, Any]] = []
    for _, item in source.iterrows():
        raw = item.to_dict()
        ticker = _normalize_ticker(_first_existing(raw, "ticker"))
        title = _string(_first_existing(raw, "news_title"))
        if not ticker:
            continue
        classification = classify_news_event(title, raw.get("news_summary") or raw.get("content"))
        keywords = _as_keywords(raw.get("news_keywords")) or classification["news_keywords"]
        sentiment = _string(raw.get("news_sentiment_label")) or classification["news_sentiment_label"]
        event_score = raw.get("news_event_score")
        try:
            event_score_value = max(0, min(100, float(event_score)))
        except (TypeError, ValueError):
            event_score_value = news_event_score(sentiment)
        rows.append(
            {
                "ticker": ticker,
                "name": _string(_first_existing(raw, "name")),
                "news_title": title,
                "news_time": _string(_first_existing(raw, "news_time")) or _now_text(),
                "news_source": _string(_first_existing(raw, "news_source")) or data_source,
                "news_url": _string(_first_existing(raw, "news_url")),
                "news_type": _string(raw.get("news_type")) or classification["news_type"],
                "news_keywords": keywords,
                "news_sentiment_label": sentiment,
                "news_heat_score": raw.get("news_heat_score"),
                "news_risk_score": raw.get("news_risk_score"),
                "news_event_score": event_score_value,
                "news_summary": _string(raw.get("news_summary")),
                "news_reason": _string(raw.get("news_reason")),
                "news_warning": _string(raw.get("news_warning")) or warning,
                "news_status": _string(raw.get("news_status")) or ("Available" if title else "Unavailable"),
                "news_updated_at": _string(raw.get("news_updated_at")) or _now_text(),
            }
        )

    if not rows:
        return _empty(status="Unavailable", warning=warning or "No mappable news rows.")
    frame = pd.DataFrame(rows, columns=NEWS_COLUMNS).drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    frame.attrs.update(
        {
            "news_source": data_source,
            "news_status": data_status,
            "news_warning": warning,
            "news_rows": len(frame),
            "news_updated_at": _now_text(),
            "cache_status": "Not Used",
            "cache_path": str(CACHE_FILE),
        }
    )
    return frame


def load_news_from_existing_df(df: pd.DataFrame | None) -> pd.DataFrame:
    return _standardize_frame(df, data_source="Existing News Fields", data_status="Available")


def load_news_from_eastmoney(tickers: list[str] | None = None, timeout: int = 10, max_stocks: int = 300) -> pd.DataFrame:
    _ = max_stocks
    try:
        url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
        params = {"page_size": "100", "page_index": "1", "ann_type": "A", "client_source": "web"}
        response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        rows = data.get("list", []) if isinstance(data, dict) else []
        frame = _standardize_frame(pd.DataFrame(rows), data_source="EastMoney News", data_status="Available")
        if tickers and not frame.empty:
            wanted = {_normalize_ticker(ticker) for ticker in tickers}
            frame = frame[frame["ticker"].isin(wanted)].copy(deep=True)
        return frame
    except Exception as exc:
        return _empty(status="Error", warning=repr(exc))


def load_news_from_sina(tickers: list[str] | None = None, timeout: int = 10, max_stocks: int = 300) -> pd.DataFrame:
    _ = tickers, timeout, max_stocks
    return _empty(status="Unavailable", warning="Sina news source is not available in this local run.")


def load_news_from_akshare(tickers: list[str] | None = None, timeout: int = 10, max_stocks: int = 300) -> pd.DataFrame:
    _ = timeout
    try:
        import akshare as ak

        if not hasattr(ak, "stock_news_em"):
            return _empty(status="Error", warning="akshare stock_news_em is unavailable.")
        frames = []
        for ticker in (tickers or [])[: max_stocks]:
            try:
                frames.append(ak.stock_news_em(symbol=str(ticker)))
            except Exception:
                continue
        raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        return _standardize_frame(raw, data_source="AkShare News", data_status="Available")
    except Exception as exc:
        return _empty(status="Error", warning=repr(exc))


def save_cached_news(df: pd.DataFrame | None) -> dict[str, Any]:
    if df is None or df.empty or len(df) < MIN_CACHE_ROWS:
        return {"cache_status": "Skipped", "cache_path": str(CACHE_FILE), "cache_updated_at": ""}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frame = df.reindex(columns=NEWS_COLUMNS).copy(deep=True)
    frame["news_keywords"] = frame["news_keywords"].map(lambda value: ",".join(value) if isinstance(value, list) else value)
    frame.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
    return {"cache_status": "Available", "cache_path": str(CACHE_FILE), "cache_updated_at": _now_text()}


def load_cached_news() -> pd.DataFrame:
    if not CACHE_FILE.exists():
        return _empty(status="Unavailable", warning="News cache is missing.")
    try:
        raw = pd.read_csv(CACHE_FILE, dtype={"ticker": str})
        frame = _standardize_frame(raw, data_source="News Cache", data_status="Cache")
        frame.attrs["cache_status"] = "Available"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        frame.attrs["cache_updated_at"] = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return frame
    except Exception as exc:
        frame = _empty(status="Error", warning=repr(exc))
        frame.attrs["cache_status"] = "Error"
        frame.attrs["cache_path"] = str(CACHE_FILE)
        return frame


def build_news_dataset(
    existing_df: pd.DataFrame | None = None,
    tickers: list[str] | None = None,
    *,
    timeout: int = 10,
    use_external: bool = True,
    max_stocks: int = 300,
) -> pd.DataFrame:
    base = load_news_from_existing_df(existing_df)
    attempts = [
        {
            "data_source": "Existing News Fields",
            "rows": len(base),
            "data_status": base.attrs.get("news_status", "Unavailable"),
            "warning": base.attrs.get("news_warning", ""),
        }
    ]
    result = base
    if use_external and result.empty:
        for loader in (load_news_from_eastmoney, load_news_from_sina, load_news_from_akshare):
            external = loader(tickers=tickers, timeout=timeout, max_stocks=max_stocks)
            attempts.append(
                {
                    "data_source": external.attrs.get("news_source", loader.__name__),
                    "rows": len(external),
                    "data_status": external.attrs.get("news_status", "Unavailable"),
                    "warning": external.attrs.get("news_warning", ""),
                }
            )
            if not external.empty:
                result = external
                result.attrs.update(save_cached_news(external))
                break
        if result.empty:
            cached = load_cached_news()
            attempts.append(
                {
                    "data_source": "News Cache",
                    "rows": len(cached),
                    "data_status": cached.attrs.get("news_status", "Unavailable"),
                    "warning": cached.attrs.get("news_warning", ""),
                }
            )
            if not cached.empty:
                result = cached
    result = result.reindex(columns=NEWS_COLUMNS)
    result.attrs["news_attempts"] = attempts
    result.attrs["news_rows"] = len(result)
    result.attrs["news_status"] = "Available" if not result.empty else "Unavailable"
    result.attrs["news_source"] = result.attrs.get("news_source", "Mixed News")
    result.attrs.setdefault("news_warning", "" if not result.empty else "No news rows available.")
    result.attrs.setdefault("news_updated_at", _now_text())
    result.attrs.setdefault("cache_status", "Missing")
    result.attrs.setdefault("cache_path", str(CACHE_FILE))
    return result


__all__ = [
    "CACHE_DIR",
    "CACHE_FILE",
    "KEYWORD_RULES",
    "NEWS_COLUMNS",
    "build_news_dataset",
    "classify_news_keywords",
    "infer_news_sentiment",
    "load_cached_news",
    "load_news_from_akshare",
    "load_news_from_eastmoney",
    "load_news_from_existing_df",
    "load_news_from_sina",
    "news_event_score",
    "save_cached_news",
]

KEYWORD_RULES = [(keyword, classify_news_event(keyword)["news_sentiment_label"]) for keyword in [
    "业绩预增",
    "业绩预亏",
    "回购",
    "增持",
    "减持",
    "重大合同",
    "并购重组",
    "政策利好",
    "政策风险",
    "监管处罚",
    "AI",
    "算力",
    "半导体",
    "机器人",
    "新能源",
    "军工",
    "低空经济",
]]
