"""Live web runner for the read-only A-share research pipeline."""

from __future__ import annotations

import copy
from datetime import date, timedelta
from typing import Any

import pandas as pd

from backtest.backtest_engine import build_backtest_dataset
from backtest.backtest_evaluation import build_backtest_evaluation
from backtest.return_analysis import build_return_analysis
from factor.factor_lab import build_factor_dataset
from screening.candidate_pool import build_candidate_pool
from screening.composite_score_engine import build_composite_quant_score
from screening.fundamental_screening import build_fundamental_screening
from screening.technical_screening import build_technical_screening
from selection.explain_engine import build_explainable_selection
from selection.stock_selection import build_stock_selection
from universe.a_share_universe import build_a_share_universe


LIVE_PIPELINE_FIELDS = [
    "ticker",
    "name",
    "universe_status",
    "fundamental_score",
    "technical_score",
    "composite_score",
    "candidate_pool",
    "candidate_rank",
    "backtest_available",
    "period_return",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "risk_level",
    "performance_label",
    "selection_score",
    "selection_rank",
    "selection_bucket",
    "selection_status",
    "selection_thesis",
    "selection_strengths",
    "selection_risks",
    "selection_explanation",
    "factor_ic",
    "factor_rank_ic",
    "factor_effectiveness_label",
]

DEMO_NOTICE = "当前为 Demo 数据，用于展示系统结构；接入真实行情后可替换为真实结果。"

DEMO_STOCKS = [
    ("600519", "贵州茅台", "Consumer"),
    ("300750", "宁德时代", "New Energy"),
    ("600036", "招商银行", "Financial"),
    ("601138", "工业富联", "Electronics"),
    ("300308", "中际旭创", "Communication"),
    ("300476", "胜宏科技", "Electronics"),
    ("002594", "比亚迪", "Auto"),
    ("000333", "美的集团", "Home Appliance"),
    ("601318", "中国平安", "Financial"),
    ("000858", "五粮液", "Consumer"),
    ("300059", "东方财富", "Financial"),
    ("600030", "中信证券", "Financial"),
    ("002475", "立讯精密", "Electronics"),
    ("002415", "海康威视", "Computer"),
    ("300760", "迈瑞医疗", "Medical"),
    ("601899", "紫金矿业", "Resource"),
    ("688256", "寒武纪", "Semiconductor"),
    ("002230", "科大讯飞", "AI"),
    ("603501", "韦尔股份", "Semiconductor"),
    ("601012", "隆基绿能", "New Energy"),
]


def _copy_frame(value: Any) -> pd.DataFrame:
    if value is None:
        return pd.DataFrame()
    if isinstance(value, pd.DataFrame):
        return value.copy(deep=True)
    if isinstance(value, list):
        return pd.DataFrame(copy.deepcopy(value))
    if isinstance(value, dict):
        return pd.DataFrame([copy.deepcopy(value)])
    return pd.DataFrame()


def _copy_price_history_dict(price_history_dict: Any) -> dict[str, pd.DataFrame]:
    if not isinstance(price_history_dict, dict):
        return {}
    copied: dict[str, pd.DataFrame] = {}
    for key, value in price_history_dict.items():
        copied[str(key)] = _copy_frame(value)
    return copied


def _build_demo_universe(max_stocks: int | None = None) -> pd.DataFrame:
    rows = []
    limit = max_stocks or len(DEMO_STOCKS)
    for index, (ticker, name, industry) in enumerate(DEMO_STOCKS[:limit], start=1):
        rows.append(
            {
                "ticker": ticker,
                "name": name,
                "market": "A股",
                "industry": industry,
                "list_date": "2010-01-01",
                "days_since_listing": 5000 - index,
                "is_st": False,
                "is_suspended": False,
                "status": "Available",
                "universe_status": "Available",
                "universe_total_count": min(limit, len(DEMO_STOCKS)),
                "universe_filtered_count": min(limit, len(DEMO_STOCKS)),
                "universe_summary": DEMO_NOTICE,
            }
        )
    frame = pd.DataFrame(rows)
    frame.attrs["universe_status"] = "Demo"
    frame.attrs["universe_total_count"] = len(frame)
    frame.attrs["universe_filtered_count"] = len(frame)
    frame.attrs["universe_summary"] = DEMO_NOTICE
    return frame


def _build_demo_fundamentals(universe: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for index, row in universe.reset_index(drop=True).iterrows():
        quality_cycle = index % 5
        rows.append(
            {
                "ticker": row["ticker"],
                "roe": [0.24, 0.18, 0.14, 0.10, 0.07][quality_cycle],
                "revenue_growth": [0.18, 0.28, 0.12, 0.08, -0.02][quality_cycle],
                "profit_growth": [0.16, 0.22, 0.10, 0.05, -0.04][quality_cycle],
                "gross_margin": [0.58, 0.34, 0.42, 0.25, 0.18][quality_cycle],
                "debt_ratio": [0.22, 0.38, 0.48, 0.56, 0.68][quality_cycle],
                "operating_cashflow": [120.0, 80.0, 60.0, 30.0, -10.0][quality_cycle],
                "pe": [28.0, 42.0, 18.0, 55.0, 75.0][quality_cycle],
                "pb": [6.0, 5.2, 1.4, 4.0, 7.5][quality_cycle],
            }
        )
    return pd.DataFrame(rows)


def _demo_history_for(index: int) -> pd.DataFrame:
    start = date.today() - timedelta(days=119)
    rows = []
    base = 20.0 + index * 4.0
    trend = [0.11, 0.07, 0.03, -0.02, 0.15][index % 5]
    drawdown_wave = [0.0, -0.018, 0.012, -0.026, 0.021]
    for day in range(120):
        progress = day / 119
        wave = drawdown_wave[(day + index) % len(drawdown_wave)]
        close = base * (1 + trend * progress + wave)
        volume = 1000000 + index * 50000 + (day % 20) * 18000
        rows.append({"date": start + timedelta(days=day), "close": round(max(close, 1.0), 2), "volume": volume})
    return pd.DataFrame(rows)


def _build_demo_price_history(universe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        str(row["ticker"]): _demo_history_for(index)
        for index, row in universe.reset_index(drop=True).iterrows()
    }


def _attach_factor_fields(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)
    factor_df = build_factor_dataset(result)
    if factor_df.empty or "ticker" not in factor_df.columns:
        for field in ["factor_ic", "factor_rank_ic", "factor_effectiveness_label"]:
            if field not in result.columns:
                result[field] = None
        return result

    preferred = factor_df[factor_df.get("factor_name").eq("selection_score")] if "factor_name" in factor_df.columns else pd.DataFrame()
    if preferred.empty:
        preferred = factor_df.drop_duplicates(subset=["ticker"], keep="first")
    else:
        preferred = preferred.drop_duplicates(subset=["ticker"], keep="first")

    factor_columns = ["ticker", "factor_name", "factor_ic", "factor_rank_ic", "factor_effectiveness_label"]
    merged = result.merge(preferred[factor_columns], on="ticker", how="left", suffixes=("", "_factor"))
    return merged


def _ensure_live_fields(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)
    for field in LIVE_PIPELINE_FIELDS:
        if field not in result.columns:
            result[field] = None
    return result


def _finalize(df: pd.DataFrame, *, is_demo: bool, source: str, message: str | None = None) -> pd.DataFrame:
    result = _ensure_live_fields(df)
    result.attrs["is_demo"] = bool(is_demo)
    result.attrs["data_source"] = source
    result.attrs["data_notice"] = message or (DEMO_NOTICE if is_demo else "Live pipeline result generated from available local/data-source inputs.")
    return result


def _run_pipeline(universe: pd.DataFrame, fundamental_df: pd.DataFrame | None, price_history_dict: dict[str, pd.DataFrame] | None) -> pd.DataFrame:
    history = _copy_price_history_dict(price_history_dict)
    fundamental = build_fundamental_screening(universe, fundamental_df=fundamental_df)
    technical = build_technical_screening(universe, price_data=history)
    composite = build_composite_quant_score(universe, fundamental, technical)
    candidate_pool = build_candidate_pool(composite)
    backtest_foundation = build_backtest_dataset(candidate_pool, price_history_dict=history)
    return_analysis = build_return_analysis(backtest_foundation, price_history_dict=history)
    backtest_evaluation = build_backtest_evaluation(return_analysis)
    stock_selection = build_stock_selection(backtest_evaluation)
    explainable_selection = build_explainable_selection(stock_selection)
    return _attach_factor_fields(explainable_selection)


def _build_demo_result(max_stocks: int | None = None) -> pd.DataFrame:
    universe = _build_demo_universe(max_stocks=max_stocks)
    fundamentals = _build_demo_fundamentals(universe)
    histories = _build_demo_price_history(universe)
    result = _run_pipeline(universe, fundamentals, histories)
    return _finalize(result, is_demo=True, source="Built-in demo", message=DEMO_NOTICE)


def run_live_pipeline(
    max_stocks: int = 100,
    use_sample_if_no_data: bool = True,
    price_history_dict: dict[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """Run the full read-only research pipeline for the Streamlit web app.

    The runner does not mutate caller inputs and falls back to a built-in demo
    research DataFrame when the live Universe/data chain is unavailable.
    """
    histories = _copy_price_history_dict(price_history_dict)
    try:
        universe = build_a_share_universe()
        universe = _copy_frame(universe)
        if max_stocks and not universe.empty:
            universe = universe.head(int(max_stocks)).copy(deep=True)
        if universe.empty:
            raise ValueError("A-share Universe is empty.")
        result = _run_pipeline(universe, fundamental_df=None, price_history_dict=histories)
        if result.empty:
            raise ValueError("Pipeline returned an empty result.")
        if use_sample_if_no_data and ("selection_score" not in result.columns or pd.to_numeric(result["selection_score"], errors="coerce").notna().sum() == 0):
            return _build_demo_result(max_stocks=max_stocks)
        return _finalize(result, is_demo=False, source="A-share Universe")
    except Exception as exc:
        if not use_sample_if_no_data:
            return _finalize(pd.DataFrame(), is_demo=False, source="Unavailable", message=f"Live pipeline failed: {exc}")
        return _build_demo_result(max_stocks=max_stocks)
