"""Read-only event context standardization for research preview."""

import copy
import math
from datetime import date, datetime

import pandas as pd


EVENT_CONTEXT_FIELDS = [
    "event_available",
    "event_type",
    "event_recency_label",
    "event_source_quality_label",
    "event_reliability_label",
    "event_context_note",
    "event_research_tags",
    "event_warnings",
]

KNOWN_EVENT_TYPES = {
    "earnings",
    "policy",
    "industry",
    "macro",
    "product",
    "risk",
    "news_only",
    "unknown",
}

_EVENT_INPUT_FIELDS = [
    "event_title",
    "event_summary",
    "event_type",
    "event_date",
    "event_source",
    "event_source_type",
    "event_confidence",
]

_TYPE_KEYWORDS = {
    "earnings": ("earnings", "revenue", "profit", "quarter", "annual", "financial report", "业绩", "财报"),
    "policy": ("policy", "regulation", "regulator", "guidance", "政策", "监管"),
    "industry": ("industry", "sector", "supply chain", "capacity", "行业", "产业"),
    "macro": ("macro", "inflation", "rate", "gdp", "central bank", "宏观", "利率"),
    "product": ("product", "launch", "approval", "pipeline", "产品", "新品"),
    "risk": ("risk", "lawsuit", "investigation", "default", "recall", "风险", "调查"),
}

_OFFICIAL_SOURCE_TYPES = {"official", "filing", "exchange", "company", "regulator", "announcement"}
_MEDIA_SOURCE_TYPES = {"reliable_media", "media", "press", "news"}
_UNVERIFIED_SOURCE_TYPES = {"social", "rumor", "forum", "unverified"}


def _source_to_frame(source):
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, pd.Series):
        return pd.DataFrame([copy.deepcopy(source.to_dict())])
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    return pd.DataFrame()


def _row_dict(row):
    if hasattr(row, "to_dict"):
        return copy.deepcopy(row.to_dict())
    if isinstance(row, dict):
        return copy.deepcopy(row)
    return {}


def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _text(value):
    return "" if _is_missing(value) else str(value).strip()


def _event_available(row):
    return any(not _is_missing(row.get(field)) for field in _EVENT_INPUT_FIELDS if field != "event_type")


def _normalize_event_type(row):
    explicit = _text(row.get("event_type")).lower().replace("-", "_").replace(" ", "_")
    if explicit in KNOWN_EVENT_TYPES:
        return explicit
    if explicit == "news":
        return "news_only"

    searchable = " ".join([_text(row.get("event_title")), _text(row.get("event_summary"))]).lower()
    for event_type, keywords in _TYPE_KEYWORDS.items():
        if any(keyword.lower() in searchable for keyword in keywords):
            return event_type
    if searchable:
        return "news_only"
    return "unknown"


def _parse_event_date(value):
    if _is_missing(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(text[:10] if fmt != "%Y%m%d" else text[:8], fmt).date()
        except ValueError:
            continue
    try:
        parsed = pd.to_datetime(text, errors="coerce")
    except Exception:
        return None
    if pd.isna(parsed):
        return None
    return parsed.date()


def _recency_label(value, today=None):
    event_date = _parse_event_date(value)
    if event_date is None:
        return "Unknown"
    current = today or date.today()
    days = (current - event_date).days
    if days < 0:
        return "Unknown"
    if days <= 30:
        return "Recent"
    return "Stale"


def _source_quality_label(row):
    source_type = _text(row.get("event_source_type")).lower().replace("-", "_").replace(" ", "_")
    source = _text(row.get("event_source")).lower()
    if source_type in _OFFICIAL_SOURCE_TYPES or any(token in source for token in ("exchange", "sec", "official")):
        return "Official"
    if source_type in _MEDIA_SOURCE_TYPES or any(token in source for token in ("reuters", "bloomberg", "xinhua")):
        return "Reliable Media"
    if source_type in _UNVERIFIED_SOURCE_TYPES:
        return "Unverified"
    if source:
        return "Unknown"
    return "Unknown"


def _confidence_label(value):
    if _is_missing(value):
        return ""
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"high", "medium", "low"}:
            return text.title()
        try:
            value = float(text)
        except ValueError:
            return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(number):
        return ""
    if number > 1:
        number = number / 100
    if number >= 0.75:
        return "High"
    if number >= 0.45:
        return "Medium"
    return "Low"


def _reliability_label(row, source_quality):
    confidence = _confidence_label(row.get("event_confidence"))
    if confidence:
        return confidence
    if source_quality == "Official":
        return "High"
    if source_quality == "Reliable Media":
        return "Medium"
    if source_quality == "Unverified":
        return "Low"
    return "Unknown"


def _research_tags(event_type, source_quality, reliability):
    tags = []
    if event_type == "earnings":
        tags.append("earnings_check")
    elif event_type == "policy":
        tags.append("policy_watch")
    elif event_type == "industry":
        tags.append("industry_review")
    elif event_type == "macro":
        tags.append("macro_watch")
    elif event_type == "product":
        tags.append("product_followup")
    elif event_type == "risk":
        tags.append("risk_review")
    elif event_type == "news_only":
        tags.append("news_context_review")
    else:
        tags.append("event_classification_review")

    if source_quality in {"Unverified", "Unknown"} or reliability in {"Low", "Unknown"}:
        tags.append("source_validation")
    return list(dict.fromkeys(tags))


def _context_note(available, event_type, recency, source_quality, reliability):
    if not available:
        return "No usable event context is available for the current research preview."
    parts = [f"{event_type} event context is available"]
    if recency == "Recent":
        parts.append("recent timing may support follow-up evidence review")
    elif recency == "Stale":
        parts.append("timing is stale and should be checked against newer evidence")
    else:
        parts.append("timing is unclear")
    parts.append(f"source quality is {source_quality}")
    parts.append(f"reliability is {reliability}")
    return "; ".join(parts) + "."


def _warnings(row, available, event_type, recency, source_quality, reliability):
    warnings = []
    if not available:
        warnings.append("event input unavailable")
        return warnings
    if event_type in {"unknown", "news_only"}:
        warnings.append("event type needs classification review")
    if recency == "Unknown":
        warnings.append("event date missing or invalid")
    if source_quality == "Unknown":
        warnings.append("event source quality unavailable")
    if reliability == "Unknown":
        warnings.append("event reliability unavailable")
    if _is_missing(row.get("event_summary")) and _is_missing(row.get("event_title")):
        warnings.append("event title and summary unavailable")
    return warnings


def build_event_context_row(row, today=None):
    row_data = _row_dict(row)
    available = _event_available(row_data)
    event_type = _normalize_event_type(row_data) if available else "unknown"
    recency = _recency_label(row_data.get("event_date"), today=today) if available else "Unknown"
    source_quality = _source_quality_label(row_data) if available else "Unknown"
    reliability = _reliability_label(row_data, source_quality) if available else "Unknown"

    return {
        "event_available": bool(available),
        "event_type": event_type,
        "event_recency_label": recency,
        "event_source_quality_label": source_quality,
        "event_reliability_label": reliability,
        "event_context_note": _context_note(available, event_type, recency, source_quality, reliability),
        "event_research_tags": _research_tags(event_type, source_quality, reliability) if available else [],
        "event_warnings": _warnings(row_data, available, event_type, recency, source_quality, reliability),
    }


def build_event_context_profile(source, today=None):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=EVENT_CONTEXT_FIELDS)
    rows = [build_event_context_row(row, today=today) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=EVENT_CONTEXT_FIELDS)


__all__ = [
    "EVENT_CONTEXT_FIELDS",
    "KNOWN_EVENT_TYPES",
    "build_event_context_profile",
    "build_event_context_row",
]
