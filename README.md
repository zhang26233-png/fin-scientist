# FinScientist

FinScientist V0.3 is a single-file Streamlit prototype for a multi-market financial research workspace. It uses yfinance market data and local rule-based logic to generate lightweight stock research views.

It does not call any AI API and does not use a database.

## Current Features

- Multi-market selection:
  - US stocks, such as `NVDA`, `AAPL`, `MSFT`
  - Hong Kong stocks, such as `0700.HK`, `9988.HK`, `3690.HK`
  - Shanghai A-shares, such as `600519.SS`, `601318.SS`, `600036.SS`
  - Shenzhen A-shares, such as `000001.SZ`, `300750.SZ`, `002594.SZ`
- Automatic yfinance symbol conversion for Hong Kong and A-share tickers.
- Sidebar controls for market, stock ticker, time range, analysis style, analysis dimensions, and benchmark comparison.
- Time ranges: 3 months, 6 months, 1 year, and 2 years.
- Market benchmark comparison:
  - US stocks: S&P 500
  - Hong Kong stocks: Hang Seng Index
  - Shanghai A-shares: SSE Composite
  - Shenzhen A-shares: SZSE Component
- Core indicators:
  - Latest close
  - 20-day return
  - 60-day return
  - 20-day moving average
  - 60-day moving average
  - Annualized volatility
  - Maximum drawdown
  - 52-week high
  - 52-week low
  - 20-day average volume
- Closing price chart with 20-day and 60-day moving averages.
- Normalized stock-vs-benchmark chart when benchmark data is available.
- Local rule-based research summary covering trend, volatility risk, price position, market comparison, and overall observation.
- Local simulated rating: strong watch, neutral watch, or risk watch.

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

## Ticker Notes

- US stocks: enter the ticker directly, such as `NVDA`.
- Hong Kong stocks: enter the numeric code, such as `0700`; the app converts it to `0700.HK`.
- Shanghai A-shares: enter the 6-digit code, such as `600519`; the app converts it to `600519.SS`.
- Shenzhen A-shares: enter the 6-digit code, such as `000001`; the app converts it to `000001.SZ`.

## Current Limitations

- yfinance data can be delayed, missing, or unavailable for some tickers and markets.
- Hong Kong and A-share support depends on yfinance symbol availability.
- The app only uses historical market data and simple local rules.
- Cross-market indicators are not fully comparable because markets differ in currency, trading rules, liquidity, and price limits.
- The simulated rating is for learning and demonstration only.
- It does not include backtesting, portfolio tracking, financial statement analysis, or AI-generated reasoning.
- It is not investment advice.

## Next Steps

- Add richer data sources for fundamentals, news, and analyst estimates.
- Add a backtesting module.
- Add AI-generated summaries.
- Improve A-share and Hong Kong market coverage with more reliable regional data sources.
- Add exportable research reports.
