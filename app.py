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

APP_VERSION = "v6.8.0"
APP_STAGE = "Full Capital Flow Engine"

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
        kline_enabled = st.checkbox("启用历史K线技术指标", value=True)
        max_kline_stocks = st.selectbox("K线最大股票数", options=[50, 100, 200, 500], index=2)
        st.caption(f"K线数据状态：{'启用' if kline_enabled else '关闭'}；仅对前 {max_kline_stocks} 只生成历史技术指标。")
        fundamental_enabled = st.checkbox("启用真实基本面数据层", value=True)
        st.caption(f"基本面数据层：{'启用' if fundamental_enabled else '关闭'}；外部源失败时读取 cache/fundamental/fundamental_latest.csv。")
        if st.button("运行完整选股模型"):
            try:
                with st.spinner("正在运行 Fin-Scientist 选股流水线..."):
                    result_df = run_live_pipeline(
                        kline_enabled=kline_enabled,
                        max_kline_stocks=int(max_kline_stocks),
                        fundamental_enabled=fundamental_enabled,
                    )
                _store_live_pipeline_result(result_df)
                if result_df.attrs.get("is_demo"):
                    st.info(result_df.attrs.get("data_notice", "当前为 Demo 数据，用于展示系统结构；接入真实行情后可替换为真实结果。"))
                st.info(
                    f"K线状态：{result_df.attrs.get('kline_status', 'Unavailable')} / "
                    f"请求：{result_df.attrs.get('kline_requested', 0)} / "
                    f"加载：{result_df.attrs.get('kline_loaded', 0)} / "
                    f"缓存命中：{result_df.attrs.get('kline_cache_hits', 0)} / "
                    f"失败：{result_df.attrs.get('kline_failures', 0)}"
                )
                st.info(
                    f"基本面状态：{result_df.attrs.get('fundamental_data_source', 'Unavailable')} / "
                    f"{result_df.attrs.get('fundamental_data_status', 'Unavailable')} / "
                    f"rows={result_df.attrs.get('fundamental_rows', 0)}"
                )
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
