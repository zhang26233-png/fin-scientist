import copy

from strategy.technical import (
    TECHNICAL_PROFILE_FIELDS,
    analyze_moving_average_structure,
    analyze_short_term_overheat,
    analyze_trend_quality,
    analyze_volatility_risk,
    analyze_volume_price_structure,
    build_technical_profile,
)


FORBIDDEN_TECHNICAL_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_TECHNICAL_WORDS:
        assert word not in text


def strong_row():
    return {
        "close": 120,
        "ma5": 115,
        "ma10": 110,
        "ma20": 100,
        "trend_score": 82,
        "momentum_score": 72,
        "return_20d": 0.18,
        "return_10d": 0.09,
        "return_5d": 0.04,
        "volume_ratio": 1.5,
        "amount": 160_000_000,
        "volume": 1_500_000,
        "turnover": 0.04,
        "volatility": 0.25,
        "recent_high": 121,
    }


def test_strategy_technical_import_and_empty_input_safe_return():
    result = build_technical_profile(None)

    assert set(TECHNICAL_PROFILE_FIELDS).issubset(result)
    assert result["ma_structure_label"] == "insufficient_ma_data"
    assert result["technical_strength"] == "uncertain"
    assert result["technical_profile_summary"]
    assert_no_forbidden_words(result)


def test_strategy_technical_missing_fields_safe_return():
    result = build_technical_profile({"symbol": "MISS1"})

    assert result["trend_quality_label"] == "insufficient_trend_data"
    assert result["volume_price_structure_label"] == "insufficient_volume_data"
    assert result["technical_strength"] == "uncertain"
    assert_no_forbidden_words(result)


def test_moving_average_structure_detects_bullish_and_bearish_alignment():
    bullish = {"close": 120, "ma5": 115, "ma10": 110, "ma20": 100}
    bearish = {"close": 80, "ma5": 85, "ma10": 90, "ma20": 100}

    assert analyze_moving_average_structure(bullish) == "bullish_alignment"
    assert analyze_moving_average_structure(bearish) == "bearish_alignment"


def test_trend_quality_detects_strong_trend():
    assert analyze_trend_quality(strong_row()) == "strong_trend"


def test_volume_price_structure_detects_confirmation_and_downside_risk():
    confirmed = strong_row()
    downside = strong_row()
    downside["return_5d"] = -0.08
    downside["return_20d"] = -0.04
    downside["volume_ratio"] = 1.8

    assert analyze_volume_price_structure(confirmed) == "volume_price_confirmed"
    assert analyze_volume_price_structure(downside) == "volume_downside_risk"


def test_short_term_overheat_and_volatility_risk_labels():
    overheated = {"return_5d": 0.18, "return_10d": 0.26, "return_20d": 0.42}
    volatile = {"volatility": 0.92}

    assert analyze_short_term_overheat(overheated) == "severe_overheat"
    assert analyze_volatility_risk(volatile) == "high_volatility"


def test_build_technical_profile_contains_all_fields_and_does_not_modify_source():
    source = strong_row()
    before = copy.deepcopy(source)

    result = build_technical_profile(source)

    assert set(TECHNICAL_PROFILE_FIELDS).issubset(result)
    assert result["ma_structure_label"] == "bullish_alignment"
    assert result["trend_quality_label"] == "strong_trend"
    assert result["technical_grade"] == "A"
    assert result["technical_style"] in {"trend_momentum", "volume_breakout"}
    assert result["technical_strength"] == "strong"
    assert result["technical_risk_level"] == "low"
    assert isinstance(result["technical_watch_points"], list)
    assert 1 <= len(result["technical_watch_points"]) <= 3
    assert result["technical_summary_short"]
    assert result["technical_profile_summary"]
    assert source == before
    assert_no_forbidden_words(result)


def test_technical_conclusion_detects_high_risk_overheat():
    row = strong_row()
    row.update({"return_5d": 0.18, "return_10d": 0.28, "return_20d": 0.42, "turnover": 0.18, "volatility": 0.92})

    result = build_technical_profile(row)

    assert result["technical_risk_level"] == "high"
    assert result["technical_grade"] in {"B", "C"}
    assert result["technical_style"] == "high_volatility_watch"
    assert any("波动风险" in point for point in result["technical_watch_points"])
    assert_no_forbidden_words(result)


def test_technical_conclusion_detects_weak_grade():
    row = {
        "close": 80,
        "ma5": 85,
        "ma10": 90,
        "ma20": 100,
        "trend_score": 28,
        "momentum_score": 25,
        "return_20d": -0.12,
        "return_5d": -0.06,
        "volume_ratio": 1.5,
        "volatility": 0.45,
    }

    result = build_technical_profile(row)

    assert result["ma_structure_label"] == "bearish_alignment"
    assert result["technical_grade"] in {"C", "D"}
    assert result["technical_strength"] == "weak"
    assert_no_forbidden_words(result)


def test_technical_watch_points_are_neutral():
    result = build_technical_profile(strong_row())

    assert result["technical_watch_points"]
    assert result["technical_summary_short"]
    assert_no_forbidden_words(result["technical_watch_points"])
    assert_no_forbidden_words(result["technical_summary_short"])
