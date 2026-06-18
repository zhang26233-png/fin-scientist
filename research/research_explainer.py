"""Human-readable explanations for unified research ranking."""

from __future__ import annotations

from typing import Any

import pandas as pd


RESEARCH_EXPLAINER_FIELDS = [
    "research_summary",
    "technical_research_explanation",
    "capital_research_explanation",
    "fundamental_research_explanation",
    "news_research_explanation",
    "industry_research_explanation",
]


def _copy(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    return df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame(df).copy(deep=True)


def _num(value: Any, default: float = 50.0) -> float:
    try:
        number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    except (TypeError, ValueError):
        return default
    if pd.isna(number):
        return default
    return float(number)


def _text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, list):
        return "; ".join(str(item) for item in value if str(item).strip())
    return str(value).strip()


def _level(score: float) -> str:
    if score >= 75:
        return "strong"
    if score >= 60:
        return "constructive"
    if score >= 45:
        return "neutral"
    return "weak"


def _row_summary(row: pd.Series) -> dict[str, str]:
    unified = _num(row.get("unified_research_score"))
    technical = _num(row.get("real_technical_score"))
    capital = _num(row.get("capital_flow_score"))
    fundamental = _num(row.get("fundamental_research_score"))
    news = _num(row.get("news_event_score"))
    industry = _num(row.get("industry_score"), _num(row.get("industry_strength_score")))
    technical_detail = _text(row.get("technical_signal_summary")) or "technical indicators are included in unified ranking."
    capital_detail = _text(row.get("capital_flow_summary")) or "capital flow score is included in unified ranking."
    fundamental_detail = _text(row.get("fundamental_reason")) or _text(row.get("fundamental_summary")) or "fundamental data is neutral or limited."
    news_detail = _text(row.get("news_reason")) or _text(row.get("news_summary")) or "news/event context is neutral or limited."
    industry_detail = _text(row.get("industry_reason")) or "industry and concept context is included in unified ranking."
    return {
        "technical_research_explanation": f"Technical score {technical:.2f} is {_level(technical)}; {technical_detail}",
        "capital_research_explanation": f"Capital flow score {capital:.2f} is {_level(capital)}; {capital_detail}",
        "fundamental_research_explanation": f"Fundamental score {fundamental:.2f} is {_level(fundamental)}; {fundamental_detail}",
        "news_research_explanation": f"News score {news:.2f} is {_level(news)}; {news_detail}",
        "industry_research_explanation": f"Industry score {industry:.2f} is {_level(industry)}; {industry_detail}",
        "research_summary": (
            f"Unified research score {unified:.2f}. "
            f"Technical {technical:.2f}; capital {capital:.2f}; fundamental {fundamental:.2f}; "
            f"news {news:.2f}; industry {industry:.2f}. "
            "Only for learning and research; not investment advice."
        ),
    }


def build_research_explanation(df: pd.DataFrame | None) -> pd.DataFrame:
    """Append research explanation fields without mutating caller input."""
    result = _copy(df)
    if result.empty:
        for field in RESEARCH_EXPLAINER_FIELDS:
            result[field] = pd.Series(dtype="object")
        return result
    output = pd.DataFrame([_row_summary(result.loc[index]) for index in result.index], index=result.index)
    for field in RESEARCH_EXPLAINER_FIELDS:
        result[field] = output[field]
    return result


__all__ = ["RESEARCH_EXPLAINER_FIELDS", "build_research_explanation"]
