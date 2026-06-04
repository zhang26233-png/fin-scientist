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

- Current: v2.0.0.
- v2.0.0: Research Memory Foundation completed.
- Next target: v2.1.0 Research Timeline.
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

Future v2.x direction:

- v2.1.0: Research Timeline.
- v2.2.0: Research Journal.
- v2.3.0: Research Retrieval.

Boundary:

- Research memory is for learning and review only.
- No promise of future performance.
- No operational language.
- No score or sorting changes by memory persistence.
- No database or vector-store dependency in v2.0.0.

## v3.x - Machine Learning Research Layer

Goal: use machine learning to assist research prioritization and diagnostics after backtest validation exists.

- Feature registry from current strategy fields.
- Dataset builder with leakage checks.
- Train/test split and time-aware validation.
- Baseline models: logistic/regression/tree-based models where appropriate.
- Feature importance and explainability reports.
- Model confidence and data coverage labels.
- Model drift monitoring.

Boundary:

- Models must not generate black-box operational conclusions.
- Model outputs remain research signals for further review.
- Human-readable diagnostics are required.

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
