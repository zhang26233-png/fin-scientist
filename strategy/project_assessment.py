"""Read-only pre-v2 project assessment helpers."""

import copy
import importlib
import math
from pathlib import Path

import pandas as pd


PROJECT_ASSESSMENT_FIELDS = [
    "project_assessment_status",
    "project_assessment_score",
    "architecture_assessment_note",
    "field_registry_assessment_note",
    "test_coverage_assessment_note",
    "ui_readability_assessment_note",
    "data_source_assessment_note",
    "scoring_boundary_assessment_note",
    "pre_v2_readiness_level",
    "pre_v2_blockers",
    "pre_v2_recommendations",
]

REQUIRED_ASSESSMENT_FIELDS = [
    "technical_grade",
    "fundamental_grade",
    "industry_relative_quality_label",
    "composite_research_grade",
    "research_priority_level",
    "priority_stability_label",
    "architecture_audit_label",
    "event_diagnostic_level",
    "event_confluence_label",
    "event_research_level",
    "research_pipeline_status",
]

REQUIRED_MODULES = [
    "strategy.technical",
    "strategy.fundamental",
    "strategy.fundamental_relative",
    "strategy.fundamental_diagnostics",
    "strategy.confluence",
    "strategy.composite_profile",
    "strategy.priority_stability",
    "strategy.architecture_audit",
    "strategy.event_context",
    "strategy.event_diagnostics",
    "strategy.event_confluence",
    "strategy.event_research_summary",
    "strategy.research_pipeline_audit",
    "strategy.preview",
]

EXPECTED_TEST_FILES = [
    "tests/test_strategy_preview.py",
    "tests/test_strategy_architecture_audit.py",
    "tests/test_strategy_research_pipeline_audit.py",
    "tests/test_strategy_event_context.py",
    "tests/test_strategy_event_diagnostics.py",
    "tests/test_strategy_event_confluence.py",
    "tests/test_strategy_event_research_summary.py",
    "tests/test_module_imports.py",
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


def _row_dict(row):
    if hasattr(row, "to_dict"):
        return copy.deepcopy(row.to_dict())
    if isinstance(row, dict):
        return copy.deepcopy(row)
    return {}


def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _text(value):
    return "" if _is_missing(value) else str(value).strip()


def _missing_fields(row):
    return [field for field in REQUIRED_ASSESSMENT_FIELDS if _is_missing(row.get(field))]


def _missing_modules(module_names=None):
    missing = []
    for module_name in module_names or REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            missing.append(f"{module_name} unavailable: {exc.__class__.__name__}")
    return missing


def _missing_tests(paths=None):
    missing = []
    for path in paths or EXPECTED_TEST_FILES:
        if not Path(path).exists():
            missing.append(path)
    return missing


def _architecture_note(missing_modules, row):
    pipeline = _text(row.get("research_pipeline_status"))
    audit = _text(row.get("architecture_audit_label"))
    if missing_modules:
        return "Architecture modules are incomplete for pre-v2 review."
    if pipeline in {"Conflict", "Incomplete"}:
        return "Architecture chain is present but pipeline status needs review before v2."
    if audit in {"Review", "Watch", "Unavailable"}:
        return "Architecture audit is available but has review items before v2."
    return "Architecture modules are present and suitable for pre-v2 review."


def _field_registry_note(row):
    field_count = len(row)
    if field_count >= 140:
        return f"Field registry is large with {field_count} fields; field grouping or export views need cleanup before v2."
    if field_count >= 100:
        return f"Field registry is broad with {field_count} fields; v2 should add grouped memory views."
    return f"Field registry size is manageable with {field_count} fields for current review."


def _test_note(missing_tests):
    if missing_tests:
        return "Some expected strategy test files are missing for pre-v2 review."
    return "Key strategy, event, pipeline, and import tests are present for pre-v2 review."


def _ui_note(row):
    field_count = len(row)
    if field_count >= 140:
        return "Preview UI is likely overloaded; grouped panels or export-first views should be prepared before v2."
    if field_count >= 100:
        return "Preview UI is dense; v2 should improve event and pipeline field grouping."
    return "Preview UI field volume is acceptable for the current prototype."


def _data_source_note():
    return "Data source boundaries remain unchanged; v2 memory work can proceed without adding new feeds."


def _scoring_boundary_note(row):
    pipeline = _text(row.get("research_pipeline_status"))
    if pipeline == "Conflict":
        return "Scoring boundary is intact, but pipeline conflicts need review before memory persistence."
    return "Scoring boundary remains read-only for assessment fields and separate from ranking fields."


def _blockers(row, missing_fields, missing_modules, missing_tests):
    blockers = []
    if missing_modules:
        blockers.append("required strategy modules unavailable")
    if len(missing_fields) >= 4:
        blockers.append("multiple required assessment fields missing")
    pipeline = _text(row.get("research_pipeline_status"))
    if pipeline == "Conflict":
        blockers.append("research pipeline conflicts unresolved")
    if missing_tests:
        blockers.append("expected test coverage files missing")
    if len(row) >= 160:
        blockers.append("preview field volume needs grouping before v2 memory work")
    return list(dict.fromkeys(blockers))


def _assessment_score(row, blockers, missing_fields, missing_modules, missing_tests):
    score = 90
    score -= min(25, len(missing_fields) * 4)
    score -= min(30, len(missing_modules) * 10)
    score -= min(20, len(missing_tests) * 4)
    if _text(row.get("research_pipeline_status")) == "Watch":
        score -= 8
    if _text(row.get("research_pipeline_status")) == "Incomplete":
        score -= 15
    if _text(row.get("research_pipeline_status")) == "Conflict":
        score -= 25
    if len(row) >= 140:
        score -= 8
    if blockers:
        score -= min(20, len(blockers) * 5)
    return max(0, min(100, int(round(score))))


def _status(score, blockers):
    if blockers:
        return "Not Ready" if score < 70 else "Watch"
    if score >= 82:
        return "Ready"
    if score >= 65:
        return "Watch"
    return "Not Ready"


def _readiness(status):
    if status == "Ready":
        return "High"
    if status == "Watch":
        return "Medium"
    return "Low"


def _recommendations(status, blockers):
    items = []
    if "preview field volume needs grouping before v2 memory work" in blockers:
        items.append("Group event and pipeline fields before adding persistent research memory.")
    if "research pipeline conflicts unresolved" in blockers:
        items.append("Resolve pipeline conflicts before persisting research memory snapshots.")
    if "multiple required assessment fields missing" in blockers:
        items.append("Complete missing pipeline fields before v2 schema work.")
    if "expected test coverage files missing" in blockers:
        items.append("Restore expected strategy tests before v2 memory work.")
    if status == "Ready":
        items.append("Proceed toward Research Memory Foundation with schema and export planning first.")
    elif not items:
        items.append("Use v1.9.1 to tighten consistency checks and UI grouping before v2.")
    return list(dict.fromkeys(items))[:4]


def build_project_assessment_row(row):
    row_data = _row_dict(row)
    missing_fields = _missing_fields(row_data)
    missing_modules = _missing_modules()
    missing_tests = _missing_tests()
    blockers = _blockers(row_data, missing_fields, missing_modules, missing_tests)
    score = _assessment_score(row_data, blockers, missing_fields, missing_modules, missing_tests)
    status = _status(score, blockers)
    return {
        "project_assessment_status": status,
        "project_assessment_score": score,
        "architecture_assessment_note": _architecture_note(missing_modules, row_data),
        "field_registry_assessment_note": _field_registry_note(row_data),
        "test_coverage_assessment_note": _test_note(missing_tests),
        "ui_readability_assessment_note": _ui_note(row_data),
        "data_source_assessment_note": _data_source_note(),
        "scoring_boundary_assessment_note": _scoring_boundary_note(row_data),
        "pre_v2_readiness_level": _readiness(status),
        "pre_v2_blockers": blockers,
        "pre_v2_recommendations": _recommendations(status, blockers),
    }


def build_project_assessment_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=PROJECT_ASSESSMENT_FIELDS)
    rows = [build_project_assessment_row(row) for _, row in frame.iterrows()]
    return pd.DataFrame(rows, columns=PROJECT_ASSESSMENT_FIELDS)


__all__ = [
    "EXPECTED_TEST_FILES",
    "PROJECT_ASSESSMENT_FIELDS",
    "REQUIRED_ASSESSMENT_FIELDS",
    "REQUIRED_MODULES",
    "build_project_assessment_profile",
    "build_project_assessment_row",
]
