# FinScientist

FinScientist V0.5 is a single-file Streamlit prototype for a multi-market financial research workspace. It supports US stocks, Hong Kong stocks, and A-shares, and combines market data, technical indicators, company profile fields, valuation fields, financial snapshots, sector notes, recent news, manual event analysis, and local rule-based summaries.

The current version does not call the OpenAI API, does not use a database, and does not perform automated trading.

## Supported Markets

- US stocks: yfinance, for example `NVDA`, `AAPL`, `MSFT`, `TSLA`
- Hong Kong stocks: yfinance, for example `0700`, `9988`, `3690`
- A-shares: akshare price data, for example `600519`, `000001`, `300750`, `002594`

## Data Sources

- `yfinance`: US and Hong Kong historical prices, company profile fields, valuation fields, selected financial fields, and optional news.
- `akshare`: A-share historical daily prices.
- Built-in mappings: selected stock-name mappings and selected A-share sector/profile mappings.

## Input Modes

You can search by stock code or stock name.

Supported built-in stock name mappings include:

- 英伟达 -> 美股 / `NVDA`
- 苹果 -> 美股 / `AAPL`
- 微软 -> 美股 / `MSFT`
- 特斯拉 -> 美股 / `TSLA`
- 腾讯控股 -> 港股 / `0700.HK`
- 阿里巴巴-W -> 港股 / `9988.HK`
- 美团-W -> 港股 / `3690.HK`
- 贵州茅台 -> A股 / `600519`
- 平安银行 -> A股 / `000001`
- 宁德时代 -> A股 / `300750`

If a name is not in the built-in mapping table, use stock code input.

## Current Features

- Market selector: US stocks, Hong Kong stocks, A-shares
- Code or name input
- Time ranges: 3 months, 6 months, 1 year, 2 years
- Analysis style selector: conservative, growth, short-term trading
- Company profile module
- Core price indicator module
- Valuation and financial summary modules
- Price trend chart using `st.line_chart`
- Technical, fundamental, and sector explanation modules
- Recent major news module
- Manual event analysis module
- Event type recognition
- Event impact explanation
- Integrated local research conclusion and simulated rating
- Risk warnings

## V0.5 News And Event Module

For US and Hong Kong stocks, the app attempts to display the first 5 available yfinance news items, including title, source, publish time, and link when available.

For A-shares, the current version does not perform complex news crawling. Use the manual event input box for event analysis.

Manual event analysis supports these event types:

- 财报业绩类
- 政策监管类
- 产品订单类
- 融资资本类
- 行业景气类
- 市场交易类
- 未分类事件

The event analysis outputs:

- Event type
- Possible positive impact
- Possible negative risk
- Data that needs further verification
- Possible short-term trading sentiment impact
- Possible medium- and long-term fundamental impact

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit in your browser.

## Current Limitations

- yfinance news can be unstable, delayed, incomplete, or unavailable.
- A-share real-time news and announcements are not formally integrated yet.
- Manual event analysis is keyword-based and can misclassify events.
- The event explanation is not a real causal model.
- Local rule-based analysis cannot replace human research.
- This project is not investment advice and should not be used for real trading decisions.

## Next Steps

- Connect more reliable news and announcement data.
- Add multi-stock comparison.
- Add a backtesting module.
- Add AI-generated research summaries.
- Split the project structure to improve maintainability.
