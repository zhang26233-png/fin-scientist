from datetime import date

import pandas as pd

from data.a_share_loader import OUTPUT_COLUMNS, load_a_share_universe


TODAY = date(2026, 6, 11)


def _large_source():
    rows = []
    for index in range(1100):
        if index % 4 == 0:
            ticker = f"60{index:04d}"[-6:]
        elif index % 4 == 1:
            ticker = f"00{index:04d}"[-6:]
        elif index % 4 == 2:
            ticker = f"30{index:04d}"[-6:]
        else:
            ticker = f"688{index % 1000:03d}"
        rows.append(
            {
                "代码": ticker,
                "名称": f"样本{index}",
                "行业": "测试行业",
                "上市日期": "2020-01-01",
                "状态": "正常",
            }
        )
    rows.extend(
        [
            {"代码": "600001", "名称": "ST样本", "行业": "测试行业", "上市日期": "2020-01-01", "状态": "正常"},
            {"代码": "600002", "名称": "*ST样本", "行业": "测试行业", "上市日期": "2020-01-01", "状态": "正常"},
            {"代码": "600003", "名称": "退市样本", "行业": "测试行业", "上市日期": "2020-01-01", "状态": "退市"},
            {"代码": "600004", "名称": "暂停样本", "行业": "测试行业", "上市日期": "2020-01-01", "状态": "暂停上市"},
            {"代码": "600005", "名称": "", "行业": "测试行业", "上市日期": "2020-01-01", "状态": "正常"},
            {"代码": "600006", "名称": "新股样本", "行业": "测试行业", "上市日期": "2026-05-01", "状态": "正常"},
            {"代码": "600010", "名称": "重复样本", "行业": "测试行业", "上市日期": "2020-01-01", "状态": "正常"},
        ]
    )
    return pd.DataFrame(rows)


def test_loader_returns_large_universe_from_free_source_shape():
    universe = load_a_share_universe(source_df=_large_source(), today=TODAY)

    assert len(universe) > 1000
    assert list(universe.columns) == OUTPUT_COLUMNS
    assert universe.attrs["raw_count"] > universe.attrs["final_count"]


def test_loader_fields_complete():
    universe = load_a_share_universe(source_df=_large_source(), today=TODAY)

    for field in ["ticker", "name", "market", "industry", "list_date"]:
        assert field in universe.columns
    assert universe[["ticker", "name", "market"]].notna().all().all()


def test_loader_has_no_duplicate_ticker():
    universe = load_a_share_universe(source_df=_large_source(), today=TODAY)

    assert not universe["ticker"].duplicated().any()


def test_loader_filters_st_delisted_suspended_empty_name_and_new_stock():
    universe = load_a_share_universe(source_df=_large_source(), today=TODAY)
    names = set(universe["name"].tolist())

    assert "ST样本" not in names
    assert "*ST样本" not in names
    assert "退市样本" not in names
    assert "暂停样本" not in names
    assert "" not in names
    assert "新股样本" not in names
    assert universe.attrs["filtered_breakdown"]["st"] >= 2
    assert universe.attrs["filtered_breakdown"]["delisted"] >= 1
    assert universe.attrs["filtered_breakdown"]["suspended"] >= 1
    assert universe.attrs["filtered_breakdown"]["empty_name"] >= 1
    assert universe.attrs["filtered_breakdown"]["new_listing"] >= 1
