"""Unified read-only service for internal strategy diagnostics."""

import copy

import pandas as pd

from strategy.adapter import build_strategy_diagnostics
from strategy.report import build_strategy_report


def _count_missing_mappings(diagnostics_output):
    mapping = diagnostics_output.get("field_mapping", {}) if isinstance(diagnostics_output, dict) else {}
    if not isinstance(mapping, dict):
        return 0
    return sum(1 for value in mapping.values() if value is None)


def _build_warnings(result_df, diagnostics_output):
    warnings = []
    if not isinstance(result_df, pd.DataFrame):
        warnings.append("输入对象不是 DataFrame，已返回空诊断。")
        return warnings
    if result_df.empty:
        warnings.append("输入 DataFrame 为空，未生成候选对象诊断。")
        return warnings

    missing_count = _count_missing_mappings(diagnostics_output)
    if missing_count:
        warnings.append(f"字段映射存在 {missing_count} 个缺失项，部分诊断可能仅供初步观察。")

    diagnostics = diagnostics_output.get("diagnostics", []) if isinstance(diagnostics_output, dict) else []
    if isinstance(diagnostics, list):
        unresolved_count = 0
        failed_filter_count = 0
        for item in diagnostics:
            if not isinstance(item, dict):
                continue
            factor_scores = item.get("factor_scores", {})
            if isinstance(factor_scores, dict):
                unresolved_count += sum(
                    1
                    for result in factor_scores.values()
                    if isinstance(result, dict) and result.get("score") == "无法计算"
                )
            filter_flags = item.get("filter_flags", {})
            if isinstance(filter_flags, dict) and filter_flags.get("passed") is False:
                failed_filter_count += 1
        if unresolved_count:
            warnings.append(f"存在 {unresolved_count} 个无法计算的策略因子。")
        if failed_filter_count:
            warnings.append(f"存在 {failed_filter_count} 个候选对象触发过滤待核验项。")
    return warnings


def build_strategy_service_output(result_df, preset_key="research_priority"):
    """Build diagnostics and report from a screening-result DataFrame.

    The service copies the input before passing it to downstream helpers so the
    caller's DataFrame is not mutated by the strategy layer.
    """
    source = result_df.copy(deep=True) if isinstance(result_df, pd.DataFrame) else result_df
    diagnostics_output = build_strategy_diagnostics(source, preset_key=preset_key)
    report = build_strategy_report(diagnostics_output)
    warnings = _build_warnings(source, diagnostics_output)
    diagnostics = diagnostics_output.get("diagnostics", []) if isinstance(diagnostics_output, dict) else []
    status = "ok" if diagnostics else "empty"
    if warnings and diagnostics:
        status = "warning"

    metadata = {
        "input_type": type(result_df).__name__,
        "input_rows": len(result_df) if isinstance(result_df, pd.DataFrame) else 0,
        "diagnostic_count": len(diagnostics) if isinstance(diagnostics, list) else 0,
        "preset_key": preset_key,
        "read_only": True,
        "ui_connected": False,
        "ranking_changed": False,
        "scoring_changed": False,
    }

    return {
        "status": status,
        "preset_name": diagnostics_output.get("preset_name", "") if isinstance(diagnostics_output, dict) else "",
        "diagnostics": copy.deepcopy(diagnostics),
        "report": report,
        "metadata": metadata,
        "warnings": warnings,
    }


__all__ = [
    "build_strategy_service_output",
]
