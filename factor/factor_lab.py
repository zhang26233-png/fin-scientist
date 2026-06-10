"""Factor Research Lab dataset builders."""

from __future__ import annotations

from typing import Any

import pandas as pd

from factor.factor_metrics import (
    calculate_factor_ic,
    calculate_group_returns,
    calculate_rank_ic,
    label_factor_effectiveness,
)


DEFAULT_FACTOR_COLUMNS = [
    "fundamental_score",
    "technical_score",
    "composite_score",
    "selection_score",
    "risk_score",
    "return_risk_ratio",
]

FACTOR_OUTPUT_COLUMNS = [
    "factor_available",
    "factor_name",
    "factor_value",
    "factor_zscore",
    "factor_group",
    "factor_ic",
    "factor_rank_ic",
    "factor_group_return",
    "factor_effectiveness_label",
    "factor_research_summary",
    "factor_warnings",
]

IDENTITY_COLUMNS = ["ticker", "symbol", "name", "selection_bucket", "selection_rank"]
RETURN_CANDIDATES = ["future_return", "period_return"]


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
        return pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")
    return pd.to_numeric(df[column], errors="coerce")


def _empty_output(extra_columns: list[str] | None = None) -> pd.DataFrame:
    columns = list(dict.fromkeys((extra_columns or []) + FACTOR_OUTPUT_COLUMNS))
    return pd.DataFrame(columns=columns)


def _return_column(source: pd.DataFrame) -> str | None:
    for column in RETURN_CANDIDATES:
        if column in source.columns and pd.to_numeric(source[column], errors="coerce").notna().any():
            return column
    return None


def _warnings_for_value(
    source: pd.DataFrame,
    factor_name: str,
    row_index: Any,
    return_col: str | None,
    factor_value: float | None,
    zscore: float | None,
) -> list[str]:
    warnings: list[str] = []
    if factor_name not in source.columns:
        warnings.append(f"{factor_name} field is missing.")
    if factor_value is None or pd.isna(factor_value):
        warnings.append(f"{factor_name} value is unavailable.")
    if zscore is None or pd.isna(zscore):
        warnings.append(f"{factor_name} zscore is unavailable.")
    if return_col is None:
        warnings.append("future_return or period_return is unavailable.")
    elif pd.isna(pd.to_numeric(pd.Series([source.at[row_index, return_col]]), errors="coerce").iloc[0]):
        warnings.append(f"{return_col} value is unavailable.")
    return warnings


def normalize_factor(df: Any, factor_columns: list[str]) -> pd.DataFrame:
    """Add zscore columns for available factor fields without mutating input."""
    source = _copy_frame(df)
    if source.empty:
        for factor_name in factor_columns:
            source[f"{factor_name}_zscore"] = pd.Series(dtype=float)
        return source
    for factor_name in factor_columns:
        if factor_name not in source.columns:
            continue
        numeric = pd.to_numeric(source[factor_name], errors="coerce")
        std = numeric.std()
        if pd.isna(std) or std == 0:
            source[f"{factor_name}_zscore"] = pd.NA
        else:
            source[f"{factor_name}_zscore"] = (numeric - numeric.mean()) / std
    return source


def build_factor_groups(df: Any, factor_name: str, n_groups: int = 5) -> pd.DataFrame:
    """Add Q1-Q5 factor groups for a single factor without changing row order."""
    source = _copy_frame(df)
    if source.empty:
        source["factor_group"] = pd.Series(dtype=object)
        source["factor_warnings"] = pd.Series(dtype=object)
        return source
    warnings = [[] for _ in range(len(source))]
    if factor_name not in source.columns:
        source["factor_group"] = pd.NA
        source["factor_warnings"] = [[f"{factor_name} field is missing."] for _ in range(len(source))]
        return source
    numeric = _numeric_series(source, factor_name)
    valid = numeric.dropna()
    source["factor_group"] = pd.NA
    if valid.empty:
        warnings = [[f"{factor_name} value is unavailable."] for _ in range(len(source))]
    else:
        unique_count = int(valid.nunique(dropna=True))
        group_count = max(1, min(int(n_groups), unique_count))
        if group_count <= 1:
            source.loc[valid.index, "factor_group"] = "Q1"
        else:
            labels = [f"Q{index}" for index in range(1, group_count + 1)]
            groups = pd.qcut(valid, q=group_count, labels=labels, duplicates="drop").astype(str)
            source.loc[groups.index, "factor_group"] = groups
        for position, row_index in enumerate(source.index):
            if pd.isna(numeric.loc[row_index]):
                warnings[position].append(f"{factor_name} value is unavailable.")
    source["factor_warnings"] = warnings
    return source


def _group_map(group_returns: pd.DataFrame) -> dict[str, float]:
    if group_returns.empty:
        return {}
    return {
        str(row["factor_group"]): float(row["factor_group_return"])
        for _, row in group_returns.iterrows()
        if pd.notna(row.get("factor_group_return"))
    }


def _summary(factor_name: str, label: str, ic_value: float | None, rank_ic: float | None) -> str:
    ic_text = "Unavailable" if ic_value is None else f"{ic_value:.4f}"
    rank_text = "Unavailable" if rank_ic is None else f"{rank_ic:.4f}"
    return (
        f"{factor_name} factor research label is {label}. "
        f"IC={ic_text}, Rank IC={rank_text}. "
        "This is a neutral research observation for further review."
    )


def build_factor_dataset(df: Any) -> pd.DataFrame:
    """Build a long-format read-only factor research dataset."""
    source = _copy_frame(df)
    available_id_columns = [column for column in IDENTITY_COLUMNS if column in source.columns]
    if source.empty:
        return _empty_output(available_id_columns)

    available_factors = [column for column in DEFAULT_FACTOR_COLUMNS if column in source.columns]
    if not available_factors:
        return _empty_output(available_id_columns)

    normalized = normalize_factor(source, available_factors)
    return_col = _return_column(source)
    rows: list[dict[str, Any]] = []

    for factor_name in available_factors:
        grouped = build_factor_groups(source, factor_name)
        ic_value = calculate_factor_ic(source, factor_name, return_col) if return_col else None
        rank_ic = calculate_rank_ic(source, factor_name, return_col) if return_col else None
        group_returns = calculate_group_returns(source, factor_name, return_col) if return_col else pd.DataFrame()
        group_returns_map = _group_map(group_returns)
        label = label_factor_effectiveness(ic_value)
        summary = _summary(factor_name, label, ic_value, rank_ic)

        for row_index, source_row in source.iterrows():
            factor_value = _numeric_series(source, factor_name).loc[row_index]
            zscore = normalized.get(f"{factor_name}_zscore", pd.Series(index=source.index)).loc[row_index]
            group = grouped.at[row_index, "factor_group"] if "factor_group" in grouped.columns else pd.NA
            output: dict[str, Any] = {column: source_row.get(column) for column in available_id_columns}
            output.update(
                {
                    "factor_available": not pd.isna(factor_value),
                    "factor_name": factor_name,
                    "factor_value": None if pd.isna(factor_value) else float(factor_value),
                    "factor_zscore": None if pd.isna(zscore) else float(zscore),
                    "factor_group": None if pd.isna(group) else str(group),
                    "factor_ic": ic_value,
                    "factor_rank_ic": rank_ic,
                    "factor_group_return": group_returns_map.get(str(group)),
                    "factor_effectiveness_label": label,
                    "factor_research_summary": summary,
                    "factor_warnings": _warnings_for_value(
                        source,
                        factor_name,
                        row_index,
                        return_col,
                        None if pd.isna(factor_value) else float(factor_value),
                        None if pd.isna(zscore) else float(zscore),
                    ),
                }
            )
            rows.append(output)

    columns = list(dict.fromkeys(available_id_columns + FACTOR_OUTPUT_COLUMNS))
    return pd.DataFrame(rows, columns=columns)


__all__ = [
    "DEFAULT_FACTOR_COLUMNS",
    "FACTOR_OUTPUT_COLUMNS",
    "build_factor_dataset",
    "build_factor_groups",
    "normalize_factor",
]
