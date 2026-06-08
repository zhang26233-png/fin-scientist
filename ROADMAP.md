# Fin-Scientist Roadmap

> Project roadmap for the permanent memory system. All outputs remain learning and research only, and do not constitute investment advice.

## v1.7.x - Research Intelligence Layer

Previous completed: v1.7.3.

- v1.7.0: Composite Profile Layer.
- v1.7.1: Research Priority Layer.
- v1.7.2: Research Priority Stability Layer completed.
- v1.7.3: Architecture Audit Layer completed.
- v1.7.x rules:
  - Keep screening output unchanged.
  - Keep default sorting unchanged.
  - Keep `strategy_score` unchanged unless explicitly scoped and tested.
  - Keep `core/scoring.py` unchanged by default.
  - Keep all new outputs neutral and research-only.

Completed v1.7.2 scope:

- Added read-only drift checks for `research_priority_score` and `research_priority_level`.
- Added tests for idempotence, input immutability, stable ordering, unavailable priority fields, and neutral wording.
- Added compact diagnostic notes when priority fields are unavailable or inconsistent.
- Did not add new data sources.
- Did not change UI sorting.
- Did not change `strategy_score`.
- Did not modify `core/scoring.py`.

Next stage:

- v1.8.x Event-Driven Research System.

Completed v1.7.3 scope:

- Added read-only architecture audit fields for module presence, field registry, boundary, and preview contract diagnostics.
- Added tests for module presence, field contract, boundary preservation, neutral wording, immutability, and stable ordering.
- Did not add new data sources.
- Did not change UI sorting.
- Did not change `strategy_score`, `research_priority_score`, or `priority_stability_score`.
- Did not modify `core/scoring.py`.

## v1.8.x - Event-Driven Research System

Current: v1.8.3.

Goal: connect research candidates with event context while keeping outputs non-operational.

- v1.8.0: Event Foundation Layer completed.
- v1.8.1: Event Diagnostics Layer completed.
- v1.8.2: Event Confluence Layer completed.
- v1.8.3: Event Research Summary Layer completed.
- Next target: v1.8.4 Event Panel Polish / Export Readiness.
- Event field standardization.
- Event type tags: earnings, policy, industry, macro, product, risk, data-quality, news-only.
- Event recency and source-quality labels.
- Event-to-research-context mapping.
- Event impact notes phrased as research hypotheses, not conclusions.
- Event reliability diagnostics.
- Optional event panel in the existing Streamlit workflow.

Completed v1.8.0 scope:

- Added read-only `strategy/event_context.py`.
- Added event availability, type, recency, source quality, reliability, context note, research tags, and warnings.
- Standardizes caller-provided event fields only.
- Does not fetch news, add external data sources, change stock pools, change default sorting, change default screening output, modify `strategy_score`, or modify `core/scoring.py`.

Completed v1.8.1 scope:

- Added read-only `strategy/event_diagnostics.py`.
- Added event completeness, clarity, consistency, confidence, diagnostic level, summary, follow-up questions, evidence gaps, and quality warnings.
- Diagnoses standardized event context and caller-provided raw event fields only.
- Does not crawl news, call external APIs, add external data sources, change stock pools, change default sorting, change default screening output, modify `strategy_score`, or modify `core/scoring.py`.

Completed v1.8.2 scope:

- Added read-only `strategy/event_confluence.py`.
- Added event confluence label, score, summary, support points, conflict points, follow-up focus, and warnings.
- Compares event context and diagnostics with existing technical, fundamental, industry-relative, and composite research profile fields.
- Does not crawl news, call external APIs, add external data sources, change stock pools, change default sorting, change default screening output, modify `strategy_score`, or modify `core/scoring.py`.

Completed v1.8.3 scope:

- Added read-only `strategy/event_research_summary.py`.
- Added event research summary, research level, key evidence, key risks, validation focus, Agent note, and summary warnings.
- Organizes event context, diagnostics, and confluence into structured research notes for future Agent use.
- Does not crawl news, call external APIs, add external data sources, change stock pools, change default sorting, change default screening output, modify `strategy_score`, or modify `core/scoring.py`.

Boundary:

- No operational advice.
- No automatic order execution.
- No event-triggered trading workflow.
- No news crawling in v1.8.0.
- No data-source change in v1.8.0.
- No `strategy_score` change in v1.8.0.
- No news crawling in v1.8.1.
- No API integration in v1.8.1.
- No data-source change in v1.8.1.
- No `strategy_score` change in v1.8.1.
- No news crawling in v1.8.2.
- No API integration in v1.8.2.
- No data-source change in v1.8.2.
- No `strategy_score` change in v1.8.2.
- No news crawling in v1.8.3.
- No API integration in v1.8.3.
- No data-source change in v1.8.3.
- No `strategy_score` change in v1.8.3.

## v1.9.x - Research Pipeline Validation Layer

Current: v1.9.1.

Goal: validate whether the research pipeline is complete and internally consistent while keeping outputs read-only.

- v1.9.0: Research Pipeline Validation Layer completed.
- v1.9.1: Pre-v2 Project Assessment Layer completed.
- Next target: v2.0.0 Research Memory Foundation.

Completed v1.9.0 scope:

- Added read-only `strategy/research_pipeline_audit.py`.
- Added research pipeline status, conflicts, warnings, and summary.
- Checks composite/priority consistency, event diagnostics/confluence consistency, event confluence/summary consistency, required module fields, and pipeline completeness.
- Does not crawl news, call external APIs, add external data sources, change stock pools, change default sorting, change default screening output, modify `strategy_score`, or modify `core/scoring.py`.

Completed v1.9.1 scope:

- Added read-only `strategy/project_assessment.py`.
- Added project assessment status, score, architecture note, field registry note, test coverage note, UI readability note, data source note, scoring boundary note, pre-v2 readiness level, blockers, and route fields.
- Assesses architecture, field registry growth, UI density, test coverage, data-source boundaries, scoring boundaries, and readiness for v2.0.
- Does not crawl news, call external APIs, add external data sources, change stock pools, change default sorting, change default screening output, modify `strategy_score`, or modify `core/scoring.py`.

Boundary:

- No operational advice.
- No automatic order execution.
- No event-triggered trading workflow.
- No scoring-system change.
- No sorting change.
- No data-source change.

## v2.x - Research Memory Foundation

Goal: persist and organize read-only research memory snapshots after the v1.x pipeline is assessed as ready.

- Current: v2.2.0.
- v2.0.0: Research Memory Foundation completed.
- v2.1.0: Research Timeline Layer completed.
- v2.2.0: Research Journal Layer completed.
- Next target: v2.3.0 Memory Retrieval.
- Read-only memory snapshot schema.
- Candidate research memory records.
- Field-grouped export payloads.
- Evidence, diagnostics, event, and pipeline memory sections.
- Memory metadata for version, source boundary, and data-quality notes.
- No automated decision workflow.

Completed v2.0.0 scope:

- Added read-only `memory/research_memory.py`.
- Added Research Snapshot Schema with snapshot identity, timestamp, ticker, name, version, stage, summary, status, and grouped research sections.
- Added grouped technical, fundamental, industry, composite, priority, event, pipeline, and project snapshots.
- Added tests for empty input, normal generation, missing fields, input immutability, fixed output order, status handling, module import, and score preservation.
- Did not add databases, vector stores, news sources, APIs, external services, data-source changes, stock-pool changes, sorting changes, default screening changes, scoring changes, or `core/scoring.py` changes.

Completed v2.1.0 scope:

- Added read-only `memory/research_timeline.py`.
- Added Research Timeline Schema with timeline identity, ticker, name, snapshot count, start time, end time, status, direction, change summary, key changes, priority trend, event trend, pipeline trend, and warnings.
- Sorts Research Snapshots by `snapshot_timestamp` and compares only same-`snapshot_ticker` snapshots.
- Emits warnings for empty input, insufficient snapshots, missing timestamps, missing ticker, inconsistent ticker, and missing trend sections.
- Added tests for empty input, single-snapshot incomplete output, available multi-snapshot timelines, timestamp sorting, ticker inconsistency warning, priority/event/pipeline trend detection, timeline direction, input immutability, module import, and score-field preservation.
- Did not add databases, vector stores, news sources, APIs, external services, data-source changes, stock-pool changes, sorting changes, default screening changes, scoring changes, or `core/scoring.py` changes.

Completed v2.2.0 scope:

- Added read-only `memory/research_journal.py`.
- Added Research Journal Schema with journal identity, ticker, name, period, status, summary, observations, risk notes, data quality notes, follow-up questions, Agent research tasks, and warnings.
- Converts one Research Snapshot plus one Research Timeline into human-readable and Agent-ready research notes.
- Extracts content from `snapshot_summary`, `priority_snapshot`, `event_snapshot`, `pipeline_snapshot`, `timeline_change_summary`, and `timeline_key_changes`.
- Keeps Agent tasks limited to research review, evidence validation, and pipeline conflict investigation.
- Added tests for empty input, snapshot-only incomplete output, available Snapshot+Timeline output, generated summary, observations, risk notes, follow-up questions, Agent tasks, input immutability, restricted-word cleanup, module import, and score-field preservation.
- Did not add databases, vector stores, news sources, APIs, external services, data-source changes, stock-pool changes, sorting changes, default screening changes, scoring changes, or `core/scoring.py` changes.

Future v2.x direction:

- v2.1.0: Research Timeline.
- v2.2.0: Research Journal.
- v2.3.0: Memory Retrieval.

Boundary:

- Research memory is for learning and review only.
- No promise of future performance.
- No operational language.
- No score or sorting changes by memory persistence.
- No database or vector-store dependency in v2.0.0.

## v3.x - Quantitative Research Foundation

Current: v3.3.0.

Goal: build shared universe, screening, scoring, and validation entry points before any machine learning layer.

- v3.0.0: A-Share Universe Engine completed.
- v3.1.0: Fundamental Screening completed.
- v3.2.0: Technical Screening completed.
- v3.3.0: Composite Quant Score Engine completed.
- Next target: v3.4.0 Candidate Pool Engine.
- A-share universe builder.
- Fundamental screening entry point.
- Technical screening entry point.
- Composite score preparation.
- Backtest engine entry point.
- Future feature registry from current strategy fields.
- Future dataset builder with leakage checks.
- Future train/test split and time-aware validation.

Completed v3.0.0 scope:

- Added `universe/a_share_universe.py`.
- Added `build_a_share_universe()` with AkShare as the preferred source and safe empty DataFrame fallback.
- Added fields for ticker, name, market, list date, days since listing, ST flag, suspended flag, row status, universe status, total count, filtered count, and universe summary.
- Added default filters for ST, delisted securities, suspended securities, and listings with fewer than 250 days.
- Added read-only A-Share Universe panel to the screening page with total count, filtered count, filter rules, and Universe Summary.
- Added tests for empty data, single stock, ST filtering, suspended filtering, new-stock filtering, field completeness, and module import.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, event modules, memory modules, default sorting, default filters, stock pools, data sources outside the new universe builder, or trading logic.

Completed v3.1.0 scope:

- Added `screening/fundamental_screening.py`.
- Added `build_fundamental_screening()` for read-only fundamental screening on A-share Universe rows.
- Added fundamental fields for availability, ROE, revenue growth, profit growth, gross margin, debt ratio, operating cashflow, PE, PB, score, level, status, reasons, and warnings.
- Covers profitability, growth, valuation, financial risk, and cashflow quality with safe missing-data handling.
- Added a read-only Fundamental Screening panel to the screening page without changing default sorting.
- Added tests for empty Universe, missing fundamental data, normal generation, High/Pass output, weak output, warnings, immutability, order preservation, old score preservation, and module import.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, event modules, memory modules, default sorting, default filters, stock pools, data sources, or trading logic.

Completed v3.2.0 scope:

- Added `screening/technical_screening.py`.
- Added `build_technical_screening()` for read-only technical screening on A-share Universe rows.
- Added technical fields for availability, close, MA20, MA60, MA position, MA trend, RSI14, MACD signal, volume ratio, score, level, status, reasons, and warnings.
- Supports caller-provided price snapshots and price history dictionaries with safe missing-data handling.
- Added a read-only Technical Screening panel to the screening page without changing default sorting.
- Added tests for empty Universe, missing price data, normal generation, High/Pass output, weak output, RSI warnings, MACD bearish downgrade, missing-field warnings, immutability, order preservation, `fundamental_score` preservation, and module import.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, fundamental modules, event modules, memory modules, default sorting, default filters, stock pools, data sources, backtest logic, machine-learning logic, or trading logic.

Completed v3.3.0 scope:

- Added `screening/composite_score_engine.py`.
- Added `build_composite_quant_score()` for read-only composite quant scoring on A-share Universe rows.
- Added composite fields for availability, score, level, screening status, reasons, warnings, and score breakdown.
- Uses default weights: 50% `fundamental_score` and 50% `technical_score`.
- Safely returns Incomplete/Unavailable when Fundamental or Technical inputs are missing or invalid.
- Added a read-only Composite Quant Score panel to the screening page without changing default sorting.
- Added tests for empty Universe, missing Fundamental input, missing Technical input, normal generation, High/Pass output, Medium/Watch output, Low/Watch output, Exclude output, readable score breakdown, warnings, immutability, order preservation, `fundamental_score` preservation, `technical_score` preservation, and module import.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, `technical_score`, Universe modules, Fundamental modules, Technical modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, backtest logic, machine-learning logic, or trading logic.

Boundary:

- Models must not generate black-box operational conclusions.
- Model outputs remain research signals for further review.
- Human-readable diagnostics are required.
- No universe output is an investment recommendation or trading instruction.

## v4.x - Deep Learning Research Layer

Goal: explore deep learning only after stable datasets and validation loops exist.

- Sequence datasets for price, factor, event, and fundamental history.
- Time-series representation learning.
- News/event embedding experiments.
- Multi-modal research summaries.
- Strict leakage prevention.
- Model card and failure-mode documentation.

Boundary:

- Deep learning cannot bypass validation, diagnostics, or safety wording.
- No opaque model output may become an operational conclusion.

## v5.x - AI Research Agent

Goal: build an AI research assistant that can organize evidence, ask follow-up questions, and produce neutral research notes.

- Agent memory connected to `PROJECT_MASTER.md`, `ROADMAP.md`, and `CHANGELOG.md`.
- Research task planner.
- Candidate evidence collector.
- Technical/fundamental/industry/event synthesis.
- Risk and data-quality challenge step.
- Backtest-aware confidence notes.
- Research note generator.
- Human approval checkpoint before any report is considered complete.

Boundary:

- Agent is a research assistant, not an automated trader.
- Agent must preserve "not investment advice" language.
- Agent must cite field evidence and data-quality gaps.

## Version Upgrade Rule

Every version upgrade must update:

- `PROJECT_MASTER.md`
- `ROADMAP.md`
- `CHANGELOG.md`

If these files are not synchronized, the version upgrade is incomplete.
