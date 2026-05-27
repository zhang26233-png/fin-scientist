import os

import pandas as pd


os.environ["FINSCIENTIST_SKIP_UI"] = "1"

import legacy_app  # noqa: E402
from data.market_data import (  # noqa: E402
    convert_a_share_to_baostock_code,
    convert_a_share_to_yfinance_ticker,
    get_screening_fallback_source,
    infer_a_share_yfinance_suffix,
    keep_recent_rows,
    normalize_a_share_symbol_for_akshare,
    normalize_a_share_symbol_for_yfinance,
    normalize_hk_symbol_for_akshare,
    normalize_price_dataframe,
)


def test_market_symbol_helpers_match_legacy_path():
    symbols = ["600519.SH", "300750.SZ", "000001", "", None]

    for symbol in symbols:
        assert normalize_a_share_symbol_for_akshare(symbol) == legacy_app.normalize_a_share_symbol_for_akshare(symbol)
        assert infer_a_share_yfinance_suffix(symbol) == legacy_app.infer_a_share_yfinance_suffix(symbol)
        assert normalize_a_share_symbol_for_yfinance(symbol) == legacy_app.normalize_a_share_symbol_for_yfinance(symbol)
        assert convert_a_share_to_yfinance_ticker(symbol) == legacy_app.convert_a_share_to_yfinance_ticker(symbol)
        assert convert_a_share_to_baostock_code(symbol) == legacy_app.convert_a_share_to_baostock_code(symbol)

    assert normalize_hk_symbol_for_akshare("700.HK") == legacy_app.normalize_hk_symbol_for_akshare("700.HK")
    assert get_screening_fallback_source("A股") == legacy_app.get_screening_fallback_source("A股")


def test_normalize_price_dataframe_keeps_structure_and_attrs():
    raw = pd.DataFrame(
        {
            "日期": ["2024-01-02", "2024-01-01", "2024-01-02", "bad-date"],
            "开盘": ["10.1", "9.8", "10.2", "11"],
            "最高": ["10.5", "10.0", "10.6", "12"],
            "最低": ["9.9", "9.5", "10.0", "10"],
            "收盘": ["10.3", "9.9", "10.4", "11"],
            "成交量": ["1000", "900", "1200", "1300"],
        }
    )

    result = normalize_price_dataframe(raw)
    legacy_result = legacy_app.normalize_price_dataframe(raw)

    pd.testing.assert_frame_equal(result, legacy_result)
    assert result.index.name == "Date"
    assert result.attrs["duplicate_dates_removed"] == 1
    assert result["Close"].iloc[-1] == 10.4


def test_normalize_price_dataframe_handles_empty_missing_and_multiindex():
    assert normalize_price_dataframe(pd.DataFrame()).empty
    assert normalize_price_dataframe(None).empty

    columns = pd.MultiIndex.from_tuples([("Close", "AAA"), ("Volume", "AAA")])
    raw = pd.DataFrame([[10, 100], [11, 120]], columns=columns, index=pd.date_range("2024-01-01", periods=2))
    result = normalize_price_dataframe(raw)

    assert list(result.columns) == ["Date", "Close", "Volume"]
    assert len(result) == 2


def test_keep_recent_rows_preserves_attrs_and_legacy_path():
    frame = pd.DataFrame({"Close": range(5)}, index=pd.date_range("2024-01-01", periods=5))
    frame.attrs["source"] = "test"

    result = keep_recent_rows(frame, 2)
    legacy_result = legacy_app.keep_recent_rows(frame, 2)

    pd.testing.assert_frame_equal(result, legacy_result)
    assert result.attrs["source"] == "test"
    assert result["Close"].tolist() == [3, 4]
    assert keep_recent_rows(frame, None) is frame
