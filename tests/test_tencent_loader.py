import importlib

from data.tencent_loader import OUTPUT_COLUMNS, load_tencent_a_share_spot


class FakeResponse:
    status_code = 200

    def __init__(self, payload_text):
        self.text = payload_text

    def raise_for_status(self):
        return None


def test_tencent_loader_importable():
    assert importlib.import_module("data.tencent_loader")


def test_tencent_loader_maps_realtime_fields(monkeypatch):
    rows = []
    for index in range(1100):
        parts = [""] * 38
        parts[0] = "1"
        parts[1] = f"Sample {index}"
        parts[2] = f"6{index:05d}"
        parts[3] = "10.1"
        parts[4] = "9.9"
        parts[5] = "9.8"
        parts[30] = "20260612150000"
        parts[31] = "0.2"
        parts[32] = "1.5"
        parts[33] = "10.5"
        parts[34] = "9.7"
        parts[36] = "1000"
        parts[37] = "2000"
        rows.append(f'v_sh6{index:05d}="' + "~".join(parts) + '";')
    quote_rows = "\n".join(rows)

    def fake_get(*args, **kwargs):
        return FakeResponse(quote_rows)

    monkeypatch.setattr("requests.get", fake_get)
    result = load_tencent_a_share_spot(timeout=1)

    assert list(result.columns) == OUTPUT_COLUMNS
    assert len(result) > 1000
    assert result.iloc[0]["ticker"] == "600000"
    assert result.iloc[0]["data_source"] == "Tencent Realtime"
    assert result.attrs["data_status"] == "Live"
    assert result.attrs["endpoint_attempts"]


def test_tencent_loader_failure_returns_empty(monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError("mock timeout")

    monkeypatch.setattr("requests.get", fail)
    result = load_tencent_a_share_spot(timeout=1)

    assert result.empty
    assert result.attrs["data_source"] == "Tencent Realtime"
    assert result.attrs["data_status"] == "Error"
    assert "returned 0 mapped rows" in result.attrs["last_error"]
