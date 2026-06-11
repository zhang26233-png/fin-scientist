"""Read-only factor metric helpers for Factor Research Lab."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _copy_frame(df: Any) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    if isinstance(df, pd.DataFrame):
        return df.copy(deep=True)
    if isinstance(df, dict):
        return pd.DataFrame([df]).copy(deep=True)
    if isinstance(df, list):
        return pd.DataFrame(df).copy(deep=True)
    return pd.DataFrame()


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce")


def _valid_pair(df: pd.DataFrame, factor_name: str, return_col: str) -> pd.DataFrame:
    source = _copy_frame(df)
    if source.empty or factor_name not in source.columns or return_col not in source.columns:
        return pd.DataFrame(columns=["factor_value", "return_value"])
    pair = pd.DataFrame(
        {
            "factor_value": _numeric_series(source, factor_name),
            "return_value": _numeric_series(source, return_col),
        }
    ).dropna()
    return pair


def _has_enough_variation(pair: pd.DataFrame) -> bool:
    if len(pair) < 2:
        return False
    return pair["factor_value"].nunique(dropna=True) > 1 and pair["return_value"].nunique(dropna=True) > 1


def calculate_factor_ic(df: Any, factor_name: str, return_col: str) -> float | None:
    """Calculate Pearson IC between a factor and return field."""
    pair = _valid_pair(df, factor_name, return_col)
    if not _has_enough_variation(pair):
        return None
    value = pair["factor_value"].corr(pair["return_value"], method="pearson")
    if pd.isna(value):
        return None
    return float(value)


def calculate_rank_ic(df: Any, factor_name: str, return_col: str) -> float | None:
    """Calculate Spearman Rank IC between a factor and return field."""
    pair = _valid_pair(df, factor_name, return_col)
    if not _has_enough_variation(pair):
        return None
    value = pair["factor_value"].corr(pair["return_value"], method="spearman")
    if pd.isna(value):
        return None
    return float(value)


def calculate_group_returns(
    df: Any,
    factor_name: str,
    return_col: str,
    n_groups: int = 5,
) -> pd.DataFrame:
    """Calculate mean return for factor quantile groups."""
    pair = _valid_pair(df, factor_name, return_col)
    columns = ["factor_group", "factor_group_return"]
    if pair.empty:
        return pd.DataFrame(columns=columns)
    result = pair.copy(deep=True)
    unique_count = int(result["factor_value"].nunique(dropna=True))
    group_count = max(1, min(int(n_groups), unique_count))
    if group_count <= 1:
        result["factor_group"] = "Q1"
    else:
        labels = [f"Q{index}" for index in range(1, group_count + 1)]
        try:
            result["factor_group"] = pd.qcut(
                result["factor_value"],
                q=group_count,
                labels=labels,
                duplicates="drop",
            ).astype(str)
        except ValueError:
            result["factor_group"] = pd.qcut(
                result["factor_value"].rank(method="first"),
                q=group_count,
                labels=labels,
                duplicates="drop",
            ).astype(str)
    grouped = (
        result.groupby("factor_group", sort=True, observed=False)["return_value"]
        .mean()
        .reset_index()
        .rename(columns={"return_value": "factor_group_return"})
    )
    return grouped[columns].copy(deep=True)


def label_factor_effectiveness(ic_value: float | None) -> str:
    """Convert an IC value into a neutral factor effectiveness label."""
    if ic_value is None:
        return "Unavailable"
    try:
        value = float(ic_value)
    except (TypeError, ValueError):
        return "Unavailable"
    if pd.isna(value):
        return "Unavailable"
    if value > 0.05:
        return "Positive"
    if value < -0.05:
        return "Negative"
    return "Weak"


__all__ = [
    "calculate_factor_ic",
    "calculate_group_returns",
    "calculate_rank_ic",
    "label_factor_effectiveness",
]
