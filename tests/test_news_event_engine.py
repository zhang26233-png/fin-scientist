import importlib

import pandas as pd

from news.event_engine import NEWS_EVENT_FIELDS, build_news_event_scores, classify_news_event


def test_news_event_engine_importable():
    assert importlib.import_module("news.event_engine")


def test_empty_dataframe_safe_return():
    result = build_news_event_scores(pd.DataFrame())

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == NEWS_EVENT_FIELDS


def test_input_object_not_mutated():
    source = pd.DataFrame([{"ticker": "600000", "news_title": "公司回购公告"}])
    original = source.copy(deep=True)

    build_news_event_scores(source)

    pd.testing.assert_frame_equal(source, original)


def test_positive_keyword_classification():
    result = classify_news_event("公司业绩预增并签订重大合同")

    assert result["news_sentiment_label"] == "Positive"
    assert "业绩预增" in result["news_keywords"]
    assert "重大合同" in result["news_keywords"]


def test_negative_keyword_classification():
    result = classify_news_event("公司收到监管处罚并提示退市风险")

    assert result["news_sentiment_label"] == "Negative"
    assert "监管处罚" in result["news_keywords"]
    assert "退市风险" in result["news_keywords"]


def test_neutral_news_classification():
    result = classify_news_event("公司发布调研会议公告")

    assert result["news_sentiment_label"] == "Neutral"
    assert result["news_type"] in {"公告", "调研", "会议"}


def test_scores_are_0_to_100():
    source = pd.DataFrame(
        [
            {"ticker": "600000", "news_title": "AI算力订单增长", "news_time": "2026-06-16"},
            {"ticker": "600001", "news_title": "公司被立案调查", "news_time": "2026-06-16"},
        ]
    )

    result = build_news_event_scores(source)

    assert result["news_event_score"].between(0, 100).all()
    assert result["news_heat_score"].between(0, 100).all()
    assert result["news_risk_score"].between(0, 100).all()


def test_negative_event_generates_warning():
    source = pd.DataFrame([{"ticker": "600000", "news_title": "公司发生债务违约并收到问询函"}])

    result = build_news_event_scores(source)

    assert "负面新闻风险" in result.loc[0, "news_warning"]


def test_hot_industry_keyword_increases_heat_score():
    base = build_news_event_scores(pd.DataFrame([{"ticker": "600000", "news_title": "公司公告"}]))
    hot = build_news_event_scores(pd.DataFrame([{"ticker": "600000", "news_title": "AI算力数据中心进展"}]))

    assert hot.loc[0, "news_heat_score"] > base.loc[0, "news_heat_score"]


def test_no_news_uses_neutral_score():
    source = pd.DataFrame([{"ticker": "600000", "name": "Sample"}])

    result = build_news_event_scores(source)

    assert result.loc[0, "news_event_score"] == 50
    assert result.loc[0, "news_heat_score"] == 50
    assert result.loc[0, "news_risk_score"] == 50


def test_output_order_is_stable():
    source = pd.DataFrame(
        [
            {"ticker": "600002", "news_title": "公司公告"},
            {"ticker": "600001", "news_title": "公司回购公告"},
        ]
    )

    result = build_news_event_scores(source)

    assert result["ticker"].tolist() == ["600002", "600001"]


def test_v710_positive_event_weights_lift_news_score():
    neutral = build_news_event_scores(pd.DataFrame([{"ticker": "600000", "news_title": "公司公告"}]))
    positive = build_news_event_scores(pd.DataFrame([{"ticker": "600000", "news_title": "AI算力订单中标"}]))

    assert positive.loc[0, "news_event_score"] > neutral.loc[0, "news_event_score"]
    assert positive.loc[0, "news_reason"]


def test_v710_negative_event_weights_reduce_news_score():
    negative = build_news_event_scores(pd.DataFrame([{"ticker": "600000", "news_title": "公司减持处罚退市风险提示"}]))

    assert negative.loc[0, "news_event_score"] < 50
    assert negative.loc[0, "news_reason"]
