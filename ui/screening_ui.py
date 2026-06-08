"""Streamlit UI entry for the automatic research-object screening page."""

import streamlit as st

from config.stock_pools import A_SHARE_SCREENING_POOLS, DEFAULT_A_SHARE_POOL_TYPE
import legacy_app as legacy_workbench
from screening.fundamental_screening import build_fundamental_screening
from screening.technical_screening import build_technical_screening
from strategy.preview import build_strategy_preview
from universe.a_share_universe import build_a_share_universe


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
    "architecture_audit_label",
    "architecture_audit_score",
    "architecture_audit_note",
    "architecture_audit_warnings",
    "field_contract_warnings",
    "module_contract_warnings",
    "boundary_contract_warnings",
    "event_available",
    "event_type",
    "event_recency_label",
    "event_source_quality_label",
    "event_reliability_label",
    "event_context_note",
    "event_research_tags",
    "event_warnings",
    "event_completeness_score",
    "event_clarity_score",
    "event_consistency_score",
    "event_confidence_score",
    "event_diagnostic_level",
    "event_diagnostic_summary",
    "event_followup_questions",
    "event_evidence_gaps",
    "event_quality_warnings",
    "event_confluence_label",
    "event_confluence_score",
    "event_confluence_summary",
    "event_support_points",
    "event_conflict_points",
    "event_followup_focus",
    "event_confluence_warnings",
    "event_research_summary",
    "event_research_level",
    "event_key_evidence",
    "event_key_risks",
    "event_validation_focus",
    "event_agent_note",
    "event_summary_warnings",
    "research_pipeline_status",
    "research_pipeline_conflicts",
    "research_pipeline_warnings",
    "research_pipeline_summary",
    "project_assessment_status",
    "project_assessment_score",
    "architecture_assessment_note",
    "field_registry_assessment_note",
    "test_coverage_assessment_note",
    "ui_readability_assessment_note",
    "data_source_assessment_note",
    "scoring_boundary_assessment_note",
    "pre_v2_readiness_level",
    "pre_v2_blockers",
    "pre_v2_recommendations",
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

FUNDAMENTAL_SCREENING_COLUMNS = [
    "ticker",
    "name",
    "fundamental_score",
    "fundamental_level",
    "fundamental_screening_status",
    "fundamental_reasons",
    "fundamental_warnings",
]

TECHNICAL_SCREENING_COLUMNS = [
    "ticker",
    "name",
    "technical_score",
    "technical_level",
    "technical_screening_status",
    "technical_reasons",
    "technical_warnings",
]


def build_screening_strategy_preview(result_df, sort_by_strategy=False):
    return build_strategy_preview(result_df, sort_by_strategy=sort_by_strategy)


@st.cache_data(ttl=3600, show_spinner=False)
def load_a_share_universe():
    return build_a_share_universe()


def render_a_share_universe_section():
    universe = load_a_share_universe()
    total_count = universe.attrs.get("universe_total_count", 0)
    filtered_count = universe.attrs.get("universe_filtered_count", 0)
    summary = universe.attrs.get("universe_summary", "")
    status = universe.attrs.get("universe_status", "Incomplete")

    st.subheader("A-Share Universe")
    metric_cols = st.columns(3)
    metric_cols[0].metric("Total securities", total_count)
    metric_cols[1].metric("Filtered securities", filtered_count)
    metric_cols[2].metric("Universe Status", status)
    st.caption("Filter rules: exclude ST, delisted, suspended, and newly listed securities.")
    st.info(summary or "Universe Summary is not available.")
    return universe


def render_fundamental_screening_section(universe):
    with st.expander("Fundamental Screening (read-only research, not investment advice)", expanded=False):
        st.caption("Fundamental screening is read-only research context. It does not change default sorting.")
        screening = build_fundamental_screening(universe)
        display_columns = [column for column in FUNDAMENTAL_SCREENING_COLUMNS if column in screening.columns]
        if screening.empty:
            st.info("Current Universe is empty. No fundamental screening rows are available.")
            return screening
        st.dataframe(screening[display_columns], hide_index=True, use_container_width=True)
        return screening


def render_technical_screening_section(universe):
    with st.expander("Technical Screening (read-only research, not investment advice)", expanded=False):
        st.caption("Technical screening is read-only research context. It does not change default sorting.")
        screening = build_technical_screening(universe)
        display_columns = [column for column in TECHNICAL_SCREENING_COLUMNS if column in screening.columns]
        if screening.empty:
            st.info("Current Universe is empty. No technical screening rows are available.")
            return screening
        st.dataframe(screening[display_columns], hide_index=True, use_container_width=True)
        return screening


def render_strategy_preview_section(result_df):
    with st.expander("Strategy preview (research support, not investment advice)", expanded=False):
        st.caption("Strategy preview is only for research-priority review. Default ordering is unchanged.")
        if result_df is None or getattr(result_df, "empty", True):
            st.info("Current candidate pool is empty. No strategy preview rows are available.")
            return build_screening_strategy_preview(result_df)

        sort_preview = st.checkbox("View preview by strategy_score", value=False)
        preview = build_screening_strategy_preview(result_df, sort_by_strategy=sort_preview)
        display_columns = [column for column in STRATEGY_PREVIEW_COLUMNS if column in preview.columns]
        st.dataframe(preview[display_columns], hide_index=True, use_container_width=True)

        warning_rows = preview[preview["warnings"].map(bool)] if "warnings" in preview.columns else preview.iloc[0:0]
        if not warning_rows.empty:
            st.caption("Some rows include missing-field or data-quality notes for research review.")
        return preview


def render_screening_page():
    """Render the screening page while keeping the legacy workflow unchanged."""
    st.caption(
        "Cached data may improve batch screening speed but does not guarantee real-time results. "
        "If results look abnormal, clear the cache and run screening again. Not investment advice."
    )
    with st.sidebar:
        st.header("Screening parameters")
        screening_market = st.selectbox("Market", options=legacy_workbench.SCREENING_MARKET_OPTIONS, index=0)
        screening_run_mode = st.selectbox("Run mode", options=legacy_workbench.SCREENING_RUN_MODE_OPTIONS, index=0)
        screening_pool_source = st.selectbox("Stock pool", options=legacy_workbench.SCREENING_POOL_OPTIONS, index=0)
        screening_a_share_pool_type = DEFAULT_A_SHARE_POOL_TYPE
        if screening_market == "A股" and screening_pool_source == "默认示例股票池":
            screening_a_share_pool_type = st.selectbox(
                "A-share pool type",
                options=list(A_SHARE_SCREENING_POOLS.keys()),
                index=list(A_SHARE_SCREENING_POOLS.keys()).index(DEFAULT_A_SHARE_POOL_TYPE),
            )
        screening_custom_input = st.text_area(
            "Custom stock pool",
            value="600519, 300750, 000001" if screening_market == "A股" else "AAPL, MSFT, NVDA",
            height=90,
        )
        screening_top_n = st.selectbox("Screening count", options=legacy_workbench.SCREENING_TOP_OPTIONS, index=0)
        screening_max_process_count = st.selectbox(
            "Max processing count",
            options=legacy_workbench.SCREENING_MAX_PROCESS_OPTIONS,
            index=0,
        )
        clear_screening_cache_button = st.button("Clear cache and refetch data")
        run_screening_button = st.button("Generate research candidate pool")

    if clear_screening_cache_button:
        try:
            st.cache_data.clear()
            st.success("Cache cleared. Run screening again when ready.")
        except Exception as exc:
            st.warning(f"Cache clearing failed. Please retry later: {exc}")

    if screening_market == "A股":
        universe = render_a_share_universe_section()
        render_fundamental_screening_section(universe)
        render_technical_screening_section(universe)

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
        st.header("Automatic research-object screening")
        st.info(
            "Choose a stock pool and run mode, then generate a research candidate pool. "
            "Current results are only for learning and research and are not investment advice."
        )
