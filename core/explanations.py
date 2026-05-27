"""Rule-based explanation text for screening and analysis results."""

import math

import pandas as pd

from core.scoring import FUNDAMENTAL_FIELDS

MISSING = "数据暂缺"
INSUFFICIENT = "数据不足"

def is_missing(value):
    if value in (None, "", MISSING, INSUFFICIENT):
        return True
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False

def to_number(value):
    if is_missing(value):
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def parse_display_percent(value):
    if is_missing(value):
        return math.nan
    text = str(value).strip()
    if text.endswith("%"):
        return to_number(text[:-1]) / 100
    return to_number(value)

def format_percent(value, missing_text=INSUFFICIENT):
    number = to_number(value)
    return missing_text if pd.isna(number) else f"{number:.2%}"


def format_large_number(value):
    number = to_number(value)
    if pd.isna(number):
        return MISSING
    abs_value = abs(number)
    if abs_value >= 1_0000_0000_0000:
        return f"{number / 1_0000_0000_0000:.2f}万亿"
    if abs_value >= 1_0000_0000:
        return f"{number / 1_0000_0000:.2f}亿"
    if abs_value >= 1_0000:
        return f"{number / 1_0000:.2f}万"
    return f"{number:,.0f}"

def format_symbol_list(symbols):
    return "、".join(symbols) if symbols else "暂无明显标的"

def join_explanation_items(items):
    clean_items = [str(item).strip() for item in items if str(item or "").strip()]
    return "；".join(clean_items)


def generate_selection_reasons(metrics):
    if not isinstance(metrics, dict):
        return ["当前指标未形成足够明确的研究优先级理由。"]

    reasons = []
    return_20d = to_number(metrics.get("近 20 日涨跌幅"))
    return_60d = to_number(metrics.get("近 60 日涨跌幅"))
    volume_ratio = to_number(metrics.get("成交量放大倍数"))
    data_quality = str(metrics.get("数据质量", ""))

    if metrics.get("当前价格是否高于 MA20") is True:
        reasons.append("当前价格站上 20 日均线，短期趋势相对较强。")
    if metrics.get("当前价格是否高于 MA60") is True:
        reasons.append("当前价格站上 60 日均线，中期趋势相对健康。")
    if metrics.get("MA20 是否高于 MA60") is True:
        reasons.append("MA20 高于 MA60，均线结构相对偏强。")
    if not pd.isna(return_20d) and return_20d > 0.10:
        reasons.append("近 20 日涨幅超过 10%，近期动能较强。")
    if not pd.isna(return_60d) and return_60d > 0.20:
        reasons.append("近 60 日涨幅超过 20%，中期表现较强。")
    if not pd.isna(volume_ratio) and volume_ratio > 1.8:
        reasons.append("近期成交量明显放大，说明短期交易活跃度提升。")
    elif not pd.isna(volume_ratio) and volume_ratio > 1.3:
        reasons.append("最近 5 日平均成交量高于 20 日均量，市场关注度有所上升。")
    if "数据较完整" in data_quality:
        reasons.append("当前行情样本较完整，指标计算基础相对充分。")

    if not reasons:
        return ["当前指标未形成足够明确的研究优先级理由。"]
    return reasons[:4]


def generate_screening_risk_warnings(metrics):
    warnings = []
    if not isinstance(metrics, dict):
        return ["当前指标不足，无法生成完整风险提示。", "当前结果只代表研究优先级，不代表买入、卖出或持有建议。"]

    return_20d = to_number(metrics.get("近 20 日涨跌幅"))
    max_drawdown = to_number(metrics.get("最大回撤"))
    annual_volatility = to_number(metrics.get("年化波动率"))
    volume_ratio = to_number(metrics.get("成交量放大倍数"))

    if not pd.isna(return_20d) and return_20d > 0.40:
        warnings.append("近 20 日涨幅较高，存在短期追高风险。")
    if not pd.isna(max_drawdown) and abs(max_drawdown) > 0.35:
        warnings.append("历史最大回撤超过 35%，该标的波动和回撤风险较高。")
    if not pd.isna(annual_volatility) and annual_volatility > 0.80:
        warnings.append("年化波动率较高，不适合低风险偏好者。")
    if metrics.get("有效交易日数量", 0) < 60:
        warnings.append("有效交易日不足 60 个，指标可靠性有限。")
    if metrics.get("成交量数据缺失") or pd.isna(volume_ratio):
        warnings.append("成交量数据缺失或不足，流动性判断不充分。")
    if metrics.get("使用备用数据源"):
        warnings.append("该标的数据来自备用数据源，不同数据源在复权口径和字段完整性上可能存在差异。")
    if "内置示例数据" in str(metrics.get("基本面数据源", "")):
        warnings.append("基本面数据来自内置示例，可能与最新真实财务数据不一致，需进一步核验。")
    if metrics.get("基本面字段缺失较多"):
        warnings.append("基本面字段缺失较多，当前基本面质量判断可靠性有限。")

    if not warnings:
        warnings.append("暂未触发主要风险阈值，但仍需结合基本面、消息面、板块环境和市场情绪进一步验证。")
    warnings.append("当前结果只代表研究优先级，不代表买入、卖出或持有建议。")
    return warnings


def generate_screening_summary(result_df, failed_items=None, insufficient_items=None):
    failed_items = failed_items or []
    insufficient_items = insufficient_items or []
    total_attr = result_df.attrs.get("total_count") if isinstance(result_df, pd.DataFrame) else None
    if result_df is None or result_df.empty:
        total_count = total_attr if isinstance(total_attr, int) else len(failed_items) + len(insufficient_items)
        return (
            f"本次共覆盖 {total_count} 只股票，其中成功生成研究优先级评分 0 只。\n\n"
            "本次未形成可排序的研究候选池，请先检查行情数据、字段完整性和数据源状态。\n\n"
            "下一步研究方向：核查公司基本面；核查行业和板块强度；核查近期公告和消息催化；"
            "核查估值水平和财务质量；用回测模块验证规则有效性。\n\n"
            "该结果仅代表研究优先级排序，不构成投资建议或交易指令。"
        )

    total_count = total_attr if isinstance(total_attr, int) else len(result_df) + len(failed_items)
    scored_count = len(result_df)
    summary_parts = [f"本次共覆盖 {total_count} 只股票，其中成功生成研究优先级评分 {scored_count} 只。"]

    ma20_count = int((result_df.get("是否高于 MA20") == "是").sum()) if "是否高于 MA20" in result_df else 0
    ma60_count = int((result_df.get("是否高于 MA60") == "是").sum()) if "是否高于 MA60" in result_df else 0
    volume_count = 0
    return_20_count = 0
    if "成交量放大倍数" in result_df:
        volume_values = result_df["成交量放大倍数"].apply(to_number)
        volume_count = int((volume_values > 1.3).sum())
    if "近 20 日涨跌幅" in result_df:
        return_20_values = result_df["近 20 日涨跌幅"].astype(str).str.rstrip("%").apply(to_number) / 100
        return_20_count = int((return_20_values > 0.10).sum())

    common_traits = []
    if ma20_count >= max(1, math.ceil(scored_count / 2)):
        common_traits.append("多数候选对象站上 MA20")
    if ma60_count >= max(1, math.ceil(scored_count / 2)):
        common_traits.append("多数候选对象站上 MA60")
    if volume_count > 0:
        common_traits.append("部分候选对象成交量放大")
    if return_20_count > 0:
        common_traits.append("部分候选对象近 20 日涨幅较高")
    summary_parts.append("Top 候选池共性：" + ("；".join(common_traits) if common_traits else "当前候选对象未形成特别集中的量价共性。"))

    risk_text = "；".join(result_df["风险提示"].fillna("").astype(str).tolist()) if "风险提示" in result_df else ""
    risk_traits = []
    if "短期追高风险" in risk_text:
        risk_traits.append("短期涨幅较高")
    if "回撤风险较高" in risk_text:
        risk_traits.append("历史回撤较大")
    if "年化波动率较高" in risk_text:
        risk_traits.append("波动率较高")
    if "备用数据源" in risk_text:
        risk_traits.append("数据源使用备用源")
    if "指标可靠性有限" in risk_text or "流动性判断不充分" in risk_text:
        risk_traits.append("数据质量存在差异")
    summary_parts.append("主要风险特征：" + ("；".join(risk_traits) if risk_traits else "暂未观察到集中触发的主要风险阈值。"))

    if "基本面数据源" in result_df:
        source_text = result_df["基本面数据源"].fillna("").astype(str)
        fundamental_count = int((source_text != "数据暂缺").sum())
        akshare_count = int(source_text.str.contains("AkShare", regex=False).sum())
        sample_count = int(source_text.str.contains("内置示例数据", regex=False).sum())
        summary_parts.append(
            f"基本面数据覆盖：本次有 {fundamental_count} 只股票获得基本面数据，其中 AkShare 基本面数据 {akshare_count} 只，内置示例数据 {sample_count} 只。"
        )
    if {"研究优先级评分", "基本面质量评分", "股票代码"}.issubset(result_df.columns):
        strong_df = result_df[
            (result_df["研究优先级评分"].apply(to_number) >= 50)
            & (result_df["基本面质量评分"].apply(to_number) >= 50)
        ]
        strong_symbols = strong_df["股票代码"].head(5).tolist()
        summary_parts.append(
            "同时具备较高研究优先级评分和较高基本面质量评分的候选对象："
            + (format_symbol_list(strong_symbols) if strong_symbols else "暂无明显对象")
            + "。"
        )

    summary_parts.append(
        "下一步研究方向：核查公司基本面；核查行业和板块强度；核查近期公告和消息催化；"
        "核查估值水平和财务质量；用回测模块验证规则有效性。"
    )
    summary_parts.append("综合研究观察评分只是量价与基本面维度的研究排序，不构成投资建议或交易指令。")
    return "\n\n".join(summary_parts)

def generate_fundamental_summary(valuation, financial=None):
    if financial is None:
        fundamental_data = valuation if isinstance(valuation, dict) else {}
        if not fundamental_data or all(is_missing(fundamental_data.get(field)) for field in FUNDAMENTAL_FIELDS):
            return "基本面数据暂缺，需后续补充财务与估值信息。"
        parts = []
        roe = to_number(fundamental_data.get("roe"))
        revenue_yoy = to_number(fundamental_data.get("revenue_yoy"))
        net_profit_yoy = to_number(fundamental_data.get("net_profit_yoy"))
        debt_asset_ratio = to_number(fundamental_data.get("debt_asset_ratio"))
        pe_ttm = to_number(fundamental_data.get("pe_ttm"))
        pb = to_number(fundamental_data.get("pb"))
        if not pd.isna(roe) and roe >= 0.15:
            parts.append("ROE 水平较高，盈利能力相对较强。")
        if not pd.isna(revenue_yoy) and revenue_yoy > 0 and not pd.isna(net_profit_yoy) and net_profit_yoy > 0:
            parts.append("营收与利润保持增长，成长性表现较好。")
        if not pd.isna(debt_asset_ratio) and debt_asset_ratio < 0.50:
            parts.append("资产负债率较低，财务结构相对稳健。")
        if (not pd.isna(pe_ttm) and pe_ttm > 80) or (not pd.isna(pb) and pb > 10):
            parts.append("估值指标偏高，需关注估值消化压力。")
        if "内置示例数据" in str(fundamental_data.get("fundamental_source", "")):
            parts.append("当前基本面数据来自内置示例，仅用于学习和原型演示，需用正式数据源进一步核验。")
        return " ".join(parts) if parts else "当前基本面字段可用于初步观察，但仍需结合正式财务数据进一步核验。"

    available = [value for value in list(valuation.values()) + list(financial.values()) if not is_missing(value)]
    if not available:
        return {"数据可信度提示": "当前可用基本面数据不足，不能形成完整判断。"}

    pe = to_number(valuation["pe"])
    pb = to_number(valuation["pb"])
    gross_margin = to_number(financial["gross_margin"])
    debt = to_number(financial["total_debt"])
    cash = to_number(financial["total_cash"])
    fcf = to_number(financial["free_cash_flow"])

    if pd.isna(pe):
        valuation_text = "PE 数据暂缺，估值水平需要结合其他指标和同行对比。"
    elif pe > 50:
        valuation_text = "PE 较高，市场可能已经计入较强增长预期。"
    elif pe > 0 and pe < 15:
        valuation_text = "PE 相对较低，但需排查盈利周期、行业景气度和一次性因素。"
    else:
        valuation_text = "PE 处于中间区间，仍需结合增速、利润率和同行估值判断。"

    margin_text = (
        "毛利率数据暂缺，盈利质量判断不完整。"
        if pd.isna(gross_margin)
        else f"毛利率为 {format_percent(gross_margin, MISSING)}，可用于观察产品竞争力和成本压力。"
    )
    balance_text = (
        "现金和债务数据暂缺，资产负债观察不完整。"
        if pd.isna(debt) or pd.isna(cash)
        else f"总现金为 {format_large_number(cash)}，总债务为 {format_large_number(debt)}，需进一步观察偿债压力。"
    )
    cashflow_text = (
        "自由现金流数据暂缺，现金创造能力还需要财报验证。"
        if pd.isna(fcf)
        else f"自由现金流为 {format_large_number(fcf)}，可辅助判断利润质量。"
    )

    return {
        "估值观察": valuation_text,
        "盈利质量观察": margin_text,
        "资产负债观察": balance_text,
        "现金流观察": cashflow_text,
        "数据可信度提示": "yfinance 与 akshare 的基本面字段可能缺失、滞后或口径不一致，需回到正式财报交叉验证。",
    }

__all__ = [
    "generate_fundamental_summary",
    "generate_screening_risk_warnings",
    "generate_screening_summary",
    "generate_selection_reasons",
    "join_explanation_items",
]
