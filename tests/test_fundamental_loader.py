import importlib

import pandas as pd

from data import fundamental_loader as loader


def test_existing_df_field_mapping():
    source = pd.DataFrame([{"code": "SH600001", "name": "Alpha", "pe": "12", "pb": "1.2", "roe": "18%"}])
    result = loader.load_fundamental_from_existing_df(source)

    assert result.loc[0, "ticker"] == "600001"
    assert result.loc[0, "pe_ttm"] == 12
    assert result.loc[0, "pb"] == 1.2
    assert result.loc[0, "roe"] == 18


def test_numeric_and_percent_conversion():
    source = pd.DataFrame([{"ticker": "600001", "roe": 0.2, "revenue_growth_yoy": "15%", "market_cap": "1,000"}])
    result = loader.load_fundamental_from_existing_df(source)

    assert result.loc[0, "roe"] == 20
    assert result.loc[0, "revenue_growth_yoy"] == 15
    assert result.loc[0, "market_cap"] == 1000


def test_empty_data_safe_return():
    result = loader.load_fundamental_from_existing_df(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == loader.FUNDAMENTAL_OUTPUT_COLUMNS


def test_cache_read_write(tmp_path, monkeypatch):
    cache_file = tmp_path / "fundamental_latest.csv"
    monkeypatch.setattr(loader, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(loader, "CACHE_FILE", cache_file)
    df = pd.DataFrame(
        [
            {"ticker": f"6{index:05d}", "name": f"S{index}", "pe_ttm": 10, "pb": 1.2}
            for index in range(loader.MIN_CACHE_ROWS)
        ]
    )
    standardized = loader.load_fundamental_from_existing_df(df)

    meta = loader.save_cached_fundamental(standardized)
    loaded = loader.load_cached_fundamental()

    assert meta["cache_status"] == "Available"
    assert len(loaded) == loader.MIN_CACHE_ROWS
    assert loaded.attrs["cache_status"] == "Available"


def test_cache_missing_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(loader, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(loader, "CACHE_FILE", tmp_path / "missing.csv")

    result = loader.load_cached_fundamental()

    assert result.empty
    assert result.attrs["fundamental_data_status"] == "Unavailable"


def test_eastmoney_mapping_from_mocked_response(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": {"diff": [{"f12": "600001", "f14": "Alpha", "f9": 12, "f23": 1.4, "f20": 1000}]}}

    monkeypatch.setattr(loader.requests, "get", lambda *args, **kwargs: Response())

    result = loader.load_fundamental_from_eastmoney(tickers=["600001"])

    assert result.loc[0, "ticker"] == "600001"
    assert result.loc[0, "pe_ttm"] == 12
    assert result.loc[0, "market_cap"] == 1000


def test_external_failure_falls_back_to_cache(tmp_path, monkeypatch):
    cache_file = tmp_path / "fundamental_latest.csv"
    monkeypatch.setattr(loader, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(loader, "CACHE_FILE", cache_file)
    cache_df = loader.load_fundamental_from_existing_df(
        pd.DataFrame([{"ticker": "600001", "pe_ttm": 10, "pb": 1.2, "roe": 18}])
    )
    cache_df.to_csv(cache_file, index=False)
    monkeypatch.setattr(loader, "load_fundamental_from_eastmoney", lambda *args, **kwargs: pd.DataFrame(columns=loader.FUNDAMENTAL_OUTPUT_COLUMNS))
    monkeypatch.setattr(loader, "load_fundamental_from_akshare", lambda *args, **kwargs: pd.DataFrame(columns=loader.FUNDAMENTAL_OUTPUT_COLUMNS))

    result = loader.build_fundamental_dataset(pd.DataFrame([{"ticker": "600001"}]), tickers=["600001"])

    assert result.loc[0, "pe_ttm"] == 10
    assert result.attrs["fundamental_data_status"] == "Available"


def test_order_preserved_when_merging_external(monkeypatch):
    external = loader.load_fundamental_from_existing_df(
        pd.DataFrame([{"ticker": "600002", "pe_ttm": 20}, {"ticker": "600001", "pe_ttm": 10}])
    )
    monkeypatch.setattr(loader, "load_fundamental_from_eastmoney", lambda *args, **kwargs: external)
    monkeypatch.setattr(loader, "load_fundamental_from_akshare", lambda *args, **kwargs: pd.DataFrame(columns=loader.FUNDAMENTAL_OUTPUT_COLUMNS))
    source = pd.DataFrame([{"ticker": "600001"}, {"ticker": "600002"}])

    result = loader.build_fundamental_dataset(source, tickers=["600001", "600002"])

    assert result["ticker"].tolist()[:2] == ["600001", "600002"]


def test_single_bad_row_does_not_block_other_rows():
    source = pd.DataFrame([{"ticker": None, "pe_ttm": 10}, {"ticker": "600001", "pe_ttm": 12}])
    result = loader.load_fundamental_from_existing_df(source)

    assert result["ticker"].tolist() == ["600001"]


def test_maximum_public_api_module_importable():
    assert importlib.import_module("data.fundamental_loader")
