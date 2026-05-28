from config.feature_flags import get_feature_flag_metadata, is_strategy_diagnostics_enabled


FORBIDDEN_FEATURE_FLAG_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_FEATURE_FLAG_WORDS:
        assert word not in text


def test_strategy_diagnostics_feature_flag_defaults_off():
    metadata = get_feature_flag_metadata()

    assert is_strategy_diagnostics_enabled() is False
    assert metadata == {
        "strategy_diagnostics_enabled": False,
        "ui_rendering_enabled": False,
        "ranking_changed": False,
        "scoring_changed": False,
        "read_only": True,
    }
    assert_no_forbidden_words(metadata)
