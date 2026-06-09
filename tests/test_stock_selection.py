import copy
import importlib

import pandas as pd

from selection.stock_selection import STOCK_SELECTION_FIELDS, build_stock_selection


def selection_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "composite_score": 90,
                "candidate_pool": "Core",
                "candidate_rank": 1,
                "performance_label": "Strong",
                "risk_level": "Low",
                "backtest_quality_label": "Good",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "composite_score": 75,
                "candidate_pool": "Watch",
                "candidate_rank": 2,
                "performance_label": "Normal",
                "risk_level": "Low",
                "backtest_quality_label": "Good",
            },
            {
                "ticker": "600002",
                "name": "Sample C",
                "composite_score": 82,
                "candidate_pool": "Exclude",
                "candidate_rank": None,
                "performance_label": "Strong",
                "risk_level": "Low",
                "backtest_quality_label": "Good",
            },
        ]
    )


def test_empty_input_safe_return():
    output = build_stock_selection(pd.DataFrame())

    assert output.empty
    assert set(STOCK_SELECTION_FIELDS).issubset(output.columns)


def test_missing_composite_score_returns_incomplete():
    frame = selection_frame().iloc[[0]].drop(columns=["composite_score"])

    output = build_stock_selection(frame)

    row = output.iloc[0]
    assert row["selection_available"] is False
    assert row["selection_status"] == "Incomplete"
    assert any("composite_score column missing" in warning for warning in row["selection_warnings"])


def test_core_high_score_outputs_selected():
    output = build_stock_selection(selection_frame().iloc[[0]])

    row = output.iloc[0]
    assert row["selection_score"] == 85
    assert row["selection_level"] == "High"
    assert row["selection_status"] == "Selected"
    assert row["selection_bucket"] == "Core"


def test_watch_medium_score_outputs_watch():
    output = build_stock_selection(selection_frame().iloc[[1]])

    row = output.iloc[0]
    assert 60 <= row["selection_score"] < 80
    assert row["selection_level"] == "Medium"
    assert row["selection_status"] == "Watch"
    assert row["selection_bucket"] == "Watch"


def test_exclude_outputs_excluded():
    output = build_stock_selection(selection_frame().iloc[[2]])

    row = output.iloc[0]
    assert row["selection_status"] == "Excluded"
    assert row["selection_bucket"] == "Exclude"


def test_high_risk_downgrades_selected_row():
    frame = selection_frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "risk_level"] = "High"

    output = build_stock_selection(frame)

    row = output.iloc[0]
    assert row["selection_status"] == "Watch"
    assert row["selection_bucket"] == "Watch"
    assert any("Risk level is High" in note for note in row["selection_risk_notes"])


def test_poor_backtest_quality_downgrades_selected_row():
    frame = selection_frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "backtest_quality_label"] = "Poor"

    output = build_stock_selection(frame)

    row = output.iloc[0]
    assert row["selection_status"] == "Watch"
    assert row["selection_bucket"] == "Watch"
    assert any("Backtest quality label is Poor" in note for note in row["selection_risk_notes"])


def test_selection_rank_generated_correctly():
    output = build_stock_selection(selection_frame())

    rank_by_ticker = dict(zip(output["ticker"], output["selection_rank"]))
    assert rank_by_ticker["600000"] == 1
    assert rank_by_ticker["600001"] == 2
    assert rank_by_ticker["600002"] == 3


def test_selection_rank_does_not_change_row_order():
    frame = selection_frame().iloc[[1, 0, 2]].reset_index(drop=True)

    output = build_stock_selection(frame)

    assert output["ticker"].tolist() == ["600001", "600000", "600002"]
    assert output["selection_rank"].tolist() == [2, 1, 3]


def test_selection_reasons_generated():
    output = build_stock_selection(selection_frame().iloc[[0]])

    reasons = output.iloc[0]["selection_reasons"]
    assert reasons
    assert any("Composite score contributes" in reason for reason in reasons)


def test_selection_risk_notes_generated():
    frame = selection_frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "risk_level"] = "High"

    output = build_stock_selection(frame)

    assert output.iloc[0]["selection_risk_notes"]


def test_selection_warnings_generated():
    frame = selection_frame().iloc[[0]].drop(columns=["performance_label"])

    output = build_stock_selection(frame)

    assert any("performance_label column missing" in warning for warning in output.iloc[0]["selection_warnings"])


def test_input_object_is_not_modified():
    frame = selection_frame()
    frame_before = copy.deepcopy(frame)

    build_stock_selection(frame)

    pd.testing.assert_frame_equal(frame, frame_before)


def test_composite_score_not_modified():
    output = build_stock_selection(selection_frame().iloc[[0]])

    assert output.iloc[0]["composite_score"] == 90


def test_candidate_rank_not_modified():
    output = build_stock_selection(selection_frame().iloc[[0]])

    assert output.iloc[0]["candidate_rank"] == 1


def test_module_importable():
    assert importlib.import_module("selection.stock_selection")
