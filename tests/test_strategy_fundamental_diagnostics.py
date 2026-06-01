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
    assert "fundamental_detail_view" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_key_evidence" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_uncertainty_notes" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_confidence_level" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_confidence_score" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_anomaly_flags" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_research_conclusion" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_research_level" in FUNDAMENTAL_DIAGNOSTIC_FIELDS
    assert "fundamental_summary_tags" in FUNDAMENTAL_DIAGNOSTIC_FIELDS


def test_missing_fundamental_fields_safe_return():
    result = build_fundamental_diagnostics_profile(pd.DataFrame([{"symbol": "MISSING"}]))
    row = result.iloc[0]

    assert row["profitability_diagnostics"]["level"] == "insufficient_data"
    assert row["growth_diagnostics"]["level"] == "insufficient_growth_data"
    assert row["fundamental_detail_view"]["profile_type"] == "insufficient_data"
    assert row["fundamental_uncertainty_notes"]
    assert row["fundamental_confidence_level"] in {"low", "insufficient"}
    assert row["fundamental_industry_comparability_label"] == "no_industry_comparison"
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
    assert row["profitability_detail"]["score"] == 88
    assert row["profitability_detail"]["evidence"]
    assert any("盈利" in item for item in row["fundamental_strength_points"])
    assert "ROE" in row["profitability_diagnostics"]["explanation"]
    assert_no_forbidden_words(row.to_dict())


def test_high_growth_sample_generates_growth_explanation():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[0]

    assert row["growth_diagnostics"]["level"] == "high_growth"
    assert row["growth_detail"]["level"] == "high_growth"
    assert row["growth_detail"]["evidence"]
    assert any("成长" in item for item in row["fundamental_strength_points"])
    assert "成长" in row["growth_diagnostics"]["explanation"]


def test_expensive_valuation_sample_generates_valuation_pressure():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[1]

    assert row["valuation_diagnostics"]["level"] == "valuation_expensive"
    assert row["valuation_detail"]["level"] == "valuation_expensive"
    assert row["valuation_detail"]["risk_or_gap"]
    assert any("估值" in item for item in row["fundamental_weakness_points"])
    assert "估值" in row["valuation_diagnostics"]["explanation"]


def test_high_debt_or_negative_cashflow_generates_risk_explanation():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[2]

    assert row["financial_risk_diagnostics"]["level"] == "high_debt_pressure"
    assert row["financial_risk_detail"]["level"] == "high_debt_pressure"
    assert row["financial_risk_detail"]["risk_or_gap"]
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


def test_quality_growth_profile_type_for_high_profitability_and_growth():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[0]

    assert row["fundamental_profile_type"] == "quality_growth"
    assert row["fundamental_detail_view"]["profile_type"] == "quality_growth"
    assert 3 <= len(row["fundamental_key_evidence"]) <= 5
    assert row["fundamental_confidence_level"] in {"high", "medium"}
    assert row["fundamental_data_completeness_score"] >= 70
    assert row["fundamental_research_level"] in {"strong_candidate", "worth_tracking"}
    assert row["fundamental_core_strength"]
    assert row["fundamental_followup_focus"]
    assert row["fundamental_summary_tags"]
    assert row["industry_relative_detail"]["industry_relative_quality_label"] == "industry_relative_strong"
    assert row["relative_advantage_points"]
    assert row["fundamental_research_questions"]
    assert_no_forbidden_words(row.to_dict())


def test_high_growth_high_valuation_profile_type_and_conflict():
    frame = pd.DataFrame(
        [
            {
                "symbol": "GROWTH_EXPENSIVE",
                "roe": 0.14,
                "gross_margin": "36%",
                "net_profit": 50_000_000,
                "operating_cashflow": 45_000_000,
                "revenue_growth": "35%",
                "profit_growth": "40%",
                "pe": 92,
                "pb": 10,
                "debt_ratio": "45%",
                "profitability_score": 72,
                "growth_score": 88,
                "valuation_score": 28,
                "financial_risk_score": 70,
                "fundamental_quality_score": 66,
                "fundamental_data_quality_label": "sufficient_fundamental_data",
                "relative_valuation_label": "relatively_expensive",
                "industry_relative_quality_label": "industry_relative_neutral",
            }
        ]
    )

    row = build_fundamental_diagnostics_profile(frame).iloc[0]

    assert row["fundamental_profile_type"] == "high_growth_high_valuation"
    assert "high_growth_high_valuation" in row["fundamental_conflict_flags"]
    assert any("估值" in question for question in row["fundamental_research_questions"])
    assert_no_forbidden_words(row.to_dict())


def test_high_profit_negative_cashflow_identifies_cashflow_risk_or_conflict():
    frame = pd.DataFrame(
        [
            {
                "symbol": "CASHFLOW",
                "roe": 0.16,
                "gross_margin": "34%",
                "net_profit": 60_000_000,
                "operating_cashflow": -15_000_000,
                "revenue_growth": "8%",
                "profit_growth": "9%",
                "pe": 22,
                "debt_ratio": "50%",
                "profitability_score": 78,
                "growth_score": 58,
                "valuation_score": 62,
                "financial_risk_score": 38,
                "fundamental_quality_score": 58,
                "fundamental_data_quality_label": "sufficient_fundamental_data",
            }
        ]
    )

    row = build_fundamental_diagnostics_profile(frame).iloc[0]

    assert row["fundamental_profile_type"] == "cashflow_risk"
    assert "high_profit_negative_cashflow" in row["fundamental_conflict_flags"]
    assert "negative_cashflow" in row["fundamental_anomaly_flags"]
    assert_no_forbidden_words(row.to_dict())


def test_high_roe_high_debt_identifies_leverage_pressure_or_conflict():
    frame = pd.DataFrame(
        [
            {
                "symbol": "LEVERAGE",
                "roe": 0.22,
                "gross_margin": "30%",
                "net_profit": 40_000_000,
                "operating_cashflow": 30_000_000,
                "debt_ratio": "82%",
                "revenue_growth": "6%",
                "profit_growth": "5%",
                "profitability_score": 75,
                "growth_score": 55,
                "valuation_score": 58,
                "financial_risk_score": 32,
                "fundamental_quality_score": 55,
                "fundamental_data_quality_label": "sufficient_fundamental_data",
            }
        ]
    )

    row = build_fundamental_diagnostics_profile(frame).iloc[0]

    assert row["fundamental_profile_type"] == "leverage_pressure"
    assert "high_roe_high_debt" in row["fundamental_conflict_flags"]
    assert "high_debt" in row["fundamental_anomaly_flags"]
    assert_no_forbidden_words(row.to_dict())


def test_low_valuation_weak_growth_identifies_value_trap_risk():
    frame = pd.DataFrame(
        [
            {
                "symbol": "LOW_VALUE_WEAK_GROWTH",
                "roe": 0.08,
                "gross_margin": "18%",
                "net_profit": 10_000_000,
                "operating_cashflow": 12_000_000,
                "revenue_growth": "-3%",
                "profit_growth": "-8%",
                "pe": 8,
                "pb": 0.9,
                "profitability_score": 48,
                "growth_score": 25,
                "valuation_score": 76,
                "financial_risk_score": 60,
                "fundamental_quality_score": 45,
                "fundamental_data_quality_label": "sufficient_fundamental_data",
                "relative_valuation_label": "relatively_cheap_but_needs_check",
            }
        ]
    )

    row = build_fundamental_diagnostics_profile(frame).iloc[0]

    assert "low_valuation_weak_growth" in row["fundamental_conflict_flags"]
    assert row["valuation_diagnostics"]["level"] == "valuation_low_but_needs_quality_check"
    assert_no_forbidden_words(row.to_dict())


def test_insufficient_industry_relative_detail_safe_return():
    row = build_fundamental_diagnostics_profile(pd.DataFrame([{"symbol": "NO_INDUSTRY"}])).iloc[0]

    assert row["industry_relative_detail"]["summary"]
    assert row["industry_relative_detail"]["advantages"] == []
    assert row["industry_relative_detail"]["disadvantages"] == []
    assert row["fundamental_uncertainty_notes"]
    assert "insufficient_data_for_conflict_check" in row["fundamental_conflict_flags"]
    assert row["fundamental_industry_comparability_label"] == "no_industry_comparison"
    assert_no_forbidden_words(row.to_dict())


def test_detail_view_contains_all_detail_blocks_and_uncertainty_notes():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[1]

    detail_view = row["fundamental_detail_view"]

    assert detail_view["profitability"] == row["profitability_detail"]
    assert detail_view["growth"] == row["growth_detail"]
    assert detail_view["valuation"] == row["valuation_detail"]
    assert detail_view["financial_risk"] == row["financial_risk_detail"]
    assert detail_view["key_evidence"] == row["fundamental_key_evidence"]
    assert detail_view["uncertainty_notes"] == row["fundamental_uncertainty_notes"]
    assert_no_forbidden_words(detail_view)


def test_key_evidence_and_uncertainty_notes_are_safe_for_risk_sample():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[2]

    assert row["fundamental_key_evidence"]
    assert row["fundamental_uncertainty_notes"]
    assert any("现金流" in item or "负债" in item or "矛盾" in item for item in row["fundamental_uncertainty_notes"])
    assert "abnormal_valuation" in row["fundamental_anomaly_flags"]
    assert "negative_cashflow" in row["fundamental_anomaly_flags"]
    assert_no_forbidden_words(row.to_dict())


def test_confidence_score_is_bounded_and_reasons_are_available():
    result = build_fundamental_diagnostics_profile(make_diagnostic_frame())

    for _, row in result.iterrows():
        assert 0 <= row["fundamental_confidence_score"] <= 100
        assert row["fundamental_confidence_level"] in {"high", "medium", "low", "insufficient"}
        assert row["fundamental_confidence_reasons"]
        assert row["fundamental_industry_comparability_label"] in {
            "sufficient_industry_comparison",
            "partial_industry_comparison",
            "insufficient_industry_comparison",
            "no_industry_comparison",
        }
    assert_no_forbidden_words(result.to_dict())


def test_field_sparse_sample_has_low_or_insufficient_confidence():
    frame = pd.DataFrame(
        [
            {
                "symbol": "SPARSE",
                "net_profit": -100,
                "fundamental_data_quality_label": "insufficient_fundamental_data",
            }
        ]
    )

    row = build_fundamental_diagnostics_profile(frame).iloc[0]

    assert row["fundamental_confidence_level"] in {"low", "insufficient"}
    assert row["fundamental_data_completeness_score"] < 35
    assert "insufficient_data" in row["fundamental_anomaly_flags"]
    assert_no_forbidden_words(row.to_dict())


def test_research_conclusion_for_quality_growth_sample():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[0]

    assert row["fundamental_research_level"] in {"strong_candidate", "worth_tracking"}
    assert row["fundamental_core_strength"]
    assert row["fundamental_followup_focus"]
    assert row["fundamental_summary_tags"]
    assert row["fundamental_research_conclusion"]
    assert_no_forbidden_words(row.to_dict())


def test_research_conclusion_for_high_growth_high_valuation_conflict():
    frame = pd.DataFrame(
        [
            {
                "symbol": "MIXED",
                "roe": 0.14,
                "gross_margin": "36%",
                "net_profit": 50_000_000,
                "operating_cashflow": 45_000_000,
                "revenue_growth": "35%",
                "profit_growth": "40%",
                "pe": 92,
                "pb": 10,
                "profitability_score": 72,
                "growth_score": 88,
                "valuation_score": 28,
                "financial_risk_score": 70,
                "fundamental_quality_score": 66,
                "fundamental_grade": "B",
                "fundamental_data_quality_label": "sufficient_fundamental_data",
                "relative_valuation_label": "relatively_expensive",
                "industry_relative_quality_label": "industry_relative_neutral",
            }
        ]
    )

    row = build_fundamental_diagnostics_profile(frame).iloc[0]

    assert row["fundamental_research_level"] == "mixed_needs_review"
    assert row["fundamental_core_risk"]
    assert row["fundamental_followup_focus"]
    assert row["fundamental_summary_tags"]
    assert_no_forbidden_words(row.to_dict())


def test_research_conclusion_for_weak_or_risky_sample():
    row = build_fundamental_diagnostics_profile(make_diagnostic_frame()).iloc[2]

    assert row["fundamental_research_level"] == "weak_or_risky"
    assert row["fundamental_core_risk"]
    assert row["fundamental_followup_focus"]
    assert row["fundamental_research_conclusion"]
    assert_no_forbidden_words(row.to_dict())


def test_research_conclusion_for_insufficient_data_sample():
    row = build_fundamental_diagnostics_profile(pd.DataFrame([{"symbol": "EMPTY"}])).iloc[0]

    assert row["fundamental_research_level"] == "insufficient_data"
    assert row["fundamental_core_risk"]
    assert row["fundamental_followup_focus"]
    assert "数据可信度不足" in row["fundamental_summary_tags"]
    assert_no_forbidden_words(row.to_dict())
