"""Read-only fundamental screening for the A-share research universe."""

from __future__ import annotations

import copy
import math

import pandas as pd


FUNDAMENTAL_SCREENING_FIELDS = [
    "fundamental_available",
    "roe",
    "revenue_growth",
    "profit_growth",
    "gross_margin",
    "debt_ratio",
    "operating_cashflow",
    "pe",
    "pb",
    "fundamental_score",
    "fundamental_level",
    "fundamental_screening_status",
    "fundamental_reasons",
    "fundamental_warnings",
]

METRIC_FIELDS = [
    "roe",
    "revenue_growth",
    "profit_growth",
    "gross_margin",
    "debt_ratio",
    "operating_cashflow",
    "pe",
    "pb",
]

KEY_ALIASES = {
    "ticker": ["ticker", "symbol", "code", "stock_code", "股票代码", "证券代码"],
}

FIELD_ALIASES = {
    "roe": ["roe", "ROE", "净资产收益率"],
    "revenue_growth": ["revenue_growth", "revenue_yoy", "营收增长率", "营业收入增长率"],
    "profit_growth": ["profit_growth", "net_profit_growth", "利润增长率", "净利润增长率"],
    "gross_margin": ["gross_margin", "毛利率"],
    "debt_ratio": ["debt_ratio", "asset_liability_ratio", "资产负债率"],
    "operating_cashflow": ["operating_cashflow", "operating_cash_flow", "经营现金流"],
    "pe": ["pe", "PE", "市盈率"],
    "pb": ["pb", "PB", "市净率"],
}

STATUS_INCOMPLETE = "Incomplete"
STATUS_PASS = "Pass"
STATUS_WATCH = "Watch"
STATUS_EXCLUDE = "Exclude"

LEVEL_HIGH = "High"
LEVEL_MEDIUM = "Medium"
LEVEL_LOW = "Low"
LEVEL_UNAVAILABLE = "Unavailable"


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


def _empty_like(universe):
    base = universe.copy(deep=True) if isinstance(universe, pd.DataFrame) else pd.DataFrame()
    for field in FUNDAMENTAL_SCREENING_FIELDS:
        base[field] = pd.Series(dtype="object")
    return base


def _first_existing(row, names):
    for name in names:
        if name in row:
            value = row[name]
            if pd.isna(value):
                continue
            if isinstance(value, str) and not value.strip():
                continue
            return value
    return None


def _normalize_ticker(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return text.zfill(6) if text.isdigit() else text


def _to_number(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)

    text = str(value).strip().replace(",", "")
    if not text:
        return None
    multiplier = 0.01 if text.endswith("%") else 1.0
    if text.endswith("%"):
        text = text[:-1].strip()
    try:
        return float(text) * multiplier
    except ValueError:
        return None


def _normalize_fundamental_frame(fundamental):
    if fundamental is None or fundamental.empty:
        return pd.DataFrame(columns=["ticker", *METRIC_FIELDS])

    rows = []
    for _, row in fundamental.iterrows():
        row_dict = row.to_dict()
        normalized = {"ticker": _normalize_ticker(_first_existing(row_dict, KEY_ALIASES["ticker"]))}
        for field in METRIC_FIELDS:
            normalized[field] = _to_number(_first_existing(row_dict, FIELD_ALIASES[field]))
        if normalized["ticker"]:
            rows.append(normalized)
    if not rows:
        return pd.DataFrame(columns=["ticker", *METRIC_FIELDS])
    return pd.DataFrame(rows).drop_duplicates(subset=["ticker"], keep="first")


def _score_row(row):
    values = {field: row.get(field) for field in METRIC_FIELDS}
    usable = {key: value for key, value in values.items() if value is not None and not pd.isna(value)}
    if not usable:
        return {
            "fundamental_available": False,
            "fundamental_score": 0,
            "fundamental_level": LEVEL_UNAVAILABLE,
            "fundamental_screening_status": STATUS_INCOMPLETE,
            "fundamental_reasons": [],
            "fundamental_warnings": ["No usable fundamental data."],
        }

    score = 0
    reasons = []
    warnings = []

    roe = values["roe"]
    if roe is None or pd.isna(roe):
        warnings.append("ROE missing.")
    elif roe >= 0.15:
        score += 25
        reasons.append("ROE is relatively strong.")
    elif roe >= 0.10:
        score += 18
        reasons.append("ROE is usable.")
    elif roe >= 0.05:
        score += 8
    else:
        warnings.append("ROE is weak or negative.")

    revenue_growth = values["revenue_growth"]
    if revenue_growth is None or pd.isna(revenue_growth):
        warnings.append("Revenue growth missing.")
    elif revenue_growth >= 0.15:
        score += 12
        reasons.append("Revenue growth is positive and strong.")
    elif revenue_growth > 0:
        score += 8
        reasons.append("Revenue growth is positive.")
    else:
        warnings.append("Revenue growth is non-positive.")

    profit_growth = values["profit_growth"]
    if profit_growth is None or pd.isna(profit_growth):
        warnings.append("Profit growth missing.")
    elif profit_growth >= 0.15:
        score += 12
        reasons.append("Profit growth is positive and strong.")
    elif profit_growth > 0:
        score += 8
        reasons.append("Profit growth is positive.")
    else:
        warnings.append("Profit growth is non-positive.")

    gross_margin = values["gross_margin"]
    if gross_margin is None or pd.isna(gross_margin):
        warnings.append("Gross margin missing.")
    elif gross_margin >= 0.35:
        score += 10
        reasons.append("Gross margin is healthy.")
    elif gross_margin >= 0.15:
        score += 5
    else:
        warnings.append("Gross margin is weak.")

    cashflow = values["operating_cashflow"]
    if cashflow is None or pd.isna(cashflow):
        warnings.append("Operating cashflow missing.")
    elif cashflow > 0:
        score += 15
        reasons.append("Operating cashflow is positive.")
    else:
        warnings.append("Operating cashflow is non-positive.")

    debt_ratio = values["debt_ratio"]
    if debt_ratio is None or pd.isna(debt_ratio):
        warnings.append("Debt ratio missing.")
    elif debt_ratio <= 0.40:
        score += 15
        reasons.append("Debt ratio is controlled.")
    elif debt_ratio <= 0.60:
        score += 8
    elif debt_ratio > 0.75:
        score -= 10
        warnings.append("Debt ratio is high.")
    else:
        warnings.append("Debt ratio needs attention.")

    pe = values["pe"]
    if pe is None or pd.isna(pe):
        warnings.append("PE missing.")
    elif pe <= 0 or pe > 80:
        score -= 5
        warnings.append("PE is abnormal.")
    elif pe <= 40:
        score += 7

    pb = values["pb"]
    if pb is None or pd.isna(pb):
        warnings.append("PB missing.")
    elif pb <= 0 or pb > 10:
        score -= 5
        warnings.append("PB is abnormal.")
    elif pb <= 6:
        score += 4

    score = int(max(0, min(100, score)))
    if score >= 75:
        level = LEVEL_HIGH
        status = STATUS_PASS
    elif score >= 50:
        level = LEVEL_MEDIUM
        status = STATUS_WATCH
    else:
        level = LEVEL_LOW
        status = STATUS_EXCLUDE if score < 30 else STATUS_WATCH

    return {
        "fundamental_available": True,
        "fundamental_score": score,
        "fundamental_level": level,
        "fundamental_screening_status": status,
        "fundamental_reasons": reasons,
        "fundamental_warnings": warnings,
    }


def build_fundamental_screening(universe_df, fundamental_df=None):
    """Append read-only fundamental screening fields to an A-share universe.

    The function preserves input rows, does not sort, and never mutates caller
    DataFrames. Missing or malformed fundamental data is represented with
    Incomplete/Unavailable fields instead of raising.
    """
    universe = _safe_copy_frame(universe_df)
    if universe is None:
        universe = pd.DataFrame()
    if universe.empty:
        return _empty_like(universe)

    result = universe.copy(deep=True)
    fundamental = _normalize_fundamental_frame(_safe_copy_frame(fundamental_df))

    if "ticker" in result.columns:
        universe_keys = result["ticker"].map(_normalize_ticker)
    elif "symbol" in result.columns:
        universe_keys = result["symbol"].map(_normalize_ticker)
    else:
        universe_keys = pd.Series([None] * len(result), index=result.index)

    fundamental_by_ticker = fundamental.set_index("ticker").to_dict(orient="index") if not fundamental.empty else {}

    output_rows = []
    for index, row in result.iterrows():
        metrics = fundamental_by_ticker.get(universe_keys.loc[index], {})
        scored_input = row.to_dict()
        for field in METRIC_FIELDS:
            scored_input[field] = metrics.get(field)
        scored = _score_row(scored_input)
        output_rows.append({**{field: scored_input.get(field) for field in METRIC_FIELDS}, **scored})

    output = pd.DataFrame(output_rows, index=result.index)
    for field in FUNDAMENTAL_SCREENING_FIELDS:
        result[field] = output[field].astype(object) if field == "fundamental_available" else output[field]
    return result


__all__ = [
    "FUNDAMENTAL_SCREENING_FIELDS",
    "build_fundamental_screening",
]
