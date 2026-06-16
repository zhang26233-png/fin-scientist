"""News and event data foundation with keyword classification.

This module intentionally uses simple keyword rules rather than complex NLP.
It is for learning and research context only and does not generate operational
investment conclusions.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests


CACHE_DIR = Path("cache/news")
CACHE_FILE = CACHE_DIR / "news_latest.csv"
MIN_CACHE_ROWS = 20

NEWS_COLUMNS = [
    "ticker",
    "name",
    "news_title",
    "news_time",
    "news_source",
    "news_url",
    "news_type",
    "news_keywords",
    "news_sentiment_label",
    "news_event_score",
    "news_summary",
    "news_warning",
]

KEYWORD_RULES = [
    ("业绩预增", "Positive"),
    ("业绩预亏", "Negative"),
    ("回购", "Positive"),
    ("增持", "Positive"),
    ("减持", "Negative"),
    ("重大合同", "Positive"),
    ("并购重组", "Neutral"),
    ("政策利好", "Positive"),
    ("政策风险", "Negative"),
    ("监管处罚", "Negative"),
    ("AI", "Neutral"),
    ("算力", "Neutral"),
    ("半导体", "Neutral"),
    ("机器人", "Neutral"),
    ("新能源", "Neutral"),
    ("军工", "Neutral"),
    ("低空经济", "Neutral"),
]

FIELD_ALIASES = {
    "ticker": ["ticker", "code", "symbol", "SECURITY_CODE"],
    "name": ["name", "stock_name", "SECURITY_NAME_ABBR"],
    "news_title": ["news_title", "title", "TITLE", "content"],
    "news_time": ["news_time", "time", "datetime", "NOTICE_DATE", "PUBLISH_TIME"],
    "news_source": ["news_source", "source", "SOURCE"],
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


def classify_news_keywords(title: Any, summary: Any = "") -> list[str]:
    text = f"{title or ''} {summary or ''}".upper()
    found: list[str] = []
    for keyword, _sentiment in KEYWORD_RULES:
        token = keyword.upper()
        if token in text and keyword not in found:
            found.append(keyword)
    return found


def infer_news_sentiment(keywords: list[str] | str | None) -> str:
    if keywords is None:
        return "Unknown"
    values = [keywords] if isinstance(keywords, str) else list(keywords)
    sentiments = [sentiment for keyword, sentiment in KEYWORD_RULES if keyword in values]
    if any(item == "Negative" for item in sentiments):
        return "Negative"
    if any(item == "Positive" for item in sentiments):
        return "Positive"
    if sentiments:
        return "Neutral"
    return "Unknown"


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
        }
    )
    return frame


def _standardize_frame(source: pd.DataFrame | None, *, data_source: str, data_status: str = "Available", warning: str = "") -> pd.DataFrame:
    if source is None or source.empty:
        return _empty(status="Unavailable", warning=warning)
    rows: list[dict[str, Any]] = []
    for _, item in source.iterrows():
        raw = item.to_dict()
        ticker = _normalize_ticker(_first_existing(raw, "ticker"))
        title = _first_existing(raw, "news_title")
        if not ticker or not title:
            continue
        keywords = raw.get("news_keywords")
        if not keywords:
            keywords = classify_news_keywords(title, raw.get("news_summary", ""))
        if isinstance(keywords, str):
            keywords = [part.strip() for part in keywords.replace(";", ",").split(",") if part.strip()]
        sentiment = raw.get("news_sentiment_label") or infer_news_sentiment(keywords)
        score = raw.get("news_event_score")
        try:
            score_value = int(float(score))
        except (TypeError, ValueError):
            score_value = news_event_score(str(sentiment))
        rows.append(
            {
                "ticker": ticker,
                "name": _first_existing(raw, "name") or "",
                "news_title": str(title),
                "news_time": _first_existing(raw, "news_time") or _now_text(),
                "news_source": _first_existing(raw, "news_source") or data_source,
                "news_url": _first_existing(raw, "news_url") or "",
                "news_type": raw.get("news_type") or (keywords[0] if keywords else "Unclassified"),
                "news_keywords": keywords,
                "news_sentiment_label": sentiment,
                "news_event_score": max(0, min(100, score_value)),
                "news_summary": raw.get("news_summary") or f"Keyword classification: {', '.join(keywords) if keywords else 'Unknown'}",
                "news_warning": raw.get("news_warning") or warning,
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
        }
    )
    return frame


def load_news_from_existing_df(df: pd.DataFrame | None) -> pd.DataFrame:
    return _standardize_frame(df, data_source="Existing News Fields", data_status="Available")


def load_news_from_eastmoney(tickers: list[str] | None = None, timeout: int = 10, max_stocks: int = 200) -> pd.DataFrame:
    _ = max_stocks
    try:
        # Public notice/news search endpoint variants change frequently. Keep
        # parsing flexible and degrade cleanly if it is unavailable.
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


def load_news_from_sina(tickers: list[str] | None = None, timeout: int = 10, max_stocks: int = 200) -> pd.DataFrame:
    _ = tickers, timeout, max_stocks
    return _empty(status="Unavailable", warning="Sina news source is not available in this local run.")


def load_news_from_akshare(tickers: list[str] | None = None, timeout: int = 10, max_stocks: int = 200) -> pd.DataFrame:
    _ = timeout, max_stocks
    try:
        import akshare as ak

        if hasattr(ak, "stock_news_em"):
            frames = []
            for ticker in (tickers or [])[: max_stocks]:
                try:
                    frames.append(ak.stock_news_em(symbol=str(ticker)))
                except Exception:
                    continue
            raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        else:
            return _empty(status="Error", warning="akshare stock_news_em is unavailable.")
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
    max_stocks: int = 200,
) -> pd.DataFrame:
    base = load_news_from_existing_df(existing_df)
    attempts = [{"data_source": "Existing News Fields", "rows": len(base), "data_status": base.attrs.get("news_status", "Unavailable"), "warning": base.attrs.get("news_warning", "")}]
    result = base
    if use_external and result.empty:
        for loader in (load_news_from_eastmoney, load_news_from_sina, load_news_from_akshare):
            external = loader(tickers=tickers, timeout=timeout, max_stocks=max_stocks)
            attempts.append({"data_source": external.attrs.get("news_source", loader.__name__), "rows": len(external), "data_status": external.attrs.get("news_status", "Unavailable"), "warning": external.attrs.get("news_warning", "")})
            if not external.empty:
                result = external
                result.attrs.update(save_cached_news(external))
                break
        if result.empty:
            cached = load_cached_news()
            attempts.append({"data_source": "News Cache", "rows": len(cached), "data_status": cached.attrs.get("news_status", "Unavailable"), "warning": cached.attrs.get("news_warning", "")})
            if not cached.empty:
                result = cached
    result = result.reindex(columns=NEWS_COLUMNS)
    result.attrs["news_attempts"] = attempts
    result.attrs["news_rows"] = len(result)
    result.attrs["news_status"] = "Available" if not result.empty else "Unavailable"
    result.attrs["news_source"] = result.attrs.get("news_source", "Mixed News")
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
