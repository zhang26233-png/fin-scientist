import os

import pandas as pd


os.environ["FINSCIENTIST_SKIP_UI"] = "1"

from legacy_app import build_screening_priority_rows  # noqa: E402


REQUIRED_SCREENING_FIELDS = {
    "研究优先级评分",
    "基本面质量评分",
    "综合研究观察评分",
    "股票名称",
    "行业",
    "板块",
    "主题标签",
    "入选理由",
    "风险提示",
}


def make_price_frame():
    return pd.DataFrame(
        {
            "Close": list(range(100, 170)),
            "Volume": [1000 + index * 10 for index in range(70)],
        },
        index=pd.date_range("2024-01-01", periods=70, freq="D"),
    )


def test_screening_priority_row_keeps_public_field_contract():
    success_items = [
        {
            "display_ticker": "300750.SZ",
            "query_ticker": "300750",
            "stock_name": "宁德时代",
            "market": "A股",
            "industry": "动力电池",
            "sector": "新能源",
            "themes": "锂电池;储能",
            "price_df": make_price_frame(),
            "data_source": "测试数据",
            "latest_trade_date": "2024-03-10",
            "data_quality": "测试数据完整",
            "primary_source": "测试数据",
            "fallback_source": "无",
            "fallback_used": False,
            "source_note": "测试数据仅用于单元测试。",
        }
    ]

    scored_rows, unscored_rows = build_screening_priority_rows(success_items, run_mode="快速模式")

    assert not unscored_rows
    assert len(scored_rows) == 1
    assert REQUIRED_SCREENING_FIELDS.issubset(scored_rows[0])
    assert scored_rows[0]["股票名称"] == "宁德时代"
    assert scored_rows[0]["行业"] == "动力电池"
    assert scored_rows[0]["板块"] == "新能源"
    assert scored_rows[0]["主题标签"] == "锂电池;储能"
