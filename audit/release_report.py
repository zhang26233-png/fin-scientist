"""Release report builder for v7.0.1 audit output."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from audit.system_audit import run_system_audit


AUDIT_CACHE_DIR = Path("cache/audit")
SYSTEM_AUDIT_CACHE = AUDIT_CACHE_DIR / "latest_system_audit.csv"
PIPELINE_AUDIT_CACHE = AUDIT_CACHE_DIR / "latest_pipeline_audit.csv"
RELEASE_REPORT_CACHE = AUDIT_CACHE_DIR / "latest_release_report.md"


def _count_status(frame: pd.DataFrame) -> str:
    if frame is None or frame.empty or "status" not in frame.columns:
        return "PASS=0 WARN=0 FAIL=0"
    counts = frame["status"].fillna("").astype(str).str.upper().value_counts()
    return f"PASS={int(counts.get('PASS', 0))} WARN={int(counts.get('WARN', 0))} FAIL={int(counts.get('FAIL', 0))}"


def _bucket_counts(df: pd.DataFrame) -> dict[str, int]:
    if df is None or df.empty or "research_bucket" not in df.columns:
        return {"core": 0, "watch": 0, "exclude": 0}
    bucket = df["research_bucket"].fillna("").astype(str)
    return {
        "core": int(bucket.eq("Core Research").sum()),
        "watch": int(bucket.eq("Watch Research").sum()),
        "exclude": int(bucket.eq("Excluded / Low Priority").sum()),
    }


def _known_issues(audit: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in ["module_audit", "data_field_audit", "pipeline_audit", "ui_audit"]:
        frame = audit.get(key)
        if isinstance(frame, pd.DataFrame) and "status" in frame.columns:
            for _, row in frame[frame["status"].isin(["WARN", "FAIL"])].iterrows():
                label = row.get("module_name") or row.get("field_name") or row.get("stage_name") or row.get("section_name") or key
                note = row.get("audit_note") or row.get("warning") or row.get("missing_items") or ""
                issues.append(f"- {label}: {row.get('status')} {note}".strip())
    return issues or ["- No blocking issue found in the current audit frames."]


def build_release_report(research_df: pd.DataFrame | None = None, version: str = "v7.0.1") -> dict[str, Any]:
    """Run audits, write CSV/Markdown artifacts, and return report metadata."""
    source = research_df.copy(deep=True) if isinstance(research_df, pd.DataFrame) else pd.DataFrame()
    audit = run_system_audit(source)
    AUDIT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    system_frame = pd.concat(
        [
            audit["module_audit"].assign(audit_type="module"),
            audit["data_field_audit"].rename(columns={"field_name": "module_name"}).assign(audit_type="data_field"),
            audit["ui_audit"].rename(columns={"section_name": "module_name"}).assign(audit_type="ui"),
        ],
        ignore_index=True,
        sort=False,
    )
    system_frame.to_csv(SYSTEM_AUDIT_CACHE, index=False, encoding="utf-8-sig")
    audit["pipeline_audit"].to_csv(PIPELINE_AUDIT_CACHE, index=False, encoding="utf-8-sig")

    counts = _bucket_counts(source)
    issues = _known_issues(audit)
    rc_ready = audit["system_status"] in {"PASS", "WARN"} and audit["research_result_status"] != "Unavailable"
    markdown = "\n".join(
        [
            f"# Fin-Scientist {version} System Audit Release Candidate",
            "",
            "All outputs are only for learning and research and do not constitute investment advice.",
            "",
            "## 1. Current Version",
            f"- Version: {version}",
            "- Stage: System Audit Release Candidate",
            "",
            "## 2. Module Status Overview",
            f"- {_count_status(audit['module_audit'])}",
            "",
            "## 3. Data Source Status",
            f"- Rows: {len(audit['data_source_status'])}",
            "",
            "## 4. Pipeline Stage Status",
            f"- {_count_status(audit['pipeline_audit'])}",
            "",
            "## 5. UI Integration Status",
            f"- {_count_status(audit['ui_audit'])}",
            "",
            "## 6. Core / Watch / Exclude Counts",
            f"- Core Research: {counts['core']}",
            f"- Watch Research: {counts['watch']}",
            f"- Excluded / Low Priority: {counts['exclude']}",
            "",
            "## 7. Known Issues",
            *issues[:50],
            "",
            "## 8. Next Version Suggestions",
            "- Continue with v7.1.0 Unified Research Ranking Engine after the audit remains stable on live and cache data.",
            "- Keep ranking explanations research-only and preserve the existing scoring boundary.",
            "",
            "## 9. Release Candidate Standard",
            f"- System Status: {audit['system_status']}",
            f"- Research Result Status: {audit['research_result_status']}",
            f"- Release Candidate Ready: {'YES' if rc_ready else 'NO'}",
        ]
    )
    RELEASE_REPORT_CACHE.write_text(markdown, encoding="utf-8")
    return {
        **audit,
        "release_report_markdown": markdown,
        "system_audit_path": str(SYSTEM_AUDIT_CACHE),
        "pipeline_audit_path": str(PIPELINE_AUDIT_CACHE),
        "release_report_path": str(RELEASE_REPORT_CACHE),
        "release_candidate_ready": bool(rc_ready),
    }


__all__ = [
    "AUDIT_CACHE_DIR",
    "PIPELINE_AUDIT_CACHE",
    "RELEASE_REPORT_CACHE",
    "SYSTEM_AUDIT_CACHE",
    "build_release_report",
]
