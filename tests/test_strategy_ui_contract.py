from pathlib import Path

from config.feature_flags import get_feature_flag_metadata, is_strategy_diagnostics_enabled


FORBIDDEN_UI_CONTRACT_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_UI_CONTRACT_WORDS:
        assert word not in text


def test_strategy_diagnostics_ui_contract_is_not_rendered_by_default():
    screening_ui = read_text("ui/screening_ui.py")
    legacy_app = read_text("legacy_app.py")

    assert is_strategy_diagnostics_enabled() is False
    assert "strategy.view_model" not in screening_ui
    assert "strategy.service" not in screening_ui
    assert "build_strategy_view_model" not in screening_ui
    assert "build_strategy_service_output" not in screening_ui
    assert "strategy.view_model" not in legacy_app
    assert "strategy.service" not in legacy_app


def test_strategy_ui_contract_metadata_preserves_existing_flow():
    metadata = get_feature_flag_metadata()

    assert metadata["ui_rendering_enabled"] is False
    assert metadata["ranking_changed"] is False
    assert metadata["scoring_changed"] is False
    assert metadata["read_only"] is True
    assert_no_forbidden_words(metadata)
