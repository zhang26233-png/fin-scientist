# Development Log

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

- `core/explanations.py` and `core/sector_strength.py` still re-export pure logic from `legacy_app.py`.
- `data/market_data.py` and `data/fundamental_data.py` still re-export data functions from `legacy_app.py`.
- `ui/screening_ui.py` still calls the legacy screening renderer.

### Next Step

- V1.2.4 should migrate one small explanation-text or sector-strength pure logic batch after focused tests.

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
- `core/explanations.py` and `core/sector_strength.py` still re-export pure logic from `legacy_app.py`.
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
- 不接入真实交易账户，不做自动买卖，不输出买入、卖出或持有建议，不改变现有研究优先级评分规则。

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
- 不新增复杂数据源，不接入 OpenAI API，不接入真实交易账户，不做自动买卖，不改变现有研究优先级评分规则。

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
- 不新增评分规则，不新增复杂数据源，不接入 OpenAI API，不接入真实交易账户，不做自动买卖。

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
- 继续保持本地规则生成，不接入 OpenAI API，不接入真实交易账户，不做自动买卖。

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
- 不接入 OpenAI API，不接入真实交易账户，不做自动买卖，仅输出研究候选池和进一步研究对象排序。

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
