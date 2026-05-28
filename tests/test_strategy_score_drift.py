import copy
from pathlib import Path

import pandas as pd

from strategy.comparison import compare_strategy_scores, summarize_score_alignment
from strategy.scoring import calculate_strategy_scores


FORBIDDEN_DRIFT_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def make_scoring_drift_frame():
    return pd.DataFrame(
        [
            {
                "股票代码": "HQ001",
                "股票名称": "高质量趋势样本",
                "最新价格": 120.0,
                "近 20 日涨跌幅": "12.00%",
                "成交量": 1800000,
                "成交额": 216000000,
                "年化波动率": "28.00%",
                "成交量放大倍数": 1.4,
                "有效交易日数量": 90,
            },
            {
                "股票代码": "LQ001",
                "股票名称": "低流动性样本",
                "最新价格": 18.0,
                "近 20 日涨跌幅": "4.00%",
                "成交量": 20000,
                "成交额": 360000,
                "年化波动率": "45.00%",
                "成交量放大倍数": 0.6,
                "有效交易日数量": 80,
            },
            {
                "股票代码": "HR001",
                "股票名称": "高风险过热样本",
                "最新价格": 80.0,
                "近 20 日涨跌幅": "48.00%",
                "成交量": 2200000,
                "成交额": 176000000,
                "年化波动率": "95.00%",
                "成交量放大倍数": 2.1,
                "有效交易日数量": 90,
            },
            {"股票代码": "MD001", "股票名称": "数据缺失样本"},
            {
                "股票代码": "NT001",
                "股票名称": "普通中性样本",
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


def make_comparison_drift_frame():
    return pd.DataFrame(
        [
            {"股票代码": "HQ001", "研究优先级评分": 75, "strategy_score": 72},
            {"股票代码": "LQ001", "研究优先级评分": 30, "strategy_score": 25},
            {"股票代码": "HR001", "研究优先级评分": 70, "strategy_score": 35},
            {"股票代码": "MD001", "研究优先级评分": None, "strategy_score": None},
            {"股票代码": "NT001", "研究优先级评分": 50, "strategy_score": 48},
            {"股票代码": "SHRL", "研究优先级评分": 32, "strategy_score": 70},
            {"股票代码": "RHSL", "研究优先级评分": 78, "strategy_score": 30},
        ]
    )


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_DRIFT_WORDS:
        assert word not in text


def test_strategy_score_fixed_samples_do_not_drift_outside_ranges():
    result = calculate_strategy_scores(make_scoring_drift_frame())
    by_symbol = {row["identity"]["symbol"]: row for row in result["scores"]}

    assert result["status"] == "ok"
    assert len(by_symbol) == 5
    assert 45 <= by_symbol["HQ001"]["strategy_score"] <= 60
    assert 25 <= by_symbol["LQ001"]["strategy_score"] <= 45
    assert 0 <= by_symbol["HR001"]["strategy_score"] <= 20
    assert by_symbol["MD001"]["strategy_score"] == 0
    assert 35 <= by_symbol["NT001"]["strategy_score"] <= 60
    assert by_symbol["LQ001"]["liquidity_score"] < by_symbol["HQ001"]["liquidity_score"]
    assert by_symbol["HR001"]["risk_penalty"] > by_symbol["HQ001"]["risk_penalty"]
    assert by_symbol["MD001"]["data_quality_penalty"] > by_symbol["HQ001"]["data_quality_penalty"]
    assert_no_forbidden_words(result)


def test_strategy_comparison_drift_labels_and_summary_stay_stable():
    comparison = compare_strategy_scores(make_comparison_drift_frame())
    labels = [item["alignment_label"] for item in comparison["comparisons"]]
    summary = summarize_score_alignment(comparison)

    assert labels == [
        "high_consensus",
        "low_consensus",
        "research_high_strategy_low",
        "insufficient_data",
        "mixed_observation",
        "strategy_high_research_low",
        "research_high_strategy_low",
    ]
    assert summary["total_count"] == 7
    assert summary["valid_count"] == 6
    assert summary["alignment_counts"] == {
        "high_consensus": 1,
        "low_consensus": 1,
        "research_high_strategy_low": 2,
        "insufficient_data": 1,
        "mixed_observation": 1,
        "strategy_high_research_low": 1,
    }
    assert summary["missing_original_score_count"] == 1
    assert summary["missing_strategy_score_count"] == 1
    assert 54 <= summary["average_original_score"] <= 56
    assert 46 <= summary["average_strategy_score"] <= 48
    assert -10 <= summary["average_score_gap"] <= -7
    assert_no_forbidden_words({"comparison": comparison, "summary": summary})


def test_strategy_drift_checks_do_not_modify_source_dataframe():
    scoring_frame = make_scoring_drift_frame()
    comparison_frame = make_comparison_drift_frame()
    scoring_before = copy.deepcopy(scoring_frame)
    comparison_before = copy.deepcopy(comparison_frame)

    calculate_strategy_scores(scoring_frame)
    summarize_score_alignment(comparison_frame)

    pd.testing.assert_frame_equal(scoring_frame, scoring_before)
    pd.testing.assert_frame_equal(comparison_frame, comparison_before)


def test_strategy_drift_modules_are_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.scoring" not in legacy_text
    assert "strategy.comparison" not in legacy_text
    assert "calculate_strategy_scores" not in legacy_text
    assert "summarize_score_alignment" not in legacy_text
    assert "strategy.scoring" not in screening_text
    assert "strategy.comparison" not in screening_text
    assert "calculate_strategy_scores" not in screening_text
    assert "summarize_score_alignment" not in screening_text
