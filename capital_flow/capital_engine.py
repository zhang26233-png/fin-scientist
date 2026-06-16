"""Capital-flow research scoring engine.

This module converts standardized capital-flow data into additive research
fields. It does not overwrite legacy selection scores and does not produce
trading instructions.
"""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd


CAPITAL_SCORE_CACHE_FILE = Path("cache/capital_flow/capital_score_cache.csv")

CAPITAL_ENGINE_FIELDS = [
    "ticker",
    "name",
    "turnover",
    "turnover_rate",
    "volume_ratio",
    "main_net_inflow",
    "main_net_inflow_ratio",
    "northbound_hold",
    "northbound_change",
    "capital_activity_score",
    "turnover_rate_score",
    "volume_ratio_score",
    "main_inflow_score",
    "northbound_score",
    "activity_score",
    "capital_flow_score",
    "capital_flow_rank",
    "capital_flow_summary",
    "capital_flow_strength",
    "capital_flow_status",
    "capital_flow_warning",
    "capital_flow_warnings",
    "capital_flow_source",
    "capital_flow_updated_at",
]

NUMERIC_FIELDS = [
    "turnover",
    "turnover_rate",
    "volume_ratio",
    "main_net_inflow",
    "main_net_inflow_ratio",
    "northbound_hold",
    "northbound_change",
    "capital_activity_score",
]


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _to_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value).strip().replace(",", "").replace("%", "")
        if not text or text in {"-", "--", "None", "nan"}:
            return None
        try:
            number = float(text)
        except ValueError:
            return None
    if pd.isna(number):
        return None
    return number


def _clip(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 2)


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


def _range_score(value: float | None, ranges: list[tuple[float, float]]) -> float:
    if value is None:
        return 50.0
    if value < ranges[0][0]:
        return ranges[0][1]
    previous_threshold, previous_score = ranges[0]
    for threshold, score in ranges[1:]:
        if value < threshold:
            ratio = (value - previous_threshold) / max(threshold - previous_threshold, 1e-9)
            return _clip(previous_score + ratio * (score - previous_score))
        previous_threshold, previous_score = threshold, score
    return ranges[-1][1]


def _turnover_rate_score(value: float | None) -> float:
    return _range_score(value, [(0, 30), (2, 45), (5, 65), (10, 82), (20, 70), (100, 45)])


def _volume_ratio_score(value: float | None) -> float:
    return _range_score(value, [(0, 35), (0.8, 50), (1.2, 65), (2, 82), (3, 90), (10, 70)])


def _main_inflow_score(value: float | None) -> float:
    if value is None:
        return 50.0
    return _clip(50.0 + max(-40.0, min(40.0, value * 4.0)))


def _northbound_score(value: float | None) -> float:
    if value is None:
        return 50.0
    return _clip(50.0 + max(-35.0, min(35.0, value / 10_000_000)))


def _activity_score(value: float | None) -> float:
    return _clip(value if value is not None else 50.0)


def _strength(score: float) -> str:
    if score >= 85:
        return "Strong Buy Research"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Medium"
    if score >= 40:
        return "Weak"
    return "Very Weak"


def _summary(row: dict[str, Any]) -> str:
    points: list[str] = []
    if (row.get("volume_ratio") or 0) >= 2:
        points.append("量比显著放大")
    if (row.get("main_net_inflow_ratio") or 0) >= 5:
        points.append("主力净流入较强")
    elif (row.get("main_net_inflow_ratio") or 0) <= -5:
        points.append("主力资金流出")
    if (row.get("northbound_change") or 0) > 0:
        points.append("北向资金流入")
    elif (row.get("northbound_change") or 0) < 0:
        points.append("北向资金减仓")
    if (row.get("turnover_rate") or 0) >= 5:
        points.append("换手较活跃")
    if (row.get("capital_activity_score") or 0) < 45:
        points.append("资金活跃度不足")
    return "，".join(points) if points else "资金面数据中性，需结合基本面、技术面和新闻事件继续研究"


def _warnings(row: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    turnover = row.get("turnover")
    if turnover is not None:
        normalized = turnover * 10_000 if 0 < turnover < 10_000_000 else turnover
        if normalized < 50_000_000:
            warnings.append("成交额过低")
    if row.get("volume_ratio") is not None and row["volume_ratio"] < 0.8:
        warnings.append("量比过低")
    if row.get("main_net_inflow_ratio") is not None and row["main_net_inflow_ratio"] <= -5:
        warnings.append("主力持续流出")
    if row.get("northbound_change") is not None and row["northbound_change"] < 0:
        warnings.append("北向持续减仓")
    if row.get("turnover_rate") is not None and row["turnover_rate"] > 20:
        warnings.append("换手异常")
    return warnings


def _empty() -> pd.DataFrame:
    frame = pd.DataFrame(columns=CAPITAL_ENGINE_FIELDS)
    frame.attrs.update(
        {
            "capital_flow_status": "Unavailable",
            "capital_flow_rows": 0,
            "capital_flow_updated_at": _now_text(),
            "capital_score_cache_status": "Skipped",
            "capital_score_cache_path": str(CAPITAL_SCORE_CACHE_FILE),
        }
    )
    return frame


def _cache_signature(source: pd.DataFrame) -> str:
    fields = ["ticker", *NUMERIC_FIELDS, "capital_flow_source", "capital_flow_updated_at"]
    available = [field for field in fields if field in source.columns]
    if not available:
        return ""
    normalized = source[available].copy(deep=True)
    if "ticker" in normalized.columns:
        normalized["ticker"] = normalized["ticker"].map(_normalize_ticker)
    if "ticker" in normalized.columns:
        normalized = normalized.sort_values("ticker", kind="mergesort")
    payload = normalized.fillna("").to_csv(index=False)
    return sha256(payload.encode("utf-8", errors="ignore")).hexdigest()


def _load_score_cache(signature: str, source: pd.DataFrame) -> pd.DataFrame | None:
    if not signature or not CAPITAL_SCORE_CACHE_FILE.exists():
        return None
    try:
        cached = pd.read_csv(CAPITAL_SCORE_CACHE_FILE, dtype={"ticker": str})
    except Exception:
        return None
    if cached.empty or "_capital_score_signature" not in cached.columns:
        return None
    if str(cached["_capital_score_signature"].iloc[0]) != signature:
        return None
    if "ticker" not in cached.columns or "ticker" not in source.columns:
        return None

    result = source.copy(deep=True)
    cached = cached.drop_duplicates(subset=["ticker"], keep="first")
    cached_map = cached.set_index("ticker").to_dict(orient="index")
    tickers = source["ticker"].map(_normalize_ticker)
    for field in CAPITAL_ENGINE_FIELDS:
        if field in {"ticker", "name"}:
            continue
        result[field] = [cached_map.get(ticker, {}).get(field) for ticker in tickers]
    result.attrs.update(getattr(source, "attrs", {}))
    result.attrs["capital_score_cache_status"] = "Hit"
    result.attrs["capital_score_cache_path"] = str(CAPITAL_SCORE_CACHE_FILE)
    result.attrs["capital_flow_rows"] = len(result)
    return result


def _save_score_cache(result: pd.DataFrame, signature: str) -> dict[str, Any]:
    if result.empty or not signature:
        return {"capital_score_cache_status": "Skipped", "capital_score_cache_path": str(CAPITAL_SCORE_CACHE_FILE)}
    try:
        CAPITAL_SCORE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cache = result.reindex(columns=CAPITAL_ENGINE_FIELDS).copy(deep=True)
        cache["_capital_score_signature"] = signature
        cache.to_csv(CAPITAL_SCORE_CACHE_FILE, index=False, encoding="utf-8-sig")
        return {
            "capital_score_cache_status": "Saved",
            "capital_score_cache_path": str(CAPITAL_SCORE_CACHE_FILE),
            "capital_score_cache_updated_at": _now_text(),
        }
    except Exception as exc:
        return {
            "capital_score_cache_status": "Error",
            "capital_score_cache_path": str(CAPITAL_SCORE_CACHE_FILE),
            "capital_score_cache_error": repr(exc),
        }


def build_capital_scores(df: pd.DataFrame | None, *, use_cache: bool = False) -> pd.DataFrame:
    """Append full capital-flow research scores without mutating input rows."""
    if df is None:
        return _empty()
    source = df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame(df).copy(deep=True)
    if source.empty:
        return _empty()
    signature = _cache_signature(source)
    if use_cache:
        cached = _load_score_cache(signature, source)
        if cached is not None:
            return cached

    rows: list[dict[str, Any]] = []
    for _, item in source.iterrows():
        raw = item.to_dict()
        row = {
            "ticker": _normalize_ticker(raw.get("ticker")),
            "name": raw.get("name", ""),
            "capital_flow_source": raw.get("capital_flow_source", "Capital Flow Engine"),
            "capital_flow_updated_at": raw.get("capital_flow_updated_at", _now_text()),
        }
        for field in NUMERIC_FIELDS:
            row[field] = _to_number(raw.get(field))
        row["turnover_rate_score"] = _turnover_rate_score(row["turnover_rate"])
        row["volume_ratio_score"] = _volume_ratio_score(row["volume_ratio"])
        row["main_inflow_score"] = _main_inflow_score(row["main_net_inflow_ratio"])
        row["northbound_score"] = _northbound_score(row["northbound_change"])
        row["activity_score"] = _activity_score(row["capital_activity_score"])
        row["capital_flow_score"] = _clip(
            (0.25 * row["turnover_rate_score"])
            + (0.20 * row["volume_ratio_score"])
            + (0.30 * row["main_inflow_score"])
            + (0.15 * row["northbound_score"])
            + (0.10 * row["activity_score"])
        )
        row["capital_flow_strength"] = _strength(row["capital_flow_score"])
        row["capital_flow_summary"] = _summary(row)
        warning_list = _warnings(row)
        existing_warning = raw.get("capital_flow_warning") or raw.get("capital_flow_warnings")
        if existing_warning:
            if isinstance(existing_warning, list):
                warning_list.extend(str(value) for value in existing_warning if value)
            else:
                warning_list.append(str(existing_warning))
        warning_list = list(dict.fromkeys(warning_list))
        row["capital_flow_warning"] = "，".join(warning_list)
        row["capital_flow_warnings"] = row["capital_flow_warning"]
        row["capital_flow_status"] = "Available" if row["ticker"] else "Unavailable"
        rows.append(row)

    result = source.copy(deep=True)
    scores = pd.DataFrame(rows, index=result.index)
    for field in CAPITAL_ENGINE_FIELDS:
        if field in {"ticker", "name"} and field in result.columns:
            continue
        result[field] = scores[field] if field in scores.columns else None
    if "capital_flow_score" in result.columns:
        result["capital_flow_rank"] = pd.to_numeric(result["capital_flow_score"], errors="coerce").rank(
            ascending=False,
            method="min",
        )
    result.attrs.update(getattr(df, "attrs", {}))
    result.attrs["capital_flow_status"] = "Available" if not result.empty else "Unavailable"
    result.attrs["capital_flow_rows"] = len(result)
    result.attrs["capital_flow_updated_at"] = _now_text()
    if use_cache:
        result.attrs.update(_save_score_cache(result, signature))
    else:
        result.attrs["capital_score_cache_status"] = "Disabled"
        result.attrs["capital_score_cache_path"] = str(CAPITAL_SCORE_CACHE_FILE)
    return result


__all__ = ["CAPITAL_ENGINE_FIELDS", "CAPITAL_SCORE_CACHE_FILE", "build_capital_scores"]
