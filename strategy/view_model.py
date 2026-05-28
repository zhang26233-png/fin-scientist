"""Read-only view-model builder for future strategy UI surfaces."""

import copy


def _as_dict(value):
    return value if isinstance(value, dict) else {}


def _as_list(value):
    return value if isinstance(value, list) else []


def _safe_text(value):
    return str(value).strip() if value is not None else ""


def _card(title, value, detail=""):
    return {
        "title": title,
        "value": value,
        "detail": detail,
    }


def _badge(label, kind="neutral", detail=""):
    return {
        "label": label,
        "kind": kind,
        "detail": detail,
    }


def _build_cards(service_output):
    report = _as_dict(service_output.get("report"))
    metadata = _as_dict(service_output.get("metadata"))
    diagnostics = _as_list(service_output.get("diagnostics"))
    warnings = _as_list(service_output.get("warnings"))
    return [
        _card("诊断状态", _safe_text(service_output.get("status")) or "unknown", "内部只读策略诊断状态。"),
        _card("策略预设", _safe_text(service_output.get("preset_name")) or "未命名预设", "当前内部诊断使用的预设名称。"),
        _card("候选对象数量", metadata.get("diagnostic_count", len(diagnostics)), "已生成策略诊断的候选对象数量。"),
        _card("风险提示数量", len(warnings), report.get("risk_summary", "")),
    ]


def _build_badges(service_output):
    badges = []
    status = _safe_text(service_output.get("status")) or "unknown"
    kind = "success" if status == "ok" else "warning" if status == "warning" else "neutral"
    badges.append(_badge(f"状态：{status}", kind=kind))

    metadata = _as_dict(service_output.get("metadata"))
    badges.append(_badge("只读", kind="neutral" if metadata.get("read_only") else "warning"))
    badges.append(_badge("未接入页面", kind="neutral" if metadata.get("ui_connected") is False else "warning"))
    badges.append(_badge("排序未改变", kind="neutral" if metadata.get("ranking_changed") is False else "warning"))
    badges.append(_badge("评分未改变", kind="neutral" if metadata.get("scoring_changed") is False else "warning"))

    for item in _as_list(service_output.get("diagnostics")):
        for risk in _as_list(_as_dict(item).get("risk_tags")):
            risk = _as_dict(risk)
            label = _safe_text(risk.get("tag"))
            if label:
                badges.append(_badge(label, kind="risk", detail=_safe_text(risk.get("message"))))
    return badges


def _build_sections(service_output):
    report = _as_dict(service_output.get("report"))
    warnings = _as_list(service_output.get("warnings"))
    return [
        {
            "title": "诊断摘要",
            "body": _safe_text(report.get("summary_text")) or "暂无可展示的诊断摘要。",
        },
        {
            "title": "因子观察",
            "body": _safe_text(report.get("factor_summary")) or "暂无可展示的因子观察。",
        },
        {
            "title": "过滤提示",
            "body": _safe_text(report.get("filter_summary")) or "暂无可展示的过滤提示。",
        },
        {
            "title": "风险提示",
            "body": _safe_text(report.get("risk_summary")) or "暂无可展示的风险提示。",
        },
        {
            "title": "数据质量",
            "body": _safe_text(report.get("data_quality_summary")) or "暂无可展示的数据质量提示。",
        },
        {
            "title": "内部警告",
            "body": "；".join(str(item) for item in warnings) if warnings else "暂无内部警告。",
        },
    ]


def _factor_brief(factor_scores):
    if not isinstance(factor_scores, dict) or not factor_scores:
        return "暂无因子结果"
    parts = []
    for name, result in factor_scores.items():
        result = _as_dict(result)
        parts.append(f"{name}:{result.get('score', '无法计算')}")
    return "；".join(parts)


def _risk_brief(risk_tags):
    labels = [_safe_text(_as_dict(item).get("tag")) for item in _as_list(risk_tags)]
    labels = [label for label in labels if label]
    return "、".join(labels) if labels else "暂无主要标签"


def _build_table_rows(service_output):
    rows = []
    for item in _as_list(service_output.get("diagnostics")):
        item = _as_dict(item)
        identity = _as_dict(item.get("identity"))
        filter_flags = _as_dict(item.get("filter_flags"))
        rows.append(
            {
                "symbol": _safe_text(identity.get("symbol")),
                "name": _safe_text(identity.get("name")),
                "sector": _safe_text(identity.get("sector")),
                "industry": _safe_text(identity.get("industry")),
                "factor_brief": _factor_brief(item.get("factor_scores")),
                "filter_passed": filter_flags.get("passed"),
                "risk_brief": _risk_brief(item.get("risk_tags")),
                "summary": _safe_text(item.get("diagnostics_summary")),
            }
        )
    return rows


def _build_empty_state(service_output, table_rows):
    if table_rows:
        return {
            "is_empty": False,
            "title": "",
            "message": "",
        }
    status = _safe_text(service_output.get("status")) or "empty"
    return {
        "is_empty": True,
        "title": "暂无策略诊断",
        "message": f"当前状态为 {status}，尚无可展示的内部策略诊断结果。",
    }


def build_strategy_view_model(service_output):
    """Build a UI-friendly read-only structure from strategy service output."""
    snapshot = copy.deepcopy(service_output) if isinstance(service_output, dict) else {}
    table_rows = _build_table_rows(snapshot)
    metadata = dict(_as_dict(snapshot.get("metadata")))
    metadata.update(
        {
            "read_only": metadata.get("read_only", True),
            "ui_connected": metadata.get("ui_connected", False),
            "ranking_changed": metadata.get("ranking_changed", False),
            "scoring_changed": metadata.get("scoring_changed", False),
            "view_model_only": True,
        }
    )
    return {
        "cards": _build_cards(snapshot),
        "badges": _build_badges(snapshot),
        "sections": _build_sections(snapshot),
        "table_rows": table_rows,
        "empty_state": _build_empty_state(snapshot, table_rows),
        "metadata": metadata,
    }


__all__ = [
    "build_strategy_view_model",
]
