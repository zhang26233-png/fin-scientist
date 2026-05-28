"""Feature-flagged strategy diagnostics panel helper.

This module is intentionally not imported by the current screening page. The
render helper is default-off through config.feature_flags and returns before
calling Streamlit when diagnostics rendering is disabled.
"""

import copy

from config.feature_flags import get_feature_flag_metadata, is_strategy_diagnostics_enabled


def _as_dict(value):
    return value if isinstance(value, dict) else {}


def _as_list(value):
    return value if isinstance(value, list) else []


def _safe_text(value):
    return str(value).strip() if value is not None else ""


def _render_enabled_panel(view_model, st_module):
    cards = _as_list(view_model.get("cards"))
    badges = _as_list(view_model.get("badges"))
    sections = _as_list(view_model.get("sections"))
    table_rows = _as_list(view_model.get("table_rows"))
    empty_state = _as_dict(view_model.get("empty_state"))

    st_module.subheader("策略诊断")
    if empty_state.get("is_empty"):
        st_module.info(_safe_text(empty_state.get("message")) or "暂无可展示的内部策略诊断结果。")
    for card in cards:
        card = _as_dict(card)
        st_module.caption(f"{_safe_text(card.get('title'))}: {_safe_text(card.get('value'))}")
    if badges:
        st_module.caption("；".join(_safe_text(_as_dict(item).get("label")) for item in badges if _safe_text(_as_dict(item).get("label"))))
    for section in sections:
        section = _as_dict(section)
        st_module.write(f"**{_safe_text(section.get('title'))}**")
        st_module.write(_safe_text(section.get("body")))
    if table_rows:
        st_module.dataframe(table_rows, hide_index=True, use_container_width=True)


def render_strategy_diagnostics_panel(view_model, st_module=None):
    """Render future strategy diagnostics only when the feature flag is enabled."""
    metadata = get_feature_flag_metadata()
    if not is_strategy_diagnostics_enabled():
        return {
            "rendered": False,
            "reason": "strategy diagnostics feature flag is disabled",
            "metadata": metadata,
        }

    snapshot = copy.deepcopy(view_model) if isinstance(view_model, dict) else {}
    if st_module is None:
        return {
            "rendered": False,
            "reason": "streamlit module is not provided",
            "metadata": metadata,
        }

    _render_enabled_panel(snapshot, st_module)
    return {
        "rendered": True,
        "reason": "",
        "metadata": metadata,
    }


__all__ = [
    "render_strategy_diagnostics_panel",
]
