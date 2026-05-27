"""Market data helpers used by the screening workflow.

The concrete implementations remain unchanged from V1.1. This module gives
V1.2 a stable import boundary while preserving the AkShare -> BaoStock ->
yfinance fallback order and existing Streamlit cache behavior.
"""

from legacy_app import (
    convert_a_share_to_baostock_code,
    convert_a_share_to_yfinance_ticker,
    fetch_a_share_baostock_data,
    fetch_a_share_history,
    fetch_screening_price_data,
    fetch_yfinance_history,
    get_screening_fallback_source,
    infer_a_share_yfinance_suffix,
    keep_recent_rows,
    normalize_a_share_symbol_for_akshare,
    normalize_a_share_symbol_for_yfinance,
    normalize_price_dataframe,
    screen_universe_data_fetch,
)

__all__ = [
    "convert_a_share_to_baostock_code",
    "convert_a_share_to_yfinance_ticker",
    "fetch_a_share_baostock_data",
    "fetch_a_share_history",
    "fetch_screening_price_data",
    "fetch_yfinance_history",
    "get_screening_fallback_source",
    "infer_a_share_yfinance_suffix",
    "keep_recent_rows",
    "normalize_a_share_symbol_for_akshare",
    "normalize_a_share_symbol_for_yfinance",
    "normalize_price_dataframe",
    "screen_universe_data_fetch",
]
