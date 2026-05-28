"""Read-only report builder for strategy diagnostics."""

import copy

INSUFFICIENT = "数据不足"


def _as_list(value):
    return value if isinstance(value, list) else []


def _safe_text(value):
    return str(value).strip() if value is not None else ""


def _get_diagnostics(adapter_output):
    if not isinstance(adapter_output, dict):
        return []
    return _as_list(adapter_output.get("diagnostics"))


def _get_preset_name(adapter_output):
    if not isinstance(adapter_output, dict):
        return ""
    return _safe_text(adapter_output.get("preset_name"))


def _summarize_factors(diagnostics):
    if not diagnostics:
        return "暂无可汇总的因子诊断。"

    total = 0
    calculable = 0
    unavailable = {}
    score_buckets = {"较高": 0, "中性": 0, "较低": 0}
    for item in diagnostics:
        factor_scores = item.get("factor_scores", {}) if isinstance(item, dict) else {}
        if not isinstance(factor_scores, dict):
            continue
        for factor_name, factor_result in factor_scores.items():
            total += 1
            if not isinstance(factor_result, dict):
                unavailable[factor_name] = unavailable.get(factor_name, 0) + 1
                continue
            score = factor_result.get("score")
            if isinstance(score, (int, float)):
                calculable += 1
                if score >= 65:
                    score_buckets["较高"] += 1
                elif score >= 40:
                    score_buckets["中性"] += 1
                else:
                    score_buckets["较低"] += 1
            else:
                unavailable[factor_name] = unavailable.get(factor_name, 0) + 1

    if total == 0:
        return "暂无可汇总的因子诊断。"

    parts = [f"共识别 {total} 个因子项，其中 {calculable} 个可计算。"]
    parts.append(
        "因子分布："
        f"较高 {score_buckets['较高']} 个，"
        f"中性 {score_buckets['中性']} 个，"
        f"较低 {score_buckets['较低']} 个。"
    )
    if unavailable:
        names = "、".join(sorted(unavailable))
        parts.append(f"存在样本或字段不足的因子：{names}。")
    return "".join(parts)


def _summarize_filters(diagnostics):
    if not diagnostics:
        return "暂无可汇总的过滤标记。"

    passed_count = 0
    total_count = 0
    failed_reasons = []
    for item in diagnostics:
        filter_flags = item.get("filter_flags", {}) if isinstance(item, dict) else {}
        if not isinstance(filter_flags, dict):
            continue
        total_count += 1
        if filter_flags.get("passed") is True:
            passed_count += 1
        for check in _as_list(filter_flags.get("checks")):
            if isinstance(check, dict) and check.get("passed") is False and check.get("reason"):
                failed_reasons.append(str(check["reason"]))

    if total_count == 0:
        return "暂无可汇总的过滤标记。"
    if failed_reasons:
        unique_reasons = list(dict.fromkeys(failed_reasons))
        return f"过滤检查通过 {passed_count}/{total_count} 个候选对象；待核验项包括：" + "；".join(unique_reasons[:5]) + "。"
    return f"过滤检查通过 {passed_count}/{total_count} 个候选对象，暂无集中待核验项。"


def _summarize_risks(diagnostics):
    if not diagnostics:
        return "暂无可汇总的风险标签。"

    tag_counts = {}
    notes = []
    for item in diagnostics:
        if not isinstance(item, dict):
            continue
        for risk in _as_list(item.get("risk_tags")):
            if not isinstance(risk, dict):
                continue
            tag = _safe_text(risk.get("tag"))
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            message = _safe_text(risk.get("message"))
            if message:
                notes.append(message)

    if not tag_counts:
        return "暂无可汇总的风险标签。"

    top_tags = sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))
    tag_text = "、".join(f"{name} {count} 次" for name, count in top_tags[:5])
    note_text = "；".join(list(dict.fromkeys(notes))[:3])
    return f"风险标签概括：{tag_text}。" + (f" 主要提示：{note_text}。" if note_text else "")


def _summarize_data_quality(diagnostics):
    if not diagnostics:
        return "输入诊断为空，数据质量需要重新核验。"

    missing_factor_count = 0
    failed_filter_count = 0
    for item in diagnostics:
        if not isinstance(item, dict):
            continue
        factor_scores = item.get("factor_scores", {})
        if isinstance(factor_scores, dict):
            missing_factor_count += sum(
                1
                for result in factor_scores.values()
                if isinstance(result, dict) and result.get("score") == "无法计算"
            )
        filter_flags = item.get("filter_flags", {})
        if isinstance(filter_flags, dict) and filter_flags.get("passed") is False:
            failed_filter_count += 1

    if missing_factor_count or failed_filter_count:
        return (
            f"数据质量提示：存在 {missing_factor_count} 个无法计算的因子项，"
            f"{failed_filter_count} 个候选对象存在过滤待核验项。"
        )
    return "数据质量提示：当前诊断结构较完整，但仍需结合原始数据源状态复核。"


def build_strategy_report(adapter_output):
    snapshot = copy.deepcopy(adapter_output) if isinstance(adapter_output, dict) else {}
    diagnostics = _get_diagnostics(snapshot)
    preset_name = _get_preset_name(snapshot)

    factor_summary = _summarize_factors(diagnostics)
    filter_summary = _summarize_filters(diagnostics)
    risk_summary = _summarize_risks(diagnostics)
    data_quality_summary = _summarize_data_quality(diagnostics)

    if diagnostics:
        summary_text = (
            f"基于 {preset_name or '未命名预设'} 生成内部策略诊断摘要。"
            f"{factor_summary}{filter_summary}{risk_summary}"
            "该摘要仅用于研究优先级观察，不构成投资建议。"
        )
    else:
        summary_text = (
            "未获得可汇总的策略诊断结果。"
            "请先检查 adapter 输出结构、字段映射和候选对象数据完整性。"
            "该摘要仅用于研究优先级观察，不构成投资建议。"
        )

    return {
        "preset_name": preset_name,
        "summary_text": summary_text,
        "factor_summary": factor_summary,
        "filter_summary": filter_summary,
        "risk_summary": risk_summary,
        "data_quality_summary": data_quality_summary,
        "notes": [
            "本报告基于 strategy.adapter 的只读诊断结果生成。",
            "本报告未接入页面展示、现有评分或排序流程。",
            "报告内容仅表达观察、提示、风险和研究优先级，不构成投资建议。",
        ],
    }


__all__ = [
    "build_strategy_report",
]
