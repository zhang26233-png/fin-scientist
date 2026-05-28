import pandas as pd

from strategy.filters import (
    apply_basic_filters,
    check_extreme_return,
    check_min_price,
    check_min_rows,
    check_min_turnover,
    check_required_columns,
)
from strategy.presets import get_strategy_preset, list_strategy_presets


def make_price_frame(rows=30):
    return pd.DataFrame(
        {
            "Close": [10 + index * 0.1 for index in range(rows)],
            "Volume": [1000 + index for index in range(rows)],
        },
        index=pd.date_range("2024-01-01", periods=rows, freq="D"),
    )


def test_strategy_filters_handle_empty_dataframe_safely():
    empty = pd.DataFrame()

    assert check_required_columns(empty)["passed"] is False
    assert check_min_rows(empty)["passed"] is False
    assert check_min_price(empty)["passed"] is False
    assert check_extreme_return(empty)["passed"] is False
    assert apply_basic_filters(empty)["passed"] is False


def test_strategy_filters_handle_missing_fields_safely():
    frame = pd.DataFrame({"Open": [1, 2, 3]})

    assert check_required_columns(frame, required_columns=("Close",))["passed"] is False
    assert check_min_turnover(frame, min_average_turnover=1000)["passed"] is False


def test_strategy_filters_return_stable_typical_results():
    frame = make_price_frame()

    assert check_required_columns(frame)["passed"] is True
    assert check_min_rows(frame, min_rows=20)["passed"] is True
    assert check_min_price(frame, min_price=1)["passed"] is True
    assert check_min_turnover(frame, min_average_turnover=1000)["passed"] is True
    assert check_extreme_return(frame, max_abs_return=0.30)["passed"] is True
    assert apply_basic_filters(frame)["passed"] is True


def test_strategy_presets_are_read_only_copies():
    preset = get_strategy_preset("research_priority")
    preset["factor_weights"]["trend"] = 0

    assert get_strategy_preset("research_priority")["factor_weights"]["trend"] == 0.35
    assert set(list_strategy_presets()) == {
        "research_priority",
        "stable_observation",
        "high_elasticity_observation",
    }
