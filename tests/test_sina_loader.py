import importlib
import json

from data.sina_loader import OUTPUT_COLUMNS, load_sina_a_share_spot


class FakeResponse:
    status_code = 200

    def __init__(self, payload_text):
        self.text = payload_text

    def raise_for_status(self):
        return None


def test_sina_loader_importable():
    assert importlib.import_module("data.sina_loader")


def test_sina_loader_maps_realtime_fields(monkeypatch):
    rows = [
        {
            "symbol": f"sh6{index:05d}",
            "name": f"Sample {index}",
            "trade": "10.1",
            "pricechange": "0.2",
            "changepercent": "1.5",
            "volume": "1000",
            "amount": "2000",
            "open": "9.9",
            "high": "10.5",
            "low": "9.8",
            "settlement": "9.9",
        }
        for index in range(1100)
    ]
    calls = {"count": 0}

    def fake_get(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return FakeResponse(json.dumps(rows))
        return FakeResponse("[]")

    monkeypatch.setattr("requests.get", fake_get)
    result = load_sina_a_share_spot(timeout=1)

    assert list(result.columns) == OUTPUT_COLUMNS
    assert len(result) > 1000
    assert result.iloc[0]["ticker"] == "600000"
    assert result.iloc[0]["data_source"] == "Sina Realtime"
    assert result.attrs["data_status"] == "Live"
    assert result.attrs["endpoint_attempts"]


def test_sina_loader_failure_returns_empty(monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError("mock timeout")

    monkeypatch.setattr("requests.get", fail)
    result = load_sina_a_share_spot(timeout=1)

    assert result.empty
    assert result.attrs["data_source"] == "Sina Realtime"
    assert result.attrs["data_status"] == "Error"
    assert "returned 0 mapped rows" in result.attrs["last_error"]
