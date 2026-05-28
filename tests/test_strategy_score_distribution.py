import pandas as pd

from strategy.scoring import calculate_strategy_scores


FORBIDDEN_DISTRIBUTION_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def make_distribution_frame():
    return pd.DataFrame(
        [
            {
                "股票代码": "A001",
                "最新价格": 120.0,
                "近 20 日涨跌幅": "12.00%",
                "成交量": 1800000,
                "成交额": 216000000,
                "年化波动率": "28.00%",
                "成交量放大倍数": 1.4,
                "有效交易日数量": 90,
            },
            {
                "股票代码": "A002",
                "最新价格": 18.0,
                "近 20 日涨跌幅": "4.00%",
                "成交量": 20000,
                "成交额": 360000,
                "年化波动率": "45.00%",
                "成交量放大倍数": 0.6,
                "有效交易日数量": 80,
            },
            {
                "股票代码": "A003",
                "最新价格": 80.0,
                "近 20 日涨跌幅": "48.00%",
                "成交量": 2200000,
                "成交额": 176000000,
                "年化波动率": "95.00%",
                "成交量放大倍数": 2.1,
                "有效交易日数量": 90,
            },
            {"股票代码": "A004"},
            {
                "股票代码": "A005",
                "最新价格": 50.0,
                "近 20 日涨跌幅": "1.50%",
                "成交量": 500000,
                "成交额": 25000000,
                "年化波动率": "42.00%",
                "成交量放大倍数": 1.0,
                "有效交易日数量": 80,
            },
        ]
    )


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_DISTRIBUTION_WORDS:
        assert word not in text


def test_strategy_score_distribution_stays_in_expected_range():
    result = calculate_strategy_scores(make_distribution_frame())
    scores = result["scores"]
    values = [row["strategy_score"] for row in scores]

    assert result["status"] == "ok"
    assert len(values) == 5
    assert all(0 <= value <= 100 for value in values)
    assert max(values) > min(values)
    assert len(set(values)) >= 3
    assert_no_forbidden_words(result)


def test_strategy_score_distribution_keeps_row_order_without_sorting():
    frame = make_distribution_frame()
    result = calculate_strategy_scores(frame)
    symbols = [row["identity"].get("symbol") for row in result["scores"]]

    assert symbols == frame["股票代码"].tolist()
    assert result["metadata"]["ranking_changed"] is False
    assert result["metadata"]["scoring_changed"] is False
