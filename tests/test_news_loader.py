import pandas as pd

from data import news_loader as loader


def test_news_empty_data_does_not_crash():
    result = loader.build_news_dataset(pd.DataFrame(), use_external=False)

    assert isinstance(result, pd.DataFrame)
    for field in loader.NEWS_COLUMNS:
        assert field in result.columns


def test_news_keyword_classification():
    keywords = loader.classify_news_keywords("公司公告回购并披露AI算力进展")

    assert "回购" in keywords
    assert "AI" in keywords
    assert "算力" in keywords


def test_news_sentiment_label_and_score():
    positive = loader.infer_news_sentiment(["业绩预增"])
    negative = loader.infer_news_sentiment(["监管处罚"])
    neutral = loader.infer_news_sentiment(["半导体"])

    assert positive == "Positive"
    assert negative == "Negative"
    assert neutral == "Neutral"
    assert 70 <= loader.news_event_score(positive) <= 90
    assert 10 <= loader.news_event_score(negative) <= 40
    assert loader.news_event_score("Unknown") == 50


def test_news_existing_rows_are_standardized():
    source = pd.DataFrame([{"ticker": "600000", "name": "Sample", "news_title": "公司业绩预增公告"}])

    result = loader.build_news_dataset(source, use_external=False)

    assert len(result) == 1
    assert result.loc[0, "news_sentiment_label"] == "Positive"
    assert result.loc[0, "news_event_score"] == 80
