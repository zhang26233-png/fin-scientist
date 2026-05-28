import copy
from pathlib import Path

import pandas as pd

from config.feature_flags import is_strategy_diagnostics_enabled
from strategy.service import build_strategy_service_output
from strategy.view_model import build_strategy_view_model
from ui.strategy_diagnostics_panel import render_strategy_diagnostics_panel


FORBIDDEN_PANEL_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


class FailingStreamlitStub:
    def __getattr__(self, name):
        raise AssertionError(f"Streamlit should not be called while feature flag is disabled: {name}")


def make_view_model():
    frame = pd.DataFrame(
        [
            {
                "股票代码": "300750.SZ",
                "股票名称": "宁德时代",
                "最新价格": 210.5,
                "近 20 日涨跌幅": "12.50%",
                "成交量": 1200000,
                "成交额": 252600000,
                "行业": "电力设备",
                "板块": "动力电池",
                "研究优先级评分": 65,
                "年化波动率": "35.00%",
                "成交量放大倍数": 1.5,
                "有效交易日数量": 80,
            }
        ]
    )
    return build_strategy_view_model(build_strategy_service_output(frame))


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_PANEL_WORDS:
        assert word not in text


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def test_strategy_diagnostics_panel_imports_and_default_flag_is_off():
    assert is_strategy_diagnostics_enabled() is False


def test_strategy_diagnostics_panel_does_not_render_when_flag_is_off():
    view_model = make_view_model()
    result = render_strategy_diagnostics_panel(view_model, st_module=FailingStreamlitStub())

    assert result["rendered"] is False
    assert result["metadata"]["ui_rendering_enabled"] is False
    assert result["metadata"]["ranking_changed"] is False
    assert result["metadata"]["scoring_changed"] is False
    assert_no_forbidden_words(result)


def test_strategy_diagnostics_panel_does_not_modify_view_model():
    view_model = make_view_model()
    before = copy.deepcopy(view_model)

    render_strategy_diagnostics_panel(view_model, st_module=FailingStreamlitStub())

    assert view_model == before


def test_strategy_diagnostics_panel_does_not_call_strategy_service():
    panel_source = read_text("ui/strategy_diagnostics_panel.py")

    assert "strategy.service" not in panel_source
    assert "build_strategy_service_output" not in panel_source


def test_strategy_diagnostics_panel_is_not_used_by_current_pages():
    screening_ui = read_text("ui/screening_ui.py")
    legacy_app = read_text("legacy_app.py")

    assert "ui.strategy_diagnostics_panel" not in screening_ui
    assert "render_strategy_diagnostics_panel" not in screening_ui
    assert "ui.strategy_diagnostics_panel" not in legacy_app
    assert "render_strategy_diagnostics_panel" not in legacy_app
