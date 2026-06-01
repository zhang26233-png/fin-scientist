# Development Log

## 2026-06-01

### Target

- Complete V1.6.0 fundamental field standardization phase.
- Add read-only fundamental field detection, value normalization, missing-field checks, quality labels, and base summaries without changing screening results, default sorting, strategy scoring, stock pools, data sources, or `core/scoring.py`.
- Keep V1.4.4-V1.5.3 tests stable.

### Fundamental Profile

- Added `strategy/fundamental.py`.
- Added `normalize_fundamental_value()`, `detect_fundamental_fields()`, `build_fundamental_data_quality()`, `build_fundamental_base_summary()`, and `build_fundamental_profile()`.
- Recognized fields: revenue, net profit, gross margin, ROE, PE, PB, PS, debt ratio, operating cashflow, revenue growth, profit growth, market cap, and industry.
- Added Chinese aliases including `营业收入`, `净利润`, `毛利率`, `净资产收益率`, `市盈率`, `市净率`, `市销率`, `资产负债率`, `经营现金流`, `营收增长率`, `净利润增长率`, `总市值`, and `行业`.
- Added preview fields: `fundamental_available`, `fundamental_fields_detected`, `missing_fundamental_fields`, `fundamental_data_quality_label`, and `fundamental_summary_base`.
- `ui/screening_ui.py` shows the compact fundamental availability and data-quality summary inside the existing strategy preview expander.
- `legacy_app.py` only updates the version and does not import strategy modules.

### Tests

- Added `tests/test_strategy_fundamental.py`.
- Expanded `tests/test_strategy_preview.py` and `tests/test_strategy_ui_integration.py` for fundamental preview fields.
- Updated `tests/test_module_imports.py` for V1.6.0 and `strategy.fundamental`.

### Next Step

- V1.6.1 can build a basic profitability, growth, valuation, and financial-risk observation layer on top of the standardized fundamental profile, still without changing screening or strategy scoring.

## 2026-06-01

### Target

- Complete V1.5.3 technical research conclusion phase.
- Convert V1.5.2 technical labels into compact, readable research conclusions without changing screening results, default sorting, scoring rules, stock pools, data sources, or `core/scoring.py`.
- Keep V1.4.4-V1.5.2 tests stable.

### Technical Conclusions

- Added `technical_grade`, `technical_style`, `technical_strength`, `technical_risk_level`, `technical_watch_points`, and `technical_summary_short`.
- `technical_grade` uses A/B/C/D research levels based on trend structure, volume-price confirmation, risk labels, and data sufficiency.
- `technical_style` summarizes the technical profile as trend momentum, volume breakout, pullback watch, high-volatility watch, weak/choppy, or insufficient data.
- `technical_risk_level` summarizes severe overheat, high volatility, and volume-downside risk as high-risk technical observations.
- `ui/screening_ui.py` now shows the compact technical conclusion fields first in the existing strategy preview expander.
- `legacy_app.py` only updates the version and does not import strategy modules.

### Tests

- Expanded `tests/test_strategy_technical.py` for technical grade, style, strength, risk level, watch points, weak structures, insufficient data, and neutral wording.
- Expanded `tests/test_strategy_preview.py` and `tests/test_strategy_ui_integration.py` for the new conclusion fields.
- Updated `tests/test_module_imports.py` for V1.5.3.

### Next Step

- V1.5.4 can add a compact technical detail panel or export view for the conclusion fields while keeping the original screening table unchanged.

## 2026-06-01

### Target

- Complete V1.5.2 technical structure preview phase.
- Add finer technical labels and summaries to `strategy.preview` without changing screening results, default sorting, scoring rules, stock pools, data sources, or `core/scoring.py`.
- Keep V1.4.4-V1.5.1 tests stable.

### Technical Structure

- Added `strategy/technical.py`.
- Added `analyze_moving_average_structure()`, `analyze_trend_quality()`, `analyze_breakout_pullback_state()`, `analyze_volume_price_structure()`, `analyze_short_term_overheat()`, `analyze_volatility_risk()`, and `build_technical_profile()`.
- Added preview fields: `ma_structure_label`, `trend_quality_label`, `breakout_pullback_label`, `volume_price_structure_label`, `short_term_overheat_label`, `volatility_risk_label`, and `technical_profile_summary`.
- `strategy.preview` appends these fields to the preview DataFrame while preserving input order by default.
- `ui/screening_ui.py` displays core technical labels inside the existing collapsed strategy preview expander.
- `legacy_app.py` only updates the version and does not import strategy modules.

### Tests

- Added `tests/test_strategy_technical.py`.
- Expanded `tests/test_strategy_preview.py` for technical preview fields.
- Expanded `tests/test_strategy_ui_integration.py` for technical field presence and order preservation.
- Updated `tests/test_module_imports.py` for V1.5.2 and `strategy.technical`.

### Next Step

- V1.5.3 can connect these technical labels to a compact detail panel or export view while keeping the original screening table unchanged.

## 2026-06-01

### Target

- Complete V1.5.1 strategy preview explanation phase.
- Add structured, readable explanations for existing `strategy_score` preview output without changing screening results, default sorting, scoring rules, stock pools, data sources, or `core/scoring.py`.
- Keep V1.4.4-V1.5.0 tests stable.

### Strategy Preview Explanations

- Added row-level explanation fields: `strategy_reason`, `trend_reason`, `momentum_reason`, `volume_price_reason`, `liquidity_reason`, `risk_reason`, `data_quality_reason`, `preset_reason`, and `confidence_note`.
- Added `build_strategy_reason_fields()` in `strategy/explanations.py`.
- `strategy.preview` appends explanation fields to the preview DataFrame while preserving input order by default.
- `ui/screening_ui.py` displays core explanation columns inside the existing collapsed preview expander.
- `legacy_app.py` only updates the version and does not import strategy modules.

### Tests

- Expanded `tests/test_strategy_explanations.py` for empty input, missing fields, trend explanation, volume-price confirmation, risk/data-quality explanation, preset reason, confidence notes, and forbidden wording.
- Expanded `tests/test_strategy_preview.py` and `tests/test_strategy_ui_integration.py` to assert explanation columns and order preservation.
- Updated `tests/test_module_imports.py` for V1.5.1.

### Next Step

- V1.5.2 can add optional preview export controls for the explanation-enhanced DataFrame while keeping the original screening table unchanged.

## 2026-05-29

### Target

- Complete V1.5.0 optional strategy preview UI phase.
- Show strategy preview results on the screening page without changing the original screening table, default sorting, scoring rules, stock pools, data sources, or `core/scoring.py`.
- Keep V1.4.4-V1.4.16 tests stable.

### Strategy Preview UI

- Added `build_screening_strategy_preview()` and `render_strategy_preview_section()` to `ui/screening_ui.py`.
- The screening page now renders a collapsed strategy preview section after the original screening workflow returns its result DataFrame.
- The preview calls `build_strategy_preview(result_df, sort_by_strategy=False)` by default.
- Optional preview sorting changes only the preview table.
- Preview display fields include symbol, name, original score, strategy score, best preset, dominant style, consensus level, per-preset scores, risk labels, data-quality labels, and warnings.
- `legacy_app.py` returns the existing screening result DataFrame for UI composition but does not import strategy modules.

### Tests

- Added `tests/test_strategy_ui_integration.py`.
- Updated `tests/test_strategy_preview.py` for the new UI dependency boundary.
- Updated `tests/test_module_imports.py` for V1.5.0.
- Covered empty input, missing fields, input immutability, default order preservation, preview-only sorting, required preview fields, safety wording, legacy boundary, and `core/scoring.py` boundary.

### Next Step

- V1.5.1 can add optional CSV/JSON-like download controls for the preview section while keeping the original screening table unchanged.

## 2026-05-29

### Target

- Complete V1.4.16 internal strategy preview/export phase.
- Build read-only strategy preview outputs for caller-provided candidate pools using default strategy scoring and cross-preset comparison.
- Keep V1.4.4-V1.4.15 tests stable without changing UI, screening output, sorting, default strategy scoring, stock pools, data sources, or `core/scoring.py`.

### Strategy Preview

- Added `strategy/preview.py`.
- Added `build_strategy_preview()`.
- Added `build_strategy_preview_row()`.
- Added `export_strategy_preview_to_json_like()`.
- Added `export_strategy_preview_to_csv()`.
- Preview fields include symbol, name, original score, default strategy score, preset name, best/worst preset, score spread, average preset score, dominant style, consensus level, per-preset scores, risk labels, data-quality labels, and warnings.
- Preview output preserves source order by default; optional strategy sorting changes only the preview DataFrame.
- The module only reads caller-provided candidate pools and does not access real data sources.

### Tests

- Added `tests/test_strategy_preview.py`.
- Updated `tests/test_module_imports.py` to include `strategy.preview` and V1.4.16 entrypoint version checks.
- Covered empty input, missing fields, row preview structure, input immutability, default order preservation, optional preview-only sorting, risk/data-quality labels, JSON-like export, CSV export, safety wording, and legacy/UI dependency boundaries.

### Next Step

- V1.4.17 can add an optional manual CLI/script wrapper around `strategy.preview` for local exports, still without UI integration or real data downloads.

## 2026-05-29

### Target

- Complete V1.4.15 internal backtest metrics schema validation and diagnostics phase.
- Check the structural stability of `build_backtest_metrics_summary()` output and generate neutral research observations by score bucket, preset, dominant style, and consensus level.
- Keep V1.4.4-V1.4.14 drift, calibration, snapshot, and backtest tests stable without changing UI, screening output, sorting, default strategy scoring, stock pools, data sources, or `core/scoring.py`.

### Backtest Diagnostics

- Added `strategy/backtest_diagnostics.py`.
- Added `validate_backtest_metrics_schema()`.
- Added `diagnose_score_bucket_performance()`.
- Added `diagnose_preset_performance()`.
- Added `diagnose_style_performance()`.
- Added `diagnose_consensus_performance()`.
- Added `build_backtest_diagnostics_report()`.
- Schema checks cover total count, valid count, insufficient-data count, outcome counts and ratios, average forward returns, average forward drawdown, grouped summaries, warnings, and metadata.
- Diagnostics identify insufficient sample counts, high insufficient-data ratios, low group coverage, missing grouped structures, and limited score-bucket distinction.
- The module only reads caller-provided summaries and does not access real data sources.

### Tests

- Added `tests/test_strategy_backtest_diagnostics.py`.
- Updated `tests/test_module_imports.py` to include `strategy.backtest_diagnostics` and V1.4.15 entrypoint version checks.
- Covered empty summary, missing fields, valid schema, stronger high-score bucket, limited score-bucket distinction, insufficient samples, preset/style/consensus observations, report assembly, source immutability, safety wording, and legacy/UI dependency boundaries.

### Next Step

- V1.4.16 can add an internal JSON-like export snapshot for diagnostics reports, still without UI integration or real data downloads.

## 2026-05-29

### Target

- Complete V1.4.14 internal backtest metric aggregation phase.
- Aggregate caller-provided backtest samples by preset, strategy-score bucket, dominant style, and consensus level for research validation only.
- Keep V1.4.4-V1.4.13 drift, calibration, snapshot, and backtest tests stable without changing UI, screening output, sorting, default strategy scoring, stock pools, data sources, or `core/scoring.py`.

### Backtest Metrics

- Added `bucket_strategy_score()`.
- Added `summarize_backtest_by_preset()`.
- Added `summarize_backtest_by_score_bucket()`.
- Added `summarize_backtest_by_dominant_style()`.
- Added `summarize_backtest_by_consensus_level()`.
- Added `build_backtest_metrics_summary()`.
- Score buckets are `high_score` for scores >= 75, `mid_score` for scores >= 50 and < 75, `low_score` for scores < 50, and `insufficient_score` for missing or invalid scores.
- Metrics include total count, valid count, insufficient-data count, outcome counts and ratios, 1/3/5/10 day forward-return averages, average forward drawdown, warnings, and read-only metadata.
- The module only uses caller-provided samples and does not access real data sources.

### Tests

- Added `tests/test_strategy_backtest_metrics.py`.
- Updated `tests/test_strategy_backtest.py` with a lightweight metrics summary aggregation check.
- Covered empty input, missing fields, score buckets, preset/style/consensus grouping, outcome distribution, return and drawdown averages, input immutability, safety wording, and legacy/UI dependency boundaries.

### Next Step

- V1.4.15 can add schema validation or export helpers for backtest metric summaries, still without UI integration or real data downloads.

## 2026-05-28

### Target

- Complete V1.4.13 internal backtest sample helper phase.
- Define validation-ready inputs and sample construction helpers for later strategy-score and multi-preset effectiveness checks without downloading data, connecting UI, changing existing screening output, sorting, default strategy scoring, or `core/scoring.py`.
- Keep V1.4.4-V1.4.12 drift, calibration, and snapshot tests stable.

### Backtest Helpers

- Added `strategy/backtest.py`.
- Added `validate_backtest_input()`.
- Added `calculate_forward_return()`.
- Added `classify_backtest_outcome()`.
- Added `build_backtest_sample()`.
- Added `summarize_backtest_samples()`.
- Outcome labels include `positive_follow_through`, `weak_follow_through`, `failed_follow_through`, `high_drawdown_risk`, and `insufficient_data`.
- The module only uses caller-provided data and does not access real data sources.

### Tests

- Added `tests/test_strategy_backtest.py`.
- Covered empty input, missing fields, stable forward-return calculation, typical sample construction, positive/weak/failed/high-drawdown/insufficient-data outcomes, sample summaries, source immutability, safety wording, and legacy/UI dependency boundaries.
- Re-ran drift, calibration, snapshot, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.14 can add internal backtest metric aggregation such as outcome hit-rate by preset and score bucket, still without UI integration or real data downloads.

## 2026-05-28

### Target

- Complete V1.4.12 internal strategy snapshot export phase.
- Convert single-candidate preset comparisons and candidate-pool preset summaries into stable JSON-like dictionaries without changing UI, existing screening output, sorting, default strategy scoring, or `core/scoring.py`.
- Keep V1.4.4-V1.4.11 drift and calibration tests stable.

### Export Helpers

- Added `strategy/export.py`.
- Added `export_preset_comparison_snapshot()`.
- Added `export_preset_pool_summary_snapshot()`.
- Added `build_strategy_snapshot_payload()`.
- Snapshot outputs include `schema_version`, `snapshot_type`, stable comparison or summary fields, warnings, and merged metadata.
- `generated_at` can be supplied for stable tests or omitted for UTC timestamp generation in combined payloads.

### Tests

- Added `tests/test_strategy_export.py`.
- Covered empty input, single-candidate snapshot structure, candidate-pool summary snapshot structure, metadata merge, warning preservation, input immutability, safety wording, and legacy/UI dependency boundaries.
- Re-ran drift, calibration, distribution, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.13 can add internal snapshot validation helpers for schema compatibility checks, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.11 internal candidate-pool preset summary phase.
- Aggregate multi-preset comparison results across a batch of candidates without changing UI, existing screening output, sorting, default strategy scoring, or `core/scoring.py`.
- Keep V1.4.4-V1.4.10 drift and calibration tests stable.

### Pool Summary

- Added `summarize_preset_comparison_pool()` to `strategy/preset_comparison.py`.
- The helper runs `compare_strategy_presets()` for each candidate row and preserves input order.
- Output includes total count, valid count, insufficient-data count, dominant-style counts and ratios, consensus-level counts and ratios, average scores by preset, average score spread, max score spread, summary text, and warnings.
- Shortcut counts are exposed for `broad_consensus_high`, `style_specific_high`, `mixed_signal`, and `broad_consensus_low`.

### Tests

- Added `tests/test_strategy_preset_pool_summary.py`.
- Covered empty input, missing fields, multi-row summary stability, style and consensus counts, preset averages, spread statistics, source immutability, safety wording, and legacy/UI dependency boundaries.
- Re-ran drift, calibration, distribution, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.12 can add internal export-ready JSON snapshots for preset comparison and pool summaries, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.10 internal cross-preset comparison summary phase.
- Compare the same candidate across multiple internal strategy presets without changing UI, existing screening output, sorting, default strategy scoring, or `core/scoring.py`.
- Keep V1.4.4-V1.4.9 drift and calibration tests stable.

### Comparison Module

- Added `strategy/preset_comparison.py`.
- Added `compare_strategy_presets(source, preset_names=None)`.
- Added `summarize_preset_scores(preset_scores)`.
- Outputs include `preset_scores`, `best_preset`, `worst_preset`, `score_spread`, `average_preset_score`, `consensus_level`, `dominant_style`, `style_notes`, and `warnings`.

### Consensus And Style

- Consensus levels include `broad_consensus_high`, `style_specific_high`, `mixed_signal`, `broad_consensus_low`, and `insufficient_data`.
- Dominant styles include `balanced`, `trend_momentum`, `volume_breakout`, `low_risk_quality`, `high_elasticity`, `mixed`, and `insufficient_data`.
- The helper is read-only and does not connect to Streamlit pages.

### Tests

- Added `tests/test_strategy_preset_comparison.py`.
- Updated version-boundary import tests.
- Re-ran drift, calibration, distribution, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.11 can add internal batch-level preset comparison across multiple candidates, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.9 internal multi-preset strategy scoring phase.
- Allow the same candidate set to be evaluated through different internal strategy views without changing UI, existing screening output, sorting, or `core/scoring.py`.
- Keep the default preset compatible with V1.4.8 scoring and keep V1.4.4-V1.4.8 drift checks stable.

### Preset Enhancements

- `strategy/presets.py` now defines `balanced_research`, `trend_momentum`, `volume_breakout`, `low_risk_quality`, and `high_elasticity_watch`.
- Each preset includes `preset_name`, `display_name`, `description`, `weights`, `risk_policy`, and `data_quality_policy`.
- Existing `research_priority`, `stable_observation`, and `high_elasticity_observation` keys remain available for adapter compatibility.
- Added `get_default_strategy_preset()` and safe fallback for unknown preset keys.

### Scoring Enhancements

- `calculate_strategy_scores()` now accepts `preset_name` or `preset_config`.
- Score rows now include `preset_name`, `preset_display_name`, and `strategy_score_components`.
- Default `balanced_research` keeps the previous score formula weights to avoid drift.
- Non-default presets adjust factor weights, risk-policy multipliers, data-quality multipliers, and limited preset bonuses or penalties.

### Tests

- Added `tests/test_strategy_presets.py`.
- Updated `tests/test_strategy_scoring.py` for multi-preset scoring behavior.
- Updated preset compatibility checks and version-boundary import tests.
- Re-ran drift, calibration, distribution, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.10 can add internal side-by-side preset comparison summaries, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.8 internal risk and data-quality explanation phase.
- Add audit-style explanations for `risk_labels`, `data_quality_labels`, `risk_penalty`, and `data_quality_penalty`.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or connect explanations to UI.

### Explanation Module

- Added `strategy/explanations.py`.
- `build_strategy_explanations()` accepts a score row, a scoring result dictionary, or a list of score rows.
- Output includes `risk_explanations`, `data_quality_explanations`, `penalty_breakdown`, `factor_notes`, `summary_text`, `warnings`, and read-only metadata.
- Empty input, missing fields, unknown labels, and abnormal inputs return safe explanation structures.

### Risk Explanations

- Added explanations for `high_volatility`, `extreme_upside_return`, `volume_downside_risk`, `overheated_turnover`, `low_liquidity`, and related data sufficiency labels.

### Data Quality Explanations

- Added explanations for `missing_price_fields`, `missing_volume_fields`, `missing_turnover_fields`, `invalid_numeric_fields`, and `insufficient_factor_data`.

### Drift Checks

- V1.4.4-V1.4.7 drift-check thresholds remained stable.
- `strategy_score` calculation was not changed.

### Tests

- Added `tests/test_strategy_explanations.py`.
- Updated version-boundary import tests.
- Re-ran drift, calibration, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.9 can add internal batch-level explanation summaries, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.7 strategy risk and data-quality penalty enhancement phase.
- Improve internal `strategy_score` risk distinction for high volatility, extreme short-term return, volume-supported downside moves, overheated turnover, low liquidity, missing key fields, and invalid numeric values.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or add strategy logic to `legacy_app.py` or `ui/screening_ui.py`.

### Risk Enhancements

- `strategy/risk.py` adds stable risk codes for `high_volatility`, `extreme_upside_return`, `volume_downside_risk`, `overheated_turnover`, `low_liquidity`, and `insufficient_factor_data`.
- Added detection for amplitude-based high volatility, short-term extreme return, volume-supported downside moves, overheated turnover, and low-liquidity evidence from amount, volume, and turnover.
- Non-finite risk inputs are treated as unavailable so risk labeling remains safe.

### Scoring Enhancements

- `strategy/scoring.py` now reads `pct_chg`, amplitude, and moving-average aliases when available.
- Risk penalty now reflects high volatility/amplitude, extreme short-term return, volume downside, overheated turnover, and confirmed low liquidity.
- Score rows now include internal `risk_labels` and `data_quality_labels`.

### Data Quality Enhancements

- Data-quality labels include `missing_price_fields`, `missing_volume_fields`, `missing_turnover_fields`, `invalid_numeric_fields`, and `insufficient_factor_data`.
- Missing turnover or moving-average fields are labeled, while penalties remain calibrated so fixed drift samples stay in range.

### Drift Checks

- V1.4.4/V1.4.5/V1.4.6 drift-check thresholds remained stable.
- No drift threshold changes were required.

### Tests

- Updated `tests/test_strategy_risk.py`.
- Updated `tests/test_strategy_scoring.py`.
- Updated version-boundary import tests.
- Re-ran drift, calibration, distribution, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.8 can add internal score-explanation summaries for risk and data-quality labels, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.6 strategy volume-price and liquidity factor enhancement phase.
- Improve internal `strategy_score` distinction for amount activity, volume-ratio confirmation, turnover health, low-liquidity risk, and overheated turnover.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or add strategy logic to `legacy_app.py` or `ui/screening_ui.py`.

### Factor Enhancements

- `strategy/factors.py` now reads amount aliases, volume-ratio aliases, and turnover aliases for volume-price and liquidity observations.
- `calculate_volume_price_factor()` adds labels for `volume_price_confirmed`, `volume_price_weak`, `low_liquidity`, `overheated_turnover`, and `volume_downside_risk`.
- `calculate_liquidity_factor()` distinguishes low amount, active amount, low turnover, moderate turnover, and overheated turnover.
- Non-finite amount, volume, turnover, and volume-ratio values are treated as unavailable so extreme inputs return bounded results.

### Scoring Enhancements

- `strategy/scoring.py` keeps the existing score components and weights, but separates volume-price confirmation from liquidity availability more clearly.
- Low amount and low turnover reduce `liquidity_score`.
- Positive trend with stronger volume ratio can raise `volume_price_score`.
- Downside movement with elevated volume ratio and overheated turnover increase `risk_penalty`.

### Drift Checks

- V1.4.4 drift-check thresholds remained stable.
- No drift threshold changes were required.

### Tests

- Updated `tests/test_strategy_factors.py`.
- Updated `tests/test_strategy_scoring.py`.
- Re-ran drift, calibration, distribution, adapter, py-compile, full pytest, safety scan, and Streamlit short-start checks.

### Next Step

- V1.4.7 can add internal factor explanation snapshots for strategy-score subcomponents, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.5 strategy trend and momentum factor enhancement phase.
- Improve internal strategy-score distinction for trend direction, moving-average position, short-term momentum, overheating, and recent weakness.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or add strategy logic to `legacy_app.py` or `ui/screening_ui.py`.

### Factor Enhancements

- `strategy/factors.py` adds `calculate_moving_average_position_factor()`.
- `strategy/factors.py` adds `calculate_momentum_profile_factor()`.
- `calculate_trend_factor()` now includes `trend_direction_label` and trend quality details.
- `calculate_momentum_factor()` now includes `momentum_label`, consecutive-up count, and consecutive-down count.

### Scoring Enhancements

- `strategy/scoring.py` now reads optional 5-day and 10-day return fields from DataFrame inputs.
- Trend sub-score distinguishes moderate trend, flat trend, downtrend, and overheated trend.
- Momentum sub-score distinguishes moderate momentum, overheated momentum, recent weakness, and continuous weakness.
- Overheated short-term return increases risk penalty.

### Drift Checks

- V1.4.4 drift-check thresholds remained stable.
- No drift threshold changes were required.

### Tests

- Updated `tests/test_strategy_factors.py`.
- Updated `tests/test_strategy_scoring.py`.
- Re-ran drift, calibration, and score-distribution tests to confirm stable ranges.

### Next Step

- V1.4.6 can add internal factor-explanation helpers for trend and momentum sub-scores, still without UI integration.

## 2026-05-28

### Target

- Complete V1.4.4 strategy score drift-check phase.
- Add fixed-sample drift checks for strategy scores, alignment labels, and aggregate comparison summaries.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or add drift logic to `legacy_app.py` or `ui/screening_ui.py`.

### Drift Samples

- High-quality trend sample.
- Low-liquidity sample.
- Overheated-risk sample.
- Missing-data sample.
- Neutral sample.
- Strategy-strong research-weak sample.
- Research-strong strategy-weak sample.

### Monitored Metrics

- `strategy_score` ranges for fixed scoring samples.
- Liquidity penalty, risk penalty, and data-quality penalty direction.
- Alignment label sequence for fixed comparison samples.
- Summary total count, valid count, alignment counts, missing score counts, average scores, and average gap.

### Tests

- Added `tests/test_strategy_score_drift.py`.
- Covered drift ranges, stable alignment labels, stable aggregate summary metrics, source DataFrame immutability, no legacy/UI dependency, and operation-word safety.

### Next Step

- V1.4.5 enhanced trend and momentum factor handling while keeping results out of UI.

## 2026-05-28

### Target

- Complete V1.4.3 aggregate comparison summary phase.
- Add batch-level summaries for existing research-priority scores and internal `strategy_score`.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or add comparison summary logic to `legacy_app.py` or `ui/screening_ui.py`.

### Added Aggregate Summary

- `strategy/comparison.py` now exposes `summarize_score_alignment()`.
- The summary accepts a score DataFrame, a `compare_strategy_scores()` output dictionary, or a comparison list.
- Summary output includes total count, valid count, missing score counts, average original score, average strategy score, average score gap, alignment counts, alignment ratios, label-specific counts, summary text, and warnings.
- The helper is read-only and preserves input row order.

### Tests

- Added `tests/test_strategy_comparison_summary.py`.
- Covered empty input, single comparison, multi-row summaries, label counts, missing score counts, stable averages, ratio sanity checks, source DataFrame immutability, no legacy/UI dependency, and operation-word safety.

### Next Step

- V1.4.4 added fixed-sample drift checks for comparison summaries and strategy scores while keeping results internal.

## 2026-05-28

### Target

- Complete V1.4.2 internal score comparison phase.
- Add comparison helpers for existing research-priority scores and internal `strategy_score`.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or add comparison logic to `legacy_app.py` or `ui/screening_ui.py`.

### Added Score Comparison

- `strategy/comparison.py` compares original research-priority scores with `strategy_score`.
- Output fields include `original_score`, `strategy_score`, `score_gap`, `alignment_label`, `interpretation`, `research_priority_type`, and `warnings`.
- The helper is read-only and preserves input row order.

### Alignment Labels

- `high_consensus`: both score systems are high.
- `research_high_strategy_low`: original research-priority score is high while strategy score is low.
- `strategy_high_research_low`: strategy score is high while original research-priority score is low.
- `low_consensus`: both score systems are low.
- `insufficient_data`: at least one key score is missing.

### Tests

- Added `tests/test_strategy_comparison.py`.
- Extended module import coverage to include `strategy.comparison`.
- Covered empty input, missing original score, missing strategy score, all primary alignment labels, stable score gaps, no source DataFrame mutation, no legacy/UI dependency, and operation-word safety.

### Next Step

- V1.4.3 added aggregate comparison summaries while keeping results internal.

## 2026-05-28

### Target

- Complete V1.4.1 strategy score calibration phase.
- Add calibration and distribution tests for internal strategy scores.
- Do not add data sources, change stock pools, replace `core/scoring.py`, change Streamlit display, change existing screening sorting, or add strategy scoring to `legacy_app.py` or `ui/screening_ui.py`.

### Calibration Samples

- High-quality trend sample: stronger trend, active amount, complete fields, moderate volatility.
- Low-liquidity sample: low amount and low volume.
- Overheated-risk sample: large short-term increase and high volatility.
- Missing-data sample: missing key market fields.
- Neutral sample: ordinary factor profile with middle-range score expectations.

### Scoring Adjustment

- Refined `strategy/scoring.py` to read source amount and volume fields from DataFrame inputs.
- Low-liquidity samples now lower `liquidity_score` more directly.
- This adjustment is internal to `strategy/scoring.py` and does not affect existing application scoring.

### Tests

- Added `tests/test_strategy_scoring_calibration.py`.
- Added `tests/test_strategy_score_distribution.py`.
- Covered score direction, 0-100 bounds, row-order preservation, low-liquidity penalty, high-risk penalty, data-quality penalty, no source DataFrame mutation, and operation-word safety.

### Next Step

- V1.4.2 added side-by-side internal comparison between existing research-priority scores and strategy scores without changing page sorting or display.

## 2026-05-28

### Target

- Complete V1.4.0 independent strategy scoring phase.
- Add internal strategy-score functions under `strategy/` without replacing `core/scoring.py`.
- Do not add data sources, change stock pools, change Streamlit display, change existing screening sorting, or add strategy scoring to `legacy_app.py` or `ui/screening_ui.py`.

### Added Strategy Scoring

- `strategy/scoring.py` computes internal strategy scores from a screening-result DataFrame or existing diagnostics.
- Score output includes `trend_score`, `momentum_score`, `volume_price_score`, `liquidity_score`, `risk_penalty`, `data_quality_penalty`, and `strategy_score`.
- `strategy_score` is clamped to 0-100 and is only a research-priority auxiliary score.
- Risk and data-quality issues lower the internal strategy score but do not change existing application scoring.

### Factor Enhancements

- `strategy/factors.py` adds trend direction, volume-price, and data-quality factor helpers.
- Existing factor snapshot behavior remains compatible.

### Compatibility

- Existing `core/scoring.py` remains unchanged.
- Existing research-priority scoring, page display, and sorting remain unchanged.
- `legacy_app.py` and `ui/screening_ui.py` do not import `strategy.scoring`.

### Tests

- Added `tests/test_strategy_scoring.py`.
- Extended `tests/test_strategy_factors.py` for new pure factor helpers.
- Extended module import coverage to include `strategy.scoring`.
- Covered empty inputs, missing fields, stable typical scoring, high-risk penalty, data-quality penalty, no source DataFrame mutation, no legacy/UI dependency, and operation-word safety.

### Next Step

- V1.4.1 added score calibration fixtures and distribution checks while keeping strategy scores internal.

## 2026-05-28

### Target

- Complete V1.3.6 gated diagnostics panel helper phase.
- Add a feature-flagged rendering helper for future strategy diagnostics display.
- Do not add data sources, change stock pools, change `core/scoring.py`, change Streamlit display, change sorting logic, or call the helper from current pages.

### Added Gated Helper

- `ui/strategy_diagnostics_panel.py` accepts a strategy view-model.
- `render_strategy_diagnostics_panel()` checks `is_strategy_diagnostics_enabled()` before any rendering.
- When the default-off flag is disabled, the helper returns `rendered: False` and does not call Streamlit.
- The helper does not import `strategy.service` and does not build diagnostics itself.

### Compatibility

- Current Streamlit pages do not call `render_strategy_diagnostics_panel()`.
- Existing research-priority scoring, page display, and sorting remain unchanged.
- `legacy_app.py` and `ui/screening_ui.py` do not import `ui.strategy_diagnostics_panel`.

### Tests

- Added `tests/test_strategy_diagnostics_panel.py`.
- Extended module import coverage to include `ui.strategy_diagnostics_panel`.
- Covered default-off behavior, no Streamlit calls while disabled, no mutation of view-model input, no service dependency in the panel, no page dependency on the panel, and operation-word safety.

### Next Step

- V1.3.7 can add an inactive integration adapter or explicit UI contract for where the panel would be mounted, still keeping the feature flag off by default.

## 2026-05-28

### Target

- Complete V1.3.5 feature-flag boundary phase.
- Add default-off strategy diagnostics feature flags and non-rendering UI contract tests.
- Do not add data sources, change stock pools, change `core/scoring.py`, change Streamlit display, change sorting logic, or add strategy logic to `legacy_app.py` or `ui/screening_ui.py`.

### Added Feature Flags

- `config/feature_flags.py` defines strategy diagnostics display flags.
- `is_strategy_diagnostics_enabled()` returns `False` by default.
- `get_feature_flag_metadata()` returns `strategy_diagnostics_enabled: False`, `ui_rendering_enabled: False`, `ranking_changed: False`, `scoring_changed: False`, and `read_only: True`.

### Compatibility

- The feature flag is not wired into current screening rendering.
- Existing research-priority scoring, page display, and sorting remain unchanged.
- `legacy_app.py` and `ui/screening_ui.py` do not import `strategy.view_model` or `strategy.service`.

### Tests

- Added `tests/test_feature_flags.py`.
- Added `tests/test_strategy_ui_contract.py`.
- Extended module import coverage to include `config.feature_flags`.
- Covered default-off behavior, no UI dependency on strategy view-model/service, unchanged ranking/scoring metadata, and operation-word safety.

### Next Step

- V1.3.6 added the gated, non-invoked rendering helper and tests confirming it remains inactive while the flag is off.

## 2026-05-28

### Target

- Complete V1.3.4 strategy view-model phase.
- Add a read-only internal view-model that converts `strategy.service` output into future UI-friendly structures.
- Do not add data sources, change stock pools, change `core/scoring.py`, change Streamlit display, change sorting logic, or add strategy logic to `legacy_app.py` or `ui/screening_ui.py`.

### Added Strategy View-Model

- `strategy/view_model.py` consumes strategy service output.
- View-model output includes `cards`, `badges`, `sections`, `table_rows`, `empty_state`, and `metadata`.
- Metadata preserves read-only behavior and confirms UI, ranking, and scoring are unchanged.
- The view-model returns safe empty states for missing or invalid input.

### Compatibility

- The view-model is not wired into the current screening flow.
- Existing research-priority scoring, page display, and sorting remain unchanged.
- `legacy_app.py` and `ui/screening_ui.py` do not import `strategy.view_model`.

### Tests

- Added `tests/test_strategy_view_model.py`.
- Extended module import coverage to include `strategy.view_model`.
- Covered empty service output, missing fields, typical service output, no mutation of service output, non-dict input, and operation-word safety.

### Next Step

- V1.3.5 added the default-off feature flag boundary and non-rendering UI contract tests.

## 2026-05-28

### Target

- Complete V1.3.3 strategy service phase.
- Add a read-only internal service that combines `strategy.adapter` diagnostics and `strategy.report` summaries.
- Do not add data sources, change stock pools, change `core/scoring.py`, change Streamlit display, change sorting logic, or add strategy logic to `legacy_app.py`.

### Added Strategy Service

- `strategy/service.py` consumes an existing screening-result DataFrame.
- The service calls `build_strategy_diagnostics()` and `build_strategy_report()`.
- Service output includes `status`, `preset_name`, `diagnostics`, `report`, `metadata`, and `warnings`.
- Metadata explicitly records read-only behavior and confirms UI, ranking, and scoring are unchanged.

### Compatibility

- The service is not wired into the current screening flow.
- Existing research-priority scoring, page display, and sorting remain unchanged.
- `legacy_app.py` does not import `strategy.service`.

### Tests

- Added `tests/test_strategy_service.py`.
- Extended module import coverage to include `strategy.service`.
- Covered empty DataFrame, missing fields, typical screening rows, no mutation of the source DataFrame, non-DataFrame input, and operation-word safety.

### Next Step

- V1.3.4 added the read-only view-model layer without page integration.

## 2026-05-28

### Target

- Complete V1.3.2 strategy report phase.
- Add a read-only report builder that summarizes `strategy.adapter` diagnostics.
- Do not add data sources, change stock pools, change `core/scoring.py`, change Streamlit display, change sorting logic, or add strategy logic to `legacy_app.py`.

### Added Strategy Report

- `strategy/report.py` consumes adapter diagnostics and returns structured internal summaries.
- Report output includes `preset_name`, `summary_text`, `factor_summary`, `filter_summary`, `risk_summary`, `data_quality_summary`, and `notes`.
- Text focuses on observations, prompts, risks, data quality, and research-priority context.
- Empty diagnostics, missing fields, and invalid structures return safe summaries.

### Compatibility

- The report builder is not wired into the current screening flow.
- Existing research-priority scoring, page display, and sorting remain unchanged.
- `legacy_app.py` does not import `strategy.report`.

### Tests

- Added `tests/test_strategy_report.py`.
- Extended module import coverage to include `strategy.report`.
- Covered empty diagnostics, missing fields, typical adapter output, no mutation of the adapter output, invalid input, and operation-word safety.

### Next Step

- V1.3.3 added the read-only internal strategy diagnostics service without UI integration.

## 2026-05-28

### Target

- Complete V1.3.1 strategy adapter phase.
- Add a read-only adapter that converts existing screening-result DataFrames into strategy diagnostics.
- Do not add data sources, change stock pools, change `core/scoring.py`, change Streamlit display, change sorting logic, or add strategy logic to `legacy_app.py`.

### Added Strategy Adapter

- `strategy/adapter.py` maps common screening-result fields into diagnostic inputs.
- Field aliases include latest price, percentage change, volume, amount, turnover, sector, industry, score, volatility, drawdown, volume ratio, valid days, and data quality.
- Adapter output includes `factor_scores`, `filter_flags`, `risk_tags`, `risk_notes`, `preset_name`, and `diagnostics_summary`.
- The adapter copies the input DataFrame and does not mutate the original object.

### Compatibility

- The adapter is not wired into the current screening flow.
- Existing research-priority scoring, page display, and sorting remain unchanged.
- `legacy_app.py` does not import `strategy.adapter`.

### Tests

- Added `tests/test_strategy_adapter.py`.
- Extended module import coverage to include `strategy.adapter`.
- Covered empty DataFrame, missing fields, typical screening rows, alias inference, no mutation of the source DataFrame, and operation-word safety.

### Next Step

- V1.3.2 added the read-only report builder while keeping existing UI and ranking unchanged.

## 2026-05-28

### Target

- Complete V1.3.0 strategy quantification phase 1.
- Add an independent `strategy/` framework for research-priority factors, filters, risk labels, and presets.
- Do not add data sources, change stock pools, change `core/scoring.py`, change page display, change sorting logic, or add strategy logic to `legacy_app.py`.

### Added Strategy Modules

- `strategy/factors.py`: pure trend, momentum, volatility, and volume factor helpers.
- `strategy/filters.py`: pure missing-field, minimum-row, minimum-price, turnover, and abnormal-move checks.
- `strategy/risk.py`: risk-label helpers that return tags and explanations only.
- `strategy/presets.py`: preset configuration structures for research-priority, stable-observation, and high-elasticity observation workflows.

### Compatibility

- The new strategy framework is not wired into the current screening flow.
- Existing research-priority scoring and composite scoring remain unchanged.
- `legacy_app.py` does not import `strategy/`.
- Streamlit page display and sorting behavior are unchanged.

### Tests

- Added `tests/test_strategy_factors.py`.
- Added `tests/test_strategy_filters.py`.
- Added `tests/test_strategy_risk.py`.
- Extended module import coverage to include `strategy/`.
- Extended forbidden-phrase runtime scanning to include `strategy/`.

### Next Step

- V1.3.1 added the read-only adapter while keeping the existing ranking and page output unchanged.

## 2026-05-28

### Target

- Complete V1.2.9 architecture wrap-up.
- Clarify the entrypoint boundaries between `app.py`, `ui/screening_ui.py`, and `legacy_app.py`.
- Do not add business features, data sources, scoring changes, stock-pool changes, UI behavior changes, real network fetch migration, or AkShare / BaoStock / yfinance call-flow changes.

### Boundary Cleanup

- `app.py` now owns Streamlit page setup and page navigation only.
- `legacy_app.py` exposes `render_legacy_workbench()` as the explicit old workbench compatibility wrapper.
- `ui/screening_ui.py` now imports `legacy_app.py` as `legacy_workbench` to make the temporary screening dependency visible.
- `legacy_app.py` declares `LEGACY_COMPATIBILITY_SURFACE` for the currently supported compatibility paths.

### Still Kept In `legacy_app.py`

- Old research workbench rendering.
- Legacy screening section rendering.
- Real network-adjacent fetch orchestration.
- AkShare / BaoStock / yfinance call flows.
- Backtest, watchlist, comparison, and remaining UI-bound helper flows.

### Tests

- Updated `tests/test_module_imports.py` with a V1.2.9 boundary test for version alignment and compatibility-surface visibility.

### Pending Migration List

- Do not move `fetch_screening_price_data` or other real fetch orchestration until narrower mocked tests cover the specific split.
- Do not move the old workbench renderer as a single large migration; split only small UI sections when behavior can be checked.
- `ui/screening_ui.py` still calls the legacy screening renderer by design for this release.

### Next Step

- V1.3 may proceed only if the next scope preserves the safety boundary and avoids direct trading conclusions. If V1.3 means strategy quantification, first define it as research-priority and risk-analysis methodology rather than trading advice.

## 2026-05-27

### Target

- Complete V1.2.8 architecture cleanup.
- Add mocked tests around real data-fetch boundaries before moving any network-adjacent logic.
- Do not add business features, data sources, scoring changes, stock-pool changes, data-source order changes, or UI changes.

### Boundary Coverage Added

- `fetch_a_share_fundamental_data` empty-info and exception paths.
- `get_fundamental_data` AkShare failure to built-in sample fallback.
- `get_fundamental_data` non-A-share safe record path.
- `fetch_screening_price_data` AkShare empty result falling back to BaoStock success.
- `fetch_screening_price_data` all A-share sources returning empty data.
- `fetch_screening_price_data` missing Close-column protection.

### Compatibility

- `legacy_app.py` remains the compatibility layer and still carries the real network fetch implementations.
- `data/market_data.py` and `data/fundamental_data.py` continue to expose lazy wrappers for network-adjacent functions.
- The AkShare -> BaoStock -> yfinance fallback order is unchanged.

### Tests

- Added `tests/test_data_fetch_boundaries.py` using monkeypatch-based mocks only.
- Tests do not call real AkShare, BaoStock, or yfinance network interfaces.

### Pending Migration List

- Real network data fetch implementations still live in `legacy_app.py`.
- `fetch_screening_price_data` is still a large legacy orchestration function and should only be split after additional mocked tests.
- `ui/screening_ui.py` still calls the legacy screening renderer.

### Next Step

- V1.2.9 completed entrypoint boundary cleanup before any further network-adjacent migration.

## 2026-05-27

### Target

- Complete V1.2.7 architecture cleanup.
- Migrate one small low-risk fundamental-data helper batch from `legacy_app.py`.
- Do not add business features, data sources, scoring changes, stock-pool changes, or data-source order changes.

### Migrated From `legacy_app.py`

- `clean_metric_value` moved to `data/fundamental_data.py`.
- `build_fundamental_record` moved to `data/fundamental_data.py`.
- `get_fundamental_sample_data` moved to `data/fundamental_data.py`.

### Compatibility

- `legacy_app.py` imports the migrated helpers from `data.fundamental_data`.
- `data/fundamental_data.py` keeps lazy wrappers for real fundamental-data fetch functions that still live in `legacy_app.py`.
- No data-source order or fallback behavior changed.

### Tests

- Added fundamental-data tests for field completion, missing-field defaults, built-in sample lookup, suffix inference, numeric cleaning, invalid values, and legacy compatibility paths.

### Pending Migration List

- Real network data fetch implementations still live in `legacy_app.py`.
- `ui/screening_ui.py` still calls the legacy screening renderer.
- Other legacy workbench summaries and UI-bound helpers remain in `legacy_app.py`.

### Next Step

- V1.2.8 added mocked data-fetch boundary coverage; the next batch can migrate only narrowly scoped helper logic.

## 2026-05-27

### Target

- Complete V1.2.6 architecture cleanup.
- Migrate one small low-risk market-data helper batch from `legacy_app.py`.
- Do not add business features, data sources, scoring changes, stock-pool changes, or data-source order changes.

### Migrated From `legacy_app.py`

- `normalize_yfinance_data` moved to `data/market_data.py`.
- `normalize_hk_symbol_for_akshare` moved to `data/market_data.py`.
- `normalize_a_share_symbol_for_akshare` moved to `data/market_data.py`.
- `infer_a_share_yfinance_suffix` moved to `data/market_data.py`.
- `normalize_a_share_symbol_for_yfinance` moved to `data/market_data.py`.
- `convert_a_share_to_yfinance_ticker` moved to `data/market_data.py`.
- `convert_a_share_to_baostock_code` moved to `data/market_data.py`.
- `get_screening_fallback_source` moved to `data/market_data.py`.
- `normalize_price_dataframe` moved to `data/market_data.py`.
- `keep_recent_rows` moved to `data/market_data.py`.

### Compatibility

- `legacy_app.py` imports the migrated helpers from `data.market_data`.
- `data/market_data.py` keeps lazy wrappers for network fetch functions that still live in `legacy_app.py`.
- The AkShare -> BaoStock -> yfinance fallback order is unchanged.

### Tests

- Added market-data tests for symbol normalization, ticker conversion, price DataFrame normalization, empty inputs, MultiIndex columns, recent-row trimming, and legacy compatibility paths.

### Pending Migration List

- Real network data fetch implementations still live in `legacy_app.py`.
- `data/fundamental_data.py` now owns basic helper functions; real fetch functions remain lazy wrappers to `legacy_app.py`.
- `ui/screening_ui.py` still calls the legacy screening renderer.
- Other legacy workbench summaries and UI-bound helpers remain in `legacy_app.py`.

### Next Step

- V1.2.7 migrated the fundamental-data helper batch; the next batch can isolate data-fetch boundaries with focused mocked tests.

## 2026-05-27

### Target

- Complete V1.2.5 architecture cleanup.
- Migrate one small low-risk explanation text pure logic batch from `legacy_app.py`.
- Do not add business features, data sources, scoring changes, stock-pool changes, or data-source order changes.

### Migrated From `legacy_app.py`

- `generate_selection_reasons` moved to `core/explanations.py`.
- `generate_screening_risk_warnings` moved to `core/explanations.py`.
- `generate_screening_summary` moved to `core/explanations.py`.
- `generate_fundamental_summary` moved to `core/explanations.py`.
- `join_explanation_items` moved to `core/explanations.py`.

### Compatibility

- `legacy_app.py` imports the migrated explanation functions from `core.explanations`.
- Existing call sites can still use the same functions through `legacy_app.py`.

### Tests

- Added explanation tests for direct core imports, legacy compatibility paths, typical inputs, empty inputs, missing fields, and invalid inputs.
- Added an import-boundary assertion that `core/explanations.py` no longer imports `legacy_app.py`.

### Pending Migration List

- `data/fundamental_data.py` still re-exports data functions from `legacy_app.py`; network fetch implementations in `data/market_data.py` remain lazy wrappers to `legacy_app.py`.
- `ui/screening_ui.py` still calls the legacy screening renderer.
- Other legacy workbench summaries and UI-bound helpers remain in `legacy_app.py`.

### Next Step

- V1.2.6 migrated the market-data helper batch; the next batch can continue data-boundary cleanup.

## 2026-05-27

### Target

- Complete V1.2.4 architecture cleanup.
- Migrate one small low-risk sector-strength pure logic batch from `legacy_app.py`.
- Do not add business features, data sources, scoring changes, stock-pool changes, or data-source order changes.

### Migrated From `legacy_app.py`

- `generate_sector_strength_summary` moved to `core/sector_strength.py`.
- `generate_sector_strength_text` moved to `core/sector_strength.py`.

### Compatibility

- `legacy_app.py` imports the migrated sector-strength functions from `core.sector_strength`.
- Existing call sites can still use `legacy_app.generate_sector_strength_summary` and `legacy_app.generate_sector_strength_text`.

### Tests

- Added sector-strength tests for the direct core path, the legacy compatibility path, empty data, and missing fields.
- Added an import-boundary assertion that `core/sector_strength.py` no longer imports `legacy_app.py`.

### Pending Migration List

- `data/market_data.py` and `data/fundamental_data.py` still re-export data functions from `legacy_app.py`.
- `ui/screening_ui.py` still calls the legacy screening renderer.

### Next Step

- V1.2.5 migrated the explanation-text pure logic batch; the next batch can target additional pure helpers or data-boundary cleanup.

## 2026-05-27

### Target

- Complete V1.2.3 architecture cleanup.
- Migrate one small low-risk `core` pure logic batch from `legacy_app.py`.
- Do not add business features, data sources, scoring changes, stock-pool changes, or data-source order changes.

### Migrated From `legacy_app.py`

- `calculate_research_priority_score` moved to `core/scoring.py`.
- `calculate_fundamental_quality_score` moved to `core/scoring.py`.
- `calculate_composite_research_score` moved to `core/scoring.py`.
- `FUNDAMENTAL_FIELDS` moved to `core/scoring.py`.

### Compatibility

- `legacy_app.py` imports the migrated scoring functions from `core.scoring`.
- Existing call sites can still use `legacy_app.calculate_research_priority_score`, `legacy_app.calculate_fundamental_quality_score`, and `legacy_app.calculate_composite_research_score`.

### Tests

- Added scoring tests for typical input, empty or invalid input, and legacy compatibility path.
- Existing module import, forbidden phrase, screening contract, core metric, and backtest tests remain active.

### Pending Migration List

- `data/market_data.py` and `data/fundamental_data.py` still re-export data functions from `legacy_app.py`.
- `ui/screening_ui.py` still calls the legacy screening renderer.

### Next Step

- V1.2.4 migrated the sector-strength pure logic batch; the next batch can target explanation-text pure functions.

## 2026-05-27

### Target

- Complete V1.2.2 architecture cleanup.
- Start reducing `legacy_app.py` responsibilities in small, low-risk batches.
- Do not add business features, data sources, scoring changes, stock-pool changes, or data-source order changes.

### Migrated From `legacy_app.py`

- A-share screening pool constants and default screening universes moved to `config/stock_pools.py`.
- A-share stock-name map and display-name helper moved to `config/stock_names.py`.
- A-share industry / sector / theme map and sector-field helper moved to `config/sector_mapping.py`.
- Built-in sample fundamental data moved to `config/fundamental_samples.py`.

### Compatibility

- `legacy_app.py` remains the compatibility layer and imports the migrated configuration.
- Existing call sites can still use the same names through `legacy_app.py`.
- `app.py` remains the Streamlit entrypoint.

### Tests

- Added a test assertion that `config` modules no longer import `legacy_app.py`.
- Existing module import, forbidden phrase, screening contract, core metric, and backtest tests remain active.

### Pending Migration List

- `core/scoring.py` still re-exports scoring functions from `legacy_app.py`.
- `data/market_data.py` and `data/fundamental_data.py` still re-export data functions from `legacy_app.py`.
- `ui/screening_ui.py` still calls the legacy screening renderer.

### Next Step

- V1.2.3 should migrate one small `core/` batch after adding focused tests for the selected functions.

## 2026-05-27

### Target

- Complete V1.2.1 stability repair after the V1.2 modular refactor review.
- Keep the release limited to stability, documentation, and tests.
- Do not add business features, data sources, scoring changes, stock-pool changes, or data-source order changes.

### Changes

- Clarified `legacy_app.py` as a compatibility layer / legacy core logic carrier.
- Unified README and ROADMAP version language around V1.2.1.
- Weakened the duplicate legacy workbench screening entry with a compatibility notice.
- Added minimum tests for module imports, forbidden phrases, and screening field contracts.
- Added cache-risk wording to the screening page: cache improves speed but does not guarantee real-time data, and abnormal results can be retried after clearing cache.

### Remaining Issues

- `legacy_app.py` still carries part of the core implementation.
- New modules currently provide stable boundaries, and more function bodies should be migrated gradually.
- Browser-side manual regression should still be done before larger feature work.

### Next Step

- V1.2.2 should continue migrating core functions from `legacy_app.py` into `config/`, `data/`, `core/`, and `ui/` in small batches.
- If entering V1.3 feature work, add focused tests first for the touched workflow.

## 2026-05-26

### Target

- Complete V1.2: project structure split and modular refactor.
- Only adjust code organization boundaries; do not add features, add data sources, change scoring rules, or change the safety boundary.
- Keep `streamlit run app.py` as the startup command.

### Modified Files

- `app.py`
- `legacy_app.py`
- `config/__init__.py`
- `config/stock_pools.py`
- `config/stock_names.py`
- `config/sector_mapping.py`
- `config/fundamental_samples.py`
- `data/__init__.py`
- `data/market_data.py`
- `data/fundamental_data.py`
- `core/__init__.py`
- `core/metrics.py`
- `core/scoring.py`
- `core/explanations.py`
- `core/sector_strength.py`
- `ui/__init__.py`
- `ui/screening_ui.py`
- `tests/conftest.py`
- `README.md`
- `docs/ROADMAP.md`
- `docs/DEV_LOG.md`

### Main Changes

- Refactored `app.py` into a lightweight Streamlit entrypoint for page navigation and dispatch.
- Added `ui.screening_ui.render_screening_page()` as the automatic research-object screening page entrypoint.
- Added stable module boundaries under `config/`, `data/`, `core/`, and `ui/`.
- Preserved the legacy workbench in `legacy_app.py` to keep single-stock analysis, comparison, backtesting, and the existing screening workflow available.
- Added `tests/conftest.py` so direct `pytest` runs can import the project root.

### Test Results

- `python -m py_compile app.py config/stock_pools.py config/stock_names.py config/sector_mapping.py config/fundamental_samples.py data/market_data.py data/fundamental_data.py core/metrics.py core/scoring.py core/explanations.py core/sector_strength.py ui/screening_ui.py legacy_app.py tests/conftest.py` passed.
- `pytest` passed: 6 passed.
- `$env:PYTHONPATH='.'; pytest` passed: 6 passed.
- Short Streamlit startup check passed on `http://localhost:8503`.
- Forbidden wording scan returned no matches for the checked source and docs set.

### Remaining Issues

- The new modules currently provide stable boundaries; much of the concrete implementation still lives in `legacy_app.py` and can be moved gradually.
- Full browser-side manual regression has not been completed.
- Free data-source availability still depends on network conditions, request limits, and upstream interface stability.

### Next Step

- Continue moving implementation bodies from `legacy_app.py` into the matching `config/`, `data/`, `core/`, and `ui/` modules in small steps.
- Future features should enter the event catalyst module, trading-discipline module, or formal data-source integration while preserving the safety boundary.

## 2026-05-26

### 本次目标

- 完成 V1.1：自动研究对象筛选模块性能优化与缓存机制。
- 不新增新功能或新数据源，不修改评分规则，不改变投资安全边界。

### 修改文件

- `app.py`
- `README.md`
- `docs/ROADMAP.md`
- `docs/DEV_LOG.md`

### 主要修改

- 使用 `st.cache_data` 缓存单只股票筛选结果，TTL 为 30 分钟。
- 使用 `st.cache_data` 缓存基本面数据，TTL 为 1 小时。
- 新增运行模式：快速模式和完整模式。
- 快速模式默认启用，跳过基本面明细、板块强度统计、完整诊断和详细筛选总结。
- 完整模式保留基本面字段、板块强度统计、筛选总结、成功获取明细和失败诊断。
- 新增处理进度条和当前处理标的提示。
- 默认最大处理数量调整为 10，并保留 10、20、30、50 选项。
- 新增“清除缓存并重新获取数据”按钮。
- 主表字段收敛为核心结果，完整指标和基本面详细字段放入折叠区。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。
- 禁用表达精确搜索无命中。
- 本地快速模式检查通过：快速模式不获取基本面明细，仍可生成综合研究观察评分。
- 待补充：手动测试快速模式和完整模式。

### 遗留问题

- 免费数据源本身的网络延迟、限流和接口稳定性无法完全通过缓存解决。
- 首次请求仍取决于 AkShare、BaoStock 和 yfinance 的响应速度。
- 当前仍为同步批量请求，未引入复杂异步框架。

### 下一步

- 可进入事件催化、交易纪律模块或项目结构拆分。
- 如继续优化性能，可考虑更细粒度缓存底层行情源、持久化本地缓存或拆分筛选服务。

## 2026-05-26

### 本次目标

- 完成 V1.0：A股基本面质量筛选初版。
- 不接入真实交易账户，不执行真实交易操作，不输出具体操作建议，不改变现有研究优先级评分规则。

### 修改文件

- `app.py`
- `README.md`
- `docs/SCREENING_SPEC.md`
- `docs/ROADMAP.md`
- `docs/DEV_LOG.md`

### 主要修改

- 新增 `FUNDAMENTAL_SAMPLE_DATA` 内置示例基本面数据。
- 新增基本面数据统一获取链路：优先 AkShare，失败后使用内置示例数据，无数据则显示数据暂缺。
- 新增基本面字段展示：总市值、PE_TTM、PB、ROE、营收同比增长率、归母净利润同比增长率、毛利率、净利率、资产负债率、股息率。
- 新增 `calculate_fundamental_quality_score(fundamental_data)`。
- 新增综合研究观察评分，结合研究优先级评分和基本面质量评分。
- Top N 研究候选池表格新增基本面质量评分、综合研究观察评分、基本面数据源和基本面观察摘要。
- 风险提示和筛选总结增加基本面数据来源、字段缺失和内置示例数据提示。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。
- 禁用表达精确搜索无命中。
- 本地函数检查通过：`600519.SH` 可返回内置示例基本面数据，基本面质量评分和综合研究观察评分可正常计算。
- 待补充：手动测试 A股不同股票池的基本面质量筛选。

### 遗留问题

- AkShare 基本面字段覆盖不稳定，部分字段仍依赖内置示例数据兜底。
- 内置示例基本面数据仅用于学习和原型演示，不代表最新真实财务数据。
- 港股和美股基本面筛选暂未启用。

### 下一步

- 评估接入 Tushare Pro 或其他正式财务数据源。
- 接入公告数据和事件催化模块。
- 在基本面质量之后推进交易纪律模块。

## 2026-05-26

### 本次目标

- 完成 V0.9.6：A股行业 / 板块 / 主题标签与板块强度初版。
- 不新增复杂数据源，不接入 OpenAI API，不接入真实交易账户，不执行真实交易操作，不改变现有研究优先级评分规则。

### 修改文件

- `app.py`
- `README.md`
- `docs/SCREENING_SPEC.md`
- `docs/ROADMAP.md`
- `docs/DEV_LOG.md`

### 主要修改

- 新增 A股行业 / 板块 / 主题标签内置映射。
- 新增 `get_stock_sector_info(ticker, market)`，返回行业、板块和主题标签。
- 解析表、Top N 研究候选池、成功获取明细、低优先级分层、无法评分或未纳入候选池、获取失败表增加行业、板块和主题标签字段。
- 新增 `generate_sector_strength_summary(result_df, all_scored_df=None)`，按当前股票池已评分样本聚合板块强度初步统计。
- 新增 `generate_sector_strength_text(sector_df)`，输出本地规则化板块观察解释。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。
- 禁用表达精确搜索无命中。
- 本地函数检查通过：`688981.SH` 返回半导体 / 科技成长 / 晶圆代工;国产替代，板块强度聚合可正常输出。
- `streamlit run app.py --server.headless true --server.port 8501` 已启动，`http://localhost:8501` 可访问。
- 待补充：手动测试 A股不同股票池的板块强度初步统计。

### 遗留问题

- 板块统计仅基于当前股票池样本，不代表全市场板块强弱。
- 暂未接入外部板块指数或完整行业分类数据源。
- 尚未纳入基本面质量和事件催化。

### 下一步

- 进入基本面质量筛选，补充盈利能力、现金流、估值和财务质量观察。
- 或先补充更完整板块数据源和板块指数，用于更稳定的板块比较。

## 2026-05-26

### 本次目标

- 完成 V0.9.5：A股研究股票池体系升级与股票中文名称展示。
- 不新增评分规则，不新增复杂数据源，不接入 OpenAI API，不接入真实交易账户，不执行真实交易操作。

### 修改文件

- `app.py`
- `README.md`
- `docs/SCREENING_SPEC.md`
- `docs/ROADMAP.md`
- `docs/DEV_LOG.md`

### 主要修改

- 新增 5 类 A股研究股票池：核心资产观察池、科技成长观察池、消费医药观察池、金融地产周期观察池、高弹性主题观察池。
- 新增 A股股票中文名称内置映射表和 `get_stock_display_name(ticker, market)`。
- 解析表、Top N 研究候选池、成功获取明细、低优先级分层、无法评分或未纳入候选池、获取失败表增加股票名称字段。
- 新增最大处理数量控件，支持 10、20、30、50，默认 20。
- 页面新增股票池信息展示，包括股票池名称、定位、总数、本次处理数量和风险提示。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。
- 本地函数检查通过：A股科技成长观察池返回 20 只，`300750.SZ` 名称返回“宁德时代”。
- `http://localhost:8501` 可访问。
- 待补充：手动测试 A股不同股票池。

### 遗留问题

- 港股和美股名称暂未扩展，当前仍以代码展示为主。
- A股名称来自内置映射表，覆盖范围有限。
- 尚未加入板块强度、基本面质量和事件催化。

### 下一步

- 进入板块强度分析，按行业或主题聚合候选对象表现。
- 后续补充更完整的基础信息数据源，用于名称、行业和板块字段。
- 在板块强度之后继续推进基本面质量、事件催化和交易纪律模块。

## 2026-05-26

### 本次目标

- 完成 V0.9.4：自动研究对象筛选模块新增解释层、入选理由、风险提示和筛选总结。
- 继续保持本地规则生成，不接入 OpenAI API，不接入真实交易账户，不执行真实交易操作。

### 修改文件

- `app.py`
- `README.md`
- `docs/SCREENING_SPEC.md`
- `docs/DEV_LOG.md`

### 主要修改

- 新增 `generate_selection_reasons(metrics)`，基于均线结构、动量表现、成交量变化和数据质量生成 2-4 条入选理由。
- 新增 `generate_screening_risk_warnings(metrics)`，基于涨幅、最大回撤、年化波动率、有效交易日、成交量数据和备用数据源生成风险提示。
- 新增 `generate_screening_summary(result_df, failed_items=None, insufficient_items=None)`，汇总覆盖数量、Top 候选池共性、主要风险特征和下一步研究方向。
- Top N 研究候选池表格新增“入选理由”和“风险提示”字段。
- 无法评分或未纳入候选池的股票单独折叠展示，并说明未纳入原因。
- 页面版本说明更新为 V0.9.4，并保留“不构成投资建议”的边界。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。
- `http://localhost:8501` 可访问。
- 待补充：`streamlit run app.py` 后手动测试 A股默认股票池。

### 遗留问题

- 尚未纳入板块强度、基本面质量和事件催化。
- 尚未加入交易纪律模块。
- 当前解释层仍偏技术面和量价维度，需要结合公司、行业、财报和公告继续验证。

### 下一步

- 增加板块强度字段和行业相对表现解释。
- 增加基本面质量检查，例如营收、利润率、现金流和估值口径。
- 增加消息催化和公告核查流程。
- 增加交易纪律模块，用于记录研究流程、风险约束和复盘规则。

## 2026-05-26

### 本次目标

- 完成 V0.9.3：自动研究对象筛选模块新增量价指标计算、研究优先级评分和 Top N 排序展示。
- 不接入 OpenAI API，不接入真实交易账户，不执行真实交易操作，仅输出研究候选池和进一步研究对象排序。

### 修改文件

- `app.py`
- `README.md`
- `docs/SCREENING_SPEC.md`
- `docs/DEV_LOG.md`
- `docs/ROADMAP.md`

### 主要修改

- 新增 `calculate_screening_metrics(price_df)`，计算最新价格、近 5/20/60 日涨跌幅、MA20、MA60、均线结构、最近 5/20 日均量、成交量放大倍数、年化波动率、最大回撤和有效交易日数量。
- 新增 `calculate_research_priority_score(metrics)`，按可解释量价规则生成“研究优先级评分”。
- 自动研究对象筛选结果新增 Top N 候选结果表，并按研究优先级评分从高到低排序。
- 无法评分或指标不足的股票进入单独折叠区，避免单只股票异常影响其他候选对象。
- 页面说明更新为 V0.9.3，并保留“不构成投资建议”的边界。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。
- 待补充：`streamlit run app.py` 后手动测试 A股默认股票池。

### 遗留问题

- 尚未生成入选理由、风险提示和筛选总结。
- 尚未纳入板块强度、基本面质量和事件催化。
- 评分偏技术面和量价维度，不能替代财报、估值、行业和事件研究。

### 下一步

- 基于已计算指标生成可追溯的入选理由。
- 基于涨幅、波动率、最大回撤、数据质量和数据源状态生成风险提示。
- 增加筛选总结，并逐步接入板块强度、基本面质量和消息催化。

## 2026-05-25

### 本次目标

- 完成 V0.9.2c：A股自动研究对象筛选模块新增 BaoStock 备用数据源。
- 暂不进入研究优先级评分、入选理由、风险提示或 OpenAI API 接入，只优化 A股批量行情数据源稳定性。

### 修改文件

- `app.py`
- `requirements.txt`（确认已包含 `baostock>=0.8.9`）
- `README.md`
- `docs/DEV_LOG.md`
- `docs/ROADMAP.md`

### 主要修改

- A股筛选模块数据源顺序调整为 `AkShare → BaoStock → yfinance`。
- 新增 BaoStock A股代码转换与历史日线获取链路，标准化为 `Date`、`Open`、`High`、`Low`、`Close`、`Volume`。
- BaoStock 请求使用 `login` / `logout`，异常情况下也会尝试 `logout`。
- 成功获取表增加主数据源、备用数据源和数据源说明。
- 失败表增加尝试过的数据源、失败原因摘要、AkShare 错误摘要、BaoStock 错误摘要和 yfinance 错误摘要。
- 页面增加 A股多数据源降级说明，并保留“不构成投资建议”的边界。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。
- 尚未手动启动 `streamlit run app.py` 测试 A股默认股票池。

### 遗留问题

- 免费数据源仍可能受网络环境、代理/VPN、接口限流、字段变化和节假日影响。
- BaoStock 适合历史行情学习和研究，不适合实盘级实时交易。
- yfinance 的 A股覆盖度和时效性可能弱于 A股本地数据源。

### 下一步

- 使用 A股默认股票池和少量自定义代码测试三源降级链路。
- 如仍大量失败，分别单独测试 AkShare、BaoStock 登录和 yfinance A股后缀代码。
- 后续可评估 Tushare Pro 可选接入，但需要 token 和权限配置。

## 2026-05-25

### 本次目标

- 完成 V0.9.2b：增强 A股数据源降级、请求节流与网络诊断。

### 修改文件

- `app.py`
- `README.md`
- `docs/DEV_LOG.md`

### 主要修改

- A股筛选模块在 AkShare 失败后尝试 yfinance 后备代码。
- A股批量请求加入轻量节流。
- 增加网络错误识别，覆盖连接中断、远程关闭、连接重置、超时、代理/VPN 等常见异常线索。
- 失败表新增网络诊断字段。
- 未加入研究优先级评分、入选理由或风险提示。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。

### 遗留问题

- AkShare 和 yfinance 免费数据源仍可能延迟、缺失或被网络环境影响。
- yfinance 的 A股后备数据覆盖度和时效性可能弱于 AkShare。
- 尚未进入 V0.9.3 指标计算和研究优先级评分。

### 下一步

- 继续测试 A股默认股票池和少量自定义代码，确认主备数据源状态和失败诊断是否清晰。

## 2026-05-25

### 本次目标

- 修复 V0.9.2 自动研究对象筛选模块中 A股批量行情获取稳定性和诊断信息不足的问题。

### 修改文件

- `app.py`
- `README.md`
- `docs/DEV_LOG.md`

### 主要修改

- A股 AkShare 请求前统一转换为 6 位数字代码。
- A股 AkShare 自动尝试 `adjust=""`、`adjust="qfq"`、`adjust="hfq"`。
- A股筛选数据请求最近约 240 个自然日，并保留最近 120 个有效交易日。
- 获取失败表增加实际查询代码、数据源、尝试参数、失败阶段、失败原因。
- A股失败较多时给出少量代码调试提示。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。

### 遗留问题

- AkShare 上游接口、网络环境和字段变化仍可能导致部分代码失败。
- 尚未进入指标计算、研究优先级评分、入选理由和风险提示。

### 下一步

- 用 A股默认股票池和少量单代码组合测试批量获取稳定性。

## 2026-05-25

### 本次目标

- 建立 V0.9.2 自动研究对象筛选模块的批量行情数据获取能力。

### 修改文件

- `app.py`
- `README.md`
- `docs/SCREENING_SPEC.md`
- `docs/DEV_LOG.md`

### 主要修改

- 新增单只候选对象行情获取包装函数。
- 新增股票池逐只行情获取汇总函数。
- 展示成功获取、获取失败和数据不足的候选对象。
- 展示实际数据源、备用源使用状态、最新交易日、有效交易日数量和基础数据质量结论。
- 保留 V0.9.1 股票池解析功能。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。

### 遗留问题

- 尚未实现指标计算。
- 尚未实现研究优先级评分。
- 尚未生成入选理由、风险提示和筛选总结。

### 下一步

- 加入批量指标计算，并继续保留“不构成投资建议”的边界。

## 2026-05-25

### 本次目标

- 建立 V0.9.1 自动研究对象筛选模块骨架。

### 修改文件

- `app.py`
- `README.md`
- `docs/SCREENING_SPEC.md`
- `docs/DEV_LOG.md`

### 主要修改

- 新增默认示例股票池。
- 新增自定义股票池输入入口。
- 新增股票代码解析和标准化逻辑。
- 新增解析结果表格展示。
- 明确当前版本不做批量行情获取、指标计算、排序、入选理由和风险提示。

### 测试结果

- `python -m py_compile app.py` 通过。
- `python -m pytest -q` 通过，6 passed。

### 遗留问题

- 尚未接入批量行情获取。
- 尚未实现指标计算和研究优先级评分。
- 尚未生成入选理由和风险提示。

### 下一步

- 在下一版本加入批量行情获取和数据源状态记录。

## YYYY-MM-DD

### 本次目标

-

### 修改文件

-

### 主要修改

-

### 测试结果

-

### 遗留问题

-

### 下一步

-
