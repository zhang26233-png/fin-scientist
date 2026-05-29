"""Read-only strategy preview helpers for candidate pools."""

import copy
import json
import math
from pathlib import Path

import pandas as pd

from strategy.adapter import infer_field_mapping, to_number
from strategy.preset_comparison import DEFAULT_COMPARISON_PRESETS, compare_strategy_presets
from strategy.scoring import calculate_strategy_scores


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


def _empty_preview():
    return pd.DataFrame(columns=PREVIEW_COLUMNS)


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
    "build_strategy_preview",
    "build_strategy_preview_row",
    "export_strategy_preview_to_csv",
    "export_strategy_preview_to_json_like",
]
