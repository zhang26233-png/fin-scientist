import copy
import importlib

import pandas as pd

from backtest.backtest_engine import BACKTEST_FOUNDATION_FIELDS, build_backtest_dataset


def candidate_pool_frame():
    return pd.DataFrame(
        [
            {"ticker": "600000", "name": "Sample A", "candidate_pool": "Core", "composite_score": 85},
            {"ticker": "600001", "name": "Sample B", "candidate_pool": "Watch", "composite_score": 66},
        ]
    )


def price_history(days=60, start="2026-01-01"):
    dates = pd.date_range(start=start, periods=days, freq="D")
    return pd.DataFrame({"date": dates, "close": [10 + index for index in range(days)]})


def test_empty_input_safe_return():
    output = build_backtest_dataset(pd.DataFrame(), {})

    assert output.empty
    assert set(BACKTEST_FOUNDATION_FIELDS).issubset(output.columns)


def test_no_price_history_returns_incomplete():
    output = build_backtest_dataset(candidate_pool_frame().iloc[[0]], {})

    row = output.iloc[0]
    assert row["backtest_available"] is False
    assert row["backtest_price_available"] is False
    assert row["backtest_status"] == "Incomplete"
    assert any("Price history missing" in warning for warning in row["backtest_warnings"])


def test_single_stock_generates_fields():
    output = build_backtest_dataset(candidate_pool_frame().iloc[[0]], {"600000": price_history(60)})

    assert len(output) == 1
    assert set(BACKTEST_FOUNDATION_FIELDS).issubset(output.columns)
    assert output.iloc[0]["backtest_available"] is True
    assert output.iloc[0]["backtest_status"] == "Available"


def test_multiple_stocks_generate_fields():
    output = build_backtest_dataset(
        candidate_pool_frame(),
        {"600000": price_history(60), "600001": price_history(61, start="2026-02-01")},
    )

    assert output["ticker"].tolist() == ["600000", "600001"]
    assert output["backtest_status"].tolist() == ["Available", "Available"]
    assert output["backtest_days"].tolist() == [60, 61]


def test_history_shorter_than_60_days_is_incomplete():
    output = build_backtest_dataset(candidate_pool_frame().iloc[[0]], {"600000": price_history(59)})

    row = output.iloc[0]
    assert row["backtest_available"] is True
    assert row["backtest_price_available"] is True
    assert row["backtest_status"] == "Incomplete"
    assert any("fewer than 60" in warning for warning in row["backtest_warnings"])


def test_history_at_least_60_days_is_available():
    output = build_backtest_dataset(candidate_pool_frame().iloc[[0]], {"600000": price_history(60)})

    row = output.iloc[0]
    assert row["backtest_available"] is True
    assert row["backtest_status"] == "Available"
    assert row["backtest_days"] == 60


def test_dates_are_calculated_correctly():
    history = pd.DataFrame(
        {
            "date": ["2026-03-03", "2026-03-01", "2026-03-02"],
            "close": [12, 10, 11],
        }
    )
    output = build_backtest_dataset(candidate_pool_frame().iloc[[0]], {"600000": history})

    row = output.iloc[0]
    assert row["backtest_start_date"] == "2026-03-01"
    assert row["backtest_end_date"] == "2026-03-03"
    assert row["backtest_days"] == 3


def test_warning_generated_for_missing_columns():
    output = build_backtest_dataset(candidate_pool_frame().iloc[[0]], {"600000": pd.DataFrame([{"date": "2026-01-01"}])})

    warnings = output.iloc[0]["backtest_warnings"]
    assert any("close column missing" in warning for warning in warnings)
    assert any("No valid date and close rows" in warning for warning in warnings)


def test_input_objects_are_not_modified():
    candidates = candidate_pool_frame()
    history = price_history(60)
    histories = {"600000": history}
    candidates_before = copy.deepcopy(candidates)
    history_before = copy.deepcopy(history)

    build_backtest_dataset(candidates, histories)

    pd.testing.assert_frame_equal(candidates, candidates_before)
    pd.testing.assert_frame_equal(history, history_before)


def test_output_order_unchanged():
    output = build_backtest_dataset(
        candidate_pool_frame(),
        {"600001": price_history(60), "600000": price_history(60)},
    )

    assert output["ticker"].tolist() == ["600000", "600001"]


def test_no_performance_metric_fields_are_generated():
    output = build_backtest_dataset(candidate_pool_frame().iloc[[0]], {"600000": price_history(60)})

    forbidden_fields = {
        "return",
        "total_return",
        "annualized_return",
        "sharpe_ratio",
        "max_drawdown",
        "win_rate",
    }
    assert forbidden_fields.isdisjoint(set(output.columns))


def test_module_importable():
    assert importlib.import_module("backtest.backtest_engine")
