"""Additive fundamental research fields for A-share research rows."""

from __future__ import annotations

from typing import Any

import pandas as pd


FUNDAMENTAL_RESEARCH_FIELDS = [
    "fundamental_available",
    "fundamental_data_source",
    "fundamental_data_status",
    "fundamental_data_warning",
    "fundamental_updated_at",
    "pe_ttm",
    "pb",
    "ps_ttm",
    "market_cap",
    "float_market_cap",
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "deducted_profit_growth_yoy",
    "debt_to_asset",
    "operating_cash_flow",
    "ocf_to_net_profit",
    "dividend_yield",
    "valuation_score",
    "profitability_score",
    "growth_score",
    "financial_quality_score",
    "fundamental_research_score",
    "fundamental_reason",
    "fundamental_summary",
    "fundamental_strengths",
    "fundamental_risks",
    "fundamental_warnings",
]

NUMERIC_FIELDS = [
    "pe_ttm",
    "pb",
    "ps_ttm",
    "market_cap",
    "float_market_cap",
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "deducted_profit_growth_yoy",
    "debt_to_asset",
    "operating_cash_flow",
    "ocf_to_net_profit",
    "dividend_yield",
]

PERCENT_FIELDS = {
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "deducted_profit_growth_yoy",
    "debt_to_asset",
    "dividend_yield",
}

CORE_AVAILABLE_FIELDS = [
    "pe_ttm",
    "pb",
    "roe",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "debt_to_asset",
]

FIELD_ALIASES = {
    "pe_ttm": ["pe_ttm", "pe", "市盈率", "市盈率-动态", "市盈率ttm", "市盈率TTM"],
    "pb": ["pb", "市净率"],
    "ps_ttm": ["ps_ttm", "ps", "市销率", "市销率ttm", "市销率TTM"],
    "market_cap": ["market_cap", "total_market_cap", "总市值"],
    "float_market_cap": ["float_market_cap", "circulating_market_cap", "流通市值"],
    "roe": ["roe", "净资产收益率"],
    "roa": ["roa", "总资产收益率"],
    "gross_margin": ["gross_margin", "毛利率"],
    "net_margin": ["net_margin", "净利率"],
    "revenue_growth_yoy": ["revenue_growth_yoy", "revenue_growth", "营收同比", "营业收入同比增长"],
    "net_profit_growth_yoy": ["net_profit_growth_yoy", "net_profit_growth", "profit_growth", "净利润同比"],
    "deducted_profit_growth_yoy": ["deducted_profit_growth_yoy", "deducted_profit_growth", "扣非净利润同比"],
    "debt_to_asset": ["debt_to_asset", "debt_ratio", "资产负债率"],
    "operating_cash_flow": ["operating_cash_flow", "operating_cashflow", "经营现金流"],
    "ocf_to_net_profit": ["ocf_to_net_profit", "经营现金流净利润比"],
    "dividend_yield": ["dividend_yield", "股息率"],
}

BOOLEAN_FIELDS = {"fundamental_available"}


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


def _normalize_number(field: str, value: Any) -> float | None:
    number = _to_number(value)
    if number is None:
        return None
    if field in PERCENT_FIELDS and abs(number) <= 1:
        number *= 100
    return round(number, 4)


def _clip_score(value: float) -> float:
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


def _first_existing(row: dict[str, Any], field: str) -> Any:
    for name in FIELD_ALIASES[field]:
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


def _prepare_fundamental_map(fundamental_df: pd.DataFrame | None) -> dict[str, dict[str, Any]]:
    if fundamental_df is None or fundamental_df.empty or "ticker" not in fundamental_df.columns:
        return {}
    frame = fundamental_df.copy(deep=True)
    frame["_fundamental_ticker"] = frame["ticker"].map(_normalize_ticker)
    frame = frame.drop_duplicates(subset=["_fundamental_ticker"], keep="first")
    return {
        str(row["_fundamental_ticker"]): row.drop(labels=["_fundamental_ticker"]).to_dict()
        for _, row in frame.iterrows()
        if row.get("_fundamental_ticker")
    }


def _band_score(value: float | None, bands: list[tuple[float, float]], *, higher_is_better: bool = False) -> float | None:
    if value is None:
        return None
    if higher_is_better:
        for threshold, score in bands:
            if value > threshold:
                return score
        return bands[-1][1]
    for threshold, score in bands:
        if value <= threshold:
            return score
    return bands[-1][1]


def _score_valuation(values: dict[str, float | None], warnings: list[str], strengths: list[str], risks: list[str]) -> float:
    pe_score = _band_score(values.get("pe_ttm"), [(0, 0), (15, 95), (25, 80), (40, 60), (float("inf"), 30)])
    pb_score = _band_score(values.get("pb"), [(0, 0), (1.5, 95), (3, 80), (6, 60), (float("inf"), 30)])
    if pe_score in (None, 0):
        warnings.append("PE TTM 不可用")
        pe_score = None
    if pb_score in (None, 0):
        warnings.append("PB 不可用")
        pb_score = None
    valid = [score for score in [pe_score, pb_score] if score is not None]
    if not valid:
        return 50.0
    score = _clip_score(sum(valid) / len(valid))
    if score >= 80:
        strengths.append("估值指标处于较优区间")
    elif score <= 40:
        risks.append("估值指标偏高或不可比")
    return score


def _score_profitability(values: dict[str, float | None], warnings: list[str], strengths: list[str]) -> float:
    roe = values.get("roe")
    roa = values.get("roa")
    roe_score = _band_score(roe, [(20, 95), (15, 80), (10, 60), (5, 40), (-float("inf"), 20)], higher_is_better=True)
    if roe_score is None:
        warnings.append("ROE 不可用")
        roe_score = 50.0
    roa_score = None
    if roa is not None:
        roa_score = _band_score(roa, [(8, 90), (5, 75), (3, 60), (0, 40), (-float("inf"), 20)], higher_is_better=True)
    score = _clip_score(0.75 * roe_score + 0.25 * (roa_score if roa_score is not None else roe_score))
    if score >= 80:
        strengths.append("盈利能力指标较强")
    return score


def _score_growth(values: dict[str, float | None], warnings: list[str], strengths: list[str], risks: list[str]) -> float:
    profit = values.get("net_profit_growth_yoy")
    revenue = values.get("revenue_growth_yoy")
    profit_score = _band_score(profit, [(30, 95), (20, 80), (10, 60), (0, 40), (-float("inf"), 20)], higher_is_better=True)
    if profit_score is None:
        warnings.append("净利润增速不可用")
        profit_score = 50.0
    revenue_score = None
    if revenue is not None:
        revenue_score = _band_score(revenue, [(30, 90), (20, 75), (10, 60), (0, 40), (-float("inf"), 20)], higher_is_better=True)
    else:
        warnings.append("营收增速不可用")
    score = _clip_score(0.7 * profit_score + 0.3 * (revenue_score if revenue_score is not None else profit_score))
    if score >= 80:
        strengths.append("成长指标较强")
    elif score <= 30:
        risks.append("成长指标偏弱")
    return score


def _score_quality(values: dict[str, float | None], warnings: list[str], strengths: list[str], risks: list[str]) -> float:
    debt = values.get("debt_to_asset")
    ocf_ratio = values.get("ocf_to_net_profit")
    debt_score = _band_score(debt, [(40, 90), (60, 75), (80, 50), (float("inf"), 20)])
    if debt_score is None:
        warnings.append("资产负债率不可用")
        debt_score = 50.0
    if debt is not None and debt > 80:
        risks.append("资产负债率较高")
    score = debt_score
    if ocf_ratio is None:
        warnings.append("经营现金流质量不可用")
    elif ocf_ratio > 1:
        score += 10
        strengths.append("经营现金流质量较好")
    elif ocf_ratio < 0.8:
        score -= 15
        risks.append("经营现金流质量偏弱")
    return _clip_score(score)


def _source_row_for(base_row: dict[str, Any], fundamental_map: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], str]:
    ticker = _normalize_ticker(base_row.get("ticker", base_row.get("symbol", "")))
    provided = fundamental_map.get(ticker)
    if provided:
        merged = dict(base_row)
        merged.update({key: value for key, value in provided.items() if key != "ticker"})
        source = str(provided.get("fundamental_data_source") or "Provided Fundamental")
        return merged, source
    return base_row, str(base_row.get("fundamental_data_source") or "Existing Fields")


def _build_row(row: pd.Series, fundamental_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    raw, data_source = _source_row_for(row.to_dict(), fundamental_map)
    values = {field: _normalize_number(field, _first_existing(raw, field)) for field in NUMERIC_FIELDS}
    available_count = sum(1 for field in CORE_AVAILABLE_FIELDS if values.get(field) is not None)
    fundamental_available = available_count >= 1
    warnings: list[str] = []
    strengths: list[str] = []
    risks: list[str] = []

    valuation = _score_valuation(values, warnings, strengths, risks)
    profitability = _score_profitability(values, warnings, strengths)
    growth = _score_growth(values, warnings, strengths, risks)
    quality = _score_quality(values, warnings, strengths, risks)

    data_warning = str(raw.get("fundamental_data_warning") or "").strip()
    if data_warning:
        warnings.append(data_warning)
    updated_at = raw.get("fundamental_updated_at")

    if not fundamental_available:
        score = 50.0
        warnings.append("基本面数据不可用，使用中性分")
        summary = "基本面数据不可用，当前仅保留中性研究分。"
        reason = "财务数据缺失，保留中性基本面研究分。"
        status = "Unavailable"
        data_source = "Unavailable"
        strengths = []
        risks = []
    else:
        score = _clip_score(0.25 * valuation + 0.25 * profitability + 0.25 * growth + 0.25 * quality)
        summary = f"估值 {valuation} / 盈利 {profitability} / 成长 {growth} / 财务质量 {quality}"
        reason_parts: list[str] = []
        if values.get("roe") is not None:
            reason_parts.append("ROE已接入")
            if values["roe"] >= 15:
                reason_parts.append("ROE较高")
        if values.get("net_profit_growth_yoy") is not None:
            reason_parts.append("净利润增长已接入")
            if values["net_profit_growth_yoy"] >= 20:
                reason_parts.append("净利润增长优秀")
        if values.get("revenue_growth_yoy") is not None:
            reason_parts.append("营收增长已接入")
        if values.get("pe_ttm") is not None or values.get("pb") is not None:
            reason_parts.append("估值数据已接入")
        if values.get("pe_ttm") is not None and values["pe_ttm"] > 40:
            reason_parts.append("估值偏高")
        if values.get("debt_to_asset") is not None:
            reason_parts.append("资产负债率已接入")
        missing = [field for field in CORE_AVAILABLE_FIELDS if values.get(field) is None]
        if missing:
            reason_parts.append("部分财务数据缺失")
        reason = "；".join(dict.fromkeys(reason_parts)) or "基本面字段有限，部分维度保留中性分。"
        status = "Available"

    output: dict[str, Any] = {
        "fundamental_available": bool(fundamental_available),
        "fundamental_data_source": data_source,
        "fundamental_data_status": status,
        "fundamental_data_warning": data_warning,
        "fundamental_updated_at": updated_at,
        "valuation_score": valuation,
        "profitability_score": profitability,
        "growth_score": growth,
        "financial_quality_score": quality,
        "fundamental_research_score": score,
        "fundamental_reason": reason,
        "fundamental_summary": summary,
        "fundamental_strengths": list(dict.fromkeys(strengths)),
        "fundamental_risks": list(dict.fromkeys(risks)),
        "fundamental_warnings": list(dict.fromkeys(warnings)),
    }
    output.update(values)
    return output


def build_fundamental_research(df: pd.DataFrame | None, fundamental_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Append fundamental research fields without mutating caller inputs."""
    if df is None:
        result = pd.DataFrame()
    elif isinstance(df, pd.DataFrame):
        result = df.copy(deep=True)
    else:
        result = pd.DataFrame(df).copy(deep=True)

    if result.empty:
        for field in FUNDAMENTAL_RESEARCH_FIELDS:
            result[field] = pd.Series(dtype="object")
        return result

    attrs = dict(getattr(df, "attrs", {}))
    fundamental_map = _prepare_fundamental_map(fundamental_df)
    output = pd.DataFrame([_build_row(result.loc[index], fundamental_map) for index in result.index], index=result.index)
    for field in FUNDAMENTAL_RESEARCH_FIELDS:
        result[field] = output[field].astype(object) if field in BOOLEAN_FIELDS else output[field]
    result.attrs.update(attrs)
    return result


__all__ = [
    "FUNDAMENTAL_RESEARCH_FIELDS",
    "build_fundamental_research",
]
