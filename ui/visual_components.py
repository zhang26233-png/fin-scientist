"""Visual Streamlit components for the Research Terminal redesign."""

from __future__ import annotations

import html
from typing import Any

import pandas as pd
import streamlit as st

from ui.visual_theme import get_risk_badge, get_score_badge, get_status_badge


def _safe_text(value: Any, fallback: str = "—") -> str:
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass
    text = str(value)
    return text if text else fallback


def _list_html(items: Any, prefix: str, fallback: str) -> str:
    if isinstance(items, str):
        values = [items] if items else []
    elif isinstance(items, (list, tuple, set)):
        values = [str(item) for item in items if _safe_text(item, "")] 
    else:
        values = []
    if not values:
        return f'<div class="fs-muted">{html.escape(fallback)}</div>'
    return "".join(f"<div>{html.escape(prefix)} {html.escape(item)}</div>" for item in values)


def render_metric_card(title: str, value: Any, help_text: str = "") -> None:
    """Render a compact dashboard metric card."""
    st.markdown(
        f"""
<div class="fs-card">
  <div class="fs-metric-label">{html.escape(title)}</div>
  <div class="fs-metric-value">{html.escape(_safe_text(value))}</div>
  <div class="fs-metric-help">{html.escape(help_text)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_stock_card(row: pd.Series, format_value) -> None:
    """Render a Top Picks stock card from one row."""
    ticker = _safe_text(row.get("ticker", row.get("symbol")))
    name = _safe_text(row.get("name"), "")
    title = " ".join(part for part in [ticker, name] if part and part != "—")
    summary = format_value(row.get("selection_summary")) or "暂无可展示摘要。"
    strengths = row.get("selection_strengths")
    risks = row.get("selection_risks")
    data_quality = row.get("explain_warnings") or row.get("selection_warnings")
    st.markdown(
        f"""
<div class="fs-card">
  <div class="fs-stock-head">
    <div>
      <div class="fs-stock-title">{html.escape(title or "研究对象")}</div>
      <div class="fs-stock-subtitle">Rank {html.escape(format_value(row.get("selection_rank")) or "—")}</div>
    </div>
    <div>{get_status_badge(row.get("selection_bucket"))}</div>
  </div>
  <div class="fs-terminal-meta">
    <span class="fs-pill">selection_score {html.escape(format_value(row.get("selection_score")) or "—")}</span>
    <span class="fs-pill">thesis {html.escape(format_value(row.get("selection_thesis")) or "—")}</span>
  </div>
  <div class="fs-card-summary">{html.escape(summary)}</div>
  <div class="fs-two-col">
    <div>
      <div class="fs-list-title">✓ 优势</div>
      {_list_html(strengths, "✓", "暂无可展示优势。")}
    </div>
    <div>
      <div class="fs-list-title">⚠ 风险提示</div>
      {_list_html(risks, "⚠", "暂无可展示风险。")}
    </div>
  </div>
  <div class="fs-card-summary"><strong>Data Quality</strong><br>{html.escape(format_value(data_quality) or "当前未汇总到明显的数据质量提示。")}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_score_bar(label: str, value: Any, badge_html: str = "") -> None:
    """Render a score row with metric, badge, and progress bar."""
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    display = "—" if pd.isna(numeric) else f"{float(numeric):.2f}"
    st.markdown(
        f'<div class="fs-score-row"><div class="fs-score-label">{html.escape(label)} {badge_html}</div></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns([1, 3])
    cols[0].metric(label, display)
    if pd.isna(numeric):
        cols[1].caption("暂无可展示数据")
    else:
        cols[1].progress(max(0.0, min(float(numeric) / 100.0, 1.0)))


def render_risk_badge(value: Any) -> None:
    """Render a risk badge."""
    st.markdown(get_risk_badge(value), unsafe_allow_html=True)


def render_quality_badge(value: Any) -> None:
    """Render a quality or status badge."""
    st.markdown(get_status_badge(value), unsafe_allow_html=True)


def render_warning_box(messages: list[str] | str) -> None:
    """Render warning and data-quality messages."""
    if isinstance(messages, str):
        values = [messages] if messages else []
    else:
        values = [str(message) for message in messages if str(message)]
    content = "<br>".join(html.escape(message) for message in values) if values else "当前未汇总到明显的数据质量提示。"
    st.markdown(f'<div class="fs-warning-box">{content}</div>', unsafe_allow_html=True)


def render_report_block(report_text: str) -> None:
    """Render a report-style preview block."""
    st.markdown(f'<div class="fs-report">{html.escape(report_text)}</div>', unsafe_allow_html=True)


def render_compare_table(table: pd.DataFrame) -> None:
    """Render the comparison table with terminal-safe missing values."""
    display = table.copy(deep=True)
    if display.empty:
        st.info("当前没有可展示的对比字段。")
        return
    display = display.replace("", "—").fillna("—")
    st.dataframe(display, hide_index=True, use_container_width=True)


__all__ = [
    "render_compare_table",
    "render_metric_card",
    "render_quality_badge",
    "render_report_block",
    "render_risk_badge",
    "render_score_bar",
    "render_stock_card",
    "render_warning_box",
]
