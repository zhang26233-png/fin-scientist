"""Streamlit UI entry for the automatic research-object screening page.

The screening workflow implementation still lives in legacy_app.py. This page
is the new navigation entry and keeps that dependency explicit until the
renderer can be migrated safely.
"""

import streamlit as st

from config.stock_pools import A_SHARE_SCREENING_POOLS, DEFAULT_A_SHARE_POOL_TYPE
import legacy_app as legacy_workbench


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
        legacy_workbench.render_screening_section(
            screening_market,
            screening_pool_source,
            screening_top_n,
            screening_custom_input,
            screening_a_share_pool_type,
            screening_max_process_count,
            screening_run_mode,
        )
    else:
        st.header('\u81ea\u52a8\u7814\u7a76\u5bf9\u8c61\u7b5b\u9009')
        st.info('\u8bf7\u9009\u62e9\u80a1\u7968\u6c60\u548c\u8fd0\u884c\u6a21\u5f0f\u540e\uff0c\u70b9\u51fb\u751f\u6210\u7814\u7a76\u5019\u9009\u6c60\u3002\u5f53\u524d\u7ed3\u679c\u4ec5\u4f9b\u5b66\u4e60\u548c\u7814\u7a76\uff0c\u4e0d\u6784\u6210\u6295\u8d44\u5efa\u8bae\u3002')
