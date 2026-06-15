import importlib

import pandas as pd

from data.a_share_loader import load_a_share_universe
from data.eastmoney_loader import OUTPUT_COLUMNS, load_eastmoney_a_share_spot


class FakeResponse:
    status_code = 200
    text = '{"mock": true}'

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeBadGateway(FakeResponse):
    status_code = 502
    text = "<html><title>502 Bad Gateway</title>"

    def __init__(self):
        super().__init__({})

    def raise_for_status(self):
        import requests

        raise requests.HTTPError("502 Bad Gateway")


def test_eastmoney_loader_importable():
    assert importlib.import_module("data.eastmoney_loader")


def test_eastmoney_loader_maps_realtime_fields(monkeypatch):
    payload = {
        "data": {
            "diff": [
                {
                    "f12": f"6{index:05d}",
                    "f14": f"Sample {index}",
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
                for index in range(1100)
            ]
        }
    }
    calls = {"count": 0}

    def fake_get(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return FakeResponse(payload)
        return FakeResponse({"data": {"diff": []}})

    monkeypatch.setattr("requests.get", fake_get)
    result = load_eastmoney_a_share_spot(timeout=1)

    assert list(result.columns) == OUTPUT_COLUMNS
    assert result.iloc[0]["ticker"] == "600000"
    assert result.iloc[0]["name"] == "Sample 0"
    assert result.iloc[0]["data_source"] == "EastMoney Direct"
    assert result.iloc[0]["data_status"] == "Live"
    assert result.attrs["request_url"]
    assert result.attrs["http_status"] == 200
    assert result.attrs["raw_preview"]
    assert result.attrs["active_endpoint"]
    assert result.attrs["endpoint_attempts"]


def test_eastmoney_loader_failure_returns_empty(monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError("mock timeout")

    monkeypatch.setattr("requests.get", fail)
    result = load_eastmoney_a_share_spot(timeout=1)

    assert result.empty
    assert result.attrs["data_source"] == "EastMoney Direct"
    assert result.attrs["data_status"] == "Error"
    assert "mock timeout" in result.attrs["last_error"]
    assert "request_url" in result.attrs
    assert "http_status" in result.attrs
    assert "raw_preview" in result.attrs


def test_eastmoney_empty_diff_reports_debug(monkeypatch):
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: FakeResponse({"data": {"diff": []}}))
    result = load_eastmoney_a_share_spot(timeout=1)

    assert result.empty
    assert result.attrs["data_status"] == "Error"
    assert "diff" in result.attrs["last_error"]
    assert result.attrs["request_url"]
    assert result.attrs["http_status"] == 200
    assert result.attrs["raw_preview"]


def test_eastmoney_falls_back_to_next_endpoint_after_502(monkeypatch):
    payload = {
        "data": {
            "diff": [
                {
                    "f12": f"6{index:05d}",
                    "f14": f"Sample {index}",
                    "f2": "-",
                    "f3": 1.0,
                    "f4": 0.1,
                    "f5": 1000,
                    "f6": 10000,
                    "f7": 1.5,
                    "f15": 10.5,
                    "f16": 9.8,
                    "f17": 10.0,
                    "f18": 9.9,
                }
                for index in range(1100)
            ]
        }
    }
    calls = {"count": 0}

    def fake_get(url, *args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return FakeBadGateway()
        if calls["count"] == 2:
            return FakeResponse(payload)
        return FakeResponse({"data": {"diff": []}})

    monkeypatch.setattr("requests.get", fake_get)
    result = load_eastmoney_a_share_spot(timeout=1)

    assert len(result) > 1000
    assert result.attrs["data_status"] == "Live"
    assert result.attrs["active_endpoint"]
    assert len(result.attrs["endpoint_attempts"]) >= 2
    assert result["latest_price"].isna().all()


def test_a_share_loader_uses_eastmoney_when_large(monkeypatch):
    rows = [
        {
            "ticker": f"6{index:05d}",
            "name": f"Sample {index}",
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

    empty = pd.DataFrame()
    empty.attrs["last_error"] = "mock empty"
    monkeypatch.setattr("data.a_share_loader.load_tencent_a_share_spot", lambda timeout=10: empty)
    monkeypatch.setattr("data.a_share_loader.load_sina_a_share_spot", lambda timeout=10: empty)
    monkeypatch.setattr("data.a_share_loader.load_eastmoney_a_share_spot", lambda timeout=30: frame)
    result = load_a_share_universe(timeout=1)

    assert len(result) > 1000
    assert result.attrs["data_source"] == "EastMoney Direct"
    assert result.attrs["data_status"] == "Live"
    assert {"ticker", "name", "data_source", "data_status"}.issubset(result.columns)
