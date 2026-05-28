import copy

import pandas as pd

from strategy.service import build_strategy_service_output


FORBIDDEN_SERVICE_WORDS = [
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
    for word in FORBIDDEN_SERVICE_WORDS:
        assert word not in text


def test_strategy_service_import_and_empty_dataframe_safe_return():
    result = build_strategy_service_output(pd.DataFrame())

    assert result["status"] == "empty"
    assert result["preset_name"] == "研究优先级策略"
    assert result["diagnostics"] == []
    assert result["report"]["summary_text"]
    assert result["metadata"]["input_rows"] == 0
    assert result["warnings"]
    assert_no_forbidden_words(result)


def test_strategy_service_handles_missing_fields_safely():
    frame = pd.DataFrame([{"股票代码": "AAPL"}])

    result = build_strategy_service_output(frame)

    assert result["status"] == "warning"
    assert len(result["diagnostics"]) == 1
    assert result["diagnostics"][0]["identity"]["symbol"] == "AAPL"
    assert result["warnings"]
    assert_no_forbidden_words(result)


def test_strategy_service_generates_stable_output_for_screening_frame():
    result = build_strategy_service_output(make_screening_frame())

    assert set(result) == {"status", "preset_name", "diagnostics", "report", "metadata", "warnings"}
    assert result["status"] in {"ok", "warning"}
    assert result["preset_name"] == "研究优先级策略"
    assert len(result["diagnostics"]) == 1
    assert result["report"]["preset_name"] == "研究优先级策略"
    assert result["metadata"]["diagnostic_count"] == 1
    assert result["metadata"]["read_only"] is True
    assert result["metadata"]["ui_connected"] is False
    assert result["metadata"]["ranking_changed"] is False
    assert result["metadata"]["scoring_changed"] is False
    assert_no_forbidden_words(result)


def test_strategy_service_does_not_modify_source_dataframe():
    frame = make_screening_frame()
    before = copy.deepcopy(frame)

    build_strategy_service_output(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_strategy_service_handles_non_dataframe_input():
    result = build_strategy_service_output(None)

    assert result["status"] == "empty"
    assert result["metadata"]["input_type"] == "NoneType"
    assert result["warnings"]
    assert_no_forbidden_words(result)
