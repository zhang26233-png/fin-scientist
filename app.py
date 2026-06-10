"""FinScientist Streamlit entrypoint.

This module owns page setup and routing only. Legacy workbench behavior stays
behind the compatibility layer.
"""

import streamlit as st

import legacy_app
from ui.product_ui import (
    LEGACY_PAGE,
    SCREENING_PIPELINE_PAGE,
    get_navigation_pages,
    render_product_page,
)
from ui.screening_ui import render_screening_page

APP_VERSION = "v6.1.0"
APP_STAGE = "Web Product Integration"

# Re-export core functions used by the existing tests and notebooks.
calculate_indicators = legacy_app.calculate_indicators
calculate_backtest_metrics = legacy_app.calculate_backtest_metrics
generate_backtest_signals = legacy_app.generate_backtest_signals
check_price_data_quality = legacy_app.check_price_data_quality


def main():
    st.set_page_config(page_title="FinScientist", page_icon="\U0001f4c8", layout="wide")
    with st.sidebar:
        st.title("Fin-Scientist")
        st.caption(f"{APP_VERSION} | {APP_STAGE}")
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
