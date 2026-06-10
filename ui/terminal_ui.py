"""Visual Research Terminal UI for read-only stock research review."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.report_builder import build_stock_research_report
from ui.terminal_components import (
    BACKTEST_FIELDS,
    COMPARE_FIELDS,
    SCORE_FIELDS,
    build_compare_frame,
    build_dashboard_summary,
    build_risk_center_tables,
    collect_warning_fields,
    existing_columns,
    format_list_field,
    format_terminal_value,
    get_identity,
    render_key_value_table,
    safe_copy_frame,
)
from ui.visual_components import (
    render_compare_table,
    render_metric_card,
    render_report_block,
    render_score_bar,
    render_stock_card,
    render_warning_box,
)
from ui.visual_theme import (
    get_risk_badge,
    get_score_badge,
    get_status_badge,
    get_terminal_css,
    render_section_title,
    render_terminal_header,
)


TERMINAL_VERSION = "v4.2.0"
TERMINAL_STAGE = "Visual Research Terminal Redesign"


def render_dashboard(df: pd.DataFrame) -> dict[str, object]:
    """Render dashboard cards and return the summary payload."""
    source = safe_copy_frame(df)
    summary = build_dashboard_summary(source)
    render_section_title("Dashboard Cards", "用卡片方式观察研究对象结构、平均分和数据完整性。")
    cards = [
        ("研究对象总数", summary["research_count"], "当前结果集中可观察的对象数量。"),
        ("Core 数量", summary["core_count"], "进入 Core 分组的研究对象。"),
        ("Watch 数量", summary["watch_count"], "需要继续观察的研究对象。"),
        ("Exclude 数量", summary["exclude_count"], "当前不进入重点观察的对象。"),
        ("平均 selection_score", format_terminal_value(summary["avg_selection_score"]), "只读选择层平均分。"),
        ("平均 composite_score", format_terminal_value(summary["avg_composite_score"]), "基本面与技术面综合分均值。"),
        ("高风险数量", summary["high_risk_count"], "risk_level 为 High 的对象数量。"),
        ("数据不完整数量", summary["incomplete_data_count"], "存在 Incomplete 或 Unavailable 状态的对象。"),
    ]
    for row_start in range(0, len(cards), 4):
        columns = st.columns(4)
        for column, (title, value, help_text) in zip(columns, cards[row_start : row_start + 4]):
            with column:
                render_metric_card(title, value, help_text)
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
    render_section_title("Top Picks Cards", "展示 Core 和 Watch 中靠前的研究对象，不改变原始结果顺序。")
    if picks.empty:
        st.info("当前没有可展示的 Core / Watch 研究对象。")
        return picks

    for _, row in picks.iterrows():
        render_stock_card(row, format_terminal_value)
    return picks


def render_score_breakdown(row: pd.Series) -> None:
    """Render score metrics, badges, and progress bars."""
    render_section_title("Score Breakdown", "评分只用于展示，不改变任何上游评分值。")
    for field in SCORE_FIELDS:
        value = row.get(field)
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        if pd.isna(numeric):
            badge = get_score_badge("Unavailable")
        elif numeric >= 75:
            badge = get_score_badge("High")
        elif numeric >= 50:
            badge = get_score_badge("Medium")
        else:
            badge = get_score_badge("Low")
        render_score_bar(field, value, badge)

    if "selection_factor_breakdown" in row.index:
        st.markdown("**因子拆解**")
        st.markdown(format_terminal_value(row.get("selection_factor_breakdown")) or "—")


def render_backtest_panel(row: pd.Series) -> None:
    """Render historical metrics from existing backtest fields."""
    render_section_title("Backtest Panel", "展示已有历史表现字段，仅用于研究回顾。")
    render_key_value_table(row, BACKTEST_FIELDS)


def render_stock_detail(df: pd.DataFrame, selected_ticker: str | None) -> pd.Series | None:
    """Render the single-stock detail panel."""
    source = safe_copy_frame(df)
    render_section_title("Stock Detail Panel", "选择单只股票查看摘要、评分、解释、历史表现、风险和数据质量。")
    if source.empty:
        st.info("当前没有可查看的研究对象。")
        return None
    if not selected_ticker or "ticker" not in source.columns:
        row = source.iloc[0].copy(deep=True)
    else:
        matched = source[source["ticker"].astype(str).eq(str(selected_ticker))]
        row = matched.iloc[0].copy(deep=True) if not matched.empty else source.iloc[0].copy(deep=True)

    ticker, name = get_identity(row)
    title = " ".join(part for part in [ticker, name] if part and part != "—").strip() or "研究对象"
    status_cols = st.columns([2, 1, 1, 1])
    status_cols[0].markdown(f"### {title}")
    status_cols[1].markdown(get_status_badge(row.get("selection_bucket")), unsafe_allow_html=True)
    status_cols[2].markdown(get_risk_badge(row.get("risk_level")), unsafe_allow_html=True)
    status_cols[3].markdown(get_status_badge(row.get("selection_status")), unsafe_allow_html=True)

    tabs = st.tabs(["基本信息", "核心摘要", "评分拆解", "解释层结果", "回测表现", "风险提示", "数据质量"])
    with tabs[0]:
        render_key_value_table(
            row,
            ["ticker", "name", "selection_bucket", "selection_rank", "selection_status", "selection_quality_label"],
        )
    with tabs[1]:
        st.markdown(format_terminal_value(row.get("selection_summary")))
        st.markdown(get_status_badge(row.get("selection_thesis")), unsafe_allow_html=True)
    with tabs[2]:
        render_score_breakdown(row)
    with tabs[3]:
        render_key_value_table(
            row,
            ["selection_thesis", "selection_summary", "selection_strengths", "selection_risks", "selection_explanation"],
        )
    with tabs[4]:
        render_backtest_panel(row)
    with tabs[5]:
        risks = format_list_field(row.get("selection_risks")) or format_list_field(row.get("selection_risk_notes"))
        render_warning_box(risks or "暂无可展示风险提示。")
    with tabs[6]:
        warnings = collect_warning_fields(row)
        render_warning_box(warnings)
    return row


def _format_risk_table(table: pd.DataFrame) -> pd.DataFrame:
    display = table.copy(deep=True)
    for column in display.columns:
        display[column] = display[column].map(lambda value, field=column: format_terminal_value(value, field))
    return display.replace("", "—").fillna("—")


def render_risk_center(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Render visual risk center grouped views."""
    tables = build_risk_center_tables(df)
    render_section_title("Risk Center", "按风险、回撤、波动、缺失数据和不可用状态进行分组查看。")
    groups = [
        ("High Risk", "high_risk", "risk_level 为 High 的对象。"),
        ("High Drawdown", "high_drawdown", "max_drawdown 小于 -20% 的对象。"),
        ("High Volatility", "high_volatility", "volatility 高于 40% 的对象。"),
        ("Missing Data", "missing_data", "存在 Incomplete 状态的对象。"),
        ("Unavailable", "unavailable", "存在 Unavailable 状态的对象。"),
    ]
    tabs = st.tabs([label for label, _, _ in groups])
    for tab, (label, key, caption) in zip(tabs, groups):
        with tab:
            table = tables[key]
            render_metric_card(label, len(table), caption)
            if table.empty:
                st.info(f"当前没有 {label} 对象。")
            else:
                st.dataframe(_format_risk_table(table), hide_index=True, use_container_width=True)
    return tables


def render_compare_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Render 2-5 stock comparison panel."""
    source = safe_copy_frame(df)
    render_section_title("Compare Panel", "选择 2-5 个研究对象进行横向对比。")
    if source.empty or "ticker" not in source.columns:
        st.info("当前没有可对比的研究对象。")
        return build_compare_frame(source)

    options = [str(value) for value in source["ticker"].dropna().tolist()]
    default = options[: min(2, len(options))]
    selected = st.multiselect("选择 2-5 只股票进行对比", options=options, default=default, max_selections=5)
    if len(selected) < 2:
        st.info("请选择至少 2 个研究对象。")
    table = build_compare_frame(source, selected)
    render_compare_table(table[existing_columns(table, COMPARE_FIELDS)])
    return table


def render_report_preview(row: pd.Series | None) -> str:
    """Render read-only single-stock research report preview."""
    render_section_title("Research Report Preview", "报告仅基于已有字段生成，只读展示，不包含操作性结论。")
    if row is None:
        st.info("当前没有可生成报告预览的研究对象。")
        return ""
    report = build_stock_research_report(row)
    render_report_block(report)
    with st.expander("纯文本报告", expanded=False):
        st.text_area("只读研究报告预览", value=report, height=360, disabled=True)
    return report


def render_research_terminal(df: pd.DataFrame) -> dict[str, object]:
    """Render the complete visual Research Terminal from existing result fields."""
    source = safe_copy_frame(df)
    st.markdown(get_terminal_css(), unsafe_allow_html=True)
    render_terminal_header(
        TERMINAL_VERSION,
        TERMINAL_STAGE,
        "卡片化、仪表盘化、报告化的个人股票研究终端；所有展示均来自现有只读研究字段。",
    )

    dashboard = render_dashboard(source)
    tabs = st.tabs(["Top Picks", "个股详情", "风险中心", "多股对比", "报告预览"])

    selected_row = None
    selected_ticker = None
    if not source.empty and "ticker" in source.columns:
        tickers = [str(value) for value in source["ticker"].dropna().tolist()]
        if tickers:
            selected_ticker = st.selectbox("选择研究对象", options=tickers, index=0)

    with tabs[0]:
        top_picks = render_top_picks(source)
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
