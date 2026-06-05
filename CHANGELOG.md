# Fin-Scientist Changelog

> Permanent changelog for the project memory system. All entries describe learning and research features only and do not constitute investment advice.

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
