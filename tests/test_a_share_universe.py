import importlib
from datetime import date

import pandas as pd

from universe.a_share_universe import UNIVERSE_FIELDS, build_a_share_universe


TODAY = date(2026, 6, 5)


def row(
    ticker="600000",
    name="浦发银行",
    list_date="2020-01-01",
    days_since_listing=2000,
    is_st=False,
    is_suspended=False,
    status="正常",
):
    return {
        "ticker": ticker,
        "name": name,
        "market": "A股",
        "list_date": list_date,
        "days_since_listing": days_since_listing,
        "is_st": is_st,
        "is_suspended": is_suspended,
        "status": status,
    }


def test_empty_data_returns_safe_empty_frame():
    universe = build_a_share_universe(pd.DataFrame(), today=TODAY)

    assert universe.empty
    assert list(universe.columns) == UNIVERSE_FIELDS
    assert universe.attrs["universe_status"] == "Incomplete"
    assert universe.attrs["universe_total_count"] == 0


def test_single_stock_available():
    universe = build_a_share_universe(pd.DataFrame([row()]), today=TODAY)

    assert len(universe) == 1
    assert universe.iloc[0]["ticker"] == "600000"
    assert universe.iloc[0]["status"] == "Available"
    assert universe.iloc[0]["universe_total_count"] == 1
    assert universe.iloc[0]["universe_filtered_count"] == 1


def test_st_filter():
    universe = build_a_share_universe(
        pd.DataFrame(
            [
                row(ticker="600000"),
                row(ticker="600001", name="ST样本", is_st=True),
            ]
        ),
        today=TODAY,
    )

    assert universe["ticker"].tolist() == ["600000"]
    assert "剔除ST 1只" in universe.attrs["universe_summary"]


def test_suspended_filter():
    universe = build_a_share_universe(
        pd.DataFrame(
            [
                row(ticker="600000"),
                row(ticker="600002", is_suspended=True, status="停牌"),
            ]
        ),
        today=TODAY,
    )

    assert universe["ticker"].tolist() == ["600000"]
    assert "剔除停牌 1只" in universe.attrs["universe_summary"]


def test_new_stock_filter():
    universe = build_a_share_universe(
        pd.DataFrame(
            [
                row(ticker="600000"),
                row(ticker="600003", list_date="2026-01-01", days_since_listing=100),
            ]
        ),
        today=TODAY,
    )

    assert universe["ticker"].tolist() == ["600000"]
    assert "剔除新股 1只" in universe.attrs["universe_summary"]


def test_field_completeness():
    universe = build_a_share_universe(pd.DataFrame([row()]), today=TODAY)

    assert list(universe.columns) == UNIVERSE_FIELDS
    assert universe.iloc[0]["universe_status"] == "Available"
    assert "全市场1只" in universe.iloc[0]["universe_summary"]


def test_module_importable():
    assert importlib.import_module("universe.a_share_universe")
