import importlib

import pandas as pd

from data.eastmoney_loader import OUTPUT_COLUMNS, load_eastmoney_a_share_spot
from data.a_share_loader import load_a_share_universe


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_eastmoney_loader_importable():
    assert importlib.import_module("data.eastmoney_loader")


def test_eastmoney_loader_maps_realtime_fields(monkeypatch):
    payload = {
        "data": {
            "diff": [
                {
                    "f12": "600519",
                    "f14": "贵州茅台",
                    "f2": 1500.0,
                    "f3": 1.2,
                    "f4": 18.0,
                    "f5": 1000,
                    "f6": 2000000,
                    "f7": 2.1,
                    "f15": 1510.0,
                    "f16": 1480.0,
                    "f17": 1490.0,
                    "f18": 1482.0,
                }
            ]
        }
    }

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: FakeResponse(payload))
    result = load_eastmoney_a_share_spot(timeout=1)

    assert list(result.columns) == OUTPUT_COLUMNS
    assert result.iloc[0]["ticker"] == "600519"
    assert result.iloc[0]["name"] == "贵州茅台"
    assert result.iloc[0]["data_source"] == "EastMoney Direct"
    assert result.iloc[0]["data_status"] == "Live"


def test_eastmoney_loader_failure_returns_empty(monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError("mock timeout")

    monkeypatch.setattr("requests.get", fail)
    result = load_eastmoney_a_share_spot(timeout=1)

    assert result.empty
    assert result.attrs["data_source"] == "EastMoney Direct"
    assert result.attrs["data_status"] == "Error"
    assert result.attrs["last_error"]


def test_a_share_loader_uses_eastmoney_when_large(monkeypatch):
    rows = [
        {
            "ticker": f"6{index:05d}",
            "name": f"样本{index}",
            "latest_price": 10.0,
            "pct_change": 0.1,
            "volume": 1000,
            "turnover": 10000,
            "market": "沪市",
            "data_source": "EastMoney Direct",
            "data_status": "Live",
        }
        for index in range(1200)
    ]
    frame = pd.DataFrame(rows)
    frame.attrs["data_source"] = "EastMoney Direct"
    frame.attrs["data_status"] = "Live"
    frame.attrs["last_error"] = ""
    frame.attrs["load_time"] = 0.1

    monkeypatch.setattr("data.a_share_loader.load_eastmoney_a_share_spot", lambda timeout=30: frame)
    result = load_a_share_universe(timeout=1)

    assert len(result) > 1000
    assert result.attrs["data_source"] == "EastMoney Direct"
    assert result.attrs["data_status"] == "Live"
    assert {"ticker", "name", "data_source", "data_status"}.issubset(result.columns)
