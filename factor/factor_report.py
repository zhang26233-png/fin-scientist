"""Neutral factor research report builder."""

from __future__ import annotations

from typing import Any

import pandas as pd

from factor.factor_lab import build_factor_dataset


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


def build_factor_research_report(df: Any, factor_name: str) -> dict[str, Any]:
    """Build a structured read-only factor research report."""
    source = _copy_frame(df)
    factor_dataset = build_factor_dataset(source)
    if factor_dataset.empty or "factor_name" not in factor_dataset.columns:
        return {
            "factor_name": factor_name,
            "factor_available": False,
            "factor_ic": None,
            "factor_rank_ic": None,
            "factor_effectiveness_label": "Unavailable",
            "factor_group_returns": pd.DataFrame(columns=["factor_group", "factor_group_return"]),
            "factor_research_summary": f"{factor_name} factor has no available research sample.",
            "factor_warnings": ["No available factor sample."],
        }

    selected = factor_dataset[factor_dataset["factor_name"].astype(str).eq(str(factor_name))].copy(deep=True)
    if selected.empty:
        return {
            "factor_name": factor_name,
            "factor_available": False,
            "factor_ic": None,
            "factor_rank_ic": None,
            "factor_effectiveness_label": "Unavailable",
            "factor_group_returns": pd.DataFrame(columns=["factor_group", "factor_group_return"]),
            "factor_research_summary": f"{factor_name} factor is not available in the current dataset.",
            "factor_warnings": [f"{factor_name} field is missing."],
        }

    first = selected.iloc[0]
    group_returns = (
        selected[["factor_group", "factor_group_return"]]
        .dropna()
        .drop_duplicates()
        .sort_values("factor_group", kind="stable")
        .reset_index(drop=True)
    )
    warnings: list[str] = []
    for value in selected["factor_warnings"].tolist():
        if isinstance(value, list):
            warnings.extend(str(item) for item in value)
        elif pd.notna(value):
            warnings.append(str(value))
    return {
        "factor_name": factor_name,
        "factor_available": bool(selected["factor_available"].fillna(False).any()),
        "factor_ic": first.get("factor_ic"),
        "factor_rank_ic": first.get("factor_rank_ic"),
        "factor_effectiveness_label": first.get("factor_effectiveness_label", "Unavailable"),
        "factor_group_returns": group_returns,
        "factor_research_summary": first.get("factor_research_summary", ""),
        "factor_warnings": sorted(set(warnings)),
    }


__all__ = ["build_factor_research_report"]
