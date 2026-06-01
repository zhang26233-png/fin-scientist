"""Read-only explanations for internal strategy outputs."""

import copy
import math


REASON_FIELDS = [
    "strategy_reason",
    "trend_reason",
    "momentum_reason",
    "volume_price_reason",
    "liquidity_reason",
    "risk_reason",
    "data_quality_reason",
    "preset_reason",
    "confidence_note",
]

_PRESET_REASON_MAP = {
    "balanced_research": "balanced_research 表示均衡研究视角，同时观察趋势、动量、量价、流动性、风险和数据质量。",
    "trend_momentum": "trend_momentum 更偏趋势延续和近期动量强度观察。",
    "volume_breakout": "volume_breakout 更关注量价是否互相确认。",
    "low_risk_quality": "low_risk_quality 更重视低风险压力、流动性和数据可用性。",
    "high_elasticity_watch": "high_elasticity_watch 用于观察高弹性研究对象，同时保留风险标签提示。",
}

_STYLE_REASON_MAP = {
    "balanced": "均衡或混合研究风格",
    "trend_momentum": "趋势动量风格",
    "volume_breakout": "量价观察风格",
    "low_risk_quality": "低风险质量风格",
    "high_elasticity": "高弹性观察风格",
    "mixed": "混合风格",
    "insufficient_data": "数据不足状态",
}

_RISK_REASON_MAP = {
    "high_volatility": "高波动压低研究可信度",
    "extreme_upside_return": "近期涨幅较大，需要核查过热风险",
    "volume_downside_risk": "放量走弱带来风险扣分",
    "overheated_turnover": "换手热度偏高",
    "low_liquidity": "流动性偏弱",
    "insufficient_factor_data": "部分因子数据不足",
    "missing_volume_fields": "量能字段不完整",
}

_DATA_QUALITY_REASON_MAP = {
    "missing_price_fields": "价格字段不完整",
    "missing_volume_fields": "量能字段不完整",
    "missing_turnover_fields": "换手字段不完整",
    "invalid_numeric_fields": "部分数值字段无效",
    "insufficient_factor_data": "因子输入不足",
}


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


def _finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _read_any(row, keys):
    if not isinstance(row, dict):
        return None
    lowered = {str(key).lower(): key for key in row}
    for key in keys:
        if key in row:
            return row.get(key)
        matched = lowered.get(str(key).lower())
        if matched is not None:
            return row.get(matched)
    return None


def _score_band(value):
    number = _finite_number(value)
    if number is None:
        return "不可用"
    if number >= 70:
        return "较强"
    if number >= 50:
        return "中等"
    if number > 0:
        return "偏弱"
    return "不可用"


def _format_percent(value):
    number = _finite_number(value)
    if number is None:
        return None
    return f"{number * 100:.1f}%"


def _format_number(value):
    number = _finite_number(value)
    if number is None:
        return None
    if abs(number) >= 100_000_000:
        return f"{number / 100_000_000:.2f}e8"
    if abs(number) >= 10_000:
        return f"{number / 10_000:.1f}w"
    return f"{number:.2f}".rstrip("0").rstrip(".")


def _join_parts(parts, fallback):
    clean_parts = [str(part) for part in parts if part not in (None, "")]
    return "; ".join(clean_parts) if clean_parts else fallback


def _label_reasons(labels, mapping):
    return [mapping.get(label, str(label)) for label in _as_list(labels)]


def _top_component_names(row):
    pairs = [
        ("趋势", _finite_number(row.get("trend_score"))),
        ("动量", _finite_number(row.get("momentum_score"))),
        ("量价", _finite_number(row.get("volume_price_score"))),
        ("流动性", _finite_number(row.get("liquidity_score"))),
    ]
    valid = [(name, value) for name, value in pairs if value is not None]
    valid.sort(key=lambda item: item[1], reverse=True)
    return [name for name, _ in valid[:2]]


def build_strategy_reason_fields(row):
    """Build row-level strategy explanations without changing scores or ordering."""

    row = copy.deepcopy(row) if isinstance(row, dict) else {}
    risk_labels = _as_list(row.get("risk_labels"))
    quality_labels = _as_list(row.get("data_quality_labels"))
    warnings = _as_list(row.get("warnings"))
    bonus_reasons = _as_list(row.get("preset_bonus_reasons"))

    best_preset = row.get("best_preset") or row.get("preset_name") or "balanced_research"
    dominant_style = row.get("dominant_style") or "mixed"
    style_text = _STYLE_REASON_MAP.get(dominant_style, str(dominant_style))
    top_components = _top_component_names(row)
    strategy_parts = [
        f"strategy_score 反映{style_text}",
        f"主要支撑项：{', '.join(top_components)}" if top_components else None,
        f"风险扣分 {int(_finite_number(row.get('risk_penalty')) or 0)}",
        f"数据质量扣分 {int(_finite_number(row.get('data_quality_penalty')) or 0)}",
    ]
    strategy_reason = _join_parts(
        strategy_parts,
        "strategy_score 仅用于研究优先级观察。",
    )

    return_20d = _read_any(row, ("return_20d", "recent_return", "pct_chg"))
    close = _read_any(row, ("close", "Close", "price"))
    ma_values = [_finite_number(_read_any(row, (key, key.upper()))) for key in ("ma5", "ma10", "ma20")]
    close_number = _finite_number(close)
    if close_number is not None and any(value is not None for value in ma_values):
        above_count = sum(1 for value in ma_values if value is not None and close_number > value)
        moving_average_note = f"价格高于 {above_count} 条可用均线"
    else:
        moving_average_note = None
    trend_return = _format_percent(return_20d)
    trend_reason = _join_parts(
        [
            f"趋势分处于{_score_band(row.get('trend_score'))}水平（{row.get('trend_score', 'n/a')}）",
            f"20日/近期收益 {trend_return}" if trend_return else None,
            row.get("trend_direction_label"),
            moving_average_note or row.get("moving_average_position"),
        ],
        "趋势输入不足，趋势解释能力有限。",
    )

    returns = [
        ("5d", _format_percent(_read_any(row, ("return_5d", "pct_chg", "recent_return")))),
        ("10d", _format_percent(_read_any(row, ("return_10d", "10d_return")))),
        ("20d", _format_percent(return_20d)),
    ]
    return_notes = [f"{label} {value}" for label, value in returns if value]
    up_count = _finite_number(row.get("consecutive_up_count"))
    down_count = _finite_number(row.get("consecutive_down_count"))
    momentum_reason = _join_parts(
        [
            f"动量分处于{_score_band(row.get('momentum_score'))}水平（{row.get('momentum_score', 'n/a')}）",
            ", ".join(return_notes) if return_notes else None,
            f"连续走强天数 {int(up_count)}" if up_count is not None else None,
            f"连续走弱天数 {int(down_count)}" if down_count is not None else None,
        ],
        "动量输入不足，动量解释能力有限。",
    )

    amount = _format_number(_read_any(row, ("amount", "turnover_amount")))
    volume = _format_number(_read_any(row, ("volume", "Volume")))
    volume_ratio = _format_number(_read_any(row, ("volume_ratio",)))
    turnover = _format_percent(_read_any(row, ("turnover", "turnover_rate")))
    volume_labels = []
    if "volume_price_confirmed" in bonus_reasons or row.get("volume_price_confirmed") is True:
        volume_labels.append("量价互相确认")
    if row.get("volume_price_weak") is True:
        volume_labels.append("量价确认偏弱")
    volume_price_reason = _join_parts(
        [
            f"量价分处于{_score_band(row.get('volume_price_score'))}水平（{row.get('volume_price_score', 'n/a')}）",
            f"成交额 {amount}" if amount else None,
            f"成交量 {volume}" if volume else None,
            f"量比 {volume_ratio}" if volume_ratio else None,
            f"换手率 {turnover}" if turnover else None,
            ", ".join(volume_labels) if volume_labels else None,
        ],
        "量价输入不足，该部分仅适合粗略观察。",
    )

    liquidity_reason = _join_parts(
        [
            f"流动性分处于{_score_band(row.get('liquidity_score'))}水平（{row.get('liquidity_score', 'n/a')}）",
            f"成交额 {amount}" if amount else None,
            f"成交量 {volume}" if volume else None,
            f"换手率 {turnover}" if turnover else None,
            "存在低流动性标签" if "low_liquidity" in risk_labels else None,
        ],
        "流动性输入不足，无法完整核查流动性支持。",
    )

    risk_reason = _join_parts(
        [
            f"风险扣分 {int(_finite_number(row.get('risk_penalty')) or 0)}",
            ", ".join(_label_reasons(risk_labels, _RISK_REASON_MAP)) if risk_labels else "当前字段未触发主要风险标签",
        ],
        "风险标签不可用。",
    )

    data_quality_reason = _join_parts(
        [
            f"数据质量扣分 {int(_finite_number(row.get('data_quality_penalty')) or 0)}",
            ", ".join(_label_reasons(quality_labels, _DATA_QUALITY_REASON_MAP))
            if quality_labels
            else "当前字段未触发主要数据质量标签",
        ],
        "数据质量标签不可用。",
    )

    preset_reason = _PRESET_REASON_MAP.get(
        best_preset,
        f"{best_preset} 是当前预览比较中分数最高的 preset。",
    )

    consensus = row.get("consensus_level") or "insufficient_data"
    if warnings or quality_labels or consensus == "insufficient_data":
        confidence_note = "解释可信度有限：数据不完整或存在 warning。"
    elif consensus == "broad_consensus_high":
        confidence_note = "解释可信度较高：数据可用且多策略共识较高。"
    elif consensus in {"mixed_signal", "style_specific_high"}:
        confidence_note = "解释可信度中低：不同 preset 之间存在分歧。"
    else:
        confidence_note = "解释可信度中等，仍需结合原始字段复核。"

    return {
        "strategy_reason": strategy_reason,
        "trend_reason": trend_reason,
        "momentum_reason": momentum_reason,
        "volume_price_reason": volume_price_reason,
        "liquidity_reason": liquidity_reason,
        "risk_reason": risk_reason,
        "data_quality_reason": data_quality_reason,
        "preset_reason": preset_reason,
        "confidence_note": confidence_note,
    }


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
                "reason_fields": build_strategy_reason_fields(row),
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


__all__ = ["REASON_FIELDS", "build_strategy_explanations", "build_strategy_reason_fields"]
