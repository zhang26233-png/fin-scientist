# Fin-Scientist Roadmap

> Project roadmap for the permanent memory system. All outputs remain learning and research only, and do not constitute investment advice.

## v1.7.x - Research Intelligence Layer

Current: v1.7.3.

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

Goal: connect research candidates with event context while keeping outputs non-operational.

- Event field standardization.
- Event type tags: earnings, policy, industry, macro, product, risk, data-quality, news-only.
- Event recency and source-quality labels.
- Event-to-research-context mapping.
- Event impact notes phrased as research hypotheses, not conclusions.
- Event reliability diagnostics.
- Optional event panel in the existing Streamlit workflow.

Boundary:

- No operational advice.
- No automatic order execution.
- No event-triggered trading workflow.

## v2.x - Backtest Validation System

Goal: validate whether research fields are stable and useful over historical samples.

- Formal backtest dataset schema.
- Historical sample builder with explicit data source boundary.
- Forward-window validation: 1d, 3d, 5d, 10d, 20d.
- Score bucket diagnostics.
- Research priority stability diagnostics.
- Preset-level validation.
- Industry-level validation.
- Data-quality-aware validation.
- Backtest report export.

Boundary:

- Backtests are validation tools only.
- No promise of future performance.
- No operational recommendation language.

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
