# Fin-Scientist Changelog

> Permanent changelog for the project memory system. All entries describe learning and research features only and do not constitute investment advice.

## v6.0.0

- Added Factor Research Lab in `factor/factor_lab.py`.
- Added factor metric helpers in `factor/factor_metrics.py`.
- Added structured factor research reports in `factor/factor_report.py`.
- Added `factor/__init__.py` public API exports.
- Added read-only factor dataset generation for default factors: `fundamental_score`, `technical_score`, `composite_score`, `selection_score`, `risk_score`, and `return_risk_ratio`.
- Added z-score normalization, Q1-Q5 factor grouping, Pearson IC, Rank IC, group returns, factor effectiveness labels, factor research summaries, and factor warnings.
- Added Factor Research Lab into `ui/workstation_ui.py` with factor overview, group-return display, and neutral research summary tabs.
- Updated `app.py`, `legacy_app.py`, README, PROJECT_MASTER, ROADMAP, and CHANGELOG for v6.0.0.
- Added tests for factor module imports, empty DataFrame handling, missing factor fields, missing return fields, z-score calculation, factor grouping, IC calculation, Rank IC calculation, group returns, effectiveness labels, report output, neutral wording, and input immutability.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v5.1.0

- Added Chart Center in `ui/chart_center.py`.
- Added chart data helpers in `ui/chart_components.py`.
- Added Score Radar / Score Profile for single-object score review.
- Added Return-Risk Scatter for candidate-pool risk-return comparison.
- Added Drawdown-Risk View for drawdown, volatility, and risk-level review.
- Added Score Breakdown Bar for single-object score decomposition.
- Added Candidate Ranking Bar for Top N `selection_score` ranking without changing default sorting.
- Added Quality Distribution for Core/Watch/Exclude and High/Medium/Low group review.
- Integrated Chart Center into `ui/workstation_ui.py`.
- Updated `app.py`, `legacy_app.py`, README, PROJECT_MASTER, ROADMAP, and CHANGELOG for v5.1.0.
- Added tests for chart module imports, empty DataFrame handling, missing fields, safe numeric conversion, chart DataFrame immutability, ranking data, scatter data, score profile data, and `app.py` import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v5.0.0

- Added Research Workstation in `ui/workstation_ui.py`.
- Added workstation component library in `ui/workstation_components.py`.
- Added workstation dark theme in `ui/workstation_theme.py`.
- Added sticky Research Header with current object, update time, candidate count, CORE count, WATCH count, average score, version, stage, and research-only boundary.
- Added left Research Navigator that groups objects into CORE, WATCH, and EXCLUDED from `selection_bucket` and uses buttons for object switching.
- Added central Main Research Area for object identity, selection score, rank, bucket, quality label, status badge, risk badge, thesis, strengths, risks, and five-part factor breakdown.
- Added right Thesis Panel with read-only Research Report Preview from `ui/report_builder.py`.
- Added Dashboard Cards for Average Score, Core Candidates, Average Return, and Average Risk Score.
- Added Score Breakdown Center, Risk Center, Backtest Center, Compare Workspace, and Research Pipeline.
- Integrated Research Workstation into `ui/screening_ui.py` after the existing Research Terminal without changing default sorting or upstream DataFrames.
- Updated `app.py`, `legacy_app.py`, README, PROJECT_MASTER, ROADMAP, and CHANGELOG for v5.0.0.
- Added tests for workstation imports, CSS output, safe field access, navigator grouping, dashboard metrics, missing explain fields, missing risk fields, compare generation, report preview generation, empty DataFrame rendering, input immutability, and `app.py` import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v4.2.0

- Added Visual Research Terminal Redesign.
- Added shared visual theme helpers in `ui/visual_theme.py`.
- Added visual Streamlit components in `ui/visual_components.py`.
- Redesigned Research Terminal header into a terminal-style landing header with version, stage, and research-only boundary text.
- Redesigned Dashboard metrics into card-based sections with labels, values, and short explanations.
- Redesigned Top Picks into visual stock cards with ticker, name, rank, score, bucket, thesis, summary, strengths, risks, and data-quality notes.
- Redesigned Score Breakdown with metrics, progress bars, and score badges without changing score values.
- Redesigned Stock Detail Panel with clearer tabs for basic information, summary, score breakdown, explanation, backtest, risk, and data quality.
- Redesigned Risk Center with grouped tabs, visual count cards, and formatted risk tables.
- Redesigned Compare Panel with clearer fields, `selection_thesis` support, and missing-value display.
- Redesigned Research Report Preview as a report-style block with numbered sections and optional pure-text preview.
- Updated `ui/terminal_components.py`, `ui/report_builder.py`, `ui/terminal_ui.py`, `app.py`, `legacy_app.py`, README, PROJECT_MASTER, ROADMAP, and CHANGELOG for v4.2.0.
- Added tests for visual theme import, visual component import, CSS output, badge handling, list formatting, dict formatting, warning aggregation, empty DataFrame handling, missing fields, restricted report wording, input immutability, and `app.py` import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v4.1.0

- Added Research Terminal UI Package in `ui/terminal_ui.py`.
- Added reusable terminal helpers in `ui/terminal_components.py`.
- Added read-only single-stock report preview builder in `ui/report_builder.py`.
- Added Research Dashboard metrics for research-object count, Core/Watch/Exclude counts, average `selection_score`, average `composite_score`, high-risk count, and incomplete-data count.
- Added Top Picks cards, Stock Detail Panel, Score Breakdown, Backtest Panel, Risk Center, Compare Panel, and Research Report Preview.
- Added safe handling for empty DataFrames, missing fields, list formatting, dict formatting, warning aggregation, numeric formatting, and percentage formatting.
- Integrated Research Terminal UI into `ui/screening_ui.py` after the Web UI Report Experience without changing default sorting or upstream DataFrames.
- Updated `app.py` version metadata and synchronized README, PROJECT_MASTER, ROADMAP, and CHANGELOG for v4.1.0.
- Added tests for module import, empty DataFrame handling, missing selection fields, missing explanation fields, list formatting, dict formatting, warning aggregation, report preview text, restricted report wording, input immutability, and `app.py` import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v4.0.0

- Added Web UI Report Experience in `ui/report_ui.py`.
- Added read-only report sections for top overview, candidate overview, stock research cards, score breakdown, backtest performance, risk notes, and data quality.
- Added Streamlit metrics, tabs, dataframes, and card-style containers for clearer research-result presentation.
- Added helpers for safe DataFrame copying, existing-field detection, list/dict formatting, display-table building, and warning/status aggregation.
- Integrated the report section into `ui/screening_ui.py` after Explainable Selection without changing default sorting or upstream DataFrames.
- Added tests for module import, empty DataFrame handling, missing selection fields, missing explanation fields, list formatting, dict formatting, warning aggregation, input immutability, and `app.py` import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v3.9.0

- Added Explainable Selection Engine in `selection/explain_engine.py`.
- Added `build_explainable_selection()` for read-only explanation of Stock Selection rows.
- Added explanation fields for availability, status, thesis, strengths, risks, factor breakdown, reason score, natural-language explanation, summary, and warnings.
- Detects strengths from `fundamental_score`, `technical_score`, `composite_score`, and `performance_label`.
- Detects risks from `risk_level`, `max_drawdown`, `volatility`, and weak historical performance.
- Added a read-only Explainable Selection panel to the screening page.
- Added tests for Core, Watch, Exclude, missing data, unavailable selection, risk detection, factor breakdown, explanation generation, summary generation, row-order preservation, upstream score preservation, empty input, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Candidate Pool modules, Backtest modules, Return Analysis modules, Backtest Evaluation modules, Stock Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, upstream scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v3.8.0

- Added Stock Selection System Package in `selection/stock_selection.py`.
- Added `selection/__init__.py`.
- Added `build_stock_selection()` for read-only selection research from existing Candidate Pool, Composite, Fundamental, Technical, and Backtest Evaluation fields.
- Added selection fields for availability, score, level, status, bucket, rank, reasons, risk notes, quality label, and warnings.
- Uses transparent selection-layer weights: Composite Score 50%, Candidate Pool 20%, Backtest Evaluation 20%, and Risk Penalty 10%.
- Generates `selection_rank` from selection score without changing row order.
- Added a read-only Stock Selection System panel to the screening page.
- Added tests for empty input, missing composite score, Core/high-score Selected output, Watch/medium-score Watch output, Exclude output, high-risk downgrade, poor-backtest-quality downgrade, rank generation, rank order preservation, reasons, risk notes, warnings, input immutability, `composite_score` preservation, `candidate_rank` preservation, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, upstream scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v3.7.0

- Added Backtest Evaluation Package in `backtest/backtest_evaluation.py`.
- Added `build_backtest_evaluation()` for read-only evaluation from Return Analysis rows.
- Added backtest-evaluation fields for availability, status, risk score, risk level, return-risk ratio, drawdown risk level, volatility risk level, performance label, performance summary, backtest quality label, and warnings.
- Evaluates only rows where `return_analysis_available` is true and required return-analysis fields are usable.
- Added a read-only Backtest Evaluation panel to the screening page.
- Added tests for empty input, unavailable return analysis, single stock, multiple stocks, risk score, risk level, return-risk ratio, zero-drawdown warning, performance label, quality label, missing-field warnings, input immutability, row-order preservation, score-field preservation, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest Foundation modules, Return Analysis modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, scoring weights, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, return promises, or operational conclusions.

## v3.6.0

- Added Return Analysis Engine in `backtest/return_analysis.py`.
- Added `build_return_analysis()` for read-only historical metric calculation from Backtest Foundation rows and caller-provided price history.
- Added return-analysis fields for availability, status, holding-period days, entry price, exit price, period return, annualized return, volatility, maximum drawdown, win rate, summary, and warnings.
- Calculates metrics only when `backtest_available` is true and valid `date` plus `close` history has at least 60 rows.
- Added a read-only Return Analysis panel to the screening page.
- Added tests for empty input, missing price history, unavailable backtest foundation, single stock, multiple stocks, period return, annualized return, volatility, maximum drawdown, win rate, missing `close`, missing `date`, input immutability, row-order preservation, score-field preservation, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, or operational conclusions.

## v3.5.0

- Added Backtest Foundation Engine in `backtest/backtest_engine.py`.
- Added `build_backtest_dataset()` for read-only backtest foundation dataset checks from Candidate Pool rows.
- Added backtest fields for availability, status, start date, end date, valid day count, price availability, and warnings.
- Supports caller-provided `price_history_dict` with `date` and `close` columns.
- Marks rows Available only when valid price history has at least 60 rows; otherwise marks Incomplete with warnings.
- Added a read-only Backtest Foundation panel to the screening page.
- Added tests for empty input, missing price history, single stock, multiple stocks, shorter-than-60 histories, at-least-60 histories, date calculation, warning generation, input immutability, row-order preservation, no performance metric fields, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, `technical_score`, `composite_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external APIs, external services, machine learning, returns calculations, cumulative returns, annualized returns, Sharpe ratio, maximum drawdown, win rate, strategy optimization, parameter search, target prices, operational trade points, position suggestions, or automated trading interfaces.

## v3.4.0

- Added Candidate Pool Engine in `screening/candidate_pool.py`.
- Added `build_candidate_pool()` for read-only candidate-pool grouping from Composite Quant Score outputs.
- Added candidate fields for pool group, candidate rank, candidate level, candidate status, reasons, risk flags, and warnings.
- Uses Core, Watch, Exclude, and Unavailable groups based on `composite_level`, `composite_screening_status`, and `composite_available`.
- Generates `candidate_rank` only inside Core/Watch based on `composite_score` descending while preserving input row order.
- Added a read-only Candidate Pool panel to the screening page.
- Added tests for empty input, missing `composite_score`, Core grouping, Watch grouping, Exclude grouping, missing-field warnings, candidate rank generation, rank order preservation, input immutability, `composite_score` preservation, `fundamental_score` preservation, `technical_score` preservation, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, `technical_score`, `composite_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Event modules, Memory modules, default sorting, default filters, stock pools, backtest logic, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external services, machine learning, backtesting changes, target prices, operational trade points, position suggestions, or automated trading interfaces.

## v3.3.0

- Added Composite Quant Score Engine in `screening/composite_score_engine.py`.
- Added `build_composite_quant_score()` for read-only composite quant scoring on A-share Universe rows.
- Added composite fields for availability, composite score, level, screening status, reasons, warnings, and readable score breakdown.
- Uses default weights: 50% `fundamental_score` and 50% `technical_score`.
- Safely returns Incomplete/Unavailable when Fundamental or Technical inputs are missing or invalid.
- Added a read-only Composite Quant Score panel to the screening page.
- Added tests for empty Universe, missing Fundamental input, missing Technical input, normal field generation, High/Pass output, Medium/Watch output, Low/Watch output, Exclude output, score breakdown, warnings, input immutability, row-order preservation, `fundamental_score` preservation, `technical_score` preservation, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, `technical_score`, Universe modules, Fundamental modules, Technical modules, Event modules, Memory modules, default sorting, default filters, stock pools, backtest logic, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external services, machine learning, backtesting changes, target prices, operational trade points, position suggestions, or automated trading interfaces.

## v3.2.0

- Added Technical Screening Engine in `screening/technical_screening.py`.
- Added `build_technical_screening()` for read-only technical screening on A-share Universe rows.
- Added technical fields for availability, close, MA20, MA60, MA position, MA trend, RSI14, MACD signal, volume ratio, technical score, level, screening status, reasons, and warnings.
- Supports caller-provided price snapshots and price history dictionaries with safe missing-data handling.
- Added a read-only Technical Screening panel to the screening page.
- Added tests for empty Universe, missing price data, normal field generation, High/Pass output, weak output, RSI warning, MACD bearish downgrade, missing-field warnings, input immutability, row-order preservation, `fundamental_score` preservation, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, `fundamental_score`, fundamental modules, event modules, memory modules, default sorting, default filters, stock pools, backtest logic, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external services, machine learning, backtesting changes, target prices, operational trade points, or automated trading interfaces.

## v3.1.0

- Added Fundamental Screening Package in `screening/fundamental_screening.py`.
- Added `build_fundamental_screening()` for read-only fundamental screening on A-share Universe rows.
- Added fundamental fields for availability, ROE, revenue growth, profit growth, gross margin, debt ratio, operating cashflow, PE, PB, fundamental score, level, screening status, reasons, and warnings.
- Covers profitability, growth, valuation, financial risk, and cashflow quality with safe missing-data handling.
- Added a read-only Fundamental Screening panel to the screening page.
- Added tests for empty Universe, missing fundamental data, normal field generation, High/Pass output, weak output, missing-field warnings, input immutability, row-order preservation, old score preservation, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, event modules, memory modules, default sorting, default filters, stock pools, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, external services, machine learning, backtesting changes, or automated trading interfaces.

## v3.0.0

- Added A-Share Universe Engine in `universe/a_share_universe.py`.
- Added `build_a_share_universe()` with AkShare as the preferred source and safe empty DataFrame fallback when the source is unavailable.
- Added universe fields for ticker, name, market, list date, days since listing, ST flag, suspended flag, row status, universe status, total count, filtered count, and universe summary.
- Added default filters for ST, delisted securities, suspended securities, and listings with fewer than 250 days.
- Added a read-only A-Share Universe panel to the screening page showing total count, filtered count, filter rules, and Universe Summary.
- Added tests for empty data, single stock, ST filtering, suspended filtering, new-stock filtering, field completeness, and module import.
- Kept `core/scoring.py`, `strategy_score`, research priority, priority stability, event modules, memory modules, default sorting, default filters, stock pools, and trading logic unchanged.
- Did not add API keys, databases, vector stores, news sources, or external services.

## v2.2.0

- Added Research Journal Layer in `memory/research_journal.py`.
- Added Research Journal Schema with journal identity, ticker, name, period, status, summary, observations, risk notes, data quality notes, follow-up questions, Agent research tasks, and warnings.
- Converts one Research Snapshot plus one Research Timeline into human-readable and Agent-ready research notes.
- Extracts journal content from `snapshot_summary`, `priority_snapshot`, `event_snapshot`, `pipeline_snapshot`, `timeline_change_summary`, and `timeline_key_changes`.
- Keeps Agent tasks limited to research review, evidence validation, and pipeline conflict investigation.
- Added tests for empty input, snapshot-only incomplete output, available Snapshot+Timeline output, generated summary, observations, risk notes, follow-up questions, Agent tasks, input immutability, restricted-word cleanup, module import, and score-field preservation.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, and `core/scoring.py` unchanged.
- Did not add databases, vector stores, news sources, APIs, or external services.

## v2.1.0

- Added Research Timeline Layer in `memory/research_timeline.py`.
- Added Research Timeline Schema with timeline identity, ticker, name, snapshot count, start time, end time, status, direction, change summary, key changes, priority trend, event trend, pipeline trend, and warnings.
- Organizes same-object Research Snapshots by `snapshot_timestamp` for read-only change review.
- Compares priority, event, and pipeline snapshot sections without modifying Snapshot fields.
- Emits warnings for empty input, insufficient snapshots, missing timestamps, missing ticker, inconsistent ticker, and missing trend sections.
- Added tests for empty input, single-snapshot incomplete output, available multi-snapshot timelines, timestamp sorting, ticker warning, trend detection, direction judgment, input immutability, module import, and score-field preservation.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, and `core/scoring.py` unchanged.
- Did not add databases, vector stores, news sources, APIs, or external services.

## v2.0.0

- Added Research Memory Foundation in `memory/research_memory.py`.
- Added Research Snapshot Schema with snapshot identity, timestamp, ticker, name, version, stage, summary, and status.
- Added grouped snapshots for technical, fundamental, industry, composite, priority, event, pipeline, and project fields.
- Added tests for empty input, normal generation, missing fields, input immutability, fixed output order, status handling, module import, and score preservation.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, and `core/scoring.py` unchanged.
- Did not add databases, vector stores, news sources, APIs, or external services.

## v1.9.1

- Added Pre-v2 Project Assessment Layer in `strategy/project_assessment.py`.
- Added project assessment status, score, architecture note, field registry note, test coverage note, UI readability note, data source note, scoring boundary note, pre-v2 readiness level, blockers, and route fields.
- Added tests for empty input, single-row assessment, missing-field blockers or warnings, input immutability, stable ordering, score preservation, neutral wording, and module import.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, and `core/scoring.py` unchanged.

## v1.9.0

- Added Research Pipeline Validation Layer in `strategy/research_pipeline_audit.py`.
- Added `research_pipeline_status`, `research_pipeline_conflicts`, `research_pipeline_warnings`, and `research_pipeline_summary`.
- Added tests for empty input, missing fields, conflict detection, incomplete detection, healthy status, input immutability, stable ordering, module import, and score preservation.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, and `core/scoring.py` unchanged.

## v1.8.3

- Added Event Research Summary Layer in `strategy/event_research_summary.py`.
- Added event research summary, research level, key evidence, key risks, validation focus, Agent note, and summary warnings.
- Added tests for empty inputs, missing events, complete events, evidence points, risk points, validation focus, Agent note, immutability, stable ordering, score preservation, neutral wording, and module import.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, event confidence, event confluence, and `core/scoring.py` unchanged.

## v1.8.2

- Added Event Confluence Layer in `strategy/event_confluence.py`.
- Added event confluence label, score, summary, support points, conflict points, follow-up focus, and warnings.
- Added tests for empty inputs, missing events, high-quality events, low-quality warnings, support points, conflict points, immutability, stable ordering, score preservation, and neutral wording.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, event confidence, and `core/scoring.py` unchanged.

## v1.8.1

- Added Event Diagnostics Layer in `strategy/event_diagnostics.py`.
- Added event completeness, clarity, consistency, confidence, diagnostic level, summary, follow-up questions, evidence gaps, and quality warnings.
- Added tests for missing events, incomplete events, unreliable sources, immutability, stable ordering, score preservation, and neutral wording.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, priority stability, architecture audit, and `core/scoring.py` unchanged.

## v1.8.0

- Added Event Foundation Layer in `strategy/event_context.py`.
- Added event context fields.
- Added event availability, type, recency, source quality, reliability, context note, tags, and warnings.
- Added tests for empty input, missing events, immutability, stable ordering, score preservation, and neutral wording.
- Kept screening output, default sorting, stock pools, data sources, `strategy_score`, research priority, architecture audit, and `core/scoring.py` unchanged.

## v1.7.3

- Added Architecture Audit Layer in `strategy/architecture_audit.py`.
- Added `architecture_audit_label`, `architecture_audit_score`, `architecture_audit_note`, `architecture_audit_warnings`, `field_contract_warnings`, `module_contract_warnings`, and `boundary_contract_warnings`.
- Added tests for module presence, field contract, boundary preservation, neutral wording, immutability, and stable ordering.
- Kept screening output, default sorting, data sources, `strategy_score`, and `core/scoring.py` unchanged.

## v1.7.2

- Added Research Priority Stability Layer in `strategy/priority_stability.py`.
- Added `priority_stability_label`, `priority_stability_score`, `priority_stability_note`, `priority_drift_detected`, and `priority_drift_reason`.
- Added idempotence, input immutability, stable ordering, unavailable priority, score preservation, `core/scoring.py` boundary, and neutral wording tests.
- Kept priority stability separate from screening output, sorting, stock pools, data sources, `strategy_score`, and `core/scoring.py`.

## v1.7.1

- Added Research Priority Layer on top of composite profiles.
- Added `research_priority_score`, `research_priority_level`, `research_priority_reasons`, and `research_priority_warnings`.
- Kept research priority fields separate from screening output, default sorting, stock pools, data sources, `strategy_score`, and `core/scoring.py`.
- Expanded composite profile and preview tests for priority, downgrade, insufficient-data, and score preservation checks.

## v1.7.0

- Added Composite Profile Layer in `strategy/composite_profile.py`.
- Added composite research grade, style, level, risk, confidence, summary, strength points, risk points, follow-up focus, and data-quality note.
- Computed composite fields after technical, fundamental, industry-relative, diagnostic, and confluence fields.
- Kept composite fields preview-only and read-only.
- Added tests for empty/missing inputs, resonance, mismatches, high risk, data quality, immutability, list limits, and neutral wording.

## v1.6.9

- Added technical and fundamental confluence module in `strategy/confluence.py`.
- Added `confluence_label`, `confluence_score`, `confluence_summary`, `confluence_strength_points`, `confluence_risk_points`, and `confluence_followup_focus`.
- Kept confluence derived from existing read-only fields and separate from sorting and scoring.
- Added confluence tests for resonance, mismatch, risk, insufficient data, score bounds, immutability, and neutral wording.

## v1.6.3

- Added fundamental diagnostics module in `strategy/fundamental_diagnostics.py`.
- Added profitability, growth, valuation, financial-risk diagnostics, strength points, weakness points, watch points, and summary.
- Added later diagnostics fields including profile type, conflict flags, detail view, confidence, anomaly flags, research conclusion, research level, core strength, core risk, follow-up focus, and summary tags.
- Kept diagnostics read-only and separate from screening output, sorting, `strategy_score`, data sources, and `core/scoring.py`.
- Added tests for safe inputs, scoring explanations, industry-relative explanations, list limits, immutability, order preservation, and neutral wording.

## v1.6.2

- Added industry-relative fundamental comparison in `strategy/fundamental_relative.py`.
- Added relative profitability, growth, valuation, financial-risk, industry-relative quality label, and industry-relative summary.
- Compared candidates inside caller-provided industry or sector groups.
- Preserved input order and kept output read-only.
- Added tests for empty input, missing industry, small peer groups, peer comparison, multi-industry isolation, immutability, and neutral wording.

## v1.6.1

- Added read-only fundamental scoring fields.
- Added `profitability_score`, `growth_score`, `valuation_score`, `financial_risk_score`, `fundamental_quality_score`, `fundamental_grade`, `fundamental_style`, `fundamental_risk_level`, and `fundamental_reason`.
- Capped fundamental quality by data-quality label to avoid overconfident sparse-data output.
- Kept fundamental scores separate from screening output, sorting, `strategy_score`, stock pools, data sources, and `core/scoring.py`.
- Expanded tests for score generation, weak fundamentals, high-growth/high-valuation style, insufficient data, no-data certainty, and neutral wording.

## v1.6.0

- Added fundamental field standardization in `strategy/fundamental.py`.
- Added value normalization, field detection, missing-field checks, data-quality labels, and base summaries.
- Recognized canonical fields: revenue, net profit, gross margin, ROE, PE, PB, PS, debt ratio, operating cashflow, revenue growth, profit growth, market cap, and industry.
- Added `fundamental_available`, `fundamental_fields_detected`, `missing_fundamental_fields`, `fundamental_data_quality_label`, and `fundamental_summary_base`.
- Kept screening output, sorting, strategy scoring, stock pools, data sources, and `core/scoring.py` unchanged.

## v1.5.3

- Added compact technical research conclusions.
- Added `technical_grade`, `technical_style`, `technical_strength`, `technical_risk_level`, `technical_watch_points`, and `technical_summary_short`.
- Derived conclusions from technical labels while preserving original screening output, sorting, scoring rules, stock pools, data sources, and `core/scoring.py`.
- Expanded technical tests for grade, style, strength, risk level, watch points, weak structures, insufficient data, and neutral wording.

## v1.5.2

- Added technical structure preview module in `strategy/technical.py`.
- Added moving-average structure, trend quality, breakout/pullback state, volume-price structure, short-term overheat, volatility risk, and technical profile summary.
- Added fields: `ma_structure_label`, `trend_quality_label`, `breakout_pullback_label`, `volume_price_structure_label`, `short_term_overheat_label`, `volatility_risk_label`, and `technical_profile_summary`.
- Preserved input order and kept output preview-only.

## v1.5.1

- Added structured explanation fields for strategy preview output.
- Added `strategy_reason`, `trend_reason`, `momentum_reason`, `volume_price_reason`, `liquidity_reason`, `risk_reason`, `data_quality_reason`, `preset_reason`, and `confidence_note`.
- Kept explanations read-only and did not change screening output, sorting, scoring rules, stock pools, data sources, or `core/scoring.py`.

## v1.5.0

- Added optional strategy preview UI in `ui/screening_ui.py`.
- Added `build_screening_strategy_preview()` and `render_strategy_preview_section()`.
- Rendered a collapsed strategy preview section after the original screening workflow.
- Kept the original screening table, default sorting, scoring rules, stock pools, data sources, and `core/scoring.py` unchanged.
- Added UI integration tests for empty input, missing fields, immutability, default order preservation, preview-only sorting, required preview fields, safety wording, and legacy boundary.

## Update Rule

Every future version upgrade must update:

- `PROJECT_MASTER.md`
- `ROADMAP.md`
- `CHANGELOG.md`

If these files are not synchronized, the development process is incomplete.
