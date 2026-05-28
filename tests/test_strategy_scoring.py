import copy
from pathlib import Path

import pandas as pd

from strategy.adapter import build_strategy_diagnostics
from strategy.scoring import calculate_strategy_scores


FORBIDDEN_STRATEGY_SCORING_WORDS = [
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


def assert_score_range(score_row):
    assert 0 <= score_row["trend_score"] <= 100
    assert 0 <= score_row["momentum_score"] <= 100
    assert 0 <= score_row["volume_price_score"] <= 100
    assert 0 <= score_row["liquidity_score"] <= 100
    assert 0 <= score_row["strategy_score"] <= 100


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_STRATEGY_SCORING_WORDS:
        assert word not in text


def test_strategy_scoring_empty_dataframe_safe_return():
    result = calculate_strategy_scores(pd.DataFrame())

    assert result["status"] == "empty"
    assert result["scores"] == []
    assert result["metadata"]["read_only"] is True
    assert_no_forbidden_words(result)


def test_strategy_scoring_missing_fields_safe_return():
    frame = pd.DataFrame([{"股票代码": "AAPL"}])

    result = calculate_strategy_scores(frame)
    score_row = result["scores"][0]

    assert result["status"] == "ok"
    assert score_row["strategy_score"] == 0
    assert score_row["data_quality_penalty"] > 0
    assert_score_range(score_row)
    assert_no_forbidden_words(result)


def test_strategy_scoring_typical_frame_stable_score():
    result = calculate_strategy_scores(make_screening_frame())
    score_row = result["scores"][0]

    assert result["status"] == "ok"
    assert score_row["identity"]["symbol"] == "300750.SZ"
    assert score_row["trend_score"] == 100
    assert score_row["momentum_score"] in {50, 65, 70, 80}
    assert score_row["strategy_score"] > 0
    assert_score_range(score_row)
    assert_no_forbidden_words(result)


def test_strategy_scoring_distinguishes_moderate_momentum_from_overheated_risk():
    moderate = pd.DataFrame(
        [
            {
                "股票代码": "MOD1",
                "最新价格": 100,
                "近 20 日涨跌幅": "12.00%",
                "return_10d": 0.08,
                "return_5d": 0.03,
                "成交量": 1000000,
                "成交额": 100000000,
                "年化波动率": "30.00%",
                "成交量放大倍数": 1.2,
                "有效交易日数量": 90,
            }
        ]
    )
    overheated = pd.DataFrame(
        [
            {
                "股票代码": "HOT1",
                "最新价格": 100,
                "近 20 日涨跌幅": "48.00%",
                "return_10d": 0.30,
                "return_5d": 0.18,
                "成交量": 1000000,
                "成交额": 100000000,
                "年化波动率": "95.00%",
                "成交量放大倍数": 2.0,
                "有效交易日数量": 90,
            }
        ]
    )

    moderate_score = calculate_strategy_scores(moderate)["scores"][0]
    overheated_score = calculate_strategy_scores(overheated)["scores"][0]

    assert moderate_score["momentum_score"] > overheated_score["momentum_score"]
    assert overheated_score["risk_penalty"] > moderate_score["risk_penalty"]
    assert moderate_score["strategy_score"] > overheated_score["strategy_score"]


def test_strategy_scoring_lowers_momentum_for_recent_weakness():
    weak = pd.DataFrame(
        [
            {
                "股票代码": "WEAK1",
                "最新价格": 100,
                "近 20 日涨跌幅": "-8.00%",
                "return_10d": -0.04,
                "return_5d": -0.06,
                "成交量": 1000000,
                "成交额": 100000000,
                "年化波动率": "35.00%",
                "成交量放大倍数": 0.9,
                "有效交易日数量": 90,
            }
        ]
    )

    score_row = calculate_strategy_scores(weak)["scores"][0]

    assert score_row["momentum_score"] <= 25
    assert 0 <= score_row["strategy_score"] <= 100


def test_strategy_scoring_accepts_diagnostics_and_penalizes_high_risk():
    diagnostics = build_strategy_diagnostics(make_screening_frame())
    item = diagnostics["diagnostics"][0]
    item["risk_tags"].append({"tag": "高波动风险", "message": "测试风险提示。"})
    item["risk_tags"].append({"tag": "短期涨幅风险", "message": "测试风险提示。"})

    result = calculate_strategy_scores(diagnostics)
    score_row = result["scores"][0]

    assert score_row["risk_penalty"] >= 25
    assert_score_range(score_row)
    assert_no_forbidden_words(result)


def test_strategy_scoring_penalizes_data_quality_issues():
    diagnostics = build_strategy_diagnostics(pd.DataFrame([{"股票代码": "AAPL"}]))

    result = calculate_strategy_scores(diagnostics)
    score_row = result["scores"][0]

    assert score_row["data_quality_penalty"] > 0
    assert score_row["strategy_score"] == 0
    assert_no_forbidden_words(result)


def test_strategy_scoring_does_not_modify_source_dataframe():
    frame = make_screening_frame()
    before = copy.deepcopy(frame)

    calculate_strategy_scores(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_strategy_scoring_is_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.scoring" not in legacy_text
    assert "calculate_strategy_scores" not in legacy_text
    assert "strategy.scoring" not in screening_text
    assert "calculate_strategy_scores" not in screening_text
