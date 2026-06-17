import pandas as pd

from audit.system_audit import (
    DATA_FIELD_AUDIT_COLUMNS,
    PIPELINE_AUDIT_COLUMNS,
    run_data_field_audit,
    run_pipeline_audit,
    run_system_audit,
)


def _research_frame():
    frame = pd.DataFrame(
        {
            "ticker": ["000001", "000002", "000003"],
            "name": ["A", "B", "C"],
            "latest_price": [10, 11, 12],
            "pct_change": [1, 2, -1],
            "turnover": [100_000_000, 90_000_000, 80_000_000],
            "turnover_rate": [2, 3, 1],
            "volume_ratio": [1.2, 1.4, 0.8],
            "real_technical_score": [80, 65, 50],
            "fundamental_research_score": [82, 60, 40],
            "capital_flow_score": [75, 55, 35],
            "news_event_score": [70, 50, 45],
            "industry_strength_score": [72, 55, 45],
            "activated_composite_score": [78, 60, 42],
            "research_bucket": ["Core Research", "Watch Research", "Excluded / Low Priority"],
            "research_rank": [1, 2, 3],
            "research_selected_reason": ["core", "watch", ""],
            "research_scheduler_warning": ["", "", "low priority"],
        }
    )
    frame.attrs["pipeline_mode"] = "Scheduler"
    frame.attrs["scheduler_status"] = "OK"
    frame.attrs["scheduler_report_df"] = pd.DataFrame(
        [
            {"stage_name": "Stage 1: Full Market Quick Scan", "stage_input_rows": 10, "stage_output_rows": 8, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
            {"stage_name": "Stage 2: Technical Filter", "stage_input_rows": 8, "stage_output_rows": 5, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
            {"stage_name": "Stage 3: Research Scoring", "stage_input_rows": 5, "stage_output_rows": 3, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
            {"stage_name": "Stage 4: Deep Event Layer", "stage_input_rows": 3, "stage_output_rows": 3, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
        ]
    )
    return frame


def test_data_field_audit_empty_dataframe_does_not_crash():
    result = run_data_field_audit(pd.DataFrame())

    assert list(result.columns) == DATA_FIELD_AUDIT_COLUMNS
    assert not result.empty
    assert set(result["status"]) == {"WARN"}


def test_data_field_audit_missing_fields_returns_warn():
    result = run_data_field_audit(pd.DataFrame({"ticker": ["000001"]}))

    assert "WARN" in result["status"].tolist()
    assert bool(result[result["field_name"].eq("name")].iloc[0]["present"]) is False


def test_pipeline_audit_output_stage_fields_complete():
    result = run_pipeline_audit(_research_frame())

    assert list(result.columns) == PIPELINE_AUDIT_COLUMNS
    assert len(result) == 4
    assert result["stage_name"].str.contains("Stage").all()


def test_system_audit_runs_without_web_rendering():
    result = run_system_audit(_research_frame())

    assert result["system_status"] in {"PASS", "WARN", "FAIL"}
    assert result["research_result_status"] == "Available"
    assert not result["ui_audit"].empty
