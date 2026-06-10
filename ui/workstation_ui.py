"""Research Workstation UI for professional read-only research review."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from ui.report_builder import build_stock_research_report
from ui.workstation_components import (
    MISSING,
    format_value,
    render_compare_table,
    render_metric_card,
    render_quality_badge,
    render_report_block,
    render_risk_card,
    render_score_bar,
    render_status_badge,
    render_stock_card,
    safe_copy_frame,
    safe_get,
)
from ui.workstation_theme import (
    WORKSTATION_STAGE,
    WORKSTATION_VERSION,
    badge_html,
    get_workstation_css,
    render_workstation_header,
    render_workstation_section,
    risk_tone,
    status_tone,
)


NAVIGATOR_GROUPS = [
    ("CORE", "Core"),
    ("WATCH", "Watch"),
    ("EXCLUDED", "Exclude"),
]

SCORE_FIELDS = [
    "fundamental_score",
    "technical_score",
    "composite_score",
    "selection_score",
]

RISK_FIELDS = [
    "risk_score",
    "risk_level",
    "drawdown_risk_level",
    "volatility_risk_level",
    "return_risk_ratio",
    "max_drawdown",
    "volatility",
]

BACKTEST_FIELDS = [
    "period_return",
    "annualized_return",
    "win_rate",
    "max_drawdown",
    "volatility",
    "holding_period_days",
]

COMPARE_FIELDS = [
    "ticker",
    "name",
    "selection_score",
    "risk_score",
    "annualized_return",
    "max_drawdown",
    "selection_bucket",
    "selection_quality_label",
]

PIPELINE_FIELDS = [
    ("Universe", "universe_status"),
    ("Fundamental", "fundamental_screening_status"),
    ("Technical", "technical_screening_status"),
    ("Composite", "composite_screening_status"),
    ("Candidate Pool", "candidate_status"),
    ("Backtest Foundation", "backtest_status"),
    ("Return Analysis", "return_analysis_status"),
    ("Backtest Evaluation", "backtest_evaluation_status"),
    ("Stock Selection", "selection_status"),
    ("Explain Engine", "explain_status"),
]


def build_dashboard_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Build the workstation dashboard metrics without mutating input."""
    source = safe_copy_frame(df)
    if source.empty:
        return {
            "average_score": None,
            "core_candidates": 0,
            "average_return": None,
            "average_risk_score": None,
            "candidate_count": 0,
            "watch_count": 0,
        }
    bucket = source["selection_bucket"] if "selection_bucket" in source.columns else pd.Series([""] * len(source))
    return {
        "average_score": source["selection_score"].mean() if "selection_score" in source.columns else None,
        "core_candidates": int(bucket.eq("Core").sum()),
        "average_return": source["annualized_return"].mean() if "annualized_return" in source.columns else None,
        "average_risk_score": source["risk_score"].mean() if "risk_score" in source.columns else None,
        "candidate_count": int(len(source)),
        "watch_count": int(bucket.eq("Watch").sum()),
    }


def build_navigator_groups(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Group research objects into CORE, WATCH, and EXCLUDED."""
    source = safe_copy_frame(df)
    result: dict[str, pd.DataFrame] = {}
    if source.empty:
        return {label: source.copy(deep=True) for label, _ in NAVIGATOR_GROUPS}
    bucket = source["selection_bucket"] if "selection_bucket" in source.columns else source.get("candidate_pool")
    if bucket is None:
        bucket = pd.Series([""] * len(source), index=source.index)
    for label, bucket_name in NAVIGATOR_GROUPS:
        if label == "EXCLUDED":
            mask = bucket.isin(["Exclude", "Excluded", "Unavailable"])
        else:
            mask = bucket.eq(bucket_name)
        result[label] = source[mask].copy(deep=True)
    return result


def select_initial_ticker(df: pd.DataFrame) -> str:
    """Return the first available ticker or an empty string."""
    source = safe_copy_frame(df)
    if source.empty or "ticker" not in source.columns:
        return ""
    values = [str(value) for value in source["ticker"].dropna().tolist()]
    return values[0] if values else ""


def get_selected_row(df: pd.DataFrame, selected_ticker: str = "") -> pd.Series | None:
    """Return selected row with safe fallback to first row."""
    source = safe_copy_frame(df)
    if source.empty:
        return None
    if selected_ticker and "ticker" in source.columns:
        matched = source[source["ticker"].astype(str).eq(str(selected_ticker))]
        if not matched.empty:
            return matched.iloc[0].copy(deep=True)
    return source.iloc[0].copy(deep=True)


def build_factor_breakdown(row: pd.Series | None) -> dict[str, str]:
    """Convert explain factor breakdown into five visible panels."""
    factor = safe_get(row, "selection_factor_breakdown", {})
    if not isinstance(factor, dict):
        factor = {}
    return {
        "Fundamental": format_value(factor.get("fundamental_score", safe_get(row, "fundamental_score"))),
        "Technical": format_value(factor.get("technical_score", safe_get(row, "technical_score"))),
        "Backtest": format_value(factor.get("return_risk_ratio", safe_get(row, "return_risk_ratio"))),
        "Risk": format_value(factor.get("risk_score", safe_get(row, "risk_score"))),
        "Quality": format_value(factor.get("selection_quality_label", safe_get(row, "selection_quality_label"))),
    }


def build_compare_workspace(df: pd.DataFrame, tickers: list[str] | None = None) -> pd.DataFrame:
    """Build workstation compare table for 2-5 stocks."""
    source = safe_copy_frame(df)
    columns = [column for column in COMPARE_FIELDS if column in source.columns]
    if source.empty or not columns:
        return pd.DataFrame(columns=columns)
    filtered = source
    if tickers and "ticker" in source.columns:
        filtered = source[source["ticker"].astype(str).isin([str(ticker) for ticker in tickers[:5]])]
    display = filtered[columns].copy(deep=True)
    for column in display.columns:
        display[column] = display[column].map(lambda value, field=column: format_value(value, field))
    return display.replace("", MISSING).fillna(MISSING)


def build_pipeline_status(row: pd.Series | None) -> list[dict[str, str]]:
    """Build full research pipeline status from row fields."""
    result = []
    for label, field in PIPELINE_FIELDS:
        value = safe_get(row, field)
        if value in {"Available", "Selected", "Watch", "Pass", "Completed", "Good", "Strong"}:
            status = "Completed"
        elif value in {MISSING, "Unavailable", "Incomplete"}:
            status = "Unavailable"
        else:
            status = "Completed"
        result.append({"stage": label, "status": status})
    return result


def render_research_navigator(df: pd.DataFrame, selected_ticker: str) -> str:
    """Render left-side navigator with grouped object buttons."""
    groups = build_navigator_groups(df)
    current = selected_ticker
    render_workstation_section("Research Navigator", "按 selection_bucket 自动分组。")
    for label, group in groups.items():
        st.caption(label)
        if group.empty:
            st.info("No objects")
            continue
        for _, row in group.iterrows():
            ticker = str(safe_get(row, "ticker", safe_get(row, "symbol")))
            render_stock_card(row, selected=ticker == current)
            if st.button(f"{safe_get(row, 'name', ticker)} | {ticker}", key=f"nav_{label}_{ticker}"):
                st.session_state["workstation_selected_ticker"] = ticker
                current = ticker
    return current


def render_dashboard_cards(metrics: dict[str, Any]) -> None:
    """Render four workstation metric cards."""
    columns = st.columns(4)
    cards = [
        ("Average Score", metrics["average_score"], "Mean selection_score"),
        ("Core Candidates", metrics["core_candidates"], "Objects in CORE"),
        ("Average Return", metrics["average_return"], "Mean annualized_return"),
        ("Average Risk Score", metrics["average_risk_score"], "Mean risk_score"),
    ]
    for column, (title, value, caption) in zip(columns, cards):
        with column:
            render_metric_card(title, value, caption)


def render_main_research_area(row: pd.Series | None) -> None:
    """Render central object overview and explain engine display."""
    render_workstation_section("Main Research Area", "核心研究对象概览与 Explain Engine 展示。")
    if row is None:
        st.info("No research object is available.")
        return
    ticker = format_value(safe_get(row, "ticker", safe_get(row, "symbol")))
    name = format_value(safe_get(row, "name", "Research Object"))
    st.markdown(f'<div class="fsw-stock-title">{name} <span class="fsw-muted">{ticker}</span></div>', unsafe_allow_html=True)

    cols = st.columns(4)
    cols[0].metric("selection_score", format_value(safe_get(row, "selection_score")))
    cols[1].metric("selection_rank", format_value(safe_get(row, "selection_rank")))
    cols[2].markdown(badge_html(safe_get(row, "selection_bucket"), status_tone(safe_get(row, "selection_bucket"))), unsafe_allow_html=True)
    cols[3].markdown(badge_html(safe_get(row, "risk_level"), risk_tone(safe_get(row, "risk_level"))), unsafe_allow_html=True)

    badge_cols = st.columns(4)
    with badge_cols[0]:
        render_status_badge(safe_get(row, "selection_level"))
    with badge_cols[1]:
        render_status_badge(safe_get(row, "selection_quality_label"))
    with badge_cols[2]:
        render_quality_badge(safe_get(row, "backtest_quality_label"))
    with badge_cols[3]:
        render_status_badge(safe_get(row, "selection_status"))

    st.markdown('<div class="fsw-divider"></div>', unsafe_allow_html=True)
    st.subheader("Investment Thesis")
    st.write(format_value(safe_get(row, "selection_thesis")))
    st.markdown("---")
    st.subheader("Strengths")
    st.write(format_value(safe_get(row, "selection_strengths")))
    st.markdown("---")
    st.subheader("Risks")
    st.write(format_value(safe_get(row, "selection_risks")))
    st.markdown("---")
    st.subheader("Factor Breakdown")
    factor_cols = st.columns(5)
    for column, (label, value) in zip(factor_cols, build_factor_breakdown(row).items()):
        with column:
            render_metric_card(label, value, "Explain context")


def render_score_breakdown_center(row: pd.Series | None) -> None:
    """Render bottom score breakdown center."""
    render_workstation_section("Score Breakdown Center", "水平进度条展示当前值、最大值和贡献比例。")
    for field in SCORE_FIELDS:
        render_score_bar(field, safe_get(row, field))


def render_risk_center(row: pd.Series | None) -> None:
    """Render workstation risk center."""
    render_workstation_section("Risk Center", "Low / Medium / High 颜色规则用于风险识别。")
    cards = [
        ("risk_score", safe_get(row, "risk_score"), safe_get(row, "risk_level")),
        ("risk_level", safe_get(row, "risk_level"), safe_get(row, "risk_level")),
        ("drawdown_risk_level", safe_get(row, "drawdown_risk_level"), safe_get(row, "drawdown_risk_level")),
        ("volatility_risk_level", safe_get(row, "volatility_risk_level"), safe_get(row, "volatility_risk_level")),
        ("return_risk_ratio", safe_get(row, "return_risk_ratio"), safe_get(row, "risk_level")),
        ("max_drawdown", safe_get(row, "max_drawdown"), safe_get(row, "drawdown_risk_level")),
        ("volatility", safe_get(row, "volatility"), safe_get(row, "volatility_risk_level")),
    ]
    for start in range(0, len(cards), 4):
        columns = st.columns(4)
        for column, (title, value, level) in zip(columns, cards[start : start + 4]):
            with column:
                render_risk_card(title, value, level)


def render_backtest_center(row: pd.Series | None) -> None:
    """Render backtest center cards."""
    render_workstation_section("Backtest Center", "展示已有历史指标，缺失值统一显示为 —。")
    for start in range(0, len(BACKTEST_FIELDS), 3):
        columns = st.columns(3)
        for column, field in zip(columns, BACKTEST_FIELDS[start : start + 3]):
            with column:
                render_metric_card(field, safe_get(row, field), "Historical metric")


def render_compare_workspace(df: pd.DataFrame) -> pd.DataFrame:
    """Render 2-5 stock comparison workspace."""
    source = safe_copy_frame(df)
    render_workstation_section("Compare Workspace", "支持 2-5 只股票横向比较。")
    if source.empty or "ticker" not in source.columns:
        table = build_compare_workspace(source)
        render_compare_table(table)
        return table
    options = [str(value) for value in source["ticker"].dropna().tolist()]
    default = options[: min(2, len(options))]
    selected = st.multiselect("Select 2-5 research objects", options=options, default=default, max_selections=5)
    table = build_compare_workspace(source, selected)
    render_compare_table(table)
    return table


def render_research_pipeline(row: pd.Series | None) -> list[dict[str, str]]:
    """Render full research pipeline."""
    pipeline = build_pipeline_status(row)
    render_workstation_section("Research Pipeline", "完整研究流程状态视图。")
    for item in pipeline:
        st.markdown(
            f"{badge_html(item['stage'], 'info')} -> {badge_html(item['status'], status_tone(item['status']))}",
            unsafe_allow_html=True,
        )
    return pipeline


def render_thesis_panel(row: pd.Series | None) -> str:
    """Render right-side thesis and report preview panel."""
    render_workstation_section("Thesis Panel", "Research Report Preview")
    if row is None:
        st.info("No report preview is available.")
        return ""
    report = build_stock_research_report(row)
    render_report_block(report)
    return report


def render_research_workstation(df: pd.DataFrame) -> dict[str, Any]:
    """Render the complete Research Workstation."""
    source = safe_copy_frame(df)
    metrics = build_dashboard_metrics(source)
    initial = select_initial_ticker(source)
    current = st.session_state.get("workstation_selected_ticker", initial)
    selected_row = get_selected_row(source, current)
    selected_name = format_value(safe_get(selected_row, "name", safe_get(selected_row, "ticker", "Research Object")))

    st.markdown(get_workstation_css(), unsafe_allow_html=True)
    render_workstation_header(
        selected_name,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        metrics["candidate_count"],
        metrics["core_candidates"],
        metrics["watch_count"],
        format_value(metrics["average_score"]),
    )
    render_dashboard_cards(metrics)

    left, center, right = st.columns([2, 5.5, 2.5])
    with left:
        current = render_research_navigator(source, current)
    selected_row = get_selected_row(source, current)
    with center:
        render_main_research_area(selected_row)
    with right:
        report = render_thesis_panel(selected_row)

    render_score_breakdown_center(selected_row)
    render_risk_center(selected_row)
    render_backtest_center(selected_row)
    compare = render_compare_workspace(source)
    pipeline = render_research_pipeline(selected_row)

    return {
        "metrics": metrics,
        "selected_row": selected_row,
        "compare": compare,
        "pipeline": pipeline,
        "report": report,
    }


__all__ = [
    "BACKTEST_FIELDS",
    "COMPARE_FIELDS",
    "PIPELINE_FIELDS",
    "RISK_FIELDS",
    "SCORE_FIELDS",
    "WORKSTATION_STAGE",
    "WORKSTATION_VERSION",
    "build_compare_workspace",
    "build_dashboard_metrics",
    "build_factor_breakdown",
    "build_navigator_groups",
    "build_pipeline_status",
    "get_selected_row",
    "render_backtest_center",
    "render_compare_workspace",
    "render_dashboard_cards",
    "render_main_research_area",
    "render_research_navigator",
    "render_research_pipeline",
    "render_research_workstation",
    "render_risk_center",
    "render_score_breakdown_center",
    "render_thesis_panel",
    "select_initial_ticker",
]
