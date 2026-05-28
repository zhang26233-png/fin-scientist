import copy

import pandas as pd

from strategy.adapter import build_strategy_diagnostics
from strategy.report import build_strategy_report


FORBIDDEN_REPORT_WORDS = [
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
                "近 60 日涨跌幅": "25.00%",
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


def assert_no_forbidden_words(report):
    text = str(report)
    for word in FORBIDDEN_REPORT_WORDS:
        assert word not in text


def test_strategy_report_import_and_empty_diagnostics_safe_return():
    report = build_strategy_report({"preset_name": "研究优先级策略", "diagnostics": []})

    assert report["preset_name"] == "研究优先级策略"
    assert report["summary_text"]
    assert report["factor_summary"]
    assert report["filter_summary"]
    assert report["risk_summary"]
    assert report["data_quality_summary"]
    assert report["notes"]
    assert_no_forbidden_words(report)


def test_strategy_report_handles_missing_fields_safely():
    report = build_strategy_report({"diagnostics": [{"identity": {"symbol": "AAPL"}}]})

    assert report["summary_text"]
    assert "暂无可汇总" in report["factor_summary"]
    assert_no_forbidden_words(report)


def test_strategy_report_generates_stable_summary_from_adapter_output():
    diagnostics = build_strategy_diagnostics(make_screening_frame())
    report = build_strategy_report(diagnostics)

    assert report["preset_name"] == "研究优先级策略"
    assert "因子" in report["factor_summary"]
    assert "过滤检查" in report["filter_summary"]
    assert "风险标签" in report["risk_summary"]
    assert "数据质量提示" in report["data_quality_summary"]
    assert "研究优先级" in report["summary_text"]
    assert_no_forbidden_words(report)


def test_strategy_report_does_not_modify_adapter_output():
    diagnostics = build_strategy_diagnostics(make_screening_frame())
    before = copy.deepcopy(diagnostics)

    build_strategy_report(diagnostics)

    assert diagnostics == before


def test_strategy_report_handles_non_dict_input():
    report = build_strategy_report(None)

    assert report["preset_name"] == ""
    assert report["summary_text"]
    assert_no_forbidden_words(report)
