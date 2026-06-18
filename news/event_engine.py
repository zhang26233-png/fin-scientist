"""News and event research scoring engine.

The engine uses explicit keyword rules only. It is additive, research-only,
and does not produce operational conclusions.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd


NEWS_EVENT_CACHE_FILE = Path("cache/news/news_event_cache.csv")
MIN_EVENT_CACHE_ROWS = 10

NEWS_EVENT_FIELDS = [
    "ticker",
    "name",
    "news_title",
    "news_time",
    "news_source",
    "news_url",
    "news_type",
    "news_keywords",
    "news_sentiment_label",
    "news_heat_score",
    "news_risk_score",
    "news_event_score",
    "news_summary",
    "news_reason",
    "news_warning",
    "news_status",
    "news_updated_at",
]

POSITIVE_KEYWORDS = [
    "订单",
    "中标",
    "业绩预增",
    "回购",
    "增持",
    "突破",
    "算力",
    "AI",
    "军工",
    "国产替代",
    "业绩预增",
    "净利润增长",
    "营收增长",
    "回购",
    "增持",
    "重大合同",
    "中标",
    "并购重组",
    "订单",
    "产能扩张",
    "政策利好",
    "融资进展",
    "新品发布",
    "AI",
    "算力",
    "半导体",
    "机器人",
    "低空经济",
    "新能源",
    "军工",
]

NEGATIVE_KEYWORDS = [
    "减持",
    "诉讼",
    "处罚",
    "亏损",
    "退市",
    "风险提示",
    "业绩预亏",
    "亏损扩大",
    "减持",
    "立案调查",
    "监管处罚",
    "问询函",
    "债务违约",
    "诉讼",
    "商誉减值",
    "退市风险",
    "暂停上市",
    "安全事故",
    "高管离职",
    "大额解禁",
]

NEUTRAL_KEYWORDS = ["公告", "调研", "会议", "日常经营", "行业新闻", "未识别事件"]
HOT_INDUSTRY_KEYWORDS = ["AI", "算力", "半导体", "机器人", "低空经济", "新能源", "军工", "芯片", "数据中心"]
SEVERE_RISK_KEYWORDS = ["监管处罚", "立案调查", "退市风险"]


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _clip(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 2)


POSITIVE_EVENT_WEIGHTS = {
    "订单": 5,
    "中标": 6,
    "业绩预增": 8,
    "回购": 5,
    "增持": 5,
    "突破": 4,
    "算力": 4,
    "AI": 4,
    "军工": 4,
    "国产替代": 5,
}

NEGATIVE_EVENT_WEIGHTS = {
    "减持": 6,
    "诉讼": 8,
    "处罚": 10,
    "亏损": 8,
    "退市": 15,
    "风险提示": 10,
}


def _normalize_ticker(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else text


def _string(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


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


def classify_news_event(title: Any, content: Any = None) -> dict[str, Any]:
    """Classify a news title/content pair with deterministic keyword rules."""
    text = f"{_string(title)} {_string(content)}"
    found_positive = [keyword for keyword in POSITIVE_KEYWORDS if keyword in text]
    found_negative = [keyword for keyword in NEGATIVE_KEYWORDS if keyword in text]
    found_neutral = [keyword for keyword in NEUTRAL_KEYWORDS if keyword in text]

    if found_negative:
        sentiment = "Negative"
        event_type = found_negative[0]
        keywords = found_negative + [keyword for keyword in found_positive + found_neutral if keyword not in found_negative]
    elif found_positive:
        sentiment = "Positive"
        event_type = found_positive[0]
        keywords = found_positive + [keyword for keyword in found_neutral if keyword not in found_positive]
    elif found_neutral:
        sentiment = "Neutral"
        event_type = found_neutral[0]
        keywords = found_neutral
    elif text.strip():
        sentiment = "Neutral"
        event_type = "未识别事件"
        keywords = ["未识别事件"]
    else:
        sentiment = "Unknown"
        event_type = "未识别事件"
        keywords = []

    return {
        "news_type": event_type,
        "news_keywords": list(dict.fromkeys(keywords)),
        "news_sentiment_label": sentiment,
    }


def _parse_time(value: Any) -> datetime | None:
    text = _string(value)
    if not text:
        return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime()


def _heat_score(keywords: list[str], same_day_count: int) -> float:
    score = 50.0
    hot_hits = [keyword for keyword in keywords if keyword in HOT_INDUSTRY_KEYWORDS]
    hot_hits.extend(keyword for keyword in keywords if keyword in {"AI", "算力", "军工", "国产替代"})
    if len(hot_hits) >= 2:
        score += 20
    elif hot_hits:
        score += 10
    if same_day_count >= 5:
        score += 15
    elif same_day_count >= 3:
        score += 10
    elif same_day_count >= 2:
        score += 5
    return _clip(score)


def _risk_score(sentiment: str, keywords: list[str]) -> float:
    if any(keyword in keywords for keyword in SEVERE_RISK_KEYWORDS) or any(keyword in keywords for keyword in {"退市", "风险提示"}):
        return 20.0
    if sentiment == "Negative":
        hit_count = sum(1 for keyword in keywords if keyword in NEGATIVE_KEYWORDS)
        return _clip(50 - min(40, 20 + hit_count * 10))
    return 50.0


def _event_score(sentiment: str, heat_score: float, risk_score: float, keywords: list[str]) -> float:
    positive_bonus = sum(POSITIVE_EVENT_WEIGHTS.get(keyword, 0) for keyword in keywords)
    negative_penalty = sum(NEGATIVE_EVENT_WEIGHTS.get(keyword, 0) for keyword in keywords)
    if sentiment == "Positive":
        return _clip(70 + min(20, max(0, heat_score - 50) * 0.5) + min(12, positive_bonus))
    if sentiment == "Negative":
        if any(keyword in keywords for keyword in SEVERE_RISK_KEYWORDS) or any(keyword in keywords for keyword in {"退市", "风险提示"}):
            return _clip(min(30, risk_score + 5))
        return _clip(max(10, min(40, risk_score - min(15, negative_penalty))))
    if sentiment == "Neutral":
        return _clip(50 + min(10, max(0, heat_score - 50) * 0.25))
    return 50.0


def _summary(sentiment: str, keywords: list[str]) -> str:
    positive = [keyword for keyword in keywords if keyword in POSITIVE_KEYWORDS]
    negative = [keyword for keyword in keywords if keyword in NEGATIVE_KEYWORDS]
    if sentiment == "Positive":
        topics = "、".join(positive[:3]) or "产业催化"
        return f"近期新闻偏正面，主要涉及{topics}。"
    if sentiment == "Negative":
        risks = "、".join(negative[:3]) or "事件风险"
        return f"新闻事件偏负面，存在{risks}。"
    return "暂无明显新闻催化，事件影响中性。"


def _reason(sentiment: str, keywords: list[str], heat_score: float, same_day_count: int) -> str:
    reasons: list[str] = []
    if keywords:
        reasons.append("关键词：" + "、".join(keywords[:3]))
    reasons.append(f"情绪标签：{sentiment}")
    if heat_score > 60:
        reasons.append("热点产业词或同日新闻数量提高热度")
    if same_day_count > 1:
        reasons.append(f"同一标的当日新闻 {same_day_count} 条")
    return "；".join(reasons[:3])


def _warning(row: dict[str, Any], sentiment: str, keywords: list[str], source_warning: str, lookback_days: int) -> str:
    warnings: list[str] = []
    if sentiment == "Negative":
        warnings.append("存在负面新闻风险")
    if any(keyword in keywords for keyword in SEVERE_RISK_KEYWORDS):
        warnings.append("存在监管或重大风险事件")
    if not _string(row.get("news_title")):
        warnings.append("新闻缺失")
    if not _string(row.get("news_source")):
        warnings.append("来源不可用")
    parsed = _parse_time(row.get("news_time"))
    if parsed is not None and parsed < datetime.now() - timedelta(days=max(int(lookback_days), 0)):
        warnings.append("新闻时间过旧")
    if source_warning:
        warnings.append(source_warning)
    return "，".join(list(dict.fromkeys(warnings)))


def _empty(status: str = "Unavailable", warning: str = "") -> pd.DataFrame:
    frame = pd.DataFrame(columns=NEWS_EVENT_FIELDS)
    frame.attrs.update(
        {
            "news_source": "Unavailable",
            "news_status": status,
            "news_rows": 0,
            "news_warning": warning,
            "news_updated_at": _now_text(),
            "news_event_cache_status": "Skipped",
            "news_event_cache_path": str(NEWS_EVENT_CACHE_FILE),
        }
    )
    return frame


def _same_day_counts(source: pd.DataFrame) -> dict[tuple[str, str], int]:
    if source.empty or "ticker" not in source.columns:
        return {}
    counts: dict[tuple[str, str], int] = {}
    for _, row in source.iterrows():
        ticker = _normalize_ticker(row.get("ticker"))
        parsed = _parse_time(row.get("news_time"))
        day = parsed.strftime("%Y-%m-%d") if parsed else ""
        key = (ticker, day)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _save_event_cache(result: pd.DataFrame) -> dict[str, Any]:
    if result.empty or len(result) < MIN_EVENT_CACHE_ROWS:
        return {"news_event_cache_status": "Skipped", "news_event_cache_path": str(NEWS_EVENT_CACHE_FILE)}
    try:
        NEWS_EVENT_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cache = result.reindex(columns=NEWS_EVENT_FIELDS).copy(deep=True)
        cache["news_keywords"] = cache["news_keywords"].map(lambda value: ",".join(value) if isinstance(value, list) else value)
        cache.to_csv(NEWS_EVENT_CACHE_FILE, index=False, encoding="utf-8-sig")
        return {
            "news_event_cache_status": "Saved",
            "news_event_cache_path": str(NEWS_EVENT_CACHE_FILE),
            "news_event_cache_updated_at": _now_text(),
        }
    except Exception as exc:
        return {
            "news_event_cache_status": "Error",
            "news_event_cache_path": str(NEWS_EVENT_CACHE_FILE),
            "news_event_cache_error": repr(exc),
        }


def load_news_event_cache() -> pd.DataFrame:
    if not NEWS_EVENT_CACHE_FILE.exists():
        return _empty(status="Unavailable", warning="News event cache is missing.")
    try:
        raw = pd.read_csv(NEWS_EVENT_CACHE_FILE, dtype={"ticker": str})
    except Exception as exc:
        frame = _empty(status="Error", warning=repr(exc))
        frame.attrs["news_event_cache_status"] = "Error"
        return frame
    frame = raw.reindex(columns=NEWS_EVENT_FIELDS)
    if "news_keywords" in frame.columns:
        frame["news_keywords"] = frame["news_keywords"].map(_as_keywords)
    frame.attrs.update(
        {
            "news_source": "News Event Cache",
            "news_status": "Cache" if not frame.empty else "Unavailable",
            "news_rows": len(frame),
            "news_warning": "" if not frame.empty else "News event cache is empty.",
            "news_updated_at": datetime.fromtimestamp(NEWS_EVENT_CACHE_FILE.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "news_event_cache_status": "Available" if not frame.empty else "Missing",
            "news_event_cache_path": str(NEWS_EVENT_CACHE_FILE),
        }
    )
    return frame


def build_news_event_scores(
    df: pd.DataFrame | None,
    *,
    use_cache: bool = False,
    lookback_days: int = 7,
) -> pd.DataFrame:
    """Append news event research fields without mutating input rows."""
    if df is None:
        return load_news_event_cache() if use_cache else _empty()
    source = df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame(df).copy(deep=True)
    if source.empty:
        return load_news_event_cache() if use_cache else _empty()

    counts = _same_day_counts(source)
    rows: list[dict[str, Any]] = []
    source_warning = _string(getattr(df, "attrs", {}).get("news_warning", ""))
    for _, item in source.iterrows():
        raw = item.to_dict()
        ticker = _normalize_ticker(raw.get("ticker"))
        classification = classify_news_event(raw.get("news_title"), raw.get("news_summary") or raw.get("content"))
        existing_keywords = _as_keywords(raw.get("news_keywords"))
        keywords = list(dict.fromkeys(existing_keywords or classification["news_keywords"]))
        sentiment = _string(raw.get("news_sentiment_label")) or classification["news_sentiment_label"]
        if sentiment not in {"Positive", "Neutral", "Negative", "Unknown"}:
            sentiment = classification["news_sentiment_label"]
        news_type = _string(raw.get("news_type")) or classification["news_type"]
        parsed = _parse_time(raw.get("news_time"))
        news_time = _string(raw.get("news_time")) or _now_text()
        same_day_count = counts.get((ticker, parsed.strftime("%Y-%m-%d") if parsed else ""), 1)
        heat = _heat_score(keywords, same_day_count)
        risk = _risk_score(sentiment, keywords)
        event_score = _event_score(sentiment, heat, risk, keywords)
        row = {
            "ticker": ticker,
            "name": _string(raw.get("name")),
            "news_title": _string(raw.get("news_title")),
            "news_time": news_time,
            "news_source": _string(raw.get("news_source")) or "Unknown",
            "news_url": _string(raw.get("news_url")),
            "news_type": news_type,
            "news_keywords": keywords,
            "news_sentiment_label": sentiment,
            "news_heat_score": heat,
            "news_risk_score": risk,
            "news_event_score": event_score,
            "news_summary": _string(raw.get("news_summary")) or _summary(sentiment, keywords),
            "news_reason": _string(raw.get("news_reason")) or _reason(sentiment, keywords, heat, same_day_count),
            "news_warning": _warning(raw, sentiment, keywords, source_warning, lookback_days),
            "news_status": "Available" if _string(raw.get("news_title")) else "Unavailable",
            "news_updated_at": _now_text(),
        }
        if not row["news_title"]:
            row["news_sentiment_label"] = "Unknown"
            row["news_event_score"] = 50.0
            row["news_heat_score"] = 50.0
            row["news_risk_score"] = 50.0
            row["news_summary"] = "暂无明显新闻催化，事件影响中性。"
        rows.append(row)

    result = pd.DataFrame(rows, columns=NEWS_EVENT_FIELDS)
    if "ticker" in result.columns:
        result = result.drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    result.attrs.update(getattr(df, "attrs", {}))
    result.attrs["news_source"] = result.attrs.get("news_source", "News Event Engine")
    result.attrs["news_status"] = "Available" if not result.empty else "Unavailable"
    result.attrs["news_rows"] = len(result)
    result.attrs["news_updated_at"] = _now_text()
    if use_cache:
        result.attrs.update(_save_event_cache(result))
    else:
        result.attrs["news_event_cache_status"] = "Disabled"
        result.attrs["news_event_cache_path"] = str(NEWS_EVENT_CACHE_FILE)
    return result


__all__ = [
    "NEWS_EVENT_CACHE_FILE",
    "NEWS_EVENT_FIELDS",
    "build_news_event_scores",
    "classify_news_event",
    "load_news_event_cache",
]
