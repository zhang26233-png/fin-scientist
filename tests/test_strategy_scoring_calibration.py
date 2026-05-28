import copy

import pandas as pd

from strategy.scoring import calculate_strategy_scores


FORBIDDEN_CALIBRATION_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def make_sample_frame(row):
    return pd.DataFrame([row])


def high_quality_trend_row():
    return {
        "股票代码": "HQ001",
        "股票名称": "高质量趋势样本",
        "最新价格": 120.0,
        "近 20 日涨跌幅": "12.00%",
        "成交量": 1800000,
        "成交额": 216000000,
        "年化波动率": "28.00%",
        "成交量放大倍数": 1.4,
        "有效交易日数量": 90,
    }


def low_liquidity_row():
    return {
        "股票代码": "LQ001",
        "股票名称": "低流动性样本",
        "最新价格": 18.0,
        "近 20 日涨跌幅": "4.00%",
        "成交量": 20000,
        "成交额": 360000,
        "年化波动率": "45.00%",
        "成交量放大倍数": 0.6,
        "有效交易日数量": 80,
    }


def overheated_risk_row():
    return {
        "股票代码": "HR001",
        "股票名称": "高风险过热样本",
        "最新价格": 80.0,
        "近 20 日涨跌幅": "48.00%",
        "成交量": 2200000,
        "成交额": 176000000,
        "年化波动率": "95.00%",
        "成交量放大倍数": 2.1,
        "有效交易日数量": 90,
    }


def missing_data_row():
    return {
        "股票代码": "MD001",
        "股票名称": "数据缺失样本",
    }


def neutral_row():
    return {
        "股票代码": "NT001",
        "股票名称": "普通中性样本",
        "最新价格": 50.0,
        "近 20 日涨跌幅": "1.50%",
        "成交量": 500000,
        "成交额": 25000000,
        "年化波动率": "42.00%",
        "成交量放大倍数": 1.0,
        "有效交易日数量": 80,
    }


def score_for(row):
    result = calculate_strategy_scores(make_sample_frame(row))
    assert result["status"] == "ok"
    return result["scores"][0]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_CALIBRATION_WORDS:
        assert word not in text


def test_strategy_score_calibration_direction_across_samples():
    high_quality = score_for(high_quality_trend_row())
    low_liquidity = score_for(low_liquidity_row())
    overheated = score_for(overheated_risk_row())
    missing_data = score_for(missing_data_row())
    neutral = score_for(neutral_row())

    assert high_quality["strategy_score"] > missing_data["strategy_score"]
    assert high_quality["strategy_score"] > low_liquidity["strategy_score"]
    assert high_quality["strategy_score"] >= neutral["strategy_score"]
    assert overheated["risk_penalty"] > high_quality["risk_penalty"]
    assert low_liquidity["liquidity_score"] < high_quality["liquidity_score"]
    assert missing_data["data_quality_penalty"] > high_quality["data_quality_penalty"]
    assert 20 <= neutral["strategy_score"] <= 80
    assert_no_forbidden_words(
        {
            "high_quality": high_quality,
            "low_liquidity": low_liquidity,
            "overheated": overheated,
            "missing_data": missing_data,
            "neutral": neutral,
        }
    )


def test_strategy_score_calibration_does_not_modify_samples():
    frame = pd.DataFrame(
        [
            high_quality_trend_row(),
            low_liquidity_row(),
            overheated_risk_row(),
            missing_data_row(),
            neutral_row(),
        ]
    )
    before = copy.deepcopy(frame)

    calculate_strategy_scores(frame)

    pd.testing.assert_frame_equal(frame, before)
