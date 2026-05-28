"""Read-only explanations for internal strategy risk and data-quality outputs."""

import copy
import math


RISK_EXPLANATION_MAP = {
    "high_volatility": {
        "title": "高波动观察",
        "message": "短期波动较高，研究时需关注价格波动风险。",
        "severity": "medium",
    },
    "extreme_upside_return": {
        "title": "短期涨幅过热观察",
        "message": "短期涨幅较大，可能存在过热或回撤压力。",
        "severity": "medium",
    },
    "volume_downside_risk": {
        "title": "放量下跌观察",
        "message": "放量下跌，说明下跌过程伴随成交活跃。",
        "severity": "medium",
    },
    "overheated_turnover": {
        "title": "换手过热观察",
        "message": "换手率偏高，短线交易拥挤度可能较高。",
        "severity": "medium",
    },
    "low_liquidity": {
        "title": "低流动性观察",
        "message": "成交额、成交量或换手率偏低，流动性不足。",
        "severity": "medium",
    },
    "insufficient_factor_data": {
        "title": "因子数据不足",
        "message": "部分因子数据不足，研究时需先核验字段完整性。",
        "severity": "low",
    },
    "missing_volume_fields": {
        "title": "量能字段不足",
        "message": "量能相关字段不足，流动性和量价观察不完整。",
        "severity": "low",
    },
    "routine_review": {
        "title": "常规核验",
        "message": "未触发主要风险阈值，仍需结合原始数据继续研究。",
        "severity": "info",
    },
}

DATA_QUALITY_EXPLANATION_MAP = {
    "missing_price_fields": {
        "title": "价格字段缺失",
        "message": "价格字段缺失或不可识别，趋势和收益观察不完整。",
        "severity": "medium",
    },
    "missing_volume_fields": {
        "title": "量能字段缺失",
        "message": "成交量或成交额字段缺失，量价和流动性观察不完整。",
        "severity": "medium",
    },
    "missing_turnover_fields": {
        "title": "换手字段缺失",
        "message": "换手率字段缺失，无法完整识别换手活跃度。",
        "severity": "low",
    },
    "invalid_numeric_fields": {
        "title": "数值字段异常",
        "message": "存在空值、非数值或非有限数值，需核验数据口径。",
        "severity": "medium",
    },
    "insufficient_factor_data": {
        "title": "因子数据不足",
        "message": "部分因子因字段或样本不足无法计算。",
        "severity": "low",
    },
}

def _as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _safe_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0
    if not math.isfinite(number):
        return 0
    return max(0, int(round(number)))


def _extract_score_rows(source):
    if isinstance(source, dict):
        if isinstance(source.get("scores"), list):
            return copy.deepcopy(source["scores"])
        return [copy.deepcopy(source)]
    if isinstance(source, list):
        return copy.deepcopy(source)
    return []


def _extract_labels(row, label_key, tags_key=None):
    labels = []
    if isinstance(row, dict):
        labels.extend(str(label) for label in _as_list(row.get(label_key)) if label)
        if tags_key:
            for tag in _as_list(row.get(tags_key)):
                if isinstance(tag, dict) and tag.get("code"):
                    labels.append(str(tag["code"]))
    return sorted(set(labels))


def _explain_labels(labels, mapping, kind):
    explanations = []
    for label in labels:
        info = mapping.get(
            label,
            {
                "title": "未分类观察",
                "message": "存在未分类标签，需结合原始诊断结果核验。",
                "severity": "low",
            },
        )
        explanations.append(
            {
                "label": label,
                "kind": kind,
                "title": info["title"],
                "message": info["message"],
                "severity": info["severity"],
            }
        )
    return explanations


def _penalty_level(value):
    if value >= 35:
        return "high"
    if value >= 15:
        return "medium"
    if value > 0:
        return "low"
    return "none"


def _penalty_breakdown(row, risk_explanations, data_quality_explanations):
    risk_penalty = _safe_number(row.get("risk_penalty") if isinstance(row, dict) else 0)
    data_quality_penalty = _safe_number(row.get("data_quality_penalty") if isinstance(row, dict) else 0)
    return {
        "risk_penalty": {
            "value": risk_penalty,
            "level": _penalty_level(risk_penalty),
            "reasons": [item["label"] for item in risk_explanations],
        },
        "data_quality_penalty": {
            "value": data_quality_penalty,
            "level": _penalty_level(data_quality_penalty),
            "reasons": [item["label"] for item in data_quality_explanations],
        },
        "total_penalty": risk_penalty + data_quality_penalty,
    }


def _factor_notes(row):
    if not isinstance(row, dict):
        return []
    notes = []
    if row.get("preset_name"):
        notes.append(
            {
                "factor": "preset",
                "value": row.get("preset_name"),
                "note": "当前内部评分使用的策略预设。",
            }
        )
    for key in ("trend_score", "momentum_score", "volume_price_score", "liquidity_score", "strategy_score"):
        if key in row:
            notes.append({"factor": key, "value": _safe_number(row.get(key)), "note": "内部研究优先级辅助观察。"})
    return notes


def _summary_text(row_count, risk_count, quality_count, total_penalty):
    if row_count <= 0:
        return "未获得可解释的内部策略评分结果，仅返回空解释摘要。"
    return (
        f"已生成 {row_count} 条内部风险与数据质量解释；"
        f"风险解释 {risk_count} 条，数据质量解释 {quality_count} 条，"
        f"合计惩罚值 {total_penalty}。本摘要仅用于学习和研究，不构成投资建议。"
    )


def _warnings(rows):
    warnings = []
    if not rows:
        warnings.append("输入为空或结构不可识别。")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            warnings.append(f"第 {index} 条输入不是字典结构。")
        elif "risk_penalty" not in row and "data_quality_penalty" not in row:
            warnings.append(f"第 {index} 条输入缺少惩罚字段。")
    return warnings


def build_strategy_explanations(source):
    rows = _extract_score_rows(source)
    warnings = _warnings(rows)
    items = []
    risk_total = 0
    quality_total = 0
    penalty_total = 0

    for index, row in enumerate(rows):
        row = row if isinstance(row, dict) else {}
        risk_labels = _extract_labels(row, "risk_labels", "risk_tags")
        quality_labels = _extract_labels(row, "data_quality_labels")
        risk_explanations = _explain_labels(risk_labels, RISK_EXPLANATION_MAP, "risk")
        data_quality_explanations = _explain_labels(quality_labels, DATA_QUALITY_EXPLANATION_MAP, "data_quality")
        penalty_breakdown = _penalty_breakdown(row, risk_explanations, data_quality_explanations)
        risk_total += len(risk_explanations)
        quality_total += len(data_quality_explanations)
        penalty_total += penalty_breakdown["total_penalty"]
        items.append(
            {
                "row_index": index,
                "identity": copy.deepcopy(row.get("identity", {})),
                "risk_explanations": risk_explanations,
                "data_quality_explanations": data_quality_explanations,
                "penalty_breakdown": penalty_breakdown,
                "factor_notes": _factor_notes(row),
            }
        )

    result = {
        "status": "ok" if rows else "empty",
        "items": items,
        "risk_explanations": [item for row in items for item in row["risk_explanations"]],
        "data_quality_explanations": [item for row in items for item in row["data_quality_explanations"]],
        "penalty_breakdown": {
            "total_risk_penalty": sum(item["penalty_breakdown"]["risk_penalty"]["value"] for item in items),
            "total_data_quality_penalty": sum(
                item["penalty_breakdown"]["data_quality_penalty"]["value"] for item in items
            ),
            "total_penalty": penalty_total,
        },
        "factor_notes": [note for row in items for note in row["factor_notes"]],
        "summary_text": _summary_text(len(rows), risk_total, quality_total, penalty_total),
        "warnings": warnings,
        "metadata": {
            "read_only": True,
            "ui_connected": False,
            "ranking_changed": False,
            "scoring_changed": False,
        },
    }
    return result


__all__ = ["build_strategy_explanations"]
