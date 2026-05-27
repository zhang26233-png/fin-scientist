import importlib
import os


os.environ["FINSCIENTIST_SKIP_UI"] = "1"


def test_v121_modules_import_cleanly():
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

