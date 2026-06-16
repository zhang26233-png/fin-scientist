import importlib

import pandas as pd

from data.source_center import SOURCE_STATUS_COLUMNS, build_data_source_status


def test_source_center_importable():
    assert importlib.import_module("data.source_center")


def test_source_status_fields_complete():
    frame = pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample",
                "capital_flow_score": 60,
                "news_event_score": 50,
                "industry_strength_score": 55,
            }
        ]
    )
    frame.attrs["data_source"] = "Tencent Realtime"
    frame.attrs["data_status"] = "Live"
    frame.attrs["source_attempts"] = [{"data_source": "Tencent Realtime", "rows": 1, "data_status": "Live", "last_error": ""}]
    frame.attrs["capital_flow_status"] = "Available"
    frame.attrs["capital_flow_rows"] = 1
    frame.attrs["news_status"] = "Available"
    frame.attrs["news_rows"] = 1
    frame.attrs["industry_status"] = "Available"
    frame.attrs["industry_rows"] = 1

    status = build_data_source_status(frame)

    assert list(status.columns) == SOURCE_STATUS_COLUMNS
    assert set(status["source_name"]) >= {
        "Tencent Realtime",
        "EastMoney Realtime",
        "Sina Realtime",
        "AkShare Kline",
        "EastMoney Fundamental",
        "Capital Flow",
        "News",
        "Industry",
        "Local Cache",
    }


def test_source_center_empty_frame_does_not_crash():
    status = build_data_source_status(pd.DataFrame())

    assert isinstance(status, pd.DataFrame)
    assert len(status) >= 9
