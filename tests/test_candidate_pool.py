import copy
import importlib

import pandas as pd

from screening.candidate_pool import CANDIDATE_POOL_FIELDS, build_candidate_pool


def composite_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "composite_available": True,
                "composite_score": 85,
                "composite_level": "High",
                "composite_screening_status": "Pass",
                "fundamental_score": 82,
                "technical_score": 88,
                "strategy_score": 42,
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "composite_available": True,
                "composite_score": 66,
                "composite_level": "Medium",
                "composite_screening_status": "Watch",
                "fundamental_score": 60,
                "technical_score": 72,
                "strategy_score": 66,
            },
        ]
    )


def test_empty_input_safe_return():
    output = build_candidate_pool(pd.DataFrame())

    assert output.empty
    assert set(CANDIDATE_POOL_FIELDS).issubset(output.columns)


def test_missing_composite_score_returns_unavailable():
    output = build_candidate_pool(pd.DataFrame([{"ticker": "600000", "composite_available": True}]))

    row = output.iloc[0]
    assert row["candidate_pool"] == "Unavailable"
    assert row["candidate_level"] == "Unavailable"
    assert row["candidate_status"] == "Incomplete"
    assert any("composite_score missing or invalid" in warning for warning in row["candidate_warnings"])


def test_high_pass_enters_core():
    output = build_candidate_pool(composite_frame().iloc[[0]])

    row = output.iloc[0]
    assert row["candidate_pool"] == "Core"
    assert row["candidate_level"] == "A"
    assert row["candidate_status"] == "Selected"


def test_medium_watch_enters_watch():
    output = build_candidate_pool(composite_frame().iloc[[1]])

    row = output.iloc[0]
    assert row["candidate_pool"] == "Watch"
    assert row["candidate_level"] == "B"
    assert row["candidate_status"] == "Watch"


def test_low_exclude_enters_exclude():
    output = build_candidate_pool(
        pd.DataFrame(
            [
                {
                    "ticker": "600002",
                    "composite_available": True,
                    "composite_score": 25,
                    "composite_level": "Low",
                    "composite_screening_status": "Exclude",
                }
            ]
        )
    )

    row = output.iloc[0]
    assert row["candidate_pool"] == "Exclude"
    assert row["candidate_level"] == "C"
    assert row["candidate_status"] == "Excluded"
    assert "Low Score" in row["candidate_risk_flags"]


def test_missing_fields_generate_warnings():
    output = build_candidate_pool(
        pd.DataFrame(
            [
                {
                    "ticker": "600000",
                    "composite_available": True,
                    "composite_score": 70,
                    "composite_screening_status": "Watch",
                }
            ]
        )
    )

    assert any("composite_level missing" in warning for warning in output.iloc[0]["candidate_warnings"])


def test_candidate_rank_generated_correctly():
    output = build_candidate_pool(
        pd.DataFrame(
            [
                {
                    "ticker": "600000",
                    "composite_available": True,
                    "composite_score": 70,
                    "composite_level": "Medium",
                    "composite_screening_status": "Watch",
                },
                {
                    "ticker": "600001",
                    "composite_available": True,
                    "composite_score": 90,
                    "composite_level": "High",
                    "composite_screening_status": "Pass",
                },
                {
                    "ticker": "600002",
                    "composite_available": True,
                    "composite_score": 30,
                    "composite_level": "Low",
                    "composite_screening_status": "Exclude",
                },
            ]
        )
    )

    assert output["candidate_rank"].tolist() == [2, 1, None]


def test_candidate_rank_does_not_change_original_order():
    frame = pd.DataFrame(
        [
            {"ticker": "600000", "composite_available": True, "composite_score": 70, "composite_level": "Medium"},
            {"ticker": "600001", "composite_available": True, "composite_score": 90, "composite_level": "High", "composite_screening_status": "Pass"},
        ]
    )
    output = build_candidate_pool(frame)

    assert output["ticker"].tolist() == ["600000", "600001"]
    assert output["candidate_rank"].tolist() == [2, 1]


def test_input_object_is_not_modified():
    frame = composite_frame()
    before = copy.deepcopy(frame)

    build_candidate_pool(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_composite_score_is_not_changed():
    output = build_candidate_pool(composite_frame())

    assert output["composite_score"].tolist() == [85, 66]


def test_fundamental_score_is_not_changed():
    output = build_candidate_pool(composite_frame())

    assert output["fundamental_score"].tolist() == [82, 60]


def test_technical_score_is_not_changed():
    output = build_candidate_pool(composite_frame())

    assert output["technical_score"].tolist() == [88, 72]


def test_module_importable():
    assert importlib.import_module("screening.candidate_pool")
