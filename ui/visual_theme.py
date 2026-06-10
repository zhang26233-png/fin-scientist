"""Visual theme helpers for the Research Terminal."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st


TERMINAL_TITLE = "Fin-Scientist"
TERMINAL_SUBTITLE = "Research Intelligence Terminal"


def get_terminal_css() -> str:
    """Return the shared CSS used by the visual Research Terminal."""
    return """
<style>
.fs-terminal-header {
    border: 1px solid rgba(148, 163, 184, 0.26);
    border-radius: 8px;
    padding: 22px 24px;
    margin-bottom: 18px;
    background:
        linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(17, 24, 39, 0.78)),
        linear-gradient(90deg, rgba(45, 212, 191, 0.14), rgba(250, 204, 21, 0.08));
}
.fs-terminal-kicker {
    color: #7dd3fc;
    font-size: 0.78rem;
    letter-spacing: 0;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.fs-terminal-title {
    color: #f8fafc;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.15;
}
.fs-terminal-subtitle {
    color: #cbd5e1;
    font-size: 1rem;
    margin-top: 6px;
    max-width: 880px;
}
.fs-terminal-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}
.fs-pill, .fs-badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 0.78rem;
    font-weight: 650;
    border: 1px solid rgba(148, 163, 184, 0.24);
    color: #e5e7eb;
    background: rgba(15, 23, 42, 0.72);
}
.fs-section-title {
    margin: 18px 0 10px 0;
    color: #f8fafc;
    font-size: 1.16rem;
    font-weight: 700;
}
.fs-section-caption {
    margin-top: -4px;
    margin-bottom: 12px;
    color: #94a3b8;
    font-size: 0.86rem;
}
.fs-card {
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 8px;
    padding: 16px;
    background: rgba(15, 23, 42, 0.58);
    margin-bottom: 12px;
}
.fs-metric-label {
    color: #94a3b8;
    font-size: 0.78rem;
    margin-bottom: 6px;
}
.fs-metric-value {
    color: #f8fafc;
    font-size: 1.55rem;
    font-weight: 750;
    line-height: 1.2;
}
.fs-metric-help {
    color: #cbd5e1;
    font-size: 0.8rem;
    margin-top: 6px;
}
.fs-stock-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
}
.fs-stock-title {
    color: #f8fafc;
    font-size: 1.1rem;
    font-weight: 750;
}
.fs-stock-subtitle {
    color: #94a3b8;
    font-size: 0.82rem;
    margin-top: 3px;
}
.fs-card-summary {
    color: #d1d5db;
    font-size: 0.9rem;
    margin: 12px 0;
}
.fs-two-col {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}
.fs-list-title {
    color: #e5e7eb;
    font-weight: 700;
    font-size: 0.86rem;
    margin-bottom: 6px;
}
.fs-muted {
    color: #94a3b8;
}
.fs-warning-box {
    border: 1px solid rgba(251, 191, 36, 0.36);
    border-radius: 8px;
    padding: 12px;
    background: rgba(120, 53, 15, 0.2);
    color: #fde68a;
    margin-bottom: 10px;
}
.fs-report {
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 8px;
    padding: 18px;
    background: rgba(2, 6, 23, 0.42);
    white-space: pre-wrap;
    line-height: 1.62;
    color: #e5e7eb;
    font-size: 0.92rem;
}
.fs-score-row {
    margin-bottom: 12px;
}
.fs-score-label {
    color: #cbd5e1;
    font-size: 0.84rem;
    margin-bottom: 4px;
}
</style>
"""


def _badge_html(label: Any, tone: str) -> str:
    colors = {
        "good": ("#052e2b", "#2dd4bf", "#99f6e4"),
        "warn": ("#451a03", "#f59e0b", "#fde68a"),
        "bad": ("#450a0a", "#ef4444", "#fecaca"),
        "neutral": ("#111827", "#94a3b8", "#e5e7eb"),
        "info": ("#082f49", "#38bdf8", "#bae6fd"),
    }
    background, border, text = colors.get(tone, colors["neutral"])
    safe_label = html.escape(str(label or "Unavailable"))
    return (
        f'<span class="fs-badge" style="background:{background};'
        f'border-color:{border};color:{text};">{safe_label}</span>'
    )


def get_score_badge(value: Any) -> str:
    """Return a score badge for High / Medium / Low / Unavailable values."""
    label = str(value or "Unavailable")
    if label == "High":
        return _badge_html(label, "good")
    if label == "Medium":
        return _badge_html(label, "warn")
    if label == "Low":
        return _badge_html(label, "bad")
    return _badge_html(label, "neutral")


def get_risk_badge(value: Any) -> str:
    """Return a risk badge for High / Medium / Low / Unavailable values."""
    label = str(value or "Unavailable")
    if label == "High":
        return _badge_html(label, "bad")
    if label == "Medium":
        return _badge_html(label, "warn")
    if label == "Low":
        return _badge_html(label, "good")
    return _badge_html(label, "neutral")


def get_status_badge(value: Any) -> str:
    """Return a status badge for available, incomplete, and unavailable states."""
    label = str(value or "Unavailable")
    if label in {"Available", "Selected", "Core", "Good", "Strong"}:
        return _badge_html(label, "good")
    if label in {"Watch", "Incomplete", "Normal"}:
        return _badge_html(label, "warn")
    if label in {"High", "Excluded", "Exclude", "Poor", "Weak"}:
        return _badge_html(label, "bad")
    return _badge_html(label, "neutral")


def render_terminal_header(version: str, stage: str, description: str = "") -> None:
    """Render the terminal-style top header."""
    safe_version = html.escape(str(version))
    safe_stage = html.escape(str(stage))
    safe_description = html.escape(
        description
        or "只读研究终端，用于观察结果、风险、数据质量和报告预览；所有内容仅供学习和研究。"
    )
    st.markdown(
        f"""
<div class="fs-terminal-header">
  <div class="fs-terminal-kicker">Personal Financial Research Workbench</div>
  <div class="fs-terminal-title">{TERMINAL_TITLE}</div>
  <div class="fs-terminal-subtitle">{TERMINAL_SUBTITLE}</div>
  <div class="fs-terminal-subtitle">{safe_description}</div>
  <div class="fs-terminal-meta">
    <span class="fs-pill">当前版本 {safe_version}</span>
    <span class="fs-pill">当前阶段 {safe_stage}</span>
    <span class="fs-pill">不构成投资建议</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_section_title(title: str, caption: str = "") -> None:
    """Render a consistent section title and optional caption."""
    st.markdown(f'<div class="fs-section-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="fs-section-caption">{html.escape(caption)}</div>', unsafe_allow_html=True)


__all__ = [
    "TERMINAL_SUBTITLE",
    "TERMINAL_TITLE",
    "get_risk_badge",
    "get_score_badge",
    "get_status_badge",
    "get_terminal_css",
    "render_section_title",
    "render_terminal_header",
]
