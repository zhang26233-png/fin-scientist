"""Sector-strength aggregation helpers for screening results."""

import math

import pandas as pd

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


def format_metric(value):
    number = to_number(value)
    return MISSING if pd.isna(number) else f"{number:.2f}"


def format_percent(value, missing_text=INSUFFICIENT):
    number = to_number(value)
    return missing_text if pd.isna(number) else f"{number:.2%}"


def format_symbol_list(symbols):
    return "、".join(symbols) if symbols else "暂无明显标的"


def generate_sector_strength_summary(result_df, all_scored_df=None):
    source_df = all_scored_df if isinstance(all_scored_df, pd.DataFrame) and not all_scored_df.empty else result_df
    if source_df is None or source_df.empty or "板块" not in source_df.columns:
        return pd.DataFrame()

    rows = []
    for sector, group in source_df.groupby("板块", dropna=False):
        sector_name = sector if str(sector or "").strip() else "板块暂缺"
        score_values = group["研究优先级评分"].apply(to_number) if "研究优先级评分" in group else pd.Series(dtype=float)
        score_values = score_values.dropna()
        score_positive_count = int((score_values > 0).sum())
        stock_count = len(group)

        def mean_percent(column):
            if column not in group:
                return math.nan
            return group[column].apply(parse_display_percent).dropna().mean()

        def mean_number(column):
            if column not in group:
                return math.nan
            return group[column].apply(to_number).dropna().mean()

        note = "样本较少，仅作参考。" if stock_count < 2 else "基于当前股票池样本的初步统计。"
        rows.append(
            {
                "板块": sector_name,
                "股票数量": stock_count,
                "平均研究优先级评分": format_metric(score_values.mean()) if len(score_values) else INSUFFICIENT,
                "触发研究优先级条件数量": score_positive_count,
                "触发比例": format_percent(score_positive_count / stock_count if stock_count else math.nan),
                "平均近 20 日涨跌幅": format_percent(mean_percent("近 20 日涨跌幅")),
                "平均近 60 日涨跌幅": format_percent(mean_percent("近 60 日涨跌幅")),
                "平均成交量放大倍数": format_metric(mean_number("成交量放大倍数")) if not pd.isna(mean_number("成交量放大倍数")) else INSUFFICIENT,
                "平均年化波动率": format_percent(mean_percent("年化波动率")),
                "平均最大回撤": format_percent(mean_percent("最大回撤")),
                "说明": note,
                "_sort_score": score_values.mean() if len(score_values) else -1,
            }
        )
    sector_df = pd.DataFrame(rows)
    if not sector_df.empty:
        sector_df = sector_df.sort_values("_sort_score", ascending=False).drop(columns=["_sort_score"])
    return sector_df


def generate_sector_strength_text(sector_df):
    if sector_df is None or sector_df.empty:
        return "当前股票池暂无可用于板块强度初步统计的数据。该统计仅基于当前股票池样本，不代表全市场板块强弱，也不构成投资建议。"

    top_score = sector_df.head(3)["板块"].tolist()
    trigger_df = sector_df.copy()
    trigger_df["_trigger_count"] = trigger_df["触发研究优先级条件数量"].apply(to_number)
    top_trigger = trigger_df.sort_values("_trigger_count", ascending=False).head(3)["板块"].tolist()

    high_risk = []
    for _, row in sector_df.iterrows():
        vol = parse_display_percent(row.get("平均年化波动率"))
        drawdown = parse_display_percent(row.get("平均最大回撤"))
        if (not pd.isna(vol) and vol > 0.60) or (not pd.isna(drawdown) and abs(drawdown) > 0.25):
            high_risk.append(row["板块"])

    return "\n\n".join(
        [
            f"当前股票池中平均研究优先级评分相对较高的板块包括：{format_symbol_list(top_score)}。",
            f"触发研究优先级条件的股票数量相对较多的板块包括：{format_symbol_list(top_trigger)}。",
            f"波动率或最大回撤相对较高的板块包括：{format_symbol_list(high_risk[:3])}。",
            "该统计仅基于当前股票池样本，不代表全市场板块强弱，也不构成投资建议。",
        ]
    )

__all__ = ["generate_sector_strength_summary", "generate_sector_strength_text"]
