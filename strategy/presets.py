"""Strategy preset definitions for internal research workflows."""

import copy


DEFAULT_STRATEGY_PRESET = "balanced_research"


STRATEGY_PRESETS = {
    "balanced_research": {
        "preset_name": "balanced_research",
        "display_name": "平衡研究策略",
        "name": "平衡研究策略",
        "description": "平衡观察趋势、动量、量价、流动性、风险和数据质量。",
        "purpose": "用于平衡型研究优先级观察，保持内部 strategy_score 与既有校准逻辑兼容。",
        "weights": {
            "trend_score": 0.30,
            "momentum_score": 0.25,
            "volume_price_score": 0.20,
            "liquidity_score": 0.15,
            "baseline_score": 0.10,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 1.00,
            "overheat_penalty_multiplier": 1.00,
            "volume_downside_penalty_multiplier": 1.00,
            "low_liquidity_penalty_multiplier": 1.00,
            "high_volatility_penalty_multiplier": 1.00,
            "volume_confirmation_bonus": 0,
            "active_liquidity_bonus": 0,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.00},
        "factor_weights": {"trend": 0.35, "momentum": 0.25, "volatility": 0.20, "volume": 0.20},
        "filters": {"min_rows": 60, "min_price": 1.0, "max_abs_return": 0.30},
        "risk_controls": ["高波动风险", "短期涨幅风险", "数据缺失风险", "流动性风险"],
    },
    "trend_momentum": {
        "preset_name": "trend_momentum",
        "display_name": "趋势动量观察策略",
        "name": "趋势动量观察策略",
        "description": "更重视趋势、动量和量价配合，同时保留过热与放量下跌惩罚。",
        "purpose": "用于观察趋势和动量较强、仍需核验风险约束的研究对象。",
        "weights": {
            "trend_score": 0.38,
            "momentum_score": 0.30,
            "volume_price_score": 0.17,
            "liquidity_score": 0.05,
            "baseline_score": 0.10,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 0.95,
            "overheat_penalty_multiplier": 1.15,
            "volume_downside_penalty_multiplier": 1.10,
            "low_liquidity_penalty_multiplier": 0.90,
            "high_volatility_penalty_multiplier": 0.95,
            "volume_confirmation_bonus": 2,
            "trend_momentum_bonus": 5,
            "active_liquidity_bonus": 0,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.00},
        "factor_weights": {"trend": 0.40, "momentum": 0.35, "volatility": 0.10, "volume": 0.15},
        "filters": {"min_rows": 60, "min_price": 1.0, "max_abs_return": 0.35},
        "risk_controls": ["短期涨幅风险", "换手过热风险", "放量下跌风险"],
    },
    "volume_breakout": {
        "preset_name": "volume_breakout",
        "display_name": "量价启动观察策略",
        "name": "量价启动观察策略",
        "description": "更重视量价确认、成交额活跃和流动性，同时惩罚放量下跌与低流动性。",
        "purpose": "用于观察量价配合较强且成交活跃的研究对象。",
        "weights": {
            "trend_score": 0.18,
            "momentum_score": 0.17,
            "volume_price_score": 0.35,
            "liquidity_score": 0.20,
            "baseline_score": 0.10,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 1.00,
            "overheat_penalty_multiplier": 1.00,
            "volume_downside_penalty_multiplier": 1.30,
            "low_liquidity_penalty_multiplier": 1.25,
            "high_volatility_penalty_multiplier": 0.90,
            "volume_confirmation_bonus": 8,
            "volume_confirmation_threshold": 1.55,
            "active_liquidity_bonus": 3,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.00},
        "factor_weights": {"trend": 0.20, "momentum": 0.20, "volatility": 0.10, "volume": 0.50},
        "filters": {"min_rows": 60, "min_price": 1.0, "max_abs_return": 0.35},
        "risk_controls": ["放量下跌风险", "流动性风险", "换手过热风险"],
    },
    "low_risk_quality": {
        "preset_name": "low_risk_quality",
        "display_name": "低风险质量观察策略",
        "name": "低风险质量观察策略",
        "description": "更重视流动性、风险惩罚和数据质量，不追求极端动量。",
        "purpose": "用于观察风险约束和数据质量更稳健的研究对象。",
        "weights": {
            "trend_score": 0.20,
            "momentum_score": 0.10,
            "volume_price_score": 0.15,
            "liquidity_score": 0.35,
            "baseline_score": 0.20,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 1.25,
            "overheat_penalty_multiplier": 1.30,
            "volume_downside_penalty_multiplier": 1.25,
            "low_liquidity_penalty_multiplier": 1.35,
            "high_volatility_penalty_multiplier": 1.35,
            "volume_confirmation_bonus": 0,
            "active_liquidity_bonus": 2,
            "stable_quality_bonus": 10,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.35},
        "factor_weights": {"trend": 0.25, "momentum": 0.10, "volatility": 0.35, "volume": 0.30},
        "filters": {"min_rows": 90, "min_price": 1.0, "max_abs_return": 0.25},
        "risk_controls": ["高波动风险", "流动性风险", "数据缺失风险"],
    },
    "high_elasticity_watch": {
        "preset_name": "high_elasticity_watch",
        "display_name": "高弹性观察策略",
        "name": "高弹性观察策略",
        "description": "允许较高动量和波动，但要求成交额和量价确认支持。",
        "purpose": "用于观察弹性较高、仍需量价和流动性确认的研究对象。",
        "weights": {
            "trend_score": 0.24,
            "momentum_score": 0.32,
            "volume_price_score": 0.24,
            "liquidity_score": 0.10,
            "baseline_score": 0.10,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 0.90,
            "overheat_penalty_multiplier": 1.15,
            "volume_downside_penalty_multiplier": 1.15,
            "low_liquidity_penalty_multiplier": 1.25,
            "high_volatility_penalty_multiplier": 0.75,
            "volume_confirmation_bonus": 4,
            "elasticity_bonus": 10,
            "active_liquidity_bonus": 1,
            "missing_volume_confirmation_penalty": 8,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.05},
        "factor_weights": {"trend": 0.25, "momentum": 0.35, "volatility": 0.15, "volume": 0.25},
        "filters": {"min_rows": 60, "min_price": 1.0, "max_abs_return": 0.40},
        "risk_controls": ["短期涨幅风险", "高波动风险", "流动性风险"],
    },
    "research_priority": {
        "preset_name": "research_priority",
        "display_name": "研究优先级策略",
        "name": "研究优先级策略",
        "description": "兼容旧版 adapter 的研究优先级策略。",
        "purpose": "用于整理趋势、动量、波动和量能观察，辅助形成进一步研究候选池。",
        "weights": {
            "trend_score": 0.30,
            "momentum_score": 0.25,
            "volume_price_score": 0.20,
            "liquidity_score": 0.15,
            "baseline_score": 0.10,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 1.00,
            "overheat_penalty_multiplier": 1.00,
            "volume_downside_penalty_multiplier": 1.00,
            "low_liquidity_penalty_multiplier": 1.00,
            "high_volatility_penalty_multiplier": 1.00,
            "volume_confirmation_bonus": 0,
            "active_liquidity_bonus": 0,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.00},
        "factor_weights": {"trend": 0.35, "momentum": 0.25, "volatility": 0.20, "volume": 0.20},
        "filters": {"min_rows": 60, "min_price": 1.0, "max_abs_return": 0.30},
        "risk_controls": ["高波动风险", "短期涨幅风险", "数据缺失风险", "流动性风险"],
    },
    "stable_observation": {
        "preset_name": "stable_observation",
        "display_name": "稳健观察策略",
        "name": "稳健观察策略",
        "description": "兼容旧版 adapter 的稳健观察策略。",
        "purpose": "偏重数据完整性、波动约束和基础趋势确认，适合作为低波动研究样本预设。",
        "weights": {
            "trend_score": 0.20,
            "momentum_score": 0.10,
            "volume_price_score": 0.15,
            "liquidity_score": 0.35,
            "baseline_score": 0.20,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 1.25,
            "overheat_penalty_multiplier": 1.30,
            "volume_downside_penalty_multiplier": 1.25,
            "low_liquidity_penalty_multiplier": 1.35,
            "high_volatility_penalty_multiplier": 1.35,
            "volume_confirmation_bonus": 0,
            "active_liquidity_bonus": 2,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.35},
        "factor_weights": {"trend": 0.30, "momentum": 0.15, "volatility": 0.35, "volume": 0.20},
        "filters": {"min_rows": 90, "min_price": 1.0, "max_abs_return": 0.25},
        "risk_controls": ["高波动风险", "数据缺失风险", "流动性风险"],
    },
    "high_elasticity_observation": {
        "preset_name": "high_elasticity_observation",
        "display_name": "高弹性观察策略",
        "name": "高弹性观察策略",
        "description": "兼容旧版 adapter 的高弹性观察策略。",
        "purpose": "偏重阶段表现和量能变化，用于发现需要进一步核验的高波动研究样本。",
        "weights": {
            "trend_score": 0.24,
            "momentum_score": 0.32,
            "volume_price_score": 0.24,
            "liquidity_score": 0.10,
            "baseline_score": 0.10,
        },
        "risk_policy": {
            "risk_penalty_multiplier": 0.90,
            "overheat_penalty_multiplier": 1.15,
            "volume_downside_penalty_multiplier": 1.15,
            "low_liquidity_penalty_multiplier": 1.25,
            "high_volatility_penalty_multiplier": 0.75,
            "volume_confirmation_bonus": 4,
            "elasticity_bonus": 10,
            "active_liquidity_bonus": 1,
            "missing_volume_confirmation_penalty": 8,
        },
        "data_quality_policy": {"data_quality_penalty_multiplier": 1.05},
        "factor_weights": {"trend": 0.25, "momentum": 0.35, "volatility": 0.15, "volume": 0.25},
        "filters": {"min_rows": 60, "min_price": 1.0, "max_abs_return": 0.40},
        "risk_controls": ["短期涨幅风险", "高波动风险", "数据缺失风险"],
    },
}


def _copy_preset(preset):
    copied = copy.deepcopy(preset)
    copied.setdefault("preset_name", "")
    copied.setdefault("display_name", copied.get("name", ""))
    copied.setdefault("description", copied.get("purpose", ""))
    copied.setdefault("weights", {})
    copied.setdefault("risk_policy", {})
    copied.setdefault("data_quality_policy", {})
    copied.setdefault("factor_weights", {})
    copied.setdefault("filters", {})
    copied.setdefault("risk_controls", [])
    return copied


def get_default_strategy_preset():
    return _copy_preset(STRATEGY_PRESETS[DEFAULT_STRATEGY_PRESET])


def get_strategy_preset(preset_key):
    preset = STRATEGY_PRESETS.get(preset_key)
    if preset is None:
        return get_default_strategy_preset()
    return _copy_preset(preset)


def list_strategy_presets():
    return {key: get_strategy_preset(key) for key in STRATEGY_PRESETS}


__all__ = [
    "DEFAULT_STRATEGY_PRESET",
    "STRATEGY_PRESETS",
    "get_default_strategy_preset",
    "get_strategy_preset",
    "list_strategy_presets",
]
