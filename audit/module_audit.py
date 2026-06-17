"""Module-level release checks for the v7.0.1 system audit."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pandas as pd


MODULE_AUDIT_COLUMNS = [
    "module_name",
    "module_type",
    "status",
    "is_importable",
    "is_callable",
    "is_connected_to_pipeline",
    "is_connected_to_ui",
    "required_fields_present",
    "sample_rows",
    "last_error",
    "audit_note",
]


MODULE_SPECS = [
    {
        "module_name": "Realtime Layer",
        "module_type": "Data Layer",
        "import_path": "data.a_share_loader",
        "callable_name": "load_a_share_universe",
        "fields": ["ticker", "name", "latest_price", "pct_change", "turnover"],
        "pipeline_tokens": ["load_a_share_universe"],
        "ui_tokens": ["Universe Size", "Realtime", "data_source"],
    },
    {
        "module_name": "KLine Layer",
        "module_type": "Data Layer",
        "import_path": "data.kline_loader",
        "callable_name": "build_price_history_dict",
        "fields": ["technical_history_available", "real_technical_score"],
        "pipeline_tokens": ["build_price_history_dict", "kline_enabled"],
        "ui_tokens": ["kline_status", "KLine", "K绾"],
    },
    {
        "module_name": "Technical Engine",
        "module_type": "Research Engine",
        "import_path": "technical.indicator_engine",
        "callable_name": "build_real_technical_indicators",
        "fields": ["real_technical_score", "technical_signal_summary"],
        "pipeline_tokens": ["build_real_technical_indicators"],
        "ui_tokens": ["real_technical_score", "technical_risk_flags"],
    },
    {
        "module_name": "Fundamental Engine",
        "module_type": "Research Engine",
        "import_path": "fundamental.fundamental_engine",
        "callable_name": "build_fundamental_research",
        "fields": ["fundamental_research_score", "fundamental_data_status"],
        "pipeline_tokens": ["build_fundamental_research"],
        "ui_tokens": ["fundamental_research_score", "fundamental_data_status"],
    },
    {
        "module_name": "Capital Flow Engine",
        "module_type": "Research Engine",
        "import_path": "capital_flow.capital_engine",
        "callable_name": "build_capital_scores",
        "fields": ["capital_flow_score", "capital_flow_strength"],
        "pipeline_tokens": ["build_capital_scores"],
        "ui_tokens": ["capital_flow_score", "capital_flow_status"],
    },
    {
        "module_name": "News Event Engine",
        "module_type": "Research Engine",
        "import_path": "news.event_engine",
        "callable_name": "build_news_event_scores",
        "fields": ["news_event_score", "news_sentiment_label"],
        "pipeline_tokens": ["build_news_event_scores"],
        "ui_tokens": ["news_event_score", "news_status"],
    },
    {
        "module_name": "Industry Layer",
        "module_type": "Data Layer",
        "import_path": "data.industry_loader",
        "callable_name": "build_industry_dataset",
        "fields": ["industry_strength_score", "concept_heat_score"],
        "pipeline_tokens": ["build_industry_dataset"],
        "ui_tokens": ["industry_strength_score", "industry_status"],
    },
    {
        "module_name": "Source Center",
        "module_type": "Diagnostics",
        "import_path": "data.source_center",
        "callable_name": "build_data_source_status",
        "fields": ["source_name", "status", "rows", "cache_status", "used_in_model"],
        "pipeline_tokens": ["build_data_source_status"],
        "ui_tokens": ["render_data_source_center_page", "build_data_source_status"],
    },
    {
        "module_name": "Research Activation",
        "module_type": "Scoring Layer",
        "import_path": "research.score_activation",
        "callable_name": "activate_research_scores",
        "fields": ["activated_composite_score", "scheduler_ready_score"],
        "pipeline_tokens": ["activate_research_scores"],
        "ui_tokens": ["activated_composite_score", "activated_selection_score"],
    },
    {
        "module_name": "Pipeline Scheduler",
        "module_type": "Scheduler",
        "import_path": "pipeline.scheduler",
        "callable_name": "run_scheduled_pipeline",
        "fields": ["research_bucket", "research_rank", "research_scheduler_warning"],
        "pipeline_tokens": ["run_scheduled_pipeline"],
        "ui_tokens": ["render_scheduler_pipeline_page", "scheduler_status"],
    },
    {
        "module_name": "UI Product Page",
        "module_type": "UI",
        "import_path": "ui.product_ui",
        "callable_name": "render_product_page",
        "fields": ["research_bucket", "research_rank"],
        "pipeline_tokens": ["render_product_page"],
        "ui_tokens": ["NAVIGATION_PAGES", "render_product_page"],
    },
    {
        "module_name": "Cache Layer",
        "module_type": "Cache",
        "import_path": "pipeline.scheduler",
        "callable_name": "load_scheduler_cache",
        "fields": [],
        "pipeline_tokens": ["load_scheduler_cache", "SCHEDULER_RESULT_CACHE"],
        "ui_tokens": ["cache_status", "Data Source"],
    },
]


def _read_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _contains_any(text: str, tokens: list[str]) -> bool:
    return any(token and token in text for token in tokens)


def _field_status(df: pd.DataFrame, fields: list[str]) -> tuple[bool, str]:
    if not fields:
        return True, "No runtime fields required."
    missing = [field for field in fields if field not in df.columns]
    if missing:
        return False, "Missing fields: " + ", ".join(missing)
    return True, "Required fields present."


def run_module_audit(research_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Audit importability, callable boundaries, pipeline wiring, UI wiring, and fields."""
    source = research_df.copy(deep=True) if isinstance(research_df, pd.DataFrame) else pd.DataFrame()
    pipeline_text = _read_text("pipeline/live_runner.py") + "\n" + _read_text("pipeline/scheduler.py")
    ui_text = _read_text("ui/product_ui.py") + "\n" + _read_text("app.py")
    rows: list[dict[str, Any]] = []

    for spec in MODULE_SPECS:
        is_importable = False
        is_callable = False
        last_error = ""
        try:
            module = importlib.import_module(str(spec["import_path"]))
            is_importable = True
            is_callable = callable(getattr(module, str(spec["callable_name"]), None))
        except Exception as exc:
            last_error = repr(exc)

        connected_pipeline = _contains_any(pipeline_text, list(spec["pipeline_tokens"]))
        connected_ui = _contains_any(ui_text, list(spec["ui_tokens"]))
        fields_present, field_note = _field_status(source, list(spec["fields"]))
        sample_rows = int(len(source))

        if is_importable and is_callable and connected_pipeline and connected_ui and fields_present:
            status = "PASS"
        elif is_importable and is_callable and connected_pipeline and connected_ui:
            status = "WARN"
        elif is_importable:
            status = "WARN"
        else:
            status = "FAIL"

        rows.append(
            {
                "module_name": spec["module_name"],
                "module_type": spec["module_type"],
                "status": status,
                "is_importable": bool(is_importable),
                "is_callable": bool(is_callable),
                "is_connected_to_pipeline": bool(connected_pipeline),
                "is_connected_to_ui": bool(connected_ui),
                "required_fields_present": bool(fields_present),
                "sample_rows": sample_rows,
                "last_error": last_error,
                "audit_note": field_note,
            }
        )
    return pd.DataFrame(rows, columns=MODULE_AUDIT_COLUMNS)


__all__ = ["MODULE_AUDIT_COLUMNS", "MODULE_SPECS", "run_module_audit"]
