import pandas as pd

from research.unified_ranking_engine import UNIFIED_RESEARCH_FIELDS, build_unified_research_score


def test_unified_research_score_formula_and_contributions():
    source = pd.DataFrame(
        [
            {
                "ticker": "600000",
                "real_technical_score": 80,
                "capital_flow_score": 70,
                "fundamental_research_score": 60,
                "industry_score": 90,
                "news_event_score": 50,
            }
        ]
    )

    result = build_unified_research_score(source)

    assert result.loc[0, "technical_contribution"] == 24
    assert result.loc[0, "capital_contribution"] == 17.5
    assert result.loc[0, "fundamental_contribution"] == 12
    assert result.loc[0, "industry_contribution"] == 13.5
    assert result.loc[0, "news_contribution"] == 5
    assert result.loc[0, "unified_research_score"] == 72


def test_missing_scores_use_neutral_50():
    result = build_unified_research_score(pd.DataFrame([{"ticker": "600000"}]))

    assert result.loc[0, "unified_research_score"] == 50
    for field in UNIFIED_RESEARCH_FIELDS:
        assert field in result.columns


def test_industry_score_can_fallback_from_existing_industry_fields():
    source = pd.DataFrame(
        [
            {
                "ticker": "600000",
                "real_technical_score": 50,
                "capital_flow_score": 50,
                "fundamental_research_score": 50,
                "industry_strength_score": 80,
                "concept_heat_score": 60,
                "news_event_score": 50,
            }
        ]
    )

    result = build_unified_research_score(source)

    assert result.loc[0, "industry_contribution"] == 11.1
    assert result.loc[0, "unified_research_score"] == 53.6


def test_input_dataframe_not_mutated():
    source = pd.DataFrame([{"ticker": "600000", "real_technical_score": 70}])
    original = source.copy(deep=True)

    build_unified_research_score(source)

    pd.testing.assert_frame_equal(source, original)


def test_empty_dataframe_safe_return():
    result = build_unified_research_score(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == UNIFIED_RESEARCH_FIELDS
