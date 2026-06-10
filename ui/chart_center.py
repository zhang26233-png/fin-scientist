"""Read-only Chart Center for Research Workstation results."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from ui.chart_components import (
    build_candidate_ranking_data,
    build_drawdown_risk_data,
    build_quality_distribution_data,
    build_return_risk_scatter_data,
    build_score_breakdown_data,
    build_score_profile_data,
    safe_chart_df,
    safe_numeric,
)


CHART_CENTER_VERSION = "v5.1.0"
CHART_CENTER_STAGE = "Chart Center"


def _warn_missing(title: str, fields: list[str]) -> None:
    st.warning(f"{title} 缺少可用字段：{', '.join(fields)}")


def _render_bar_chart(data: pd.DataFrame, x_field: str, y_field: str, title: str) -> None:
    st.subheader(title)
    if data.empty or x_field not in data.columns or y_field not in data.columns:
        st.warning(f"{title} 暂无可展示数据。")
        return
    st.bar_chart(data.set_index(x_field)[y_field])


def render_score_profile(row: pd.Series | dict[str, Any] | None) -> pd.DataFrame:
    """Render score profile for a single object."""
    data = build_score_profile_data(row)
    _render_bar_chart(data.dropna(subset=["score_value"]), "score_field", "score_value", "Score Radar / Score Profile")
    if data["score_value"].isna().any():
        _warn_missing("Score Profile", data[data["score_value"].isna()]["score_field"].tolist())
    return data


def render_return_risk_scatter(df: pd.DataFrame) -> pd.DataFrame:
    """Render return-risk scatter using Streamlit native scatter chart."""
    data = build_return_risk_scatter_data(df)
    st.subheader("Return-Risk Scatter")
    if data.empty:
        st.warning("Return-Risk Scatter 缺少 volatility/risk_score 或 period_return/annualized_return。")
        return data
    st.scatter_chart(data, x="x_risk", y="y_return")
    st.dataframe(data, hide_index=True, use_container_width=True)
    return data


def render_drawdown_risk_view(df: pd.DataFrame) -> pd.DataFrame:
    """Render drawdown-risk view."""
    data = build_drawdown_risk_data(df)
    st.subheader("Drawdown-Risk View")
    if data.empty:
        st.warning("Drawdown-Risk View 缺少 max_drawdown、volatility 或 risk_level。")
        return data
    numeric = data[[field for field in ["max_drawdown", "volatility"] if field in data.columns]].copy(deep=True)
    if numeric.empty:
        st.warning("Drawdown-Risk View 缺少可绘制的数值字段。")
    else:
        st.bar_chart(numeric)
    st.dataframe(data, hide_index=True, use_container_width=True)
    return data


def render_score_breakdown_bar(row: pd.Series | dict[str, Any] | None) -> pd.DataFrame:
    """Render a single-object score breakdown bar."""
    data = build_score_breakdown_data(row)
    _render_bar_chart(data.dropna(subset=["score_value"]), "score_field", "score_value", "Score Breakdown Bar")
    return data


def render_candidate_ranking_bar(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Render Top N selection_score ranking."""
    data = build_candidate_ranking_data(df, top_n=top_n)
    _render_bar_chart(data, "label", "selection_score", "Candidate Ranking Bar")
    return data


def render_quality_distribution(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Render candidate and risk distribution charts."""
    distributions = build_quality_distribution_data(df)
    st.subheader("Quality Distribution")
    columns = st.columns(2)
    with columns[0]:
        _render_bar_chart(distributions["selection_bucket"], "label", "count", "Core / Watch / Exclude 分布")
    with columns[1]:
        _render_bar_chart(distributions["risk_level"], "label", "count", "High / Medium / Low 风险分布")
    return distributions


def render_chart_center(df: pd.DataFrame) -> dict[str, Any]:
    """Render the full Chart Center and return chart payloads."""
    source = safe_chart_df(
        df,
        [
            "ticker",
            "name",
            "fundamental_score",
            "technical_score",
            "composite_score",
            "selection_score",
            "risk_score",
            "volatility",
            "period_return",
            "annualized_return",
            "max_drawdown",
            "risk_level",
            "selection_bucket",
        ],
    )
    st.header("Chart Center")
    st.caption("所有图表均为只读研究展示，不改变评分、排序、筛选流程或交易逻辑。")
    if source.empty:
        st.warning("Chart Center 当前没有可展示数据。")
        empty_row = None
    else:
        empty_row = source.iloc[0].copy(deep=True)

    tabs = st.tabs(["单股图表", "风险收益", "排名与分布"])
    with tabs[0]:
        score_profile = render_score_profile(empty_row)
        score_breakdown = render_score_breakdown_bar(empty_row)
    with tabs[1]:
        scatter = render_return_risk_scatter(source)
        drawdown = render_drawdown_risk_view(source)
    with tabs[2]:
        ranking = render_candidate_ranking_bar(source)
        distribution = render_quality_distribution(source)
    return {
        "score_profile": score_profile,
        "score_breakdown": score_breakdown,
        "return_risk_scatter": scatter,
        "drawdown_risk": drawdown,
        "candidate_ranking": ranking,
        "quality_distribution": distribution,
    }


__all__ = [
    "CHART_CENTER_STAGE",
    "CHART_CENTER_VERSION",
    "render_candidate_ranking_bar",
    "render_chart_center",
    "render_drawdown_risk_view",
    "render_quality_distribution",
    "render_return_risk_scatter",
    "render_score_breakdown_bar",
    "render_score_profile",
    "safe_chart_df",
    "safe_numeric",
]
