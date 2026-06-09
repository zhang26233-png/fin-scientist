import importlib

import pandas as pd

from selection.explain_engine import EXPLAIN_SELECTION_FIELDS, build_explainable_selection


def explain_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "selection_available": True,
                "selection_score": 86,
                "selection_rank": 1,
                "selection_bucket": "Core",
                "selection_status": "Selected",
                "fundamental_score": 82,
                "technical_score": 90,
                "composite_score": 86,
                "risk_score": 18,
                "risk_level": "Low",
                "max_drawdown": -0.12,
                "volatility": 0.18,
                "performance_label": "Strong",
            },
            {
                "ticker": "600001",
                "name": "Sample B",
                "selection_available": True,
                "selection_score": 68,
                "selection_rank": 2,
                "selection_bucket": "Watch",
                "selection_status": "Watch",
                "fundamental_score": 78,
                "technical_score": 65,
                "composite_score": 70,
                "risk_score": 35,
                "risk_level": "Medium",
                "max_drawdown": -0.18,
                "volatility": 0.25,
                "performance_label": "Normal",
            },
            {
                "ticker": "600002",
                "name": "Sample C",
                "selection_available": True,
                "selection_score": 35,
                "selection_rank": 3,
                "selection_bucket": "Exclude",
                "selection_status": "Excluded",
                "fundamental_score": 45,
                "technical_score": 40,
                "composite_score": 42,
                "risk_score": 82,
                "risk_level": "High",
                "max_drawdown": -0.42,
                "volatility": 0.46,
                "performance_label": "Weak",
            },
        ]
    )


def test_core_explanation_generated():
    output = build_explainable_selection(explain_frame().iloc[[0]])

    row = output.iloc[0]
    assert row["explain_available"] is True
    assert row["explain_status"] == "Available"
    assert row["selection_thesis"] == "Quality Growth"
    assert "Strong Fundamental" in row["selection_strengths"]


def test_watch_explanation_generated():
    output = build_explainable_selection(explain_frame().iloc[[1]])

    row = output.iloc[0]
    assert row["selection_thesis"] == "Watch Candidate"
    assert row["selection_summary"]


def test_exclude_explanation_generated():
    output = build_explainable_selection(explain_frame().iloc[[2]])

    row = output.iloc[0]
    assert row["selection_thesis"] == "Weak Candidate"
    assert "Weak Historical Performance" in row["selection_risks"]


def test_missing_data_returns_warning():
    frame = explain_frame().iloc[[0]].drop(columns=["selection_rank"])

    output = build_explainable_selection(frame)

    warnings = output.iloc[0]["explain_warnings"]
    assert any("selection_rank column missing" in warning for warning in warnings)


def test_unavailable_selection_returns_incomplete():
    frame = explain_frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "selection_available"] = False

    output = build_explainable_selection(frame)

    row = output.iloc[0]
    assert row["explain_available"] is False
    assert row["explain_status"] == "Incomplete"


def test_risk_detection():
    output = build_explainable_selection(explain_frame().iloc[[2]])

    risks = output.iloc[0]["selection_risks"]
    assert "High Risk" in risks
    assert "Large Drawdown Risk" in risks
    assert "High Volatility" in risks


def test_factor_breakdown():
    output = build_explainable_selection(explain_frame().iloc[[0]])

    breakdown = output.iloc[0]["selection_factor_breakdown"]
    assert breakdown["fundamental_score"] == 82
    assert breakdown["technical_score"] == 90
    assert breakdown["composite_score"] == 86
    assert breakdown["risk_score"] == 18


def test_explanation_generation():
    output = build_explainable_selection(explain_frame().iloc[[0]])

    explanation = output.iloc[0]["selection_explanation"]
    assert "Core" in explanation
    assert "selection rank is 1" in explanation
    assert "research review only" in explanation


def test_summary_generation():
    output = build_explainable_selection(explain_frame().iloc[[0]])

    summary = output.iloc[0]["selection_summary"]
    assert summary
    assert len(summary) <= 30


def test_output_order_unchanged():
    frame = explain_frame().iloc[[2, 0, 1]].reset_index(drop=True)

    output = build_explainable_selection(frame)

    assert output["ticker"].tolist() == ["600002", "600000", "600001"]


def test_upstream_scores_not_modified():
    output = build_explainable_selection(explain_frame().iloc[[0]])

    assert output.iloc[0]["selection_score"] == 86
    assert output.iloc[0]["composite_score"] == 86


def test_empty_input_safe_return():
    output = build_explainable_selection(pd.DataFrame())

    assert output.empty
    assert set(EXPLAIN_SELECTION_FIELDS).issubset(output.columns)


def test_module_importable():
    assert importlib.import_module("selection.explain_engine")
