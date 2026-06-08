"""A-share universe builder for research screening entry points."""

from __future__ import annotations

import copy
from datetime import date, datetime

import pandas as pd


UNIVERSE_FIELDS = [
    "ticker",
    "name",
    "market",
    "list_date",
    "days_since_listing",
    "is_st",
    "is_suspended",
    "status",
    "universe_status",
    "universe_total_count",
    "universe_filtered_count",
    "universe_summary",
]

REQUIRED_FIELDS = [
    "ticker",
    "name",
    "market",
    "list_date",
    "days_since_listing",
    "is_st",
    "is_suspended",
    "status",
]

DEFAULT_MIN_LISTING_DAYS = 250
DEFAULT_MARKET = "A股"
STATUS_AVAILABLE = "Available"
STATUS_INCOMPLETE = "Incomplete"


def _empty_universe(summary="全市场0只；过滤后0只；剔除ST 0只；剔除停牌 0只；剔除新股 0只。"):
    frame = pd.DataFrame(columns=UNIVERSE_FIELDS)
    frame.attrs["universe_status"] = STATUS_INCOMPLETE
    frame.attrs["universe_total_count"] = 0
    frame.attrs["universe_filtered_count"] = 0
    frame.attrs["universe_summary"] = summary
    return frame


def _safe_copy_frame(source):
    if source is None:
        return None
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    return pd.DataFrame()


def _fetch_akshare_a_share_spot():
    try:
        import akshare as ak
    except Exception:
        return pd.DataFrame()

    try:
        return ak.stock_zh_a_spot_em()
    except Exception:
        return pd.DataFrame()


def _first_existing(row, names, default=None):
    for name in names:
        if name in row and not pd.isna(row[name]):
            value = row[name]
            if isinstance(value, str) and not value.strip():
                continue
            return value
    return default


def _normalize_ticker(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else text


def _parse_list_date(value, today):
    if pd.isna(value) or value in ("", None):
        return None, None
    if isinstance(value, (datetime, date)):
        parsed = value.date() if isinstance(value, datetime) else value
        return parsed.isoformat(), max((today - parsed).days, 0)

    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            parsed = datetime.strptime(text, fmt).date()
            return parsed.isoformat(), max((today - parsed).days, 0)
        except ValueError:
            continue
    return text, None


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y", "是", "停牌", "暂停上市"}


def _normalize_source_frame(source_frame, today):
    rows = []
    for _, row in source_frame.iterrows():
        row_dict = row.to_dict()
        name = _first_existing(row_dict, ["name", "名称", "股票简称", "证券简称"], "")
        ticker = _normalize_ticker(_first_existing(row_dict, ["ticker", "代码", "symbol", "证券代码"]))
        list_date, days_since_listing = _parse_list_date(
            _first_existing(row_dict, ["list_date", "上市日期", "上市时间"]),
            today,
        )
        explicit_days = _first_existing(row_dict, ["days_since_listing", "上市天数"])
        if explicit_days is not None and not pd.isna(explicit_days):
            try:
                days_since_listing = int(explicit_days)
            except (TypeError, ValueError):
                pass

        is_st = _parse_bool(_first_existing(row_dict, ["is_st", "ST", "是否ST"], False)) or "ST" in str(name).upper()
        status_text = str(_first_existing(row_dict, ["status", "状态", "交易状态"], "") or "")
        is_suspended = _parse_bool(_first_existing(row_dict, ["is_suspended", "停牌", "是否停牌"], False))
        if "停牌" in status_text or "暂停" in status_text:
            is_suspended = True

        rows.append(
            {
                "ticker": ticker,
                "name": str(name).strip(),
                "market": _first_existing(row_dict, ["market", "市场"], DEFAULT_MARKET),
                "list_date": list_date,
                "days_since_listing": days_since_listing,
                "is_st": bool(is_st),
                "is_suspended": bool(is_suspended),
                "status": status_text or STATUS_AVAILABLE,
            }
        )
    return pd.DataFrame(rows, columns=REQUIRED_FIELDS)


def _summary(total_count, filtered_count, st_count, suspended_count, new_count):
    return (
        f"全市场{total_count}只；过滤后{filtered_count}只；"
        f"剔除ST {st_count}只；剔除停牌 {suspended_count}只；剔除新股 {new_count}只。"
    )


def _attach_universe_fields(frame, universe_status, total_count, filtered_count, summary):
    result = frame.copy(deep=True)
    result["universe_status"] = universe_status
    result["universe_total_count"] = total_count
    result["universe_filtered_count"] = filtered_count
    result["universe_summary"] = summary
    result = result.reindex(columns=UNIVERSE_FIELDS)
    result.attrs["universe_status"] = universe_status
    result.attrs["universe_total_count"] = total_count
    result.attrs["universe_filtered_count"] = filtered_count
    result.attrs["universe_summary"] = summary
    return result


def build_a_share_universe(source=None, min_listing_days=DEFAULT_MIN_LISTING_DAYS, today=None):
    """Build the default filtered A-share research universe.

    If source is None, AkShare is used as the preferred source. Any fetch or
    normalization failure returns an empty DataFrame with universe metadata.
    """
    today_date = today or date.today()
    source_frame = _safe_copy_frame(source)
    if source_frame is None:
        source_frame = _fetch_akshare_a_share_spot()

    if source_frame is None or source_frame.empty:
        return _empty_universe()

    try:
        normalized = _normalize_source_frame(source_frame, today_date)
    except Exception:
        return _empty_universe()

    if normalized.empty:
        return _empty_universe()

    total_count = len(normalized)
    st_mask = normalized["is_st"].fillna(False)
    suspended_mask = normalized["is_suspended"].fillna(False)
    days = pd.to_numeric(normalized["days_since_listing"], errors="coerce")
    new_mask = days.lt(min_listing_days) | days.isna()
    delisted_mask = normalized["status"].astype(str).str.contains("退市|Delisted|delisted", regex=True, na=False)

    available_mask = ~(st_mask | suspended_mask | new_mask | delisted_mask)
    filtered = normalized.loc[available_mask].copy()
    filtered["status"] = STATUS_AVAILABLE

    summary = _summary(
        total_count=total_count,
        filtered_count=len(filtered),
        st_count=int(st_mask.sum()),
        suspended_count=int(suspended_mask.sum()),
        new_count=int(new_mask.sum()),
    )
    universe_status = STATUS_AVAILABLE if total_count > 0 else STATUS_INCOMPLETE
    return _attach_universe_fields(filtered, universe_status, total_count, len(filtered), summary)


__all__ = [
    "DEFAULT_MARKET",
    "DEFAULT_MIN_LISTING_DAYS",
    "REQUIRED_FIELDS",
    "STATUS_AVAILABLE",
    "STATUS_INCOMPLETE",
    "UNIVERSE_FIELDS",
    "build_a_share_universe",
]
