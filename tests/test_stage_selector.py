import pandas as pd

from pipeline.stage_selector import (
    assign_final_buckets,
    select_stage1_candidates,
    select_stage2_candidates,
    select_stage3_candidates,
)


def test_stage1_filters_st_suspended_error_rows():
    df = pd.DataFrame(
        [
            {"ticker": "000001", "name": "Good", "latest_price": 10, "turnover": 100_000_000, "data_status": "Live"},
            {"ticker": "000002", "name": "ST Bad", "latest_price": 10, "turnover": 100_000_000, "data_status": "Live"},
            {"ticker": "000003", "name": "Stop", "latest_price": 10, "turnover": 100_000_000, "is_suspended": True},
            {"ticker": "000004", "name": "Error", "latest_price": 10, "turnover": 100_000_000, "data_status": "Error"},
        ]
    )

    result = select_stage1_candidates(df, limit=10)

    assert result["ticker"].tolist() == ["000001"]


def test_stage1_filters_chinese_status_rows():
    df = pd.DataFrame(
        [
            {"ticker": "000001", "name": "正常股份", "latest_price": 10, "turnover": 100_000_000, "data_status": "Live"},
            {"ticker": "000002", "name": "退市整理", "latest_price": 10, "turnover": 100_000_000, "data_status": "Live"},
            {"ticker": "000003", "name": "停牌股份", "latest_price": 10, "turnover": 100_000_000, "status": "停牌"},
            {"ticker": "000004", "name": "布尔股份", "latest_price": 10, "turnover": 100_000_000, "is_suspended": "是"},
        ]
    )

    result = select_stage1_candidates(df, limit=10)

    assert result["ticker"].tolist() == ["000001"]


def test_stage1_sorts_by_liquidity():
    df = pd.DataFrame(
        [
            {"ticker": "000001", "name": "A", "latest_price": 10, "turnover": 20_000_000, "turnover_rate": 1, "pct_change": 1},
            {"ticker": "000002", "name": "B", "latest_price": 10, "turnover": 200_000_000, "turnover_rate": 3, "pct_change": 1},
        ]
    )

    result = select_stage1_candidates(df, limit=2)

    assert result["ticker"].tolist()[0] == "000002"


def test_stage2_sorts_by_technical_score():
    df = pd.DataFrame({"ticker": ["a", "b"], "real_technical_score": [60, 90]})

    result = select_stage2_candidates(df, limit=2)

    assert result["ticker"].tolist() == ["b", "a"]


def test_stage3_sorts_by_research_scores():
    df = pd.DataFrame(
        {
            "ticker": ["a", "b"],
            "fundamental_research_score": [55, 80],
            "capital_flow_score": [55, 80],
            "real_technical_score": [55, 80],
            "liquidity_score": [55, 80],
        }
    )

    result = select_stage3_candidates(df, limit=2)

    assert result["ticker"].tolist() == ["b", "a"]


def test_assign_final_buckets_generates_core_watch_exclude():
    df = pd.DataFrame(
        {
            "ticker": ["core", "watch", "exclude"],
            "activated_composite_score": [80, 60, 40],
            "quote_quality_score": [80, 80, 80],
        }
    )

    result = assign_final_buckets(df, core_limit=1, watch_limit=1)

    assert result["research_bucket"].tolist() == ["Core Research", "Watch Research", "Excluded / Low Priority"]
    assert result["research_rank"].tolist() == [1, 2, 3]


def test_output_order_is_stable_for_equal_scores():
    df = pd.DataFrame({"ticker": ["a", "b", "c"], "real_technical_score": [70, 70, 70]})

    result = select_stage2_candidates(df, limit=3)

    assert result["ticker"].tolist() == ["a", "b", "c"]


def test_empty_dataframe_returns_safely():
    empty = pd.DataFrame()

    assert select_stage1_candidates(empty).empty
    assert select_stage2_candidates(empty).empty
    assert select_stage3_candidates(empty).empty
    assert assign_final_buckets(empty).empty
