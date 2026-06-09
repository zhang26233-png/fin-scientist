# Fin-Scientist Project Master

> Single Source of Truth. This file is the permanent project memory for Fin-Scientist.
> All research outputs are only for learning and research, and do not constitute investment advice.

## Project Overview

- Project name: Fin-Scientist
- Positioning: AI financial research platform
- Current product shape: personal financial research workbench prototype
- Research workflow goal:
  - Data analysis
  - Technical analysis
  - Fundamental analysis
  - Industry comparison
  - Risk identification
  - Research priority assessment
  - Future backtest validation
  - Future AI research Agent

## Version State

- CURRENT_VERSION = v3.7.0
- CURRENT_STAGE = Backtest Evaluation Package
- NEXT_TARGET = v3.8.0 Strategy Rule Engine

Version evidence from current files:

- `app.py`: `APP_VERSION = "V2.0.0"`
- `legacy_app.py`: `APP_VERSION = "V2.0.0"`
- `README.md`: Current version: V2.0.0
- `docs/DEV_LOG.md`: V2.0.0 Research Memory Foundation

V3.7.0 adds the Backtest Evaluation Package on top of the Backtest Foundation and Return Analysis layers. The new evaluation layer calculates read-only risk, return-risk, performance, and backtest-quality fields only from existing return-analysis outputs. This version does not add API keys, databases, vector stores, news sources, external services, trading connections, target prices, position suggestions, automated trading, strategy optimization, parameter search, machine-learning predictions, scoring-weight changes, default sorting changes, stock-pool changes, universe-module changes, fundamental-module changes, technical-module changes, composite-module changes, candidate-pool changes, Backtest Foundation changes, Return Analysis changes, or event/memory module changes. The recommended v3.8 main line is Strategy Rule Engine.

## Current Architecture

Generated from the current project root scan on 2026-06-03.

```text
.
|-- .gitignore
|-- AGENTS.md
|-- app.py
|-- legacy_app.py
|-- memory/
|   |-- __init__.py
|   |-- research_journal.py
|   |-- research_memory.py
|   `-- research_timeline.py
|-- universe/
|   |-- __init__.py
|   `-- a_share_universe.py
|-- backtest/
|   |-- __init__.py
|   |-- backtest_engine.py
|   |-- backtest_evaluation.py
|   `-- return_analysis.py
|-- screening/
|   |-- __init__.py
|   |-- candidate_pool.py
|   |-- composite_score_engine.py
|   |-- fundamental_screening.py
|   `-- technical_screening.py
|-- README.md
|-- requirements.txt
|-- streamlit-err.log
|-- streamlit-out.log
|-- config/
|   |-- __init__.py
|   |-- feature_flags.py
|   |-- fundamental_samples.py
|   |-- sector_mapping.py
|   |-- stock_names.py
|   `-- stock_pools.py
|-- core/
|   |-- __init__.py
|   |-- explanations.py
|   |-- metrics.py
|   |-- scoring.py
|   `-- sector_strength.py
|-- data/
|   |-- __init__.py
|   |-- fundamental_data.py
|   `-- market_data.py
|-- docs/
|   |-- DEV_LOG.md
|   |-- PROJECT_BRIEF.md
|   |-- ROADMAP.md
|   |-- SCREENING_SPEC.md
|   `-- TEST_CHECKLIST.md
|-- strategy/
|   |-- __init__.py
|   |-- architecture_audit.py
|   |-- adapter.py
|   |-- backtest.py
|   |-- backtest_diagnostics.py
|   |-- comparison.py
|   |-- composite_profile.py
|   |-- confluence.py
|   |-- explanations.py
|   |-- export.py
|   |-- factors.py
|   |-- filters.py
|   |-- fundamental.py
|   |-- fundamental_diagnostics.py
|   |-- fundamental_relative.py
|   |-- presets.py
|   |-- preset_comparison.py
|   |-- priority_stability.py
|   |-- preview.py
|   |-- report.py
|   |-- risk.py
|   |-- scoring.py
|   |-- service.py
|   |-- technical.py
|   `-- view_model.py
|-- tests/
|   |-- conftest.py
|   |-- test_core_metrics.py
|   |-- test_core_scoring.py
|   |-- test_data_fetch_boundaries.py
|   |-- test_explanations.py
|   |-- test_feature_flags.py
|   |-- test_forbidden_phrases.py
|   |-- test_fundamental_data.py
|   |-- test_market_data.py
|   |-- test_module_imports.py
|   |-- test_a_share_universe.py
|   |-- test_research_journal.py
|   |-- test_research_timeline.py
|   |-- test_screening_contract.py
|   |-- test_sector_strength.py
|   |-- test_strategy_*.py
|   |-- test_strategy_architecture_audit.py
|   |-- test_strategy_priority_stability.py
|   `-- test_strategy_ui_integration.py
`-- ui/
    |-- __init__.py
    |-- screening_ui.py
    `-- strategy_diagnostics_panel.py
```

Ignored runtime/cache directories present in the scan:

- `.git/`
- `.pytest_cache/`
- `__pycache__/`
- package-level `__pycache__/`

## Current Module Status

Generated from the current `strategy/` directory.

| Area | Module | Status | Notes |
|---|---|---|---|
| Strategy adapter | `strategy/adapter.py` | active | Field mapping, diagnostics assembly, risk text |
| Factors | `strategy/factors.py` | active | Trend, momentum, volatility, volume and liquidity factor snapshots |
| Risk | `strategy/risk.py` | active | Research risk labels and risk text |
| Filters | `strategy/filters.py` | active | Strategy-side filter helpers |
| Strategy scoring | `strategy/scoring.py` | active | Internal `strategy_score`; separate from `core/scoring.py` |
| Presets | `strategy/presets.py` | active | Research preset definitions |
| Preset comparison | `strategy/preset_comparison.py` | active | Multi-preset comparison, dominant style, consensus level |
| Score comparison | `strategy/comparison.py` | active | Original score and strategy score alignment checks |
| Preview | `strategy/preview.py` | active | Read-only candidate-pool preview layer |
| Explanation layer | `strategy/explanations.py` | active | Strategy preview reason fields |
| Technical module | `strategy/technical.py` | active | Technical labels, grade, style, strength, risk level |
| Fundamental module | `strategy/fundamental.py` | active | Field detection, normalization, data quality, quality scores |
| Fundamental relative module | `strategy/fundamental_relative.py` | active | Industry/sector relative comparison |
| Fundamental diagnostics | `strategy/fundamental_diagnostics.py` | active | Field-level diagnostics, evidence, confidence, research level |
| Confluence module | `strategy/confluence.py` | active | Technical/fundamental confluence labels and score |
| Composite profile | `strategy/composite_profile.py` | active | Composite research profile plus research priority layer |
| Priority stability | `strategy/priority_stability.py` | active | Read-only stability and drift diagnostics for research priority fields |
| Architecture audit | `strategy/architecture_audit.py` | active | Read-only module, field, boundary, and contract diagnostics for Research Intelligence Layer |
| Event context | `strategy/event_context.py` | active | Read-only event field standardization for Evidence Understanding Layer |
| Event diagnostics | `strategy/event_diagnostics.py` | active | Read-only event evidence quality diagnostics for Evidence Quality Layer |
| Event confluence | `strategy/event_confluence.py` | active | Read-only event-to-research-profile confluence review for evidence synthesis |
| Event research summary | `strategy/event_research_summary.py` | active | Read-only Agent-ready event research notes for evidence synthesis |
| Research pipeline audit | `strategy/research_pipeline_audit.py` | active | Read-only cross-module pipeline completeness and conflict diagnostics |
| Project assessment | `strategy/project_assessment.py` | active | Read-only pre-v2 architecture, field, UI, test, data-source, scoring-boundary, and readiness assessment |
| Research memory | `memory/research_memory.py` | active | Read-only Research Snapshot Schema for grouped memory payloads |
| Research timeline | `memory/research_timeline.py` | active | Read-only Research Timeline Layer for organizing same-object snapshots by time |
| Research journal | `memory/research_journal.py` | active | Read-only Research Journal Layer for human-readable and Agent-ready research notes |
| A-share universe | `universe/a_share_universe.py` | active | All-A-share universe builder for future screening, scoring, and backtest entry points |
| Fundamental screening | `screening/fundamental_screening.py` | active | Read-only fundamental screening fields for Universe rows with safe incomplete fallback |
| Technical screening | `screening/technical_screening.py` | active | Read-only technical screening fields for Universe rows with safe incomplete fallback |
| Composite quant score | `screening/composite_score_engine.py` | active | Read-only 50/50 composite score from fundamental and technical screening outputs |
| Candidate pool | `screening/candidate_pool.py` | active | Read-only candidate-pool grouping and rank fields from composite score outputs |
| Backtest foundation | `backtest/backtest_engine.py` | active | Read-only price-history availability and coverage fields for future validation |
| Return analysis | `backtest/return_analysis.py` | active | Read-only historical return metrics from validated price history |
| Backtest evaluation | `backtest/backtest_evaluation.py` | active | Read-only risk, return-risk, performance, and quality evaluation from return-analysis fields |
| Backtest helpers | `strategy/backtest.py` | internal research | Caller-provided validation samples only |
| Backtest diagnostics | `strategy/backtest_diagnostics.py` | internal research | Backtest summary schema and diagnostics |
| Export | `strategy/export.py` | internal research | JSON-like snapshot payloads |
| Report | `strategy/report.py` | active | Strategy report assembly |
| Service | `strategy/service.py` | active | Strategy service output wrapper |
| View model | `strategy/view_model.py` | active | UI-friendly strategy report model |

## Current Field Registry

This registry is generated from `strategy/technical.py`, `strategy/fundamental.py`, `strategy/fundamental_relative.py`, `strategy/fundamental_diagnostics.py`, `strategy/confluence.py`, `strategy/composite_profile.py`, and `strategy/preview.py`.

### Identity And Strategy Preview

| Field | Source | Meaning |
|---|---|---|
| `symbol` | `strategy.preview` | Security identifier |
| `name` | `strategy.preview` | Display name |
| `original_score` | `strategy.preview` | Original research observation score from caller data |
| `strategy_score` | `strategy.scoring` | Internal research score; not a trading conclusion |
| `preset_name` | `strategy.scoring` | Active strategy preset name |
| `best_preset` | `strategy.preset_comparison` | Highest-scoring preset in comparison |
| `worst_preset` | `strategy.preset_comparison` | Lowest-scoring preset in comparison |
| `score_spread` | `strategy.preset_comparison` | Spread between preset scores |
| `average_preset_score` | `strategy.preset_comparison` | Mean preset score |
| `dominant_style` | `strategy.preset_comparison` | Dominant research style |
| `consensus_level` | `strategy.preset_comparison` | Cross-preset consistency level |
| `balanced_research_score` | `strategy.preview` | Balanced research preset score |
| `trend_momentum_score` | `strategy.preview` | Trend momentum preset score |
| `volume_breakout_score` | `strategy.preview` | Volume breakout preset score |
| `low_risk_quality_score` | `strategy.preview` | Low-risk quality preset score |
| `high_elasticity_watch_score` | `strategy.preview` | High-elasticity watch preset score |
| `risk_labels` | `strategy.scoring` | Risk labels used for research review |
| `data_quality_labels` | `strategy.scoring` | Data quality labels |
| `warnings` | `strategy.preview` | Preview warnings |

### Strategy Explanation Fields

| Field | Source |
|---|---|
| `strategy_reason` | `strategy.explanations` |
| `trend_reason` | `strategy.explanations` |
| `momentum_reason` | `strategy.explanations` |
| `volume_price_reason` | `strategy.explanations` |
| `liquidity_reason` | `strategy.explanations` |
| `risk_reason` | `strategy.explanations` |
| `data_quality_reason` | `strategy.explanations` |
| `preset_reason` | `strategy.explanations` |
| `confidence_note` | `strategy.explanations` |

### Technical Fields

| Field | Source |
|---|---|
| `ma_structure_label` | `strategy.technical` |
| `trend_quality_label` | `strategy.technical` |
| `breakout_pullback_label` | `strategy.technical` |
| `volume_price_structure_label` | `strategy.technical` |
| `short_term_overheat_label` | `strategy.technical` |
| `volatility_risk_label` | `strategy.technical` |
| `technical_profile_summary` | `strategy.technical` |
| `technical_grade` | `strategy.technical` |
| `technical_style` | `strategy.technical` |
| `technical_strength` | `strategy.technical` |
| `technical_risk_level` | `strategy.technical` |
| `technical_watch_points` | `strategy.technical` |
| `technical_summary_short` | `strategy.technical` |

### Fundamental Fields

| Field | Source |
|---|---|
| `fundamental_available` | `strategy.fundamental` |
| `fundamental_fields_detected` | `strategy.fundamental` |
| `missing_fundamental_fields` | `strategy.fundamental` |
| `fundamental_data_quality_label` | `strategy.fundamental` |
| `fundamental_summary_base` | `strategy.fundamental` |
| `profitability_score` | `strategy.fundamental` |
| `growth_score` | `strategy.fundamental` |
| `valuation_score` | `strategy.fundamental` |
| `financial_risk_score` | `strategy.fundamental` |
| `fundamental_quality_score` | `strategy.fundamental` |
| `fundamental_grade` | `strategy.fundamental` |
| `fundamental_style` | `strategy.fundamental` |
| `fundamental_risk_level` | `strategy.fundamental` |
| `fundamental_reason` | `strategy.fundamental` |

Canonical raw fundamental inputs recognized by `strategy.fundamental`:

`revenue`, `net_profit`, `gross_margin`, `roe`, `pe`, `pb`, `ps`, `debt_ratio`, `operating_cashflow`, `revenue_growth`, `profit_growth`, `market_cap`, `industry`.

### Industry Relative Fields

| Field | Source |
|---|---|
| `relative_profitability_label` | `strategy.fundamental_relative` |
| `relative_growth_label` | `strategy.fundamental_relative` |
| `relative_valuation_label` | `strategy.fundamental_relative` |
| `relative_financial_risk_label` | `strategy.fundamental_relative` |
| `industry_relative_quality_label` | `strategy.fundamental_relative` |
| `industry_relative_summary` | `strategy.fundamental_relative` |

### Fundamental Diagnostics Fields

| Field | Source |
|---|---|
| `fundamental_diagnostics` | `strategy.fundamental_diagnostics` |
| `profitability_diagnostics` | `strategy.fundamental_diagnostics` |
| `growth_diagnostics` | `strategy.fundamental_diagnostics` |
| `valuation_diagnostics` | `strategy.fundamental_diagnostics` |
| `financial_risk_diagnostics` | `strategy.fundamental_diagnostics` |
| `fundamental_watch_points` | `strategy.fundamental_diagnostics` |
| `fundamental_strength_points` | `strategy.fundamental_diagnostics` |
| `fundamental_weakness_points` | `strategy.fundamental_diagnostics` |
| `fundamental_diagnostics_summary` | `strategy.fundamental_diagnostics` |
| `fundamental_profile_type` | `strategy.fundamental_diagnostics` |
| `fundamental_conflict_flags` | `strategy.fundamental_diagnostics` |
| `fundamental_conflict_summary` | `strategy.fundamental_diagnostics` |
| `industry_relative_detail` | `strategy.fundamental_diagnostics` |
| `relative_advantage_points` | `strategy.fundamental_diagnostics` |
| `relative_disadvantage_points` | `strategy.fundamental_diagnostics` |
| `relative_position_summary` | `strategy.fundamental_diagnostics` |
| `fundamental_research_questions` | `strategy.fundamental_diagnostics` |
| `fundamental_detail_view` | `strategy.fundamental_diagnostics` |
| `profitability_detail` | `strategy.fundamental_diagnostics` |
| `growth_detail` | `strategy.fundamental_diagnostics` |
| `valuation_detail` | `strategy.fundamental_diagnostics` |
| `financial_risk_detail` | `strategy.fundamental_diagnostics` |
| `fundamental_key_evidence` | `strategy.fundamental_diagnostics` |
| `fundamental_uncertainty_notes` | `strategy.fundamental_diagnostics` |
| `fundamental_confidence_level` | `strategy.fundamental_diagnostics` |
| `fundamental_confidence_score` | `strategy.fundamental_diagnostics` |
| `fundamental_confidence_reasons` | `strategy.fundamental_diagnostics` |
| `fundamental_data_completeness_score` | `strategy.fundamental_diagnostics` |
| `fundamental_industry_comparability_label` | `strategy.fundamental_diagnostics` |
| `fundamental_anomaly_flags` | `strategy.fundamental_diagnostics` |
| `fundamental_research_conclusion` | `strategy.fundamental_diagnostics` |
| `fundamental_research_level` | `strategy.fundamental_diagnostics` |
| `fundamental_core_strength` | `strategy.fundamental_diagnostics` |
| `fundamental_core_risk` | `strategy.fundamental_diagnostics` |
| `fundamental_followup_focus` | `strategy.fundamental_diagnostics` |
| `fundamental_summary_tags` | `strategy.fundamental_diagnostics` |

### Confluence Fields

| Field | Source |
|---|---|
| `confluence_label` | `strategy.confluence` |
| `confluence_score` | `strategy.confluence` |
| `confluence_summary` | `strategy.confluence` |
| `confluence_strength_points` | `strategy.confluence` |
| `confluence_risk_points` | `strategy.confluence` |
| `confluence_followup_focus` | `strategy.confluence` |

### Composite Profile And Research Priority Fields

| Field | Source |
|---|---|
| `composite_research_grade` | `strategy.composite_profile` |
| `composite_research_style` | `strategy.composite_profile` |
| `composite_research_level` | `strategy.composite_profile` |
| `composite_risk_level` | `strategy.composite_profile` |
| `composite_confidence_level` | `strategy.composite_profile` |
| `composite_summary` | `strategy.composite_profile` |
| `composite_strength_points` | `strategy.composite_profile` |
| `composite_risk_points` | `strategy.composite_profile` |
| `composite_followup_focus` | `strategy.composite_profile` |
| `composite_data_quality_note` | `strategy.composite_profile` |
| `research_priority_score` | `strategy.composite_profile` |
| `research_priority_level` | `strategy.composite_profile` |
| `research_priority_reasons` | `strategy.composite_profile` |
| `research_priority_warnings` | `strategy.composite_profile` |

### Priority Stability Fields

| Field | Source |
|---|---|
| `priority_stability_label` | `strategy.priority_stability` |
| `priority_stability_score` | `strategy.priority_stability` |
| `priority_stability_note` | `strategy.priority_stability` |
| `priority_drift_detected` | `strategy.priority_stability` |
| `priority_drift_reason` | `strategy.priority_stability` |

### Architecture Audit Fields

| Field | Source |
|---|---|
| `architecture_audit_label` | `strategy.architecture_audit` |
| `architecture_audit_score` | `strategy.architecture_audit` |
| `architecture_audit_note` | `strategy.architecture_audit` |
| `architecture_audit_warnings` | `strategy.architecture_audit` |
| `field_contract_warnings` | `strategy.architecture_audit` |
| `module_contract_warnings` | `strategy.architecture_audit` |
| `boundary_contract_warnings` | `strategy.architecture_audit` |

### Event Context Fields

| Field | Source | Meaning |
|---|---|---|
| `event_available` | `strategy.event_context` | Whether caller-provided event information is available |
| `event_type` | `strategy.event_context` | Standard event category such as earnings, policy, industry, macro, product, risk, news_only, or unknown |
| `event_recency_label` | `strategy.event_context` | Event timing label: Recent, Stale, or Unknown |
| `event_source_quality_label` | `strategy.event_context` | Source quality label: Official, Reliable Media, Unverified, or Unknown |
| `event_reliability_label` | `strategy.event_context` | Reliability label: High, Medium, Low, or Unknown |
| `event_context_note` | `strategy.event_context` | Neutral research-context note for follow-up evidence review |
| `event_research_tags` | `strategy.event_context` | Tags for future diagnostics and Agent task routing |
| `event_warnings` | `strategy.event_context` | Missing-field, unclear-type, source-quality, and reliability warnings |

Event Context Fields are read-only and research-only. They do not change default screening output, default sorting, stock pools, data sources, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, or `core/scoring.py`.

### Event Diagnostics Fields

| Field | Source | Meaning |
|---|---|---|
| `event_completeness_score` | `strategy.event_diagnostics` | Event evidence completeness score based on title, summary, type, date, source, source type, and confidence |
| `event_clarity_score` | `strategy.event_diagnostics` | Event description clarity score based on type, title, summary, and context note |
| `event_consistency_score` | `strategy.event_diagnostics` | Consistency score across event type, source quality, reliability, recency, and warnings |
| `event_confidence_score` | `strategy.event_diagnostics` | Overall event evidence quality confidence score |
| `event_diagnostic_level` | `strategy.event_diagnostics` | Event diagnostic level: Strong, Usable, Weak, or Unavailable |
| `event_diagnostic_summary` | `strategy.event_diagnostics` | Neutral research summary of event evidence quality |
| `event_followup_questions` | `strategy.event_diagnostics` | Follow-up research questions generated from event gaps |
| `event_evidence_gaps` | `strategy.event_diagnostics` | Missing or unclear event evidence fields |
| `event_quality_warnings` | `strategy.event_diagnostics` | Source, reliability, and quality warnings for research review |

Event Diagnostics Fields are read-only and research-only. They do not change default screening output, default sorting, stock pools, data sources, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, or `core/scoring.py`.

### Event Confluence Fields

| Field | Source | Meaning |
|---|---|---|
| `event_confluence_label` | `strategy.event_confluence` | Event confluence label: Supportive, Mixed, Conflicting, or Unavailable |
| `event_confluence_score` | `strategy.event_confluence` | Read-only event confluence score, not used for sorting or main scoring |
| `event_confluence_summary` | `strategy.event_confluence` | Neutral research summary of event alignment with the current profile |
| `event_support_points` | `strategy.event_confluence` | Reasons why event context may support current research profile review |
| `event_conflict_points` | `strategy.event_confluence` | Event/profile mismatches or conflicts for follow-up review |
| `event_followup_focus` | `strategy.event_confluence` | Follow-up research focus generated from event confluence |
| `event_confluence_warnings` | `strategy.event_confluence` | Event quality, profile completeness, and confluence availability warnings |

Event Confluence Fields are read-only and research-only. They do not change default screening output, default sorting, stock pools, data sources, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, or `core/scoring.py`.

### Event Research Summary Fields

| Field | Source | Meaning |
|---|---|---|
| `event_research_summary` | `strategy.event_research_summary` | Neutral event research summary built from context, diagnostics, and confluence |
| `event_research_level` | `strategy.event_research_summary` | Event research value level: High, Medium, Low, or Unavailable |
| `event_key_evidence` | `strategy.event_research_summary` | Key event evidence points for research review |
| `event_key_risks` | `strategy.event_research_summary` | Key event risks, uncertainty, and conflict points |
| `event_validation_focus` | `strategy.event_research_summary` | Follow-up validation focus for deeper research |
| `event_agent_note` | `strategy.event_research_summary` | Structured note for future AI Research Agent use |
| `event_summary_warnings` | `strategy.event_research_summary` | Summary availability, evidence quality, and conflict warnings |

Event Research Summary Fields are read-only and research-only. They do not change default screening output, default sorting, stock pools, data sources, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

### Research Pipeline Audit Fields

| Field | Source | Meaning |
|---|---|---|
| `research_pipeline_status` | `strategy.research_pipeline_audit` | Overall pipeline status: Healthy, Watch, Conflict, or Incomplete |
| `research_pipeline_conflicts` | `strategy.research_pipeline_audit` | Cross-module conflicts found in the research pipeline |
| `research_pipeline_warnings` | `strategy.research_pipeline_audit` | Missing fields, weak links, and review warnings |
| `research_pipeline_summary` | `strategy.research_pipeline_audit` | Neutral summary of pipeline completeness and consistency |

Research Pipeline Audit Fields are read-only and research-only. They do not change default screening output, default sorting, stock pools, data sources, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

### Project Assessment Fields

| Field | Source | Meaning |
|---|---|---|
| `project_assessment_status` | `strategy.project_assessment` | Overall pre-v2 assessment status: Ready, Watch, or Not Ready |
| `project_assessment_score` | `strategy.project_assessment` | Read-only project maturity score, not used for research sorting |
| `architecture_assessment_note` | `strategy.project_assessment` | Architecture completeness and module-chain assessment |
| `field_registry_assessment_note` | `strategy.project_assessment` | Field volume, field grouping, and registry-boundary assessment |
| `test_coverage_assessment_note` | `strategy.project_assessment` | Key test-file presence and coverage assessment |
| `ui_readability_assessment_note` | `strategy.project_assessment` | Preview UI density and readability assessment |
| `data_source_assessment_note` | `strategy.project_assessment` | Data-source boundary and reliability assessment |
| `scoring_boundary_assessment_note` | `strategy.project_assessment` | Scoring boundary and contamination-risk assessment |
| `pre_v2_readiness_level` | `strategy.project_assessment` | Readiness level for entering v2.0: High, Medium, or Low |
| `pre_v2_blockers` | `strategy.project_assessment` | Items that should be resolved before v2.0 |
| `pre_v2_recommendations` | `strategy.project_assessment` | Suggested route for entering Research Memory Foundation |

Project Assessment Fields are read-only and research-only. They do not change default screening output, default sorting, stock pools, data sources, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

### Research Memory Snapshot Fields

| Field | Source | Meaning |
|---|---|---|
| `snapshot_id` | `memory.research_memory` | Unique Research Snapshot identifier |
| `snapshot_timestamp` | `memory.research_memory` | UTC snapshot generation timestamp |
| `snapshot_ticker` | `memory.research_memory` | Security identifier copied from the preview object |
| `snapshot_name` | `memory.research_memory` | Security display name copied from the preview object |
| `snapshot_version` | `memory.research_memory` | Project version attached to the snapshot schema |
| `snapshot_stage` | `memory.research_memory` | Project stage attached to the snapshot schema |
| `snapshot_summary` | `memory.research_memory` | Neutral summary of snapshot availability and key context |
| `snapshot_status` | `memory.research_memory` | Snapshot status: Available or Incomplete |
| `technical_snapshot` | `memory.research_memory` | Grouped technical research fields |
| `fundamental_snapshot` | `memory.research_memory` | Grouped fundamental research fields |
| `industry_snapshot` | `memory.research_memory` | Grouped industry-relative research fields |
| `composite_snapshot` | `memory.research_memory` | Grouped composite research profile fields |
| `priority_snapshot` | `memory.research_memory` | Grouped research priority and priority stability fields |
| `event_snapshot` | `memory.research_memory` | Grouped event context, diagnostics, confluence, and summary fields |
| `pipeline_snapshot` | `memory.research_memory` | Grouped architecture audit and research pipeline audit fields |
| `project_snapshot` | `memory.research_memory` | Grouped project assessment and pre-v2 readiness fields |

Research Memory Snapshot Fields are schema-only, read-only, and research-only. V2.0.0 does not save historical records, add a database, add a vector store, fetch news, call APIs, add data sources, change default screening output, change default sorting, change stock pools, change `strategy_score`, change `research_priority_score`, change `priority_stability_score`, change `architecture_audit_score`, change `event_confidence_score`, change `event_confluence_score`, or modify `core/scoring.py`.

### Research Timeline Fields

| Field | Source | Meaning |
|---|---|---|
| `timeline_id` | `memory.research_timeline` | Unique Research Timeline identifier |
| `timeline_ticker` | `memory.research_timeline` | Security identifier shared by the compared snapshots |
| `timeline_name` | `memory.research_timeline` | Security display name copied from the timeline snapshots |
| `timeline_snapshot_count` | `memory.research_timeline` | Number of same-ticker snapshots used in the timeline comparison |
| `timeline_start_time` | `memory.research_timeline` | Earliest snapshot timestamp used in the timeline |
| `timeline_end_time` | `memory.research_timeline` | Latest snapshot timestamp used in the timeline |
| `timeline_status` | `memory.research_timeline` | Timeline status: Available or Incomplete |
| `timeline_direction` | `memory.research_timeline` | Overall research-state direction: Improving, Stable, Deteriorating, Mixed, or Unavailable |
| `timeline_change_summary` | `memory.research_timeline` | Neutral summary of the observed snapshot-to-snapshot changes |
| `timeline_key_changes` | `memory.research_timeline` | Cross-section list of priority, event, and pipeline field changes |
| `timeline_priority_trend` | `memory.research_timeline` | Research priority trend between the first and last same-ticker snapshots |
| `timeline_event_trend` | `memory.research_timeline` | Event research trend between the first and last same-ticker snapshots |
| `timeline_pipeline_trend` | `memory.research_timeline` | Research pipeline trend between the first and last same-ticker snapshots |
| `timeline_warnings` | `memory.research_timeline` | Missing timestamp, insufficient snapshot, inconsistent ticker, and section-availability warnings |

Research Timeline Fields are schema-only, read-only, and research-only. V2.1.0 does not save historical records, add a database, add a vector store, fetch news, call APIs, add data sources, change default screening output, change default sorting, change stock pools, change `strategy_score`, change `research_priority_score`, change `priority_stability_score`, change `architecture_audit_score`, change `event_confidence_score`, change `event_confluence_score`, or modify `core/scoring.py`.

### Research Journal Fields

| Field | Source | Meaning |
|---|---|---|
| `journal_id` | `memory.research_journal` | Unique Research Journal identifier |
| `journal_ticker` | `memory.research_journal` | Security identifier copied from Snapshot or Timeline |
| `journal_name` | `memory.research_journal` | Security display name copied from Snapshot or Timeline |
| `journal_period` | `memory.research_journal` | Time period covered by the Snapshot and Timeline inputs |
| `journal_status` | `memory.research_journal` | Journal status: Available or Incomplete |
| `journal_summary` | `memory.research_journal` | Human-readable neutral summary of the Snapshot and Timeline context |
| `journal_observations` | `memory.research_journal` | Main research observations extracted from snapshot sections and timeline changes |
| `journal_risk_notes` | `memory.research_journal` | Risk, uncertainty, warning, and conflict notes for research review |
| `journal_data_quality_notes` | `memory.research_journal` | Data quality and source-boundary notes from Snapshot and Timeline context |
| `journal_followup_questions` | `memory.research_journal` | Follow-up research questions for deeper evidence review |
| `journal_agent_tasks` | `memory.research_journal` | Future Agent research tasks; no operational tasks |
| `journal_warnings` | `memory.research_journal` | Missing Snapshot, missing Timeline, incomplete status, missing ticker, and coverage warnings |

Research Journal Fields are schema-only, read-only, and research-only. V2.2.0 does not save historical records, add a database, add a vector store, fetch news, call APIs, add data sources, change default screening output, change default sorting, change stock pools, change `strategy_score`, change `research_priority_score`, change `priority_stability_score`, change `architecture_audit_score`, change `event_confidence_score`, change `event_confluence_score`, or modify `core/scoring.py`.

### A-Share Universe Fields

| Field | Source | Meaning |
|---|---|---|
| `ticker` | `universe.a_share_universe` | Normalized A-share security identifier |
| `name` | `universe.a_share_universe` | Security display name |
| `market` | `universe.a_share_universe` | Market label, defaulting to A股 |
| `list_date` | `universe.a_share_universe` | Listing date when available |
| `days_since_listing` | `universe.a_share_universe` | Days since listing, used for new-stock filtering |
| `is_st` | `universe.a_share_universe` | Whether the security is marked as ST |
| `is_suspended` | `universe.a_share_universe` | Whether the security is suspended |
| `status` | `universe.a_share_universe` | Row-level universe status after filtering |
| `universe_status` | `universe.a_share_universe` | Universe build status: Available or Incomplete |
| `universe_total_count` | `universe.a_share_universe` | Total source securities before filtering |
| `universe_filtered_count` | `universe.a_share_universe` | Securities remaining after default filters |
| `universe_summary` | `universe.a_share_universe` | Human-readable summary of total count and filter exclusions |

A-Share Universe Fields are research-universe fields for future screening and validation. V3.0.0 uses AkShare as the preferred source when available and safely returns an empty DataFrame if the source fails. It does not add API keys, databases, vector stores, news sources, external services, real trading connections, default sorting changes, stock-pool scoring changes, `strategy_score` changes, `research_priority_score` changes, `priority_stability_score` changes, event-module changes, memory-module changes, or `core/scoring.py` changes.

### Fundamental Screening Fields

| Field | Source | Meaning |
|---|---|---|
| `fundamental_available` | `screening.fundamental_screening` | Whether usable caller-provided fundamental data exists for the Universe row |
| `roe` | `screening.fundamental_screening` | Return on equity |
| `revenue_growth` | `screening.fundamental_screening` | Revenue growth rate |
| `profit_growth` | `screening.fundamental_screening` | Profit growth rate |
| `gross_margin` | `screening.fundamental_screening` | Gross margin |
| `debt_ratio` | `screening.fundamental_screening` | Asset-liability ratio |
| `operating_cashflow` | `screening.fundamental_screening` | Operating cashflow |
| `pe` | `screening.fundamental_screening` | Price-to-earnings ratio |
| `pb` | `screening.fundamental_screening` | Price-to-book ratio |
| `fundamental_score` | `screening.fundamental_screening` | Read-only fundamental research score |
| `fundamental_level` | `screening.fundamental_screening` | Fundamental level: High, Medium, Low, or Unavailable |
| `fundamental_screening_status` | `screening.fundamental_screening` | Screening status: Pass, Watch, Exclude, or Incomplete |
| `fundamental_reasons` | `screening.fundamental_screening` | Neutral reasons for pass/watch status |
| `fundamental_warnings` | `screening.fundamental_screening` | Missing, abnormal, or unavailable data warnings |

Fundamental Screening Fields are read-only research fields for early fundamental review. V3.1.0 does not change default sorting, default screening workflow, stock-pool construction, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, event modules, memory modules, trading logic, or `core/scoring.py`.

### Technical Screening Fields

| Field | Source | Meaning |
|---|---|---|
| `technical_available` | `screening.technical_screening` | Whether usable caller-provided technical data exists for the Universe row |
| `close` | `screening.technical_screening` | Latest close price |
| `ma20` | `screening.technical_screening` | 20-day moving average |
| `ma60` | `screening.technical_screening` | 60-day moving average |
| `above_ma20` | `screening.technical_screening` | Whether close is above MA20 |
| `above_ma60` | `screening.technical_screening` | Whether close is above MA60 |
| `ma_trend` | `screening.technical_screening` | Moving-average trend: Uptrend, Downtrend, Mixed, or Unknown |
| `rsi14` | `screening.technical_screening` | 14-period RSI |
| `macd_signal` | `screening.technical_screening` | MACD status: Bullish, Bearish, Neutral, or Unknown |
| `volume_ratio` | `screening.technical_screening` | Current volume relative to recent average volume |
| `technical_score` | `screening.technical_screening` | Read-only technical research score |
| `technical_level` | `screening.technical_screening` | Technical level: High, Medium, Low, or Unavailable |
| `technical_screening_status` | `screening.technical_screening` | Screening status: Pass, Watch, Exclude, or Incomplete |
| `technical_reasons` | `screening.technical_screening` | Neutral reasons for pass/watch/exclude status |
| `technical_warnings` | `screening.technical_screening` | Missing, abnormal, or unavailable data warnings |

Technical Screening Fields are read-only research fields for early technical review. V3.2.0 does not create trade points, backtests, machine-learning outputs, automated trading workflows, target prices, or operational conclusions. It does not change default sorting, default screening workflow, stock-pool construction, `fundamental_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, fundamental modules, event modules, memory modules, trading logic, or `core/scoring.py`.

### Composite Quant Score Fields

| Field | Source | Meaning |
|---|---|---|
| `composite_available` | `screening.composite_score_engine` | Whether both fundamental and technical screening scores are usable |
| `composite_score` | `screening.composite_score_engine` | Read-only composite quant score using default 50% fundamental and 50% technical weights |
| `composite_level` | `screening.composite_score_engine` | Composite level: High, Medium, Low, or Unavailable |
| `composite_screening_status` | `screening.composite_score_engine` | Composite screening status: Pass, Watch, Exclude, or Incomplete |
| `composite_reasons` | `screening.composite_score_engine` | Neutral reasons for the composite score and level |
| `composite_warnings` | `screening.composite_score_engine` | Missing, invalid, or unavailable input warnings |
| `score_breakdown` | `screening.composite_score_engine` | Human-readable score decomposition such as Fundamental, Technical, and Composite values |

Composite Quant Score Fields are read-only research fields for standardizing the next candidate-pool input. V3.3.0 does not create buy signals, sell signals, target prices, position suggestions, backtest results, machine-learning predictions, or automated trading workflows. It does not change default sorting, default screening workflow, stock-pool construction, Universe modules, Fundamental modules, Technical modules, Event modules, Memory modules, trading logic, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

### Candidate Pool Fields

| Field | Source | Meaning |
|---|---|---|
| `candidate_pool` | `screening.candidate_pool` | Candidate group: Core, Watch, Exclude, or Unavailable |
| `candidate_rank` | `screening.candidate_pool` | Read-only rank inside Core/Watch based on `composite_score` descending without changing row order |
| `candidate_level` | `screening.candidate_pool` | Candidate level: A, B, C, or Unavailable |
| `candidate_status` | `screening.candidate_pool` | Candidate status: Selected, Watch, Excluded, or Incomplete |
| `candidate_reasons` | `screening.candidate_pool` | Neutral reasons for Core, Watch, or Exclude grouping |
| `candidate_risk_flags` | `screening.candidate_pool` | Risk labels such as Low Score, Missing Data, Weak Technical, or Weak Fundamental |
| `candidate_warnings` | `screening.candidate_pool` | Missing, abnormal, or unavailable input warnings |

Candidate Pool Fields are read-only research fields for organizing composite-score outputs before future backtest validation. V3.4.0 does not create buy points, sell points, target prices, position suggestions, backtest results, machine-learning predictions, or automated trading workflows. It does not change default sorting, default screening workflow, stock-pool construction, Universe modules, Fundamental modules, Technical modules, Composite modules, Event modules, Memory modules, trading logic, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

### Backtest Foundation Fields

| Field | Source | Meaning |
|---|---|---|
| `backtest_available` | `backtest.backtest_engine` | Whether the candidate has usable price history for future backtest validation |
| `backtest_status` | `backtest.backtest_engine` | Backtest foundation status: Available or Incomplete |
| `backtest_start_date` | `backtest.backtest_engine` | Earliest valid price-history date |
| `backtest_end_date` | `backtest.backtest_engine` | Latest valid price-history date |
| `backtest_days` | `backtest.backtest_engine` | Count of valid date and close rows |
| `backtest_price_available` | `backtest.backtest_engine` | Whether valid price history exists |
| `backtest_warnings` | `backtest.backtest_engine` | Missing or abnormal price-history warnings |

Backtest Foundation Fields are read-only data-availability fields for future validation. V3.5.0 does not calculate returns, cumulative returns, annualized returns, Sharpe ratio, maximum drawdown, win rate, strategy optimization, parameter search, machine-learning predictions, automated trading actions, buy/sell suggestions, target prices, or position suggestions. It does not change default sorting, default screening workflow, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Event modules, Memory modules, trading logic, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

### Return Analysis Fields

| Field | Source | Meaning |
|---|---|---|
| `return_analysis_available` | `backtest.return_analysis` | Whether validated price history is sufficient for read-only return analysis |
| `return_analysis_status` | `backtest.return_analysis` | Return analysis status: Available or Incomplete |
| `holding_period_days` | `backtest.return_analysis` | Count of valid date and close rows used for the analysis period |
| `entry_price` | `backtest.return_analysis` | First valid close price in the validated analysis window |
| `exit_price` | `backtest.return_analysis` | Last valid close price in the validated analysis window |
| `period_return` | `backtest.return_analysis` | Historical period return calculated from first and last close prices |
| `annualized_return` | `backtest.return_analysis` | Annualized historical return derived from period return and holding-period days |
| `volatility` | `backtest.return_analysis` | Annualized volatility based on daily close-to-close returns |
| `max_drawdown` | `backtest.return_analysis` | Largest historical drawdown observed in the validated close-price path |
| `win_rate` | `backtest.return_analysis` | Share of valid daily returns that are positive |
| `return_analysis_summary` | `backtest.return_analysis` | Neutral summary of the validated analysis window |
| `return_analysis_warnings` | `backtest.return_analysis` | Missing, abnormal, or unavailable price-history warnings |

Return Analysis Fields are read-only historical metric fields for future risk analysis and report assembly. V3.6.0 only computes metrics when `backtest_available` is true and valid `date` plus `close` history has at least 60 rows. It does not create target prices, position suggestions, strategy optimization, parameter search, machine-learning predictions, automated trading workflows, or operational conclusions. It does not change default sorting, default screening workflow, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Event modules, Memory modules, trading logic, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

### Backtest Evaluation Fields

| Field | Source | Meaning |
|---|---|---|
| `backtest_evaluation_available` | `backtest.backtest_evaluation` | Whether return-analysis fields are sufficient for read-only backtest evaluation |
| `backtest_evaluation_status` | `backtest.backtest_evaluation` | Backtest evaluation status: Available or Incomplete |
| `risk_score` | `backtest.backtest_evaluation` | Read-only risk score derived from max drawdown, volatility, and negative period-return context |
| `risk_level` | `backtest.backtest_evaluation` | Risk level: High, Medium, Low, or Unavailable |
| `return_risk_ratio` | `backtest.backtest_evaluation` | Historical period return divided by absolute maximum drawdown when available |
| `drawdown_risk_level` | `backtest.backtest_evaluation` | Drawdown risk level derived from maximum drawdown magnitude |
| `volatility_risk_level` | `backtest.backtest_evaluation` | Volatility risk level derived from annualized volatility |
| `performance_label` | `backtest.backtest_evaluation` | Historical performance label: Strong, Normal, Weak, or Unavailable |
| `performance_summary` | `backtest.backtest_evaluation` | Neutral summary of historical return, volatility, and drawdown context |
| `backtest_quality_label` | `backtest.backtest_evaluation` | Backtest quality label: Good, Watch, Poor, or Unavailable |
| `backtest_evaluation_warnings` | `backtest.backtest_evaluation` | Missing, abnormal, or unavailable evaluation warnings |

Backtest Evaluation Fields are read-only historical evaluation fields for closing the backtest review loop before future strategy-rule work. V3.7.0 only evaluates rows where `return_analysis_available` is true and required return-analysis fields are usable. It does not create buy or sell advice, target prices, position suggestions, automated trading workflows, strategy optimization, parameter search, machine-learning predictions, return promises, or scoring-weight changes. It does not change default sorting, default screening workflow, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest Foundation modules, Return Analysis modules, Event modules, Memory modules, trading logic, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`.

## Current Development Principles

- Do not directly modify `core/scoring.py` unless the task explicitly targets core scoring and includes tests.
- Do not change default sorting by default.
- Do not output investment instructions or operational conclusions.
- Do not output buy/sell points.
- Keep the project as a research system first.
- Quantitative system work comes later and must be validation-first.
- Preserve existing functionality with small, clear changes.
- Data source failures must not crash the page.
- Page copy must preserve the boundary: not investment advice.
- New fields should be read-only unless a later version explicitly changes the contract.
- `strategy_score` must remain separate from original screening output and separate from research priority fields.

## Permanent Memory Update Rule

For every future version upgrade, these files must be updated together:

- `PROJECT_MASTER.md`
- `ROADMAP.md`
- `CHANGELOG.md`

If a version changes but these files are not synchronized, the development process is incomplete.

## Boundary

Fin-Scientist does not connect to real trading accounts, does not perform automated order execution, and does not provide buy/sell/hold advice. The system is only for learning, research, data quality review, and research-priority workflow construction.
