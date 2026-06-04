# FinScientist

## Current Version

Current version: V2.0.0

V2.0.0 adds the Research Memory Foundation. The project now defines a read-only Research Snapshot schema for organizing preview results into grouped memory sections without adding a database, vector store, external service, data source, scoring change, or sorting change.

Startup command remains:

```bash
streamlit run app.py
```

### Project Structure

```text
config/    Stock pools, stock names, sector labels, built-in fundamental samples
data/      Market data and fundamental data access boundaries
core/      Metrics, scoring, explanations, and sector-strength helpers
strategy/  Independent strategy comparison, scoring, view-model, service, reports, diagnostics, factors, filters, risk labels, and presets
ui/        Streamlit page entrypoints and screening page rendering
app.py     Main Streamlit entrypoint and page navigation
legacy_app.py  Compatibility layer / legacy core logic carrier
```

`legacy_app.py` is not an unused backup. In V2.0.0 it remains the explicit compatibility layer for the old research workbench, the legacy screening renderer, and network-adjacent fetch orchestration that has not yet been migrated. Strategy preview rendering lives in `ui/screening_ui.py`; `legacy_app.py` does not import strategy modules in this release.

FinScientist V2.0.0 是一个模块化 Streamlit 金融研究学习原型。后续项目方向以 A股研究为主，兼容港股和美股。当前提供单股票分析、技术指标、基本面字段、板块观察、新闻/事件分析、多对象对比、临时观察列表、简单策略回测、数据源可靠性与数据质量报告，以及自动研究对象筛选模块。

当前版本不调用 OpenAI API，不使用数据库，不执行真实交易操作。所有结果仅用于学习演示，不构成投资建议。

## 项目定位

FinScientist 是学习与研究工具，用于演示多市场行情分析、技术指标、规则化摘要、多股票对比、自选股观察和简单策略回测。它不是正式投研系统，不连接真实交易账户，不提供真实交易操作功能，任何页面输出都不构成投资建议。

## 当前版本

当前版本：V2.0.0

V2.0.0 research memory foundation phase:

- Added `memory/research_memory.py` for read-only Research Snapshot schema generation.
- Added snapshot identity fields and grouped technical, fundamental, industry, composite, priority, event, pipeline, and project snapshot sections.
- This phase does not add a database, vector store, machine learning, Agent workflow, external service, data source, scoring change, or sorting change.

V1.9.1 pre-v2 project assessment phase:

- Added `strategy/project_assessment.py` for read-only project readiness assessment before v2.0.
- Added project assessment status, score, architecture, field registry, test coverage, UI readability, data source, scoring boundary, readiness, blocker, and route fields.
- Project assessment fields are preview-only and do not change screening, sorting, stock pools, data sources, `strategy_score`, research priority fields, priority stability fields, architecture audit fields, event confidence fields, event confluence fields, or `core/scoring.py`.

V1.9.0 research pipeline validation phase:

- Added `strategy/research_pipeline_audit.py` for read-only end-to-end research pipeline validation.
- Added research pipeline status, conflicts, warnings, and summary.
- Pipeline audit fields are preview-only and do not change screening, sorting, stock pools, data sources, `strategy_score`, research priority fields, priority stability fields, architecture audit fields, event confidence fields, event confluence fields, or `core/scoring.py`.

V1.8.3 event research summary phase:

- Added `strategy/event_research_summary.py` for read-only Agent-ready event research notes.
- Added event research summary, research level, key evidence, key risks, validation focus, Agent note, and summary warnings.
- Event research summary fields are preview-only and do not change screening, sorting, stock pools, data sources, `strategy_score`, research priority fields, priority stability fields, architecture audit fields, event confidence fields, event confluence fields, or `core/scoring.py`.

V1.8.2 event confluence phase:

- Added `strategy/event_confluence.py` for read-only event-to-research-profile confluence review.
- Added event confluence label, score, summary, support points, conflict points, follow-up focus, and warnings.
- Event confluence fields are preview-only and do not change screening, sorting, stock pools, data sources, `strategy_score`, research priority fields, priority stability fields, architecture audit fields, event confidence fields, or `core/scoring.py`.

V1.8.1 event diagnostics phase:

- Added `strategy/event_diagnostics.py` for read-only event evidence quality diagnostics.
- Added event completeness, clarity, consistency, confidence, diagnostic level, summary, follow-up questions, evidence gaps, and quality warnings.
- Event diagnostics fields are preview-only and do not change screening, sorting, stock pools, data sources, `strategy_score`, research priority fields, priority stability fields, architecture audit fields, or `core/scoring.py`.

V1.8.0 event foundation phase:

- Added `strategy/event_context.py` for read-only event field standardization.
- Added event availability, type, recency, source quality, reliability, context note, research tags, and warnings.
- Event context fields are preview-only and do not change screening, sorting, stock pools, data sources, `strategy_score`, research priority fields, architecture audit fields, or `core/scoring.py`.

V1.7.3 architecture audit phase:

- Added `strategy/architecture_audit.py` for read-only module, field, boundary, and contract diagnostics.
- Added `architecture_audit_label`, `architecture_audit_score`, `architecture_audit_note`, `architecture_audit_warnings`, `field_contract_warnings`, `module_contract_warnings`, and `boundary_contract_warnings`.
- Architecture audit diagnostics do not change screening, sorting, `strategy_score`, `research_priority_score`, `priority_stability_score`, or `core/scoring.py`.

V1.7.2 research priority stability phase:

- Added `strategy/priority_stability.py` for read-only priority stability and drift diagnostics.
- Added `priority_stability_label`, `priority_stability_score`, `priority_stability_note`, `priority_drift_detected`, and `priority_drift_reason`.
- Stability diagnostics read existing priority fields only and do not change screening, sorting, `strategy_score`, or `core/scoring.py`.

V1.7.1 research priority experiment phase:

- Added read-only `derive_research_priority(profile)` in `strategy/composite_profile.py`.
- Added `research_priority_score`, `research_priority_level`, `research_priority_reasons`, and `research_priority_warnings`.
- Research priority fields are preview-only and do not change screening, sorting, `strategy_score`, or `core/scoring.py`.

V1.7.0 composite research profile phase:

- Added `strategy/composite_profile.py` for read-only composite research profiles.
- Added `composite_research_grade`, `composite_research_style`, `composite_research_level`, `composite_risk_level`, `composite_confidence_level`, `composite_summary`, `composite_strength_points`, `composite_risk_points`, `composite_followup_focus`, and `composite_data_quality_note`.
- Composite profiles combine existing preview fields only and do not change screening, sorting, `strategy_score`, or `core/scoring.py`.
- The screening page shows these fields only inside the existing strategy preview expander.

V1.6.9 technical and fundamental confluence phase:

- Added `strategy/confluence.py` for read-only confluence analysis between technical preview fields and fundamental diagnostics fields.
- Added `confluence_label`, `confluence_score`, `confluence_summary`, `confluence_strength_points`, `confluence_risk_points`, and `confluence_followup_focus`.
- Confluence labels are research-only observations and are not connected to screening, sorting, `strategy_score`, or `core/scoring.py`.
- This phase does not add data sources, stock-pool changes, export flows, or operation-oriented language.

V1.6.3 fundamental diagnostics phase:

- Added `strategy/fundamental_diagnostics.py` for read-only field-level explanations behind the fundamental preview scores.
- Added `fundamental_diagnostics`, `profitability_diagnostics`, `growth_diagnostics`, `valuation_diagnostics`, `financial_risk_diagnostics`, `fundamental_watch_points`, `fundamental_strength_points`, `fundamental_weakness_points`, and `fundamental_diagnostics_summary`.
- Diagnostics combine caller-provided fundamental fields, V1.6.1 fundamental scores, and V1.6.2 industry-relative labels.
- Strength, weakness, and watch-point lists are capped at three items each and preserve neutral research wording.
- This phase does not change screening results, default sorting, stock pools, data sources, `strategy_score`, or `core/scoring.py`.

V1.6.2 industry-relative fundamental comparison phase:

- Added `strategy/fundamental_relative.py` for read-only industry and sector relative fundamental comparison in strategy preview.
- Added `relative_profitability_label`, `relative_growth_label`, `relative_valuation_label`, `relative_financial_risk_label`, `industry_relative_quality_label`, and `industry_relative_summary`.
- Industry grouping uses `industry`, `industry_name`, `sector`, `板块`, `行业`, and existing encoded aliases when available.
- Relative labels are computed only inside the caller-provided candidate pool and preserve input order.
- This phase does not change screening results, default sorting, stock pools, data sources, `strategy_score`, or `core/scoring.py`.

V1.6.1 fundamental quality scoring phase:

- Added `profitability_score`, `growth_score`, `valuation_score`, `financial_risk_score`, `fundamental_quality_score`, `fundamental_grade`, `fundamental_style`, `fundamental_risk_level`, and `fundamental_reason`.
- Scores are read-only research observations derived from standardized caller-provided fields; they are not connected to screening, sorting, `strategy_score`, or `core/scoring.py`.
- `fundamental_quality_score` is capped by fundamental data quality so sparse data cannot produce overconfident results.
- This phase keeps all outputs neutral and only supports research preview analysis.

V1.6.0 fundamental field standardization phase:

- Added `strategy/fundamental.py` for read-only fundamental field detection, value normalization, missing-field checks, quality labeling, and base summaries.
- Recognized fields include revenue, net profit, gross margin, ROE, PE, PB, PS, debt ratio, operating cashflow, revenue growth, profit growth, market cap, and industry.
- Chinese aliases such as `营业收入`, `净利润`, `毛利率`, `净资产收益率`, `市盈率`, `市净率`, `市销率`, `资产负债率`, `经营现金流`, `营收增长率`, `净利润增长率`, `总市值`, and `行业` are supported.
- Added preview fields: `fundamental_available`, `fundamental_fields_detected`, `missing_fundamental_fields`, `fundamental_data_quality_label`, and `fundamental_summary_base`.
- This phase does not create a final fundamental score and does not change screening results, default sorting, stock pools, data sources, `strategy_score`, or `core/scoring.py`.

V1.5.3 technical research conclusion phase:

- Added `technical_grade`, `technical_style`, `technical_strength`, `technical_risk_level`, `technical_watch_points`, and `technical_summary_short`.
- Technical conclusions are derived from the V1.5.2 technical labels only: moving-average structure, trend quality, breakout/pullback state, volume-price structure, short-term overheat, and volatility risk.
- `technical_grade` uses A/B/C/D research levels; A requires stronger trend structure and volume-price confirmation without severe overheat, while D is used for weak, high-risk, or heavily data-limited structures.
- The screening page shows the compact conclusion fields in the existing collapsed preview expander.
- No real data source, network download, stock-pool change, sorting change, research-priority score change, or `core/scoring.py` change was introduced.

V1.5.2 technical structure preview phase:

- Added `strategy/technical.py` for read-only row-level technical structure analysis.
- Added preview fields: `ma_structure_label`, `trend_quality_label`, `breakout_pullback_label`, `volume_price_structure_label`, `short_term_overheat_label`, `volatility_risk_label`, and `technical_profile_summary`.
- Technical labels use only existing row fields and existing strategy preview fields; no real data source, network download, stock-pool change, sorting change, research-priority score change, or `core/scoring.py` change was introduced.
- The screening page keeps the strategy preview inside the collapsed expander and shows core technical labels in that preview table.
- Technical explanations are for research-priority observation only and are not operation instructions.

V1.5.1 strategy preview explanation phase:

- Added `strategy_reason`, `trend_reason`, `momentum_reason`, `volume_price_reason`, `liquidity_reason`, `risk_reason`, `data_quality_reason`, `preset_reason`, and `confidence_note`.
- `strategy_reason` summarizes the dominant style, strongest score components, risk penalty, and data-quality penalty.
- Factor explanations use only existing preview/scoring fields and caller-provided row fields; no new real data source, network download, stock-pool change, sorting change, research-priority score change, or `core/scoring.py` change was introduced.
- The screening page keeps the preview in a collapsed expander and displays core explanation columns without changing the original result table.
- Explanations are for research-priority observation only and do not provide operation instructions.

V1.5.0 optional strategy preview UI phase:

- Added a collapsed strategy preview section after the screening result table.
- The preview calls `build_strategy_preview(..., sort_by_strategy=False)` by default.
- Displayed fields include symbol, name, original score, strategy score, best preset, dominant style, consensus level, per-preset scores, risk labels, data-quality labels, and warnings.
- Optional preview sorting affects only the preview table and does not change the original screening table.
- `legacy_app.py` returns the already-built screening result DataFrame but does not import strategy logic.
- No network calls, downloads, real data-source access, stock-pool changes, default sorting changes, original research-priority score changes, or `core/scoring.py` changes were introduced.

V1.4.16 internal strategy preview/export phase:

- Added `strategy/preview.py`.
- Added `build_strategy_preview()` and `build_strategy_preview_row()` for caller-provided candidate pools.
- Preview output includes default `balanced_research` strategy score, cross-preset comparison fields, per-preset scores, dominant style, consensus level, risk labels, data-quality labels, and warnings.
- Added `export_strategy_preview_to_json_like()` and `export_strategy_preview_to_csv()`.
- The preview keeps input order by default; optional strategy sorting affects only the preview output.
- No network calls, downloads, real data-source access, default UI integration, stock-pool changes, existing screening-order changes, default `strategy_score` logic changes, or `core/scoring.py` changes were introduced.

V1.4.15 internal backtest diagnostics phase:

- Added `strategy/backtest_diagnostics.py`.
- Added `validate_backtest_metrics_schema()` for backtest metrics summary schema checks.
- Added score-bucket, preset, dominant-style, and consensus-level diagnostics.
- Added `build_backtest_diagnostics_report()` with schema status, missing fields, data-quality warnings, neutral diagnostics, summary text, and read-only metadata.
- Diagnostics are internal research observations only and do not produce operation instructions.
- No network calls, downloads, real data-source access, UI integration, stock-pool changes, sorting changes, default `strategy_score` logic changes, or `core/scoring.py` changes were introduced.

V1.4.14 internal backtest metric aggregation phase:

- Added `bucket_strategy_score()` with `high_score`, `mid_score`, `low_score`, and `insufficient_score` buckets.
- Added metric summaries by `preset_name`, score bucket, `dominant_style`, and `consensus_level`.
- Added `build_backtest_metrics_summary()` with total/valid/insufficient counts, outcome distributions, forward-return averages, and average forward drawdown.
- Aggregation accepts caller-provided lists or DataFrames and does not mutate inputs.
- No network calls, downloads, real data-source access, UI integration, stock-pool changes, sorting changes, default `strategy_score` logic changes, or `core/scoring.py` changes were introduced.

V1.4.13 internal backtest sample helper phase:

- Added `strategy/backtest.py`.
- Added `validate_backtest_input()` for required-field and forward-price validation.
- Added `calculate_forward_return()` for 1/3/5/10 day forward-return calculations from caller-provided prices.
- Added `classify_backtest_outcome()` with labels: `positive_follow_through`, `weak_follow_through`, `failed_follow_through`, `high_drawdown_risk`, and `insufficient_data`.
- Added `build_backtest_sample()` and `summarize_backtest_samples()` for internal research-validation samples.
- No network calls, downloads, real data-source access, UI integration, stock-pool changes, or `core/scoring.py` changes were introduced.
- V1.4.4-V1.4.12 drift-check thresholds did not need adjustment.

V1.4.12 internal strategy snapshot export phase:

- Added `strategy/export.py`.
- Added `export_preset_comparison_snapshot()` for single-candidate preset comparison snapshots.
- Added `export_preset_pool_summary_snapshot()` for candidate-pool preset summary snapshots.
- Added `build_strategy_snapshot_payload()` to combine optional comparison and pool summary snapshots with stable metadata.
- Snapshot outputs include `schema_version`, `snapshot_type`, preserved warnings, merged metadata, and stable JSON-like dictionaries.
- V1.4.4-V1.4.11 drift-check thresholds did not need adjustment.
- The changes remain internal only and do not change `strategy_score` default logic, UI, sorting, existing screening output, stock pools, data sources, or `core/scoring.py`.

V1.4.11 candidate-pool preset summary phase:

- Added `summarize_preset_comparison_pool()` in `strategy/preset_comparison.py`.
- The helper runs `compare_strategy_presets()` row by row for an internal candidate pool and preserves input order.
- Summary output includes total/valid counts, insufficient-data count, dominant-style counts and ratios, consensus-level counts and ratios, average scores by preset, average score spread, max score spread, summary text, and warnings.
- Shortcut counts are provided for `broad_consensus_high`, `style_specific_high`, `mixed_signal`, and `broad_consensus_low`.
- V1.4.4-V1.4.10 drift-check thresholds did not need adjustment.
- The changes remain internal only and do not change `strategy_score` default logic, UI, sorting, existing screening output, stock pools, data sources, or `core/scoring.py`.

V1.4.10 cross-preset comparison phase:

- Added `strategy/preset_comparison.py` with `compare_strategy_presets()` and `summarize_preset_scores()`.
- Comparison output includes `preset_scores`, `best_preset`, `worst_preset`, `score_spread`, `average_preset_score`, `consensus_level`, `dominant_style`, `style_notes`, and `warnings`.
- `consensus_level` can be `broad_consensus_high`, `style_specific_high`, `mixed_signal`, `broad_consensus_low`, or `insufficient_data`.
- `dominant_style` can be `balanced`, `trend_momentum`, `volume_breakout`, `low_risk_quality`, `high_elasticity`, `mixed`, or `insufficient_data`.
- V1.4.4-V1.4.9 drift-check thresholds did not need adjustment.
- The changes remain internal only and do not change `strategy_score` default logic, UI, sorting, existing screening output, stock pools, data sources, or `core/scoring.py`.

V1.4.9 multi-preset strategy scoring phase:

- Added strategy presets: `balanced_research`, `trend_momentum`, `volume_breakout`, `low_risk_quality`, and `high_elasticity_watch`.
- `calculate_strategy_scores()` now accepts `preset_name` or `preset_config` and returns `preset_name`, `preset_display_name`, and `strategy_score_components`.
- Default `balanced_research` preserves the v1.4.8 scoring weights: trend 0.30, momentum 0.25, volume-price 0.20, liquidity 0.15, baseline 0.10.
- `trend_momentum` emphasizes trend and momentum; `volume_breakout` emphasizes volume-price and liquidity; `low_risk_quality` emphasizes liquidity, risk, and data quality; `high_elasticity_watch` allows elasticity only with volume and liquidity support.
- Legacy preset keys remain available for adapter compatibility.
- V1.4.4-V1.4.8 drift-check thresholds did not need adjustment.
- The changes remain internal only and do not change UI, sorting, existing screening output, stock pools, data sources, or `core/scoring.py`.

V1.4.8 internal risk and data-quality explanation phase:

- Added `strategy/explanations.py` for read-only internal explanations based on strategy score rows or scoring result dictionaries.
- Converts risk labels such as `high_volatility`, `extreme_upside_return`, `volume_downside_risk`, `overheated_turnover`, and `low_liquidity` into structured risk explanations.
- Converts data-quality labels such as `missing_price_fields`, `missing_volume_fields`, `missing_turnover_fields`, `invalid_numeric_fields`, and `insufficient_factor_data` into structured data-quality explanations.
- Adds `penalty_breakdown`, `factor_notes`, `summary_text`, and `warnings` for audit-style review.
- V1.4.4-V1.4.7 drift-check thresholds did not need adjustment.
- The changes remain internal only and do not change `strategy_score`, UI, sorting, existing screening output, stock pools, data sources, or `core/scoring.py`.

V1.4.7 risk and data-quality penalty enhancement phase:

- Enhanced `strategy/risk.py` with stable risk codes for high volatility, extreme upside return, volume downside risk, overheated turnover, low liquidity, and insufficient factor data.
- `strategy/scoring.py` now outputs internal `risk_labels` and `data_quality_labels` alongside existing score components.
- Risk penalty now distinguishes high volatility or amplitude, extreme short-term return, volume-supported downside moves, overheated turnover, and confirmed low liquidity.
- Data-quality penalty now labels missing price, volume, turnover, moving-average factor data, and invalid numeric values while keeping fixed-sample drift ranges stable.
- V1.4.4/V1.4.5/V1.4.6 drift-check thresholds did not need adjustment.
- The changes remain internal only and do not change UI, sorting, existing screening output, stock pools, data sources, or `core/scoring.py`.

V1.4.6 volume-price and liquidity factor enhancement phase:

- Enhanced `strategy/factors.py` amount, volume-ratio, turnover, volume-price, and liquidity observations.
- Added volume-price and liquidity labels: `volume_price_confirmed`, `volume_price_weak`, `low_liquidity`, `overheated_turnover`, and `volume_downside_risk`.
- `strategy/scoring.py` now separates `volume_price_score` and `liquidity_score` more clearly while preserving the existing component weights and 0-100 bounds.
- Low amount and low turnover reduce liquidity score; volume-supported positive trend can raise volume-price score; volume-supported downside and overheated turnover increase risk penalty.
- Added alias support for `turnover_rate` and `量比`, plus non-finite value handling for extreme inputs.
- V1.4.4 drift-check thresholds did not need adjustment.
- The changes remain internal only and do not change UI, sorting, existing screening output, stock pools, data sources, or `core/scoring.py`.

V1.4.5 trend and momentum factor enhancement phase:

- Added moving-average position and momentum-profile helpers in `strategy/factors.py`.
- Enhanced trend factor details with `trend_direction_label` and trend quality observations.
- Enhanced momentum factor details with `momentum_label`, consecutive-up count, and consecutive-down count.
- Adjusted internal `strategy/scoring.py` trend and momentum sub-scores using 5/10/20-day return fields where available.
- Overheated momentum now increases risk penalty and does not receive unlimited score uplift.
- V1.4.4 drift-check thresholds did not need adjustment.

V1.4.4 strategy drift-check phase:

- Added fixed-sample drift checks for internal `strategy_score` ranges.
- Added drift checks for alignment labels and aggregate comparison summary metrics.
- Fixed samples cover high-quality trend, low-liquidity, overheated-risk, missing-data, neutral, strategy-strong research-weak, and research-strong strategy-weak cases.
- No scoring or summary logic was changed in this release.
- Checks remain internal and do not change UI, sorting, or existing scores.

V1.4.3 aggregate comparison summary phase:

- Added `summarize_score_alignment()` to `strategy/comparison.py`.
- Summary output includes total count, valid count, missing score counts, average scores, average gap, alignment counts, alignment ratios, summary text, and warnings.
- Summary input can be a score DataFrame, `compare_strategy_scores()` output, or a comparison list.
- Summaries are internal only and do not change UI, sorting, or existing scores.

V1.4.2 internal score comparison phase:

- Added `strategy/comparison.py` for internal comparison between existing research-priority scores and `strategy_score`.
- Comparison output includes original score, strategy score, score gap, alignment label, interpretation, research-priority type, and warnings.
- Alignment labels include `high_consensus`, `research_high_strategy_low`, `strategy_high_research_low`, `low_consensus`, and `insufficient_data`.
- Comparison is read-only, preserves input order, and is not connected to UI or existing sorting.

V1.4.1 strategy score calibration phase:

- Added calibration tests for high-quality trend, low-liquidity, overheated-risk, missing-data, and neutral samples.
- Added score-distribution tests to keep internal strategy scores in 0-100 and preserve input row order.
- Refined internal liquidity scoring to use source amount and volume fields when a DataFrame is provided.
- Strategy scores remain internal research-priority auxiliary scores and are not connected to UI or existing sorting.

V1.4.0 independent strategy scoring phase:

- Added `strategy/scoring.py` as an internal strategy-score system.
- Strategy score output includes `trend_score`, `momentum_score`, `volume_price_score`, `liquidity_score`, `risk_penalty`, `data_quality_penalty`, and `strategy_score`.
- Enhanced `strategy/factors.py` with trend direction, volume-price, and data-quality factor helpers.
- The score range is 0-100 and is only a research-priority auxiliary score.
- Existing `core/scoring.py`, existing screening output, page display, and sorting logic are unchanged.

V1.3.6 gated diagnostics panel helper phase:

- Added `ui/strategy_diagnostics_panel.py` as a feature-flagged helper for future strategy diagnostics display.
- The helper returns without rendering when `is_strategy_diagnostics_enabled()` is `False`.
- The feature flag remains disabled by default.
- Current Streamlit pages do not call the helper.
- No strategy diagnostics are rendered in Streamlit in this release.

V1.3.5 feature-flag boundary phase:

- Added `config/feature_flags.py` for future strategy diagnostics display boundaries.
- Strategy diagnostics display is disabled by default.
- Feature-flag metadata returns `strategy_diagnostics_enabled: False`, `ui_rendering_enabled: False`, `ranking_changed: False`, `scoring_changed: False`, and `read_only: True`.
- Added non-rendering UI contract tests that ensure `ui/screening_ui.py` and `legacy_app.py` do not depend on strategy view-model or service code.
- No strategy diagnostics are rendered in Streamlit in this release.

V1.3.4 strategy view-model phase:

- Added `strategy/view_model.py` as a read-only conversion layer from strategy service output to future UI-friendly structures.
- View-model output includes `cards`, `badges`, `sections`, `table_rows`, `empty_state`, and `metadata`.
- Metadata records read-only status and confirms that UI, ranking, and scoring are not changed.
- The view-model is not connected to UI, existing screening output, scoring rules, page display, or sorting logic.

V1.3.3 strategy service phase:

- Added `strategy/service.py` as a read-only internal service that combines `strategy.adapter` and `strategy.report`.
- Service input is an existing screening-result DataFrame.
- Service output includes `status`, `preset_name`, `diagnostics`, `report`, `metadata`, and `warnings`.
- Metadata records read-only status and confirms that UI, ranking, and scoring are not changed.
- The service is not connected to UI, existing screening output, scoring rules, page display, or sorting logic.

V1.3.2 strategy report phase:

- Added `strategy/report.py` as a read-only internal report builder based on `strategy.adapter` output.
- Report output includes `preset_name`, `summary_text`, `factor_summary`, `filter_summary`, `risk_summary`, `data_quality_summary`, and `notes`.
- Report text summarizes factor observations, filter flags, risk labels, data-quality hints, and research-priority context.
- Empty diagnostics, missing fields, and abnormal structures return safe summaries.
- The report builder is not connected to UI, existing screening output, scoring rules, page display, or sorting logic.

V1.3.1 strategy adapter phase:

- Added `strategy/adapter.py` as a read-only conversion layer from existing screening-result DataFrames to strategy diagnostics.
- Adapter field mapping recognizes common aliases such as `close` / `price` / `最新价`, `pct_chg` / `change_pct` / `涨跌幅`, `volume` / `成交量`, `amount` / `成交额`, `turnover` / `换手率`, and `sector` / `industry` / `板块`.
- Adapter output includes `factor_scores`, `filter_flags`, `risk_tags`, `risk_notes`, `preset_name`, and `diagnostics_summary`.
- Empty inputs, missing fields, and abnormal fields return safe diagnostics without modifying the input DataFrame.
- The adapter is not connected to UI, existing screening output, scoring rules, page display, or sorting logic.

V1.3.0 strategy framework phase 1:

- Added `strategy/factors.py` for pure trend, momentum, volatility, and volume factor helpers.
- Added `strategy/filters.py` for pure preprocessing checks such as required fields, row count, price threshold, turnover threshold, and abnormal move checks.
- Added `strategy/risk.py` for risk-label helpers that return risk tags and explanations only.
- Added `strategy/presets.py` for research-priority, stable-observation, and high-elasticity observation preset structures.
- The new framework is not connected to existing screening output, scoring rules, page display, or sorting logic.
- `legacy_app.py` does not import the new strategy package.

V1.2.9 architecture wrap-up:

- Clarified `app.py` as the Streamlit page setup and navigation entrypoint only.
- Added an explicit `render_legacy_workbench()` compatibility wrapper in `legacy_app.py`.
- Made `ui/screening_ui.py` depend on `legacy_app.py` through an explicit `legacy_workbench` compatibility alias.
- Kept legacy workbench UI, legacy screening renderer, real network fetch orchestration, scoring rules, stock pools, and AkShare / BaoStock / yfinance call flows unchanged.
- Added a boundary test for version alignment and compatibility surface visibility.

V1.2.8 architecture cleanup:

- Added mock tests for `fetch_a_share_fundamental_data` empty and exception paths.
- Added mock tests for `get_fundamental_data` sample fallback and non-A-share safe records.
- Added mock tests for `fetch_screening_price_data` AkShare-to-BaoStock fallback, all-source failure, and missing Close-field protection.
- Kept real AkShare, BaoStock, and yfinance call implementations unchanged in `legacy_app.py`.
- No business features, data sources, scoring rules, or stock-pool contents were changed.

V1.2.7 architecture cleanup:

- Migrated `clean_metric_value` to `data/fundamental_data.py`.
- Migrated `build_fundamental_record` to `data/fundamental_data.py`.
- Migrated `get_fundamental_sample_data` to `data/fundamental_data.py`.
- Kept real fundamental-data fetch implementations in `legacy_app.py`; `data/fundamental_data.py` exposes lazy compatibility wrappers for those paths.
- No business features, data sources, scoring rules, or stock-pool contents were changed.

V1.2.6 architecture cleanup:

- Migrated A-share and HK symbol normalization helpers to `data/market_data.py`.
- Migrated A-share yfinance and BaoStock ticker conversion helpers to `data/market_data.py`.
- Migrated `normalize_price_dataframe` and `keep_recent_rows` to `data/market_data.py`.
- Kept network data fetch implementations in `legacy_app.py`; `data/market_data.py` exposes lazy compatibility wrappers for those paths.
- No business features, data sources, scoring rules, or stock-pool contents were changed.

V1.2.5 architecture cleanup:

- Migrated `generate_selection_reasons` to `core/explanations.py`.
- Migrated `generate_screening_risk_warnings` to `core/explanations.py`.
- Migrated `generate_screening_summary` to `core/explanations.py`.
- Migrated `generate_fundamental_summary` to `core/explanations.py`.
- Migrated `join_explanation_items` to `core/explanations.py`.
- `legacy_app.py` keeps importing these functions as the compatibility path.
- No business features, data sources, scoring rules, or stock-pool contents were changed.

V1.2.4 架构清理：

- 迁移板块强度初步统计函数 `generate_sector_strength_summary` 到 `core/sector_strength.py`。
- 迁移板块强度解释函数 `generate_sector_strength_text` 到 `core/sector_strength.py`。
- `legacy_app.py` 继续作为兼容层导入这些函数，保持旧调用路径可用。
- 补充板块强度 core 路径、legacy 兼容路径、空数据和缺失字段测试。
- 不新增业务功能，不新增数据源，不修改评分规则，不改变股票池内容。

V1.2.3 架构清理：

- 第一批迁移 `core` 层评分逻辑：研究优先级评分、基本面质量评分、综合研究观察评分。
- `legacy_app.py` 继续作为兼容层导入这些评分函数，保持旧调用路径可用。
- 补充评分函数典型输入、空输入和兼容路径测试。
- 不新增业务功能，不新增数据源，不修改评分规则，不改变股票池内容。

V1.2.2 已完成：

- 第一批迁移 `config` 层所有权：股票池、股票名称映射、行业/板块/主题映射、内置基本面样例数据。
- `legacy_app.py` 继续作为兼容层导入这些配置，避免破坏旧调用路径。
- 补充配置模块不依赖 `legacy_app.py` 的测试。
- 不新增业务功能，不新增数据源，不修改评分规则，不改变股票池内容。

V1.2.1 已完成：

- 统一 README、ROADMAP 和 DEV_LOG 版本信息。
- 明确 `legacy_app.py` 当前是兼容层 / 旧版核心逻辑承载层，不是无用备份。
- 自动研究对象筛选推荐入口统一为 `ui.screening_ui.render_screening_page()`。
- 补充模块导入、安全文案和筛选字段契约的最小测试。
- 不新增业务功能，不新增数据源，不修改评分规则，不改变股票池内容。

V1.1 已完成：

- 自动研究对象筛选模块增加性能优化与缓存机制。
- 行情筛选结果缓存 30 分钟，基本面数据缓存 1 小时。
- 新增运行模式：快速模式和完整模式。
- 快速模式默认启用，优先展示核心量价结果，跳过基本面明细、板块强度和详细诊断。
- 完整模式展示基本面字段、板块强度统计、筛选总结和详细失败诊断。
- 新增“清除缓存并重新获取数据”按钮。
- 默认最大处理数量调整为 10，可选 10、20、30、50。
- 免费数据源可能延迟、缺失、限流或接口不稳定；本项目不适合直接用于实盘交易。

V1.0 新增：

- A股基本面质量筛选初版。
- 基本面字段包括总市值、PE_TTM、PB、ROE、营收同比增长率、归母净利润同比增长率、毛利率、净利率、资产负债率和股息率。
- 新增基本面质量评分，不替代原有研究优先级评分。
- 新增综合研究观察评分，用于结合量价和基本面维度做研究排序参考。
- 基本面数据优先尝试 AkShare，失败后使用内置示例数据兜底；港股和美股暂不强行启用基本面筛选。
- 内置示例基本面数据仅用于学习和原型演示，不代表最新真实财务数据。
- 本模块不构成投资建议。后续可接入 Tushare Pro、正式财务数据源、公告数据和事件催化。

V0.9.6 新增：

- A股股票增加行业、板块、主题标签。
- 自动研究对象筛选表格展示行业、板块和主题标签。
- 新增板块强度初步统计，按当前股票池样本聚合平均研究优先级评分、触发比例、近 20/60 日涨跌幅、成交量放大倍数、年化波动率和最大回撤。
- 新增板块强度解释文本，用于输出当前股票池内的板块观察和研究线索。
- 板块统计只基于当前股票池样本，不代表全市场板块强弱，不构成投资建议。
- 后续将加入更完整的板块数据源、板块指数、基本面质量和事件催化。

V0.9.5 新增：

- A股默认股票池升级为多类型研究股票池。
- 新增股票中文名称展示，解析表、候选池表、成功明细、未纳入表和失败表均尽量展示股票名称。
- 新增最大处理数量控制，支持 10、20、30、50，默认 20。
- A股名称当前主要来自内置映射表，保证离线和批量展示稳定，后续可接入更完整的基础信息数据源。
- 股票池只是研究样本，不代表投资建议。
- 后续将加入板块强度、基本面质量、事件催化和交易纪律模块。

V0.9.4 新增：

- 自动研究对象筛选模块新增入选理由。
- 新增基于指标阈值的数据不足、波动、回撤、量能和数据源风险提示。
- 新增筛选总结，概括覆盖数量、Top 候选池共性、主要风险特征和下一步研究方向。
- 入选理由来自真实量价指标，例如均线结构、近 20/60 日涨跌幅、成交量放大倍数和数据质量结论。
- 风险提示来自真实指标和数据源状态，例如短期涨幅、最大回撤、年化波动率、有效交易日数量、成交量字段和备用数据源。
- 筛选结果只代表研究优先级，当前仍偏技术面和量价维度，不构成投资建议。
- 后续将加入板块强度、基本面质量、消息催化和交易纪律模块。

V0.9.3 新增：

- 自动研究对象筛选模块新增量价指标计算。
- 新增研究优先级评分，并按分数从高到低展示 Top N 候选结果表。
- 指标包括最新价格、近 5/20/60 日涨跌幅、MA20、MA60、均线结构、成交量放大倍数、最大回撤、年化波动率和有效交易日数量。
- 评分偏技术面和量价维度，只用于帮助排序进一步研究对象，不代表具体操作建议，不构成投资建议。
- 数据不足、Close 缺失、Volume 缺失、NaN 或 inf 等情况会显示“数据不足”或“无法评分”，单只股票异常不会影响其他候选对象。

V0.9.2c 修复：

- A股自动研究对象筛选新增 `BaoStock` 作为备用数据源。
- A股批量行情数据源顺序调整为 `AkShare → BaoStock → yfinance`。
- AkShare 失败后优先尝试 BaoStock；BaoStock 失败后再尝试 yfinance 兜底。
- 成功获取表展示实际数据源、主数据源、备用数据源、是否使用备用数据源和数据源说明。
- 失败表展示 AkShare、BaoStock、yfinance 各自的错误摘要。

V0.9.2b 修复：

- A股 AkShare 请求失败时，筛选模块会尝试 yfinance 降级数据源。
- A股批量获取增加轻量请求节流，降低连续请求触发上游连接异常的概率。
- 获取失败表新增网络诊断字段，帮助识别 AkShare 接口、代理/VPN、网络环境或请求频率问题。
- 保留 V0.9.2 的批量获取概览、成功获取表、失败表和数据不足表。

V0.9.2 数据获取稳定性修复：

- A股批量获取会先将 `600519.SH`、`300750.SZ` 等代码转换为 6 位数字再请求 AkShare。
- A股 AkShare 会依次尝试 `adjust=""`、`adjust="qfq"`、`adjust="hfq"`。
- 如果 AkShare 因网络连接异常、接口不稳定或返回空数据失败，筛选模块会尝试 yfinance 后备代码，例如 `600519.SS`、`300750.SZ`。
- A股批量请求之间会加入轻量间隔，减少连续请求压力。
- A股筛选数据默认请求最近约 240 个自然日，并只保留最近 120 个有效交易日用于展示。
- 获取失败表会展示更详细诊断信息，包括实际查询代码、数据源、尝试参数、失败阶段、网络诊断和失败原因。

## 支持市场

- 美股：通过 `yfinance` 获取数据，例如 `NVDA`、`AAPL`、`MSFT`、`TSLA`
- 港股：通过 `yfinance` 获取数据，例如 `0700`、`9988`、`3690`，系统会自动转换为 `0700.HK`
- A股：以 `AkShare` 为主，筛选模块增加 `BaoStock` 和 `yfinance` 降级数据源，例如 `600519`、`000001`、`300750`、`002594`

## 数据源分层

- 美股：主数据源为 `yfinance`，当前不强制启用备用源。
- 港股：主数据源为 `AkShare`，备用数据源为 `yfinance`。如果 AkShare 获取失败，系统会自动尝试 yfinance，并在页面提示已使用备用数据源。
- A股：主数据源为 `AkShare`，自动研究对象筛选的数据源顺序为 `AkShare → BaoStock → yfinance`。BaoStock 适合历史行情学习和研究，不适合实盘级实时交易。

所有行情数据会尽量标准化为：

- `Date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

页面会展示实际使用的数据源、主数据源、备用数据源、是否使用备用源、最近交易日、数据频率、币种、复权口径和数据源风险提示。

## 免费数据源局限

- 免费数据源可能存在延迟。
- 字段可能缺失或临时不可用。
- 不同数据源口径可能不一致。
- 复权口径可能不完全一致。
- 新闻、财务和估值字段可能滞后或缺失。
- 免费数据源不适合直接用于实盘交易。
- 本项目不会接入真实交易账户，也不会执行真实交易操作。

## 数据质量报告

在单股票页面的“数据源与可靠性”区域，展开“数据质量报告 Data Quality Report”即可查看。

报告指标包括：

- 数据起始日期：当前行情样本最早日期。
- 数据结束日期：当前行情样本最新日期。
- 总交易日数量：当前样本行数。
- 缺失值总数：标准化行情表中的缺失字段数量。
- 重复日期数量：同一交易日重复出现的数量。
- 收盘价为空的行数：无法用于核心价格指标计算的行数。
- 成交量为 0 的行数：可能代表停牌、无成交或数据源缺失。
- 单日涨跌幅超过 20% 的异常记录数量：可能来自极端行情、复权差异或数据异常，只标记，不自动删除。
- 是否足够计算 MA20 / MA60 / MA120。
- 是否足够计算年化波动率。
- 是否足够计算最大回撤。
- 数据质量结论：数据较完整、数据基本可用但存在缺陷、数据不足请谨慎使用。

## 港股主备数据源校验

港股页面会提供“港股主备数据源校验”：

- 系统尝试同时获取 AkShare 和 yfinance 的最近行情。
- 如果两个数据源都成功，会比较最近共同交易日或最近可比交易日的收盘价。
- 差异小于等于 1% 时，提示“AkShare 与 yfinance 最近收盘价差异较小”。
- 差异超过 1% 时，提示“不同数据源存在超过 1% 的价格差异，请谨慎使用”。
- 如果任一数据源失败，校验会提示暂无法完成，但不会影响主行情展示。

## Tushare 说明

Tushare Pro 可作为未来 A股数据源增强方向，但需要 token、权限和配额配置。当前版本不强制启用，也不会要求用户输入 token。它仅作为未来可扩展的数据源方向预留，不属于当前默认数据链路。

## OpenAI API 说明

OpenAI API 不是行情数据源，不用于获取价格、成交量或财务行情。它只适合后续作为研究解释层，用于整理已获取的数据、形成学习型摘要或辅助结构化分析；当前版本不接入 OpenAI API。

## 数据来源与局限

- 数据可能存在延迟、缺失、重复日期、字段口径差异或接口临时不可用。
- App 会展示数据来源、最近更新时间、市场类型、币种、起止日期和基础数据质量检查。
- 数据质量检查包括缺失收盘价数量、重复日期数量、异常日涨跌幅数量。
- 如果历史数据不足，部分指标、对比项或回测结果会显示“数据不足”。

## 当前功能

- 单股票研究工作台
- 市场选择：美股、港股、A股
- 股票代码或内置股票名称输入
- 时间范围：3个月、6个月、1年、2年、5年
- 公司基础信息、核心价格指标、均线与趋势指标
- 估值和财务摘要
- 技术面、基本面、板块解释
- 近期重大消息和手动事件分析
- 综合本地模拟评级
- 多股票对比表格和归一化走势
- 临时自选股观察列表
- 简单策略回测
- 自动研究对象筛选模块

## 自动研究对象筛选

本模块用于从股票池中筛选研究优先级较高的候选对象，仅用于学习和研究，不构成投资建议，也不代表具体操作建议。

当前 V0.9.5 已完成：

- 模块入口
- 默认示例股票池
- 自定义股票池输入
- 股票代码解析和标准化
- 解析结果表格展示
- 批量行情数据获取
- 成功和失败记录
- 数据源展示
- 基础数据质量概览
- 量价指标计算
- 研究优先级评分
- Top N 候选结果排序展示
- 入选理由
- 风险提示
- 筛选总结
- A股多类型研究股票池
- 股票中文名称展示
- 最大处理数量控制
- 行业 / 板块 / 主题标签
- 板块强度初步统计
- A股基本面质量筛选初版
- 基本面质量评分
- 综合研究观察评分

当前 V1.0 尚未实现：

- 消息催化跟踪
- 交易纪律模块

### 研究优先级评分说明

研究优先级评分从 0 到 100，使用本地可解释规则计算。趋势结构包括当前价格是否高于 MA20、是否高于 MA60、MA20 是否高于 MA60；动量表现包括近 20 日和近 60 日涨跌幅；量能变化包括最近 5 日均量相对最近 20 日均量的放大倍数；风险扣分包括短期涨幅过大、最大回撤偏大、年化波动率偏高、有效交易日不足、成交量数据缺失和数据质量较差。

该评分只代表研究优先级，偏技术面和量价维度，用于辅助排序进一步研究对象。它不是投资建议，也不代表具体操作建议。V0.9.4 已加入入选理由、风险提示和筛选总结，后续将继续加入板块强度、基本面质量和消息催化，以提升研究完整度。

### 入选理由、风险提示和筛选总结

V0.9.4 的入选理由由本地规则生成，只引用已经计算出的真实指标。系统会检查价格是否站上 MA20/MA60、MA20 是否高于 MA60、近 20/60 日涨跌幅、成交量放大倍数和数据质量结论。如果指标不足，页面会提示当前指标未形成足够明确的研究优先级理由。

风险提示同样由本地规则生成。系统会检查近 20 日涨幅是否过高、最大回撤是否偏大、年化波动率是否偏高、有效交易日是否不足、成交量数据是否缺失，以及是否使用备用数据源。未触发主要风险阈值时，也会提示仍需结合基本面、消息面、板块环境和市场情绪进一步验证。

筛选总结会汇总本次覆盖数量、成功生成研究优先级评分的数量、Top 候选池共性、主要风险特征和下一步研究方向。当前筛选仍偏技术面和量价维度，后续将加入板块强度、基本面质量、消息催化和交易纪律模块。

### A股研究股票池体系

V0.9.5 增加 5 类 A股研究股票池：

- A股核心资产观察池：大盘蓝筹、行业龙头、长期观察。
- A股科技成长观察池：半导体、AI、电子、计算机、新能源、高端制造等成长方向。
- A股消费医药观察池：消费、白酒、医药、医疗器械、CXO、中药等方向。
- A股金融地产周期观察池：银行、保险、券商、地产链、资源周期、基建等方向。
- A股高弹性主题观察池：短期主题、成长弹性和波动较高标的，仅用于研究观察。

页面会展示股票池名称、定位、股票池总数、本次处理数量和风险提示。最大处理数量可选 10、20、30、50，默认 20；如果股票池数量超过最大处理数量，只处理前 N 只，并提示免费数据源批量请求可能较慢。

股票池仅是研究样本集合，用于组织初筛和后续研究流程，不代表投资建议。A股股票名称当前主要来自内置映射表，避免为了名称展示增加不稳定网络请求；港股和美股暂时显示“名称暂缺”，后续可接入更完整的基础信息数据源。

### 行业 / 板块 / 主题标签与板块强度

V0.9.6 为 A股内置研究股票池增加行业、板块和主题标签。标签来自本地映射表，不依赖网络实时请求。解析结果、Top N 研究候选池、成功获取明细、低优先级分层、无法评分或未纳入候选池、获取失败表都会尽量展示这些字段。

板块强度初步统计只基于当前股票池中已评分的样本，不接入外部板块指数，也不代表全市场板块强弱。统计字段包括板块、股票数量、平均研究优先级评分、触发研究优先级条件数量、触发比例、平均近 20/60 日涨跌幅、平均成交量放大倍数、平均年化波动率和平均最大回撤。

该模块用于板块观察和研究线索整理，不构成投资建议。后续可继续接入更完整的板块数据源、板块指数、基本面质量和事件催化。

### 基本面质量筛选

V1.0 新增 A股基本面质量观察。系统优先尝试通过 AkShare 获取 A股基本面字段；如果失败，会使用内置示例基本面数据作为兜底；如果仍无数据，则显示“数据暂缺”。页面会明确展示基本面数据来源：AkShare、内置示例数据或数据暂缺。

基本面质量评分从 0 到 100，观察盈利能力、成长性、盈利质量、财务稳健性、估值约束、股东回报和数据完整性。综合研究观察评分按研究优先级评分 60% 和基本面质量评分 40% 加权；如果其中一个无法评分，则使用可用分数；如果都无法评分，则显示“无法评分”。

内置示例基本面数据仅用于学习和原型演示，不代表最新真实财务数据，不能作为实盘依据。后续可接入 Tushare Pro、正式财务数据源、公告数据和事件催化。

### 性能优化与缓存

V1.1 使用 `st.cache_data` 缓存部分行情和基本面数据。自动筛选中，单只股票筛选结果缓存 30 分钟，基本面数据缓存 1 小时。缓存可减少重复请求免费数据源，提升 10-30 只股票批量筛选时的响应速度。

运行模式：

- 快速模式：只展示核心结果表，适合快速筛选股票池。
- 完整模式：展示完整基本面字段、板块强度统计、筛选总结、数据源诊断和失败详情，适合深入研究。

如遇数据源异常或怀疑缓存结果过期，可点击“清除缓存并重新获取数据”，系统会调用 `st.cache_data.clear()` 清除缓存。免费数据源仍可能存在速度和稳定性限制，本项目不适合直接用于实盘交易。

### 自动研究对象筛选数据源

- A股：本项目后续重点研究市场。筛选模块数据源顺序为 `AkShare → BaoStock → yfinance`。查询前会转换为 6 位数字代码，BaoStock 查询代码会转换为 `sh.600519` 或 `sz.000001` 格式。免费数据源可能因接口返回空数据、字段变化、日期范围、代理/VPN、请求频率或网络环境导致失败。
- 港股：主数据源为 `AkShare`，备用数据源为 `yfinance`，如果使用备用源会在结果表中显示。
- 美股：主数据源为 `yfinance`，输入会统一大写。

### 批量获取结果说明

成功获取表展示：

- 股票代码
- 股票名称
- 市场
- 实际查询代码
- 数据源
- 主数据源
- 备用数据源
- 是否使用备用数据源
- 最新交易日
- 有效交易日数量
- 数据质量
- 数据源说明

获取失败表展示无法获取行情的候选对象及诊断信息，包括股票代码、股票名称、实际查询代码、市场、尝试过的数据源、失败阶段、失败原因摘要、AkShare 错误摘要、BaoStock 错误摘要和 yfinance 错误摘要。

数据不足表展示有效交易日少于 60 的候选对象。数据不足不等于代码错误，但表示当前样本不适合直接用于后续指标计算。

免费数据源可能延迟、缺失或临时失败。当前版本的自动研究对象筛选模块输出的是研究候选池和研究优先级排序，不构成投资建议。

### 默认股票池

A股：

```text
600519.SH, 300750.SZ, 601318.SH, 600036.SH, 000858.SZ, 002594.SZ, 688981.SH, 300760.SZ, 600276.SH, 000333.SZ
```

港股：

```text
0700.HK, 9988.HK, 3690.HK, 1810.HK, 0981.HK, 1211.HK, 2269.HK, 9999.HK, 9618.HK, 1024.HK
```

美股：

```text
AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA, AMD, AVGO, NFLX
```

### 自定义股票池输入格式

支持英文逗号、中文逗号、空格和换行分隔：

```text
NVDA, AAPL, MSFT
```

```text
600519.SH, 300750.SZ
```

```text
0700.HK, 9988.HK
```

单次最多解析 50 只，超过后仅保留前 50 只并显示提示。

## 多股票输入格式

多股票对比输入框支持英文逗号、中文逗号、空格和换行分隔：

```text
NVDA, AAPL, MSFT
```

```text
0700，9988 3690
```

```text
600519
000001
300750
```

单次最多处理 10 只股票。超过 10 只时，系统只取前 10 只并提示。

## 自选股观察列表

自选股列表通过 `st.session_state` 临时保存：

- 可将当前单股票分析标的加入自选股
- 可查看当前自选股数量和代码列表
- 可清空自选股
- 可基于自选股一键运行多股票对比

自选股列表仅保存在当前 Streamlit 会话中，关闭会话后可能丢失。

## 简单策略回测

当前支持策略：

1. 均线趋势策略：当收盘价高于 20 日均线时持仓，否则空仓。
2. 双均线策略：当 20 日均线高于 60 日均线时持仓，否则空仓。
3. 动量策略：当过去 20 日收益率大于 0 时持仓，否则空仓。

所有策略都使用上一日信号作为当日持仓，避免未来函数。回测中加入简化单边交易成本，仓位变化时扣除成本。

## 回测指标说明

回测模块展示：

- 策略累计收益率
- 基准累计收益率
- 策略年化收益率
- 基准年化收益率
- 策略年化波动率
- 策略最大回撤
- 夏普比率，假设无风险利率为 0
- 交易次数
- 持仓天数占比
- 胜率，按策略日收益大于 0 粗略计算

回测模块还会展示策略净值曲线、基准净值曲线和最近 20 条买卖信号。

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 运行

```powershell
streamlit run app.py
```

运行后打开 Streamlit 在终端中显示的本地 URL。

## 运行测试

```powershell
python -m pytest -q
```

测试覆盖核心指标函数和回测函数的基础场景，包括正常数据、空数据、缺失值数据和极端涨跌数据。

## 安全注意事项

- 项目不需要 API key、token、密码或交易账户凭证。
- 不要把 `.env`、`.streamlit/secrets.toml`、日志、缓存、数据库文件提交到 GitHub。
- 当前 `.gitignore` 已忽略常见密钥文件、缓存文件、日志文件和本地数据库文件。
- 不要在公开环境中输入真实账户、身份证件、手机号、邮箱或其他敏感个人信息。
- 本项目不执行用户输入的代码，不使用 `eval` 或 `exec` 处理用户输入。
- 股票代码和股票名称只做基础格式校验，不能替代数据源自身的合法性校验。

## 当前局限

- 安全检查仍是基础级别，不等同于生产级安全审计。
- 回测模型非常简化。
- 没有考虑滑点、真实撮合、停牌、涨跌停、分红复权差异等复杂因素。
- 交易成本只是简化估计。
- 回测结果不代表未来收益。
- 当前结果仅用于学习演示，不构成投资建议。
- 自选股列表仅保存在当前会话中。
- 多股票对比和回测速度受 `yfinance`、`akshare` 等数据源影响。
- 数据源可能延迟、缺失或字段口径不一致。
- 不应据此进行真实交易。

## 下一步计划

- 加入更多策略模板
- 加入参数调节
- 加入多股票组合回测
- 加入 AI 研究摘要
- 拆分项目结构，提高可维护性
