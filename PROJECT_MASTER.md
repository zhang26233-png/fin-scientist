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

- CURRENT_VERSION = v1.8.0
- CURRENT_STAGE = Event-Driven Research System
- NEXT_TARGET = v1.8.1

Version evidence from current files:

- `app.py`: `APP_VERSION = "V1.8.0"`
- `legacy_app.py`: `APP_VERSION = "V1.8.0"`
- `README.md`: Current version: V1.8.0
- `docs/DEV_LOG.md`: V1.8.0 Event Foundation Layer

V1.8.0 starts the Event-Driven Research System with a read-only Event Foundation Layer. The event layer standardizes caller-provided event fields into research context only; it does not fetch news, change data sources, alter sorting, or change scoring.

## Current Architecture

Generated from the current project root scan on 2026-06-03.

```text
.
|-- .gitignore
|-- AGENTS.md
|-- app.py
|-- legacy_app.py
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
