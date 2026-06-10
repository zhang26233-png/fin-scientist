import importlib

import pandas as pd

from ui.product_ui import (
    BACKTEST_PAGE,
    CHART_PAGE,
    DASHBOARD_PAGE,
    FACTOR_PAGE,
    REPORT_PAGE,
    SELECTION_PAGE,
    SYSTEM_PAGE,
    UNIVERSE_PAGE,
    WORKSTATION_PAGE,
    build_dashboard_summary,
    collect_warning_fields,
    find_missing_fields,
    get_navigation_pages,
    render_backtest_page,
    render_chart_center_page,
    render_dashboard_page,
    render_factor_lab_page,
    render_report_preview_page,
    render_selection_page,
    render_stock_workstation_page,
    render_system_status_page,
    render_universe_page,
)


def product_frame():
    return pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample A",
                "market": "A",
                "list_date": "2000-01-01",
                "is_st": False,
                "is_suspended": False,
                "universe_status": "Available",
                "fundamental_score": 80,
                "technical_score": 70,
                "composite_score": 75,
                "selection_score": 88,
                "selection_rank": 1,
                "selection_bucket": "Core",
                "selection_status": "Selected",
                "selection_quality_label": "Strong",
                "selection_summary": "Research object summary.",
                "selection_risk_notes": [],
                "selection_thesis": "Quality Growth",
                "selection_strengths": ["Stable score"],
                "selection_risks": ["Volatility needs review"],
                "selection_explanation": "Neutral research explanation.",
                "backtest_available": True,
                "period_return": 0.12,
                "annualized_return": 0.18,
                "volatility": 0.30,
                "max_drawdown": -0.12,
                "win_rate": 0.55,
                "return_risk_ratio": 1.0,
                "risk_score": 25,
                "risk_level": "Low",
                "performance_label": "Strong",
                "backtest_quality_label": "Good",
                "factor_warnings": [],
            }
        ]
    )


def test_app_importable():
    assert importlib.import_module("app")


def test_page_render_functions_importable():
    module = importlib.import_module("ui.product_ui")
    for name in [
        "render_dashboard_page",
        "render_universe_page",
        "render_selection_page",
        "render_stock_workstation_page",
        "render_backtest_page",
        "render_chart_center_page",
        "render_factor_lab_page",
        "render_report_preview_page",
        "render_system_status_page",
    ]:
        assert callable(getattr(module, name))


def test_navigation_config_can_be_generated():
    pages = get_navigation_pages()

    assert DASHBOARD_PAGE in pages
    assert UNIVERSE_PAGE in pages
    assert SELECTION_PAGE in pages
    assert WORKSTATION_PAGE in pages
    assert BACKTEST_PAGE in pages
    assert CHART_PAGE in pages
    assert FACTOR_PAGE in pages
    assert REPORT_PAGE in pages
    assert SYSTEM_PAGE in pages


def test_empty_dataframe_pages_do_not_raise():
    empty = pd.DataFrame()

    render_dashboard_page(empty)
    render_universe_page(empty)
    render_selection_page(empty)
    render_stock_workstation_page(empty)
    render_backtest_page(empty)
    render_chart_center_page(empty)
    render_factor_lab_page(empty)
    render_report_preview_page(empty)
    render_system_status_page(empty)


def test_missing_selection_fields_do_not_raise():
    frame = product_frame().drop(columns=["selection_score", "selection_bucket", "selection_status"])

    summary = build_dashboard_summary(frame)
    payload = render_selection_page(frame)

    assert summary["total_count"] == 1
    assert "table" in payload


def test_missing_factor_fields_do_not_raise():
    frame = product_frame().drop(
        columns=["fundamental_score", "technical_score", "composite_score", "selection_score", "risk_score", "return_risk_ratio"]
    )

    payload = render_factor_lab_page(frame)

    assert payload["dataset"].empty


def test_missing_backtest_fields_do_not_raise():
    frame = product_frame().drop(
        columns=["period_return", "annualized_return", "volatility", "max_drawdown", "win_rate", "return_risk_ratio"]
    )

    table = render_backtest_page(frame)

    assert len(table) == 1


def test_missing_fields_and_warning_summary():
    frame = product_frame().drop(columns=["selection_thesis"])
    missing = find_missing_fields(frame)
    warnings = collect_warning_fields(frame)

    assert "selection_thesis" in missing["Explainable Selection"]
    assert isinstance(warnings, list)


def test_report_text_restricted_words_absent():
    report = render_report_preview_page(product_frame())

    assert "买入" not in report
    assert "卖出" not in report
    assert "目标价" not in report
