"""Additive industry and concept research scoring."""

from __future__ import annotations

from typing import Any

import pandas as pd


INDUSTRY_RESEARCH_FIELDS = [
    "industry_score",
    "industry_heat_score",
    "industry_rank_percentile",
    "concept_coverage_count",
    "industry_reason",
]


HOT_CONCEPTS = ["AI", "算力", "军工", "国产替代", "半导体", "机器人", "低空经济", "新能源", "数据中心"]


def _copy(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    return df.copy(deep=True) if isinstance(df, pd.DataFrame) else pd.DataFrame(df).copy(deep=True)


def _num(value: Any, index: pd.Index) -> pd.Series:
    if isinstance(value, pd.Series):
        return pd.to_numeric(value, errors="coerce")
    return pd.Series([None] * len(index), index=index, dtype="float64")


def _concepts(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        pass
    text = str(value).replace(";", ",").replace("|", ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def _reason(row: pd.Series, score: float, percentile: float, concept_count: int) -> str:
    parts: list[str] = []
    industry = str(row.get("industry") or "").strip()
    if percentile <= 10:
        parts.append(f"{industry or 'Industry'} heat ranks in top 10%.")
    elif percentile <= 30:
        parts.append(f"{industry or 'Industry'} heat ranks in top 30%.")
    else:
        parts.append(f"{industry or 'Industry'} heat is neutral.")
    if concept_count:
        parts.append(f"Concept coverage {concept_count} item(s).")
    if score >= 70:
        parts.append("Industry strength is constructive.")
    elif score <= 40:
        parts.append("Industry strength is weak or needs review.")
    return " ".join(parts)


def build_industry_research(df: pd.DataFrame | None) -> pd.DataFrame:
    """Append industry research fields from existing industry/concept columns."""
    result = _copy(df)
    if result.empty:
        for field in INDUSTRY_RESEARCH_FIELDS:
            result[field] = pd.Series(dtype="object")
        return result

    strength = _num(result.get("industry_strength_score"), result.index).fillna(50).clip(lower=0, upper=100)
    heat = _num(result.get("concept_heat_score"), result.index).fillna(50).clip(lower=0, upper=100)
    concept_counts = result.get("concepts", pd.Series([""] * len(result), index=result.index)).map(_concepts).map(len)
    hot_counts = result.get("concepts", pd.Series([""] * len(result), index=result.index)).map(
        lambda value: sum(1 for concept in _concepts(value) if any(keyword.lower() in concept.lower() for keyword in HOT_CONCEPTS))
    )
    concept_bonus = (concept_counts.clip(upper=5) * 2.0) + (hot_counts.clip(upper=3) * 3.0)
    industry_score = (strength * 0.70 + heat * 0.20 + concept_bonus).clip(lower=0, upper=100).round(2)
    percentile = industry_score.rank(pct=True, ascending=False, method="min").mul(100).round(2)

    result["industry_heat_score"] = heat.round(2)
    result["industry_rank_percentile"] = percentile
    result["concept_coverage_count"] = concept_counts.astype(int)
    result["industry_score"] = industry_score
    result["industry_reason"] = [
        _reason(result.loc[index], float(industry_score.loc[index]), float(percentile.loc[index]), int(concept_counts.loc[index]))
        for index in result.index
    ]
    return result


__all__ = ["INDUSTRY_RESEARCH_FIELDS", "build_industry_research"]
