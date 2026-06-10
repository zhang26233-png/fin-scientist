"""Reusable Streamlit components for the Research Terminal UI."""

from __future__ import annotations

import copy
from typing import Any

import pandas as pd
import streamlit as st


SCORE_FIELDS = [
    "fundamental_score",
    "technical_score",
    "composite_score",
    "risk_score",
    "selection_score",
]

BACKTEST_FIELDS = [
    "period_return",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "win_rate",
    "return_risk_ratio",
    "performance_label",
    "backtest_quality_label",
]

COMPARE_FIELDS = [
    "ticker",
    "name",
    "selection_score",
    "composite_score",
    "fundamental_score",
    "technical_score",
    "period_return",
    "annualized_return",
    "max_drawdown",
    "volatility",
    "risk_level",
    "performance_label",
]

PERCENT_FIELDS = {
    "period_return",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "win_rate",
}

WARNING_STATUS_FIELDS = [
    "fundamental_screening_status",
    "technical_screening_status",
    "composite_screening_status",
    "candidate_status",
    "backtest_status",
    "return_analysis_status",
    "backtest_evaluation_status",
    "selection_status",
    "explain_status",
]


def safe_copy_frame(source: Any) -> pd.DataFrame:
    """Return a defensive DataFrame copy for read-only terminal rendering."""
    if source is None:
        return pd.DataFrame()
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    return pd.DataFrame()


def is_missing(value: Any) -> bool:
    """Handle pandas, Python, list, and dict missing values without raising."""
    if value is None:
        return True
    if isinstance(value, (list, dict, tuple, set)):
        return False
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def format_list_field(value: Any) -> str:
    """Format list-like values for readable terminal cards."""
    if is_missing(value):
        return ""
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value if not is_missing(item))
    if isinstance(value, tuple):
        return "\n".join(f"- {item}" for item in value if not is_missing(item))
    if isinstance(value, set):
        return "\n".join(f"- {item}" for item in sorted(value) if not is_missing(item))
    return str(value)


def format_dict_field(value: Any) -> str:
    """Format dictionaries recursively for compact terminal display."""
    if is_missing(value):
        return ""
    if not isinstance(value, dict):
        return str(value)
    lines = []
    for key, item in value.items():
        if isinstance(item, dict):
            rendered = format_dict_field(item).replace("\n", "; ")
        elif isinstance(item, (list, tuple, set)):
            rendered = format_list_field(item).replace("\n", "; ")
        else:
            rendered = format_terminal_value(item)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines)


def format_terminal_value(value: Any, field_name: str = "") -> str:
    """Format values with field-aware percentage and numeric handling."""
    if is_missing(value):
        return ""
    if isinstance(value, dict):
        return format_dict_field(value)
    if isinstance(value, (list, tuple, set)):
        return format_list_field(value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if field_name in PERCENT_FIELDS:
            return f"{value * 100:.2f}%"
        return f"{value:.2f}"
    return str(value)


def existing_columns(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    """Return the requested columns that exist in the DataFrame."""
    return [column for column in columns if column in frame.columns]


def get_identity(row: pd.Series) -> tuple[str, str]:
    """Return ticker and name with symbol fallback."""
    ticker = format_terminal_value(row.get("ticker", row.get("symbol", "")))
    name = format_terminal_value(row.get("name", ""))
    return ticker, name


def collect_warning_fields(row: pd.Series) -> list[str]:
    """Collect warning fields and incomplete/unavailable statuses from one row."""
    warnings: list[str] = []
    for field, value in row.items():
        if field.endswith("_warnings") or field == "warnings":
            if isinstance(value, list):
                warnings.extend(str(item) for item in value if not is_missing(item) and str(item))
            elif not is_missing(value) and str(value):
                warnings.append(str(value))
    for field in WARNING_STATUS_FIELDS:
        value = row.get(field)
        if value in {"Incomplete", "Unavailable"}:
            warnings.append(f"{field}: {value}")
    return warnings


def build_dashboard_summary(frame: pd.DataFrame) -> dict[str, Any]:
    """Build dashboard metrics without mutating the input frame."""
    source = safe_copy_frame(frame)
    if source.empty:
        return {
            "research_count": 0,
            "core_count": 0,
            "watch_count": 0,
            "exclude_count": 0,
            "avg_selection_score": None,
            "avg_composite_score": None,
            "high_risk_count": 0,
            "incomplete_data_count": 0,
        }

    bucket = source["selection_bucket"] if "selection_bucket" in source.columns else source.get("candidate_pool")
    if bucket is None:
        bucket = pd.Series([""] * len(source), index=source.index)

    status_values = []
    for field in WARNING_STATUS_FIELDS:
        if field in source.columns:
            status_values.append(source[field].isin(["Incomplete", "Unavailable"]))
    incomplete_mask = status_values[0] if status_values else pd.Series([False] * len(source), index=source.index)
    for mask in status_values[1:]:
        incomplete_mask = incomplete_mask | mask

    risk_mask = source["risk_level"].eq("High") if "risk_level" in source.columns else pd.Series([False] * len(source), index=source.index)

    return {
        "research_count": int(len(source)),
        "core_count": int(bucket.eq("Core").sum()),
        "watch_count": int(bucket.eq("Watch").sum()),
        "exclude_count": int(bucket.eq("Exclude").sum()),
        "avg_selection_score": source["selection_score"].mean() if "selection_score" in source.columns else None,
        "avg_composite_score": source["composite_score"].mean() if "composite_score" in source.columns else None,
        "high_risk_count": int(risk_mask.sum()),
        "incomplete_data_count": int(incomplete_mask.sum()),
    }


def build_compare_frame(frame: pd.DataFrame, tickers: list[str] | None = None) -> pd.DataFrame:
    """Build a display-ready comparison frame for selected tickers."""
    source = safe_copy_frame(frame)
    columns = existing_columns(source, COMPARE_FIELDS)
    if source.empty or not columns:
        return pd.DataFrame(columns=columns)
    filtered = source
    if tickers and "ticker" in source.columns:
        filtered = source[source["ticker"].isin(tickers)]
    display = filtered[columns].copy(deep=True)
    for column in display.columns:
        display[column] = display[column].map(lambda value, field=column: format_terminal_value(value, field))
    return display


def build_risk_center_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build risk center groups from existing fields only."""
    source = safe_copy_frame(frame)
    base_columns = existing_columns(source, ["ticker", "name", "risk_level", "max_drawdown", "volatility", "selection_status", "explain_status"])
    empty = pd.DataFrame(columns=base_columns)
    if source.empty:
        return {
            "high_risk": empty,
            "high_drawdown": empty,
            "high_volatility": empty,
            "missing_data": empty,
            "unavailable": empty,
        }

    high_risk = source[source["risk_level"].eq("High")] if "risk_level" in source.columns else source.iloc[0:0]
    high_drawdown = source[pd.to_numeric(source.get("max_drawdown"), errors="coerce").lt(-0.2)] if "max_drawdown" in source.columns else source.iloc[0:0]
    high_volatility = source[pd.to_numeric(source.get("volatility"), errors="coerce").gt(0.4)] if "volatility" in source.columns else source.iloc[0:0]

    missing_mask = pd.Series([False] * len(source), index=source.index)
    unavailable_mask = pd.Series([False] * len(source), index=source.index)
    for field in WARNING_STATUS_FIELDS:
        if field in source.columns:
            missing_mask = missing_mask | source[field].eq("Incomplete")
            unavailable_mask = unavailable_mask | source[field].eq("Unavailable")

    return {
        "high_risk": high_risk[base_columns].copy(deep=True) if base_columns else pd.DataFrame(),
        "high_drawdown": high_drawdown[base_columns].copy(deep=True) if base_columns else pd.DataFrame(),
        "high_volatility": high_volatility[base_columns].copy(deep=True) if base_columns else pd.DataFrame(),
        "missing_data": source[missing_mask][base_columns].copy(deep=True) if base_columns else pd.DataFrame(),
        "unavailable": source[unavailable_mask][base_columns].copy(deep=True) if base_columns else pd.DataFrame(),
    }


def render_metric_grid(summary: dict[str, Any]) -> None:
    """Render the Research Dashboard metric grid."""
    first = st.columns(4)
    first[0].metric("研究对象数量", summary["research_count"])
    first[1].metric("Core 数量", summary["core_count"])
    first[2].metric("Watch 数量", summary["watch_count"])
    first[3].metric("Exclude 数量", summary["exclude_count"])

    second = st.columns(4)
    second[0].metric("平均 selection_score", format_terminal_value(summary["avg_selection_score"]))
    second[1].metric("平均 composite_score", format_terminal_value(summary["avg_composite_score"]))
    second[2].metric("高风险标的数量", summary["high_risk_count"])
    second[3].metric("数据不完整标的数量", summary["incomplete_data_count"])


def render_score_progress(row: pd.Series) -> None:
    """Render score fields with metrics and progress bars."""
    for field in SCORE_FIELDS:
        value = row.get(field)
        label = field
        if is_missing(value):
            st.caption(f"{label}: 暂无可展示数据")
            continue
        metric_cols = st.columns([1, 3])
        metric_cols[0].metric(label, format_terminal_value(value, field))
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        if not pd.isna(numeric):
            metric_cols[1].progress(max(0.0, min(float(numeric) / 100.0, 1.0)))


def render_key_value_table(row: pd.Series, fields: list[str]) -> None:
    """Render selected row fields as a compact key-value table."""
    rows = []
    for field in fields:
        if field in row.index:
            rows.append({"字段": field, "内容": format_terminal_value(row.get(field), field)})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    else:
        st.info("当前字段暂不可用。")


__all__ = [
    "BACKTEST_FIELDS",
    "COMPARE_FIELDS",
    "SCORE_FIELDS",
    "WARNING_STATUS_FIELDS",
    "build_compare_frame",
    "build_dashboard_summary",
    "build_risk_center_tables",
    "collect_warning_fields",
    "existing_columns",
    "format_dict_field",
    "format_list_field",
    "format_terminal_value",
    "get_identity",
    "render_key_value_table",
    "render_metric_grid",
    "render_score_progress",
    "safe_copy_frame",
]
