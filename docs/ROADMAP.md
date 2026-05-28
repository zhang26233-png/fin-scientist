# Roadmap

## 后续重点方向

- A股研究能力作为后续重点方向，优先增强 A股数据获取稳定性、字段口径说明和数据质量检查。
- 港股和美股继续作为兼容市场保留，避免破坏现有单股分析、多股票对比、自选股、新闻与事件分析、策略回测等功能。
- 后续可选接入 Tushare Pro，但需要 token、权限和配额配置，不作为当前默认链路。
- 保留安全边界：所有结果仅用于学习和研究，不构成投资建议，不接入真实交易账户，不执行自动买卖流程。

## v0.6 单股行情查询与基础研究工作台

- 建立单股票行情查询流程。
- 展示基础价格指标、均线指标和风险指标。
- 输出本地规则化研究摘要。
- 保留“不构成投资建议”的安全边界。

## v0.7 数据质量报告与数据源可靠性

- 明确展示行情数据来源、市场、币种和最近交易日。
- 增加 Data Quality Report，提示缺失值、重复日期和异常涨跌幅。
- 加强免费数据源延迟、缺失和口径差异提示。
- 为后续筛选模块提供更可靠的数据基础。
- A股自动研究对象筛选优先采用 `AkShare → BaoStock → yfinance` 的多数据源降级链路。

## v0.8 自动研究候选池

- 建立默认股票池和自定义股票池输入。
- 基于可解释指标生成研究候选池。
- 输出研究优先级评分、入选理由和风险提示。
- 避免使用会被误解为操作建议的评分名称或交易结论。
- 在进入研究优先级评分前，先稳定 A股批量行情获取、失败诊断和数据质量提示。
- V0.9.5 已完成 A股研究股票池体系升级。
- V0.9.5 已完成股票中文名称展示。

## v0.9 板块强度分析

- 已进入板块强度分析初版。
- V0.9.6 已完成行业 / 板块标签与板块强度初版。
- 增加板块或行业维度的相对表现观察。
- 汇总板块内代表性标的的趋势和波动。
- 输出板块强弱变化的学习型解释。
- 提示样本数量和数据源限制。
- 下一步建议进入基本面质量筛选或更完整板块数据源。

## v1.0 基本面筛选

- V1.0 已完成基本面质量筛选初版。
- 引入更多基本面字段的结构化观察。
- 支持估值、盈利能力、现金流和资产负债维度筛选。
- 增加字段缺失和口径差异提示。
- 输出进一步研究对象，而不是投资建议。
- 下一步建议进入事件催化、公告数据或交易纪律模块。

## v1.1 事件催化分析

- 优化手动事件分类和事件影响框架。
- 增加事件类型、可能影响、验证数据和风险点。
- 支持公司事件和行业事件的分层记录。
- 保持规则化解释，不做确定性预测。

## v1.1 性能优化与缓存机制

- V1.1 已完成自动研究对象筛选的性能优化与缓存机制。
- 增加快速模式和完整模式。
- 增加行情筛选结果和基本面数据缓存。
- 增加缓存清除入口。
- 下一步可进入事件催化、交易纪律模块或项目结构拆分。


## v1.2 Project Structure Split And Modular Refactor

- V1.2 initial modular refactor is complete.
- `app.py` remains the Streamlit startup entrypoint and handles page navigation.
- Added module boundaries: `config/`, `data/`, `core/`, and `ui/`.
- This release does not add features, add data sources, change scoring rules, or change the safety boundary.
- `legacy_app.py` remains a compatibility layer / legacy core logic carrier during the transition.

## v1.2.1 Stability Review And Repair

- V1.2.1 unifies version documentation after the V1.2 refactor.
- Clarifies that `legacy_app.py` is not an unused backup.
- Weakens the duplicate legacy screening entry and recommends `ui.screening_ui.render_screening_page()` as the screening entry.
- Adds minimum tests for module imports, forbidden phrases, and screening field contracts.
- Completed by V1.2.2; next migration batch can continue in V1.2.3.

## v1.2.2 Architecture Cleanup

- Migrates the first low-risk configuration batch out of `legacy_app.py`.
- `config/stock_pools.py` owns stock pools and default screening universes.
- `config/stock_names.py` owns stock display-name mappings and lookup helper.
- `config/sector_mapping.py` owns industry / sector / theme mappings and helper.
- `config/fundamental_samples.py` owns built-in sample fundamental data.
- No business features, data sources, scoring rules, stock-pool contents, or fallback order are changed.
- Completed by V1.2.3; next migration batch can continue with explanation or sector-strength pure functions.

## v1.2.3 Core Scoring Migration

- Migrates low-risk scoring logic into `core/scoring.py`.
- `calculate_research_priority_score`, `calculate_fundamental_quality_score`, and `calculate_composite_research_score` now live in `core/scoring.py`.
- `legacy_app.py` imports these functions to preserve the old call path.
- No scoring rules, data sources, stock-pool contents, or fallback order are changed.
- Completed by V1.2.4; next migration batch can continue with explanation-text pure functions or data boundary cleanup.

## v1.2.4 Sector Strength Core Migration

- Migrates low-risk sector-strength pure logic into `core/sector_strength.py`.
- `generate_sector_strength_summary` and `generate_sector_strength_text` now live in `core/sector_strength.py`.
- `legacy_app.py` imports these functions to preserve the old call path.
- No business features, data sources, scoring rules, stock-pool contents, or fallback order are changed.
- Completed by V1.2.5; next migration batch can continue with additional pure helpers or data boundary cleanup.

## v1.2.5 Explanation Text Core Migration

- Migrates low-risk explanation text functions into `core/explanations.py`.
- `generate_selection_reasons`, `generate_screening_risk_warnings`, `generate_screening_summary`, `generate_fundamental_summary`, and `join_explanation_items` now live in `core/explanations.py`.
- `legacy_app.py` imports these functions to preserve the old call path.
- No business features, data sources, scoring rules, stock-pool contents, or fallback order are changed.
- Completed by V1.2.6; next migration batch can continue with data-boundary cleanup or remaining pure helpers.

## v1.2.6 Market Data Helper Migration

- Migrates low-risk market-data formatting and cleaning helpers into `data/market_data.py`.
- Symbol normalization, A-share ticker conversion, price DataFrame normalization, and recent-row trimming now live in `data/market_data.py`.
- Network fetch implementations remain in `legacy_app.py`; lazy wrappers preserve import compatibility and fallback behavior.
- No business features, data sources, scoring rules, stock-pool contents, or fallback order are changed.
- Completed by V1.2.7; next migration batch can continue with carefully isolated data-fetch boundaries or remaining pure helpers.

## v1.2.7 Fundamental Data Helper Migration

- Migrates low-risk fundamental-data formatting and sample helpers into `data/fundamental_data.py`.
- `clean_metric_value`, `build_fundamental_record`, and `get_fundamental_sample_data` now live in `data/fundamental_data.py`.
- Real fundamental-data fetch implementations remain in `legacy_app.py`; lazy wrappers preserve import compatibility.
- No business features, data sources, scoring rules, stock-pool contents, or fallback order are changed.
- Completed by V1.2.8; next migration batch can move only narrowly scoped fetch-boundary helpers after mocked tests.

## v1.2.8 Data Fetch Boundary Tests

- Adds focused mock tests around real data-fetch boundaries without changing the actual network call implementations.
- Covers `fetch_a_share_fundamental_data`, `get_fundamental_data`, and `fetch_screening_price_data` empty data, exception, fallback, missing-field, and stable-return paths.
- Real AkShare, BaoStock, and yfinance call flows remain in `legacy_app.py`.
- No business features, data sources, scoring rules, stock-pool contents, or fallback order are changed.
- Completed by V1.2.9; entrypoint boundaries are now explicit before the next feature phase.

## v1.2.9 Entrypoint Boundary Wrap-Up

- Clarifies `app.py` as the Streamlit page setup and page navigation entrypoint.
- Clarifies `ui/screening_ui.py` as the new screening page entry that still calls the legacy screening renderer.
- Clarifies `legacy_app.py` as the compatibility layer for the old workbench, legacy screening renderer, and real network-adjacent fetch orchestration.
- Adds a small compatibility wrapper for the old research workbench without changing page behavior.
- No business features, data sources, scoring rules, stock-pool contents, fallback order, or AkShare / BaoStock / yfinance call flows are changed.
- The remaining legacy migration risk is concentrated in real fetch orchestration and the large Streamlit workbench renderer; these should not be moved without narrower tests.

## v1.3 Strategy Quantification Framework

- V1.3.0 starts with an independent `strategy/` package.
- `strategy/factors.py` owns pure research-priority factor helpers for trend, momentum, volatility, and volume.
- `strategy/filters.py` owns pure preprocessing filters for missing fields, row count, price threshold, turnover threshold, and abnormal move checks.
- `strategy/risk.py` owns risk-label helpers that return risk tags and explanations only.
- `strategy/presets.py` owns preset configuration structures for research workflows.
- V1.3.0 does not connect the new framework to the Streamlit workflow, existing screening output, scoring rules, page display, or sorting logic.
- V1.3.1 adds `strategy/adapter.py` as a read-only conversion layer from existing screening-result DataFrames to strategy diagnostics.
- Adapter output includes factor scores, filter flags, risk tags, risk notes, preset name, and a diagnostics summary.
- V1.3.1 still does not connect strategy diagnostics to the Streamlit workflow, existing screening output, scoring rules, page display, or sorting logic.
- Future V1.3.x work can add a read-only strategy diagnostics panel only after the adapter behavior and UI boundary are explicitly tested.

## v1.4 交易纪律模块

- 建立学习型交易纪律清单。
- 记录仓位、止损、复盘和风险控制原则。
- 不接入真实交易账户。
- 不输出自动买卖指令。

## v1.5 回测验证增强

- 增加更多策略模板和参数设置。
- 完善交易成本、持仓比例和样本区间说明。
- 增加回测结果的稳定性和局限性提示。
- 强调回测结果不代表未来收益。

## v1.6 AI 研究摘要模块

- 探索 AI 辅助整理研究摘要的可能性。
- 保留数据来源、指标依据和风险提示。
- 不让 AI 直接生成交易结论。
- 明确区分事实、规则判断和主观假设。

## v1.7 工程化增强

- 将单文件原型逐步拆分为更清晰的模块。
- 增加测试覆盖和文档规范。
- 优化配置、日志和错误处理。
- 为长期维护和协作开发打基础。
