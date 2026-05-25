# FinScientist

FinScientist is a single-file Streamlit prototype for an AI-assisted financial research workspace. The current version uses yfinance market data and local rule-based logic to generate a lightweight stock research summary.

It does not call any AI API and does not use a database.

## Current Features

- Sidebar controls for stock ticker, time range, analysis style, and analysis dimensions.
- Time ranges: 3 months, 6 months, 1 year, and 2 years.
- Historical daily market data download with yfinance.
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
- Local rule-based research summary covering trend, volatility risk, price position, and overall observation.
- Local simulated rating: strong watch, neutral watch, or risk watch.
- Risk notes for data quality, market volatility, and investment-advice limitations.

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

- yfinance data can be delayed, missing, or unavailable for some tickers.
- The app only uses historical market data and simple local rules.
- The simulated rating is for learning and demonstration only.
- It does not include backtesting, portfolio tracking, financial statement analysis, or AI-generated reasoning.
- It is not investment advice.

## Next Steps

- Add richer data sources for fundamentals, news, and analyst estimates.
- Add a backtesting module.
- Add AI-generated summaries.
- Support A-share and Hong Kong stock workflows.
