"""Read-only research report builder for the Research Terminal."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ui.terminal_components import collect_warning_fields, format_terminal_value, get_identity, is_missing


REPORT_BOUNDARY_TEXT = "本报告仅用于学习和研究，不构成投资建议。"
RESTRICTED_REPORT_TERMS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u76ee\u6807\u4ef7",
    "\u4ed3\u4f4d\u5efa\u8bae",
    "\u6536\u76ca\u627f\u8bfa",
]


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
    replacements = {
        "\u4e70\u5165": "纳入研究观察",
        "\u5356\u51fa": "移出研究观察",
        "\u76ee\u6807\u4ef7": "估值观察点",
        "\u4ed3\u4f4d\u5efa\u8bae": "风险暴露观察",
        "\u6536\u76ca\u627f\u8bfa": "历史表现说明",
    }
    cleaned = text
    for term, replacement in replacements.items():
        cleaned = cleaned.replace(term, replacement)
    return cleaned


def build_stock_research_report(row: pd.Series | dict[str, Any]) -> str:
    """Build a neutral single-stock research report from existing row fields."""
    source = pd.Series(row).copy(deep=True)
    ticker, name = get_identity(source)
    title = " ".join(part for part in [ticker, name] if part and part != "—").strip() or "研究对象"

    strengths = _as_lines(source.get("selection_strengths")) or _as_lines(source.get("selection_reasons"))
    risks = (
        _as_lines(source.get("selection_risks"))
        + _as_lines(source.get("selection_risk_notes"))
        + _as_lines(source.get("candidate_risk_flags"))
    )
    warnings = collect_warning_fields(source)

    score_lines = []
    for field in ["fundamental_score", "technical_score", "composite_score", "risk_score", "selection_score"]:
        score_lines.append(f"- {field}: {format_terminal_value(source.get(field), field)}")

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
        history_lines.append(f"- {field}: {format_terminal_value(source.get(field), field)}")

    follow_up = [
        "继续核对数据完整性与异常字段。",
        "观察基本面、技术面与历史表现之间是否存在冲突。",
        "跟踪风险等级、回撤和波动变化是否影响研究优先级。",
    ]

    report = f"""# {title} 研究报告预览

{REPORT_BOUNDARY_TEXT}

一、研究摘要
- 研究分组：{format_terminal_value(source.get("selection_bucket"))}
- 研究排序：{format_terminal_value(source.get("selection_rank"))}
- 核心摘要：{format_terminal_value(source.get("selection_summary"))}

二、核心逻辑
{_bullet_section(strengths, "当前缺少可展示的核心逻辑字段。")}

三、评分拆解
{chr(10).join(score_lines)}

四、历史表现
{chr(10).join(history_lines)}

五、风险提示
{_bullet_section(risks, "当前缺少可展示的风险字段，仍需结合数据质量继续观察。")}

六、数据质量
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
