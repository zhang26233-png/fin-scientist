import importlib

import pandas as pd

from fundamental.fundamental_engine import build_fundamental_research


def _base_quotes() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"ticker": "600001", "name": "Alpha", "pe_ttm": 10, "pb": 1.5, "ps_ttm": 2},
            {"ticker": "600002", "name": "Beta", "pe_ttm": 80, "pb": 6, "ps_ttm": 10},
        ]
    )


def _full_fundamental() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": "600001",
                "pe_ttm": 10,
                "pb": 1.5,
                "ps_ttm": 2,
                "roe": 22,
                "roa": 9,
                "gross_margin": 45,
                "net_margin": 18,
                "revenue_growth_yoy": 35,
                "net_profit_growth_yoy": 12,
                "deducted_profit_growth_yoy": -1,
                "debt_to_asset": 35,
                "ocf_to_net_profit": 1.2,
                "dividend_yield": 3.5,
            }
        ]
    )


def test_empty_dataframe_safe_return():
    result = build_fundamental_research(pd.DataFrame())
    assert result.empty
    assert "fundamental_research_score" in result.columns


def test_input_object_not_mutated():
    source = _base_quotes()
    original = source.copy(deep=True)
    build_fundamental_research(source)
    pd.testing.assert_frame_equal(source, original)


def test_without_fundamental_df_graceful_degrade_from_existing_fields():
    result = build_fundamental_research(_base_quotes())
    assert "fundamental_available" in result.columns
    assert result.loc[0, "fundamental_available"] is True
    assert result.loc[0, "fundamental_research_score"] != 50
    assert "估值数据已接入" in result.loc[0, "fundamental_reason"]


def test_fundamental_df_merges_by_ticker():
    source = pd.DataFrame([{"ticker": "600001", "name": "Alpha"}])
    result = build_fundamental_research(source, fundamental_df=_full_fundamental())
    assert result.loc[0, "fundamental_available"] is True
    assert result.loc[0, "fundamental_data_source"] == "Provided Fundamental"
    assert result.loc[0, "roe"] == 22


def test_pe_pb_ps_valuation_score_correct():
    result = build_fundamental_research(_full_fundamental(), fundamental_df=_full_fundamental())
    assert result.loc[0, "valuation_score"] == 95


def test_profitability_score_correct():
    result = build_fundamental_research(_full_fundamental(), fundamental_df=_full_fundamental())
    assert result.loc[0, "profitability_score"] == 93.75


def test_growth_score_correct():
    result = build_fundamental_research(_full_fundamental(), fundamental_df=_full_fundamental())
    assert result.loc[0, "growth_score"] == 69


def test_high_debt_generates_risk():
    source = pd.DataFrame(
        [
            {
                "ticker": "600003",
                "pe_ttm": 20,
                "pb": 3,
                "roe": 8,
                "revenue_growth_yoy": 5,
                "net_profit_growth_yoy": 3,
                "debt_to_asset": 85,
                "ocf_to_net_profit": 0.8,
            }
        ]
    )
    result = build_fundamental_research(source)
    assert "资产负债率较高" in result.loc[0, "fundamental_risks"]


def test_weak_cashflow_generates_risk():
    source = pd.DataFrame(
        [
            {
                "ticker": "600004",
                "pe_ttm": 20,
                "pb": 3,
                "roe": 8,
                "revenue_growth_yoy": 5,
                "net_profit_growth_yoy": 3,
                "debt_to_asset": 50,
                "ocf_to_net_profit": -0.2,
            }
        ]
    )
    result = build_fundamental_research(source)
    assert "经营现金流质量偏弱" in result.loc[0, "fundamental_risks"]


def test_fundamental_research_score_in_0_to_100():
    result = build_fundamental_research(_full_fundamental(), fundamental_df=_full_fundamental())
    assert result["fundamental_research_score"].between(0, 100).all()


def test_unavailable_fundamental_uses_neutral_score():
    result = build_fundamental_research(pd.DataFrame([{"ticker": "600005", "name": "Missing"}]))
    assert result.loc[0, "fundamental_available"] is False
    assert result.loc[0, "fundamental_research_score"] == 50
    assert "基本面数据不可用，使用中性分" in result.loc[0, "fundamental_warnings"]


def test_real_field_calibrated_scores():
    frame = pd.DataFrame(
        [
            {
                "ticker": "600006",
                "pe_ttm": 45,
                "pb": 4,
                "roe": 16,
                "roa": 6,
                "revenue_growth_yoy": 22,
                "net_profit_growth_yoy": 35,
                "debt_to_asset": 55,
                "ocf_to_net_profit": 1.1,
            }
        ]
    )
    result = build_fundamental_research(frame)

    assert result.loc[0, "valuation_score"] == 45
    assert result.loc[0, "profitability_score"] == 78.75
    assert result.loc[0, "growth_score"] == 89
    assert result.loc[0, "financial_quality_score"] == 85


def test_output_order_preserved():
    source = pd.DataFrame([{"ticker": "600002"}, {"ticker": "600001"}, {"ticker": "600003"}])
    result = build_fundamental_research(source, fundamental_df=_full_fundamental())
    assert result["ticker"].tolist() == ["600002", "600001", "600003"]


def test_module_importable():
    module = importlib.import_module("fundamental.fundamental_engine")
    assert callable(module.build_fundamental_research)
