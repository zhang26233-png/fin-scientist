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

- CURRENT_VERSION = v6.5.0
- CURRENT_STAGE = Real Technical Indicator Engine
- NEXT_TARGET = v6.5.1 Real Historical K-Line Integration

Version evidence from current files:

- `app.py`: `APP_VERSION = "v6.5.0"`
- `legacy_app.py`: `APP_VERSION = "v6.5.0"`
- `README.md`: Current version: v6.5.0
- `docs/DEV_LOG.md`: V2.0.0 Research Memory Foundation

V6.5.0 adds the Real Technical Indicator Engine. `technical/indicator_engine.py` builds additive real technical indicator fields from optional historical price data, including moving averages, MA alignment, 20/60-day returns, RSI14, MACD, ATR14, annualized 20-day volatility, 60-day drawdown, volume and turnover ratios, 52-week position, neutral signal summaries, technical risk flags, warnings, and the read-only `real_technical_score`. `pipeline/live_runner.py` calls `build_real_technical_indicators()` before `activate_research_scores()`, so v6.4 score activation can prefer `real_technical_score` when historical indicators are available and gracefully fall back to realtime snapshot activation when history is missing. Dashboard, Selection Results, and the product Research Workstation expose the new technical research fields. This version does not modify `core/scoring.py`, old scoring functions, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, or `selection_score`, and it does not add buy/sell/hold advice, target prices, position suggestions, return promises, machine-learning predictions, API keys, databases, or vector stores.

V6.5.0 file additions:

- `technical/__init__.py`
- `technical/indicator_engine.py`
- `tests/test_indicator_engine.py`
- Real Technical Indicator Fields

V6.4.0 adds Research Score Activation. `research/score_activation.py` converts realtime quote fields from the Live A-share universe into additive `activated_*` research fields, including quote availability, quote quality, liquidity, momentum, intraday price position, activated technical score, activated composite score, activated selection score, research level, research bucket, status, reasons, and warnings. Tencent-style turnover units are normalized inside the activation calculation without mutating the original `turnover` column. `pipeline/live_runner.py` calls `activate_research_scores()` at the end of the read-only pipeline, after explainable selection and factor fields are assembled. Dashboard and Selection Results now prefer activated research score fields while preserving the old `selection_score`, `composite_score`, `technical_score`, `fundamental_score`, and `candidate_rank` contracts. This version does not modify `core/scoring.py`, existing scoring functions, stock-selection algorithms, trading logic, or default underlying DataFrame order, and it does not create buy/sell/hold advice, target prices, position suggestions, return promises, machine-learning predictions, API keys, databases, or vector stores.

V6.4.0 file additions:

- `research/__init__.py`
- `research/score_activation.py`
- `tests/test_score_activation.py`

V6.3.5 adds Full A-Share Pagination and Cache Layer. Tencent Realtime now scans supported A-share code ranges across Shanghai, Shenzhen, ChiNext, STAR, and Beijing-style prefixes through bounded batch quote requests, merges and deduplicates tickers, and targets raw rows above 4000 when the public endpoint is available. `data/a_share_loader.py` keeps the priority order Tencent Realtime, Sina Realtime, EastMoney Direct, AkShare, BaoStock, Local Cache, then Demo. `data/local_cache.py` stores `cache/a_share_universe_latest.csv` and `cache/a_share_quotes_latest.csv`; external source success with more than 1000 rows writes cache, and external failure reads Local Cache before Demo. Dashboard and System Status expose data source, data status, raw count, filtered count, cache status, cache update time, load time, and update time. This version only strengthens the free data-source and cache layer and does not modify stock-selection algorithms, scoring weights, `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, or `selection_score`.

V6.3.5 file additions and data artifacts:

- `data/local_cache.py`
- `cache/a_share_universe_latest.csv` runtime cache, ignored by Git
- `cache/a_share_quotes_latest.csv` runtime cache, ignored by Git
- Full A-Share Pagination in `data/tencent_loader.py`
- Cache Layer in `data/a_share_loader.py`

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
|-- selection/
|   |-- __init__.py
|   |-- explain_engine.py
|   `-- stock_selection.py
|-- factor/
|   |-- __init__.py
|   |-- factor_lab.py
|   |-- factor_metrics.py
|   `-- factor_report.py
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
|   |-- test_factor_lab.py
|   |-- test_factor_metrics.py
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
    |-- chart_center.py
    |-- chart_components.py
    |-- report_ui.py
    |-- report_builder.py
    |-- product_ui.py
    |-- screening_ui.py
    |-- strategy_diagnostics_panel.py
    |-- terminal_components.py
    |-- terminal_ui.py
    |-- visual_components.py
    |-- visual_theme.py
    |-- workstation_components.py
    |-- workstation_theme.py
    `-- workstation_ui.py
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
| Stock selection | `selection/stock_selection.py` | active | Read-only selection score, bucket, rank, reasons, and risk notes from existing research fields |
| Explainable selection | `selection/explain_engine.py` | active | Read-only thesis, strengths, risks, factor breakdown, explanation, and summary for selection rows |
| Backtest helpers | `strategy/backtest.py` | internal research | Caller-provided validation samples only |
| Backtest diagnostics | `strategy/backtest_diagnostics.py` | internal research | Backtest summary schema and diagnostics |
| Export | `strategy/export.py` | internal research | JSON-like snapshot payloads |
| Report | `strategy/report.py` | active | Strategy report assembly |
| Web UI report experience | `ui/report_ui.py` | active | Read-only Streamlit report layout, metrics, cards, formatted tables, warning collection, and data-quality summaries |
| Research Terminal UI | `ui/terminal_ui.py` | active | Read-only terminal layout for dashboard, top picks, stock detail, score breakdown, backtest, risk center, compare panel, and report preview |
| Research Terminal components | `ui/terminal_components.py` | active | Safe DataFrame copying, field formatting, dashboard summary, warning collection, risk grouping, comparison table helpers, and Streamlit component helpers |
| Research report builder | `ui/report_builder.py` | active | Read-only single-stock research report preview text from existing row fields |
| Visual terminal theme | `ui/visual_theme.py` | active | Shared CSS, terminal header, section titles, score badges, risk badges, and status badges |
| Visual terminal components | `ui/visual_components.py` | active | Metric cards, stock cards, score bars, warning boxes, report blocks, quality badges, risk badges, and comparison table rendering |
| Research Workstation UI | `ui/workstation_ui.py` | active | Three-column professional research workspace with navigator, research area, thesis panel, score/risk/backtest centers, compare workspace, pipeline, and report preview |
| Research Workstation components | `ui/workstation_components.py` | active | Safe field access, missing-value handling, metric cards, stock cards, score bars, risk cards, badges, report blocks, and compare table rendering |
| Research Workstation theme | `ui/workstation_theme.py` | active | Bloomberg/GitHub dark CSS, sticky workstation header, section titles, badges, and tone mapping |
| Chart Center | `ui/chart_center.py` | active | Read-only chart center for score profile, return-risk scatter, drawdown-risk view, score breakdown, ranking, and quality distribution |
| Chart components | `ui/chart_components.py` | active | Safe numeric conversion, defensive chart DataFrame preparation, ranking data, scatter data, score profile data, and distribution data |
| Web Product Integration | `ui/product_ui.py` | active | Product-level navigation, dashboard, module pages, data-quality status, Chart Center page, Factor Lab page, and empty-state-safe Streamlit rendering |
| Research Score Activation | `research.score_activation` | active | Additive realtime quote activation fields for research scoring without overwriting old score columns |
| Factor Research Lab | `factor/factor_lab.py` | active | Read-only factor dataset builder, z-score normalization, factor grouping, factor warnings, and factor summaries |
| Factor metrics | `factor/factor_metrics.py` | active | Pearson IC, Rank IC, group returns, and factor effectiveness labels |
| Factor report | `factor/factor_report.py` | active | Structured neutral factor research report fields |
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

### Stock Selection Fields

| Field | Source | Meaning |
|---|---|---|
| `selection_available` | `selection.stock_selection` | Whether existing research fields are sufficient for read-only stock-selection research |
| `selection_score` | `selection.stock_selection` | Read-only stock-selection score from composite score, candidate pool, backtest evaluation, and risk penalty |
| `selection_level` | `selection.stock_selection` | Selection level: High, Medium, Low, or Unavailable |
| `selection_status` | `selection.stock_selection` | Selection status: Selected, Watch, Excluded, or Incomplete |
| `selection_bucket` | `selection.stock_selection` | Selection bucket: Core, Watch, Exclude, or Unavailable |
| `selection_rank` | `selection.stock_selection` | Read-only rank based on selection score without changing row order |
| `selection_reasons` | `selection.stock_selection` | Explainable reasons for the selection layer result |
| `selection_risk_notes` | `selection.stock_selection` | Risk and quality notes for research review |
| `selection_quality_label` | `selection.stock_selection` | Selection quality label: Strong, Normal, Weak, or Unavailable |
| `selection_warnings` | `selection.stock_selection` | Missing, abnormal, or unavailable field warnings |

Stock Selection Fields are read-only research fields for structuring candidate review. V3.8.0 integrates existing upstream fields with default selection-layer weights: Composite Score 50%, Candidate Pool 20%, Backtest Evaluation 20%, and Risk Penalty 10%. It does not modify upstream scoring weights or overwrite `composite_score`, `candidate_rank`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`. It does not create buy or sell advice, buy/sell points, target prices, position suggestions, automated trading workflows, strategy optimization, parameter search, machine-learning predictions, or return promises. It does not change default sorting, default screening workflow, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Event modules, Memory modules, stock pools, data sources, or trading logic.

### Explainable Selection Fields

| Field | Source | Meaning |
|---|---|---|
| `explain_available` | `selection.explain_engine` | Whether selection explanation can be generated from available fields |
| `explain_status` | `selection.explain_engine` | Explanation status: Available or Incomplete |
| `selection_thesis` | `selection.explain_engine` | Neutral research thesis such as Quality Growth, Momentum Trend, Watch Candidate, or Weak Candidate |
| `selection_strengths` | `selection.explain_engine` | Strength list detected from fundamental, technical, composite, and historical performance fields |
| `selection_risks` | `selection.explain_engine` | Risk list detected from risk level, drawdown, volatility, and weak historical performance |
| `selection_factor_breakdown` | `selection.explain_engine` | Dictionary of available factor scores used for explanation context |
| `selection_reason_score` | `selection.explain_engine` | Explanation confidence score from 0 to 100 based on field completeness and detected evidence |
| `selection_explanation` | `selection.explain_engine` | Natural-language explanation of bucket, rank, score, thesis, strengths, and risks |
| `selection_summary` | `selection.explain_engine` | Short one-line summary of the explanation |
| `explain_warnings` | `selection.explain_engine` | Missing, abnormal, or unavailable explanation warnings |

Explainable Selection Fields are read-only explanation fields for understanding selection-layer outputs. V3.9.0 does not modify `selection_score`, `selection_rank`, `selection_bucket`, `selection_status`, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, or `core/scoring.py`. It does not create buy or sell advice, buy/sell points, target prices, position suggestions, automated trading workflows, strategy optimization, parameter search, machine-learning predictions, return promises, external APIs, databases, vector stores, news sources, or data-source changes. It does not change default sorting, default screening workflow, Candidate Pool modules, Backtest modules, Return Analysis modules, Backtest Evaluation modules, Stock Selection modules, Event modules, Memory modules, stock pools, or trading logic.

### Web UI Report Experience

| Area | Source | Meaning |
|---|---|---|
| Top overview | `ui.report_ui` | Version, stage, research-object count, Core/Watch/Exclude counts, and explainable-result count |
| Candidate overview | `ui.report_ui` | Candidate pool, selection bucket, rank, score, status, and quality label |
| Stock research cards | `ui.report_ui` | Per-stock ticker, name, selection score, rank, bucket, thesis, summary, strengths, risks, and explanation |
| Score breakdown | `ui.report_ui` | Fundamental, technical, composite, risk, selection score, and factor-breakdown display |
| Backtest performance | `ui.report_ui` | Period return, annualized return, volatility, max drawdown, win rate, return-risk ratio, performance label, and quality label |
| Risk notes | `ui.report_ui` | Selection risk notes plus backtest, return-analysis, and explanation warnings |
| Data quality | `ui.report_ui` | Warning summary plus Incomplete and Unavailable status collection |

Web UI Report Experience is a read-only Streamlit presentation layer. V4.0.0 does not add a new selection algorithm, does not modify scoring logic, does not modify `selection_score`, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, or `core/scoring.py`, and does not change default sorting or the default screening workflow. It only formats existing result fields into clearer report sections using metrics, tabs, dataframes, and card-style containers. It does not add APIs, databases, vector stores, news sources, external services, automated trading interfaces, machine-learning predictions, buy/sell advice, target prices, position suggestions, or return promises.

### Research Terminal UI Package

| Area | Source | Meaning |
|---|---|---|
| Research Dashboard | `ui.terminal_ui` | Total research-object count, Core/Watch/Exclude counts, average selection/composite scores, high-risk count, and incomplete-data count |
| Top Picks | `ui.terminal_ui` | Top Core/Watch cards with ticker, name, rank, score, bucket, thesis, summary, strengths, and risks |
| Stock Detail Panel | `ui.terminal_ui` | Single-stock detail tabs for basic information, score breakdown, explanation fields, backtest view, risk notes, and data-quality notes |
| Score Breakdown | `ui.terminal_components` | Fundamental, technical, composite, risk, and selection score display with metrics and progress bars |
| Backtest Panel | `ui.terminal_ui` | Period return, annualized return, volatility, max drawdown, win rate, return-risk ratio, performance label, and quality label |
| Risk Center | `ui.terminal_components` | High Risk, High Drawdown, High Volatility, Missing Data, and Unavailable grouped views |
| Compare Panel | `ui.terminal_components` | 2-5 object comparison across selection, composite, fundamental, technical, return, drawdown, volatility, risk, and performance fields |
| Research Report Preview | `ui.report_builder` | Read-only single-stock research report preview with summary, core logic, scores, history, risks, data quality, and follow-up questions |

Research Terminal UI Package is a read-only Streamlit terminal experience layer. V4.1.0 does not add a new selection algorithm, does not modify scoring logic, does not modify `selection_score`, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, or `core/scoring.py`, and does not change default sorting or the default screening workflow. It only reorganizes existing result fields into dashboard, card, detail, risk, comparison, and report-preview sections. It does not add APIs, databases, vector stores, news sources, external services, machine-learning predictions, target prices, position suggestions, return promises, or operational conclusions.

### Visual Research Terminal Redesign

| Area | Source | Meaning |
|---|---|---|
| Unified theme | `ui.visual_theme` | Shared CSS, terminal-style header, section titles, and badge helpers for score, risk, and status states |
| Visual components | `ui.visual_components` | Metric cards, stock cards, score bars, risk badges, quality badges, warning boxes, report blocks, and comparison table rendering |
| Terminal header | `ui.terminal_ui` | Fin-Scientist, Research Intelligence Terminal, current version, current stage, and research-only system note |
| Dashboard cards | `ui.terminal_ui` | Card-based metrics for total objects, Core/Watch/Exclude, average scores, high-risk count, and incomplete-data count |
| Top Picks cards | `ui.visual_components` | Card-based Core/Watch review with ticker, name, rank, score, bucket, thesis, summary, strengths, risks, and data-quality notes |
| Score visualization | `ui.visual_components` | Progress bars, metric values, and badges for fundamental, technical, composite, risk, and selection scores |
| Risk center redesign | `ui.terminal_ui` | Grouped risk tabs with visual count cards and formatted tables for High Risk, High Drawdown, High Volatility, Missing Data, and Unavailable |
| Report preview redesign | `ui.report_builder` and `ui.visual_components` | Numbered research report structure rendered as a report block plus optional pure-text preview |

Visual Research Terminal Redesign is a read-only presentation-layer upgrade. V4.2.0 does not add a new selection algorithm, does not modify scoring logic, does not modify `selection_score`, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, or `core/scoring.py`, and does not change default sorting or the default screening workflow. It only changes visual layout, CSS, card rendering, badges, progress bars, risk grouping presentation, comparison formatting, and report preview layout. It does not add APIs, databases, vector stores, news sources, external services, machine-learning predictions, target prices, position suggestions, return promises, or operational conclusions.

### Research Workstation

| Area | Source | Meaning |
|---|---|---|
| Workstation theme | `ui.workstation_theme` | Bloomberg/GitHub dark CSS, sticky header, version/stage metadata, section titles, and badge tone mapping |
| Workstation components | `ui.workstation_components` | Safe field access, defensive DataFrame copying, metric cards, stock cards, score bars, risk cards, badges, report blocks, and comparison table rendering |
| Research Navigator | `ui.workstation_ui` | Left-side CORE/WATCH/EXCLUDED grouping from `selection_bucket`, with button-based object switching instead of dropdown navigation |
| Research Header | `ui.workstation_ui` | Sticky header with current object, update time, candidate count, CORE count, WATCH count, and average score |
| Research Area | `ui.workstation_ui` | Central object overview with score, rank, bucket, quality, status, thesis, strengths, risks, and factor breakdown panels |
| Thesis Panel | `ui.workstation_ui` | Right-side read-only research report preview from `ui.report_builder` |
| Risk & Score Analysis | `ui.workstation_ui` | Full-width score breakdown center, risk center, backtest center, compare workspace, and research pipeline |

Research Workstation is a read-only professional UI workspace. V5.0.0 does not add a new selection algorithm, does not modify scoring logic, does not modify `selection_score`, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, or `core/scoring.py`, and does not change default sorting or the default screening workflow. It only reorganizes existing results into a professional workstation layout with navigation, cards, badges, score bars, risk cards, comparison tables, pipeline status, and report preview. It does not add APIs, databases, vector stores, news sources, external services, machine-learning predictions, target prices, position suggestions, return promises, or operational conclusions.

### Chart Center

| Area | Source | Meaning |
|---|---|---|
| Chart data helpers | `ui.chart_components` | Safe numeric conversion, defensive chart DataFrame copies, score profile data, scatter data, drawdown-risk data, ranking data, and quality distribution data |
| Score Profile | `ui.chart_center` | Single-object visualization for `fundamental_score`, `technical_score`, `composite_score`, `selection_score`, and `risk_score` |
| Return-Risk Scatter | `ui.chart_center` | Candidate-pool scatter view using `volatility` or `risk_score` against `period_return` or `annualized_return` |
| Drawdown-Risk View | `ui.chart_center` | Candidate-pool risk view for `max_drawdown`, `volatility`, and `risk_level` |
| Score Breakdown Bar | `ui.chart_center` | Single-object bar chart for score decomposition |
| Candidate Ranking Bar | `ui.chart_center` | Top N `selection_score` ranking view without changing default sorting |
| Quality Distribution | `ui.chart_center` | Distribution charts for Core/Watch/Exclude and High/Medium/Low groups |

Chart Center is a read-only visualization layer inside the Research Workstation. V5.1.0 does not add a new selection algorithm, does not modify scoring logic, does not modify `selection_score`, `candidate_rank`, `composite_score`, `fundamental_score`, `technical_score`, `strategy_score`, `research_priority_score`, `priority_stability_score`, or `core/scoring.py`, and does not change default sorting or the default screening workflow. It only turns existing fields into charts using safe DataFrame copies and Streamlit-native chart fallbacks. It does not add APIs, databases, vector stores, news sources, external services, machine-learning predictions, target prices, position suggestions, return promises, or operational conclusions.

### Factor Research Lab

| Area | Source | Meaning |
|---|---|---|
| Factor dataset | `factor.factor_lab` | Long-format read-only factor dataset from existing scores and return-analysis fields |
| Factor normalization | `factor.factor_lab` | Z-score normalization for available factor fields without mutating input DataFrames |
| Factor grouping | `factor.factor_lab` | Q1-Q5 quantile groups for single-factor review while preserving input row order |
| Factor IC | `factor.factor_metrics` | Pearson correlation between factor value and `future_return` or `period_return` |
| Rank IC | `factor.factor_metrics` | Spearman correlation between factor value and `future_return` or `period_return` |
| Group returns | `factor.factor_metrics` | Mean return by factor group for read-only factor inspection |
| Factor report | `factor.factor_report` | Structured factor research report with summary, label, warnings, and group-return table |
| Workstation view | `ui.workstation_ui` | Factor Research Lab section inside Research Workstation with factor overview, group returns, and research summary |

Factor Research Lab is a read-only quantitative factor research foundation. V6.0.0 adds `factor_available`, `factor_name`, `factor_value`, `factor_zscore`, `factor_group`, `factor_ic`, `factor_rank_ic`, `factor_group_return`, `factor_effectiveness_label`, `factor_research_summary`, and `factor_warnings`. It uses existing `fundamental_score`, `technical_score`, `composite_score`, `selection_score`, `risk_score`, and `return_risk_ratio` fields as default factor candidates and uses `future_return` or `period_return` only when available for IC review. It does not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, default sorting, default screening workflow, upstream research modules, data sources, or trading logic.

### Web Product Integration

| Area | Source | Meaning |
|---|---|---|
| Product navigation | `app.py` and `ui.product_ui` | Left-side Streamlit navigation across the integrated research platform |
| Dashboard page | `ui.product_ui` | Card-based total count, Core/Watch/Exclude, average score, factor count, backtest count, and incomplete-data count |
| Universe page | `ui.product_ui` | A-share Universe table with market, ST, suspended, and status filters |
| Selection page | `ui.product_ui` | Selection result table plus Top Core, Top Watch, risk, and missing-data groups |
| Workstation page | `ui.product_ui` and `ui.workstation_ui` | Existing Research Workstation visible from product navigation |
| Backtest page | `ui.product_ui` | Historical return, volatility, drawdown, win rate, return-risk ratio, performance label, and quality label |
| Chart Center page | `ui.product_ui` and `ui.chart_center` | Ranking, return-risk scatter, risk view, candidate distribution, and score breakdown |
| Factor Lab page | `ui.product_ui` and `factor.*` | Factor overview, IC, Rank IC, Q1-Q5 group returns, effectiveness label, and research summary |
| Report page | `ui.product_ui` and `ui.report_builder` | Read-only single-object research report preview |
| System status page | `ui.product_ui` | Version, stage, module registry, missing fields, warning summary, test status, and data-source notes |

Web Product Integration is a read-only Streamlit product layer. V6.1.0 makes completed modules visible through a unified product navigation and stores screening pipeline outputs in session state for reuse by the product pages. Empty DataFrames and missing fields render page structure and explanatory notices instead of blank pages. It does not modify `core/scoring.py`, `strategy_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, default sorting, default screening workflow, upstream research modules, data sources, or trading logic.

### Research Score Activation

| Field | Source | Meaning |
|---|---|---|
| `quote_available` | `research.score_activation` | Whether realtime quote fields are sufficient for score activation |
| `quote_quality_score` | `research.score_activation` | Completeness score for realtime price, change, volume, turnover, and OHLC fields |
| `liquidity_score` | `research.score_activation` | Liquidity score based on turnover, with volume fallback |
| `momentum_score` | `research.score_activation` | Neutral short-term price-change context score |
| `price_position_score` | `research.score_activation` | Intraday price-position score from latest, open, high, and low |
| `activated_technical_score` | `research.score_activation` | Additive technical activation from liquidity, momentum, and price position |
| `activated_composite_score` | `research.score_activation` | Additive composite activation using old composite score when available, otherwise quote-derived inputs |
| `activated_selection_score` | `research.score_activation` | Additive research selection activation score with optional risk-score deduction |
| `activated_research_level` | `research.score_activation` | High, Medium, Low, or Unavailable research level |
| `activated_research_bucket` | `research.score_activation` | Core, Watch, Exclude, or Unavailable research bucket |
| `activated_research_status` | `research.score_activation` | Selected, Watch, Excluded, or Incomplete research status |
| `activated_research_reasons` | `research.score_activation` | Neutral reasons explaining score activation inputs |
| `activated_research_warnings` | `research.score_activation` | Data-quality and short-term volatility warnings |

Research Score Activation is additive and read-only. V6.4.0 does not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, existing scoring functions, default sorting, stock-selection algorithms, data-source order, or trading logic. It only lets realtime quote fields participate in separate activated research fields for learning, screening structure, and further research review.

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
