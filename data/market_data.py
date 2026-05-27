"""Market data helpers used by the screening workflow.

This module owns low-risk market-data formatting and cleaning helpers.
Network data fetch functions are still implemented in ``legacy_app.py`` during
the V1.2.x transition and are exposed here through lazy compatibility wrappers
so the AkShare -> BaoStock -> yfinance fallback order remains unchanged.
"""

import re

import pandas as pd


def normalize_yfinance_data(data):
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = data.columns.get_level_values(0)
    return data


def normalize_hk_symbol_for_akshare(symbol):
    return symbol.upper().replace(".HK", "").zfill(5)


def normalize_a_share_symbol_for_akshare(symbol):
    return str(symbol or "").strip().upper().replace(".SH", "").replace(".SZ", "")


def infer_a_share_yfinance_suffix(symbol):
    query_symbol = normalize_a_share_symbol_for_akshare(symbol)
    if query_symbol.startswith("6"):
        return ".SS"
    if query_symbol.startswith(("0", "3")):
        return ".SZ"
    return ""


def normalize_a_share_symbol_for_yfinance(symbol):
    query_symbol = normalize_a_share_symbol_for_akshare(symbol)
    suffix = infer_a_share_yfinance_suffix(query_symbol)
    return f"{query_symbol}{suffix}" if suffix else ""


def convert_a_share_to_yfinance_ticker(query_ticker):
    query_symbol = normalize_a_share_symbol_for_akshare(query_ticker)
    if not re.fullmatch(r"\d{6}", query_symbol):
        return None, "A股 yfinance 查询代码必须先标准化为 6 位数字。"
    if query_symbol.startswith("6"):
        return f"{query_symbol}.SS", ""
    if query_symbol.startswith(("0", "2", "3")):
        return f"{query_symbol}.SZ", ""
    return None, "无法根据 A股代码首位判断 yfinance 后缀。"


def convert_a_share_to_baostock_code(query_ticker):
    query_symbol = normalize_a_share_symbol_for_akshare(query_ticker)
    if not re.fullmatch(r"\d{6}", query_symbol):
        return None, "A股 BaoStock 查询代码必须先标准化为 6 位数字。"
    if query_symbol.startswith("6"):
        return f"sh.{query_symbol}", ""
    if query_symbol.startswith(("0", "2", "3")):
        return f"sz.{query_symbol}", ""
    return None, "无法根据 A股代码首位判断 BaoStock 市场前缀。"


def get_screening_fallback_source(market):
    if market == "A股":
        return "BaoStock / yfinance"
    if market == "港股":
        return "yfinance"
    return "无"


def normalize_price_dataframe(raw_data):
    if raw_data is None or raw_data.empty:
        return pd.DataFrame()

    data = normalize_yfinance_data(raw_data.copy())
    column_map = {
        "日期": "Date",
        "开盘": "Open",
        "最高": "High",
        "最低": "Low",
        "收盘": "Close",
        "成交量": "Volume",
        "成交额": "Turnover",
        "Adj Close": "Adj Close",
    }
    data = data.rename(columns=column_map)

    if "Date" not in data.columns:
        data = data.reset_index()
        first_col = data.columns[0]
        data = data.rename(columns={first_col: "Date"})

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])
    data = data.sort_values("Date")
    duplicate_dates_removed = int(data["Date"].duplicated().sum())
    data = data.drop_duplicates(subset=["Date"], keep="last")

    standard_columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Turnover", "Adj Close"]
    keep_columns = [col for col in standard_columns if col in data.columns]
    data = data[keep_columns]

    for col in ["Open", "High", "Low", "Close", "Volume", "Turnover", "Adj Close"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.set_index("Date", drop=False)
    data.attrs["duplicate_dates_removed"] = duplicate_dates_removed
    return data


def keep_recent_rows(price_df, limit_rows=120):
    if price_df is None or price_df.empty or not limit_rows:
        return price_df
    recent = price_df.tail(limit_rows).copy()
    recent.attrs.update(price_df.attrs)
    return recent


def fetch_a_share_baostock_data(*args, **kwargs):
    from legacy_app import fetch_a_share_baostock_data as _impl

    return _impl(*args, **kwargs)


def fetch_a_share_history(*args, **kwargs):
    from legacy_app import fetch_a_share_history as _impl

    return _impl(*args, **kwargs)


def fetch_screening_price_data(*args, **kwargs):
    from legacy_app import fetch_screening_price_data as _impl

    return _impl(*args, **kwargs)


def fetch_yfinance_history(*args, **kwargs):
    from legacy_app import fetch_yfinance_history as _impl

    return _impl(*args, **kwargs)


def screen_universe_data_fetch(*args, **kwargs):
    from legacy_app import screen_universe_data_fetch as _impl

    return _impl(*args, **kwargs)


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
    "normalize_hk_symbol_for_akshare",
    "normalize_price_dataframe",
    "normalize_yfinance_data",
    "screen_universe_data_fetch",
]
