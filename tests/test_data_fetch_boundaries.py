import os

import pandas as pd


os.environ["FINSCIENTIST_SKIP_UI"] = "1"

import legacy_app  # noqa: E402
from data import fundamental_data, market_data  # noqa: E402
from core.scoring import FUNDAMENTAL_FIELDS  # noqa: E402


def clear_streamlit_caches():
    for func in (legacy_app.fetch_screening_price_data, legacy_app.get_fundamental_data):
        clear = getattr(func, "clear", None)
        if callable(clear):
            clear()


def make_ticker_item():
    return {
        "原始输入": "600519",
        "股票名称": "贵州茅台",
        "stock_name": "贵州茅台",
        "展示代码": "600519.SH",
        "内部查询代码": "600519",
        "市场": "A股",
        "行业": "食品饮料",
        "板块": "白酒",
        "主题标签": "消费",
        "industry": "食品饮料",
        "sector": "白酒",
        "themes": "消费",
        "is_valid": True,
    }


def make_price_frame():
    frame = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=70, freq="D"),
            "Close": [100 + index for index in range(70)],
            "Volume": [1000 + index for index in range(70)],
        }
    )
    frame = frame.set_index("Date", drop=False)
    return frame


def empty_source(stage, message, attempt):
    frame = pd.DataFrame()
    frame.attrs.update(
        {
            "failure_stage": stage,
            "error_message": message,
            "attempt_params": attempt,
        }
    )
    return frame


def test_fetch_a_share_fundamental_data_handles_empty_and_exception(monkeypatch):
    monkeypatch.setattr(legacy_app, "fetch_a_share_info", lambda query_ticker: {})
    data, error = fundamental_data.fetch_a_share_fundamental_data("600519.SH", "600519")

    assert data is None
    assert isinstance(error, str)

    def raise_error(query_ticker):
        raise RuntimeError("mock fundamental failure")

    monkeypatch.setattr(legacy_app, "fetch_a_share_info", raise_error)
    data, error = legacy_app.fetch_a_share_fundamental_data("600519.SH", "600519")

    assert data is None
    assert "mock fundamental failure" in error


def test_get_fundamental_data_uses_sample_when_akshare_fails(monkeypatch):
    clear_streamlit_caches()
    monkeypatch.setattr(legacy_app, "fetch_a_share_fundamental_data", lambda display, query: (None, "mock akshare empty"))

    result = fundamental_data.get_fundamental_data("600519.SH", "600519", "A股")

    assert set(FUNDAMENTAL_FIELDS).issubset(result)
    assert result["fundamental_source"] == "内置示例数据"
    assert result["fundamental_error"] == "mock akshare empty"


def test_get_fundamental_data_keeps_non_a_share_safe_record():
    clear_streamlit_caches()

    result = legacy_app.get_fundamental_data("AAPL", "AAPL", "美股")

    assert set(FUNDAMENTAL_FIELDS).issubset(result)
    assert result["fundamental_source"] == "数据暂缺"
    assert result["fundamental_error"]


def test_fetch_screening_price_data_falls_back_from_akshare_to_baostock(monkeypatch):
    clear_streamlit_caches()
    baostock_frame = make_price_frame()
    baostock_frame.attrs.update({"successful_adjust": "mock baostock", "actual_query_symbol": "sh.600519"})

    monkeypatch.setattr(
        legacy_app,
        "fetch_a_share_history",
        lambda *args, **kwargs: empty_source("AkShare mock empty", "ak empty", "ak mock"),
    )
    monkeypatch.setattr(legacy_app, "fetch_a_share_baostock_data", lambda *args, **kwargs: baostock_frame)

    def fail_yfinance(*args, **kwargs):
        raise AssertionError("yfinance should not be called after BaoStock succeeds")

    monkeypatch.setattr(legacy_app, "fetch_yfinance_history", fail_yfinance)

    result = market_data.fetch_screening_price_data(make_ticker_item(), "A股")

    assert result["success"] is True
    assert result["data_source"] == "BaoStock"
    assert result["fallback_used"] is True
    assert result["valid_trading_days"] == 70
    assert isinstance(result["price_df"], pd.DataFrame)


def test_fetch_screening_price_data_returns_stable_failure_when_all_sources_empty(monkeypatch):
    clear_streamlit_caches()

    monkeypatch.setattr(
        legacy_app,
        "fetch_a_share_history",
        lambda *args, **kwargs: empty_source("AkShare mock empty", "ak empty", "ak mock"),
    )
    monkeypatch.setattr(
        legacy_app,
        "fetch_a_share_baostock_data",
        lambda *args, **kwargs: empty_source("BaoStock mock empty", "bs empty", "bs mock"),
    )
    monkeypatch.setattr(
        legacy_app,
        "fetch_yfinance_history",
        lambda *args, **kwargs: empty_source("yfinance mock empty", "yf empty", "yf mock"),
    )

    result = legacy_app.fetch_screening_price_data(make_ticker_item(), "A股")

    assert result["success"] is False
    assert result["price_df"].empty
    assert result["akshare_error_summary"]
    assert result["baostock_error_summary"]
    assert result["yfinance_error_summary"]
    assert result["error_message"]


def test_fetch_screening_price_data_protects_missing_close_column(monkeypatch):
    clear_streamlit_caches()
    frame = pd.DataFrame({"Date": pd.date_range("2024-01-01", periods=3)})
    frame = frame.set_index("Date", drop=False)

    monkeypatch.setattr(legacy_app, "fetch_a_share_history", lambda *args, **kwargs: frame)

    result = market_data.fetch_screening_price_data(make_ticker_item(), "A股", a_share_source_mode="仅 AkShare")

    assert result["success"] is False
    assert result["failure_stage"] == "Close 字段缺失"
    assert "Close" in result["error_message"]
