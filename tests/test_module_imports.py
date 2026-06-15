import importlib
import os


os.environ["FINSCIENTIST_SKIP_UI"] = "1"


def test_v122_modules_import_cleanly():
    module_names = [
        "app",
        "ui.product_ui",
        "ui.screening_ui",
        "ui.strategy_diagnostics_panel",
        "config.feature_flags",
        "config.stock_pools",
        "config.stock_names",
        "config.sector_mapping",
        "config.fundamental_samples",
        "data.market_data",
        "data.fundamental_data",
        "core.metrics",
        "core.scoring",
        "core.explanations",
        "core.sector_strength",
        "factor.factor_lab",
        "factor.factor_metrics",
        "factor.factor_report",
        "memory.research_memory",
        "strategy.adapter",
        "strategy.architecture_audit",
        "strategy.backtest",
        "strategy.backtest_diagnostics",
        "strategy.comparison",
        "strategy.composite_profile",
        "strategy.confluence",
        "strategy.event_confluence",
        "strategy.event_context",
        "strategy.event_diagnostics",
        "strategy.event_research_summary",
        "strategy.explanations",
        "strategy.export",
        "strategy.factors",
        "strategy.fundamental",
        "strategy.fundamental_diagnostics",
        "strategy.fundamental_relative",
        "strategy.filters",
        "strategy.report",
        "strategy.risk",
        "strategy.scoring",
        "strategy.service",
        "strategy.technical",
        "strategy.view_model",
        "strategy.presets",
        "strategy.preset_comparison",
        "strategy.priority_stability",
        "strategy.project_assessment",
        "strategy.preview",
        "strategy.research_pipeline_audit",
    ]

    for module_name in module_names:
        assert importlib.import_module(module_name)


def test_config_modules_no_longer_import_legacy_app():
    config_modules = [
        "config/stock_pools.py",
        "config/stock_names.py",
        "config/sector_mapping.py",
        "config/fundamental_samples.py",
    ]

    for module_path in config_modules:
        with open(module_path, encoding="utf-8") as file:
            assert "legacy_app" not in file.read()


def test_sector_strength_module_no_longer_imports_legacy_app():
    with open("core/sector_strength.py", encoding="utf-8") as file:
        assert "legacy_app" not in file.read()


def test_explanations_module_no_longer_imports_legacy_app():
    with open("core/explanations.py", encoding="utf-8") as file:
        assert "legacy_app" not in file.read()


def test_v150_entrypoints_keep_explicit_compatibility_boundary():
    app = importlib.import_module("app")
    legacy_app = importlib.import_module("legacy_app")
    screening_ui = importlib.import_module("ui.screening_ui")

    assert app.APP_VERSION == "v6.3.5"
    assert legacy_app.APP_VERSION == app.APP_VERSION
    assert callable(legacy_app.render_legacy_workbench)
    assert "render_screening_section" in legacy_app.LEGACY_COMPATIBILITY_SURFACE
    assert screening_ui.legacy_workbench is legacy_app


def test_strategy_modules_do_not_extend_legacy_app():
    with open("legacy_app.py", encoding="utf-8") as file:
        assert "strategy." not in file.read()
