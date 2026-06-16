import pandas as pd

from data import industry_loader as loader


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
