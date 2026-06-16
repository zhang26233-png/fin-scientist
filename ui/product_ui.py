"""Product-level Streamlit UI for the integrated quant research platform."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from data.source_center import build_data_source_status
from factor.factor_lab import DEFAULT_FACTOR_COLUMNS, build_factor_dataset
from factor.factor_report import build_factor_research_report
from ui.chart_center import (
    render_candidate_ranking_bar,
    render_drawdown_risk_view,
    render_return_risk_scatter,
    render_score_breakdown_bar,
)
from ui.report_builder import build_stock_research_report
from ui.workstation_components import MISSING, format_value, safe_copy_frame, safe_get
from ui.workstation_theme import badge_html, get_workstation_css, status_tone
from ui.workstation_ui import render_research_workstation


PRODUCT_VERSION = "v6.8.0"
PRODUCT_STAGE = "Full Capital Flow Engine"

DASHBOARD_PAGE = "首页总览 Dashboard"
UNIVERSE_PAGE = "全A股票池"
SELECTION_PAGE = "选股结果"
WORKSTATION_PAGE = "个股研究工作台"
BACKTEST_PAGE = "回测分析"
CHART_PAGE = "图表中心"
FACTOR_PAGE = "因子研究实验室"
REPORT_PAGE = "研究报告预览"
SYSTEM_PAGE = "系统状态 / 数据质量"
DATA_SOURCE_PAGE = "数据源中心"
SCREENING_PIPELINE_PAGE = "筛选流水线"
LEGACY_PAGE = "旧版研究工作台"

NAVIGATION_PAGES = [
    DASHBOARD_PAGE,
    UNIVERSE_PAGE,
    SELECTION_PAGE,
    WORKSTATION_PAGE,
    BACKTEST_PAGE,
    CHART_PAGE,
    FACTOR_PAGE,
    REPORT_PAGE,
    SYSTEM_PAGE,
    DATA_SOURCE_PAGE,
    SCREENING_PIPELINE_PAGE,
    LEGACY_PAGE,
]

REQUIRED_FIELD_GROUPS = {
    "Universe": ["ticker", "name", "market", "list_date", "is_st", "is_suspended", "universe_status"],
    "Fundamental": ["fundamental_score", "fundamental_level", "fundamental_screening_status"],
    "Technical": ["technical_score", "technical_level", "technical_screening_status"],
    "Composite": ["composite_score", "composite_level", "composite_screening_status"],
    "Candidate Pool": ["candidate_pool", "candidate_rank", "candidate_status"],
    "Backtest Foundation": ["backtest_available", "backtest_status"],
    "Return Analysis": ["period_return", "annualized_return", "volatility", "max_drawdown", "win_rate"],
    "Backtest Evaluation": ["risk_score", "risk_level", "return_risk_ratio", "performance_label"],
    "Stock Selection": ["selection_score", "selection_bucket", "selection_status", "selection_rank"],
    "Research Score Activation": [
        "quote_available",
        "quote_quality_score",
        "liquidity_score",
        "momentum_score",
        "price_position_score",
        "activated_technical_score",
        "activated_fundamental_score",
        "activated_composite_score",
        "activated_selection_score",
        "activated_research_bucket",
        "activated_research_status",
        "activated_research_level",
    ],
    "Real Technical Indicator Engine": [
        "technical_history_available",
        "technical_history_days",
        "real_technical_score",
        "technical_trend_score",
        "technical_momentum_score",
        "technical_volume_score",
        "technical_volatility_score",
        "technical_position_score",
        "macd_signal",
        "rsi14",
        "position_52w",
        "technical_signal_summary",
        "technical_risk_flags",
    ],
    "Fundamental Research Engine": [
        "fundamental_available",
        "fundamental_research_score",
        "fundamental_data_source",
        "fundamental_data_status",
        "fundamental_updated_at",
        "valuation_score",
        "profitability_score",
        "growth_score",
        "financial_quality_score",
        "pe_ttm",
        "pb",
        "roe",
        "net_profit_growth_yoy",
        "fundamental_summary",
        "fundamental_warnings",
    ],
    "Capital Flow": ["capital_flow_score", "capital_flow_strength", "capital_flow_rank", "capital_activity_score", "turnover_rate", "volume_ratio", "main_net_inflow", "capital_flow_warning"],
    "News Event": ["news_event_score", "news_sentiment_label", "news_title", "news_source"],
    "Industry Concept": ["industry", "concepts", "industry_strength_score", "concept_heat_score"],
    "Explainable Selection": ["selection_thesis", "selection_strengths", "selection_risks", "selection_explanation"],
    "Factor Research Lab": ["factor_name", "factor_ic", "factor_rank_ic", "factor_effectiveness_label"],
}

UNIVERSE_COLUMNS = ["ticker", "name", "market", "industry", "list_date", "status", "universe_status"]
SELECTION_COLUMNS = [
    "ticker",
    "name",
    "latest_price",
    "pct_change",
    "turnover",
    "capital_flow_score",
    "capital_flow_strength",
    "capital_flow_rank",
    "capital_activity_score",
    "turnover_rate",
    "volume_ratio",
    "main_net_inflow",
    "main_net_inflow_ratio",
    "northbound_change",
    "capital_flow_summary",
    "capital_flow_warning",
    "news_event_score",
    "news_sentiment_label",
    "news_title",
    "industry",
    "concepts",
    "industry_strength_score",
    "concept_heat_score",
    "activated_fundamental_score",
    "activated_selection_score",
    "activated_research_bucket",
    "activated_research_status",
    "activated_research_level",
    "activated_research_reasons",
    "activated_research_warnings",
    "technical_history_available",
    "technical_history_days",
    "real_technical_score",
    "rsi14",
    "macd_signal",
    "ma20",
    "ma60",
    "return_20d",
    "return_60d",
    "position_52w",
    "technical_risk_flags",
    "technical_trend_score",
    "technical_momentum_score",
    "technical_volume_score",
    "technical_volatility_score",
    "technical_position_score",
    "technical_signal_summary",
    "fundamental_research_score",
    "valuation_score",
    "profitability_score",
    "growth_score",
    "financial_quality_score",
    "pe_ttm",
    "pb",
    "roe",
    "roa",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "debt_to_asset",
    "fundamental_summary",
    "fundamental_warnings",
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
STOCK_DETAIL_FIELDS = [
    "ticker",
    "name",
    "fundamental_score",
    "technical_score",
    "composite_score",
    "candidate_pool",
    "candidate_status",
    "period_return",
    "annualized_return",
    "risk_score",
    "risk_level",
    "selection_thesis",
    "selection_strengths",
    "selection_risks",
    "selection_explanation",
    "real_technical_score",
    "technical_trend_score",
    "technical_momentum_score",
    "technical_volume_score",
    "technical_volatility_score",
    "technical_position_score",
    "macd_signal",
    "rsi14",
    "position_52w",
    "technical_signal_summary",
    "technical_risk_flags",
    "fundamental_research_score",
    "fundamental_data_source",
    "fundamental_data_status",
    "fundamental_updated_at",
    "valuation_score",
    "profitability_score",
    "growth_score",
    "financial_quality_score",
    "pe_ttm",
    "pb",
    "roe",
    "roa",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "debt_to_asset",
    "fundamental_summary",
    "fundamental_strengths",
    "fundamental_risks",
    "fundamental_warnings",
    "capital_flow_score",
    "capital_flow_rank",
    "capital_flow_strength",
    "capital_activity_score",
    "turnover_rate",
    "volume_ratio",
    "main_net_inflow",
    "main_net_inflow_ratio",
    "capital_flow_summary",
    "capital_flow_warning",
    "capital_flow_warnings",
    "news_event_score",
    "news_sentiment_label",
    "news_title",
    "news_summary",
    "news_warning",
    "industry",
    "concepts",
    "industry_strength_score",
    "concept_heat_score",
]


def get_navigation_pages() -> list[str]:
    """Return stable product navigation entries."""
    return list(NAVIGATION_PAGES)


def _state_frame(state: dict[str, Any] | None, key: str) -> pd.DataFrame:
    if not isinstance(state, dict):
        return pd.DataFrame()
    return safe_copy_frame(state.get(key))


def get_product_state() -> dict[str, pd.DataFrame]:
    """Read product data frames from session state with safe empty fallbacks."""
    state = st.session_state.get("fin_scientist_product_state", {})
    research_df = safe_copy_frame(st.session_state.get("research_df"))
    if not research_df.empty:
        return {
            "universe": research_df,
            "fundamental": research_df,
            "technical": research_df,
            "composite": research_df,
            "candidate_pool": research_df,
            "backtest_foundation": research_df,
            "return_analysis": research_df,
            "backtest_evaluation": research_df,
            "stock_selection": research_df,
            "explainable_selection": research_df,
        }
    return {
        "universe": _state_frame(state, "universe"),
        "fundamental": _state_frame(state, "fundamental"),
        "technical": _state_frame(state, "technical"),
        "composite": _state_frame(state, "composite"),
        "candidate_pool": _state_frame(state, "candidate_pool"),
        "backtest_foundation": _state_frame(state, "backtest_foundation"),
        "return_analysis": _state_frame(state, "return_analysis"),
        "backtest_evaluation": _state_frame(state, "backtest_evaluation"),
        "stock_selection": _state_frame(state, "stock_selection"),
        "explainable_selection": _state_frame(state, "explainable_selection"),
    }


def set_product_state(**frames: Any) -> None:
    """Store product pipeline frames for navigation pages."""
    current = st.session_state.get("fin_scientist_product_state", {})
    next_state = dict(current) if isinstance(current, dict) else {}
    for key, value in frames.items():
        next_state[key] = safe_copy_frame(value)
    st.session_state["fin_scientist_product_state"] = next_state


def primary_research_frame(state: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    """Choose the richest available research frame without mutating inputs."""
    session_research = safe_copy_frame(st.session_state.get("research_df"))
    if not session_research.empty:
        return session_research
    data = state or get_product_state()
    for key in ["explainable_selection", "stock_selection", "backtest_evaluation", "return_analysis", "candidate_pool", "universe"]:
        frame = safe_copy_frame(data.get(key))
        if not frame.empty:
            return frame
    return pd.DataFrame()


def _metric_value(df: pd.DataFrame, field: str) -> Any:
    if df.empty or field not in df.columns:
        return None
    return pd.to_numeric(df[field], errors="coerce").mean()


def _has_nonempty_value(value: Any) -> bool:
    if isinstance(value, list):
        return any(bool(item) for item in value)
    if isinstance(value, tuple) or isinstance(value, set):
        return any(bool(item) for item in value)
    if value is None:
        return False
    if pd.isna(value):
        return False
    return bool(str(value).strip())


def _first_available_field(df: pd.DataFrame, fields: list[str]) -> str | None:
    for field in fields:
        if field in df.columns:
            return field
    return None


def build_dashboard_summary(df: Any) -> dict[str, Any]:
    """Build product dashboard metrics from the current research frame."""
    source = safe_copy_frame(df)
    bucket_field = _first_available_field(source, ["activated_research_bucket", "selection_bucket"])
    selection_score_field = _first_available_field(source, ["activated_selection_score", "selection_score"])
    composite_score_field = _first_available_field(source, ["activated_composite_score", "composite_score"])
    if source.empty:
        bucket = pd.Series(dtype=object)
    elif bucket_field:
        bucket = source[bucket_field].fillna("")
    else:
        bucket = pd.Series([""] * len(source), index=source.index)
    warnings = collect_warning_fields(source)
    technical_history_count = (
        int(source["technical_history_available"].fillna(False).astype(bool).sum())
        if "technical_history_available" in source.columns
        else 0
    )
    technical_high_risk_count = (
        int(source["technical_risk_flags"].map(_has_nonempty_value).sum())
        if "technical_risk_flags" in source.columns
        else 0
    )
    fundamental_available_count = (
        int(source["fundamental_available"].fillna(False).astype(bool).sum())
        if "fundamental_available" in source.columns
        else 0
    )
    source_status = build_data_source_status(source)
    capital_flow_coverage = (
        int(pd.to_numeric(source["capital_flow_score"], errors="coerce").notna().sum())
        if "capital_flow_score" in source.columns
        else 0
    )
    capital_strength = source["capital_flow_strength"].fillna("") if "capital_flow_strength" in source.columns else pd.Series([""] * len(source), index=source.index)
    return {
        "total_count": int(len(source)),
        "universe_size": int(source.attrs.get("universe_size", len(source))) if hasattr(source, "attrs") else int(len(source)),
        "core_count": int(bucket.eq("Core").sum()),
        "watch_count": int(bucket.eq("Watch").sum()),
        "exclude_count": int(bucket.isin(["Exclude", "Excluded"]).sum()),
        "average_selection_score": _metric_value(source, selection_score_field) if selection_score_field else None,
        "average_composite_score": _metric_value(source, composite_score_field) if composite_score_field else None,
        "average_real_technical_score": _metric_value(source, "real_technical_score"),
        "technical_history_available_count": technical_history_count,
        "technical_high_risk_count": technical_high_risk_count,
        "average_fundamental_research_score": _metric_value(source, "fundamental_research_score"),
        "fundamental_available_count": fundamental_available_count,
        "average_pe_ttm": _metric_value(source, "pe_ttm"),
        "average_pb": _metric_value(source, "pb"),
        "average_roe": _metric_value(source, "roe"),
        "average_revenue_growth_yoy": _metric_value(source, "revenue_growth_yoy"),
        "average_net_profit_growth_yoy": _metric_value(source, "net_profit_growth_yoy"),
        "fundamental_data_source": source.attrs.get("fundamental_data_source", "Unavailable") if hasattr(source, "attrs") else "Unavailable",
        "fundamental_data_status": source.attrs.get("fundamental_data_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable",
        "capital_flow_status": source.attrs.get("capital_flow_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable",
        "news_status": source.attrs.get("news_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable",
        "industry_status": source.attrs.get("industry_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable",
        "source_status_count": len(source_status),
        "source_available_count": int(source_status["status"].isin(["Live", "Available", "Cache"]).sum()) if not source_status.empty else 0,
        "average_capital_flow_score": _metric_value(source, "capital_flow_score"),
        "capital_flow_coverage_count": capital_flow_coverage,
        "capital_flow_coverage_rate": round(capital_flow_coverage / len(source) * 100, 2) if len(source) else 0,
        "average_main_net_inflow": _metric_value(source, "main_net_inflow"),
        "average_northbound_change": _metric_value(source, "northbound_change"),
        "strong_capital_flow_count": int(capital_strength.isin(["Strong Buy Research", "Strong"]).sum()),
        "weak_capital_flow_count": int(capital_strength.isin(["Weak", "Very Weak"]).sum()),
        "average_news_event_score": _metric_value(source, "news_event_score"),
        "average_industry_strength_score": _metric_value(source, "industry_strength_score"),
        "average_concept_heat_score": _metric_value(source, "concept_heat_score"),
        "kline_cache_hits": int(source.attrs.get("kline_cache_hits", 0)) if hasattr(source, "attrs") else 0,
        "kline_failures": int(source.attrs.get("kline_failures", 0)) if hasattr(source, "attrs") else 0,
        "average_risk_score": _metric_value(source, "risk_score"),
        "factor_count": len([field for field in DEFAULT_FACTOR_COLUMNS if field in source.columns]),
        "backtest_available_count": int(source["backtest_available"].fillna(False).sum()) if "backtest_available" in source.columns else 0,
        "incomplete_count": len(warnings),
    }


def collect_warning_fields(df: Any) -> list[str]:
    """Collect warning-like fields and incomplete status notes."""
    source = safe_copy_frame(df)
    if source.empty:
        return []
    results: list[str] = []
    for _, row in source.iterrows():
        ticker = format_value(safe_get(row, "ticker", safe_get(row, "symbol", "Object")))
        for column in source.columns:
            lower = column.lower()
            value = row.get(column)
            if "warning" in lower or "warnings" in lower or "risk_notes" in lower:
                if isinstance(value, list):
                    results.extend(f"{ticker}: {item}" for item in value if item)
                elif isinstance(value, str) and value.strip():
                    results.append(f"{ticker}: {value}")
            if lower.endswith("status") and str(value) in {"Incomplete", "Unavailable"}:
                results.append(f"{ticker}: {column} = {value}")
    return results


def find_missing_fields(df: Any) -> dict[str, list[str]]:
    """Return missing fields by module group."""
    source = safe_copy_frame(df)
    return {
        group: [field for field in fields if field not in source.columns]
        for group, fields in REQUIRED_FIELD_GROUPS.items()
    }


def _format_display_table(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    source = safe_copy_frame(df)
    available = [column for column in columns if column in source.columns]
    if not available:
        return pd.DataFrame(columns=columns)
    display = source[available].copy(deep=True)
    for column in display.columns:
        display[column] = display[column].map(lambda value, field=column: format_value(value, field))
    return display.replace("", MISSING).fillna(MISSING)


def _render_metric_card(title: str, value: Any, caption: str = "") -> None:
    st.markdown(
        f"""
<div class="fsw-card">
  <div class="fsw-metric-label">{title}</div>
  <div class="fsw-metric-value">{format_value(value)}</div>
  <div class="fsw-muted">{caption}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_page_header(title: str, caption: str) -> None:
    st.markdown(get_workstation_css(), unsafe_allow_html=True)
    st.title(title)
    st.caption(f"{PRODUCT_VERSION} {PRODUCT_STAGE} | {caption} | 仅供学习和研究，不构成投资建议。")


def _render_empty_notice(module_name: str) -> None:
    st.info(f"{module_name} 当前没有可展示数据。页面结构已保留，运行筛选流水线后会显示对应结果。")


def _render_table(df: pd.DataFrame, columns: list[str], empty_module: str) -> pd.DataFrame:
    table = _format_display_table(df, columns)
    if table.empty:
        _render_empty_notice(empty_module)
    st.dataframe(table, hide_index=True, use_container_width=True)
    return table


def render_dashboard_page(df: Any) -> dict[str, Any]:
    """Render product dashboard cards."""
    source = safe_copy_frame(df)
    _render_page_header("首页总览 Dashboard", "研究对象、选股结果、风险和因子状态总览")
    summary = build_dashboard_summary(source)
    data_source = source.attrs.get("data_source", "Unavailable") if hasattr(source, "attrs") else "Unavailable"
    data_status = source.attrs.get("data_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable"
    load_time = source.attrs.get("load_time", 0) if hasattr(source, "attrs") else 0
    updated_at = source.attrs.get("updated_at", "—") if hasattr(source, "attrs") else "—"
    last_error = source.attrs.get("last_error", "") if hasattr(source, "attrs") else ""
    raw_count = source.attrs.get("raw_count", len(source)) if hasattr(source, "attrs") else len(source)
    filtered_count = source.attrs.get("filtered_count", 0) if hasattr(source, "attrs") else 0
    cache_status = source.attrs.get("cache_status", "Missing") if hasattr(source, "attrs") else "Missing"
    cache_updated_at = source.attrs.get("cache_updated_at", "—") if hasattr(source, "attrs") else "—"
    status_text = (
        f"当前数据源：{data_source} / {data_status} / 股票数量：{summary['universe_size']} / "
        f"原始数量：{raw_count} / 过滤数量：{filtered_count} / "
        f"缓存：{cache_status} / 缓存更新时间：{cache_updated_at or '—'} / "
        f"加载时间：{load_time} 秒 / 更新时间：{updated_at}"
    )
    if data_status == "Live":
        st.success(status_text)
    elif data_status == "Cache":
        st.info(status_text)
    elif data_status == "Fallback":
        st.warning(status_text)
    else:
        st.error(f"{status_text} / 最近错误：{last_error}")
    if summary["universe_size"] < 1000:
        st.error("真实数据不足，仅用于结构验证。所有结果仅供学习和研究，不构成投资建议。")
    cards = [
        ("Universe Size", summary["universe_size"], "Current A-share universe size"),
        ("Raw Count", raw_count, "Realtime/cache raw rows"),
        ("Filtered Count", filtered_count, "Filtered rows removed"),
        ("Cache Status", cache_status, f"Updated: {cache_updated_at or '—'}"),
        ("总股票数", summary["total_count"], "当前研究样本数量"),
        ("Core 数量", summary["core_count"], "核心研究对象"),
        ("Watch 数量", summary["watch_count"], "观察研究对象"),
        ("Exclude 数量", summary["exclude_count"], "排除或不可用对象"),
        ("平均 activated_selection_score", summary["average_selection_score"], "激活后的研究分数均值"),
        ("平均 activated_composite_score", summary["average_composite_score"], "激活后的综合研究分数均值"),
        ("平均 real_technical_score", summary["average_real_technical_score"], "真实技术指标研究分均值"),
        ("技术历史可用数量", summary["technical_history_available_count"], "历史行情可用的研究对象"),
        ("技术风险提示数量", summary["technical_high_risk_count"], "存在技术风险提示的对象"),
        ("平均 fundamental_research_score", summary["average_fundamental_research_score"], "基本面研究分均值"),
        ("Fundamental Data Source", summary["fundamental_data_source"], "基本面数据来源"),
        ("Fundamental Status", summary["fundamental_data_status"], "基本面数据状态"),
        ("基本面可用数量", summary["fundamental_available_count"], "基本面字段可用的研究对象"),
        ("平均 PE", summary["average_pe_ttm"], "PE TTM 均值"),
        ("平均 PB", summary["average_pb"], "PB 均值"),
        ("平均 ROE", summary["average_roe"], "ROE 均值"),
        ("平均营收增速", summary["average_revenue_growth_yoy"], "revenue_growth_yoy 均值"),
        ("平均净利润增速", summary["average_net_profit_growth_yoy"], "net_profit_growth_yoy 均值"),
        ("平均资金分", summary["average_capital_flow_score"], "capital_flow_score 均值"),
        ("资金覆盖率", f"{summary['capital_flow_coverage_rate']}%", f"覆盖 {summary['capital_flow_coverage_count']} 个对象"),
        ("主力净流入均值", summary["average_main_net_inflow"], "main_net_inflow 均值"),
        ("北向资金均值", summary["average_northbound_change"], "northbound_change 均值"),
        ("资金强势数量", summary["strong_capital_flow_count"], "Strong / Strong Buy Research"),
        ("资金弱势数量", summary["weak_capital_flow_count"], "Weak / Very Weak"),
        ("K线缓存命中", summary["kline_cache_hits"], "cache/kline 命中数量"),
        ("K线加载失败", summary["kline_failures"], "外部源和缓存均不可用数量"),
        ("平均 risk_score", summary["average_risk_score"], "风险评分均值"),
        ("因子数量", summary["factor_count"], "可识别默认因子数量"),
        ("可回测数量", summary["backtest_available_count"], "Backtest Foundation 可用数量"),
        ("数据不完整数量", summary["incomplete_count"], "warnings 与不可用状态汇总"),
    ]
    for start in range(0, len(cards), 5):
        columns = st.columns(5)
        for column, (title, value, caption) in zip(columns, cards[start : start + 5]):
            with column:
                _render_metric_card(title, value, caption)
    st.subheader("数据源总览")
    st.dataframe(build_data_source_status(source), hide_index=True, use_container_width=True)
    if source.empty:
        _render_empty_notice("Dashboard")
    return summary


def render_universe_page(df: Any) -> pd.DataFrame:
    """Render A-share Universe page with lightweight filters."""
    source = safe_copy_frame(df)
    _render_page_header("全A股票池", "Universe 股票池、ST、停牌和可用状态")
    filtered = source.copy(deep=True)
    if not filtered.empty:
        query = st.text_input("搜索股票 / 代码 / 名称", value="")
        if query.strip():
            keyword = query.strip()
            mask = pd.Series(False, index=filtered.index)
            for field in ["ticker", "name"]:
                if field in filtered.columns:
                    mask = mask | filtered[field].astype(str).str.contains(keyword, case=False, na=False)
            filtered = filtered[mask]
        if "market" in filtered.columns:
            markets = ["全部"] + sorted(str(value) for value in filtered["market"].dropna().unique())
            selected_market = st.selectbox("市场", options=markets)
            if selected_market != "全部":
                filtered = filtered[filtered["market"].astype(str).eq(selected_market)]
        for label, field in [("是否 ST", "is_st"), ("是否停牌", "is_suspended")]:
            if field in filtered.columns:
                selected = st.selectbox(label, options=["全部", "是", "否"])
                if selected != "全部":
                    filtered = filtered[filtered[field].astype(bool).eq(selected == "是")]
        if "universe_status" in filtered.columns:
            statuses = ["全部"] + sorted(str(value) for value in filtered["universe_status"].dropna().unique())
            selected_status = st.selectbox("是否可用", options=statuses)
            if selected_status != "全部":
                filtered = filtered[filtered["universe_status"].astype(str).eq(selected_status)]
    return _render_table(filtered, UNIVERSE_COLUMNS, "Universe")


def render_selection_page(df: Any) -> dict[str, pd.DataFrame]:
    """Render stock-selection result page."""
    source = safe_copy_frame(df)
    _render_page_header("选股结果", "Core、Watch、风险和数据缺失对象分组")
    display_source = source.copy(deep=True)
    sort_options = ["activated_selection_score", "capital_flow_score", "selection_score"]
    available_sort_options = [field for field in sort_options if field in display_source.columns]
    sort_field = available_sort_options[0] if available_sort_options else ""
    if available_sort_options:
        sort_field = st.selectbox("结果排序", options=available_sort_options, index=0)
    if sort_field:
        display_source = display_source.sort_values(
            by=sort_field,
            ascending=False,
            kind="mergesort",
        )
    table = _render_table(display_source, SELECTION_COLUMNS, "Stock Selection")
    bucket_field = _first_available_field(source, ["activated_research_bucket", "selection_bucket"])
    bucket = source[bucket_field] if bucket_field else pd.Series([""] * len(source), index=source.index)
    risk = source["risk_level"] if "risk_level" in source.columns else pd.Series([""] * len(source), index=source.index)
    warnings = collect_warning_fields(source)
    sections = {
        "top_core": source[bucket.eq("Core")].copy(deep=True),
        "top_watch": source[bucket.eq("Watch")].copy(deep=True),
        "risk_objects": source[risk.eq("High")].copy(deep=True),
        "missing_data": source.iloc[0:0].copy(deep=True),
    }
    if warnings and not source.empty:
        sections["missing_data"] = source.copy(deep=True)
    tabs = st.tabs(["Top Core", "Top Watch", "风险标的", "数据缺失标的"])
    for tab, (label, frame) in zip(tabs, sections.items()):
        with tab:
            _render_table(frame, SELECTION_COLUMNS, label)
    return {"table": table, **sections}


def render_stock_workstation_page(df: Any) -> dict[str, Any]:
    """Render single-stock research workstation page."""
    source = safe_copy_frame(df)
    _render_page_header("个股研究工作台", "单只股票研究详情、解释层和报告预览")
    if source.empty:
        _render_empty_notice("个股研究工作台")
        return {"selected_row": None, "report": ""}
    ticker_options = [str(value) for value in source.get("ticker", pd.Series(range(len(source)))).fillna("").tolist()]
    selected = st.selectbox("选择股票", options=ticker_options)
    row = source[source["ticker"].astype(str).eq(selected)].iloc[0] if "ticker" in source.columns else source.iloc[0]
    columns = st.columns(4)
    for column, field in zip(columns, ["ticker", "name", "selection_score", "selection_bucket"]):
        with column:
            _render_metric_card(field, safe_get(row, field), "股票基本信息")
    st.subheader("研究详情")
    detail = _format_display_table(pd.DataFrame([row]), STOCK_DETAIL_FIELDS)
    st.dataframe(detail, hide_index=True, use_container_width=True)
    st.subheader("研究报告预览")
    report = build_stock_research_report(row)
    st.text_area("只读报告", value=report, height=320, disabled=True)
    return {"selected_row": row.copy(deep=True), "report": report}


def _render_technical_indicator_cards(row: pd.Series) -> None:
    st.subheader("技术指标")
    cards = [
        ("趋势", safe_get(row, "technical_trend_score"), safe_get(row, "technical_signal_summary")),
        ("动量", safe_get(row, "technical_momentum_score"), f"RSI {format_value(safe_get(row, 'rsi14'))} / MACD {format_value(safe_get(row, 'macd_signal'))}"),
        ("量能", safe_get(row, "technical_volume_score"), f"Volume ratio {format_value(safe_get(row, 'volume_ratio_20d'))}"),
        ("波动", safe_get(row, "technical_volatility_score"), f"Volatility {format_value(safe_get(row, 'volatility_20d'))}"),
        ("位置", safe_get(row, "technical_position_score"), f"52w position {format_value(safe_get(row, 'position_52w'))}"),
        ("风险提示", safe_get(row, "technical_risk_flags"), safe_get(row, "technical_indicator_warnings")),
    ]
    columns = st.columns(3)
    for column, (title, value, caption) in zip(columns * 2, cards):
        with column:
            _render_metric_card(title, value, caption)


def _render_fundamental_research_cards(row: pd.Series) -> None:
    st.subheader("基本面分析")
    cards = [
        ("估值", safe_get(row, "valuation_score"), f"PE {format_value(safe_get(row, 'pe_ttm'))} / PB {format_value(safe_get(row, 'pb'))}"),
        ("盈利能力", safe_get(row, "profitability_score"), f"ROE {format_value(safe_get(row, 'roe'))}"),
        ("成长能力", safe_get(row, "growth_score"), f"净利润增速 {format_value(safe_get(row, 'net_profit_growth_yoy'))}"),
        ("财务质量", safe_get(row, "financial_quality_score"), f"现金流质量 {format_value(safe_get(row, 'ocf_to_net_profit'))}"),
        ("基本面研究分", safe_get(row, "fundamental_research_score"), safe_get(row, "fundamental_summary")),
        ("基本面风险提示", safe_get(row, "fundamental_risks"), safe_get(row, "fundamental_warnings")),
        ("数据来源", safe_get(row, "fundamental_data_source"), safe_get(row, "fundamental_data_status")),
        ("更新时间", safe_get(row, "fundamental_updated_at"), safe_get(row, "fundamental_data_warning")),
    ]
    columns = st.columns(3)
    for column, (title, value, caption) in zip(columns * 3, cards):
        with column:
            _render_metric_card(title, value, caption)


def _render_capital_news_industry_cards(row: pd.Series) -> None:
    st.subheader("资金研究卡片")
    cards = [
        ("资金评分", safe_get(row, "capital_flow_score"), f"Rank {format_value(safe_get(row, 'capital_flow_rank'))}"),
        ("资金等级", safe_get(row, "capital_flow_strength"), safe_get(row, "capital_flow_status")),
        ("资金解释", safe_get(row, "capital_flow_summary"), ""),
        ("资金风险", safe_get(row, "capital_flow_warning"), safe_get(row, "capital_flow_warnings")),
        ("数据来源", safe_get(row, "capital_flow_source"), safe_get(row, "capital_flow_status")),
        ("更新时间", safe_get(row, "capital_flow_updated_at"), ""),
        ("资金活跃度", safe_get(row, "capital_activity_score"), f"Turnover rate {format_value(safe_get(row, 'turnover_rate'))} / Volume ratio {format_value(safe_get(row, 'volume_ratio'))}"),
        ("主力净流入", safe_get(row, "main_net_inflow"), safe_get(row, "main_net_inflow_ratio")),
        ("北向变化", safe_get(row, "northbound_change"), safe_get(row, "northbound_hold")),
    ]
    columns = st.columns(3)
    for column, (title, value, caption) in zip(columns * 3, cards):
        with column:
            _render_metric_card(title, value, caption)
    st.subheader("新闻事件 / 行业概念")
    context_cards = [
        ("News Event Score", safe_get(row, "news_event_score"), safe_get(row, "news_sentiment_label")),
        ("News Title", safe_get(row, "news_title"), safe_get(row, "news_source")),
        ("Industry", safe_get(row, "industry"), safe_get(row, "concepts")),
        ("Industry Strength", safe_get(row, "industry_strength_score"), safe_get(row, "industry_rank")),
        ("Concept Heat", safe_get(row, "concept_heat_score"), safe_get(row, "concept_rank")),
        ("Data Source Diagnostics", safe_get(row, "news_source"), safe_get(row, "industry_source")),
    ]
    columns = st.columns(3)
    for column, (title, value, caption) in zip(columns * 2, context_cards):
        with column:
            _render_metric_card(title, value, caption)


def render_backtest_page(df: Any) -> pd.DataFrame:
    """Render backtest analysis page."""
    source = safe_copy_frame(df)
    _render_page_header("回测分析", "历史收益、波动、回撤和质量标签")
    metrics = [
        ("平均 period_return", _metric_value(source, "period_return"), "区间收益均值"),
        ("平均 annualized_return", _metric_value(source, "annualized_return"), "年化收益均值"),
        ("平均 volatility", _metric_value(source, "volatility"), "波动率均值"),
        ("平均 max_drawdown", _metric_value(source, "max_drawdown"), "最大回撤均值"),
        ("平均 win_rate", _metric_value(source, "win_rate"), "胜率均值"),
        ("平均 return_risk_ratio", _metric_value(source, "return_risk_ratio"), "收益风险比均值"),
    ]
    columns = st.columns(3)
    for column, (title, value, caption) in zip(columns * 2, metrics):
        with column:
            _render_metric_card(title, value, caption)
    return _render_table(source, BACKTEST_COLUMNS, "Backtest Analysis")


def render_chart_center_page(df: Any) -> dict[str, Any]:
    """Render the product Chart Center page."""
    source = safe_copy_frame(df)
    _render_page_header("图表中心", "评分排行、收益风险、风险分布和单股评分拆解")
    if source.empty:
        _render_empty_notice("Chart Center")
    tabs = st.tabs(["评分排行图", "收益风险散点图", "风险分布图", "单股评分拆解图"])
    with tabs[0]:
        ranking = render_candidate_ranking_bar(source)
    with tabs[1]:
        scatter = render_return_risk_scatter(source)
    with tabs[2]:
        drawdown = render_drawdown_risk_view(source)
        if "selection_bucket" in source.columns:
            st.subheader("候选池分布图")
            st.bar_chart(source["selection_bucket"].fillna("Unavailable").value_counts())
        else:
            st.warning("候选池分布图缺少 selection_bucket 字段。")
    with tabs[3]:
        row = source.iloc[0].copy(deep=True) if not source.empty else None
        breakdown = render_score_breakdown_bar(row)
    return {"ranking": ranking, "scatter": scatter, "drawdown": drawdown, "breakdown": breakdown}


def render_factor_lab_page(df: Any) -> dict[str, Any]:
    """Render Factor Research Lab page."""
    source = safe_copy_frame(df)
    _render_page_header("因子研究实验室", "因子总览、IC、Rank IC、Q1-Q5 分组收益和摘要")
    dataset = build_factor_dataset(source)
    if dataset.empty:
        _render_empty_notice("Factor Research Lab")
    overview_columns = [
        "factor_name",
        "factor_ic",
        "factor_rank_ic",
        "factor_group_return",
        "factor_effectiveness_label",
        "factor_research_summary",
    ]
    overview = _format_display_table(dataset, overview_columns)
    st.subheader("因子总览表")
    st.dataframe(overview.drop_duplicates() if not overview.empty else overview, hide_index=True, use_container_width=True)
    st.subheader("IC / Rank IC 表")
    ic_table = _format_display_table(dataset, ["factor_name", "factor_ic", "factor_rank_ic", "factor_effectiveness_label"])
    st.dataframe(ic_table.drop_duplicates() if not ic_table.empty else ic_table, hide_index=True, use_container_width=True)
    st.subheader("Q1-Q5 分组收益表")
    group_table = _format_display_table(dataset, ["factor_name", "factor_group", "factor_group_return"])
    st.dataframe(group_table.drop_duplicates() if not group_table.empty else group_table, hide_index=True, use_container_width=True)
    report: dict[str, Any] = {}
    available_factors = [factor for factor in DEFAULT_FACTOR_COLUMNS if factor in source.columns]
    if available_factors:
        selected_factor = st.selectbox("选择因子", options=available_factors)
        report = build_factor_research_report(source, selected_factor)
        _render_metric_card("因子有效性标签", report.get("factor_effectiveness_label"), "基于 IC 的中性标签")
        st.write(report.get("factor_research_summary", ""))
    else:
        st.warning("当前数据缺少默认因子字段。")
    return {"dataset": dataset, "overview": overview, "ic_table": ic_table, "group_table": group_table, "report": report}


def render_report_preview_page(df: Any) -> str:
    """Render research report preview page."""
    source = safe_copy_frame(df)
    _render_page_header("研究报告预览", "单只研究对象的只读报告文本")
    if source.empty:
        _render_empty_notice("研究报告预览")
        return ""
    row = source.iloc[0].copy(deep=True)
    report = build_stock_research_report(row)
    st.text_area("研究报告", value=report, height=420, disabled=True)
    return report


def render_data_source_center_page(df: Any) -> pd.DataFrame:
    """Render the unified data-source center page."""
    source = safe_copy_frame(df)
    _render_page_header("数据源中心", "实时行情、K线、基本面、资金面、新闻、行业与缓存状态")
    status = build_data_source_status(source)
    st.dataframe(status, hide_index=True, use_container_width=True)
    return status


def render_system_status_page(df: Any) -> dict[str, Any]:
    """Render system status and data-quality page."""
    source = safe_copy_frame(df)
    data_source = source.attrs.get("data_source", "Unavailable") if hasattr(source, "attrs") else "Unavailable"
    data_status = source.attrs.get("data_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable"
    is_demo = bool(source.attrs.get("is_demo", False)) if hasattr(source, "attrs") else False
    raw_count = source.attrs.get("raw_count", len(source)) if hasattr(source, "attrs") else len(source)
    filtered_count = source.attrs.get("filtered_count", 0) if hasattr(source, "attrs") else 0
    final_count = source.attrs.get("final_count", len(source)) if hasattr(source, "attrs") else len(source)
    load_time = source.attrs.get("load_time", "—") if hasattr(source, "attrs") else "—"
    updated_at = source.attrs.get("updated_at", "—") if hasattr(source, "attrs") else "—"
    last_error = source.attrs.get("last_error", "") if hasattr(source, "attrs") else ""
    source_attempts = source.attrs.get("source_attempts", []) if hasattr(source, "attrs") else []
    cache_status = source.attrs.get("cache_status", "Missing") if hasattr(source, "attrs") else "Missing"
    cache_updated_at = source.attrs.get("cache_updated_at", "—") if hasattr(source, "attrs") else "—"
    cache_universe_path = source.attrs.get("cache_universe_path", "cache/a_share_universe_latest.csv") if hasattr(source, "attrs") else "cache/a_share_universe_latest.csv"
    cache_quotes_path = source.attrs.get("cache_quotes_path", "cache/a_share_quotes_latest.csv") if hasattr(source, "attrs") else "cache/a_share_quotes_latest.csv"
    kline_status = source.attrs.get("kline_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable"
    kline_requested = source.attrs.get("kline_requested", 0) if hasattr(source, "attrs") else 0
    kline_loaded = source.attrs.get("kline_loaded", 0) if hasattr(source, "attrs") else 0
    kline_cache_hits = source.attrs.get("kline_cache_hits", 0) if hasattr(source, "attrs") else 0
    kline_failures = source.attrs.get("kline_failures", 0) if hasattr(source, "attrs") else 0
    fundamental_data_source = source.attrs.get("fundamental_data_source", "Unavailable") if hasattr(source, "attrs") else "Unavailable"
    fundamental_data_status = source.attrs.get("fundamental_data_status", "Unavailable") if hasattr(source, "attrs") else "Unavailable"
    fundamental_rows = source.attrs.get("fundamental_rows", 0) if hasattr(source, "attrs") else 0
    _render_page_header("系统状态 / 数据质量", "版本、模块、缺失字段、warnings 和数据源说明")
    modules = list(REQUIRED_FIELD_GROUPS.keys())
    columns = st.columns(4)
    cards = [
        ("当前版本", PRODUCT_VERSION, "Web 入口版本"),
        ("当前阶段", PRODUCT_STAGE, "产品集成阶段"),
        ("可用模块", len(modules), "已注册展示模块"),
        ("测试状态说明", "pytest passed", "以最近一次本地测试为准"),
    ]
    for column, (title, value, caption) in zip(columns, cards):
        with column:
            _render_metric_card(title, value, caption)
    missing = find_missing_fields(source)
    warnings = collect_warning_fields(source)
    st.subheader("可用模块")
    for module in modules:
        st.markdown(badge_html(module, "info"), unsafe_allow_html=True)
    st.subheader("缺失字段")
    missing_rows = [{"module": module, "missing_fields": ", ".join(fields) or MISSING} for module, fields in missing.items()]
    st.dataframe(pd.DataFrame(missing_rows), hide_index=True, use_container_width=True)
    st.subheader("warnings 汇总")
    if warnings:
        st.warning("\n".join(f"- {item}" for item in warnings[:100]))
    else:
        st.info("当前页面数据没有汇总到 warning 字段。")
    st.subheader("数据源状态说明")
    st.info("当前产品页读取已生成的本地研究结果。免费行情或基础数据源可能延迟、缺失或字段变化。")
    status_rows = [
        {"item": "数据源", "value": data_source},
        {"item": "数据状态", "value": data_status},
        {"item": "Universe Size", "value": final_count},
        {"item": "加载时间", "value": load_time},
        {"item": "更新时间", "value": updated_at},
        {"item": "原始股票", "value": raw_count},
        {"item": "过滤数量", "value": filtered_count},
        {"item": "最终样本数", "value": final_count},
        {"item": "缓存状态", "value": cache_status},
        {"item": "缓存更新时间", "value": cache_updated_at or "—"},
        {"item": "Universe 缓存路径", "value": cache_universe_path},
        {"item": "Quotes 缓存路径", "value": cache_quotes_path},
        {"item": "K线状态", "value": kline_status},
        {"item": "K线请求数量", "value": kline_requested},
        {"item": "K线加载数量", "value": kline_loaded},
        {"item": "K线缓存命中", "value": kline_cache_hits},
        {"item": "K线加载失败", "value": kline_failures},
        {"item": "K线缓存路径", "value": "cache/kline/{ticker}.csv"},
        {"item": "基本面数据源", "value": fundamental_data_source},
        {"item": "基本面状态", "value": fundamental_data_status},
        {"item": "基本面数据行数", "value": fundamental_rows},
        {"item": "基本面缓存路径", "value": "cache/fundamental/fundamental_latest.csv"},
        {"item": "最近错误", "value": last_error or "—"},
    ]
    st.dataframe(pd.DataFrame(status_rows), hide_index=True, use_container_width=True)
    st.subheader("Realtime source fallback attempts")
    fallback_rows = source_attempts if isinstance(source_attempts, list) else []
    if fallback_rows:
        st.dataframe(pd.DataFrame(fallback_rows), hide_index=True, use_container_width=True)
    else:
        st.info("No realtime source attempt metadata is available for the current frame.")
    if is_demo:
        st.warning(source.attrs.get("data_notice", "当前为 Demo 数据，用于展示系统结构；接入真实行情后可替换为真实结果。"))
    st.info(f"当前数据来源：{data_source}；是否 Demo：{is_demo}；样本数量：{len(source)}。所有结果仅供学习和研究，不构成投资建议。")
    return {
        "missing_fields": missing,
        "warnings": warnings,
        "modules": modules,
        "data_source": data_source,
        "data_status": data_status,
        "is_demo": is_demo,
        "raw_count": raw_count,
        "filtered_count": filtered_count,
        "final_count": final_count,
        "source_attempts": fallback_rows,
    }


def render_product_page(page: str, state: dict[str, pd.DataFrame] | None = None) -> Any:
    """Render a product page by navigation name."""
    data = state or get_product_state()
    research = primary_research_frame(data)
    if not research.empty and bool(research.attrs.get("is_demo", False)):
        st.warning(research.attrs.get("data_notice", "当前为 Demo 数据，用于展示系统结构；接入真实行情后可替换为真实结果。"))
    if page == DASHBOARD_PAGE:
        return render_dashboard_page(research)
    if page == UNIVERSE_PAGE:
        return render_universe_page(research)
    if page == SELECTION_PAGE:
        return render_selection_page(research)
    if page == WORKSTATION_PAGE:
        return render_research_workstation_product(research)
    if page == BACKTEST_PAGE:
        return render_backtest_page(research)
    if page == CHART_PAGE:
        return render_chart_center_page(research)
    if page == FACTOR_PAGE:
        return render_factor_lab_page(research)
    if page == REPORT_PAGE:
        return render_report_preview_page(research)
    if page == SYSTEM_PAGE:
        return render_system_status_page(research)
    if page == DATA_SOURCE_PAGE:
        return render_data_source_center_page(research)
    return render_dashboard_page(research)


def render_research_workstation_product(df: Any) -> dict[str, Any]:
    """Render the existing workstation from product navigation."""
    source = safe_copy_frame(df)
    if source.empty:
        _render_page_header("个股研究工作台", "Research Workstation 页面框架")
        _render_empty_notice("Research Workstation")
        return {"metrics": {}, "selected_row": None, "compare": pd.DataFrame(), "charts": {}, "factor_lab": {}, "pipeline": [], "report": ""}
    if any(field in source.columns for field in ["real_technical_score", "technical_trend_score", "technical_risk_flags"]):
        _render_technical_indicator_cards(source.iloc[0].copy(deep=True))
    if any(field in source.columns for field in ["fundamental_research_score", "valuation_score", "fundamental_risks"]):
        _render_fundamental_research_cards(source.iloc[0].copy(deep=True))
    if any(field in source.columns for field in ["capital_flow_score", "news_event_score", "industry_strength_score"]):
        _render_capital_news_industry_cards(source.iloc[0].copy(deep=True))
    return render_research_workstation(source)


__all__ = [
    "BACKTEST_PAGE",
    "CHART_PAGE",
    "DASHBOARD_PAGE",
    "DATA_SOURCE_PAGE",
    "FACTOR_PAGE",
    "LEGACY_PAGE",
    "NAVIGATION_PAGES",
    "PRODUCT_STAGE",
    "PRODUCT_VERSION",
    "REPORT_PAGE",
    "SCREENING_PIPELINE_PAGE",
    "SELECTION_PAGE",
    "SYSTEM_PAGE",
    "UNIVERSE_PAGE",
    "WORKSTATION_PAGE",
    "build_dashboard_summary",
    "collect_warning_fields",
    "find_missing_fields",
    "get_navigation_pages",
    "get_product_state",
    "primary_research_frame",
    "render_backtest_page",
    "render_chart_center_page",
    "render_dashboard_page",
    "render_data_source_center_page",
    "render_factor_lab_page",
    "render_product_page",
    "render_report_preview_page",
    "render_research_workstation_product",
    "render_selection_page",
    "render_stock_workstation_page",
    "render_system_status_page",
    "render_universe_page",
    "set_product_state",
]
