"""Read-only research report builder for the Research Terminal."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ui.terminal_components import collect_warning_fields, format_terminal_value, get_identity, is_missing


REPORT_BOUNDARY_TEXT = "本报告仅用于学习和研究，不构成投资建议。"
RESTRICTED_REPORT_TERMS = ["买入", "卖出", "目标价", "仓位建议"]


def _as_lines(value: Any) -> list[str]:
    if is_missing(value):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if not is_missing(item) and str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if not is_missing(item) and str(item)]
    if isinstance(value, set):
        return [str(item) for item in sorted(value) if not is_missing(item) and str(item)]
    return [str(value)] if str(value) else []


def _bullet_section(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def _sanitize_report_text(text: str) -> str:
    cleaned = text
    replacements = {
        "买入": "纳入研究观察",
        "卖出": "移出研究观察",
        "目标价": "后续估值观察点",
        "仓位建议": "风险暴露观察",
    }
    for term, replacement in replacements.items():
        cleaned = cleaned.replace(term, replacement)
    return cleaned


def build_stock_research_report(row: pd.Series | dict[str, Any]) -> str:
    """Build a neutral single-stock research report from existing row fields."""
    source = pd.Series(row).copy(deep=True)
    ticker, name = get_identity(source)
    title = " ".join(part for part in [ticker, name] if part).strip() or "研究对象"

    strengths = _as_lines(source.get("selection_strengths")) or _as_lines(source.get("selection_reasons"))
    risks = (
        _as_lines(source.get("selection_risks"))
        + _as_lines(source.get("selection_risk_notes"))
        + _as_lines(source.get("candidate_risk_flags"))
    )
    warnings = collect_warning_fields(source)

    score_lines = []
    for field in ["fundamental_score", "technical_score", "composite_score", "risk_score", "selection_score"]:
        score_lines.append(f"- {field}: {format_terminal_value(source.get(field), field) or '暂无可展示数据'}")

    history_lines = []
    for field in [
        "period_return",
        "annualized_return",
        "volatility",
        "max_drawdown",
        "win_rate",
        "return_risk_ratio",
        "performance_label",
        "backtest_quality_label",
    ]:
        history_lines.append(f"- {field}: {format_terminal_value(source.get(field), field) or '暂无可展示数据'}")

    follow_up = [
        "继续核对数据完整性与异常字段。",
        "观察基本面、技术面与历史表现之间是否存在冲突。",
        "跟踪风险等级、回撤和波动变化是否影响研究优先级。",
    ]

    report = f"""# {title} 研究报告预览

{REPORT_BOUNDARY_TEXT}

一、研究摘要
- 研究分组：{format_terminal_value(source.get("selection_bucket")) or format_terminal_value(source.get("candidate_pool")) or "暂无可展示数据"}
- 研究排序：{format_terminal_value(source.get("selection_rank")) or "暂无可展示数据"}
- 研究摘要：{format_terminal_value(source.get("selection_summary")) or "暂无可展示摘要"}

二、核心逻辑
{_bullet_section(strengths, "当前缺少可展示的核心逻辑字段。")}

三、评分拆解
{chr(10).join(score_lines)}

四、历史表现
{chr(10).join(history_lines)}

五、风险提示
{_bullet_section(risks, "当前缺少可展示的风险字段，仍需结合数据质量继续观察。")}

六、数据质量说明
{_bullet_section(warnings, "当前未汇总到明显的数据质量提示。")}

七、后续观察问题
{_bullet_section(follow_up, "继续补充研究证据。")}
"""
    return _sanitize_report_text(report)


__all__ = [
    "REPORT_BOUNDARY_TEXT",
    "RESTRICTED_REPORT_TERMS",
    "build_stock_research_report",
]
