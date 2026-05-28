import copy

import pandas as pd

from strategy.service import build_strategy_service_output
from strategy.view_model import build_strategy_view_model


FORBIDDEN_VIEW_MODEL_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def make_screening_frame():
    return pd.DataFrame(
        [
            {
                "股票代码": "300750.SZ",
                "股票名称": "宁德时代",
                "最新价格": 210.5,
                "近 20 日涨跌幅": "12.50%",
                "成交量": 1200000,
                "成交额": 252600000,
                "行业": "电力设备",
                "板块": "动力电池",
                "研究优先级评分": 65,
                "年化波动率": "35.00%",
                "成交量放大倍数": 1.5,
                "有效交易日数量": 80,
            }
        ]
    )


def assert_no_forbidden_words(result):
    text = str(result)
    for word in FORBIDDEN_VIEW_MODEL_WORDS:
        assert word not in text


def test_strategy_view_model_import_and_empty_service_output_safe_return():
    view_model = build_strategy_view_model({})

    assert set(view_model) == {"cards", "badges", "sections", "table_rows", "empty_state", "metadata"}
    assert view_model["empty_state"]["is_empty"] is True
    assert view_model["metadata"]["read_only"] is True
    assert view_model["metadata"]["ui_connected"] is False
    assert view_model["metadata"]["ranking_changed"] is False
    assert view_model["metadata"]["scoring_changed"] is False
    assert_no_forbidden_words(view_model)


def test_strategy_view_model_handles_missing_fields_safely():
    service_output = {"status": "warning", "diagnostics": [{"identity": {"symbol": "AAPL"}}], "metadata": {}}

    view_model = build_strategy_view_model(service_output)

    assert view_model["empty_state"]["is_empty"] is False
    assert len(view_model["table_rows"]) == 1
    assert view_model["table_rows"][0]["symbol"] == "AAPL"
    assert view_model["table_rows"][0]["factor_brief"] == "暂无因子结果"
    assert_no_forbidden_words(view_model)


def test_strategy_view_model_generates_stable_output_from_service():
    service_output = build_strategy_service_output(make_screening_frame())

    view_model = build_strategy_view_model(service_output)

    assert len(view_model["cards"]) == 4
    assert view_model["badges"]
    assert len(view_model["sections"]) == 6
    assert len(view_model["table_rows"]) == 1
    assert view_model["table_rows"][0]["symbol"] == "300750.SZ"
    assert view_model["empty_state"]["is_empty"] is False
    assert view_model["metadata"]["view_model_only"] is True
    assert view_model["metadata"]["ui_connected"] is False
    assert_no_forbidden_words(view_model)


def test_strategy_view_model_does_not_modify_service_output():
    service_output = build_strategy_service_output(make_screening_frame())
    before = copy.deepcopy(service_output)

    build_strategy_view_model(service_output)

    assert service_output == before


def test_strategy_view_model_handles_non_dict_input():
    view_model = build_strategy_view_model(None)

    assert view_model["empty_state"]["is_empty"] is True
    assert view_model["table_rows"] == []
    assert_no_forbidden_words(view_model)
