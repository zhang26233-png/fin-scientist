import pandas as pd

from pipeline.stage_selector import assign_final_buckets


def test_core_zero_triggers_relative_ranking_fallback_10_30_split():
    df = pd.DataFrame(
        {
            "ticker": [f"{i:06d}" for i in range(100)],
            "name": [f"Name {i}" for i in range(100)],
            "activated_composite_score": list(range(49, -51, -1)),
            "quote_quality_score": [80] * 100,
        }
    )

    result = assign_final_buckets(df, core_limit=20, watch_limit=50)

    assert int(result["research_bucket"].eq("Core Research").sum()) == 10
    assert int(result["research_bucket"].eq("Watch Research").sum()) == 20
    assert int(result["research_bucket"].eq("Excluded / Low Priority").sum()) == 70
    assert result["bucket_generation_reason"].eq("Relative Ranking Fallback").any()


def test_bucket_generation_reason_uses_absolute_threshold_when_core_exists():
    df = pd.DataFrame(
        {
            "ticker": ["core", "watch", "exclude"],
            "name": ["Core", "Watch", "Exclude"],
            "activated_composite_score": [80, 60, 40],
            "quote_quality_score": [80, 80, 80],
        }
    )

    result = assign_final_buckets(df, core_limit=1, watch_limit=1)

    assert result["bucket_generation_reason"].tolist() == ["Absolute Threshold", "Absolute Threshold", "Absolute Threshold"]
    assert result["research_score"].tolist() == result["activated_composite_score"].tolist()


def test_optional_layer_unavailable_does_not_exclude_valid_rows():
    df = pd.DataFrame(
        {
            "ticker": ["core", "watch"],
            "name": ["Core", "Watch"],
            "activated_composite_score": [80, 60],
            "quote_quality_score": [80, 80],
            "latest_price": [10, 11],
            "data_status": ["Cache", "Cache"],
            "fundamental_data_status": ["Unavailable", "Unavailable"],
            "capital_flow_status": ["Unavailable", "Unavailable"],
            "news_status": ["Unavailable", "Unavailable"],
        }
    )

    result = assign_final_buckets(df, core_limit=1, watch_limit=1)

    assert result["research_bucket"].tolist() == ["Core Research", "Watch Research"]
