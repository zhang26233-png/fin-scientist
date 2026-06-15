from pathlib import Path

import pandas as pd

from data import local_cache


def test_write_and_read_a_share_universe_cache(tmp_path, monkeypatch):
    universe_path = tmp_path / "a_share_universe_latest.csv"
    quotes_path = tmp_path / "a_share_quotes_latest.csv"
    monkeypatch.setattr(local_cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(local_cache, "A_SHARE_UNIVERSE_CACHE", universe_path)
    monkeypatch.setattr(local_cache, "A_SHARE_QUOTES_CACHE", quotes_path)

    frame = pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample",
                "latest_price": 10.0,
                "data_source": "Test",
                "data_status": "Live",
            }
        ]
    )

    metadata = local_cache.write_a_share_cache(universe=frame, quotes=frame)
    cached = local_cache.read_a_share_universe_cache()

    assert Path(metadata["cache_universe_path"]) == universe_path
    assert Path(metadata["cache_quotes_path"]) == quotes_path
    assert metadata["cache_status"] == "Available"
    assert len(cached) == 1
    assert cached.iloc[0]["ticker"] == "600000"
    assert cached.attrs["cache_status"] == "Available"


def test_missing_cache_returns_empty_with_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(local_cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(local_cache, "A_SHARE_UNIVERSE_CACHE", tmp_path / "missing_universe.csv")
    monkeypatch.setattr(local_cache, "A_SHARE_QUOTES_CACHE", tmp_path / "missing_quotes.csv")

    cached = local_cache.read_a_share_universe_cache()

    assert cached.empty
    assert cached.attrs["cache_status"] == "Missing"
    assert "missing" in cached.attrs["last_error"].lower()
