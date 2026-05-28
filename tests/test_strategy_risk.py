from strategy.risk import (
    build_risk_labels,
    detect_consecutive_rise_risk,
    detect_high_volatility_risk,
    detect_liquidity_risk,
    detect_missing_data_risk,
    detect_turnover_overheat_risk,
    detect_volume_downside_risk,
    risk_tags_to_text,
)


FORBIDDEN_RISK_WORDS = ["\u4e70\u5165", "\u5356\u51fa", "\u6ee1\u4ed3", "\u68ad\u54c8"]


def make_metrics():
    return {
        "年化波动率": 0.95,
        "近 20 日涨跌幅": 0.45,
        "成交量放大倍数": 0.6,
        "有效交易日数量": 40,
        "成交量数据缺失": False,
        "基本面字段缺失较多": True,
    }


def assert_no_operation_words(text):
    for word in FORBIDDEN_RISK_WORDS:
        assert word not in text


def test_strategy_risk_handles_empty_and_missing_inputs():
    risks = build_risk_labels(None)
    text = risk_tags_to_text(risks)

    assert risks
    assert_no_operation_words(text)


def test_strategy_risk_returns_labels_without_operation_words():
    metrics = make_metrics()
    risks = build_risk_labels(metrics)
    tags = {item["tag"] for item in risks}
    text = risk_tags_to_text(risks)

    assert "高波动风险" in tags
    assert "短期涨幅风险" in tags
    assert "样本不足风险" in tags
    assert "基本面缺失风险" in tags
    assert "流动性风险" in tags
    assert_no_operation_words(text)


def test_strategy_risk_individual_detectors_are_stable():
    metrics = make_metrics()

    assert detect_high_volatility_risk(metrics)
    assert detect_consecutive_rise_risk(metrics)
    assert detect_missing_data_risk(metrics)
    assert detect_liquidity_risk(metrics)
    assert risk_tags_to_text("bad input") == ""


def test_strategy_risk_detects_volume_downside_turnover_and_low_liquidity_codes():
    metrics = {
        "近 5 日涨跌幅": -0.08,
        "成交量放大倍数": 1.8,
        "换手率": 0.20,
        "成交额": 2_000_000,
        "成交量": 50_000,
        "有效交易日数量": 90,
        "基本面字段缺失较多": False,
    }

    risks = build_risk_labels(metrics)
    codes = {item.get("code") for item in risks}

    assert detect_volume_downside_risk(metrics)
    assert detect_turnover_overheat_risk(metrics)
    assert "volume_downside_risk" in codes
    assert "overheated_turnover" in codes
    assert "low_liquidity" in codes
    assert_no_operation_words(risk_tags_to_text(risks))


def test_strategy_risk_handles_inf_nan_and_amplitude_safely():
    metrics = {
        "年化波动率": float("inf"),
        "振幅": 0.16,
        "成交量放大倍数": float("nan"),
        "有效交易日数量": 90,
        "基本面字段缺失较多": False,
    }

    risks = build_risk_labels(metrics)
    codes = {item.get("code") for item in risks}

    assert "high_volatility" in codes
    assert_no_operation_words(risk_tags_to_text(risks))
