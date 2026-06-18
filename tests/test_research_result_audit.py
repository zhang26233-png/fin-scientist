import pandas as pd

from audit.research_result_audit import RESEARCH_RESULT_AUDIT_CACHE, audit_research_result


def test_research_result_audit_reports_rows_fields_and_distribution(tmp_path):
    path = tmp_path / "latest_research_result.csv"
    df = pd.DataFrame(
        {
            "ticker": ["000001", "000002"],
            "name": ["A", "B"],
            "activated_composite_score": [80, 60],
            "research_rank": [1, 2],
            "research_bucket": ["Core Research", "Watch Research"],
        }
    )
    df.to_csv(path, index=False)

    result = audit_research_result(path=path)

    assert result["exists"] is True
    assert result["rows"] == 2
    assert result["missing_fields"] == ""
    assert "Core Research" in result["bucket_distribution"]
    assert RESEARCH_RESULT_AUDIT_CACHE.exists()


def test_research_result_audit_reports_missing_fields(tmp_path):
    path = tmp_path / "latest_research_result.csv"
    pd.DataFrame({"ticker": ["000001"]}).to_csv(path, index=False)

    result = audit_research_result(path=path)

    assert result["rows"] == 1
    assert "research_bucket" in result["missing_fields"]
