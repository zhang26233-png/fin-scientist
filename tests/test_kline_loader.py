import importlib

import pandas as pd

from data import kline_loader
from data.kline_loader import (
    KLINE_COLUMNS,
    build_price_history_dict,
    load_a_share_kline,
    load_batch_a_share_klines,
    load_cached_kline,
    normalize_ticker,
    save_cached_kline,
)


def raw_kline(rows=80, ticker="600001"):
    dates = pd.date_range("2025-01-01", periods=rows, freq="D")
    return pd.DataFrame(
        {
            "日期": dates[::-1],
            "开盘": [10 + index * 0.1 for index in range(rows)],
            "最高": [10.5 + index * 0.1 for index in range(rows)],
            "最低": [9.5 + index * 0.1 for index in range(rows)],
            "收盘": [10.2 + index * 0.1 for index in range(rows)],
            "成交量": [1_000_000 + index for index in range(rows)],
            "成交额": [20_000_000 + index for index in range(rows)],
            "ticker": ticker,
        }
    )


def test_ticker_format_compatible():
    assert normalize_ticker("sh600001") == "600001"
    assert normalize_ticker("600001.SH") == "600001"
    assert normalize_ticker(1) == "000001"


def test_empty_ticker_safe_return():
    result = load_a_share_kline("")

    assert result.empty
    assert result.attrs["data_status"] == "Error"


def test_single_kline_fields_standardized(monkeypatch):
    monkeypatch.setattr(kline_loader, "_fetch_akshare_kline", lambda *args, **kwargs: kline_loader._normalize_kline_frame(raw_kline(), "600001", data_source="Test", data_status="Live"))

    result = load_a_share_kline("600001")

    assert list(result.columns) == KLINE_COLUMNS
    assert result.iloc[0]["ticker"] == "600001"


def test_date_ascending(monkeypatch):
    monkeypatch.setattr(kline_loader, "_fetch_akshare_kline", lambda *args, **kwargs: kline_loader._normalize_kline_frame(raw_kline(), "600001", data_source="Test", data_status="Live"))

    result = load_a_share_kline("600001")

    assert result["date"].is_monotonic_increasing


def test_numeric_fields_are_numeric(monkeypatch):
    monkeypatch.setattr(kline_loader, "_fetch_akshare_kline", lambda *args, **kwargs: kline_loader._normalize_kline_frame(raw_kline(), "600001", data_source="Test", data_status="Live"))

    result = load_a_share_kline("600001")

    for field in ["open", "high", "low", "close", "volume", "turnover"]:
        assert pd.api.types.is_numeric_dtype(result[field])


def test_rows_over_60_write_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(kline_loader, "KLINE_CACHE_DIR", tmp_path)

    attrs = save_cached_kline("600001", raw_kline(rows=80))

    assert attrs["cache_status"] == "Saved"
    assert (tmp_path / "600001.csv").exists()


def test_external_failure_reads_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(kline_loader, "KLINE_CACHE_DIR", tmp_path)
    save_cached_kline("600001", raw_kline(rows=80))
    monkeypatch.setattr(kline_loader, "_fetch_akshare_kline", lambda *args, **kwargs: kline_loader._empty("600001", last_error="external failed"))

    result = load_a_share_kline("600001")

    assert not result.empty
    assert result.attrs["data_status"] == "Cache"
    assert result.attrs["cache_status"] == "Hit"


def test_cache_missing_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(kline_loader, "KLINE_CACHE_DIR", tmp_path)

    result = load_cached_kline("600001")

    assert result.empty
    assert result.attrs["cache_status"] == "Missing"


def test_build_price_history_dict_returns_dict(monkeypatch):
    frame = kline_loader._normalize_kline_frame(raw_kline(), "600001", data_source="Test", data_status="Live")
    monkeypatch.setattr(kline_loader, "load_a_share_kline", lambda ticker, **kwargs: frame.copy(deep=True))

    result = build_price_history_dict(["600001"], max_stocks=1)

    assert isinstance(result, dict)
    assert "600001" in result


def test_single_failure_does_not_affect_other_ticker(monkeypatch):
    def fake_load(ticker, **kwargs):
        if str(ticker) == "600002":
            return pd.DataFrame(columns=KLINE_COLUMNS)
        return kline_loader._normalize_kline_frame(raw_kline(ticker=str(ticker)), str(ticker), data_source="Test", data_status="Live")

    monkeypatch.setattr(kline_loader, "load_a_share_kline", fake_load)

    result = load_batch_a_share_klines(["600001", "600002", "600003"], sleep_seconds=0)

    assert "600001" in result
    assert "600003" in result
    assert "600002" not in result
    assert result["_attrs"]["failures"] == 1


def test_max_stocks_effective(monkeypatch):
    calls = []

    def fake_load(ticker, **kwargs):
        calls.append(ticker)
        return kline_loader._normalize_kline_frame(raw_kline(ticker=str(ticker)), str(ticker), data_source="Test", data_status="Live")

    monkeypatch.setattr(kline_loader, "load_a_share_kline", fake_load)

    result = load_batch_a_share_klines(["600001", "600002", "600003"], max_stocks=2, sleep_seconds=0)

    assert calls == ["600001", "600002"]
    assert result["_attrs"]["requested"] == 2


def test_module_importable():
    assert importlib.import_module("data.kline_loader")
