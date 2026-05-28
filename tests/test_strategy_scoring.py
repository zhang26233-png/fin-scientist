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


def test_strategy_scoring_liquidity_uses_amount_volume_and_turnover():
    active = pd.DataFrame(
        [
            {
                "symbol": "ACTIVE1",
                "Close": 100,
                "return_20d": 0.10,
                "return_10d": 0.05,
                "return_5d": 0.02,
                "volume": 1_500_000,
                "amount": 150_000_000,
                "turnover": 0.04,
                "volatility": 0.30,
                "volume_ratio": 1.2,
                "valid_trading_days": 90,
            }
        ]
    )
    low = active.copy(deep=True)
    low["symbol"] = "LOW1"
    low["amount"] = 2_000_000
    low["volume"] = 50_000
    low["turnover"] = 0.001

    active_score = calculate_strategy_scores(active)["scores"][0]
    low_score = calculate_strategy_scores(low)["scores"][0]

    assert active_score["liquidity_score"] > low_score["liquidity_score"]
    assert low_score["liquidity_score"] <= 25
    assert_score_range(active_score)
    assert_score_range(low_score)


def test_strategy_scoring_volume_price_confirms_or_weakens_trend():
    confirmed = pd.DataFrame(
        [
            {
                "symbol": "CONF1",
                "Close": 100,
                "return_20d": 0.12,
                "return_10d": 0.06,
                "return_5d": 0.03,
                "volume": 1_500_000,
                "amount": 150_000_000,
                "turnover": 0.04,
                "volatility": 0.30,
                "volume_ratio": 1.5,
                "valid_trading_days": 90,
            }
        ]
    )
    weak = confirmed.copy(deep=True)
    weak["symbol"] = "WEAKVOL1"
    weak["volume_ratio"] = 0.55

    confirmed_score = calculate_strategy_scores(confirmed)["scores"][0]
    weak_score = calculate_strategy_scores(weak)["scores"][0]

    assert confirmed_score["volume_price_score"] > weak_score["volume_price_score"]
    assert confirmed_score["strategy_score"] >= weak_score["strategy_score"]


def test_strategy_scoring_penalizes_volume_downside_and_overheated_turnover():
    base = pd.DataFrame(
        [
            {
                "symbol": "BASE1",
                "Close": 100,
                "return_20d": 0.02,
                "return_10d": 0.01,
                "return_5d": 0.0,
                "volume": 1_000_000,
                "amount": 100_000_000,
                "turnover": 0.04,
                "volatility": 0.35,
                "volume_ratio": 1.0,
                "valid_trading_days": 90,
            }
        ]
    )
    downside = base.copy(deep=True)
    downside["symbol"] = "DOWNVOL1"
    downside["return_20d"] = -0.08
    downside["volume_ratio"] = 1.8
    overheated = base.copy(deep=True)
    overheated["symbol"] = "TURNHOT1"
    overheated["turnover"] = 0.20

    base_score = calculate_strategy_scores(base)["scores"][0]
    downside_score = calculate_strategy_scores(downside)["scores"][0]
    overheated_score = calculate_strategy_scores(overheated)["scores"][0]

    assert downside_score["risk_penalty"] > base_score["risk_penalty"]
    assert overheated_score["risk_penalty"] > base_score["risk_penalty"]
    assert downside_score["volume_price_score"] < base_score["volume_price_score"]
    assert_score_range(downside_score)
    assert_score_range(overheated_score)


def test_strategy_scoring_accepts_turnover_rate_and_volume_ratio_aliases():
    frame = pd.DataFrame(
        [
            {
                "symbol": "ALIAS1",
                "Close": 100,
                "return_20d": 0.10,
                "return_10d": 0.04,
                "return_5d": 0.02,
                "volume": 1_200_000,
                "turnover_amount": 120_000_000,
                "turnover_rate": 0.04,
                "量比": 1.45,
                "volatility": 0.30,
                "valid_trading_days": 90,
            }
        ]
    )

    score_row = calculate_strategy_scores(frame)["scores"][0]

    assert score_row["volume_price_score"] >= 75
    assert score_row["liquidity_score"] > 40
    assert_score_range(score_row)


def test_strategy_scoring_handles_extreme_volume_liquidity_values_safely():
    frame = pd.DataFrame(
        [
            {
                "symbol": "EXTREME1",
                "Close": 100,
                "return_20d": 0.10,
                "volume": float("inf"),
                "amount": float("inf"),
                "turnover": float("inf"),
                "volume_ratio": float("inf"),
                "valid_trading_days": 90,
            }
        ]
    )

    score_row = calculate_strategy_scores(frame)["scores"][0]

    assert_score_range(score_row)


def test_strategy_scoring_penalizes_extreme_short_return_and_high_volatility():
    normal = pd.DataFrame(
        [
            {
                "symbol": "NORMALRISK",
                "Close": 100,
                "return_20d": 0.08,
                "return_10d": 0.04,
                "return_5d": 0.02,
                "amount": 120_000_000,
                "volume": 1_200_000,
                "turnover": 0.04,
                "volume_ratio": 1.1,
                "volatility": 0.30,
                "amplitude": 0.05,
                "valid_trading_days": 90,
            }
        ]
    )
    high_risk = normal.copy(deep=True)
    high_risk["symbol"] = "HIGHRISK"
    high_risk["return_5d"] = 0.18
    high_risk["pct_chg"] = 0.14
    high_risk["volatility"] = 0.95
    high_risk["amplitude"] = 0.16

    normal_score = calculate_strategy_scores(normal)["scores"][0]
    high_risk_score = calculate_strategy_scores(high_risk)["scores"][0]

    assert high_risk_score["risk_penalty"] > normal_score["risk_penalty"]
    assert "extreme_upside_return" in high_risk_score["risk_labels"]
    assert "high_volatility" in high_risk_score["risk_labels"]
    assert_score_range(high_risk_score)


def test_strategy_scoring_outputs_risk_and_data_quality_labels():
    frame = pd.DataFrame(
        [
            {
                "symbol": "QUALITYRISK",
                "Close": float("inf"),
                "return_5d": -0.08,
                "volume": 50_000,
                "amount": 2_000_000,
                "turnover": 0.001,
                "volume_ratio": 1.8,
                "volatility": 0.35,
                "valid_trading_days": 90,
            }
        ]
    )

    score_row = calculate_strategy_scores(frame)["scores"][0]

    assert score_row["data_quality_penalty"] > 0
    assert "invalid_numeric_fields" in score_row["data_quality_labels"]
    assert "missing_turnover_fields" not in score_row["data_quality_labels"]
    assert "volume_downside_risk" in score_row["risk_labels"]
    assert "low_liquidity" in score_row["risk_labels"]
    assert_score_range(score_row)
    assert_no_forbidden_words(score_row)


def test_strategy_scoring_missing_key_fields_raise_data_quality_labels():
    frame = pd.DataFrame([{"symbol": "MISSINGKEYS", "Close": 50}])

    score_row = calculate_strategy_scores(frame)["scores"][0]

    assert score_row["data_quality_penalty"] > 0
    assert "missing_volume_fields" in score_row["data_quality_labels"]
    assert "missing_turnover_fields" in score_row["data_quality_labels"]
    assert "insufficient_factor_data" in score_row["data_quality_labels"]
    assert_score_range(score_row)


def test_strategy_scoring_supports_multiple_presets_for_same_sample():
    frame = pd.DataFrame(
        [
            {
                "symbol": "PRESET1",
                "Close": 100,
                "return_20d": 0.16,
                "return_10d": 0.09,
                "return_5d": 0.04,
                "amount": 150_000_000,
                "volume": 1_500_000,
                "turnover": 0.04,
                "volume_ratio": 1.5,
                "volatility": 0.35,
                "valid_trading_days": 90,
            }
        ]
    )

    balanced = calculate_strategy_scores(frame, preset_name="balanced_research")["scores"][0]
    trend = calculate_strategy_scores(frame, preset_name="trend_momentum")["scores"][0]
    volume = calculate_strategy_scores(frame, preset_name="volume_breakout")["scores"][0]

    assert balanced["preset_name"] == "balanced_research"
    assert trend["preset_name"] == "trend_momentum"
    assert volume["preset_name"] == "volume_breakout"
    assert len({balanced["strategy_score"], trend["strategy_score"], volume["strategy_score"]}) >= 2
    assert "strategy_score_components" in trend
    assert_score_range(trend)


def test_trend_momentum_scores_trend_sample_above_low_risk_quality():
    frame = pd.DataFrame(
        [
            {
                "symbol": "TRENDMOM",
                "Close": 100,
                "return_20d": 0.18,
                "return_10d": 0.10,
                "return_5d": 0.04,
                "amount": 120_000_000,
                "volume": 1_200_000,
                "turnover": 0.04,
                "volume_ratio": 1.4,
                "volatility": 0.36,
                "valid_trading_days": 90,
            }
        ]
    )

    trend = calculate_strategy_scores(frame, preset_name="trend_momentum")["scores"][0]
    low_risk = calculate_strategy_scores(frame, preset_name="low_risk_quality")["scores"][0]

    assert trend["strategy_score"] > low_risk["strategy_score"]
    assert_score_range(trend)
    assert_score_range(low_risk)


def test_low_risk_quality_penalizes_high_risk_sample_more():
    frame = pd.DataFrame(
        [
            {
                "symbol": "RISKY",
                "Close": 100,
                "return_20d": 0.45,
                "return_10d": 0.28,
                "return_5d": 0.18,
                "amount": 80_000_000,
                "volume": 1_000_000,
                "turnover": 0.20,
                "volume_ratio": 2.1,
                "volatility": 0.95,
                "valid_trading_days": 90,
            }
        ]
    )

    balanced = calculate_strategy_scores(frame, preset_name="balanced_research")["scores"][0]
    low_risk = calculate_strategy_scores(frame, preset_name="low_risk_quality")["scores"][0]

    assert low_risk["strategy_score"] < balanced["strategy_score"] or low_risk["strategy_score"] == 0
    assert low_risk["strategy_score_components"]["adjusted_risk_penalty"] >= balanced["strategy_score_components"]["adjusted_risk_penalty"]
    assert_score_range(low_risk)


def test_volume_breakout_prefers_confirmed_active_volume_sample():
    confirmed = pd.DataFrame(
        [
            {
                "symbol": "VOLCONF",
                "Close": 100,
                "return_20d": 0.12,
                "return_10d": 0.06,
                "return_5d": 0.02,
                "amount": 180_000_000,
                "volume": 1_800_000,
                "turnover": 0.04,
                "volume_ratio": 1.6,
                "volatility": 0.32,
                "valid_trading_days": 90,
            }
        ]
    )
    weak = confirmed.copy(deep=True)
    weak["symbol"] = "VOLWEAK"
    weak["amount"] = 20_000_000
    weak["volume_ratio"] = 0.7

    confirmed_score = calculate_strategy_scores(confirmed, preset_name="volume_breakout")["scores"][0]
    weak_score = calculate_strategy_scores(weak, preset_name="volume_breakout")["scores"][0]

    assert confirmed_score["strategy_score"] > weak_score["strategy_score"]
    assert "volume_price_confirmed" in confirmed_score["strategy_score_components"]["preset_bonus_reasons"]
    assert_score_range(confirmed_score)


def test_high_elasticity_requires_volume_confirmation():
    confirmed = pd.DataFrame(
        [
            {
                "symbol": "ELASTICCONF",
                "Close": 100,
                "return_20d": 0.22,
                "return_10d": 0.12,
                "return_5d": 0.06,
                "amount": 180_000_000,
                "volume": 1_800_000,
                "turnover": 0.05,
                "volume_ratio": 1.6,
                "volatility": 0.70,
                "valid_trading_days": 90,
            }
        ]
    )
    unsupported = confirmed.copy(deep=True)
    unsupported["symbol"] = "ELASTICWEAK"
    unsupported["amount"] = 2_000_000
    unsupported["volume"] = 50_000
    unsupported["turnover"] = 0.001
    unsupported["volume_ratio"] = 0.6

    confirmed_score = calculate_strategy_scores(confirmed, preset_name="high_elasticity_watch")["scores"][0]
    unsupported_score = calculate_strategy_scores(unsupported, preset_name="high_elasticity_watch")["scores"][0]

    assert confirmed_score["strategy_score"] > unsupported_score["strategy_score"]
    assert "missing_volume_confirmation" in unsupported_score["strategy_score_components"]["preset_bonus_reasons"]
    assert_score_range(unsupported_score)


def test_strategy_scoring_unknown_preset_and_custom_config_are_safe():
    frame = pd.DataFrame(
        [
            {
                "symbol": "CUSTOMPRESET",
                "Close": 100,
                "return_20d": 0.08,
                "amount": 100_000_000,
                "volume": 1_000_000,
                "turnover": 0.03,
                "volume_ratio": 1.1,
                "valid_trading_days": 90,
            }
        ]
    )
    unknown = calculate_strategy_scores(frame, preset_name="does-not-exist")["scores"][0]
    custom = calculate_strategy_scores(
        frame,
        preset_config={
            "preset_name": "custom_internal",
            "weights": {"trend_score": 0.10, "momentum_score": 0.10, "volume_price_score": 0.40, "liquidity_score": 0.30, "baseline_score": 0.10},
        },
    )["scores"][0]

    assert unknown["preset_name"] == "balanced_research"
    assert custom["preset_name"] == "custom_internal"
    assert_score_range(unknown)
    assert_score_range(custom)


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
