import copy
import importlib

from memory.research_timeline import TIMELINE_FIELDS, build_research_timeline


def snapshot(
    timestamp,
    ticker="AAA",
    name="Alpha Sample",
    priority_score=70,
    priority_level="watch_research",
    event_confidence=60,
    event_level="Medium",
    event_confluence="Mixed",
    pipeline_status="Watch",
    architecture_score=90,
    strategy_score=73,
):
    return {
        "snapshot_id": f"snapshot-{ticker}-{timestamp}",
        "snapshot_timestamp": timestamp,
        "snapshot_ticker": ticker,
        "snapshot_name": name,
        "snapshot_status": "Available",
        "strategy_score": strategy_score,
        "research_priority_score": priority_score,
        "priority_stability_score": 88,
        "architecture_audit_score": architecture_score,
        "event_confidence_score": event_confidence,
        "event_confluence_score": 61,
        "priority_snapshot": {
            "research_priority_score": priority_score,
            "research_priority_level": priority_level,
            "priority_stability_label": "Stable",
            "priority_stability_score": 88,
        },
        "event_snapshot": {
            "event_available": True,
            "event_diagnostic_level": event_level,
            "event_confidence_score": event_confidence,
            "event_confluence_label": event_confluence,
            "event_confluence_score": 61,
            "event_research_level": event_level,
        },
        "pipeline_snapshot": {
            "architecture_audit_label": "Pass",
            "architecture_audit_score": architecture_score,
            "research_pipeline_status": pipeline_status,
        },
    }


def test_empty_input_safe_return():
    timeline = build_research_timeline([])

    assert list(timeline.keys()) == TIMELINE_FIELDS
    assert timeline["timeline_status"] == "Incomplete"
    assert timeline["timeline_snapshot_count"] == 0
    assert timeline["timeline_direction"] == "Unavailable"


def test_single_snapshot_returns_incomplete():
    timeline = build_research_timeline([snapshot("2026-06-01T00:00:00+00:00")])

    assert timeline["timeline_status"] == "Incomplete"
    assert timeline["timeline_snapshot_count"] == 1
    assert any("At least two snapshots" in warning for warning in timeline["timeline_warnings"])


def test_multiple_snapshots_generate_available_timeline():
    timeline = build_research_timeline(
        [
            snapshot("2026-06-01T00:00:00+00:00"),
            snapshot("2026-06-02T00:00:00+00:00", priority_score=72),
        ]
    )

    assert timeline["timeline_status"] == "Available"
    assert timeline["timeline_ticker"] == "AAA"
    assert timeline["timeline_snapshot_count"] == 2


def test_snapshot_timestamp_sorting():
    timeline = build_research_timeline(
        [
            snapshot("2026-06-03T00:00:00+00:00", priority_score=80),
            snapshot("2026-06-01T00:00:00+00:00", priority_score=60),
        ]
    )

    assert timeline["timeline_start_time"] == "2026-06-01T00:00:00+00:00"
    assert timeline["timeline_end_time"] == "2026-06-03T00:00:00+00:00"
    assert timeline["timeline_priority_trend"]["end"]["research_priority_score"] == 80


def test_ticker_inconsistent_warning():
    timeline = build_research_timeline(
        [
            snapshot("2026-06-01T00:00:00+00:00", ticker="AAA"),
            snapshot("2026-06-02T00:00:00+00:00", ticker="BBB"),
        ]
    )

    assert any("inconsistent snapshot_ticker" in warning for warning in timeline["timeline_warnings"])
    assert timeline["timeline_snapshot_count"] == 1


def test_priority_trend_detection():
    timeline = build_research_timeline(
        [
            snapshot("2026-06-01T00:00:00+00:00", priority_score=50),
            snapshot("2026-06-02T00:00:00+00:00", priority_score=75, priority_level="priority_research"),
        ]
    )

    trend = timeline["timeline_priority_trend"]
    assert trend["direction"] == "Improving"
    assert any(change["field"] == "research_priority_score" for change in trend["changed_fields"])


def test_event_trend_detection():
    timeline = build_research_timeline(
        [
            snapshot("2026-06-01T00:00:00+00:00", event_confidence=45, event_level="Weak"),
            snapshot(
                "2026-06-02T00:00:00+00:00",
                event_confidence=82,
                event_level="Strong",
                event_confluence="Supportive",
            ),
        ]
    )

    assert timeline["timeline_event_trend"]["direction"] == "Improving"
    assert any(
        change["field"] == "event_confidence_score"
        for change in timeline["timeline_event_trend"]["changed_fields"]
    )


def test_pipeline_trend_detection():
    timeline = build_research_timeline(
        [
            snapshot("2026-06-01T00:00:00+00:00", pipeline_status="Conflict", architecture_score=70),
            snapshot("2026-06-02T00:00:00+00:00", pipeline_status="Healthy", architecture_score=95),
        ]
    )

    assert timeline["timeline_pipeline_trend"]["direction"] == "Improving"
    assert any(
        change["field"] == "research_pipeline_status"
        for change in timeline["timeline_pipeline_trend"]["changed_fields"]
    )


def test_timeline_direction_judgment():
    improving = build_research_timeline(
        [
            snapshot("2026-06-01T00:00:00+00:00", priority_score=40, event_confidence=40, pipeline_status="Conflict"),
            snapshot(
                "2026-06-02T00:00:00+00:00",
                priority_score=80,
                priority_level="priority_research",
                event_confidence=82,
                event_level="Strong",
                event_confluence="Supportive",
                pipeline_status="Healthy",
            ),
        ]
    )
    mixed = build_research_timeline(
        [
            snapshot("2026-06-01T00:00:00+00:00", priority_score=80, event_confidence=40),
            snapshot("2026-06-02T00:00:00+00:00", priority_score=60, event_confidence=82, event_level="Strong"),
        ]
    )

    assert improving["timeline_direction"] == "Improving"
    assert mixed["timeline_direction"] == "Mixed"


def test_input_objects_are_not_modified():
    snapshots = [
        snapshot("2026-06-01T00:00:00+00:00", priority_score=60),
        snapshot("2026-06-02T00:00:00+00:00", priority_score=70),
    ]
    before = copy.deepcopy(snapshots)

    build_research_timeline(snapshots)

    assert snapshots == before


def test_module_importable():
    assert importlib.import_module("memory.research_timeline")


def test_scoring_fields_are_not_changed_by_timeline_builder():
    snapshots = [
        snapshot("2026-06-01T00:00:00+00:00", priority_score=60, strategy_score=73),
        snapshot("2026-06-02T00:00:00+00:00", priority_score=70, strategy_score=74),
    ]
    before = copy.deepcopy(snapshots)

    build_research_timeline(snapshots)

    assert snapshots[0]["strategy_score"] == before[0]["strategy_score"]
    assert snapshots[0]["research_priority_score"] == before[0]["research_priority_score"]
    assert snapshots[0]["priority_stability_score"] == before[0]["priority_stability_score"]
    assert snapshots[0]["architecture_audit_score"] == before[0]["architecture_audit_score"]
    assert snapshots[0]["event_confidence_score"] == before[0]["event_confidence_score"]
    assert snapshots[0]["event_confluence_score"] == before[0]["event_confluence_score"]
