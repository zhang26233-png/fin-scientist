import importlib
import os


os.environ["FINSCIENTIST_SKIP_UI"] = "1"


def test_v122_modules_import_cleanly():
    module_names = [
        "app",
        "ui.screening_ui",
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
