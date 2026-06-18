"""Unified research ranking score for final Scheduler ordering."""

from __future__ import annotations

from typing import Any

import pandas as pd


UNIFIED_RESEARCH_FIELDS = [
    "unified_research_score",
    "technical_contribution",
    "capital_contribution",
    "fundamental_contribution",
    "industry_contribution",
    "news_contribution",
]


def _copy(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    return df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame(df).copy(deep=True)


def _num(value: Any, index: pd.Index) -> pd.Series:
    if isinstance(value, pd.Series):
        return pd.to_numeric(value, errors="coerce")
    return pd.Series([None] * len(index), index=index, dtype="float64")


def _score(source: pd.DataFrame, field: str) -> pd.Series:
    return _num(source.get(field), source.index).fillna(50).clip(lower=0, upper=100)


def build_unified_research_score(df: pd.DataFrame | None) -> pd.DataFrame:
    """Append unified research score fields without mutating caller input."""
    result = _copy(df)
    if result.empty:
        for field in UNIFIED_RESEARCH_FIELDS:
            result[field] = pd.Series(dtype="float64")
        return result

    technical = _score(result, "real_technical_score")
    capital = _score(result, "capital_flow_score")
    fundamental = _score(result, "fundamental_research_score")
    industry = _score(result, "industry_score")
    if "industry_score" not in result.columns:
        industry_strength = _score(result, "industry_strength_score")
        concept_heat = _score(result, "concept_heat_score")
        industry = ((industry_strength * 0.70) + (concept_heat * 0.30)).clip(lower=0, upper=100)
    news = _score(result, "news_event_score")

    result["technical_contribution"] = (technical * 0.30).round(4)
    result["capital_contribution"] = (capital * 0.25).round(4)
    result["fundamental_contribution"] = (fundamental * 0.20).round(4)
    result["industry_contribution"] = (industry * 0.15).round(4)
    result["news_contribution"] = (news * 0.10).round(4)
    result["unified_research_score"] = (
        result["technical_contribution"]
        + result["capital_contribution"]
        + result["fundamental_contribution"]
        + result["industry_contribution"]
        + result["news_contribution"]
    ).round(2)
    return result


__all__ = ["UNIFIED_RESEARCH_FIELDS", "build_unified_research_score"]
