import copy

import pandas as pd

from strategy.adapter import build_strategy_diagnostics, infer_field_mapping


FORBIDDEN_OPERATION_WORDS = ["\u4e70\u5165", "\u5356\u51fa", "\u6ee1\u4ed3", "\u68ad\u54c8"]


def make_screening_frame():
    return pd.DataFrame(
        [
            {
                "股票代码": "300750.SZ",
                "股票名称": "宁德时代",
                "最新价格": 210.5,
                "近 20 日涨跌幅": "12.50%",
                "近 60 日涨跌幅": "25.00%",
                "成交量": 1200000,
                "成交额": 252600000,
                "换手率": "1.20%",
                "行业": "电力设备",
                "板块": "动力电池",
                "研究优先级评分": 65,
                "年化波动率": "35.00%",
                "最大回撤": "-18.00%",
                "成交量放大倍数": 1.5,
                "有效交易日数量": 80,
                "数据质量": "数据较完整",
            }
        ]
    )


def stringify_result(result):
    return str(result)


def assert_no_operation_words(result):
    text = stringify_result(result)
    for word in FORBIDDEN_OPERATION_WORDS:
        assert word not in text


def test_strategy_adapter_import_and_empty_dataframe_safe_return():
    result = build_strategy_diagnostics(pd.DataFrame())

    assert result["diagnostics"] == []
    assert result["preset_name"] == "研究优先级策略"
    assert result["diagnostics_summary"]
    assert result["risk_tags"]
    assert_no_operation_words(result)


def test_strategy_adapter_handles_missing_fields_safely():
    frame = pd.DataFrame([{"股票代码": "AAPL"}])

    result = build_strategy_diagnostics(frame)
    item = result["diagnostics"][0]

    assert item["identity"]["symbol"] == "AAPL"
    assert item["factor_scores"]["trend"]["score"] == "无法计算"
    assert item["filter_flags"]["passed"] is False
    assert item["risk_tags"]
    assert_no_operation_words(result)


def test_strategy_adapter_generates_stable_diagnostics_for_screening_frame():
    frame = make_screening_frame()

    result = build_strategy_diagnostics(frame)
    item = result["diagnostics"][0]

    assert result["preset_name"] == "研究优先级策略"
    assert result["field_mapping"]["close"] == "最新价格"
    assert item["identity"]["symbol"] == "300750.SZ"
    assert item["factor_scores"]["trend"]["factor"] == "trend"
    assert item["factor_scores"]["momentum"]["factor"] == "momentum"
    assert item["filter_flags"]["checks"]
    assert isinstance(item["risk_tags"], list)
    assert item["risk_notes"]
    assert item["diagnostics_summary"]
    assert_no_operation_words(result)


def test_strategy_adapter_does_not_modify_source_dataframe():
    frame = make_screening_frame()
    before = copy.deepcopy(frame)

    build_strategy_diagnostics(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_strategy_adapter_infers_alias_fields():
    frame = pd.DataFrame(
        [
            {
                "symbol": "MSFT",
                "price": 420.0,
                "change_pct": 0.02,
                "volume": 1000,
                "amount": 420000,
                "turnover": 0.01,
                "sector": "Software",
            }
        ]
    )

    mapping = infer_field_mapping(frame)
    result = build_strategy_diagnostics(frame, preset_key="stable_observation")

    assert mapping["close"] == "price"
    assert mapping["change_pct"] == "change_pct"
    assert mapping["sector"] == "sector"
    assert result["preset_name"] == "稳健观察策略"
