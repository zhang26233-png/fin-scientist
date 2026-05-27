import os

import pandas as pd


os.environ["FINSCIENTIST_SKIP_UI"] = "1"

import legacy_app  # noqa: E402
from core.explanations import (  # noqa: E402
    generate_fundamental_summary,
    generate_screening_risk_warnings,
    generate_screening_summary,
    generate_selection_reasons,
    join_explanation_items,
)


def make_metrics():
    return {
        "当前价格是否高于 MA20": True,
        "当前价格是否高于 MA60": True,
        "MA20 是否高于 MA60": True,
        "近 20 日涨跌幅": 0.12,
        "近 60 日涨跌幅": 0.24,
        "成交量放大倍数": 1.5,
        "最大回撤": -0.12,
        "年化波动率": 0.32,
        "有效交易日数量": 80,
        "成交量数据缺失": False,
        "使用备用数据源": False,
        "数据质量": "数据较完整",
        "基本面数据源": "AkShare",
        "基本面字段缺失较多": False,
    }


def make_summary_frame():
    frame = pd.DataFrame(
        [
            {
                "股票代码": "300750",
                "是否高于 MA20": "是",
                "是否高于 MA60": "是",
                "成交量放大倍数": "1.50",
                "近 20 日涨跌幅": "12.00%",
                "风险提示": "暂未触发主要风险阈值。",
                "基本面数据源": "AkShare",
                "研究优先级评分": 65,
                "基本面质量评分": 55,
            }
        ]
    )
    frame.attrs["total_count"] = 1
    return frame


def test_explanation_functions_import_and_legacy_paths_match():
    metrics = make_metrics()

    assert generate_selection_reasons(metrics) == legacy_app.generate_selection_reasons(metrics)
    assert generate_screening_risk_warnings(metrics) == legacy_app.generate_screening_risk_warnings(metrics)
    assert generate_screening_summary(make_summary_frame()) == legacy_app.generate_screening_summary(make_summary_frame())
    assert join_explanation_items(["A", "", None, "B"]) == legacy_app.join_explanation_items(["A", "", None, "B"])


def test_explanations_return_stable_text_for_typical_inputs():
    reasons = generate_selection_reasons(make_metrics())
    warnings = generate_screening_risk_warnings(make_metrics())
    summary = generate_screening_summary(make_summary_frame())

    assert reasons
    assert warnings
    assert isinstance(summary, str)
    assert "不构成投资建议" in summary


def test_explanations_handle_empty_missing_and_invalid_inputs():
    assert generate_selection_reasons(None)
    assert generate_screening_risk_warnings(None)
    assert isinstance(generate_screening_summary(pd.DataFrame()), str)
    assert isinstance(generate_screening_summary(None, failed_items=[{}], insufficient_items=[{}]), str)

    assert isinstance(generate_fundamental_summary({}), str)
    assert isinstance(generate_fundamental_summary({"roe": None, "pe_ttm": "bad"}), str)


def test_fundamental_summary_core_and_legacy_paths_match():
    fundamental = {
        "roe": 0.18,
        "revenue_yoy": 0.12,
        "net_profit_yoy": 0.10,
        "debt_asset_ratio": 0.35,
        "pe_ttm": 35,
        "pb": 4,
        "fundamental_source": "AkShare",
    }

    assert generate_fundamental_summary(fundamental) == legacy_app.generate_fundamental_summary(fundamental)
