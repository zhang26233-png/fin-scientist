import copy

import pandas as pd

from strategy.fundamental_relative import RELATIVE_FUNDAMENTAL_FIELDS, build_fundamental_relative_profile


FORBIDDEN_RELATIVE_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_RELATIVE_WORDS:
        assert word not in text


def make_relative_frame():
    return pd.DataFrame(
        [
            {
                "symbol": "LEAD1",
                "industry": "Tech",
                "roe": 0.22,
                "gross_margin": 0.48,
                "net_profit": 120_000_000,
                "operating_cashflow": 110_000_000,
                "revenue_growth": 0.28,
                "profit_growth": 0.35,
                "pe": 86,
                "pb": 9.2,
                "ps": 18,
                "debt_ratio": 0.35,
            },
            {
                "symbol": "MID1",
                "industry": "Tech",
                "roe": 0.12,
                "gross_margin": 0.30,
                "net_profit": 60_000_000,
                "operating_cashflow": 45_000_000,
                "revenue_growth": 0.08,
                "profit_growth": 0.05,
                "pe": 26,
                "pb": 3.2,
                "ps": 6,
                "debt_ratio": 0.50,
            },
            {
                "symbol": "RISK1",
                "industry": "Tech",
                "roe": -0.03,
                "gross_margin": 0.12,
                "net_profit": -10_000_000,
                "operating_cashflow": -25_000_000,
                "revenue_growth": -0.04,
                "profit_growth": -0.18,
                "pe": -6,
                "pb": 7.5,
                "ps": 10,
                "debt_ratio": 0.88,
            },
            {
                "symbol": "MED1",
                "industry": "Health",
                "roe": 0.18,
                "gross_margin": 0.42,
                "net_profit": 80_000_000,
                "operating_cashflow": 70_000_000,
                "revenue_growth": 0.12,
                "profit_growth": 0.11,
                "pe": 32,
                "pb": 4,
                "ps": 7,
                "debt_ratio": 0.42,
            },
            {
                "symbol": "MED2",
                "industry": "Health",
                "roe": 0.08,
                "gross_margin": 0.24,
                "net_profit": 35_000_000,
                "operating_cashflow": 20_000_000,
                "revenue_growth": 0.04,
                "profit_growth": 0.02,
                "pe": 24,
                "pb": 2.2,
                "ps": 4,
                "debt_ratio": 0.60,
            },
        ]
    )


def test_fundamental_relative_import_and_empty_input_safe_return():
    result = build_fundamental_relative_profile(pd.DataFrame())

    assert list(result.columns) == RELATIVE_FUNDAMENTAL_FIELDS
    assert result.empty


def test_fundamental_relative_missing_industry_safe_return():
    result = build_fundamental_relative_profile(pd.DataFrame([{"symbol": "A", "roe": 0.2}, {"symbol": "B", "roe": 0.1}]))

    assert len(result) == 2
    assert set(result["industry_relative_quality_label"]) == {"insufficient_industry_data"}
    assert_no_forbidden_words(result.to_dict())


def test_fundamental_relative_single_industry_sample_insufficient():
    result = build_fundamental_relative_profile(pd.DataFrame([{"symbol": "A", "industry": "Only", "roe": 0.2}]))

    assert len(result) == 1
    assert result.iloc[0]["industry_relative_quality_label"] == "insufficient_industry_data"
    assert_no_forbidden_words(result.to_dict())


def test_fundamental_relative_detects_strong_profitability_and_growth():
    frame = make_relative_frame()
    result = build_fundamental_relative_profile(frame)
    lead = result.iloc[0]

    assert lead["relative_profitability_label"] == "industry_leading"
    assert lead["relative_growth_label"] == "high_relative_growth"
    assert lead["industry_relative_quality_label"] == "industry_relative_strong"
    assert_no_forbidden_words(lead.to_dict())


def test_fundamental_relative_detects_expensive_valuation():
    result = build_fundamental_relative_profile(make_relative_frame())

    assert result.iloc[0]["relative_valuation_label"] == "relatively_expensive"


def test_fundamental_relative_detects_high_financial_risk():
    result = build_fundamental_relative_profile(make_relative_frame())
    risk_row = result.iloc[2]

    assert risk_row["relative_financial_risk_label"] == "higher_than_industry_risk"
    assert risk_row["industry_relative_quality_label"] == "industry_relative_weak"


def test_fundamental_relative_multi_industry_groups_do_not_interfere():
    result = build_fundamental_relative_profile(make_relative_frame())

    assert result.iloc[3]["relative_profitability_label"] in {"industry_leading", "above_industry_average"}
    assert result.iloc[4]["relative_profitability_label"] in {"below_industry_average", "around_industry_average"}


def test_fundamental_relative_preserves_order_and_does_not_modify_source():
    frame = make_relative_frame()
    before = copy.deepcopy(frame)

    result = build_fundamental_relative_profile(frame)

    assert list(frame["symbol"]) == ["LEAD1", "MID1", "RISK1", "MED1", "MED2"]
    assert len(result) == len(frame)
    pd.testing.assert_frame_equal(frame, before)
    assert_no_forbidden_words(result.to_dict())


def test_fundamental_relative_accepts_sector_alias():
    frame = pd.DataFrame(
        [
            {"symbol": "A", "sector": "S1", "roe": 0.2, "gross_margin": 0.4, "revenue_growth": 0.2, "profit_growth": 0.2},
            {"symbol": "B", "sector": "S1", "roe": 0.1, "gross_margin": 0.2, "revenue_growth": 0.05, "profit_growth": 0.03},
        ]
    )
    result = build_fundamental_relative_profile(frame)

    assert result.iloc[0]["industry_relative_quality_label"] != "insufficient_industry_data"
    assert_no_forbidden_words(result.to_dict())
