from pathlib import Path

import pandas as pd

from audit.release_report import AUDIT_CACHE_DIR, build_release_report


def _research_frame():
    frame = pd.DataFrame(
        {
            "ticker": ["000001", "000002", "000003"],
            "name": ["A", "B", "C"],
            "latest_price": [10, 11, 12],
            "pct_change": [1, 2, -1],
            "turnover": [100_000_000, 90_000_000, 80_000_000],
            "turnover_rate": [2, 3, 1],
            "volume_ratio": [1.2, 1.4, 0.8],
            "real_technical_score": [80, 65, 50],
            "fundamental_research_score": [82, 60, 40],
            "capital_flow_score": [75, 55, 35],
            "news_event_score": [70, 50, 45],
            "industry_strength_score": [72, 55, 45],
            "activated_composite_score": [78, 60, 42],
            "research_bucket": ["Core Research", "Watch Research", "Excluded / Low Priority"],
            "research_rank": [1, 2, 3],
            "research_selected_reason": ["core", "watch", ""],
            "research_scheduler_warning": ["", "", "low priority"],
        }
    )
    frame.attrs["pipeline_mode"] = "Scheduler"
    frame.attrs["scheduler_status"] = "OK"
    frame.attrs["scheduler_report_df"] = pd.DataFrame(
        [
            {"stage_name": "Stage 1: Full Market Quick Scan", "stage_input_rows": 10, "stage_output_rows": 8, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
            {"stage_name": "Stage 2: Technical Filter", "stage_input_rows": 8, "stage_output_rows": 5, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
            {"stage_name": "Stage 3: Research Scoring", "stage_input_rows": 5, "stage_output_rows": 3, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
            {"stage_name": "Stage 4: Deep Event Layer", "stage_input_rows": 3, "stage_output_rows": 3, "stage_seconds": 0.1, "stage_status": "OK", "stage_warning": ""},
        ]
    )
    return frame


def test_release_report_generates_markdown_and_cache_files():
    result = build_release_report(_research_frame())

    assert "Release Candidate" in result["release_report_markdown"]
    assert Path(result["system_audit_path"]).exists()
    assert Path(result["pipeline_audit_path"]).exists()
    assert Path(result["release_report_path"]).exists()


def test_audit_cache_path_is_writable():
    AUDIT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    probe = AUDIT_CACHE_DIR / "write_probe.txt"
    probe.write_text("ok", encoding="utf-8")

    assert probe.read_text(encoding="utf-8") == "ok"
