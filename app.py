"""FinScientist Streamlit entrypoint.

This module owns page setup and routing only. Legacy workbench behavior stays
behind the compatibility layer.
"""

import streamlit as st

import legacy_app
from pipeline.live_runner import run_live_pipeline
from ui.product_ui import (
    LEGACY_PAGE,
    SCREENING_PIPELINE_PAGE,
    get_navigation_pages,
    render_product_page,
    set_product_state,
)
from ui.screening_ui import render_screening_page

APP_VERSION = "v6.3.5"
APP_STAGE = "Full A-Share Pagination and Cache Layer"

# Re-export core functions used by the existing tests and notebooks.
calculate_indicators = legacy_app.calculate_indicators
calculate_backtest_metrics = legacy_app.calculate_backtest_metrics
generate_backtest_signals = legacy_app.generate_backtest_signals
check_price_data_quality = legacy_app.check_price_data_quality


def _store_live_pipeline_result(result_df):
    st.session_state["research_df"] = result_df
    set_product_state(
        universe=result_df,
        fundamental=result_df,
        technical=result_df,
        composite=result_df,
        candidate_pool=result_df,
        backtest_foundation=result_df,
        return_analysis=result_df,
        backtest_evaluation=result_df,
        stock_selection=result_df,
        explainable_selection=result_df,
    )


def main():
    st.set_page_config(page_title="FinScientist", page_icon="\U0001f4c8", layout="wide")
    with st.sidebar:
        st.title("Fin-Scientist")
        st.caption(f"{APP_VERSION} | {APP_STAGE}")
        if st.button("运行完整选股模型"):
            try:
                with st.spinner("正在运行 Fin-Scientist 选股流水线..."):
                    result_df = run_live_pipeline()
                _store_live_pipeline_result(result_df)
                if result_df.attrs.get("is_demo"):
                    st.info(result_df.attrs.get("data_notice", "当前为 Demo 数据，用于展示系统结构；接入真实行情后可替换为真实结果。"))
                st.success(f"选股流水线已完成，生成 {len(result_df)} 条研究结果。")
            except Exception as exc:
                st.error(f"选股流水线运行失败，请稍后重试或检查数据源：{exc}")
        page = st.radio("平台导航", options=get_navigation_pages(), index=0)
        st.caption("所有页面仅用于学习和研究，不构成投资建议。")

    if page == SCREENING_PIPELINE_PAGE:
        render_screening_page()
    elif page == LEGACY_PAGE:
        legacy_app.render_legacy_workbench()
    else:
        render_product_page(page)


if __name__ == "__main__":
    main()
