import copy
import importlib

import pandas as pd

from strategy.fundamental_diagnostics import (
    FUNDAMENTAL_DIAGNOSTIC_FIELDS,
    build_fundamental_diagnostics_profile,
)


FORBIDDEN_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
    "\u63a8\u8350\u4e70\u5165",
    "\u76ee\u6807\u4ef7",
    "\u77ed\u7ebf\u4ecb\u5165",
    "\u6284\u5e95",
    "\u6b62\u76c8",
    "\u6b62\u635f",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_WORDS:
        assert word not in text


def make_diagnostic_frame():
    return pd.DataFrame(
        [
            {
                "symbol": "QUALITY",
                "roe": 0.18,
                "gross_margin": "38%",
                "net_profit": 80_000_000,
                "operating_cashflow": 90_000_000,
                "revenue_growth": "18%",
                "profit_growth": "24%",
                "pe": 24,
                "pb": 2.2,
                "ps": 4,
                "debt_ratio": "42%",
                "profitability_score": 88,
                "growth_score": 91,
                "valuation_score": 68,
                "financial_risk_score": 82,
                "fundamental_quality_score": 82,
                "fundamental_grade": "A",
                "fundamental_style": "quality_growth",
                "fundamental_risk_level": "low",
                "fundamental_data_quality_label": "sufficient_fundamental_data",
                "relative_profitability_label": "industry_leading",
                "relative_growth_label": "high_relative_growth",
                "relative_valuation_label": "relatively_reasonable",
                "relative_financial_risk_label": "lower_than_industry_risk",
                "industry_relative_quality_label": "industry_relative_strong",
                "industry_relative_summary": "peer summary",
            },
            {
                "symbol": "EXPENSIVE",
                "roe": 0.10,
                "gross_margin": "25%",
                "net_profit": 20_000_000,
                "operating_cashflow": 12_000_000,
                "revenue_growth": "5%",
                "profit_growth": "6%",
                "pe": 86,
                "pb": 9,
                "ps": 18,
                "debt_ratio": "58%",
                "profitability_score": 58,
                "growth_score": 55,
                "valuation_score": 30,
                "financial_risk_score": 56,
                "fundamental_quality_score": 50,
                "fundamental_grade": "C",
                "fundamental_style": "stable_quality",
                "fundamental_risk_level": "medium",
                "fundamental_data_quality_label": "sufficient_fundamental_data",
                "relative_profitability_label": "around_industry_average",
                "relative_growth_label": "moderate_relative_growth",
                "relative_valuation_label": "relatively_expensive",
                "relative_financial_risk_label": "normal_industry_risk",
                "industry_relative_quality_label": "industry_relative_neutral",
            },
            {
                "symbol": "RISK",
                "roe": -0.04,
                "gross_margin": "8%",
                "net_profit": -10_000_000,
                "operating_cashflow": -20_000_000,
                "revenue_growth": "-8%",
                "profit_growth": "-18%",
                "pe": -5,
                "pb": 7,
                "ps": 12,
                "debt_ratio": "86%",
                "profitability_score": 20,
                "growth_score": 15,
                "valuation_score": 20,
                "financial_risk_score": 18,
                "fundamental_quality_score": 22,
                "fundamental_grade": "D",
                "fundamental_style": "weak_fundamental",
                "fundamental_risk_level": "high",
                "fundamental_data_quality_label": "sufficient_fundamental_data",
                "relative_profitability_label": "below_industry_average",
                "relative_growth_label": "negative_relative_growth",
                "relative_valuation_label": "abnormal_valuation_data",
                "relative_financial_risk_label": "higher_than_industry_risk",
                "industry_relative_quality_label": "industry_relative_weak",
            },
        ]
    )


def test_fundamental_diagnostics_module_imports():
    assert importlib.import_module("strategy.fundamental_diagnostics")


def test_empty_input_safe_return():
    result = build_fundamental_diagnostics_profile(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == FUNDAMENTAL_DIAGNOSTIC_FIELDS


def test_missing_fundamental_fields_safe_return():
    result = build_fundamental_diagnostics_profile(pd.DataFrame([{"symbol": "MISSING"}]))
    row = result.iloc[0]

    assert row["profitability_diagnostics"]["level"] == "insufficient_data"
    assert row["growth_diagnostics"]["level"] == "insufficient_growth_data"
    assert "fundamental_data_insufficient" in row["fundamental_diagnostics"]["warnings"]
    assert_no_forbidden_words(row.to_dict())


def test_missing_industry_relative_fields_safe_return():
    frame = pd.DataFrame(
        [
            {
                "symbol": "NO_REL",
                "roe": 0.15,
                "gross_margin": "32%",
                "net_profit": 1_000,
                "profitability_score": 75,
                "fundamental_data_quality_label": "partial_fundamental_data",
            }
        ]
    )

    result = build_fundamental_diagnostics_profile(frame)

    assert len(result) == 1
    assert result.iloc[0]["fundamental_diagnostics"]["industry_relative"]["industry_relative_quality_label"] is None
    assert_no_forbidden_words(result.to_dict())


def test_high_profitability_sample_generates_strength_explanation():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[0]

    assert row["profitability_diagnostics"]["level"] == "high_profitability"
    assert any("盈利" in item for item in row["fundamental_strength_points"])
    assert "ROE" in row["profitability_diagnostics"]["explanation"]
    assert_no_forbidden_words(row.to_dict())


def test_high_growth_sample_generates_growth_explanation():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[0]

    assert row["growth_diagnostics"]["level"] == "high_growth"
    assert any("成长" in item for item in row["fundamental_strength_points"])
    assert "成长" in row["growth_diagnostics"]["explanation"]


def test_expensive_valuation_sample_generates_valuation_pressure():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[1]

    assert row["valuation_diagnostics"]["level"] == "valuation_expensive"
    assert any("估值" in item for item in row["fundamental_weakness_points"])
    assert "估值" in row["valuation_diagnostics"]["explanation"]


def test_high_debt_or_negative_cashflow_generates_risk_explanation():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[2]

    assert row["financial_risk_diagnostics"]["level"] == "high_debt_pressure"
    assert any("风险" in item for item in row["fundamental_weakness_points"])
    assert "负债" in row["financial_risk_diagnostics"]["explanation"]


def test_strong_industry_relative_sample_generates_industry_strength():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[0]

    assert "行业内相对质量较好" in row["fundamental_strength_points"]
    assert row["fundamental_diagnostics"]["industry_relative"]["industry_relative_quality_label"] == "industry_relative_strong"


def test_point_lists_are_limited_to_three_items():
    result = build_fundamental_diagnostics_profile(make_diagnostic_frame())

    for _, row in result.iterrows():
        assert len(row["fundamental_strength_points"]) <= 3
        assert len(row["fundamental_weakness_points"]) <= 3
        assert len(row["fundamental_watch_points"]) <= 3


def test_input_dataframe_not_modified_and_output_order_preserved():
    frame = make_diagnostic_frame()
    before = copy.deepcopy(frame)

    result = build_fundamental_diagnostics_profile(frame)

    pd.testing.assert_frame_equal(frame, before)
    assert list(frame["symbol"]) == ["QUALITY", "EXPENSIVE", "RISK"]
    assert list(result.index) == [0, 1, 2]
    assert_no_forbidden_words(result.to_dict())
