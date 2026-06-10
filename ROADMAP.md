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

Current: v5.1.0.

Goal: build shared universe, screening, scoring, and validation entry points before any machine learning layer.

- v3.0.0: A-Share Universe Engine completed.
- v3.1.0: Fundamental Screening completed.
- v3.2.0: Technical Screening completed.
- v3.3.0: Composite Quant Score Engine completed.
- v3.4.0: Candidate Pool Engine completed.
- v3.5.0: Backtest Foundation Engine completed.
- v3.6.0: Return Analysis Engine completed.
- v3.7.0: Backtest Evaluation Package completed.
- v3.8.0: Stock Selection System Package completed.
- v3.9.0: Explainable Selection Engine completed.
- v4.0.0: Web UI Report Experience completed.
- v4.1.0: Research Terminal UI Package completed.
- v4.2.0: Visual Research Terminal Redesign completed.
- v5.0.0: Research Workstation completed.
- v5.1.0: Chart Center completed.
- Next target: v5.2.0 Research Report Export Engine.
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

Completed v3.4.0 scope:

- Added `screening/candidate_pool.py`.
- Added `build_candidate_pool()` for read-only candidate-pool grouping from Composite Quant Score outputs.
- Added candidate fields for pool group, rank, level, status, reasons, risk flags, and warnings.
- Uses Core, Watch, Exclude, and Unavailable groups based on `composite_level`, `composite_screening_status`, and `composite_available`.
- Generates `candidate_rank` only inside Core/Watch based on `composite_score` descending while preserving input row order.
- Added a read-only Candidate Pool panel to the screening page without changing default sorting.
- Added tests for empty input, missing `composite_score`, Core grouping, Watch grouping, Exclude grouping, missing-field warnings, rank generation, rank order preservation, input immutability, `composite_score` preservation, `fundamental_score` preservation, `technical_score` preservation, and module import.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, `technical_score`, `composite_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, backtest logic, machine-learning logic, or trading logic.

Completed v3.5.0 scope:

- Added `backtest/backtest_engine.py`.
- Added `build_backtest_dataset()` for read-only backtest foundation dataset checks from Candidate Pool rows.
- Added backtest fields for availability, status, start date, end date, valid day count, price availability, and warnings.
- Supports caller-provided `price_history_dict` with `date` and `close` columns.
- Marks rows Available only when valid price history has at least 60 rows; otherwise marks Incomplete with warnings.
- Added a read-only Backtest Foundation panel to the screening page without changing default sorting.
- Added tests for empty input, missing price history, single stock, multiple stocks, shorter-than-60 histories, at-least-60 histories, date calculation, warning generation, input immutability, row-order preservation, no performance metric fields, and module import.
- Did not calculate returns, cumulative returns, annualized returns, Sharpe ratio, maximum drawdown, win rate, strategy optimization, parameter search, machine-learning predictions, automated trading actions, buy/sell suggestions, target prices, or position suggestions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, `technical_score`, `composite_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v3.6.0 scope:

- Added `backtest/return_analysis.py`.
- Added `build_return_analysis()` for read-only return analysis from Backtest Foundation rows and caller-provided price history.
- Added return-analysis fields for availability, status, holding-period days, entry price, exit price, period return, annualized return, volatility, maximum drawdown, win rate, summary, and warnings.
- Calculates metrics only when `backtest_available` is true and valid `date` plus `close` price history has at least 60 rows.
- Added a read-only Return Analysis panel to the screening page without changing default sorting.
- Added tests for empty input, missing price history, unavailable backtest foundation, single stock, multiple stocks, period return, annualized return, volatility, maximum drawdown, win rate, missing `close`, missing `date`, input immutability, row-order preservation, old score-field preservation, and module import.
- Did not add databases, vector stores, news sources, APIs, external services, machine learning, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v3.7.0 scope:

- Added `backtest/backtest_evaluation.py`.
- Added `build_backtest_evaluation()` for read-only backtest evaluation from Return Analysis rows.
- Added evaluation fields for availability, status, risk score, risk level, return-risk ratio, drawdown risk level, volatility risk level, performance label, performance summary, backtest quality label, and warnings.
- Evaluates only rows where `return_analysis_available` is true and required return-analysis fields are usable.
- Added a read-only Backtest Evaluation panel to the screening page without changing default sorting.
- Added tests for empty input, unavailable return analysis, single stock, multiple stocks, risk score, risk level, return-risk ratio, zero-drawdown warning, performance label, quality label, missing-field warnings, input immutability, row-order preservation, old score-field preservation, and module import.
- Did not add databases, vector stores, news sources, APIs, external services, machine learning, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, scoring-weight changes, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest Foundation modules, Return Analysis modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v3.8.0 scope:

- Added `selection/stock_selection.py`.
- Added `selection/__init__.py`.
- Added `build_stock_selection()` for read-only stock-selection research from Candidate Pool, Composite, Fundamental, Technical, and Backtest Evaluation fields already present in the input frame.
- Added selection fields for availability, score, level, status, bucket, rank, reasons, risk notes, quality label, and warnings.
- Uses transparent selection-layer weights: Composite Score 50%, Candidate Pool 20%, Backtest Evaluation 20%, and Risk Penalty 10%.
- Generates `selection_rank` from selection score without changing row order.
- Added a read-only Stock Selection System panel to the screening page without changing default sorting.
- Added tests for empty input, missing composite score, Core/high-score Selected output, Watch/medium-score Watch output, Exclude output, high-risk downgrade, poor-backtest-quality downgrade, rank generation, rank order preservation, reasons, risk notes, warnings, input immutability, `composite_score` preservation, `candidate_rank` preservation, and module import.
- Did not add databases, vector stores, news sources, APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, upstream scoring-weight changes, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v3.9.0 scope:

- Added `selection/explain_engine.py`.
- Added `build_explainable_selection()` for read-only explanation of Stock Selection rows.
- Added explanation fields for availability, status, thesis, strengths, risks, factor breakdown, reason score, natural-language explanation, summary, and warnings.
- Detects strengths from fundamental, technical, composite, and historical performance fields.
- Detects risks from high risk level, large drawdown, high volatility, and weak historical performance.
- Added a read-only Explainable Selection panel to the screening page without changing default sorting.
- Added tests for Core, Watch, Exclude, missing data, unavailable selection, risk detection, factor breakdown, explanation generation, summary generation, row-order preservation, upstream score preservation, empty input, and module import.
- Did not add databases, vector stores, news sources, APIs, external services, machine learning, buy/sell points, target prices, position suggestions, strategy optimization, parameter search, automated trading workflows, scoring changes, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `architecture_audit_score`, `event_confidence_score`, `event_confluence_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Candidate Pool modules, Backtest modules, Return Analysis modules, Backtest Evaluation modules, Stock Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v4.0.0 scope:

- Added `ui/report_ui.py`.
- Added a read-only Web UI Report Experience for existing research outputs.
- Added report overview metrics for version, stage, research-object count, Core/Watch/Exclude counts, and explainable-result count.
- Added candidate overview, stock research cards, score breakdown, backtest performance, risk notes, and data-quality report sections.
- Added list and dict formatting helpers for Streamlit display.
- Added warning aggregation across warning fields plus Incomplete and Unavailable statuses.
- Integrated the report section into `ui/screening_ui.py` after Explainable Selection without changing default sorting.
- Added tests for module import, empty DataFrame handling, missing selection/explain fields, list/dict formatting, warning aggregation, input immutability, and `app.py` import.
- Did not add selection algorithms, scoring changes, APIs, databases, vector stores, news sources, external services, machine learning, buy/sell points, target prices, position suggestions, automated trading workflows, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v4.1.0 scope:

- Added `ui/terminal_ui.py`.
- Added `ui/terminal_components.py`.
- Added `ui/report_builder.py`.
- Added Research Terminal UI Package for read-only terminal-style review of existing research outputs.
- Added Research Dashboard metrics for total research objects, Core/Watch/Exclude counts, average `selection_score`, average `composite_score`, high-risk objects, and incomplete-data objects.
- Added Top Picks cards for Core/Watch objects with ticker, name, rank, score, bucket, thesis, summary, strengths, and risks.
- Added Stock Detail Panel with basic information, score breakdown, explanation fields, backtest panel, risk notes, and data-quality notes.
- Added Risk Center groups for High Risk, High Drawdown, High Volatility, Missing Data, and Unavailable objects.
- Added Compare Panel for 2-5 objects across selection, composite, fundamental, technical, return, drawdown, volatility, risk, and performance fields.
- Added Research Report Preview for a single object using neutral research-only text.
- Integrated the terminal section into `ui/screening_ui.py` after Web UI Report Experience without changing default sorting.
- Added tests for module import, empty DataFrame handling, missing selection fields, missing explain fields, list formatting, dict formatting, warning aggregation, report text generation, restricted report wording checks, input immutability, and `app.py` import.
- Did not add selection algorithms, scoring changes, APIs, databases, vector stores, news sources, external services, machine learning, buy/sell points, target prices, position suggestions, automated trading workflows, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v4.2.0 scope:

- Added `ui/visual_theme.py`.
- Added `ui/visual_components.py`.
- Redesigned the Research Terminal into a visual terminal interface with shared CSS, terminal header, section titles, badges, metric cards, stock cards, score bars, warning boxes, report blocks, and formatted comparison tables.
- Updated `ui/terminal_ui.py` to use the visual theme and component layer while preserving existing public rendering functions.
- Updated `ui/terminal_components.py` for clearer Chinese labels, missing-value display, comparison formatting, and `selection_thesis` comparison support.
- Updated `ui/report_builder.py` with a readable numbered research report structure and neutral wording cleanup.
- Updated `app.py` and `legacy_app.py` version metadata to v4.2.0.
- Added tests for visual theme imports, visual component imports, CSS generation, badge handling, list formatting, dict formatting, warning aggregation, empty DataFrame handling, missing selection fields, missing explanation fields, restricted report wording, input immutability, and `app.py` import.
- Did not add selection algorithms, scoring changes, APIs, databases, vector stores, news sources, external services, machine learning, buy/sell points, target prices, position suggestions, automated trading workflows, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v5.0.0 scope:

- Added `ui/workstation_ui.py`.
- Added `ui/workstation_components.py`.
- Added `ui/workstation_theme.py`.
- Added Research Workstation layout with sticky header, left Research Navigator, central Research Area, right Thesis Panel, and full-width Risk & Score Analysis sections.
- Added CORE/WATCH/EXCLUDED navigator grouping from `selection_bucket` with button-based object switching.
- Added Dashboard Cards for Average Score, Core Candidates, Average Return, and Average Risk Score.
- Added main research area for object identity, score, rank, bucket, quality label, status badge, risk badge, thesis, strengths, risks, and five-part factor breakdown.
- Added Score Breakdown Center, Risk Center, Backtest Center, Compare Workspace, Research Pipeline, and Research Report Preview.
- Integrated Research Workstation into `ui/screening_ui.py` after the existing Research Terminal without changing default sorting.
- Updated `app.py` and `legacy_app.py` version metadata to v5.0.0.
- Added tests for Workstation import, safe field access, navigator grouping, dashboard metrics, missing explain fields, missing risk fields, compare generation, report preview generation, empty DataFrame rendering, input immutability, and `app.py` import.
- Did not add selection algorithms, scoring changes, APIs, databases, vector stores, news sources, external services, machine learning, buy/sell points, target prices, position suggestions, automated trading workflows, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

Completed v5.1.0 scope:

- Added `ui/chart_center.py`.
- Added `ui/chart_components.py`.
- Added Chart Center inside Research Workstation for read-only visual research review.
- Added Score Radar / Score Profile for `fundamental_score`, `technical_score`, `composite_score`, `selection_score`, and `risk_score`.
- Added Return-Risk Scatter using `volatility` or `risk_score` against `period_return` or `annualized_return`.
- Added Drawdown-Risk View for `max_drawdown`, `volatility`, and `risk_level`.
- Added Score Breakdown Bar for single-object score decomposition.
- Added Candidate Ranking Bar for Top N `selection_score` ranking without changing default sorting.
- Added Quality Distribution for Core/Watch/Exclude and High/Medium/Low group review.
- Integrated Chart Center into `ui/workstation_ui.py`.
- Updated `app.py` and `legacy_app.py` version metadata to v5.1.0.
- Added tests for Chart Center imports, empty DataFrame handling, missing score fields, missing return fields, safe numeric conversion, chart DataFrame immutability, ranking data generation, scatter data generation, score profile handling, and `app.py` import.
- Did not add selection algorithms, scoring changes, APIs, databases, vector stores, news sources, external services, machine learning, buy/sell points, target prices, position suggestions, automated trading workflows, return promises, or operational conclusions.
- Did not modify `core/scoring.py`, `strategy_score`, `research_priority_score`, `priority_stability_score`, `fundamental_score`, `technical_score`, `composite_score`, `candidate_rank`, `selection_score`, Universe modules, Fundamental modules, Technical modules, Composite modules, Candidate Pool modules, Backtest modules, Stock Selection modules, Explainable Selection modules, Event modules, Memory modules, default sorting, default filters, stock pools, data sources, machine-learning logic, or trading logic.

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
