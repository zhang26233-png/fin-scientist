import pandas as pd

from audit.real_data_audit import run_real_data_audit


def test_real_data_audit_passes_when_core_and_watch_exist():
    df = pd.DataFrame(
        {
            "ticker": ["core", "watch", "exclude"],
            "activated_composite_score": [64, 60, 40],
            "research_bucket": ["Core Research", "Watch Research", "Excluded / Low Priority"],
        }
    )

    result = run_real_data_audit(df)

    assert "FAIL" not in result["status"].tolist()


def test_real_data_audit_fails_when_core_empty_with_rows():
    df = pd.DataFrame(
        {
            "ticker": ["watch"],
            "activated_composite_score": [60],
            "research_bucket": ["Watch Research"],
        }
    )

    result = run_real_data_audit(df)
    core_row = result[result["check_name"].eq("Core count")].iloc[0]

    assert core_row["status"] == "FAIL"


def test_real_data_audit_warns_when_watch_empty_with_rows():
    df = pd.DataFrame(
        {
            "ticker": ["core"],
            "activated_composite_score": [64],
            "research_bucket": ["Core Research"],
        }
    )

    result = run_real_data_audit(df)
    watch_row = result[result["check_name"].eq("Watch count")].iloc[0]

    assert watch_row["status"] == "WARN"


def test_real_data_audit_empty_dataframe_fails_without_crashing():
    result = run_real_data_audit(pd.DataFrame())

    assert "FAIL" in result["status"].tolist()
