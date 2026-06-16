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
    assert neutral == "Positive"
    assert 70 <= loader.news_event_score(positive) <= 90
    assert 10 <= loader.news_event_score(negative) <= 40
    assert loader.news_event_score("Unknown") == 50


def test_news_existing_rows_are_standardized():
    source = pd.DataFrame([{"ticker": "600000", "name": "Sample", "news_title": "公司业绩预增公告"}])

    result = loader.build_news_dataset(source, use_external=False)

    assert len(result) == 1
    assert result.loc[0, "news_sentiment_label"] == "Positive"
    assert result.loc[0, "news_event_score"] == 80
    assert result.loc[0, "news_status"] == "Available"


def test_news_cache_read_write(tmp_path, monkeypatch):
    cache_file = tmp_path / "news_latest.csv"
    monkeypatch.setattr(loader, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(loader, "CACHE_FILE", cache_file)
    frame = pd.DataFrame(
        [
            {"ticker": f"600{i:03d}", "name": f"Sample {i}", "news_title": "公司回购公告"}
            for i in range(10)
        ]
    )
    standardized = loader.build_news_dataset(frame, use_external=False)

    meta = loader.save_cached_news(standardized)
    cached = loader.load_cached_news()

    assert meta["cache_status"] == "Available"
    assert len(cached) == 10
    assert cached.attrs["cache_status"] == "Available"
    assert list(cached.columns) == loader.NEWS_COLUMNS


def test_news_external_failure_falls_back_to_cache(tmp_path, monkeypatch):
    cache_file = tmp_path / "news_latest.csv"
    monkeypatch.setattr(loader, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(loader, "CACHE_FILE", cache_file)
    frame = pd.DataFrame(
        [
            {"ticker": f"600{i:03d}", "name": f"Sample {i}", "news_title": "公司公告"}
            for i in range(10)
        ]
    )
    loader.save_cached_news(loader.build_news_dataset(frame, use_external=False))
    monkeypatch.setattr(loader, "load_news_from_eastmoney", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr(loader, "load_news_from_sina", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr(loader, "load_news_from_akshare", lambda *args, **kwargs: pd.DataFrame())

    result = loader.build_news_dataset(pd.DataFrame(), use_external=True)

    assert len(result) == 10
    assert result.attrs["news_status"] == "Available"


def test_news_standard_fields_output():
    result = loader.build_news_dataset(
        pd.DataFrame([{"ticker": "600000", "name": "Sample", "news_title": "公司公告"}]),
        use_external=False,
    )

    assert list(result.columns) == loader.NEWS_COLUMNS
