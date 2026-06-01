import copy
import math

from strategy.fundamental import (
    FUNDAMENTAL_PROFILE_FIELDS,
    build_fundamental_data_quality,
    build_fundamental_profile,
    detect_fundamental_fields,
    normalize_fundamental_value,
)


FORBIDDEN_FUNDAMENTAL_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_FUNDAMENTAL_WORDS:
        assert word not in text


def full_english_row():
    return {
        "revenue": "1.2亿",
        "net_profit": "3,500万",
        "gross_margin": "35%",
        "roe": 0.18,
        "pe": "18.5",
        "pb": "2.1",
        "ps": "4.2",
        "debt_ratio": "45%",
        "operating_cashflow": "2,000万",
        "revenue_growth": "12%",
        "profit_growth": "8%",
        "market_cap": "360亿",
        "industry": "制造业",
    }


def test_strategy_fundamental_import_and_empty_input_safe_return():
    profile = build_fundamental_profile(None)

    assert set(FUNDAMENTAL_PROFILE_FIELDS).issubset(profile)
    assert profile["fundamental_available"] is False
    assert profile["fundamental_data_quality_label"] == "no_fundamental_data"
    assert profile["fundamental_fields_detected"] == []
    assert_no_forbidden_words(profile)


def test_strategy_fundamental_missing_fields_safe_return():
    profile = build_fundamental_profile({"symbol": "MISS1"})

    assert profile["fundamental_available"] is False
    assert profile["fundamental_data_quality_label"] == "no_fundamental_data"
    assert "revenue" in profile["missing_fundamental_fields"]
    assert_no_forbidden_words(profile)


def test_normalize_fundamental_value_handles_percent_units_and_invalid_values():
    assert normalize_fundamental_value("12.5%") == 0.125
    assert normalize_fundamental_value("1,234.5") == 1234.5
    assert normalize_fundamental_value("3万") == 30_000
    assert normalize_fundamental_value("2.5亿") == 250_000_000
    assert normalize_fundamental_value("") is None
    assert normalize_fundamental_value(None) is None
    assert normalize_fundamental_value(float("nan")) is None
    assert normalize_fundamental_value(float("inf")) is None
    assert normalize_fundamental_value("--") is None


def test_detect_fundamental_fields_accepts_english_aliases():
    detected = detect_fundamental_fields(full_english_row())

    assert detected["revenue"] == 120_000_000
    assert detected["net_profit"] == 35_000_000
    assert detected["gross_margin"] == 0.35
    assert detected["industry"] == "制造业"


def test_detect_fundamental_fields_accepts_chinese_aliases():
    row = {
        "营业收入": "5亿",
        "净利润": "8,000万",
        "毛利率": "42%",
        "净资产收益率": "16%",
        "市盈率": 20,
        "市净率": 2.5,
        "市销率": 4,
        "资产负债率": "38%",
        "经营现金流": "1.1亿",
        "营收增长率": "15%",
        "净利润增长率": "9%",
        "总市值": "420亿",
        "行业": "医药",
    }

    detected = detect_fundamental_fields(row)

    assert detected["revenue"] == 500_000_000
    assert detected["roe"] == 0.16
    assert detected["market_cap"] == 42_000_000_000
    assert detected["industry"] == "医药"


def test_fundamental_quality_labels_for_full_partial_and_none():
    full = build_fundamental_data_quality(full_english_row())
    partial = build_fundamental_data_quality({"revenue": 100, "net_profit": 10, "pe": 18, "industry": "消费"})
    sparse = build_fundamental_data_quality({"revenue": 100})
    none = build_fundamental_data_quality({"symbol": "NONE1"})

    assert full["fundamental_data_quality_label"] == "sufficient_fundamental_data"
    assert partial["fundamental_data_quality_label"] == "partial_fundamental_data"
    assert sparse["fundamental_data_quality_label"] == "insufficient_fundamental_data"
    assert none["fundamental_data_quality_label"] == "no_fundamental_data"


def test_build_fundamental_profile_contains_all_fields_and_does_not_modify_source():
    source = full_english_row()
    before = copy.deepcopy(source)

    profile = build_fundamental_profile(source)

    assert set(FUNDAMENTAL_PROFILE_FIELDS).issubset(profile)
    assert profile["fundamental_available"] is True
    assert profile["fundamental_data_quality_label"] == "sufficient_fundamental_data"
    assert "基本面字段较完整" in profile["fundamental_summary_base"]
    assert source == before
    assert_no_forbidden_words(profile)
