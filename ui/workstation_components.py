"""Reusable components and safe data helpers for Research Workstation."""

from __future__ import annotations

import copy
import html
from typing import Any

import pandas as pd
import streamlit as st

from ui.workstation_theme import badge_html, risk_tone, status_tone


MISSING = "\u2014"


def safe_copy_frame(source: Any) -> pd.DataFrame:
    """Return a defensive DataFrame copy."""
    if source is None:
        return pd.DataFrame()
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    return pd.DataFrame()


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, dict, tuple, set)):
        return False
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def safe_get(row: Any, field: str, default: str = MISSING) -> Any:
    """Read a field safely from Series or dict."""
    if row is None:
        return default
    value = row.get(field, default) if hasattr(row, "get") else default
    if is_missing(value) or value == "":
        return default
    return value


def format_value(value: Any, field: str = "") -> str:
    """Format scalar, list, dict, and percentage fields for display."""
    if is_missing(value):
        return MISSING
    if isinstance(value, dict):
        return "\n".join(f"{key}: {format_value(item)}" for key, item in value.items()) or MISSING
    if isinstance(value, (list, tuple, set)):
        return "\n".join(f"- {item}" for item in value if not is_missing(item)) or MISSING
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if field in {"period_return", "annualized_return", "win_rate", "max_drawdown", "volatility"}:
            return f"{value * 100:.2f}%"
        return f"{value:.2f}"
    return str(value)


def render_metric_card(title: str, value: Any, caption: str = "") -> None:
    """Render a Bloomberg-style metric card."""
    st.markdown(
        f"""
<div class="fsw-card">
  <div class="fsw-metric-label">{html.escape(title)}</div>
  <div class="fsw-metric-value">{html.escape(format_value(value))}</div>
  <div class="fsw-muted">{html.escape(caption)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_quality_badge(value: Any) -> None:
    st.markdown(badge_html(format_value(value), status_tone(value)), unsafe_allow_html=True)


def render_status_badge(value: Any) -> None:
    st.markdown(badge_html(format_value(value), status_tone(value)), unsafe_allow_html=True)


def render_score_bar(label: str, value: Any, max_value: float = 100.0) -> None:
    """Render score with current value, max value, contribution ratio, and progress."""
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric):
        current = MISSING
        ratio = 0.0
    else:
        ratio = max(0.0, min(float(numeric) / max_value, 1.0))
        current = f"{float(numeric):.2f}"
    cols = st.columns([1.2, 3.0, 1.2])
    cols[0].metric(label, current)
    cols[1].progress(ratio)
    cols[2].caption(f"Max {max_value:.0f} | {ratio * 100:.1f}%")


def render_risk_card(title: str, value: Any, level: Any = None) -> None:
    """Render risk card using Low/Medium/High color rules."""
    tone = risk_tone(level if level is not None else value)
    st.markdown(
        f"""
<div class="fsw-card">
  <div class="fsw-metric-label">{html.escape(title)}</div>
  <div class="fsw-metric-value">{html.escape(format_value(value, title))}</div>
  {badge_html(format_value(level if level is not None else value), tone)}
</div>
""",
        unsafe_allow_html=True,
    )


def render_stock_card(row: pd.Series, selected: bool = False) -> None:
    """Render a compact navigator stock card."""
    ticker = format_value(safe_get(row, "ticker", safe_get(row, "symbol")))
    name = format_value(safe_get(row, "name", "Research Object"))
    score = format_value(safe_get(row, "selection_score"))
    level = format_value(safe_get(row, "selection_level"))
    border = "#58A6FF" if selected else "#30363D"
    st.markdown(
        f"""
<div class="fsw-card" style="border-color:{border};">
  <div class="fsw-stock-title">{html.escape(name)}</div>
  <div class="fsw-muted">{html.escape(ticker)}</div>
  <div class="fsw-meta">
    <span class="fsw-pill">Score {html.escape(score)}</span>
    <span class="fsw-pill">{html.escape(level)}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_report_block(report_text: str) -> None:
    st.markdown(f'<div class="fsw-report">{html.escape(report_text)}</div>', unsafe_allow_html=True)


def render_compare_table(table: pd.DataFrame) -> None:
    display = table.copy(deep=True)
    if display.empty:
        st.info("No comparable rows are available.")
        return
    st.dataframe(display.replace("", MISSING).fillna(MISSING), hide_index=True, use_container_width=True)


__all__ = [
    "MISSING",
    "format_value",
    "is_missing",
    "render_compare_table",
    "render_metric_card",
    "render_quality_badge",
    "render_report_block",
    "render_risk_card",
    "render_score_bar",
    "render_status_badge",
    "render_stock_card",
    "safe_copy_frame",
    "safe_get",
]
