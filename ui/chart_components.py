"""Safe chart data helpers for the read-only Chart Center."""

from __future__ import annotations

from typing import Any

import pandas as pd


SCORE_PROFILE_FIELDS = [
    "fundamental_score",
    "technical_score",
    "composite_score",
    "selection_score",
    "risk_score",
]

RETURN_RISK_FIELDS = [
    "ticker",
    "name",
    "volatility",
    "risk_score",
    "period_return",
    "annualized_return",
]

DRAWDOWN_RISK_FIELDS = [
    "ticker",
    "name",
    "max_drawdown",
    "volatility",
    "risk_level",
]

RANKING_FIELDS = [
    "ticker",
    "name",
    "selection_score",
]


def safe_numeric(value: Any) -> float | None:
    """Convert values to float when possible."""
    if value is None:
        return None
    try:
        converted = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    except (TypeError, ValueError):
        return None
    if pd.isna(converted):
        return None
    return float(converted)


def safe_chart_df(df: Any, required_fields: list[str]) -> pd.DataFrame:
    """Return a defensive DataFrame copy containing available required fields."""
    if df is None:
        return pd.DataFrame(columns=required_fields)
    if isinstance(df, pd.DataFrame):
        source = df.copy(deep=True)
    elif isinstance(df, list):
        source = pd.DataFrame(df).copy(deep=True)
    elif isinstance(df, dict):
        source = pd.DataFrame([df]).copy(deep=True)
    else:
        source = pd.DataFrame()
    available = [field for field in required_fields if field in source.columns]
    if source.empty:
        return pd.DataFrame(columns=available)
    return source[available].copy(deep=True)


def build_score_profile_data(row: pd.Series | dict[str, Any] | None) -> pd.DataFrame:
    """Build single-row score profile data."""
    source = pd.Series(row).copy(deep=True) if row is not None else pd.Series(dtype=object)
    rows = []
    for field in SCORE_PROFILE_FIELDS:
        rows.append({"score_field": field, "score_value": safe_numeric(source.get(field))})
    return pd.DataFrame(rows)


def build_score_breakdown_data(row: pd.Series | dict[str, Any] | None) -> pd.DataFrame:
    """Build score breakdown bar data."""
    return build_score_profile_data(row)


def build_return_risk_scatter_data(df: Any) -> pd.DataFrame:
    """Build return-risk scatter data with automatic axis fallback."""
    source = safe_chart_df(df, RETURN_RISK_FIELDS)
    if source.empty:
        return pd.DataFrame(columns=["label", "x_risk", "y_return"])
    output = pd.DataFrame(index=source.index)
    output["label"] = source.get("ticker", source.get("name", pd.Series([""] * len(source), index=source.index))).astype(str)
    output["x_risk"] = source["volatility"].map(safe_numeric) if "volatility" in source.columns else None
    if "risk_score" in source.columns:
        fallback = source["risk_score"].map(safe_numeric)
        output["x_risk"] = output["x_risk"].where(output["x_risk"].notna(), fallback)
    output["y_return"] = source["period_return"].map(safe_numeric) if "period_return" in source.columns else None
    if "annualized_return" in source.columns:
        fallback = source["annualized_return"].map(safe_numeric)
        output["y_return"] = output["y_return"].where(output["y_return"].notna(), fallback)
    return output.dropna(subset=["x_risk", "y_return"], how="any").copy(deep=True)


def build_drawdown_risk_data(df: Any) -> pd.DataFrame:
    """Build drawdown-risk display data."""
    source = safe_chart_df(df, DRAWDOWN_RISK_FIELDS)
    if source.empty:
        return source
    display = source.copy(deep=True)
    for field in ["max_drawdown", "volatility"]:
        if field in display.columns:
            display[field] = display[field].map(safe_numeric)
    return display


def build_candidate_ranking_data(df: Any, top_n: int = 10) -> pd.DataFrame:
    """Build Top N selection_score ranking data without mutating input order."""
    source = safe_chart_df(df, RANKING_FIELDS)
    if source.empty or "selection_score" not in source.columns:
        return pd.DataFrame(columns=["label", "selection_score"])
    display = source.copy(deep=True)
    display["selection_score"] = display["selection_score"].map(safe_numeric)
    label_source = display["ticker"] if "ticker" in display.columns else display.get("name", pd.Series([""] * len(display)))
    display["label"] = label_source.astype(str)
    display = display.dropna(subset=["selection_score"]).sort_values("selection_score", ascending=False, kind="stable")
    return display[["label", "selection_score"]].head(top_n).copy(deep=True)


def build_quality_distribution_data(df: Any) -> dict[str, pd.DataFrame]:
    """Build distribution tables for bucket and level fields."""
    source = safe_chart_df(df, ["selection_bucket", "risk_level"])
    result: dict[str, pd.DataFrame] = {}
    if source.empty:
        return {
            "selection_bucket": pd.DataFrame(columns=["label", "count"]),
            "risk_level": pd.DataFrame(columns=["label", "count"]),
        }
    for field in ["selection_bucket", "risk_level"]:
        if field not in source.columns:
            result[field] = pd.DataFrame(columns=["label", "count"])
            continue
        counts = source[field].fillna("Unavailable").replace("", "Unavailable").value_counts().reset_index()
        counts.columns = ["label", "count"]
        result[field] = counts
    return result


__all__ = [
    "DRAWDOWN_RISK_FIELDS",
    "RANKING_FIELDS",
    "RETURN_RISK_FIELDS",
    "SCORE_PROFILE_FIELDS",
    "build_candidate_ranking_data",
    "build_drawdown_risk_data",
    "build_quality_distribution_data",
    "build_return_risk_scatter_data",
    "build_score_breakdown_data",
    "build_score_profile_data",
    "safe_chart_df",
    "safe_numeric",
]
