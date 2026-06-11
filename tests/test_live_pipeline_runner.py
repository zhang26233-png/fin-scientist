import copy
import importlib

import pandas as pd

from pipeline.live_runner import LIVE_PIPELINE_FIELDS, run_live_pipeline


def test_live_runner_importable():
    assert importlib.import_module("pipeline.live_runner")


def test_run_live_pipeline_returns_dataframe():
    result = run_live_pipeline(max_stocks=20)

    assert isinstance(result, pd.DataFrame)


def test_data_source_failure_returns_demo_dataframe(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "build_a_share_universe", lambda: pd.DataFrame())
    result = live_runner.run_live_pipeline(max_stocks=20)

    assert result.attrs.get("is_demo") is True
    assert len(result) >= 20


def test_demo_dataframe_has_required_selection_explain_and_factor_fields(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "build_a_share_universe", lambda: pd.DataFrame())
    result = live_runner.run_live_pipeline(max_stocks=20)

    for field in LIVE_PIPELINE_FIELDS:
        assert field in result.columns
    assert "selection_score" in result.columns
    assert "selection_rank" in result.columns
    assert "selection_bucket" in result.columns
    assert "selection_explanation" in result.columns
    assert "factor_ic" in result.columns
    assert "factor_rank_ic" in result.columns
    assert "factor_effectiveness_label" in result.columns


def test_input_price_history_is_not_mutated(monkeypatch):
    import pipeline.live_runner as live_runner

    history = {"600519": pd.DataFrame({"date": pd.date_range("2024-01-01", periods=80), "close": range(80)})}
    original = copy.deepcopy(history)
    monkeypatch.setattr(live_runner, "build_a_share_universe", lambda: pd.DataFrame())

    live_runner.run_live_pipeline(price_history_dict=history)

    pd.testing.assert_frame_equal(history["600519"], original["600519"])


def test_app_importable_after_live_pipeline_addition():
    assert importlib.import_module("app")
