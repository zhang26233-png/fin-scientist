"""Read-only adapter from screening result frames to strategy diagnostics."""

import math

import pandas as pd

from strategy.factors import build_factor_snapshot
from strategy.filters import apply_basic_filters, check_min_turnover
from strategy.presets import get_strategy_preset
from strategy.risk import build_risk_labels, risk_tags_to_text

DEFAULT_PRESET_KEY = "research_priority"

FIELD_ALIASES = {
    "symbol": ("股票代码", "symbol", "ticker", "code"),
    "name": ("股票名称", "name", "stock_name"),
    "close": ("最新价格", "最新价", "close", "price", "Close"),
    "change_pct": ("涨跌幅", "pct_chg", "change_pct"),
    "return_20d": ("近 20 日涨跌幅", "return_20d", "20d_return"),
    "return_60d": ("近 60 日涨跌幅", "return_60d", "60d_return"),
    "volume": ("成交量", "volume", "Volume"),
    "amount": ("成交额", "amount", "turnover_amount"),
    "turnover": ("换手率", "turnover"),
    "sector": ("板块", "sector"),
    "industry": ("行业", "industry"),
    "score": ("综合研究观察评分", "研究优先级评分", "score"),
    "volatility": ("年化波动率", "volatility", "annual_volatility"),
    "max_drawdown": ("最大回撤", "max_drawdown"),
    "volume_ratio": ("成交量放大倍数", "volume_ratio"),
    "valid_days": ("有效交易日数量", "valid_trading_days"),
    "data_quality": ("数据质量", "data_quality"),
}


def to_number(value):
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").replace("%", "").strip()
    try:
        number = float(text)
    except ValueError:
        return math.nan
    if "%" in str(value):
        return number / 100
    return number


def _find_column(columns, aliases):
    for alias in aliases:
        if alias in columns:
            return alias
    lowered = {str(column).lower(): column for column in columns}
    for alias in aliases:
        column = lowered.get(str(alias).lower())
        if column is not None:
            return column
    return None


def infer_field_mapping(result_df):
    if not isinstance(result_df, pd.DataFrame):
        return {name: None for name in FIELD_ALIASES}
    columns = list(result_df.columns)
    return {name: _find_column(columns, aliases) for name, aliases in FIELD_ALIASES.items()}


def _read_mapped(row, mapping, field):
    column = mapping.get(field)
    if column is None:
        return None
    return row.get(column)


def _format_identity(row, mapping, index):
    symbol = _read_mapped(row, mapping, "symbol")
    name = _read_mapped(row, mapping, "name")
    return {
        "row_index": int(index) if isinstance(index, int) else str(index),
        "symbol": "" if symbol is None else str(symbol),
        "name": "" if name is None else str(name),
        "sector": "" if _read_mapped(row, mapping, "sector") is None else str(_read_mapped(row, mapping, "sector")),
        "industry": "" if _read_mapped(row, mapping, "industry") is None else str(_read_mapped(row, mapping, "industry")),
    }


def _build_price_frame(row, mapping):
    close = to_number(_read_mapped(row, mapping, "close"))
    if math.isnan(close) or close <= 0:
        return pd.DataFrame()

    return_20d = to_number(_read_mapped(row, mapping, "return_20d"))
    change_pct = to_number(_read_mapped(row, mapping, "change_pct"))
    period_return = return_20d if not math.isnan(return_20d) else change_pct
    rows = 61 if not math.isnan(period_return) and period_return > -0.95 else 1

    if rows > 1:
        start_price = close / (1 + period_return)
        close_values = pd.Series(
            [start_price + (close - start_price) * index / (rows - 1) for index in range(rows)],
            dtype=float,
        )
    else:
        close_values = pd.Series([close], dtype=float)

    volume = to_number(_read_mapped(row, mapping, "volume"))
    amount = to_number(_read_mapped(row, mapping, "amount"))
    if math.isnan(volume) and not math.isnan(amount) and close > 0:
        volume = amount / close
    volume_values = [volume if not math.isnan(volume) and volume > 0 else 0.0 for _ in range(rows)]

    return pd.DataFrame({"Close": close_values, "Volume": volume_values})


def _build_risk_metrics(row, mapping):
    valid_days = to_number(_read_mapped(row, mapping, "valid_days"))
    volume_ratio = to_number(_read_mapped(row, mapping, "volume_ratio"))
    return {
        "年化波动率": to_number(_read_mapped(row, mapping, "volatility")),
        "近 20 日涨跌幅": to_number(_read_mapped(row, mapping, "return_20d")),
        "成交量放大倍数": volume_ratio,
        "有效交易日数量": 0 if math.isnan(valid_days) else int(valid_days),
        "成交量数据缺失": math.isnan(to_number(_read_mapped(row, mapping, "volume"))) and math.isnan(volume_ratio),
        "基本面字段缺失较多": False,
    }


def _build_filter_flags(price_frame, row, mapping, preset):
    filter_config = preset.get("filters", {}) if isinstance(preset, dict) else {}
    flags = apply_basic_filters(
        price_frame,
        min_rows=filter_config.get("min_rows", 20),
        min_price=filter_config.get("min_price", 1.0),
    )
    amount = to_number(_read_mapped(row, mapping, "amount"))
    turnover_check = check_min_turnover(
        price_frame,
        min_average_turnover=amount if not math.isnan(amount) else None,
    )
    return {
        "passed": bool(flags["passed"] and turnover_check["passed"]),
        "checks": list(flags["checks"]) + [turnover_check],
    }


def _summarize_diagnostics(identity, factor_scores, filter_flags, risk_tags):
    unresolved_factors = [
        name for name, value in factor_scores.items() if value.get("score") == "无法计算"
    ]
    risk_names = [item.get("tag", "") for item in risk_tags if isinstance(item, dict)]
    label = identity.get("symbol") or identity.get("name") or f"row-{identity.get('row_index')}"
    parts = [f"{label} 已生成只读策略诊断。"]
    if unresolved_factors:
        parts.append("部分因子因字段或样本不足无法计算：" + "、".join(unresolved_factors) + "。")
    parts.append("过滤检查" + ("通过。" if filter_flags.get("passed") else "存在待核验项。"))
    parts.append("风险标签：" + ("、".join(risk_names) if risk_names else "暂无主要标签") + "。")
    parts.append("该诊断仅用于研究优先级辅助，不构成投资建议。")
    return "".join(parts)


def build_strategy_diagnostics(result_df, preset_key=DEFAULT_PRESET_KEY):
    preset = get_strategy_preset(preset_key) or get_strategy_preset(DEFAULT_PRESET_KEY)
    preset_name = preset["name"] if preset else ""
    mapping = infer_field_mapping(result_df)

    if not isinstance(result_df, pd.DataFrame) or result_df.empty:
        risk_tags = build_risk_labels(None)
        return {
            "preset_name": preset_name,
            "field_mapping": mapping,
            "diagnostics": [],
            "diagnostics_summary": "输入结果为空，未生成候选对象策略诊断。该诊断仅用于研究优先级辅助，不构成投资建议。",
            "risk_tags": risk_tags,
            "risk_notes": risk_tags_to_text(risk_tags),
        }

    source = result_df.copy(deep=True)
    diagnostics = []
    for index, row in source.iterrows():
        identity = _format_identity(row, mapping, index)
        price_frame = _build_price_frame(row, mapping)
        factor_scores = build_factor_snapshot(price_frame)
        filter_flags = _build_filter_flags(price_frame, row, mapping, preset)
        risk_tags = build_risk_labels(_build_risk_metrics(row, mapping))
        risk_notes = risk_tags_to_text(risk_tags)
        diagnostics.append(
            {
                "identity": identity,
                "factor_scores": factor_scores,
                "filter_flags": filter_flags,
                "risk_tags": risk_tags,
                "risk_notes": risk_notes,
                "preset_name": preset_name,
                "diagnostics_summary": _summarize_diagnostics(identity, factor_scores, filter_flags, risk_tags),
            }
        )

    return {
        "preset_name": preset_name,
        "field_mapping": mapping,
        "diagnostics": diagnostics,
        "diagnostics_summary": f"已为 {len(diagnostics)} 个候选对象生成只读策略诊断。该结果未接入现有页面、评分或排序。",
    }


__all__ = [
    "DEFAULT_PRESET_KEY",
    "FIELD_ALIASES",
    "build_strategy_diagnostics",
    "infer_field_mapping",
]
