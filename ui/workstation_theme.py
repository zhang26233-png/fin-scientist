"""Bloomberg-style dark theme helpers for the Research Workstation."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st


WORKSTATION_VERSION = "v6.0.0"
WORKSTATION_STAGE = "Factor Research Lab"


def get_workstation_css() -> str:
    """Return shared CSS for the Research Workstation."""
    return """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #0E1117;
    color: #E6EDF3;
    font-family: "Segoe UI", sans-serif;
}
.fsw-header {
    position: sticky;
    top: 0;
    z-index: 50;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
    background: rgba(14, 17, 23, 0.96);
}
.fsw-title {
    color: #58A6FF;
    font-size: 1.45rem;
    font-weight: 750;
}
.fsw-subtitle {
    color: #E6EDF3;
    font-size: 0.96rem;
    margin-top: 2px;
}
.fsw-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}
.fsw-pill, .fsw-badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    border: 1px solid #30363D;
    background: #161B22;
    color: #C9D1D9;
    padding: 4px 10px;
    font-size: 0.78rem;
    font-weight: 650;
}
.fsw-card {
    border: 1px solid #30363D;
    border-radius: 8px;
    background: #161B22;
    padding: 14px;
    margin-bottom: 12px;
}
.fsw-section {
    color: #58A6FF;
    font-size: 1.02rem;
    font-weight: 750;
    margin: 12px 0 8px 0;
}
.fsw-muted {
    color: #8B949E;
    font-size: 0.82rem;
}
.fsw-metric-label {
    color: #8B949E;
    font-size: 0.78rem;
}
.fsw-metric-value {
    color: #E6EDF3;
    font-size: 1.45rem;
    font-weight: 800;
}
.fsw-stock-title {
    color: #E6EDF3;
    font-size: 1.24rem;
    font-weight: 800;
}
.fsw-divider {
    border-top: 1px solid #30363D;
    margin: 12px 0;
}
.fsw-report {
    border: 1px solid #30363D;
    border-radius: 8px;
    background: #0E1117;
    padding: 14px;
    white-space: pre-wrap;
    line-height: 1.55;
    font-size: 0.88rem;
}
</style>
"""


def badge_html(label: Any, tone: str = "neutral") -> str:
    """Return a dark-terminal badge."""
    colors = {
        "good": ("#003B1F", "#00C853", "#B9F6CA"),
        "watch": ("#3D3300", "#FFD54F", "#FFF8E1"),
        "risk": ("#3B0A0A", "#FF5252", "#FFCDD2"),
        "info": ("#071D33", "#58A6FF", "#D2E9FF"),
        "neutral": ("#161B22", "#30363D", "#C9D1D9"),
    }
    background, border, color = colors.get(tone, colors["neutral"])
    safe_label = html.escape(str(label or "Unavailable"))
    return (
        f'<span class="fsw-badge" style="background:{background};'
        f'border-color:{border};color:{color};">{safe_label}</span>'
    )


def risk_tone(value: Any) -> str:
    label = str(value or "Unavailable")
    if label == "Low":
        return "good"
    if label == "Medium":
        return "watch"
    if label == "High":
        return "risk"
    return "neutral"


def status_tone(value: Any) -> str:
    label = str(value or "Unavailable")
    if label in {"Core", "Selected", "Available", "Completed", "Good", "Strong"}:
        return "good"
    if label in {"Watch", "Medium", "Normal", "Incomplete"}:
        return "watch"
    if label in {"High", "Exclude", "Excluded", "Low", "Weak", "Poor"}:
        return "risk"
    return "neutral"


def render_workstation_header(
    current_object: str,
    updated_at: str,
    candidate_count: int,
    core_count: int,
    watch_count: int,
    average_score: str,
) -> None:
    """Render the sticky Research Workstation header."""
    st.markdown(
        f"""
<div class="fsw-header">
  <div class="fsw-title">Fin-Scientist</div>
  <div class="fsw-subtitle">Research Workstation</div>
  <div class="fsw-meta">
    <span class="fsw-pill">Current: {html.escape(current_object)}</span>
    <span class="fsw-pill">Updated: {html.escape(updated_at)}</span>
    <span class="fsw-pill">Candidates: {candidate_count}</span>
    <span class="fsw-pill">CORE: {core_count}</span>
    <span class="fsw-pill">WATCH: {watch_count}</span>
    <span class="fsw-pill">Average Score: {html.escape(average_score)}</span>
    <span class="fsw-pill">Research only</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_workstation_section(title: str, caption: str = "") -> None:
    """Render a workstation section title."""
    st.markdown(f'<div class="fsw-section">{html.escape(title)}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="fsw-muted">{html.escape(caption)}</div>', unsafe_allow_html=True)


__all__ = [
    "WORKSTATION_STAGE",
    "WORKSTATION_VERSION",
    "badge_html",
    "get_workstation_css",
    "render_workstation_header",
    "render_workstation_section",
    "risk_tone",
    "status_tone",
]
