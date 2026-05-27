import math
import os


os.environ["FINSCIENTIST_SKIP_UI"] = "1"

import legacy_app  # noqa: E402
from core.scoring import FUNDAMENTAL_FIELDS  # noqa: E402
from data.fundamental_data import (  # noqa: E402
    build_fundamental_record,
    clean_metric_value,
    get_fundamental_sample_data,
)


def test_build_fundamental_record_fills_missing_fields_and_matches_legacy():
    values = (1000, 12, 2.5)

    result = build_fundamental_record(values, "测试来源", "测试错误")
    legacy_result = legacy_app.build_fundamental_record(values, "测试来源", "测试错误")

    assert result == legacy_result
    assert set(FUNDAMENTAL_FIELDS).issubset(result)
    assert result["market_cap"] == 1000
    assert result["pe_ttm"] == 12
    assert result["pb"] == 2.5
    assert result["roe"] == "数据暂缺"
    assert result["fundamental_source"] == "测试来源"
    assert result["fundamental_error"] == "测试错误"


def test_get_fundamental_sample_data_supports_suffix_inference_and_legacy_path():
    direct = get_fundamental_sample_data("600519.SH")
    inferred = get_fundamental_sample_data("600519")

    assert direct == legacy_app.get_fundamental_sample_data("600519.SH")
    assert inferred == legacy_app.get_fundamental_sample_data("600519")
    assert direct == inferred
    assert direct["fundamental_source"] == "内置示例数据"
    assert get_fundamental_sample_data("not-a-code") is None


def test_clean_metric_value_handles_invalid_missing_and_infinite_values():
    assert clean_metric_value("12.5") == 12.5
    assert clean_metric_value(0) == 0
    assert math.isnan(clean_metric_value("bad"))
    assert math.isnan(clean_metric_value(None))
    assert math.isnan(clean_metric_value(float("inf")))
    assert math.isnan(clean_metric_value(float("-inf")))


def test_fundamental_helpers_keep_legacy_call_path_available():
    assert legacy_app.clean_metric_value("10") == clean_metric_value("10")
    assert legacy_app.build_fundamental_record((), "来源") == build_fundamental_record((), "来源")
    assert legacy_app.get_fundamental_sample_data("300750") == get_fundamental_sample_data("300750")
