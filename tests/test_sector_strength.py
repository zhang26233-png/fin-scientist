import os

import pandas as pd


os.environ["FINSCIENTIST_SKIP_UI"] = "1"

import legacy_app  # noqa: E402
from core.sector_strength import generate_sector_strength_summary, generate_sector_strength_text  # noqa: E402


def make_sector_frame():
    return pd.DataFrame(
        [
            {
                "股票代码": "300750",
                "板块": "新能源",
                "研究优先级评分": 72,
                "近 20 日涨跌幅": "12.00%",
                "近 60 日涨跌幅": "24.00%",
                "成交量放大倍数": "1.50",
                "年化波动率": "32.00%",
                "最大回撤": "-12.00%",
            },
            {
                "股票代码": "002594",
                "板块": "新能源",
                "研究优先级评分": 58,
                "近 20 日涨跌幅": "5.00%",
                "近 60 日涨跌幅": "18.00%",
                "成交量放大倍数": "1.20",
                "年化波动率": "28.00%",
                "最大回撤": "-9.00%",
            },
            {
                "股票代码": "600519",
                "板块": "消费",
                "研究优先级评分": 45,
                "近 20 日涨跌幅": "-2.00%",
                "近 60 日涨跌幅": "3.00%",
                "成交量放大倍数": "0.90",
                "年化波动率": "18.00%",
                "最大回撤": "-6.00%",
            },
        ]
    )


def test_sector_strength_core_and_legacy_paths_match():
    source_df = make_sector_frame()

    core_result = generate_sector_strength_summary(source_df)
    legacy_result = legacy_app.generate_sector_strength_summary(source_df)

    pd.testing.assert_frame_equal(core_result, legacy_result)
    assert core_result["板块"].tolist() == ["新能源", "消费"]
    assert core_result.iloc[0]["平均研究优先级评分"] == "65.00"


def test_sector_strength_text_core_and_legacy_paths_match():
    sector_df = generate_sector_strength_summary(make_sector_frame())

    core_text = generate_sector_strength_text(sector_df)
    legacy_text = legacy_app.generate_sector_strength_text(sector_df)

    assert core_text == legacy_text
    assert "不构成投资建议" in core_text
    assert "新能源" in core_text


def test_sector_strength_handles_empty_and_missing_fields():
    assert generate_sector_strength_summary(pd.DataFrame()).empty

    missing_field_df = pd.DataFrame([{"股票代码": "000001", "板块": "金融"}])
    result = generate_sector_strength_summary(missing_field_df)

    assert len(result) == 1
    assert result.iloc[0]["板块"] == "金融"
    assert isinstance(generate_sector_strength_text(pd.DataFrame()), str)
