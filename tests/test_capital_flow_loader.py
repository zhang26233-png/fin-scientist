import pandas as pd

from data import capital_flow_loader as loader


def test_capital_flow_empty_data_does_not_crash():
    result = loader.build_capital_flow_dataset(pd.DataFrame(), use_external=False)

    assert isinstance(result, pd.DataFrame)
    for field in loader.CAPITAL_FLOW_COLUMNS:
        assert field in result.columns


def test_capital_flow_existing_fields_are_standardized():
    source = pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample",
                "turnover": "300000000",
                "turnover_rate": "3.5",
                "volume_ratio": "1.4",
                "main_net_inflow": "10000000",
                "main_net_inflow_ratio": "2.5",
            }
        ]
    )

    result = loader.build_capital_flow_dataset(source, use_external=False)

    assert result.loc[0, "ticker"] == "600000"
    assert result.loc[0, "capital_activity_score"] > 50
    assert result.loc[0, "capital_flow_score"] > 50


def test_capital_flow_cache_read_write(tmp_path, monkeypatch):
    cache_file = tmp_path / "capital_flow_latest.csv"
    monkeypatch.setattr(loader, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(loader, "CACHE_FILE", cache_file)
    monkeypatch.setattr(loader, "MIN_CACHE_ROWS", 1)
    frame = loader.build_capital_flow_dataset(
        pd.DataFrame([{"ticker": "600000", "name": "Sample", "turnover": 1_000_000_000}]),
        use_external=False,
    )

    saved = loader.save_cached_capital_flow(frame)
    cached = loader.load_cached_capital_flow()

    assert saved["cache_status"] == "Available"
    assert len(cached) == 1
    assert cached.loc[0, "ticker"] == "600000"
