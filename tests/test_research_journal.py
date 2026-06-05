import copy
import importlib

from memory.research_journal import JOURNAL_FIELDS, build_research_journal


def snapshot():
    return {
        "snapshot_id": "snapshot-AAA-001",
        "snapshot_timestamp": "2026-06-01T00:00:00+00:00",
        "snapshot_ticker": "AAA",
        "snapshot_name": "Alpha Sample",
        "snapshot_status": "Available",
        "snapshot_summary": "Research snapshot for AAA Alpha Sample is available.",
        "strategy_score": 73,
        "research_priority_score": 81,
        "priority_stability_score": 95,
        "architecture_audit_score": 100,
        "event_confidence_score": 86,
        "event_confluence_score": 82,
        "fundamental_snapshot": {
            "fundamental_data_quality_label": "usable",
            "fundamental_diagnostics_summary": "Fundamental diagnostics have enough fields for research review.",
        },
        "priority_snapshot": {
            "research_priority_score": 81,
            "research_priority_level": "priority_research",
            "research_priority_reasons": ["Evidence chain is complete enough for deeper research."],
            "research_priority_warnings": ["Priority evidence should be reviewed with latest data quality notes."],
        },
        "event_snapshot": {
            "event_research_summary": "Event context is available for evidence review.",
            "event_key_evidence": ["Event evidence source is documented."],
            "event_key_risks": ["Event evidence may need recency validation."],
            "event_validation_focus": ["Confirm source quality and timing."],
            "event_summary_warnings": ["Event evidence has limited detail."],
        },
        "pipeline_snapshot": {
            "research_pipeline_status": "Healthy",
            "research_pipeline_conflicts": [],
            "research_pipeline_warnings": ["Pipeline still depends on caller-provided fields."],
            "research_pipeline_summary": "Pipeline is complete enough for research review.",
        },
        "project_snapshot": {
            "data_source_assessment_note": "Data source boundary remains unchanged.",
        },
    }


def timeline():
    return {
        "timeline_id": "timeline-AAA-001",
        "timeline_ticker": "AAA",
        "timeline_name": "Alpha Sample",
        "timeline_snapshot_count": 2,
        "timeline_start_time": "2026-06-01T00:00:00+00:00",
        "timeline_end_time": "2026-06-02T00:00:00+00:00",
        "timeline_status": "Available",
        "timeline_direction": "Improving",
        "timeline_change_summary": "Research timeline for AAA Alpha Sample is available; tracked changes=2.",
        "timeline_key_changes": [
            {
                "section": "priority_snapshot",
                "field": "research_priority_score",
                "from": 70,
                "to": 81,
                "direction": "Improving",
            },
            {
                "section": "pipeline_snapshot",
                "field": "research_pipeline_status",
                "from": "Watch",
                "to": "Healthy",
                "direction": "Improving",
            },
        ],
        "timeline_warnings": [],
    }


def flattened_text(value):
    if isinstance(value, dict):
        return " ".join(flattened_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flattened_text(item) for item in value)
    return str(value)


def test_empty_input_safe_return():
    journal = build_research_journal()

    assert list(journal.keys()) == JOURNAL_FIELDS
    assert journal["journal_status"] == "Incomplete"
    assert journal["journal_ticker"] is None


def test_snapshot_only_returns_incomplete():
    journal = build_research_journal(snapshot=snapshot())

    assert journal["journal_status"] == "Incomplete"
    assert journal["journal_ticker"] == "AAA"
    assert any("Timeline" in warning for warning in journal["journal_warnings"])


def test_snapshot_and_timeline_return_available():
    journal = build_research_journal(snapshot(), timeline())

    assert journal["journal_status"] == "Available"
    assert journal["journal_ticker"] == "AAA"
    assert journal["journal_period"] == "2026-06-01T00:00:00+00:00 to 2026-06-02T00:00:00+00:00"


def test_generates_journal_summary():
    journal = build_research_journal(snapshot(), timeline())

    assert "Research journal for AAA Alpha Sample" in journal["journal_summary"]
    assert "Research snapshot for AAA" in journal["journal_summary"]


def test_generates_journal_observations():
    journal = build_research_journal(snapshot(), timeline())

    assert journal["journal_observations"]
    assert any("priority_research" in item for item in journal["journal_observations"])
    assert any("timeline" in item for item in journal["journal_observations"])


def test_generates_journal_risk_notes():
    journal = build_research_journal(snapshot(), timeline())

    assert journal["journal_risk_notes"]
    assert any("validation" in item for item in journal["journal_risk_notes"])


def test_generates_journal_followup_questions():
    journal = build_research_journal(snapshot(), timeline())

    assert journal["journal_followup_questions"]
    assert all(item.endswith("?") for item in journal["journal_followup_questions"])


def test_generates_journal_agent_tasks():
    journal = build_research_journal(snapshot(), timeline())

    assert journal["journal_agent_tasks"]
    assert any("research" in item for item in journal["journal_agent_tasks"])


def test_input_objects_are_not_modified():
    source_snapshot = snapshot()
    source_timeline = timeline()
    before_snapshot = copy.deepcopy(source_snapshot)
    before_timeline = copy.deepcopy(source_timeline)

    build_research_journal(source_snapshot, source_timeline)

    assert source_snapshot == before_snapshot
    assert source_timeline == before_timeline


def test_forbidden_terms_are_removed_from_journal_output():
    source_snapshot = snapshot()
    source_snapshot["snapshot_summary"] = "research note contains b" + "uy and \u4e70\u5165 wording"
    source_snapshot["event_snapshot"]["event_validation_focus"] = ["avoid s" + "ell wording"]

    journal = build_research_journal(source_snapshot, timeline())
    text = flattened_text(journal).lower()
    forbidden_terms = [
        "b" + "uy",
        "s" + "ell",
        "h" + "old",
        "target" + " price",
        "reco" + "mmend",
        "strong " + "b" + "uy",
        "\u4e70\u5165",
        "\u5356\u51fa",
        "\u6301\u6709",
        "\u76ee\u6807\u4ef7",
        "\u6295\u8d44\u5efa\u8bae",
    ]

    assert all(term not in text for term in forbidden_terms)


def test_module_importable():
    assert importlib.import_module("memory.research_journal")


def test_scoring_fields_are_not_changed_by_journal_builder():
    source_snapshot = snapshot()
    source_timeline = timeline()
    before = copy.deepcopy(source_snapshot)

    build_research_journal(source_snapshot, source_timeline)

    assert source_snapshot["strategy_score"] == before["strategy_score"]
    assert source_snapshot["research_priority_score"] == before["research_priority_score"]
    assert source_snapshot["priority_stability_score"] == before["priority_stability_score"]
    assert source_snapshot["architecture_audit_score"] == before["architecture_audit_score"]
    assert source_snapshot["event_confidence_score"] == before["event_confidence_score"]
    assert source_snapshot["event_confluence_score"] == before["event_confluence_score"]
