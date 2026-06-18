import importlib

import pandas as pd

from pipeline.runtime_monitor import SCHEDULER_REPORT_COLUMNS
from pipeline.scheduler import run_scheduled_pipeline


def _universe(rows=8):
    return pd.DataFrame(
        [
            {
                "ticker": f"00000{i}",
                "name": f"Name {i}",
                "latest_price": 10 + i,
                "pct_change": i,
                "volume": 1_000_000 + i,
                "turnover": 100_000_000 + i * 10_000_000,
                "turnover_rate": 1 + i,
                "volume_ratio": 1 + i / 10,
                "open": 10,
                "high": 12,
                "low": 9,
                "prev_close": 10,
                "data_status": "Live",
            }
            for i in range(rows)
        ]
    )


def _fake_full_run(source, **kwargs):
    result = source.copy(deep=True)
    if "real_technical_score" not in result.columns:
        result["real_technical_score"] = range(60, 60 + len(result))
    result["fundamental_research_score"] = range(55, 55 + len(result))
    result["capital_flow_score"] = range(56, 56 + len(result))
    result["news_event_score"] = 60
    result["quote_quality_score"] = 80
    result["activated_composite_score"] = (
        result["fundamental_research_score"] * 0.3
        + result["real_technical_score"] * 0.3
        + result["capital_flow_score"] * 0.25
        + result["news_event_score"] * 0.1
        + result["quote_quality_score"] * 0.05
    )
    return result


def test_scheduler_importable():
    assert importlib.import_module("pipeline.scheduler")


def test_empty_data_does_not_crash():
    result = run_scheduled_pipeline(pd.DataFrame())

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert "scheduler_report_df" in result.attrs


def test_four_stage_rows_decrease(monkeypatch):
    import pipeline.scheduler as scheduler

    monkeypatch.setattr(scheduler, "_scheduled_full_run", _fake_full_run)
    result = scheduler.run_scheduled_pipeline(_universe(10), stage1_limit=8, stage2_limit=5, stage3_limit=3, core_limit=1, watch_limit=1)
    report = result.attrs["scheduler_report_df"]

    assert report["stage_output_rows"].tolist() == [8, 5, 3, 3]


def test_stage_failure_can_degrade(monkeypatch):
    import pipeline.scheduler as scheduler

    def fail_once(source, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(scheduler, "_scheduled_full_run", fail_once)
    result = scheduler.run_scheduled_pipeline(_universe(5), stage1_limit=5, stage2_limit=3, stage3_limit=2)
    report = result.attrs["scheduler_report_df"]

    assert isinstance(result, pd.DataFrame)
    assert "Warning" in report["stage_status"].tolist()


def test_use_scheduler_true_returns_research_df(monkeypatch):
    import pipeline.live_runner as live_runner

    frame = _universe(1002)
    frame.attrs["data_source"] = "Tencent Realtime"
    frame.attrs["data_status"] = "Live"
    frame.attrs["raw_count"] = 1002
    frame.attrs["final_count"] = 1002
    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: frame)

    def fake_scheduler(universe, **kwargs):
        result = universe.head(2).copy(deep=True)
        result["research_bucket"] = ["Core Research", "Watch Research"]
        result["research_rank"] = [1, 2]
        report = pd.DataFrame(columns=SCHEDULER_REPORT_COLUMNS)
        result.attrs["scheduler_report_df"] = report
        return result

    monkeypatch.setattr(live_runner, "run_scheduled_pipeline", fake_scheduler)
    result = live_runner.run_live_pipeline(use_scheduler=True)

    assert isinstance(result, pd.DataFrame)
    assert result.attrs["pipeline_mode"] == "Scheduler"
    assert "research_bucket" in result.columns


def test_scheduler_report_fields_complete(monkeypatch):
    import pipeline.scheduler as scheduler

    monkeypatch.setattr(scheduler, "_scheduled_full_run", _fake_full_run)
    result = scheduler.run_scheduled_pipeline(_universe(6), stage1_limit=5, stage2_limit=4, stage3_limit=3)
    report = result.attrs["scheduler_report_df"]

    assert list(report.columns) == SCHEDULER_REPORT_COLUMNS


def test_scheduler_report_includes_final_bucket_summary(monkeypatch):
    import pipeline.scheduler as scheduler

    monkeypatch.setattr(scheduler, "_scheduled_full_run", _fake_full_run)
    result = scheduler.run_scheduled_pipeline(_universe(10), stage1_limit=8, stage2_limit=6, stage3_limit=5)
    report = result.attrs["scheduler_report_df"]

    assert int(report["rows"].iloc[0]) == len(result)
    assert int(report["final_rows"].iloc[0]) == len(result)
    assert int(report["core_count"].iloc[0]) == int(result["research_bucket"].eq("Core Research").sum())
    assert "bucket_distribution" in report.columns


def test_scheduler_result_cache_contains_final_bucket_fields(monkeypatch, tmp_path):
    import pipeline.scheduler as scheduler

    monkeypatch.setattr(scheduler, "_scheduled_full_run", _fake_full_run)
    monkeypatch.setattr(scheduler, "SCHEDULER_CACHE_DIR", tmp_path)
    monkeypatch.setattr(scheduler, "SCHEDULER_RESULT_CACHE", tmp_path / "latest_research_result.csv")
    monkeypatch.setattr(scheduler, "SCHEDULER_REPORT_CACHE", tmp_path / "latest_scheduler_report.csv")
    scheduler.run_scheduled_pipeline(_universe(10), stage1_limit=8, stage2_limit=6, stage3_limit=5)

    cached = pd.read_csv(tmp_path / "latest_research_result.csv", dtype={"ticker": str})

    assert {
        "research_rank",
        "research_score",
        "research_bucket",
        "bucket_generation_reason",
        "unified_research_score",
        "research_summary",
    }.issubset(cached.columns)
    assert cached["research_bucket"].notna().any()


def test_scheduler_final_rank_uses_unified_research_score(monkeypatch):
    import pipeline.scheduler as scheduler

    def fake_full_run(source, **kwargs):
        result = source.copy(deep=True)
        is_unified_high = result["ticker"].astype(str).eq("000003")
        result["name"] = is_unified_high.map({True: "unified_high", False: "activated_high"})
        result["real_technical_score"] = is_unified_high.map({True: 90, False: 40})
        result["capital_flow_score"] = is_unified_high.map({True: 90, False: 40})
        result["fundamental_research_score"] = is_unified_high.map({True: 90, False: 40})
        result["industry_score"] = is_unified_high.map({True: 90, False: 40})
        result["news_event_score"] = is_unified_high.map({True: 90, False: 40})
        result["activated_composite_score"] = is_unified_high.map({True: 50, False: 95})
        return result

    monkeypatch.setattr(scheduler, "_scheduled_full_run", fake_full_run)
    result = scheduler.run_scheduled_pipeline(_universe(4), stage1_limit=4, stage2_limit=2, stage3_limit=2, core_limit=1, watch_limit=1)

    assert result["name"].tolist()[0] == "unified_high"
    assert result["research_score"].tolist()[0] == result["unified_research_score"].tolist()[0]


def test_scheduler_cache_invalidates_missing_bucket(monkeypatch, tmp_path):
    import pipeline.scheduler as scheduler

    result_path = tmp_path / "latest_research_result.csv"
    report_path = tmp_path / "latest_scheduler_report.csv"
    pd.DataFrame({"ticker": ["000001"], "name": ["Name"]}).to_csv(result_path, index=False)
    pd.DataFrame(columns=SCHEDULER_REPORT_COLUMNS).to_csv(report_path, index=False)
    monkeypatch.setattr(scheduler, "SCHEDULER_RESULT_CACHE", result_path)
    monkeypatch.setattr(scheduler, "SCHEDULER_REPORT_CACHE", report_path)

    result, report = scheduler.load_scheduler_cache()

    assert result.empty
    assert report.empty


def test_does_not_mutate_input(monkeypatch):
    import pipeline.scheduler as scheduler

    monkeypatch.setattr(scheduler, "_scheduled_full_run", _fake_full_run)
    source = _universe(6)
    original = source.copy(deep=True)
    scheduler.run_scheduled_pipeline(source, stage1_limit=5, stage2_limit=4, stage3_limit=3)

    pd.testing.assert_frame_equal(source, original)


def test_core_tab_not_empty(monkeypatch):
    import ui.product_ui as product_ui

    df = pd.DataFrame(
        {
            "ticker": ["core", "watch", "exclude"],
            "name": ["Core", "Watch", "Exclude"],
            "research_bucket": ["Core Research", "Watch Research", "Excluded / Low Priority"],
            "research_rank": [1, 2, 3],
            "activated_composite_score": [64, 60, 40],
        }
    )

    class DummyTab:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(product_ui, "_render_page_header", lambda *args, **kwargs: None)
    monkeypatch.setattr(product_ui, "_render_table", lambda frame, columns, label: frame.copy(deep=True))
    monkeypatch.setattr(product_ui.st, "selectbox", lambda label, options, index=0: options[index])
    monkeypatch.setattr(product_ui.st, "tabs", lambda labels: [DummyTab() for _ in labels])
    monkeypatch.setattr(product_ui.st, "columns", lambda count: [DummyTab() for _ in range(count)])
    monkeypatch.setattr(product_ui.st, "error", lambda message: None)
    metric_cards = []
    monkeypatch.setattr(product_ui, "_render_metric_card", lambda title, value, caption: metric_cards.append((title, value, caption)))

    result = product_ui.render_selection_page(df)

    assert not result["top_core"].empty
    assert ("Core数量", 1, "research_bucket") in metric_cards
    assert ("Watch数量", 1, "research_bucket") in metric_cards
    assert ("Excluded数量", 1, "research_bucket") in metric_cards
