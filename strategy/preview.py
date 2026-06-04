"""Read-only strategy preview helpers for candidate pools."""

import copy
import json
import math
from pathlib import Path

import pandas as pd

from strategy.adapter import infer_field_mapping, to_number
from strategy.architecture_audit import ARCHITECTURE_AUDIT_FIELDS, build_architecture_audit_profile
from strategy.composite_profile import COMPOSITE_PROFILE_FIELDS, build_composite_profile
from strategy.confluence import CONFLUENCE_FIELDS, build_confluence_profile
from strategy.event_context import EVENT_CONTEXT_FIELDS, build_event_context_profile
from strategy.event_confluence import EVENT_CONFLUENCE_FIELDS, build_event_confluence_profile
from strategy.event_diagnostics import EVENT_DIAGNOSTIC_FIELDS, build_event_diagnostics_profile
from strategy.event_research_summary import EVENT_RESEARCH_SUMMARY_FIELDS, build_event_research_summary_profile
from strategy.explanations import REASON_FIELDS, build_strategy_reason_fields
from strategy.fundamental import FUNDAMENTAL_PROFILE_FIELDS, build_fundamental_profile
from strategy.fundamental_diagnostics import FUNDAMENTAL_DIAGNOSTIC_FIELDS, build_fundamental_diagnostics_profile
from strategy.fundamental_relative import RELATIVE_FUNDAMENTAL_FIELDS, build_fundamental_relative_profile
from strategy.preset_comparison import DEFAULT_COMPARISON_PRESETS, compare_strategy_presets
from strategy.priority_stability import PRIORITY_STABILITY_FIELDS, build_priority_stability_profile
from strategy.research_pipeline_audit import RESEARCH_PIPELINE_AUDIT_FIELDS, build_research_pipeline_audit_profile
from strategy.scoring import calculate_strategy_scores
from strategy.technical import TECHNICAL_PROFILE_FIELDS, build_technical_profile


PREVIEW_COLUMNS = [
    "symbol",
    "name",
    "original_score",
    "strategy_score",
    "preset_name",
    "best_preset",
    "worst_preset",
    "score_spread",
    "average_preset_score",
    "dominant_style",
    "consensus_level",
    "balanced_research_score",
    "trend_momentum_score",
    "volume_breakout_score",
    "low_risk_quality_score",
    "high_elasticity_watch_score",
    "risk_labels",
    "data_quality_labels",
    "warnings",
    "strategy_reason",
    "trend_reason",
    "momentum_reason",
    "volume_price_reason",
    "liquidity_reason",
    "risk_reason",
    "data_quality_reason",
    "preset_reason",
    "confidence_note",
    "ma_structure_label",
    "trend_quality_label",
    "breakout_pullback_label",
    "volume_price_structure_label",
    "short_term_overheat_label",
    "volatility_risk_label",
    "technical_profile_summary",
    "technical_grade",
    "technical_style",
    "technical_strength",
    "technical_risk_level",
    "technical_watch_points",
    "technical_summary_short",
    "fundamental_available",
    "fundamental_fields_detected",
    "missing_fundamental_fields",
    "fundamental_data_quality_label",
    "fundamental_summary_base",
    "profitability_score",
    "growth_score",
    "valuation_score",
    "financial_risk_score",
    "fundamental_quality_score",
    "fundamental_grade",
    "fundamental_style",
    "fundamental_risk_level",
    "fundamental_reason",
    "relative_profitability_label",
    "relative_growth_label",
    "relative_valuation_label",
    "relative_financial_risk_label",
    "industry_relative_quality_label",
    "industry_relative_summary",
    "fundamental_diagnostics",
    "profitability_diagnostics",
    "growth_diagnostics",
    "valuation_diagnostics",
    "financial_risk_diagnostics",
    "fundamental_watch_points",
    "fundamental_strength_points",
    "fundamental_weakness_points",
    "fundamental_diagnostics_summary",
    "confluence_label",
    "confluence_score",
    "confluence_summary",
    "confluence_strength_points",
    "confluence_risk_points",
    "confluence_followup_focus",
    "composite_research_grade",
    "composite_research_style",
    "composite_research_level",
    "composite_risk_level",
    "composite_confidence_level",
    "composite_summary",
    "composite_strength_points",
    "composite_risk_points",
    "composite_followup_focus",
    "composite_data_quality_note",
    "research_priority_score",
    "research_priority_level",
    "research_priority_reasons",
    "research_priority_warnings",
    "priority_stability_label",
    "priority_stability_score",
    "priority_stability_note",
    "priority_drift_detected",
    "priority_drift_reason",
    "architecture_audit_label",
    "architecture_audit_score",
    "architecture_audit_note",
    "architecture_audit_warnings",
    "field_contract_warnings",
    "module_contract_warnings",
    "boundary_contract_warnings",
    "event_available",
    "event_type",
    "event_recency_label",
    "event_source_quality_label",
    "event_reliability_label",
    "event_context_note",
    "event_research_tags",
    "event_warnings",
    "event_completeness_score",
    "event_clarity_score",
    "event_consistency_score",
    "event_confidence_score",
    "event_diagnostic_level",
    "event_diagnostic_summary",
    "event_followup_questions",
    "event_evidence_gaps",
    "event_quality_warnings",
    "event_confluence_label",
    "event_confluence_score",
    "event_confluence_summary",
    "event_support_points",
    "event_conflict_points",
    "event_followup_focus",
    "event_confluence_warnings",
    "event_research_summary",
    "event_research_level",
    "event_key_evidence",
    "event_key_risks",
    "event_validation_focus",
    "event_agent_note",
    "event_summary_warnings",
    "research_pipeline_status",
    "research_pipeline_conflicts",
    "research_pipeline_warnings",
    "research_pipeline_summary",
]


def _source_to_frame(source):
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, pd.Series):
        return pd.DataFrame([copy.deepcopy(source.to_dict())])
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    return pd.DataFrame()


def _read_mapped(row, mapping, key):
    column = mapping.get(key) if isinstance(mapping, dict) else None
    if column is None:
        return None
    return row.get(column)


def _safe_text(value):
    return "" if value is None else str(value)


def _safe_number(value):
    number = to_number(value)
    return None if math.isnan(number) else number


def _score_value(value):
    number = _safe_number(value)
    return None if number is None else int(round(number))


def _read_any(row, candidates):
    for column in candidates:
        if column in row:
            return row.get(column)
    lowered = {str(column).lower(): column for column in row.index}
    for column in candidates:
        matched = lowered.get(str(column).lower())
        if matched is not None:
            return row.get(matched)
    return None


def _empty_preview():
    return pd.DataFrame(columns=PREVIEW_COLUMNS)


def _default_relative_profile():
    return {
        "relative_profitability_label": "insufficient_data",
        "relative_growth_label": "insufficient_data",
        "relative_valuation_label": "insufficient_data",
        "relative_financial_risk_label": "insufficient_data",
        "industry_relative_quality_label": "insufficient_industry_data",
        "industry_relative_summary": "行业字段或同行样本不足，暂不能形成行业相对基本面观察。",
    }


def _merge_contexts(left, right):
    merged = copy.deepcopy(left) if isinstance(left, dict) else {}
    if isinstance(right, dict):
        merged.update(copy.deepcopy(right))
    return merged


def _preset_score_map(comparison):
    scores = {}
    for item in comparison.get("preset_scores", []) if isinstance(comparison, dict) else []:
        if not isinstance(item, dict):
            continue
        preset_name = item.get("preset_name")
        if preset_name:
            scores[f"{preset_name}_score"] = _score_value(item.get("strategy_score"))
    return scores


def _preset_name(item):
    if not isinstance(item, dict):
        return ""
    return _safe_text(item.get("preset_name"))


def _source_reason_metrics(row, mapping):
    return {
        "close": _safe_number(_read_mapped(row, mapping, "close")),
        "amount": _safe_number(_read_mapped(row, mapping, "amount")),
        "volume": _safe_number(_read_mapped(row, mapping, "volume")),
        "turnover": _safe_number(_read_mapped(row, mapping, "turnover")),
        "volume_ratio": _safe_number(_read_mapped(row, mapping, "volume_ratio")),
        "volatility": _safe_number(_read_mapped(row, mapping, "volatility")),
        "amplitude": _safe_number(_read_mapped(row, mapping, "amplitude")),
        "return_20d": _safe_number(_read_mapped(row, mapping, "return_20d")),
        "recent_return": _safe_number(_read_mapped(row, mapping, "change_pct")),
        "return_10d": _safe_number(_read_any(row, ("return_10d", "10d_return"))),
        "return_5d": _safe_number(_read_any(row, ("return_5d", "5d_return", "pct_chg", "recent_return"))),
        "recent_high": _safe_number(_read_any(row, ("recent_high", "high_20d", "highest_20d"))),
        "recent_low": _safe_number(_read_any(row, ("recent_low", "low_20d", "lowest_20d"))),
        "support_price": _safe_number(_read_any(row, ("support_price",))),
        "ma5": _safe_number(_read_mapped(row, mapping, "ma5")),
        "ma10": _safe_number(_read_mapped(row, mapping, "ma10")),
        "ma20": _safe_number(_read_mapped(row, mapping, "ma20")),
    }


def build_strategy_preview_row(row, preset_names=None):
    row_dict = copy.deepcopy(row.to_dict()) if isinstance(row, pd.Series) else copy.deepcopy(row)
    if not isinstance(row_dict, dict):
        row_dict = {}
    source = pd.DataFrame([row_dict])
    mapping = infer_field_mapping(source)
    score_result = calculate_strategy_scores(source, preset_name="balanced_research")
    scores = score_result.get("scores", []) if isinstance(score_result, dict) else []
    default_score = copy.deepcopy(scores[0]) if scores else {}
    comparison = compare_strategy_presets(source, preset_names=preset_names)
    preset_scores = _preset_score_map(comparison)
    warnings = []
    if isinstance(score_result, dict) and score_result.get("status") != "ok":
        warnings.append("strategy score unavailable")
    if isinstance(comparison, dict):
        warnings.extend(str(item) for item in comparison.get("warnings", []) if item)
    else:
        warnings.append("preset comparison unavailable")

    identity = default_score.get("identity", {}) if isinstance(default_score, dict) else {}
    row_data = {
        "symbol": _safe_text(identity.get("symbol") or _read_mapped(source.iloc[0], mapping, "symbol")),
        "name": _safe_text(identity.get("name") or _read_mapped(source.iloc[0], mapping, "name")),
        "original_score": _safe_number(_read_mapped(source.iloc[0], mapping, "score")),
        "strategy_score": _score_value(default_score.get("strategy_score")),
        "preset_name": _safe_text(default_score.get("preset_name") or "balanced_research"),
        "best_preset": _preset_name(comparison.get("best_preset") if isinstance(comparison, dict) else None),
        "worst_preset": _preset_name(comparison.get("worst_preset") if isinstance(comparison, dict) else None),
        "score_spread": comparison.get("score_spread") if isinstance(comparison, dict) else None,
        "average_preset_score": comparison.get("average_preset_score") if isinstance(comparison, dict) else None,
        "dominant_style": _safe_text(comparison.get("dominant_style") if isinstance(comparison, dict) else ""),
        "consensus_level": _safe_text(comparison.get("consensus_level") if isinstance(comparison, dict) else ""),
        "risk_labels": list(default_score.get("risk_labels", [])) if isinstance(default_score.get("risk_labels"), list) else [],
        "data_quality_labels": list(default_score.get("data_quality_labels", []))
        if isinstance(default_score.get("data_quality_labels"), list)
        else [],
        "warnings": list(dict.fromkeys(warnings)),
    }
    for column in PREVIEW_COLUMNS:
        if column.endswith("_score") and column not in row_data:
            row_data[column] = preset_scores.get(column)
    reason_context = {}
    reason_context.update(_source_reason_metrics(source.iloc[0], mapping))
    reason_context.update(copy.deepcopy(default_score))
    components = default_score.get("strategy_score_components", {}) if isinstance(default_score, dict) else {}
    if isinstance(components, dict):
        reason_context["preset_bonus_reasons"] = list(components.get("preset_bonus_reasons", []))
    reason_context.update(row_data)
    row_data.update(build_technical_profile(reason_context))
    row_data.update(build_fundamental_profile(row_dict))
    row_data.update(_default_relative_profile())
    diagnostic_frame = build_fundamental_diagnostics_profile([_merge_contexts(row_dict, row_data)])
    if not diagnostic_frame.empty:
        row_data.update(diagnostic_frame.iloc[0].to_dict())
    confluence_frame = build_confluence_profile([row_data])
    if not confluence_frame.empty:
        row_data.update(confluence_frame.iloc[0].to_dict())
    composite_frame = build_composite_profile([row_data])
    if not composite_frame.empty:
        row_data.update(composite_frame.iloc[0].to_dict())
    stability_frame = build_priority_stability_profile([row_data])
    if not stability_frame.empty:
        row_data.update(stability_frame.iloc[0].to_dict())
    event_frame = build_event_context_profile([_merge_contexts(row_dict, row_data)])
    if not event_frame.empty:
        row_data.update(event_frame.iloc[0].to_dict())
    event_diagnostic_frame = build_event_diagnostics_profile([_merge_contexts(row_dict, row_data)])
    if not event_diagnostic_frame.empty:
        row_data.update(event_diagnostic_frame.iloc[0].to_dict())
    event_confluence_frame = build_event_confluence_profile([_merge_contexts(row_dict, row_data)])
    if not event_confluence_frame.empty:
        row_data.update(event_confluence_frame.iloc[0].to_dict())
    event_summary_frame = build_event_research_summary_profile([_merge_contexts(row_dict, row_data)])
    if not event_summary_frame.empty:
        row_data.update(event_summary_frame.iloc[0].to_dict())
    pipeline_frame = build_research_pipeline_audit_profile([row_data])
    if not pipeline_frame.empty:
        row_data.update(pipeline_frame.iloc[0].to_dict())
    audit_frame = build_architecture_audit_profile([row_data])
    if not audit_frame.empty:
        row_data.update(audit_frame.iloc[0].to_dict())
    reason_context.update(row_data)
    row_data.update(build_strategy_reason_fields(reason_context))
    return {column: row_data.get(column) for column in PREVIEW_COLUMNS}


def build_strategy_preview(source, preset_names=None, sort_by_strategy=False):
    frame = _source_to_frame(source)
    if frame.empty:
        return _empty_preview()

    source_copy = frame.copy(deep=True)
    rows = [
        build_strategy_preview_row(row, preset_names=preset_names)
        for _, row in source_copy.iterrows()
    ]
    preview = pd.DataFrame(rows, columns=PREVIEW_COLUMNS)
    relative = build_fundamental_relative_profile(source_copy)
    if not relative.empty:
        for column in RELATIVE_FUNDAMENTAL_FIELDS:
            if column in relative.columns:
                preview[column] = list(relative[column])
    diagnostic_source = [
        _merge_contexts(raw_row.to_dict(), preview.iloc[index].to_dict())
        for index, (_, raw_row) in enumerate(source_copy.iterrows())
    ]
    diagnostics = build_fundamental_diagnostics_profile(diagnostic_source)
    if not diagnostics.empty:
        for column in FUNDAMENTAL_DIAGNOSTIC_FIELDS:
            if column in diagnostics.columns:
                preview[column] = list(diagnostics[column])
    confluence = build_confluence_profile(preview)
    if not confluence.empty:
        for column in CONFLUENCE_FIELDS:
            if column in confluence.columns:
                preview[column] = list(confluence[column])
    composite = build_composite_profile(preview)
    if not composite.empty:
        for column in COMPOSITE_PROFILE_FIELDS:
            if column in composite.columns:
                preview[column] = list(composite[column])
    stability = build_priority_stability_profile(preview)
    if not stability.empty:
        for column in PRIORITY_STABILITY_FIELDS:
            if column in stability.columns:
                preview[column] = list(stability[column])
    event_context = build_event_context_profile(diagnostic_source)
    if not event_context.empty:
        for column in EVENT_CONTEXT_FIELDS:
            if column in event_context.columns:
                preview[column] = list(event_context[column])
    event_diagnostics_source = [
        _merge_contexts(raw_row.to_dict(), preview.iloc[index].to_dict())
        for index, (_, raw_row) in enumerate(source_copy.iterrows())
    ]
    event_diagnostics = build_event_diagnostics_profile(event_diagnostics_source)
    if not event_diagnostics.empty:
        for column in EVENT_DIAGNOSTIC_FIELDS:
            if column in event_diagnostics.columns:
                preview[column] = list(event_diagnostics[column])
    event_confluence = build_event_confluence_profile(preview)
    if not event_confluence.empty:
        for column in EVENT_CONFLUENCE_FIELDS:
            if column in event_confluence.columns:
                preview[column] = list(event_confluence[column])
    event_summary = build_event_research_summary_profile(preview)
    if not event_summary.empty:
        for column in EVENT_RESEARCH_SUMMARY_FIELDS:
            if column in event_summary.columns:
                preview[column] = list(event_summary[column])
    pipeline_audit = build_research_pipeline_audit_profile(preview)
    if not pipeline_audit.empty:
        for column in RESEARCH_PIPELINE_AUDIT_FIELDS:
            if column in pipeline_audit.columns:
                preview[column] = list(pipeline_audit[column])
    audit = build_architecture_audit_profile(preview)
    if not audit.empty:
        for column in ARCHITECTURE_AUDIT_FIELDS:
            if column in audit.columns:
                preview[column] = list(audit[column])
    if sort_by_strategy:
        preview = preview.sort_values(
            by=["strategy_score", "average_preset_score"],
            ascending=[False, False],
            na_position="last",
            kind="mergesort",
        ).reset_index(drop=True)
    return preview


def _json_safe(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (list, dict)):
        return copy.deepcopy(value)
    if pd.isna(value):
        return None
    return value


def export_strategy_preview_to_json_like(preview):
    frame = _source_to_frame(preview)
    if frame.empty:
        records = []
    else:
        records = [
            {column: _json_safe(row.get(column)) for column in frame.columns}
            for _, row in frame.iterrows()
        ]
    return {
        "schema_version": "strategy_preview.v1",
        "records": records,
        "metadata": {
            "record_count": len(records),
            "read_only": True,
            "uses_real_data_source": False,
            "ui_connected": False,
            "ranking_changed": False,
            "preview_columns": list(frame.columns) if not frame.empty else list(PREVIEW_COLUMNS),
        },
    }


def export_strategy_preview_to_csv(preview, path):
    frame = _source_to_frame(preview)
    export_frame = frame.copy(deep=True)
    for column in export_frame.columns:
        export_frame[column] = export_frame[column].map(
            lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (list, dict)) else value
        )
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_frame.to_csv(output_path, index=False, encoding="utf-8")
    return {
        "path": str(output_path),
        "row_count": len(export_frame),
        "metadata": {
            "read_only": True,
            "uses_real_data_source": False,
            "ui_connected": False,
            "ranking_changed": False,
        },
    }


__all__ = [
    "PREVIEW_COLUMNS",
    "ARCHITECTURE_AUDIT_FIELDS",
    "COMPOSITE_PROFILE_FIELDS",
    "CONFLUENCE_FIELDS",
    "EVENT_CONTEXT_FIELDS",
    "EVENT_CONFLUENCE_FIELDS",
    "EVENT_DIAGNOSTIC_FIELDS",
    "EVENT_RESEARCH_SUMMARY_FIELDS",
    "FUNDAMENTAL_DIAGNOSTIC_FIELDS",
    "FUNDAMENTAL_PROFILE_FIELDS",
    "PRIORITY_STABILITY_FIELDS",
    "REASON_FIELDS",
    "RESEARCH_PIPELINE_AUDIT_FIELDS",
    "RELATIVE_FUNDAMENTAL_FIELDS",
    "TECHNICAL_PROFILE_FIELDS",
    "build_strategy_preview",
    "build_strategy_preview_row",
    "export_strategy_preview_to_csv",
    "export_strategy_preview_to_json_like",
]
