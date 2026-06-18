import pandas as pd

from audit.scheduler_bucket_audit import SCHEDULER_BUCKET_AUDIT_CACHE, audit_scheduler_buckets


def test_scheduler_bucket_audit_counts_final_buckets(tmp_path):
    path = tmp_path / "latest_research_result.csv"
    pd.DataFrame(
        {
            "ticker": ["core", "watch", "exclude"],
            "research_bucket": ["Core Research", "Watch Research", "Excluded / Low Priority"],
        }
    ).to_csv(path, index=False)

    result = audit_scheduler_buckets(path=path)

    assert result["core_count"] == 1
    assert result["watch_count"] == 1
    assert result["exclude_count"] == 1
    assert SCHEDULER_BUCKET_AUDIT_CACHE.exists()


def test_scheduler_bucket_audit_handles_missing_bucket(tmp_path):
    path = tmp_path / "latest_research_result.csv"
    pd.DataFrame({"ticker": ["000001"]}).to_csv(path, index=False)

    result = audit_scheduler_buckets(path=path)

    assert result["rows"] == 1
    assert result["core_count"] == 0
    assert result["watch_count"] == 0
    assert result["exclude_count"] == 0
