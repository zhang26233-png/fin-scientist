"""Activate research scores from realtime quote fields.

This layer is intentionally additive. It does not overwrite existing scoring
fields and does not produce trading instructions.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


ACTIVATED_RESEARCH_FIELDS = [
    "quote_available",
    "quote_quality_score",
    "liquidity_score",
    "momentum_score",
    "price_position_score",
    "activated_technical_score",
    "activated_fundamental_score",
    "activated_capital_flow_score",
    "activated_news_score",
    "activated_industry_score",
    "activated_composite_score",
    "activated_selection_score",
    "scheduler_ready_score",
    "activated_research_level",
    "activated_research_bucket",
    "activated_research_status",
    "activated_research_reasons",
    "activated_research_warnings",
]


def _to_number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value).strip().replace(",", "")
        if not text or text in {"-", "--", "None", "nan"}:
            return None
        try:
            number = float(text)
        except ValueError:
            return None
    if pd.isna(number):
        return None
    return number


def _is_valid_number(value: Any) -> bool:
    return _to_number(value) is not None


def _clip_score(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 2)


def _quote_available(row: pd.Series) -> bool:
    fields = ["latest_price", "pct_change", "volume", "turnover"]
    return sum(1 for field in fields if _is_valid_number(row.get(field))) >= 2


def _quote_quality_score(row: pd.Series) -> int:
    score = 0
    if _is_valid_number(row.get("latest_price")):
        score += 20
    if _is_valid_number(row.get("pct_change")):
        score += 20
    if _is_valid_number(row.get("volume")):
        score += 20
    if _is_valid_number(row.get("turnover")):
        score += 20
    ohlc_fields = ["open", "high", "low", "prev_close"]
    if sum(1 for field in ohlc_fields if _is_valid_number(row.get(field))) >= 2:
        score += 20
    return score


def _liquidity_score(row: pd.Series) -> int:
    turnover = _to_number(row.get("turnover"))
    if turnover is not None:
        # Tencent quote payloads commonly expose amount in ten-thousand-yuan
        # units. Keep the source column unchanged and normalize only for score
        # activation so the documented yuan thresholds remain meaningful.
        if 0 < turnover < 10_000_000:
            turnover = turnover * 10_000
        if turnover >= 1_000_000_000:
            return 100
        if turnover >= 500_000_000:
            return 85
        if turnover >= 100_000_000:
            return 70
        if turnover >= 50_000_000:
            return 55
        if turnover > 0:
            return 40
        return 30

    volume = _to_number(row.get("volume"))
    if volume is None:
        return 30
    if volume >= 100_000_000:
        return 85
    if volume >= 50_000_000:
        return 70
    if volume >= 10_000_000:
        return 55
    if volume > 0:
        return 40
    return 30


def _momentum_score(row: pd.Series, warnings: list[str]) -> int:
    pct_change = _to_number(row.get("pct_change"))
    if pct_change is None:
        return 50
    if -3 <= pct_change <= 6:
        return 80
    if 6 < pct_change <= 9.8:
        return 70
    if pct_change > 9.8:
        warnings.append("涨幅过高，可能存在追高风险")
        return 60
    if -6 <= pct_change < -3:
        return 45
    warnings.append("跌幅较大，短期波动风险较高")
    return 30


def _price_position_score(row: pd.Series, warnings: list[str]) -> int:
    latest_price = _to_number(row.get("latest_price"))
    high = _to_number(row.get("high"))
    low = _to_number(row.get("low"))
    open_price = _to_number(row.get("open"))
    if latest_price is None or high is None or low is None or open_price is None:
        warnings.append("日内价格位置字段不足")
        return 50
    if high == low:
        warnings.append("日内最高价与最低价相同，价格位置不可判定")
        return 50

    position = (latest_price - low) / (high - low)
    if 0.55 <= position <= 0.85:
        return 80
    if 0.35 <= position < 0.55:
        return 65
    if position > 0.85:
        warnings.append("价格接近日内高位")
        return 60
    return 45


def _existing_positive_score(row: pd.Series, field: str) -> float | None:
    value = _to_number(row.get(field))
    if value is None or value <= 0:
        return None
    return _clip_score(value)


def _score_or_neutral(row: pd.Series, field: str, warnings: list[str]) -> float:
    score = _existing_positive_score(row, field)
    if score is None:
        warnings.append(f"{field} missing; scheduler activation used neutral score 50.")
        return 50.0
    return score


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, tuple) or isinstance(value, set):
        return [str(item) for item in value if item]
    if pd.isna(value):
        return []
    text = str(value).strip()
    return [text] if text else []


def _layer(score: float, quote_available: bool) -> tuple[str, str, str]:
    if not quote_available:
        return "Unavailable", "Unavailable", "Incomplete"
    if score >= 75:
        return "High", "Core", "Selected"
    if score >= 60:
        return "Medium", "Watch", "Watch"
    if score >= 40:
        return "Low", "Watch", "Watch"
    return "Low", "Exclude", "Excluded"


def _activate_row(row: pd.Series) -> dict[str, Any]:
    warnings: list[str] = []
    reasons: list[str] = []
    quote_available = _quote_available(row)
    quote_quality_score = _quote_quality_score(row)
    liquidity_score = _liquidity_score(row)
    momentum_score = _momentum_score(row, warnings)
    price_position_score = _price_position_score(row, warnings)

    real_technical_score = _existing_positive_score(row, "real_technical_score")
    if real_technical_score is not None:
        activated_technical_score = real_technical_score
        reasons.append("真实技术指标已接入")
        warnings.extend(_as_list(row.get("technical_indicator_warnings")))
        warnings.extend(_as_list(row.get("technical_risk_flags")))
    else:
        activated_technical_score = _clip_score(
            (0.4 * liquidity_score) + (0.4 * momentum_score) + (0.2 * price_position_score)
        )
    valuation_score = _existing_positive_score(row, "valuation_score")
    profitability_score = _existing_positive_score(row, "profitability_score")
    growth_score = _existing_positive_score(row, "growth_score")
    financial_quality_score = _existing_positive_score(row, "financial_quality_score")
    if all(score is not None for score in [valuation_score, profitability_score, growth_score, financial_quality_score]):
        activated_fundamental_score = _clip_score(
            (0.30 * valuation_score)
            + (0.30 * profitability_score)
            + (0.25 * growth_score)
            + (0.15 * financial_quality_score)
        )
    else:
        activated_fundamental_score = _existing_positive_score(row, "fundamental_research_score")

    if activated_fundamental_score is None:
        activated_fundamental_score = _score_or_neutral(row, "activated_fundamental_score", warnings)

    activated_capital_flow_score = _score_or_neutral(row, "capital_flow_score", warnings)
    raw_news_score = _existing_positive_score(row, "news_event_score")
    activated_news_score = raw_news_score if raw_news_score is not None else _score_or_neutral(row, "activated_news_score", warnings)
    activated_industry_score = _score_or_neutral(row, "industry_strength_score", warnings)
    if raw_news_score is not None:
        reasons.extend(_as_list(row.get("news_reason")))
        summary = row.get("news_summary")
        if summary is not None and not pd.isna(summary) and str(summary).strip():
            reasons.append(str(summary).strip())
        warnings.extend(_as_list(row.get("news_warning")))

    if activated_fundamental_score is not None:
        technical_component = real_technical_score if real_technical_score is not None else activated_technical_score
        activated_composite_score = _clip_score(
            (0.30 * activated_fundamental_score)
            + (0.30 * technical_component)
            + (0.25 * activated_capital_flow_score)
            + (0.10 * activated_news_score)
            + (0.05 * quote_quality_score)
        )
        if raw_news_score is not None:
            reasons.append("News event fields are included in v6.9.0 activated composite scoring.")
        reasons.append("基本面研究评分已接入")
        warnings.extend(_as_list(row.get("fundamental_warnings")))
        warnings.extend(_as_list(row.get("fundamental_risks")))
    else:
        existing_composite = _existing_positive_score(row, "composite_score")
        if existing_composite is not None:
            activated_composite_score = _clip_score((0.7 * existing_composite) + (0.3 * activated_technical_score))
            reasons.append("Activated composite score blends existing composite_score with realtime technical activation.")
        else:
            activated_composite_score = _clip_score(
                (0.5 * activated_technical_score) + (0.3 * quote_quality_score) + (0.2 * liquidity_score)
            )
            reasons.append("Activated composite score is derived from realtime quote quality, liquidity, and momentum context.")

    activated_selection_score = (
        (0.5 * activated_composite_score)
        + (0.2 * liquidity_score)
        + (0.2 * momentum_score)
        + (0.1 * quote_quality_score)
    )
    risk_score = _to_number(row.get("risk_score"))
    if risk_score is not None:
        if risk_score > 85:
            activated_selection_score -= 20
            warnings.append("risk_score 高于 85，研究评分已扣分")
        elif risk_score > 70:
            activated_selection_score -= 10
            warnings.append("risk_score 高于 70，研究评分已扣分")
    activated_selection_score = _clip_score(activated_selection_score)
    scheduler_ready_score = _clip_score(
        (0.25 * quote_quality_score)
        + (0.25 * liquidity_score)
        + (0.20 * activated_technical_score)
        + (0.15 * activated_fundamental_score)
        + (0.15 * activated_capital_flow_score)
    )

    if not quote_available:
        warnings.append("实时行情字段不足，研究评分激活不完整")
        activated_selection_score = 0.0

    level, bucket, status = _layer(activated_selection_score, quote_available)
    return {
        "quote_available": bool(quote_available),
        "quote_quality_score": quote_quality_score,
        "liquidity_score": liquidity_score,
        "momentum_score": momentum_score,
        "price_position_score": price_position_score,
        "activated_technical_score": activated_technical_score,
        "activated_fundamental_score": activated_fundamental_score,
        "activated_capital_flow_score": activated_capital_flow_score,
        "activated_news_score": activated_news_score,
        "activated_industry_score": activated_industry_score,
        "activated_composite_score": activated_composite_score,
        "activated_selection_score": activated_selection_score,
        "scheduler_ready_score": scheduler_ready_score,
        "activated_research_level": level,
        "activated_research_bucket": bucket,
        "activated_research_status": status,
        "activated_research_reasons": reasons,
        "activated_research_warnings": warnings,
    }


def activate_research_scores(df: pd.DataFrame | None) -> pd.DataFrame:
    """Append activated research score fields without mutating input rows."""
    if df is None:
        result = pd.DataFrame()
    elif isinstance(df, pd.DataFrame):
        result = df.copy(deep=True)
    else:
        result = pd.DataFrame(df).copy(deep=True)

    if result.empty:
        for field in ACTIVATED_RESEARCH_FIELDS:
            result[field] = pd.Series(dtype="object")
        return result

    attrs = dict(getattr(df, "attrs", {}))
    output = pd.DataFrame([_activate_row(result.loc[index]) for index in result.index], index=result.index)
    for field in ACTIVATED_RESEARCH_FIELDS:
        result[field] = output[field].astype(object) if field in {"quote_available"} else output[field]
    result.attrs.update(attrs)
    return result


__all__ = [
    "ACTIVATED_RESEARCH_FIELDS",
    "activate_research_scores",
]
