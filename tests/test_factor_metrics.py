import copy
import importlib

import pandas as pd

from factor.factor_metrics import (
    calculate_factor_ic,
    calculate_group_returns,
    calculate_rank_ic,
    label_factor_effectiveness,
)


def metric_frame():
    return pd.DataFrame(
        [
            {"ticker": "A", "selection_score": 10, "period_return": 0.01},
            {"ticker": "B", "selection_score": 20, "period_return": 0.02},
            {"ticker": "C", "selection_score": 30, "period_return": 0.03},
            {"ticker": "D", "selection_score": 40, "period_return": 0.04},
            {"ticker": "E", "selection_score": 50, "period_return": 0.05},
        ]
    )


def test_factor_metrics_importable():
    assert importlib.import_module("factor.factor_metrics")


def test_factor_ic_calculation():
    ic = calculate_factor_ic(metric_frame(), "selection_score", "period_return")

    assert round(ic, 6) == 1.0


def test_rank_ic_calculation():
    rank_ic = calculate_rank_ic(metric_frame(), "selection_score", "period_return")

    assert round(rank_ic, 6) == 1.0


def test_missing_factor_field_returns_none():
    assert calculate_factor_ic(metric_frame(), "missing_factor", "period_return") is None


def test_missing_return_field_returns_none():
    assert calculate_rank_ic(metric_frame(), "selection_score", "missing_return") is None


def test_group_returns_are_generated():
    result = calculate_group_returns(metric_frame(), "selection_score", "period_return", n_groups=5)

    assert list(result.columns) == ["factor_group", "factor_group_return"]
    assert result.iloc[0]["factor_group"] == "Q1"
    assert result.iloc[-1]["factor_group"] == "Q5"


def test_group_returns_missing_fields_returns_empty():
    result = calculate_group_returns(metric_frame(), "selection_score", "missing_return")

    assert result.empty


def test_effectiveness_label_rules():
    assert label_factor_effectiveness(0.06) == "Positive"
    assert label_factor_effectiveness(0.0) == "Weak"
    assert label_factor_effectiveness(-0.06) == "Negative"
    assert label_factor_effectiveness(None) == "Unavailable"


def test_metric_functions_do_not_modify_input():
    frame = metric_frame()
    before = copy.deepcopy(frame)

    calculate_factor_ic(frame, "selection_score", "period_return")
    calculate_rank_ic(frame, "selection_score", "period_return")
    calculate_group_returns(frame, "selection_score", "period_return")

    pd.testing.assert_frame_equal(frame, before)
