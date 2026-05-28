"""Stable JSON-like export helpers for internal strategy snapshots."""

import copy
from datetime import datetime, timezone


COMPARISON_FIELDS = (
    "preset_scores",
    "best_preset",
    "worst_preset",
    "score_spread",
    "average_preset_score",
    "consensus_level",
    "dominant_style",
    "style_notes",
    "warnings",
)

POOL_SUMMARY_FIELDS = (
    "total_count",
    "valid_count",
    "insufficient_data_count",
    "dominant_style_counts",
    "dominant_style_ratios",
    "consensus_level_counts",
    "consensus_level_ratios",
    "average_scores_by_preset",
    "average_score_spread",
    "max_score_spread",
    "summary_text",
    "warnings",
)


def _safe_dict(value):
    return copy.deepcopy(value) if isinstance(value, dict) else {}


def _safe_list(value):
    return copy.deepcopy(value) if isinstance(value, list) else []


def _metadata(source, extra=None, generated_at=None):
    metadata = _safe_dict(source)
    if isinstance(extra, dict):
        metadata.update(copy.deepcopy(extra))
    metadata.setdefault("read_only", True)
    metadata.setdefault("ui_connected", False)
    metadata.setdefault("ranking_changed", False)
    metadata.setdefault("scoring_changed", False)
    if generated_at is not None:
        metadata["generated_at"] = generated_at
    return metadata


def _now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def export_preset_comparison_snapshot(comparison, schema_version="1.0", generated_at=None, metadata=None):
    source = _safe_dict(comparison)
    snapshot = {
        "schema_version": schema_version,
        "snapshot_type": "preset_comparison",
        "preset_scores": _safe_list(source.get("preset_scores")),
        "best_preset": copy.deepcopy(source.get("best_preset")),
        "worst_preset": copy.deepcopy(source.get("worst_preset")),
        "score_spread": source.get("score_spread"),
        "average_preset_score": source.get("average_preset_score"),
        "consensus_level": source.get("consensus_level", "insufficient_data"),
        "dominant_style": source.get("dominant_style", "insufficient_data"),
        "style_notes": _safe_list(source.get("style_notes")),
        "warnings": _safe_list(source.get("warnings")),
        "metadata": _metadata(source.get("metadata"), metadata, generated_at),
    }
    if not source:
        snapshot["warnings"].append("comparison input is empty or invalid")
    return snapshot


def export_preset_pool_summary_snapshot(summary, schema_version="1.0", generated_at=None, metadata=None):
    source = _safe_dict(summary)
    snapshot = {
        "schema_version": schema_version,
        "snapshot_type": "preset_pool_summary",
        "total_count": source.get("total_count", 0),
        "valid_count": source.get("valid_count", 0),
        "insufficient_data_count": source.get("insufficient_data_count", 0),
        "dominant_style_counts": _safe_dict(source.get("dominant_style_counts")),
        "dominant_style_ratios": _safe_dict(source.get("dominant_style_ratios")),
        "consensus_level_counts": _safe_dict(source.get("consensus_level_counts")),
        "consensus_level_ratios": _safe_dict(source.get("consensus_level_ratios")),
        "average_scores_by_preset": _safe_dict(source.get("average_scores_by_preset")),
        "average_score_spread": source.get("average_score_spread"),
        "max_score_spread": source.get("max_score_spread"),
        "summary_text": source.get("summary_text", ""),
        "warnings": _safe_list(source.get("warnings")),
        "metadata": _metadata(source.get("metadata"), metadata, generated_at),
    }
    if not source:
        snapshot["warnings"].append("pool summary input is empty or invalid")
    return snapshot


def build_strategy_snapshot_payload(
    comparison=None,
    pool_summary=None,
    metadata=None,
    schema_version="1.0",
    generated_at=None,
):
    timestamp = _now_iso() if generated_at is None else generated_at
    return {
        "schema_version": schema_version,
        "snapshot_type": "strategy_snapshot_payload",
        "comparison": export_preset_comparison_snapshot(
            comparison,
            schema_version=schema_version,
            generated_at=timestamp,
            metadata=metadata,
        )
        if comparison is not None
        else None,
        "pool_summary": export_preset_pool_summary_snapshot(
            pool_summary,
            schema_version=schema_version,
            generated_at=timestamp,
            metadata=metadata,
        )
        if pool_summary is not None
        else None,
        "metadata": _metadata({}, metadata, timestamp),
    }


__all__ = [
    "build_strategy_snapshot_payload",
    "export_preset_comparison_snapshot",
    "export_preset_pool_summary_snapshot",
]
