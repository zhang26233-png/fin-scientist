import pandas as pd

from research.research_explainer import RESEARCH_EXPLAINER_FIELDS, build_research_explanation


def test_research_explanation_generates_summary_and_dimension_text():
    source = pd.DataFrame(
        [
            {
                "ticker": "600000",
                "unified_research_score": 68.6,
                "real_technical_score": 88,
                "capital_flow_score": 72,
                "fundamental_research_score": 63,
                "news_event_score": 55,
                "industry_score": 70,
                "technical_signal_summary": "突破60日均线",
                "capital_flow_summary": "主力净流入增强",
                "fundamental_reason": "ROE较高",
                "news_reason": "存在轻度利好新闻",
                "industry_reason": "行业热度提升",
            }
        ]
    )

    result = build_research_explanation(source)

    assert "Unified research score 68.60" in result.loc[0, "research_summary"]
    assert "突破60日均线" in result.loc[0, "technical_research_explanation"]
    assert "主力净流入增强" in result.loc[0, "capital_research_explanation"]
    assert "ROE较高" in result.loc[0, "fundamental_research_explanation"]
    assert "存在轻度利好新闻" in result.loc[0, "news_research_explanation"]
    assert "行业热度提升" in result.loc[0, "industry_research_explanation"]


def test_research_explanation_handles_missing_scores_with_neutral_defaults():
    result = build_research_explanation(pd.DataFrame([{"ticker": "600000"}]))

    assert "Unified research score 50.00" in result.loc[0, "research_summary"]
    for field in RESEARCH_EXPLAINER_FIELDS:
        assert field in result.columns
        assert result.loc[0, field]


def test_empty_dataframe_safe_return():
    result = build_research_explanation(pd.DataFrame())

    assert result.empty
    assert list(result.columns) == RESEARCH_EXPLAINER_FIELDS
