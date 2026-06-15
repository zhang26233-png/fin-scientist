"""Live web runner for the read-only A-share research pipeline."""

from __future__ import annotations

import copy
from datetime import date, timedelta
from typing import Any

import pandas as pd

from backtest.backtest_engine import build_backtest_dataset
from backtest.backtest_evaluation import build_backtest_evaluation
from data.a_share_loader import load_a_share_universe
from data.fundamental_loader import build_fundamental_dataset
from data.kline_loader import build_price_history_dict
from backtest.return_analysis import build_return_analysis
from factor.factor_lab import build_factor_dataset
from fundamental.fundamental_engine import FUNDAMENTAL_RESEARCH_FIELDS, build_fundamental_research
from research.score_activation import ACTIVATED_RESEARCH_FIELDS, activate_research_scores
from screening.candidate_pool import build_candidate_pool
from screening.composite_score_engine import build_composite_quant_score
from screening.fundamental_screening import build_fundamental_screening
from screening.technical_screening import build_technical_screening
from selection.explain_engine import build_explainable_selection
from selection.stock_selection import build_stock_selection
from technical.indicator_engine import REAL_TECHNICAL_INDICATOR_FIELDS, build_real_technical_indicators


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
    *REAL_TECHNICAL_INDICATOR_FIELDS,
    *FUNDAMENTAL_RESEARCH_FIELDS,
    *ACTIVATED_RESEARCH_FIELDS,
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
        if key == "_attrs":
            continue
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
    frame.attrs["data_source"] = "Demo"
    frame.attrs["data_status"] = "Fallback"
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


def _select_kline_tickers(df: pd.DataFrame, max_kline_stocks: int) -> list[str]:
    if df.empty or "ticker" not in df.columns or max_kline_stocks <= 0:
        return []
    source = df.copy(deep=True)
    if "activated_selection_score" in source.columns:
        score = pd.to_numeric(source["activated_selection_score"], errors="coerce")
        source = source.assign(_kline_rank_score=score).sort_values("_kline_rank_score", ascending=False, kind="mergesort")
    elif "selection_score" in source.columns:
        score = pd.to_numeric(source["selection_score"], errors="coerce")
        source = source.assign(_kline_rank_score=score).sort_values("_kline_rank_score", ascending=False, kind="mergesort")
    elif "candidate_rank" in source.columns:
        rank = pd.to_numeric(source["candidate_rank"], errors="coerce")
        source = source.assign(_kline_rank_score=rank).sort_values("_kline_rank_score", ascending=True, kind="mergesort")
    tickers: list[str] = []
    for value in source["ticker"].tolist():
        text = str(value).strip()
        if text and text not in tickers:
            tickers.append(text)
        if len(tickers) >= max_kline_stocks:
            break
    return tickers


def _build_pipeline_histories(
    df: pd.DataFrame,
    existing_history: dict[str, pd.DataFrame],
    *,
    kline_enabled: bool,
    max_kline_stocks: int,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    histories = _copy_price_history_dict(existing_history)
    kline_attrs: dict[str, Any] = {
        "kline_enabled": bool(kline_enabled),
        "kline_max_stocks": int(max_kline_stocks),
        "kline_requested": 0,
        "kline_loaded": len(histories),
        "kline_cache_hits": 0,
        "kline_failures": 0,
        "kline_status": "Disabled" if not kline_enabled else "Not Requested",
        "kline_attempts": [],
    }
    if not kline_enabled:
        return histories, kline_attrs

    tickers = _select_kline_tickers(df, max_kline_stocks)
    missing = [ticker for ticker in tickers if ticker not in histories]
    kline_attrs["kline_requested"] = len(tickers)
    if missing:
        loaded = build_price_history_dict(missing, max_stocks=max_kline_stocks)
        loaded_attrs = loaded.get("_attrs", {}) if isinstance(loaded, dict) else {}
        for ticker, frame in loaded.items():
            if ticker == "_attrs":
                continue
            histories[str(ticker)] = _copy_frame(frame)
        kline_attrs.update(
            {
                "kline_loaded": len(histories),
                "kline_cache_hits": int(loaded_attrs.get("cache_hits", 0)),
                "kline_failures": int(loaded_attrs.get("failures", 0)),
                "kline_attempts": list(loaded_attrs.get("attempts", [])),
            }
        )
    kline_attrs["kline_status"] = "Available" if histories else "Unavailable"
    return histories, kline_attrs


def _finalize(
    df: pd.DataFrame,
    *,
    is_demo: bool,
    source: str,
    message: str | None = None,
    source_attrs: dict[str, Any] | None = None,
) -> pd.DataFrame:
    result = _ensure_live_fields(df)
    if source_attrs:
        result.attrs.update(source_attrs)
    result.attrs["is_demo"] = bool(is_demo)
    result.attrs["data_source"] = source
    result.attrs.setdefault("data_status", "Fallback" if is_demo else "Live")
    result.attrs["data_notice"] = message or (DEMO_NOTICE if is_demo else "Live pipeline result generated from available local/data-source inputs.")
    result.attrs.setdefault("universe_size", len(result))
    result.attrs.setdefault("final_count", len(result))
    return result


def _run_pipeline(
    universe: pd.DataFrame,
    fundamental_df: pd.DataFrame | None,
    price_history_dict: dict[str, pd.DataFrame] | None,
    *,
    kline_enabled: bool = True,
    max_kline_stocks: int = 200,
    fundamental_enabled: bool = True,
) -> pd.DataFrame:
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
    with_factors = _attach_factor_fields(explainable_selection)
    enriched_history, kline_attrs = _build_pipeline_histories(
        with_factors,
        history,
        kline_enabled=kline_enabled,
        max_kline_stocks=max_kline_stocks,
    )
    with_real_technical = build_real_technical_indicators(with_factors, price_history_dict=enriched_history)
    loaded_fundamentals = (
        build_fundamental_dataset(
            with_real_technical,
            tickers=with_real_technical["ticker"].astype(str).tolist() if "ticker" in with_real_technical.columns else None,
            use_external=True,
        )
        if fundamental_enabled
        else build_fundamental_dataset(with_real_technical, use_external=False)
    )
    if fundamental_df is not None and not fundamental_df.empty:
        source_attrs = dict(getattr(loaded_fundamentals, "attrs", {}))
        loaded_fundamentals = pd.concat([fundamental_df, loaded_fundamentals], ignore_index=True)
        loaded_fundamentals.attrs.update(source_attrs)
    with_fundamental_research = build_fundamental_research(with_real_technical, fundamental_df=loaded_fundamentals)
    result = activate_research_scores(with_fundamental_research)
    result.attrs.update(kline_attrs)
    result.attrs["fundamental_enabled"] = bool(fundamental_enabled)
    result.attrs["fundamental_data_source"] = loaded_fundamentals.attrs.get("fundamental_data_source", "Unavailable")
    result.attrs["fundamental_data_status"] = loaded_fundamentals.attrs.get("fundamental_data_status", "Unavailable")
    result.attrs["fundamental_rows"] = int(loaded_fundamentals.attrs.get("fundamental_rows", len(loaded_fundamentals)))
    result.attrs["fundamental_source_attempts"] = list(loaded_fundamentals.attrs.get("fundamental_source_attempts", []))
    return result


def _build_demo_result(max_stocks: int | None = None) -> pd.DataFrame:
    universe = _build_demo_universe(max_stocks=max_stocks)
    fundamentals = _build_demo_fundamentals(universe)
    histories = _build_demo_price_history(universe)
    result = _run_pipeline(universe, fundamentals, histories, kline_enabled=False, max_kline_stocks=max_stocks or 200, fundamental_enabled=False)
    return _finalize(result, is_demo=True, source="Built-in demo", message=DEMO_NOTICE, source_attrs=universe.attrs)


def run_live_pipeline(
    max_stocks: int | None = None,
    use_sample_if_no_data: bool = True,
    price_history_dict: dict[str, pd.DataFrame] | None = None,
    kline_enabled: bool = True,
    max_kline_stocks: int = 200,
    fundamental_enabled: bool = True,
) -> pd.DataFrame:
    """Run the full read-only research pipeline for the Streamlit web app.

    The runner does not mutate caller inputs and falls back to a built-in demo
    research DataFrame when the live Universe/data chain is unavailable.
    """
    histories = _copy_price_history_dict(price_history_dict)
    try:
        universe = load_a_share_universe()
        universe = _copy_frame(universe)
        if max_stocks and not universe.empty:
            universe = universe.head(int(max_stocks)).copy(deep=True)
        source_attrs = dict(universe.attrs)
        if universe.empty:
            raise ValueError("A-share Universe is empty.")
        if source_attrs.get("data_status") not in {"Live", "Cache"} or len(universe) <= 1000:
            demo = _build_demo_result(max_stocks=max_stocks)
            demo.attrs["last_error"] = source_attrs.get("last_error", "Real A-share source unavailable or too small.")
            return demo
        universe["status"] = "Available"
        universe["universe_status"] = "Available"
        universe["universe_total_count"] = universe.attrs.get("raw_count", len(universe))
        universe["universe_filtered_count"] = universe.attrs.get("final_count", len(universe))
        universe["universe_summary"] = (
            f"数据源：{universe.attrs.get('data_source', 'Unknown')}；"
            f"原始股票：{universe.attrs.get('raw_count', len(universe))}；"
            f"过滤后：{len(universe)}。"
        )
        result = _run_pipeline(
            universe,
            fundamental_df=None,
            price_history_dict=histories,
            kline_enabled=kline_enabled,
            max_kline_stocks=max_kline_stocks,
            fundamental_enabled=fundamental_enabled,
        )
        if result.empty:
            raise ValueError("Pipeline returned an empty result.")
        return _finalize(result, is_demo=False, source=source_attrs.get("data_source", "A-share Universe"), source_attrs=source_attrs)
    except Exception as exc:
        if not use_sample_if_no_data:
            return _finalize(pd.DataFrame(), is_demo=False, source="Unavailable", message=f"Live pipeline failed: {exc}")
        return _build_demo_result(max_stocks=max_stocks)
