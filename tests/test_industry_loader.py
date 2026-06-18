import pandas as pd

from data import industry_loader as loader
from industry.industry_engine import build_industry_research


def test_industry_empty_data_does_not_crash():
    result = loader.build_industry_dataset(pd.DataFrame(), use_external=False)

    assert isinstance(result, pd.DataFrame)
    for field in loader.INDUSTRY_COLUMNS:
        assert field in result.columns


def test_industry_existing_fields_are_standardized():
    source = pd.DataFrame([{"ticker": "600000", "name": "Sample", "industry": "Bank", "concepts": "Finance,Index"}])

    result = loader.build_industry_dataset(source, use_external=False)

    assert len(result) == 1
    assert result.loc[0, "industry"] == "Bank"
    assert result.loc[0, "concept_heat_score"] >= 50


def test_industry_research_score_and_reason_from_existing_fields():
    source = pd.DataFrame(
        [
            {"ticker": "600000", "industry": "Defense", "concepts": "AI,算力,军工", "industry_strength_score": 80, "concept_heat_score": 75},
            {"ticker": "600001", "industry": "Neutral", "concepts": "", "industry_strength_score": 50, "concept_heat_score": 50},
        ]
    )

    result = build_industry_research(source)

    assert result.loc[0, "industry_score"] > result.loc[1, "industry_score"]
    assert result.loc[0, "concept_coverage_count"] == 3
    assert result.loc[0, "industry_reason"]
