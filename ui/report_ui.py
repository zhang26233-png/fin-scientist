"""Read-only Streamlit report experience for Fin-Scientist research outputs."""

from __future__ import annotations

import copy
from typing import Any

import pandas as pd
import streamlit as st


REPORT_VERSION = "v4.0.0"
REPORT_STAGE = "Web UI Report Experience"

OVERVIEW_COLUMNS = [
    "candidate_pool",
    "selection_bucket",
    "selection_rank",
    "selection_score",
    "selection_status",
    "selection_quality_label",
]

CARD_COLUMNS = [
    "ticker",
    "name",
    "selection_score",
    "selection_rank",
    "selection_bucket",
    "selection_thesis",
    "selection_summary",
    "selection_strengths",
    "selection_risks",
    "selection_explanation",
]

SCORE_COLUMNS = [
    "ticker",
    "name",
    "fundamental_score",
    "technical_score",
    "composite_score",
    "risk_score",
    "selection_score",
    "selection_factor_breakdown",
]

BACKTEST_COLUMNS = [
    "ticker",
    "name",
    "period_return",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "win_rate",
    "return_risk_ratio",
    "performance_label",
    "backtest_quality_label",
]

RISK_COLUMNS = [
    "ticker",
    "name",
    "selection_risk_notes",
    "backtest_evaluation_warnings",
    "return_analysis_warnings",
    "explain_warnings",
]

STATUS_COLUMNS = [
    "return_analysis_status",
    "backtest_evaluation_status",
    "selection_status",
    "explain_status",
]


def safe_copy_frame(source: Any) -> pd.DataFrame:
    """Return a defensive DataFrame copy for read-only report rendering."""
    if source is None:
        return pd.DataFrame()
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    return pd.DataFrame()


def format_report_value(value: Any) -> str:
    """Format scalar, list, and dict values for compact UI display."""
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value) if value else ""
    if isinstance(value, dict):
        return "\n".join(f"{key}: {format_report_value(item)}" for key, item in value.items()) if value else ""
    return str(value)


def existing_columns(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    """Return only columns that exist in the frame."""
    return [column for column in columns if column in frame.columns]


def format_display_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Create a display-only frame with list and dict values formatted."""
    source = safe_copy_frame(frame)
    selected = existing_columns(source, columns)
    if source.empty or not selected:
        return pd.DataFrame(columns=selected)
    display = source[selected].copy(deep=True)
    for column in display.columns:
        display[column] = display[column].map(format_report_value)
    return display


def _truthy_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series([False] * len(frame), index=frame.index)
    return frame[column].map(lambda value: bool(value) if not pd.isna(value) else False)


def build_report_overview(frame: pd.DataFrame) -> dict[str, Any]:
    """Build top-level report counts without mutating the input frame."""
    source = safe_copy_frame(frame)
    if source.empty:
        return {
            "version": REPORT_VERSION,
            "stage": REPORT_STAGE,
            "research_count": 0,
            "core_count": 0,
            "watch_count": 0,
            "exclude_count": 0,
            "explain_count": 0,
        }

    bucket_source = source["selection_bucket"] if "selection_bucket" in source.columns else source.get("candidate_pool")
    if bucket_source is None:
        bucket_source = pd.Series([""] * len(source), index=source.index)

    return {
        "version": REPORT_VERSION,
        "stage": REPORT_STAGE,
        "research_count": int(len(source)),
        "core_count": int((bucket_source == "Core").sum()),
        "watch_count": int((bucket_source == "Watch").sum()),
        "exclude_count": int((bucket_source == "Exclude").sum()),
        "explain_count": int(_truthy_series(source, "explain_available").sum()),
    }


def collect_warning_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Collect warnings, Incomplete statuses, and Unavailable statuses."""
    source = safe_copy_frame(frame)
    rows = []
    if source.empty:
        return pd.DataFrame(columns=["ticker", "name", "field", "message"])

    warning_columns = [column for column in source.columns if column.endswith("_warnings") or column == "warnings"]
    status_columns = existing_columns(source, STATUS_COLUMNS)

    for _, row in source.iterrows():
        ticker = row.get("ticker", row.get("symbol", ""))
        name = row.get("name", "")
        for column in warning_columns:
            value = row.get(column)
            if isinstance(value, list):
                messages = [str(item) for item in value if str(item)]
            elif value is None or (isinstance(value, float) and pd.isna(value)) or value == "":
                messages = []
            else:
                messages = [str(value)]
            for message in messages:
                rows.append({"ticker": ticker, "name": name, "field": column, "message": message})
        for column in status_columns:
            value = row.get(column)
            if value in {"Incomplete", "Unavailable"}:
                rows.append({"ticker": ticker, "name": name, "field": column, "message": str(value)})
    return pd.DataFrame(rows, columns=["ticker", "name", "field", "message"])


def build_report_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build all display tables used by the report page."""
    source = safe_copy_frame(frame)
    return {
        "candidate_overview": format_display_frame(source, ["ticker", "name"] + OVERVIEW_COLUMNS),
        "score_breakdown": format_display_frame(source, SCORE_COLUMNS),
        "backtest": format_display_frame(source, BACKTEST_COLUMNS),
        "risk": format_display_frame(source, RISK_COLUMNS),
        "data_quality": collect_warning_summary(source),
    }


def _render_overview_metrics(summary: dict[str, Any]) -> None:
    columns = st.columns(6)
    columns[0].metric("Version", summary["version"])
    columns[1].metric("Stage", summary["stage"])
    columns[2].metric("Research Objects", summary["research_count"])
    columns[3].metric("Core", summary["core_count"])
    columns[4].metric("Watch", summary["watch_count"])
    columns[5].metric("Explainable", summary["explain_count"])


def _render_stock_cards(frame: pd.DataFrame) -> None:
    source = safe_copy_frame(frame)
    if source.empty:
        st.info("No stock research cards are available.")
        return

    for _, row in source.iterrows():
        ticker = format_report_value(row.get("ticker", row.get("symbol", "")))
        name = format_report_value(row.get("name", ""))
        title = " ".join(part for part in [ticker, name] if part).strip() or "Research Object"
        score = format_report_value(row.get("selection_score", ""))
        rank = format_report_value(row.get("selection_rank", ""))
        bucket = format_report_value(row.get("selection_bucket", "Unavailable"))
        thesis = format_report_value(row.get("selection_thesis", "Unavailable"))
        summary = format_report_value(row.get("selection_summary", ""))
        strengths = format_report_value(row.get("selection_strengths", []))
        risks = format_report_value(row.get("selection_risks", []))
        explanation = format_report_value(row.get("selection_explanation", ""))

        with st.container(border=True):
            st.subheader(title)
            metric_cols = st.columns(4)
            metric_cols[0].metric("Selection Score", score)
            metric_cols[1].metric("Selection Rank", rank)
            metric_cols[2].metric("Bucket", bucket)
            metric_cols[3].metric("Thesis", thesis)
            if summary:
                st.caption(summary)
            card_tabs = st.tabs(["Strengths", "Risks", "Explanation"])
            card_tabs[0].markdown(strengths or "No strengths available.")
            card_tabs[1].markdown(risks or "No risk notes available.")
            card_tabs[2].markdown(explanation or "No explanation available.")


def render_report_experience(report_df: pd.DataFrame) -> dict[str, Any]:
    """Render the read-only web report experience and return display payloads."""
    source = safe_copy_frame(report_df)
    summary = build_report_overview(source)
    tables = build_report_tables(source)

    st.header("Personal Stock Research Workbench")
    st.caption("All sections are read-only research views and do not constitute investment advice.")
    _render_overview_metrics(summary)

    tabs = st.tabs(
        [
            "Candidate Overview",
            "Stock Cards",
            "Score Breakdown",
            "Backtest",
            "Risk",
            "Data Quality",
        ]
    )

    with tabs[0]:
        st.subheader("Candidate Pool Overview")
        if tables["candidate_overview"].empty:
            st.info("No candidate overview rows are available.")
        else:
            st.dataframe(tables["candidate_overview"], hide_index=True, use_container_width=True)

    with tabs[1]:
        st.subheader("Stock Research Cards")
        _render_stock_cards(source)

    with tabs[2]:
        st.subheader("Score Breakdown")
        if tables["score_breakdown"].empty:
            st.info("No score breakdown rows are available.")
        else:
            st.dataframe(tables["score_breakdown"], hide_index=True, use_container_width=True)

    with tabs[3]:
        st.subheader("Backtest Performance")
        if tables["backtest"].empty:
            st.info("No backtest performance rows are available.")
        else:
            st.dataframe(tables["backtest"], hide_index=True, use_container_width=True)

    with tabs[4]:
        st.subheader("Risk Notes")
        if tables["risk"].empty:
            st.info("No risk rows are available.")
        else:
            st.dataframe(tables["risk"], hide_index=True, use_container_width=True)

    with tabs[5]:
        st.subheader("Data Quality")
        if tables["data_quality"].empty:
            st.info("No warnings or incomplete statuses are available.")
        else:
            st.dataframe(tables["data_quality"], hide_index=True, use_container_width=True)

    return {"summary": summary, "tables": tables}


__all__ = [
    "BACKTEST_COLUMNS",
    "CARD_COLUMNS",
    "OVERVIEW_COLUMNS",
    "REPORT_STAGE",
    "REPORT_VERSION",
    "RISK_COLUMNS",
    "SCORE_COLUMNS",
    "build_report_overview",
    "build_report_tables",
    "collect_warning_summary",
    "existing_columns",
    "format_display_frame",
    "format_report_value",
    "render_report_experience",
    "safe_copy_frame",
]
