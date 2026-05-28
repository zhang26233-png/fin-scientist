"""Feature flags for optional FinScientist capabilities.

All flags are conservative by default. V1.3.5 defines the strategy diagnostics
UI boundary but does not enable rendering or connect it to the Streamlit pages.
"""

STRATEGY_DIAGNOSTICS_ENABLED = False
STRATEGY_DIAGNOSTICS_UI_RENDERING_ENABLED = False
STRATEGY_DIAGNOSTICS_RANKING_CHANGED = False
STRATEGY_DIAGNOSTICS_SCORING_CHANGED = False


def is_strategy_diagnostics_enabled():
    return bool(STRATEGY_DIAGNOSTICS_ENABLED and STRATEGY_DIAGNOSTICS_UI_RENDERING_ENABLED)


def get_feature_flag_metadata():
    return {
        "strategy_diagnostics_enabled": STRATEGY_DIAGNOSTICS_ENABLED,
        "ui_rendering_enabled": STRATEGY_DIAGNOSTICS_UI_RENDERING_ENABLED,
        "ranking_changed": STRATEGY_DIAGNOSTICS_RANKING_CHANGED,
        "scoring_changed": STRATEGY_DIAGNOSTICS_SCORING_CHANGED,
        "read_only": True,
    }


__all__ = [
    "get_feature_flag_metadata",
    "is_strategy_diagnostics_enabled",
]
