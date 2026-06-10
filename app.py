"""FinScientist Streamlit entrypoint.

This module owns page setup and routing only. Legacy workbench behavior stays
behind the compatibility layer.
"""

import streamlit as st

import legacy_app
from ui.screening_ui import render_screening_page

APP_VERSION = "v4.1.0"
LEGACY_WORKBENCH_PAGE = "Research Workbench"
SCREENING_PAGE = "Research Terminal"

# Re-export core functions used by the existing tests and notebooks.
calculate_indicators = legacy_app.calculate_indicators
calculate_backtest_metrics = legacy_app.calculate_backtest_metrics
generate_backtest_signals = legacy_app.generate_backtest_signals
check_price_data_quality = legacy_app.check_price_data_quality


def main():
    st.set_page_config(page_title="FinScientist", page_icon="\U0001f4c8", layout="wide")
    st.title("FinScientist")
    st.caption(
        f"{APP_VERSION} Research Terminal UI Package; all outputs are for learning "
        "and research only and do not constitute investment advice."
    )

    page = st.sidebar.radio(
        "Page navigation",
        options=[LEGACY_WORKBENCH_PAGE, SCREENING_PAGE],
        index=0,
    )

    if page == SCREENING_PAGE:
        render_screening_page()
    else:
        legacy_app.render_legacy_workbench()


if __name__ == "__main__":
    main()
