"""Static UI readiness checks for product pages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from data.source_center import SOURCE_STATUS_COLUMNS


UI_AUDIT_COLUMNS = ["section_name", "status", "required_items", "missing_items", "audit_note"]

UI_REQUIREMENTS = {
    "Dashboard": [
        "Universe Size",
        "Realtime Rows",
        "KLine Status",
        "Fundamental Status",
        "Capital Flow Status",
        "News Status",
        "Core Count",
        "Watch Count",
        "Exclude Count",
        "Total Runtime",
    ],
    "Selection Results": [
        "ticker",
        "name",
        "research_bucket",
        "research_rank",
        "activated_composite_score",
        "real_technical_score",
        "fundamental_research_score",
        "capital_flow_score",
        "news_event_score",
        "research_selected_reason",
        "research_scheduler_warning",
    ],
    "Research Workstation": [
        "technical_risk_flags",
        "fundamental_risks",
        "capital_flow_score",
        "news_event_score",
        "Data Source Diagnostics",
    ],
    "Data Source Center": ["source_name", "status", "rows", "cache_status", "last_error", "used_in_model"],
}

ALIASES = {
    "Realtime Rows": ["Raw Count", "raw_count", "Realtime Rows"],
    "KLine Status": ["kline_status", "K绾", "KLine Status"],
    "Fundamental Status": ["fundamental_data_status", "Fundamental Status"],
    "Capital Flow Status": ["capital_flow_status", "Capital Flow Status"],
    "News Status": ["news_status", "News Status"],
    "Core Count": ["core_count", "Core Count"],
    "Watch Count": ["watch_count", "Watch Count"],
    "Exclude Count": ["exclude_count", "Exclude Count"],
    "Total Runtime": ["scheduler_total_seconds", "Total Seconds", "Total Runtime"],
}


def _ui_text() -> str:
    try:
        return Path("ui/product_ui.py").read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _present(text: str, item: str) -> bool:
    candidates = ALIASES.get(item, [item])
    return any(candidate in text for candidate in candidates)


def run_ui_audit(research_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Audit whether product UI code is prepared to show release-check fields."""
    _ = research_df
    text = _ui_text()
    rows: list[dict[str, Any]] = []
    for section, required in UI_REQUIREMENTS.items():
        if section == "Data Source Center":
            missing = [item for item in required if item not in SOURCE_STATUS_COLUMNS and item not in text]
        else:
            missing = [item for item in required if not _present(text, item)]
        status = "PASS" if not missing else "WARN"
        rows.append(
            {
                "section_name": section,
                "status": status,
                "required_items": ", ".join(required),
                "missing_items": ", ".join(missing),
                "audit_note": "UI fields are statically available." if not missing else "UI should expose or label these fields more explicitly.",
            }
        )
    return pd.DataFrame(rows, columns=UI_AUDIT_COLUMNS)


__all__ = ["UI_AUDIT_COLUMNS", "UI_REQUIREMENTS", "run_ui_audit"]
