"""Research Terminal UI package for read-only stock research review."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.report_builder import build_stock_research_report
from ui.terminal_components import (
    BACKTEST_FIELDS,
    COMPARE_FIELDS,
    build_compare_frame,
    build_dashboard_summary,
    build_risk_center_tables,
    collect_warning_fields,
    existing_columns,
    format_list_field,
    format_terminal_value,
    get_identity,
    render_key_value_table,
    render_metric_grid,
    render_score_progress,
    safe_copy_frame,
)


TERMINAL_VERSION = "v4.1.0"
TERMINAL_STAGE = "Research Terminal UI Package"


def render_dashboard(df: pd.DataFrame) -> dict[str, object]:
    """Render Research Dashboard and return the summary payload."""
    source = safe_copy_frame(df)
    summary = build_dashboard_summary(source)
    st.subheader("Research Dashboard")
    st.caption("研究终端仅展示现有研究字段，不构成投资建议。")
    render_metric_grid(summary)
    return summary


def _top_pick_frame(df: pd.DataFrame) -> pd.DataFrame:
    source = safe_copy_frame(df)
    if source.empty:
        return source
    bucket = source["selection_bucket"] if "selection_bucket" in source.columns else source.get("candidate_pool")
    if bucket is None:
        return source.iloc[0:0]
    picks = source[bucket.isin(["Core", "Watch"])].copy(deep=True)
    if "selection_rank" in picks.columns:
        return picks.sort_values("selection_rank", kind="stable").head(8)
    return picks.head(8)


def render_top_picks(df: pd.DataFrame) -> pd.DataFrame:
    """Render Top Core / Watch stock cards."""
    picks = _top_pick_frame(df)
    st.subheader("Top Picks")
    if picks.empty:
        st.info("当前没有可展示的 Core / Watch 研究对象。")
        return picks

    for _, row in picks.iterrows():
        ticker, name = get_identity(row)
        title = " ".join(part for part in [ticker, name] if part).strip() or "研究对象"
        with st.container(border=True):
            st.markdown(f"### {title}")
            metric_cols = st.columns(4)
            metric_cols[0].metric("selection_rank", format_terminal_value(row.get("selection_rank")))
            metric_cols[1].metric("selection_score", format_terminal_value(row.get("selection_score")))
            metric_cols[2].metric("selection_bucket", format_terminal_value(row.get("selection_bucket")))
            metric_cols[3].metric("selection_thesis", format_terminal_value(row.get("selection_thesis")))
            st.caption(format_terminal_value(row.get("selection_summary")) or "暂无可展示摘要。")
            cols = st.columns(2)
            cols[0].markdown("**✓ 优势**")
            cols[0].markdown(format_list_field(row.get("selection_strengths")) or "暂无可展示优势。")
            cols[1].markdown("**⚠ 风险提示**")
            cols[1].markdown(format_list_field(row.get("selection_risks")) or "暂无可展示风险。")
    return picks


def render_score_breakdown(row: pd.Series) -> None:
    """Render score metrics, progress bars, and factor breakdown."""
    st.subheader("Score Breakdown")
    render_score_progress(row)
    if "selection_factor_breakdown" in row.index:
        st.markdown("**因子拆解**")
        st.markdown(format_terminal_value(row.get("selection_factor_breakdown")) or "暂无可展示因子拆解。")


def render_backtest_panel(row: pd.Series) -> None:
    """Render historical metrics from existing backtest fields."""
    st.subheader("Backtest Panel")
    render_key_value_table(row, BACKTEST_FIELDS)


def render_stock_detail(df: pd.DataFrame, selected_ticker: str | None) -> pd.Series | None:
    """Render the single-stock detail panel."""
    source = safe_copy_frame(df)
    st.subheader("Stock Detail Panel")
    if source.empty:
        st.info("当前没有可查看的研究对象。")
        return None
    if not selected_ticker or "ticker" not in source.columns:
        row = source.iloc[0].copy(deep=True)
    else:
        matched = source[source["ticker"].astype(str).eq(str(selected_ticker))]
        row = matched.iloc[0].copy(deep=True) if not matched.empty else source.iloc[0].copy(deep=True)

    ticker, name = get_identity(row)
    st.markdown(f"### {' '.join(part for part in [ticker, name] if part).strip() or '研究对象'}")
    tabs = st.tabs(["基本信息", "评分拆解", "解释层结果", "回测表现", "风险提示", "数据质量提示"])
    with tabs[0]:
        render_key_value_table(row, ["ticker", "name", "selection_bucket", "selection_rank", "selection_status", "selection_quality_label"])
    with tabs[1]:
        render_score_breakdown(row)
    with tabs[2]:
        render_key_value_table(row, ["selection_thesis", "selection_summary", "selection_strengths", "selection_risks", "selection_explanation"])
    with tabs[3]:
        render_backtest_panel(row)
    with tabs[4]:
        st.markdown(format_list_field(row.get("selection_risks")) or format_list_field(row.get("selection_risk_notes")) or "暂无可展示风险提示。")
    with tabs[5]:
        warnings = collect_warning_fields(row)
        st.markdown(format_list_field(warnings) or "当前未汇总到明显的数据质量提示。")
    return row


def render_risk_center(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Render risk center grouped views."""
    tables = build_risk_center_tables(df)
    st.subheader("Risk Center")
    labels = [
        ("High Risk 股票", "high_risk"),
        ("High Drawdown 股票", "high_drawdown"),
        ("High Volatility 股票", "high_volatility"),
        ("Missing Data 股票", "missing_data"),
        ("Unavailable 股票", "unavailable"),
    ]
    tabs = st.tabs([label for label, _ in labels])
    for tab, (label, key) in zip(tabs, labels):
        with tab:
            table = tables[key]
            if table.empty:
                st.info(f"当前没有 {label}。")
            else:
                st.dataframe(table, hide_index=True, use_container_width=True)
    return tables


def render_compare_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Render 2-5 stock comparison panel."""
    source = safe_copy_frame(df)
    st.subheader("Compare Panel")
    if source.empty or "ticker" not in source.columns:
        st.info("当前没有可对比的研究对象。")
        return build_compare_frame(source)

    options = [str(value) for value in source["ticker"].dropna().tolist()]
    default = options[: min(2, len(options))]
    selected = st.multiselect("选择 2-5 只股票进行对比", options=options, default=default, max_selections=5)
    if len(selected) < 2:
        st.info("请选择至少 2 个研究对象。")
    table = build_compare_frame(source, selected)
    if table.empty:
        st.info("当前没有可展示的对比字段。")
    else:
        st.dataframe(table[existing_columns(table, COMPARE_FIELDS)], hide_index=True, use_container_width=True)
    return table


def render_report_preview(row: pd.Series | None) -> str:
    """Render read-only single-stock research report preview."""
    st.subheader("Research Report Preview")
    if row is None:
        st.info("当前没有可生成报告预览的研究对象。")
        return ""
    report = build_stock_research_report(row)
    st.text_area("只读研究报告预览", value=report, height=420, disabled=True)
    return report


def render_research_terminal(df: pd.DataFrame) -> dict[str, object]:
    """Render the complete Research Terminal page from existing result fields."""
    source = safe_copy_frame(df)
    st.header("Research Terminal")
    st.caption(f"{TERMINAL_VERSION} {TERMINAL_STAGE}；仅供学习和研究，不构成投资建议。")

    dashboard = render_dashboard(source)
    tabs = st.tabs(["Top Picks", "Stock Detail", "Risk Center", "Compare", "Report Preview"])

    with tabs[0]:
        top_picks = render_top_picks(source)

    selected_ticker = None
    if not source.empty and "ticker" in source.columns:
        tickers = [str(value) for value in source["ticker"].dropna().tolist()]
        if tickers:
            selected_ticker = st.selectbox("选择研究对象", options=tickers, index=0)

    with tabs[1]:
        selected_row = render_stock_detail(source, selected_ticker)
    with tabs[2]:
        risk_tables = render_risk_center(source)
    with tabs[3]:
        compare_table = render_compare_panel(source)
    with tabs[4]:
        report = render_report_preview(selected_row)

    return {
        "dashboard": dashboard,
        "top_picks": top_picks,
        "selected_row": selected_row,
        "risk_tables": risk_tables,
        "compare_table": compare_table,
        "report": report,
    }


__all__ = [
    "TERMINAL_STAGE",
    "TERMINAL_VERSION",
    "build_stock_research_report",
    "collect_warning_fields",
    "format_list_field",
    "render_backtest_panel",
    "render_compare_panel",
    "render_dashboard",
    "render_research_terminal",
    "render_risk_center",
    "render_score_breakdown",
    "render_stock_detail",
    "render_top_picks",
]
