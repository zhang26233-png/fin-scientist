from pipeline.runtime_monitor import PipelineRunReport, SCHEDULER_REPORT_COLUMNS


def test_stage_report_fields_complete():
    report = PipelineRunReport(run_id="test-run")
    report.add_stage("Stage 1", 10, 5, 0.1, "OK", "")
    frame = report.to_dataframe()

    assert list(frame.columns) == SCHEDULER_REPORT_COLUMNS


def test_stage_seconds_non_negative():
    report = PipelineRunReport()
    report.add_stage("Stage 1", 1, 1, -1, "OK", "")
    frame = report.to_dataframe()

    assert frame["stage_seconds"].iloc[0] >= 0
    assert frame["total_seconds"].iloc[0] >= 0


def test_warning_can_be_recorded():
    report = PipelineRunReport()
    report.add_stage("Stage 2", 5, 5, 0.0, "Warning", "degraded")
    frame = report.to_dataframe()

    assert frame["stage_status"].iloc[0] == "Warning"
    assert frame["stage_warning"].iloc[0] == "degraded"


def test_can_output_dataframe():
    report = PipelineRunReport()
    report.add_stage("Stage 1", 2, 1, 0.0)

    assert not report.to_dataframe().empty
