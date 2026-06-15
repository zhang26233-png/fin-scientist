"""Additive fundamental research fields for A-share research rows."""

from __future__ import annotations

from typing import Any

import pandas as pd


FUNDAMENTAL_RESEARCH_FIELDS = [
    "fundamental_available",
    "fundamental_data_source",
    "fundamental_data_status",
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

FIELD_ALIASES = {
    "pe_ttm": ["pe_ttm", "pe", "市盈率", "市盈率-动态", "市盈率ttm"],
    "pb": ["pb", "市净率"],
    "ps_ttm": ["ps_ttm", "ps", "市销率", "市销率ttm"],
    "market_cap": ["market_cap", "total_market_cap", "总市值"],
    "float_market_cap": ["float_market_cap", "circulating_market_cap", "流通市值"],
    "roe": ["roe", "净资产收益率"],
    "roa": ["roa", "总资产收益率"],
    "gross_margin": ["gross_margin", "毛利率"],
    "net_margin": ["net_margin", "净利率"],
    "revenue_growth_yoy": ["revenue_growth_yoy", "revenue_growth", "营收同比", "营业收入同比增长"],
    "net_profit_growth_yoy": ["net_profit_growth_yoy", "profit_growth", "net_profit_growth", "净利润同比"],
    "deducted_profit_growth_yoy": ["deducted_profit_growth_yoy", "扣非净利润同比", "deducted_profit_growth"],
    "debt_to_asset": ["debt_to_asset", "debt_ratio", "资产负债率"],
    "operating_cash_flow": ["operating_cash_flow", "operating_cashflow", "经营现金流"],
    "ocf_to_net_profit": ["ocf_to_net_profit", "经营现金流净利润比"],
    "dividend_yield": ["dividend_yield", "股息率"],
}


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
        if name in row:
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


def _prepare_fundamental_df(fundamental_df: pd.DataFrame | None) -> pd.DataFrame:
    if fundamental_df is None or fundamental_df.empty:
        return pd.DataFrame()
    frame = fundamental_df.copy(deep=True)
    if "ticker" not in frame.columns:
        return pd.DataFrame()
    frame["_fundamental_ticker"] = frame["ticker"].map(_normalize_ticker)
    frame = frame.drop_duplicates(subset=["_fundamental_ticker"], keep="first")
    return frame


def _merge_source(df: pd.DataFrame, fundamental_df: pd.DataFrame | None) -> pd.DataFrame:
    result = df.copy(deep=True)
    prepared = _prepare_fundamental_df(fundamental_df)
    if prepared.empty or "ticker" not in result.columns:
        return result
    result["_fundamental_ticker"] = result["ticker"].map(_normalize_ticker)
    merged = result.merge(prepared, on="_fundamental_ticker", how="left", suffixes=("", "_fundamental"))
    return merged.drop(columns=["_fundamental_ticker"], errors="ignore")


def _score_valuation(values: dict[str, float | None], warnings: list[str], strengths: list[str], risks: list[str]) -> float:
    score = 50.0
    pe = values.get("pe_ttm")
    if pe is None or pe <= 0:
        warnings.append("PE TTM 不可用")
    elif pe <= 15:
        score += 20
        strengths.append("估值水平偏低")
    elif pe <= 30:
        score += 10
    elif pe > 60:
        score -= 15
        risks.append("PE估值偏高")

    pb = values.get("pb")
    if pb is None or pb <= 0:
        warnings.append("PB 不可用")
    elif pb <= 2:
        score += 15
        strengths.append("PB估值较低")
    elif pb <= 5:
        score += 5
    elif pb > 5:
        score -= 10
        risks.append("PB估值偏高")

    ps = values.get("ps_ttm")
    if ps is not None:
        if 0 < ps <= 3:
            score += 10
        elif ps > 8:
            score -= 10
            risks.append("PS估值偏高")
    return _clip_score(score)


def _score_profitability(values: dict[str, float | None], warnings: list[str], strengths: list[str]) -> float:
    score = 50.0
    roe = values.get("roe")
    if roe is None:
        warnings.append("ROE 不可用")
    elif roe >= 20:
        score += 25
        strengths.append("ROE较高")
    elif roe >= 10:
        score += 15
    elif roe >= 5:
        score += 5
    else:
        score -= 10

    roa = values.get("roa")
    if roa is not None:
        if roa >= 8:
            score += 10
        elif roa >= 3:
            score += 5
        else:
            score -= 5

    gross = values.get("gross_margin")
    if gross is not None:
        if gross >= 40:
            score += 10
            strengths.append("毛利率较高")
        elif gross >= 20:
            score += 5
        else:
            score -= 5

    net = values.get("net_margin")
    if net is not None:
        if net >= 15:
            score += 10
        elif net >= 5:
            score += 5
        else:
            score -= 5
    return _clip_score(score)


def _score_growth(values: dict[str, float | None], warnings: list[str], strengths: list[str], risks: list[str]) -> float:
    score = 50.0
    revenue = values.get("revenue_growth_yoy")
    if revenue is None:
        warnings.append("营收增速不可用")
    elif revenue >= 30:
        score += 20
        strengths.append("营收增长较快")
    elif revenue >= 10:
        score += 10
    elif revenue >= 0:
        score += 5
    else:
        score -= 10
        risks.append("营收同比下滑")

    profit = values.get("net_profit_growth_yoy")
    if profit is None:
        warnings.append("净利润增速不可用")
    elif profit >= 30:
        score += 20
        strengths.append("净利润增长较快")
    elif profit >= 10:
        score += 10
    elif profit >= 0:
        score += 5
    else:
        score -= 15
        risks.append("净利润同比下滑")

    deducted = values.get("deducted_profit_growth_yoy")
    if deducted is not None:
        if deducted >= 20:
            score += 10
        elif deducted >= 0:
            score += 5
        else:
            score -= 10
            risks.append("扣非净利润同比下滑")
    return _clip_score(score)


def _score_quality(values: dict[str, float | None], warnings: list[str], strengths: list[str], risks: list[str]) -> float:
    score = 50.0
    debt = values.get("debt_to_asset")
    if debt is None:
        warnings.append("资产负债率不可用")
    elif debt <= 40:
        score += 15
        strengths.append("资产负债率较低")
    elif debt <= 60:
        score += 5
    elif debt <= 75:
        score -= 5
    else:
        score -= 15
        risks.append("资产负债率较高")

    ocf_ratio = values.get("ocf_to_net_profit")
    if ocf_ratio is None:
        warnings.append("经营现金流质量不可用")
    elif ocf_ratio >= 1:
        score += 20
        strengths.append("经营现金流质量较好")
    elif ocf_ratio >= 0.5:
        score += 10
    elif ocf_ratio >= 0:
        score -= 5
    else:
        score -= 15
        risks.append("经营现金流质量偏弱")

    dividend = values.get("dividend_yield")
    if dividend is not None:
        if dividend >= 3:
            score += 10
        elif dividend >= 1:
            score += 5
    return _clip_score(score)


def _build_row(row: pd.Series, has_input_df: bool) -> dict[str, Any]:
    raw = row.to_dict()
    values = {field: _normalize_number(field, _first_existing(raw, field)) for field in NUMERIC_FIELDS}
    available_count = sum(1 for value in values.values() if value is not None)
    fundamental_available = available_count >= 3
    warnings: list[str] = []
    strengths: list[str] = []
    risks: list[str] = []

    valuation = _score_valuation(values, warnings, strengths, risks)
    profitability = _score_profitability(values, warnings, strengths)
    growth = _score_growth(values, warnings, strengths, risks)
    quality = _score_quality(values, warnings, strengths, risks)

    if not fundamental_available:
        score = 50.0
        warnings.append("基本面数据不可用，使用中性分")
        summary = "基本面数据不可用，当前仅保留中性研究分。"
        status = "Unavailable"
    else:
        score = _clip_score((0.25 * valuation) + (0.25 * profitability) + (0.25 * growth) + (0.25 * quality))
        summary = f"估值 {valuation} / 盈利 {profitability} / 成长 {growth} / 财务质量 {quality}"
        status = "Available"

    data_source = "Provided Fundamental" if has_input_df else "Existing Fields"
    output: dict[str, Any] = {
        "fundamental_available": bool(fundamental_available),
        "fundamental_data_source": data_source if fundamental_available else "Unavailable",
        "fundamental_data_status": status,
        "valuation_score": valuation,
        "profitability_score": profitability,
        "growth_score": growth,
        "financial_quality_score": quality,
        "fundamental_research_score": score,
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
    merged = _merge_source(result, fundamental_df)
    has_input_df = fundamental_df is not None and not fundamental_df.empty
    output = pd.DataFrame([_build_row(merged.loc[index], has_input_df) for index in merged.index], index=result.index)
    for field in FUNDAMENTAL_RESEARCH_FIELDS:
        result[field] = output[field].astype(object) if field == "fundamental_available" else output[field]
    result.attrs.update(attrs)
    return result


__all__ = [
    "FUNDAMENTAL_RESEARCH_FIELDS",
    "build_fundamental_research",
]
