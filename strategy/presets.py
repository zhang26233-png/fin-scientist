"""Strategy preset definitions for future research workflows."""

STRATEGY_PRESETS = {
    "research_priority": {
        "name": "研究优先级策略",
        "purpose": "用于整理趋势、动量、波动和量能观察，辅助形成进一步研究候选池。",
        "factor_weights": {
            "trend": 0.35,
            "momentum": 0.25,
            "volatility": 0.20,
            "volume": 0.20,
        },
        "filters": {
            "min_rows": 60,
            "min_price": 1.0,
            "max_abs_return": 0.30,
        },
        "risk_controls": ["高波动风险", "短期涨幅风险", "数据缺失风险", "流动性风险"],
    },
    "stable_observation": {
        "name": "稳健观察策略",
        "purpose": "偏重数据完整性、波动约束和基础趋势确认，适合作为低波动研究样本预设。",
        "factor_weights": {
            "trend": 0.30,
            "momentum": 0.15,
            "volatility": 0.35,
            "volume": 0.20,
        },
        "filters": {
            "min_rows": 90,
            "min_price": 1.0,
            "max_abs_return": 0.25,
        },
        "risk_controls": ["高波动风险", "数据缺失风险", "流动性风险"],
    },
    "high_elasticity_observation": {
        "name": "高弹性观察策略",
        "purpose": "偏重阶段表现和量能变化，用于发现需要进一步核验的高波动研究样本。",
        "factor_weights": {
            "trend": 0.25,
            "momentum": 0.35,
            "volatility": 0.15,
            "volume": 0.25,
        },
        "filters": {
            "min_rows": 60,
            "min_price": 1.0,
            "max_abs_return": 0.40,
        },
        "risk_controls": ["短期涨幅风险", "高波动风险", "数据缺失风险"],
    },
}


def get_strategy_preset(preset_key):
    preset = STRATEGY_PRESETS.get(preset_key)
    if preset is None:
        return None
    return {
        "name": preset["name"],
        "purpose": preset["purpose"],
        "factor_weights": dict(preset["factor_weights"]),
        "filters": dict(preset["filters"]),
        "risk_controls": list(preset["risk_controls"]),
    }


def list_strategy_presets():
    return {key: get_strategy_preset(key) for key in STRATEGY_PRESETS}


__all__ = [
    "STRATEGY_PRESETS",
    "get_strategy_preset",
    "list_strategy_presets",
]
