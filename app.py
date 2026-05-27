"""FinScientist Streamlit entrypoint.

V1.2 keeps app.py lightweight and routes feature pages to dedicated modules.
"""

import streamlit as st

import legacy_app
from ui.screening_ui import render_screening_page

APP_VERSION = "V1.2.6"

# Re-export core functions used by the existing tests and notebooks.
calculate_indicators = legacy_app.calculate_indicators
calculate_backtest_metrics = legacy_app.calculate_backtest_metrics
generate_backtest_signals = legacy_app.generate_backtest_signals
check_price_data_quality = legacy_app.check_price_data_quality


def main():
    st.set_page_config(page_title="FinScientist", page_icon="\U0001f4c8", layout="wide")
    st.title("FinScientist")
    st.caption('V1.2.6 \u67b6\u6784\u6e05\u7406\uff1b\u6240\u6709\u7ed3\u679c\u4ec5\u4f9b\u5b66\u4e60\u548c\u7814\u7a76\uff0c\u4e0d\u6784\u6210\u6295\u8d44\u5efa\u8bae\u3002')

    page = st.sidebar.radio(
        '\u9875\u9762\u5bfc\u822a',
        options=['\u7814\u7a76\u5de5\u4f5c\u53f0', '\u81ea\u52a8\u7814\u7a76\u5bf9\u8c61\u7b5b\u9009'],
        index=0,
    )

    if page == '\u81ea\u52a8\u7814\u7a76\u5bf9\u8c61\u7b5b\u9009':
        render_screening_page()
    else:
        legacy_app.render_legacy_app()


if __name__ == "__main__":
    main()
