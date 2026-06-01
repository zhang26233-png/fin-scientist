import copy
from pathlib import Path

import pandas as pd

from ui.screening_ui import build_screening_strategy_preview


FORBIDDEN_STRATEGY_UI_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_STRATEGY_UI_WORDS:
        assert word not in text


def make_screening_result_frame():
    return pd.DataFrame(
        [
            {
                "股票代码": "LOW1",
                "股票名称": "Low Sample",
                "最新价格": 100,
                "近 20 日涨跌幅": -0.08,
                "return_10d": -0.04,
                "return_5d": -0.02,
                "成交量": 60_000,
                "成交额": 3_000_000,
                "换手率": 0.001,
                "成交量放大倍数": 0.7,
                "年化波动率": 0.35,
                "有效交易日数量": 90,
                "研究优先级评分": 42,
            },
            {
                "股票代码": "HIGH1",
                "股票名称": "High Sample",
                "最新价格": 100,
                "近 20 日涨跌幅": 0.16,
                "return_10d": 0.09,
                "return_5d": 0.04,
                "MA5": 98,
                "MA10": 95,
                "MA20": 90,
                "营业收入": "5亿",
                "净利润": "8,000万",
                "毛利率": "42%",
                "行业": "医药",
                "成交量": 1_500_000,
                "成交额": 160_000_000,
                "换手率": 0.04,
                "成交量放大倍数": 1.4,
                "年化波动率": 0.25,
                "有效交易日数量": 90,
                "研究优先级评分": 66,
            },
        ]
    )


def test_strategy_ui_integration_empty_dataframe_safe_return():
    preview = build_screening_strategy_preview(pd.DataFrame())

    assert preview.empty
    assert "strategy_score" in preview.columns
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_ui_integration_missing_fields_safe_return():
    preview = build_screening_strategy_preview(pd.DataFrame([{"股票代码": "MISSING"}]))

    assert len(preview) == 1
    assert preview.iloc[0]["symbol"] == "MISSING"
    assert preview.iloc[0]["strategy_score"] == 0
    assert "best_preset" in preview.columns
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_ui_integration_does_not_modify_source_dataframe():
    frame = make_screening_result_frame()
    before = copy.deepcopy(frame)

    build_screening_strategy_preview(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_strategy_ui_integration_preserves_input_order_by_default():
    preview = build_screening_strategy_preview(make_screening_result_frame())

    assert list(preview["symbol"]) == ["LOW1", "HIGH1"]
    assert {"strategy_score", "best_preset", "dominant_style", "consensus_level"}.issubset(preview.columns)
    assert {"strategy_reason", "risk_reason", "data_quality_reason", "confidence_note"}.issubset(preview.columns)
    assert {"ma_structure_label", "trend_quality_label", "technical_profile_summary"}.issubset(preview.columns)
    assert {"technical_grade", "technical_style", "technical_strength", "technical_risk_level"}.issubset(preview.columns)
    assert {"fundamental_available", "fundamental_data_quality_label", "fundamental_summary_base"}.issubset(preview.columns)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_ui_integration_sorting_only_changes_preview_output():
    frame = make_screening_result_frame()
    before = copy.deepcopy(frame)
    preview = build_screening_strategy_preview(frame, sort_by_strategy=True)

    assert list(preview["symbol"]) != ["LOW1", "HIGH1"]
    pd.testing.assert_frame_equal(frame, before)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_ui_integration_dependency_boundary():
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    core_scoring_text = Path("core/scoring.py").read_text(encoding="utf-8")

    assert "strategy.preview" in screening_text
    assert "strategy.preview" not in legacy_text
    assert "build_strategy_preview" not in legacy_text
    assert "strategy.preview" not in core_scoring_text
    assert_no_forbidden_words(screening_text)
