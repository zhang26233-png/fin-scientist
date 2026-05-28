from strategy.presets import get_default_strategy_preset, get_strategy_preset, list_strategy_presets


def test_strategy_presets_import_and_list_multiple_presets():
    presets = list_strategy_presets()

    assert "balanced_research" in presets
    assert "trend_momentum" in presets
    assert "volume_breakout" in presets
    assert "low_risk_quality" in presets
    assert "high_elasticity_watch" in presets
    assert len(presets) >= 5


def test_default_strategy_preset_is_balanced_and_safe_copy():
    preset = get_default_strategy_preset()
    preset["weights"]["trend_score"] = 0

    fresh = get_default_strategy_preset()

    assert fresh["preset_name"] == "balanced_research"
    assert fresh["weights"]["trend_score"] == 0.30
    assert fresh["risk_policy"]["risk_penalty_multiplier"] == 1.00


def test_unknown_strategy_preset_falls_back_to_default():
    preset = get_strategy_preset("unknown-preset")

    assert preset["preset_name"] == "balanced_research"
    assert preset["display_name"] == "平衡研究策略"


def test_legacy_preset_keys_remain_compatible():
    preset = get_strategy_preset("research_priority")

    assert preset["name"] == "研究优先级策略"
    assert preset["factor_weights"]["trend"] == 0.35
    assert preset["weights"]["trend_score"] == 0.30
