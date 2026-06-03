"""Streamlit UI entry for the automatic research-object screening page.

The screening workflow implementation still lives in legacy_app.py. This page
is the new navigation entry and keeps that dependency explicit until the
renderer can be migrated safely.
"""

import streamlit as st

from config.stock_pools import A_SHARE_SCREENING_POOLS, DEFAULT_A_SHARE_POOL_TYPE
import legacy_app as legacy_workbench
from strategy.preview import build_strategy_preview


STRATEGY_PREVIEW_COLUMNS = [
    "symbol",
    "name",
    "strategy_score",
    "composite_research_grade",
    "composite_research_style",
    "composite_research_level",
    "composite_risk_level",
    "composite_confidence_level",
    "composite_summary",
    "composite_strength_points",
    "composite_risk_points",
    "composite_followup_focus",
    "composite_data_quality_note",
    "research_priority_score",
    "research_priority_level",
    "research_priority_reasons",
    "research_priority_warnings",
    "priority_stability_label",
    "priority_stability_score",
    "priority_stability_note",
    "priority_drift_detected",
    "priority_drift_reason",
    "technical_grade",
    "technical_style",
    "technical_strength",
    "technical_risk_level",
    "technical_summary_short",
    "technical_watch_points",
    "fundamental_available",
    "fundamental_data_quality_label",
    "fundamental_summary_base",
    "fundamental_quality_score",
    "fundamental_grade",
    "fundamental_style",
    "fundamental_risk_level",
    "fundamental_reason",
    "industry_relative_quality_label",
    "relative_profitability_label",
    "relative_growth_label",
    "relative_valuation_label",
    "relative_financial_risk_label",
    "industry_relative_summary",
    "fundamental_diagnostics_summary",
    "fundamental_strength_points",
    "fundamental_weakness_points",
    "fundamental_watch_points",
    "profitability_diagnostics",
    "growth_diagnostics",
    "valuation_diagnostics",
    "financial_risk_diagnostics",
    "original_score",
    "best_preset",
    "dominant_style",
    "consensus_level",
    "balanced_research_score",
    "trend_momentum_score",
    "volume_breakout_score",
    "low_risk_quality_score",
    "high_elasticity_watch_score",
    "risk_labels",
    "data_quality_labels",
    "ma_structure_label",
    "trend_quality_label",
    "volume_price_structure_label",
    "short_term_overheat_label",
    "volatility_risk_label",
    "technical_profile_summary",
    "strategy_reason",
    "risk_reason",
    "data_quality_reason",
    "preset_reason",
    "confidence_note",
    "warnings",
]


def build_screening_strategy_preview(result_df, sort_by_strategy=False):
    return build_strategy_preview(result_df, sort_by_strategy=sort_by_strategy)


def render_strategy_preview_section(result_df):
    with st.expander("策略评分预览（研究辅助，不构成投资建议）", expanded=False):
        st.caption("以下策略评分仅用于研究优先级观察，不构成投资建议；默认不改变原筛选排序。")
        if result_df is None or getattr(result_df, "empty", True):
            st.info("当前候选池为空，暂无可展示的策略评分预览。")
            return build_screening_strategy_preview(result_df)

        sort_preview = st.checkbox("按 strategy_score 查看预览", value=False)
        preview = build_screening_strategy_preview(result_df, sort_by_strategy=sort_preview)
        display_columns = [column for column in STRATEGY_PREVIEW_COLUMNS if column in preview.columns]
        st.dataframe(preview[display_columns], hide_index=True, use_container_width=True)

        warning_rows = preview[preview["warnings"].map(bool)] if "warnings" in preview.columns else preview.iloc[0:0]
        if not warning_rows.empty:
            st.caption("部分候选对象存在字段缺失或数据质量提示，请结合原始指标继续核对。")
        return preview


def render_screening_page():
    """Render the V1.2 screening page with the unchanged V1.1 workflow."""
    st.caption(
        "缓存用于提升批量筛选速度，不保证实时性。免费数据源可能失败，"
        "如果结果异常，可清除缓存后重试。"
    )
    with st.sidebar:
        st.header('\u81ea\u52a8\u7b5b\u9009\u53c2\u6570')
        screening_market = st.selectbox('\u7b5b\u9009\u5e02\u573a', options=legacy_workbench.SCREENING_MARKET_OPTIONS, index=0)
        screening_run_mode = st.selectbox('\u8fd0\u884c\u6a21\u5f0f', options=legacy_workbench.SCREENING_RUN_MODE_OPTIONS, index=0)
        screening_pool_source = st.selectbox('\u80a1\u7968\u6c60\u9009\u62e9', options=legacy_workbench.SCREENING_POOL_OPTIONS, index=0)
        screening_a_share_pool_type = DEFAULT_A_SHARE_POOL_TYPE
        if screening_market == 'A\u80a1' and screening_pool_source == '\u9ed8\u8ba4\u793a\u4f8b\u80a1\u7968\u6c60':
            screening_a_share_pool_type = st.selectbox(
                'A\u80a1\u80a1\u7968\u6c60\u7c7b\u578b',
                options=list(A_SHARE_SCREENING_POOLS.keys()),
                index=list(A_SHARE_SCREENING_POOLS.keys()).index(DEFAULT_A_SHARE_POOL_TYPE),
            )
        screening_custom_input = st.text_area(
            '\u81ea\u5b9a\u4e49\u80a1\u7968\u6c60',
            value="600519, 300750, 000001" if screening_market == 'A\u80a1' else "AAPL, MSFT, NVDA",
            height=90,
        )
        screening_top_n = st.selectbox('\u7b5b\u9009\u6570\u91cf', options=legacy_workbench.SCREENING_TOP_OPTIONS, index=0)
        screening_max_process_count = st.selectbox('\u6700\u5927\u5904\u7406\u6570\u91cf', options=legacy_workbench.SCREENING_MAX_PROCESS_OPTIONS, index=0)
        clear_screening_cache_button = st.button('\u6e05\u9664\u7f13\u5b58\u5e76\u91cd\u65b0\u83b7\u53d6\u6570\u636e')
        run_screening_button = st.button('\u751f\u6210\u7814\u7a76\u5019\u9009\u6c60')

    if clear_screening_cache_button:
        try:
            st.cache_data.clear()
            st.success('\u7f13\u5b58\u5df2\u6e05\u9664\uff0c\u8bf7\u91cd\u65b0\u8fd0\u884c\u7b5b\u9009\u3002')
        except Exception as exc:
            st.warning(f"缓存清除失败，请稍后重试：{exc}")

    if run_screening_button:
        screening_result = legacy_workbench.render_screening_section(
            screening_market,
            screening_pool_source,
            screening_top_n,
            screening_custom_input,
            screening_a_share_pool_type,
            screening_max_process_count,
            screening_run_mode,
        )
        render_strategy_preview_section(screening_result)
    else:
        st.header('\u81ea\u52a8\u7814\u7a76\u5bf9\u8c61\u7b5b\u9009')
        st.info('\u8bf7\u9009\u62e9\u80a1\u7968\u6c60\u548c\u8fd0\u884c\u6a21\u5f0f\u540e\uff0c\u70b9\u51fb\u751f\u6210\u7814\u7a76\u5019\u9009\u6c60\u3002\u5f53\u524d\u7ed3\u679c\u4ec5\u4f9b\u5b66\u4e60\u548c\u7814\u7a76\uff0c\u4e0d\u6784\u6210\u6295\u8d44\u5efa\u8bae\u3002')
