import math
import re
from datetime import date

import akshare as ak
import pandas as pd
import streamlit as st
import yfinance as yf


APP_VERSION = "V0.7"
MISSING = "数据暂缺"
INSUFFICIENT = "数据不足"

MARKET_OPTIONS = ["美股", "港股", "A股"]
PERIOD_OPTIONS = {"3个月": "3mo", "6个月": "6mo", "1年": "1y", "2年": "2y", "5年": "5y"}
PERIOD_MONTHS = {"3个月": 3, "6个月": 6, "1年": 12, "2年": 24, "5年": 60}
ANALYSIS_STYLES = ["稳健型", "成长型", "短线交易型"]
ANALYSIS_DIMENSIONS = ["趋势", "波动", "估值", "成交量", "基本面", "板块", "风险"]
BACKTEST_STRATEGIES = ["均线趋势策略", "双均线策略", "动量策略"]
BACKTEST_PERIOD_OPTIONS = ["6个月", "1年", "2年", "5年"]

NAME_MAP = {
    "英伟达": ("美股", "NVDA"),
    "苹果": ("美股", "AAPL"),
    "微软": ("美股", "MSFT"),
    "特斯拉": ("美股", "TSLA"),
    "腾讯控股": ("港股", "0700.HK"),
    "阿里巴巴-W": ("港股", "9988.HK"),
    "美团-W": ("港股", "3690.HK"),
    "贵州茅台": ("A股", "600519"),
    "平安银行": ("A股", "000001"),
    "宁德时代": ("A股", "300750"),
    "比亚迪": ("A股", "002594"),
    "中芯国际": ("A股", "688981"),
}

A_SHARE_PROFILE_MAP = {
    "600519": {
        "company_name": "贵州茅台",
        "industry": "食品饮料",
        "sector": "白酒",
        "exchange": "上海证券交易所",
        "country": "中国",
    },
    "300750": {
        "company_name": "宁德时代",
        "industry": "电力设备",
        "sector": "动力电池",
        "exchange": "深圳证券交易所",
        "country": "中国",
    },
    "000001": {
        "company_name": "平安银行",
        "industry": "银行",
        "sector": "股份制银行",
        "exchange": "深圳证券交易所",
        "country": "中国",
    },
    "002594": {
        "company_name": "比亚迪",
        "industry": "汽车",
        "sector": "新能源汽车",
        "exchange": "深圳证券交易所",
        "country": "中国",
    },
    "688981": {
        "company_name": "中芯国际",
        "industry": "电子",
        "sector": "半导体",
        "exchange": "上海证券交易所",
        "country": "中国",
    },
}

SECTOR_RULES = {
    "半导体": "关注 AI 算力需求、资本开支周期、库存周期、先进制程竞争和地缘风险。",
    "白酒": "关注消费需求、渠道库存、价格带竞争、品牌护城河和经销体系健康度。",
    "银行": "关注净息差、资产质量、地产链风险、资本充足率和拨备覆盖水平。",
    "股份制银行": "关注净息差、资产质量、地产链风险、资本充足率和零售业务韧性。",
    "新能源汽车": "关注销量、价格战、毛利率、电池成本、出口政策和产品周期。",
    "动力电池": "关注装机量、客户结构、原材料成本、技术路线和海外扩产节奏。",
    "软件": "关注订阅收入、客户留存、云迁移、利润率和 AI 产品化能力。",
    "消费电子": "关注新品周期、供应链库存、终端需求和毛利率变化。",
}

EVENT_KEYWORDS = {
    "财报业绩类": ["财报", "业绩", "收入", "利润", "净利润", "亏损", "盈利", "指引", "预告", "超预期", "低于预期"],
    "政策监管类": ["政策", "监管", "处罚", "调查", "反垄断", "许可证", "审批", "合规", "制裁"],
    "产品订单类": ["订单", "客户", "产品", "发布", "新品", "交付", "合同", "中标", "产能", "出货"],
    "融资资本类": ["融资", "增发", "回购", "分红", "减持", "增持", "并购", "重组", "债务", "现金流"],
    "行业景气类": ["涨价", "降价", "需求", "库存", "周期", "景气", "竞争", "价格战", "供给", "出口"],
    "市场交易类": ["放量", "突破", "跌破", "涨停", "跌停", "资金流入", "资金流出", "换手", "回调"],
}

def is_missing(value):
    if value in (None, "", MISSING, INSUFFICIENT):
        return True
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False


def safe_get(source, key, default=MISSING):
    if not isinstance(source, dict):
        return default
    value = source.get(key, default)
    return default if is_missing(value) else value


def to_number(value):
    if is_missing(value):
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def format_price(value):
    number = to_number(value)
    return INSUFFICIENT if pd.isna(number) else f"{number:.2f}"


def format_metric(value):
    number = to_number(value)
    return MISSING if pd.isna(number) else f"{number:.2f}"


def format_percent(value, missing_text=INSUFFICIENT):
    number = to_number(value)
    return missing_text if pd.isna(number) else f"{number:.2%}"


def format_large_number(value):
    number = to_number(value)
    if pd.isna(number):
        return MISSING
    abs_value = abs(number)
    if abs_value >= 1_0000_0000_0000:
        return f"{number / 1_0000_0000_0000:.2f}万亿"
    if abs_value >= 1_0000_0000:
        return f"{number / 1_0000_0000:.2f}亿"
    if abs_value >= 1_0000:
        return f"{number / 1_0000:.2f}万"
    return f"{number:,.0f}"


def resolve_name_to_ticker(name):
    return NAME_MAP.get(name.strip())


def normalize_ticker(raw_ticker, market):
    ticker = raw_ticker.strip().upper()
    if not ticker:
        return ""
    if market == "港股":
        if ticker.endswith(".HK"):
            return ticker
        return f"{ticker.zfill(4)}.HK"
    if market == "A股":
        return ticker.replace(".SS", "").replace(".SZ", "")
    return ticker


def normalize_yfinance_data(data):
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = data.columns.get_level_values(0)
    return data


def fetch_yfinance_history(symbol, period):
    data = yf.download(
        symbol,
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=False,
    )
    data = normalize_yfinance_data(data)
    return data


def fetch_a_share_history(symbol, period_label):
    end_date = date.today()
    start_date = end_date - pd.DateOffset(months=PERIOD_MONTHS[period_label])
    raw = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        adjust="qfq",
    )
    if raw.empty:
        return pd.DataFrame()

    column_map = {
        "日期": "Date",
        "开盘": "Open",
        "收盘": "Close",
        "最高": "High",
        "最低": "Low",
        "成交量": "Volume",
        "成交额": "Turnover",
    }
    data = raw.rename(columns=column_map)
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")
    keep_columns = [col for col in ["Open", "High", "Low", "Close", "Volume", "Turnover"] if col in data]
    return data[keep_columns].apply(pd.to_numeric, errors="coerce")


def fetch_market_data(symbol, market, period_label):
    if market == "A股":
        return fetch_a_share_history(symbol, period_label)
    return fetch_yfinance_history(symbol, PERIOD_OPTIONS[period_label])


def fetch_yfinance_info(symbol):
    try:
        return yf.Ticker(symbol).info or {}
    except Exception:
        return {}


def fetch_a_share_info(symbol):
    info = {}
    try:
        raw = ak.stock_individual_info_em(symbol=symbol)
        if not raw.empty and {"item", "value"}.issubset(raw.columns):
            info = dict(zip(raw["item"], raw["value"]))
    except Exception:
        info = {}
    return info


def fetch_company_profile(symbol, market, info):
    if market in ("美股", "港股"):
        return {
            "company_name": safe_get(info, "longName"),
            "short_name": safe_get(info, "shortName"),
            "market": market,
            "exchange": safe_get(info, "exchange"),
            "industry": safe_get(info, "industry"),
            "sector": safe_get(info, "sector"),
            "country": safe_get(info, "country"),
            "description": safe_get(info, "longBusinessSummary"),
            "website": safe_get(info, "website"),
            "employees": safe_get(info, "fullTimeEmployees"),
        }

    mapped = A_SHARE_PROFILE_MAP.get(symbol, {})
    return {
        "company_name": mapped.get("company_name") or safe_get(info, "股票简称"),
        "short_name": mapped.get("company_name") or safe_get(info, "股票简称"),
        "market": market,
        "exchange": mapped.get("exchange") or infer_a_share_exchange(symbol),
        "industry": mapped.get("industry", MISSING),
        "sector": mapped.get("sector", MISSING),
        "country": mapped.get("country", "中国"),
        "description": MISSING,
        "website": MISSING,
        "employees": MISSING,
    }


def infer_a_share_exchange(symbol):
    if symbol.startswith(("60", "68")):
        return "上海证券交易所"
    if symbol.startswith(("00", "30")):
        return "深圳证券交易所"
    return MISSING


def fetch_valuation_metrics(symbol, market, info, price_metrics):
    if market in ("美股", "港股"):
        dividend_yield = safe_get(info, "dividendYield")
        return {
            "market_cap": safe_get(info, "marketCap"),
            "pe": safe_get(info, "trailingPE"),
            "forward_pe": safe_get(info, "forwardPE"),
            "pb": safe_get(info, "priceToBook"),
            "ps": safe_get(info, "priceToSalesTrailing12Months"),
            "dividend_yield": dividend_yield,
            "beta": safe_get(info, "beta"),
            "high_52w": safe_get(info, "fiftyTwoWeekHigh", price_metrics["high_52w"]),
            "low_52w": safe_get(info, "fiftyTwoWeekLow", price_metrics["low_52w"]),
            "target_mean_price": safe_get(info, "targetMeanPrice"),
        }

    return {
        "market_cap": safe_get(info, "总市值"),
        "pe": safe_get(info, "市盈率"),
        "forward_pe": MISSING,
        "pb": safe_get(info, "市净率"),
        "ps": MISSING,
        "dividend_yield": MISSING,
        "beta": MISSING,
        "high_52w": price_metrics["high_52w"],
        "low_52w": price_metrics["low_52w"],
        "target_mean_price": MISSING,
    }


def fetch_financial_snapshot(market, info):
    if market in ("美股", "港股"):
        return {
            "total_revenue": safe_get(info, "totalRevenue"),
            "gross_margin": safe_get(info, "grossMargins"),
            "ebitda": safe_get(info, "ebitda"),
            "net_income_margin": safe_get(info, "profitMargins"),
            "total_cash": safe_get(info, "totalCash"),
            "total_debt": safe_get(info, "totalDebt"),
            "free_cash_flow": safe_get(info, "freeCashflow"),
            "roe_roa": safe_get(info, "returnOnEquity", safe_get(info, "returnOnAssets")),
        }

    return {
        "total_revenue": MISSING,
        "gross_margin": MISSING,
        "ebitda": MISSING,
        "net_income_margin": MISSING,
        "total_cash": MISSING,
        "total_debt": MISSING,
        "free_cash_flow": MISSING,
        "roe_roa": MISSING,
    }


def calculate_return(close_prices, days):
    if len(close_prices) <= days:
        return math.nan
    return close_prices.iloc[-1] / close_prices.iloc[-days - 1] - 1


def calculate_max_drawdown(close_prices):
    if len(close_prices) < 2:
        return math.nan
    running_high = close_prices.cummax()
    drawdown = close_prices / running_high - 1
    return drawdown.min()


def calculate_indicators(data):
    close_prices = data["Close"].dropna() if "Close" in data else pd.Series(dtype=float)
    volume = data["Volume"].dropna() if "Volume" in data else pd.Series(dtype=float)
    daily_returns = close_prices.pct_change().dropna()
    latest_close = close_prices.iloc[-1] if len(close_prices) else math.nan

    return {
        "latest_close": latest_close,
        "return_5d": calculate_return(close_prices, 5),
        "return_20d": calculate_return(close_prices, 20),
        "return_60d": calculate_return(close_prices, 60),
        "return_120d": calculate_return(close_prices, 120),
        "ma_5d": close_prices.tail(5).mean() if len(close_prices) >= 5 else math.nan,
        "ma_20d": close_prices.tail(20).mean() if len(close_prices) >= 20 else math.nan,
        "ma_60d": close_prices.tail(60).mean() if len(close_prices) >= 60 else math.nan,
        "ma_120d": close_prices.tail(120).mean() if len(close_prices) >= 120 else math.nan,
        "bias_20d": latest_close / close_prices.tail(20).mean() - 1 if len(close_prices) >= 20 else math.nan,
        "bias_60d": latest_close / close_prices.tail(60).mean() - 1 if len(close_prices) >= 60 else math.nan,
        "annual_volatility": daily_returns.std() * math.sqrt(252) if len(daily_returns) >= 20 else math.nan,
        "max_drawdown": calculate_max_drawdown(close_prices),
        "range_high": close_prices.max() if len(close_prices) else math.nan,
        "range_low": close_prices.min() if len(close_prices) else math.nan,
        "high_52w": close_prices.tail(252).max() if len(close_prices) >= 60 else math.nan,
        "low_52w": close_prices.tail(252).min() if len(close_prices) >= 60 else math.nan,
        "avg_volume_20d": volume.tail(20).mean() if len(volume) >= 20 else math.nan,
        "data_points": len(close_prices),
    }


def parse_ticker_list(input_text, market_type="美股"):
    raw_items = re.split(r"[,，\s]+", input_text or "")
    tickers = []
    seen = set()

    for raw_item in raw_items:
        item = raw_item.strip().upper()
        if not item:
            continue
        normalized = normalize_ticker(item, market_type)
        if normalized and normalized not in seen:
            tickers.append(normalized)
            seen.add(normalized)

    if len(tickers) > 10:
        st.warning("多股票对比最多支持 10 只股票，本次仅处理前 10 只。")
        tickers = tickers[:10]

    return tickers


def get_comparison_trend_state(metrics):
    if metrics["data_points"] < 60:
        return "数据不足"
    latest_close = metrics["latest_close"]
    ma_20d = metrics["ma_20d"]
    ma_60d = metrics["ma_60d"]
    if pd.isna(latest_close) or pd.isna(ma_20d) or pd.isna(ma_60d):
        return "数据不足"
    if latest_close > ma_20d and latest_close > ma_60d:
        return "偏强"
    if latest_close < ma_20d and latest_close < ma_60d:
        return "偏弱"
    return "中性"


def get_comparison_rating(metrics):
    if metrics["data_points"] < 60:
        return "数据不足"

    trend_state = get_comparison_trend_state(metrics)
    return_60d = to_number(metrics["return_60d"])
    annual_volatility = to_number(metrics["annual_volatility"])
    max_drawdown = to_number(metrics["max_drawdown"])

    if (
        trend_state == "偏强"
        and not pd.isna(return_60d)
        and return_60d > 0
        and (pd.isna(max_drawdown) or max_drawdown > -0.25)
    ):
        return "强势观察"
    if (
        trend_state == "偏弱"
        or (not pd.isna(max_drawdown) and max_drawdown <= -0.25)
        or (not pd.isna(annual_volatility) and annual_volatility >= 0.45)
    ):
        return "风险观察"
    return "中性观察"


def normalize_price_series(price_series_map):
    normalized = pd.DataFrame()
    for ticker, close_prices in price_series_map.items():
        clean_prices = close_prices.dropna()
        if len(clean_prices) < 2:
            continue
        first_price = clean_prices.iloc[0]
        if pd.isna(first_price) or first_price == 0:
            continue
        normalized[ticker] = clean_prices / first_price * 100
    return normalized


def build_comparison_table(tickers, market_type, period):
    rows = []
    price_series_map = {}

    for ticker in tickers:
        row = {
            "输入代码": ticker,
            "实际查询代码": ticker,
            "最新收盘价": INSUFFICIENT,
            "近20日涨跌幅": INSUFFICIENT,
            "近60日涨跌幅": INSUFFICIENT,
            "年化波动率": INSUFFICIENT,
            "最大回撤": INSUFFICIENT,
            "相对20日均线偏离": INSUFFICIENT,
            "相对60日均线偏离": INSUFFICIENT,
            "趋势状态": "数据不足",
            "本地模拟评级": "数据不足",
            "数据状态": "数据不足",
        }
        try:
            actual_ticker = normalize_ticker(ticker, market_type)
            row["实际查询代码"] = actual_ticker
            data = fetch_market_data(actual_ticker, market_type, period)
            if data.empty or "Close" not in data.columns:
                row["数据状态"] = "获取失败"
                rows.append(row)
                continue

            metrics = calculate_indicators(data)
            row.update(
                {
                    "最新收盘价": format_price(metrics["latest_close"]),
                    "近20日涨跌幅": format_percent(metrics["return_20d"]),
                    "近60日涨跌幅": format_percent(metrics["return_60d"]),
                    "年化波动率": format_percent(metrics["annual_volatility"]),
                    "最大回撤": format_percent(metrics["max_drawdown"]),
                    "相对20日均线偏离": format_percent(metrics["bias_20d"]),
                    "相对60日均线偏离": format_percent(metrics["bias_60d"]),
                    "趋势状态": get_comparison_trend_state(metrics),
                    "本地模拟评级": get_comparison_rating(metrics),
                    "数据状态": "正常" if metrics["data_points"] >= 20 else "数据不足",
                    "_return_60d": metrics["return_60d"],
                    "_annual_volatility": metrics["annual_volatility"],
                    "_max_drawdown": metrics["max_drawdown"],
                    "_bias_20d": metrics["bias_20d"],
                    "_bias_60d": metrics["bias_60d"],
                }
            )
            price_series_map[actual_ticker] = data["Close"]
        except Exception:
            row["数据状态"] = "获取失败"
        rows.append(row)

    comparison_df = pd.DataFrame(rows)
    comparison_df.attrs["normalized_prices"] = normalize_price_series(price_series_map)
    return comparison_df


def list_symbols_by_condition(comparison_df, condition, limit=5):
    symbols = []
    for _, row in comparison_df.iterrows():
        try:
            if condition(row):
                symbols.append(str(row["实际查询代码"]))
        except Exception:
            continue
    return symbols[:limit]


def format_symbol_list(symbols):
    return "、".join(symbols) if symbols else "暂无明显标的"


def generate_comparison_summary(comparison_df):
    if comparison_df.empty:
        return "暂无可用于生成摘要的多股票对比数据。仅用于学习演示，不构成投资建议。"

    valid_df = comparison_df[comparison_df["数据状态"] != "获取失败"].copy()
    if valid_df.empty:
        return "本次对比未获取到可用行情数据。请检查股票代码、市场类型或数据源状态。仅用于学习演示，不构成投资建议。"

    strong_symbols = list_symbols_by_condition(
        valid_df,
        lambda row: not pd.isna(to_number(row.get("_return_60d")))
        and to_number(row.get("_return_60d")) > 0.05,
    )
    high_vol_symbols = list_symbols_by_condition(
        valid_df,
        lambda row: not pd.isna(to_number(row.get("_annual_volatility")))
        and to_number(row.get("_annual_volatility")) >= 0.45,
    )
    high_drawdown_symbols = list_symbols_by_condition(
        valid_df,
        lambda row: not pd.isna(to_number(row.get("_max_drawdown")))
        and to_number(row.get("_max_drawdown")) <= -0.25,
    )
    weak_symbols = list_symbols_by_condition(valid_df, lambda row: row.get("趋势状态") == "偏弱")
    above_ma_symbols = list_symbols_by_condition(
        valid_df,
        lambda row: not pd.isna(to_number(row.get("_bias_20d")))
        and not pd.isna(to_number(row.get("_bias_60d")))
        and to_number(row.get("_bias_20d")) > 0
        and to_number(row.get("_bias_60d")) > 0,
    )
    research_symbols = list_symbols_by_condition(
        valid_df,
        lambda row: row.get("本地模拟评级") in ("强势观察", "中性观察")
        and row.get("趋势状态") != "偏弱",
    )

    return "\n".join(
        [
            f"1. 相对强势标的：{format_symbol_list(strong_symbols)}。这些标的近60日表现相对更强，但仍需结合估值、财报和行业信息继续验证。",
            f"2. 高波动标的：{format_symbol_list(high_vol_symbols)}。这些标的年化波动率偏高，适合重点观察价格弹性和风险暴露。",
            f"3. 高回撤标的：{format_symbol_list(high_drawdown_symbols)}。这些标的区间最大回撤较大，需要进一步排查基本面、行业景气和事件冲击。",
            f"4. 趋势较弱标的：{format_symbol_list(weak_symbols)}。这些标的当前价格相对主要均线偏弱，短中期趋势确认度较低。",
            f"5. 后续研究建议：价格高于20日和60日均线的标的包括 {format_symbol_list(above_ma_symbols)}；更适合进入下一步研究清单的标的包括 {format_symbol_list(research_symbols)}。本摘要不输出买入、卖出或目标价，仅用于学习演示，不构成投资建议。",
        ]
    )


def add_to_watchlist(ticker):
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []
    ticker = (ticker or "").strip().upper()
    if ticker and ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(ticker)


def clear_watchlist():
    st.session_state.watchlist = []


def render_watchlist_panel():
    st.header("自选股观察列表")
    watchlist = st.session_state.get("watchlist", [])
    st.metric("当前自选股数量", len(watchlist))
    if watchlist:
        st.write("、".join(watchlist))
    else:
        st.info("当前暂无自选股，可先在单股票分析区加入当前标的。")


def render_comparison_section(tickers, market_type, period_label):
    st.divider()
    st.header("多股票对比")

    if not tickers:
        st.warning("请输入至少一只股票代码后再运行多股票对比。")
        return

    try:
        with st.spinner(f"正在获取 {market_type} 多股票对比数据..."):
            comparison_df = build_comparison_table(tickers, market_type, period_label)
    except Exception as exc:
        st.error(f"多股票对比生成失败，请稍后重试。错误信息：{exc}")
        return

    if comparison_df.empty:
        st.warning("多股票对比表为空，请检查输入代码或数据源状态。")
        return

    display_columns = [col for col in comparison_df.columns if not col.startswith("_")]
    st.dataframe(comparison_df[display_columns], hide_index=True, use_container_width=True)

    st.subheader("表格解释")
    st.write(generate_comparison_summary(comparison_df))

    normalized_prices = comparison_df.attrs.get("normalized_prices", pd.DataFrame())
    if isinstance(normalized_prices, pd.DataFrame) and not normalized_prices.empty:
        st.subheader("归一化收盘价走势")
        st.caption("每只股票第一天价格设为 100，后续按相对变化展示。")
        st.line_chart(normalized_prices)
    else:
        st.info("本次可用于绘制归一化价格走势的数据不足。")


def is_valid_number(value):
    number = to_number(value)
    return not pd.isna(number) and math.isfinite(number)


def calculate_max_drawdown_for_series(nav_series):
    clean_nav = nav_series.dropna() if isinstance(nav_series, pd.Series) else pd.Series(dtype=float)
    clean_nav = clean_nav[clean_nav > 0]
    if len(clean_nav) < 2:
        return math.nan
    running_high = clean_nav.cummax()
    drawdown = clean_nav / running_high - 1
    return drawdown.min()


def generate_backtest_signals(price_df, strategy_name, trading_cost=0.0):
    if price_df is None or price_df.empty or "Close" not in price_df.columns:
        return pd.DataFrame()

    backtest_df = pd.DataFrame(index=price_df.index)
    backtest_df["Close"] = pd.to_numeric(price_df["Close"], errors="coerce")
    backtest_df = backtest_df.dropna(subset=["Close"])
    if backtest_df.empty:
        return pd.DataFrame()

    if strategy_name in ("均线趋势策略", "动量策略") and len(backtest_df) < 20:
        return pd.DataFrame()
    if strategy_name == "双均线策略" and len(backtest_df) < 60:
        return pd.DataFrame()

    backtest_df["return"] = backtest_df["Close"].pct_change().fillna(0)

    if strategy_name == "均线趋势策略":
        backtest_df["MA20"] = backtest_df["Close"].rolling(20).mean()
        backtest_df["signal"] = (backtest_df["Close"] > backtest_df["MA20"]).astype(int)
    elif strategy_name == "双均线策略":
        backtest_df["MA20"] = backtest_df["Close"].rolling(20).mean()
        backtest_df["MA60"] = backtest_df["Close"].rolling(60).mean()
        backtest_df["signal"] = (backtest_df["MA20"] > backtest_df["MA60"]).astype(int)
    elif strategy_name == "动量策略":
        backtest_df["momentum_20d"] = backtest_df["Close"] / backtest_df["Close"].shift(20) - 1
        backtest_df["signal"] = (backtest_df["momentum_20d"] > 0).astype(int)
    else:
        return pd.DataFrame()

    backtest_df["signal"] = backtest_df["signal"].fillna(0).astype(int)
    backtest_df["position"] = backtest_df["signal"].shift(1).fillna(0)
    backtest_df["position_change"] = backtest_df["position"].diff().abs().fillna(backtest_df["position"].abs())
    backtest_df["strategy_return"] = (
        backtest_df["position"] * backtest_df["return"]
        - backtest_df["position_change"] * max(float(trading_cost), 0.0)
    )
    backtest_df["benchmark_return"] = backtest_df["return"]
    backtest_df["strategy_return"] = backtest_df["strategy_return"].replace([math.inf, -math.inf], math.nan).fillna(0)
    backtest_df["benchmark_return"] = backtest_df["benchmark_return"].replace([math.inf, -math.inf], math.nan).fillna(0)
    backtest_df["strategy_nav"] = (1 + backtest_df["strategy_return"]).cumprod()
    backtest_df["benchmark_nav"] = (1 + backtest_df["benchmark_return"]).cumprod()

    return backtest_df[
        [
            "Close",
            "return",
            "signal",
            "position",
            "strategy_return",
            "benchmark_return",
            "strategy_nav",
            "benchmark_nav",
        ]
    ]


def calculate_backtest_metrics(backtest_df):
    empty_metrics = {
        "strategy_total_return": math.nan,
        "benchmark_total_return": math.nan,
        "strategy_annual_return": math.nan,
        "benchmark_annual_return": math.nan,
        "strategy_annual_volatility": math.nan,
        "strategy_max_drawdown": math.nan,
        "sharpe_ratio": math.nan,
        "trade_count": math.nan,
        "holding_days_ratio": math.nan,
        "win_rate": math.nan,
    }
    if backtest_df is None or backtest_df.empty or len(backtest_df) < 2:
        return empty_metrics

    data = backtest_df.copy()
    days = len(data)
    if days <= 1:
        return empty_metrics

    strategy_nav = data["strategy_nav"].dropna()
    benchmark_nav = data["benchmark_nav"].dropna()
    if strategy_nav.empty or benchmark_nav.empty:
        return empty_metrics

    strategy_total_return = strategy_nav.iloc[-1] - 1
    benchmark_total_return = benchmark_nav.iloc[-1] - 1
    years = days / 252
    strategy_annual_return = (strategy_nav.iloc[-1] ** (1 / years) - 1) if years > 0 and strategy_nav.iloc[-1] > 0 else math.nan
    benchmark_annual_return = (benchmark_nav.iloc[-1] ** (1 / years) - 1) if years > 0 and benchmark_nav.iloc[-1] > 0 else math.nan

    strategy_returns = data["strategy_return"].dropna()
    return_std = strategy_returns.std()
    strategy_annual_volatility = return_std * math.sqrt(252) if len(strategy_returns) >= 20 else math.nan
    sharpe_ratio = (
        strategy_returns.mean() / return_std * math.sqrt(252)
        if len(strategy_returns) >= 20 and return_std and return_std > 0
        else math.nan
    )

    position_change = data["position"].diff().abs().fillna(data["position"].abs())
    trade_count = int(position_change.sum()) if len(position_change) else math.nan
    holding_days_ratio = data["position"].mean() if "position" in data else math.nan
    win_rate = (strategy_returns > 0).mean() if len(strategy_returns) else math.nan

    metrics = {
        "strategy_total_return": strategy_total_return,
        "benchmark_total_return": benchmark_total_return,
        "strategy_annual_return": strategy_annual_return,
        "benchmark_annual_return": benchmark_annual_return,
        "strategy_annual_volatility": strategy_annual_volatility,
        "strategy_max_drawdown": calculate_max_drawdown_for_series(data["strategy_nav"]),
        "sharpe_ratio": sharpe_ratio,
        "trade_count": trade_count,
        "holding_days_ratio": holding_days_ratio,
        "win_rate": win_rate,
    }

    return {
        key: (value if is_valid_number(value) else math.nan)
        for key, value in metrics.items()
    }


def format_backtest_number(value):
    return INSUFFICIENT if not is_valid_number(value) else f"{value:.2f}"


def format_backtest_count(value):
    return INSUFFICIENT if not is_valid_number(value) else f"{int(value)}"


def generate_backtest_summary(metrics, strategy_name):
    if not metrics or not is_valid_number(metrics.get("strategy_total_return")):
        return "回测数据不足，暂时无法生成稳定解读。回测结果仅用于学习演示，不代表未来收益，不构成投资建议。"

    strategy_return = metrics["strategy_total_return"]
    benchmark_return = metrics["benchmark_total_return"]
    max_drawdown = metrics["strategy_max_drawdown"]
    volatility = metrics["strategy_annual_volatility"]
    trade_count = metrics["trade_count"]

    relative_text = "跑赢基准" if strategy_return > benchmark_return else "未跑赢基准"
    drawdown_text = (
        "回撤相对可控"
        if is_valid_number(max_drawdown) and max_drawdown > -0.2
        else "回撤压力较大，需要重点观察极端行情下的风险"
    )
    volatility_text = (
        "波动率偏高，净值曲线可能较不稳定"
        if is_valid_number(volatility) and volatility > 0.35
        else "波动率处于相对温和区间"
    )
    trade_text = (
        "交易频率较高，结果对交易成本更敏感"
        if is_valid_number(trade_count) and trade_count > 20
        else "交易频率较低，策略更偏向阶段性持仓"
    )

    if strategy_name == "双均线策略":
        suitable_market = "可能更适合趋势延续较强、噪音相对较低的市场环境。"
        failure_market = "在横盘震荡和频繁假突破环境中可能反复切换仓位。"
    elif strategy_name == "动量策略":
        suitable_market = "可能更适合短中期动量延续明显的市场环境。"
        failure_market = "在快速反转或消息驱动跳变较多的市场中可能失效。"
    else:
        suitable_market = "可能更适合价格持续站上短期均线的趋势行情。"
        failure_market = "在均线附近反复震荡时可能出现较多无效信号。"

    return "\n".join(
        [
            f"1. 策略相对表现：本次 {strategy_name} {relative_text}，策略累计收益率为 {format_percent(strategy_return)}，基准累计收益率为 {format_percent(benchmark_return)}。",
            f"2. 收益与回撤特征：策略最大回撤为 {format_percent(max_drawdown)}，{drawdown_text}。",
            f"3. 波动风险：策略年化波动率为 {format_percent(volatility)}，{volatility_text}。",
            f"4. 交易频率：本次粗略统计交易次数为 {format_backtest_count(trade_count)}，{trade_text}。",
            f"5. 适合环境：{suitable_market}",
            f"6. 可能失效环境：{failure_market}",
            "7. 风险提示：回测结果不代表未来收益，仅用于学习演示，不构成投资建议，不应用于真实交易。",
        ]
    )


def run_backtest_section(
    ticker,
    market_type,
    strategy_name,
    period_label,
    initial_capital,
    trading_cost,
):
    st.divider()
    st.header("策略回测")

    if not ticker:
        st.warning("请输入有效股票代码后再运行回测。")
        return

    try:
        actual_ticker = normalize_ticker(ticker, market_type)
        with st.spinner(f"正在运行 {actual_ticker} 的策略回测..."):
            backtest_price_data = fetch_market_data(actual_ticker, market_type, period_label)
            backtest_df = generate_backtest_signals(backtest_price_data, strategy_name, trading_cost)
    except Exception as exc:
        st.error(f"策略回测失败，请检查代码、市场类型或数据源状态。错误信息：{exc}")
        return

    min_days = 60 if strategy_name == "双均线策略" else 20
    if backtest_price_data is None or backtest_price_data.empty or "Close" not in backtest_price_data.columns:
        st.warning("未获取到可用于回测的历史价格数据。")
        return
    if len(backtest_price_data.dropna(subset=["Close"])) < min_days:
        st.warning(f"{strategy_name} 至少需要 {min_days} 个交易日数据，当前历史数据不足。")
        return
    if backtest_df.empty:
        st.warning("回测结果为空，请检查策略参数或历史数据。")
        return

    metrics = calculate_backtest_metrics(backtest_df)

    st.subheader("回测说明")
    st.write(
        f"策略名称：{strategy_name} | 股票代码：{actual_ticker} | 市场类型：{market_type} | "
        f"回测时间范围：{period_label} | 初始资金：{initial_capital:,.0f} | 单边交易成本：{trading_cost:.4f}"
    )
    st.caption("这是教学演示，不构成投资建议；回测结果不代表未来收益。")

    metric_cols = st.columns(6)
    metric_cols[0].metric("策略累计收益率", format_percent(metrics["strategy_total_return"]))
    metric_cols[1].metric("基准累计收益率", format_percent(metrics["benchmark_total_return"]))
    metric_cols[2].metric("策略最大回撤", format_percent(metrics["strategy_max_drawdown"]))
    metric_cols[3].metric("夏普比率", format_backtest_number(metrics["sharpe_ratio"]))
    metric_cols[4].metric("交易次数", format_backtest_count(metrics["trade_count"]))
    metric_cols[5].metric("持仓天数占比", format_percent(metrics["holding_days_ratio"]))

    st.subheader("净值曲线")
    nav_frame = pd.DataFrame(index=backtest_df.index)
    nav_frame["策略净值"] = backtest_df["strategy_nav"] * initial_capital
    nav_frame["基准净值"] = backtest_df["benchmark_nav"] * initial_capital
    st.line_chart(nav_frame)

    st.subheader("最近 20 条买卖信号")
    signal_table = backtest_df.tail(20).reset_index()
    first_col = signal_table.columns[0]
    signal_table = signal_table.rename(
        columns={
            first_col: "日期",
            "Close": "收盘价",
            "signal": "signal",
            "position": "position",
            "strategy_return": "strategy_return",
            "strategy_nav": "strategy_nav",
            "benchmark_nav": "benchmark_nav",
        }
    )
    st.dataframe(
        signal_table[["日期", "收盘价", "signal", "position", "strategy_return", "strategy_nav", "benchmark_nav"]],
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("回测解释")
    st.write(generate_backtest_summary(metrics, strategy_name))


def build_price_frame(data):
    price_frame = pd.DataFrame(index=data.index)
    price_frame["收盘价"] = data["Close"]
    price_frame["20日均线"] = data["Close"].rolling(20).mean()
    price_frame["60日均线"] = data["Close"].rolling(60).mean()
    return price_frame


def describe_trend(metrics):
    if metrics["data_points"] < 60:
        return "样本不足，暂时无法形成稳定的短中期趋势判断。"
    latest_close = metrics["latest_close"]
    ma_20d = metrics["ma_20d"]
    ma_60d = metrics["ma_60d"]
    if latest_close > ma_20d and latest_close > ma_60d:
        return "当前价格高于20日和60日均线，短中期趋势偏强。"
    if latest_close < ma_20d and latest_close < ma_60d:
        return "当前价格低于20日和60日均线，趋势偏弱。"
    return "当前价格在主要均线附近，趋势中性或震荡。"


def generate_rating(metrics):
    reasons = []
    if metrics["data_points"] < 60:
        return "中性观察", ["历史数据不足60个交易日，评级置信度较低。"]

    score = 0
    if metrics["latest_close"] > metrics["ma_20d"]:
        score += 1
        reasons.append("价格高于20日均线")
    else:
        score -= 1
        reasons.append("价格未站上20日均线")

    if metrics["latest_close"] > metrics["ma_60d"]:
        score += 1
        reasons.append("价格高于60日均线")
    else:
        score -= 1
        reasons.append("价格未站上60日均线")

    if not pd.isna(metrics["return_60d"]) and metrics["return_60d"] > 0:
        score += 1
        reasons.append("近60日涨跌幅为正")
    else:
        score -= 1
        reasons.append("近60日涨跌幅不强")

    if not pd.isna(metrics["max_drawdown"]) and metrics["max_drawdown"] < -0.25:
        score -= 1
        reasons.append("最大回撤偏大")
    if not pd.isna(metrics["annual_volatility"]) and metrics["annual_volatility"] > 0.45:
        score -= 1
        reasons.append("年化波动率偏高")

    if score >= 2:
        return "强势观察", reasons
    if score <= -2:
        return "风险观察", reasons
    return "中性观察", reasons


def generate_technical_summary(metrics, analysis_style):
    volume_text = (
        f"近20日平均成交量为 {format_large_number(metrics['avg_volume_20d'])}。"
        if not pd.isna(to_number(metrics["avg_volume_20d"]))
        else "成交量数据不足，暂时无法判断量能变化。"
    )
    return {
        "趋势判断": describe_trend(metrics),
        "波动风险": (
            f"年化波动率为 {format_percent(metrics['annual_volatility'])}，最大回撤为 "
            f"{format_percent(metrics['max_drawdown'])}。{analysis_style} 应结合持有周期控制风险。"
        ),
        "价格位置": (
            f"当前区间最高价为 {format_price(metrics['range_high'])}，区间最低价为 "
            f"{format_price(metrics['range_low'])}，52周区间数据用于辅助判断价格位置。"
        ),
        "成交量观察": volume_text,
        "综合技术观察": "技术面结论由均线、涨跌幅、波动率和回撤规则生成，不能单独作为投资依据。",
    }


def generate_fundamental_summary(valuation, financial):
    available = [value for value in list(valuation.values()) + list(financial.values()) if not is_missing(value)]
    if not available:
        return {"数据可信度提示": "当前可用基本面数据不足，不能形成完整判断。"}

    pe = to_number(valuation["pe"])
    pb = to_number(valuation["pb"])
    gross_margin = to_number(financial["gross_margin"])
    debt = to_number(financial["total_debt"])
    cash = to_number(financial["total_cash"])
    fcf = to_number(financial["free_cash_flow"])

    if pd.isna(pe):
        valuation_text = "PE 数据暂缺，估值水平需要结合其他指标和同行对比。"
    elif pe > 50:
        valuation_text = "PE 较高，市场可能已经计入较强增长预期。"
    elif pe > 0 and pe < 15:
        valuation_text = "PE 相对较低，但需排查盈利周期、行业景气度和一次性因素。"
    else:
        valuation_text = "PE 处于中间区间，仍需结合增速、利润率和同行估值判断。"

    margin_text = (
        "毛利率数据暂缺，盈利质量判断不完整。"
        if pd.isna(gross_margin)
        else f"毛利率为 {format_percent(gross_margin, MISSING)}，可用于观察产品竞争力和成本压力。"
    )
    balance_text = (
        "现金和债务数据暂缺，资产负债观察不完整。"
        if pd.isna(debt) or pd.isna(cash)
        else f"总现金为 {format_large_number(cash)}，总债务为 {format_large_number(debt)}，需进一步观察偿债压力。"
    )
    cashflow_text = (
        "自由现金流数据暂缺，现金创造能力还需要财报验证。"
        if pd.isna(fcf)
        else f"自由现金流为 {format_large_number(fcf)}，可辅助判断利润质量。"
    )

    return {
        "估值观察": valuation_text,
        "盈利质量观察": margin_text,
        "资产负债观察": balance_text,
        "现金流观察": cashflow_text,
        "数据可信度提示": "yfinance 与 akshare 的基本面字段可能缺失、滞后或口径不一致，需回到正式财报交叉验证。",
    }


def generate_sector_summary(profile):
    industry = profile["industry"]
    sector = profile["sector"]
    lookup_keys = [str(sector), str(industry)]
    logic = next((SECTOR_RULES[key] for key in lookup_keys if key in SECTOR_RULES), None)
    if logic is None:
        logic = "当前行业规则样本有限，需要结合行业景气度、竞争格局、政策环境和公司财报进一步研究。"

    return {
        "所属行业": industry,
        "所属板块": sector,
        "行业逻辑简述": logic,
        "需要进一步研究的问题": "后续应验证行业需求、竞争格局、利润率变化、估值位置和重大政策或技术变化。",
    }


def format_news_item(item):
    if not isinstance(item, dict):
        return None

    content = item.get("content") if isinstance(item.get("content"), dict) else {}
    title = item.get("title") or content.get("title")
    if is_missing(title):
        return None

    publisher = item.get("publisher") or item.get("provider") or content.get("provider") or "yfinance"
    publish_time = item.get("providerPublishTime") or item.get("pubDate") or content.get("pubDate")
    link = item.get("link") or item.get("clickThroughUrl") or content.get("canonicalUrl") or MISSING

    if isinstance(publish_time, (int, float)):
        publish_time = pd.to_datetime(publish_time, unit="s").strftime("%Y-%m-%d %H:%M")
    elif is_missing(publish_time):
        publish_time = MISSING

    if isinstance(link, dict):
        link = link.get("url", MISSING)

    return {
        "标题": str(title),
        "来源": publisher if not is_missing(publisher) else MISSING,
        "发布时间": publish_time,
        "链接": link if not is_missing(link) else MISSING,
    }


def fetch_news(symbol, market, limit=5):
    if market == "A股":
        return []
    try:
        raw_news = yf.Ticker(symbol).news or []
    except Exception:
        return []

    news_items = []
    for item in raw_news:
        formatted = format_news_item(item)
        if formatted:
            news_items.append(formatted)
        if len(news_items) >= limit:
            break
    return news_items


def classify_event(event_text):
    lowered = event_text.lower()
    for event_type, keywords in EVENT_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return event_type
    return "未分类事件"


def generate_event_analysis(event_text, event_type, analysis_style):
    if not event_text.strip():
        return None

    rules = {
        "财报业绩类": {
            "positive": "如果收入、利润率、现金流或管理层指引同步改善，可能强化市场对公司增长质量的认可。",
            "negative": "如果增长依赖一次性因素、利润率承压或现金流质量不足，短期利好可能难以持续。",
            "verify": "需要验证收入增长、毛利率、净利润、自由现金流和未来指引。",
            "short": "短期交易情绪通常对超预期或低于预期的财报反应较快，容易带来跳空和放量波动。",
            "long": "中长期影响取决于业绩改善是否可持续，以及估值是否已经充分反映增长预期。",
        },
        "政策监管类": {
            "positive": "如果政策方向利好行业需求或降低经营不确定性，可能提升估值修复空间。",
            "negative": "监管、处罚、调查或制裁可能带来合规成本、业务限制和估值折价。",
            "verify": "需要验证政策文件、监管口径、执行范围、影响周期和公司实际暴露程度。",
            "short": "短期情绪可能快速受政策标题影响，波动和风险偏好变化会被放大。",
            "long": "中长期影响取决于政策是否改变行业竞争格局、盈利模式或业务边界。",
        },
        "产品订单类": {
            "positive": "新产品、订单或大客户合同可能提升收入可见度，并强化市场对增长路径的信心。",
            "negative": "订单兑现、交付能力、毛利率、客户集中度和产能约束仍可能削弱实际贡献。",
            "verify": "需要验证订单金额、交付节奏、毛利率、客户结构和收入确认方式。",
            "short": "短期可能提升题材热度和交易活跃度，尤其在成交量同步放大时更明显。",
            "long": "中长期影响取决于订单是否转化为可持续收入和利润，而不是一次性事件。",
        },
        "融资资本类": {
            "positive": "回购、增持、分红或合理融资可能改善资本结构、股东回报或现金储备。",
            "negative": "增发、减持、债务压力或高成本融资可能带来股本摊薄和市场信心压力。",
            "verify": "需要验证融资规模、用途、价格、股本摊薄、现金流改善和资本结构变化。",
            "short": "短期交易情绪通常关注回购/增持的信号意义，以及减持/增发的供给压力。",
            "long": "中长期影响取决于资本动作是否提升公司竞争力、现金流和股东回报质量。",
        },
        "行业景气类": {
            "positive": "需求改善、涨价、库存去化或出口增长可能改善收入和利润率预期。",
            "negative": "降价、库存压力、价格战和供给扩张可能压缩利润并加剧竞争。",
            "verify": "需要验证供需数据、价格趋势、库存周期、竞争格局和出口政策。",
            "short": "短期可能驱动板块联动和风格切换，相关股票容易同涨同跌。",
            "long": "中长期影响取决于行业景气是否持续，以及公司是否具备成本、品牌或技术优势。",
        },
        "市场交易类": {
            "positive": "放量突破或资金流入可能强化趋势交易信号，提高短期关注度。",
            "negative": "跌破关键位置、放量下跌或高换手回落可能意味着情绪退潮和回撤风险。",
            "verify": "需要验证成交量、换手率、关键均线、支撑压力位和后续价格确认。",
            "short": "短期影响主要体现在交易情绪、趋势延续和波动率变化。",
            "long": "中长期基本面影响有限，除非交易信号背后有基本面或事件催化支撑。",
        },
        "未分类事件": {
            "positive": "事件描述暂未匹配到明确类别，可能仍包含潜在利好线索。",
            "negative": "分类不明确会降低规则解释的可靠性，容易误判事件性质。",
            "verify": "需要补充事件来源、发生时间、影响范围和公司公告依据。",
            "short": "短期影响暂不明确，需要观察价格和成交量是否有异常反应。",
            "long": "中长期影响暂不明确，需要结合财报、行业数据和管理层说明判断。",
        },
    }

    result = rules[event_type]
    if analysis_style == "保守解读":
        style_note = "当前采用保守解读，应优先确认风险、数据来源和事件兑现概率。"
    elif analysis_style == "积极解读":
        style_note = "当前采用积极解读，可关注事件带来的增长弹性，但仍需验证兑现能力。"
    else:
        style_note = "当前采用中性解读，正面线索和负面风险需要同时跟踪。"

    return {
        "事件类型": event_type,
        "可能正面影响": result["positive"],
        "可能负面风险": result["negative"],
        "需要进一步验证的数据": result["verify"],
        "对短期交易情绪的可能影响": f"{result['short']} {style_note}",
        "对中长期基本面的可能影响": result["long"],
    }


def generate_integrated_conclusion(
    rating,
    rating_reasons,
    technical_summary,
    fundamental_summary,
    sector_summary,
    event_analysis,
):
    event_text = (
        f"事件面识别为 {event_analysis['事件类型']}，需要结合公告和数据验证。"
        if event_analysis
        else "事件面暂无手动输入，近期消息仅作为辅助观察。"
    )

    return {
        "技术面结论": technical_summary["趋势判断"],
        "基本面结论": fundamental_summary.get("估值观察", fundamental_summary.get("数据可信度提示", MISSING)),
        "板块结论": sector_summary["行业逻辑简述"],
        "事件面结论": event_text,
        "综合观察评级": rating,
        "评级依据": rating_reasons,
        "免责声明": "该综合结论由本地规则生成，不构成投资建议。",
    }


def truncate_text(text, limit=300):
    if is_missing(text):
        return MISSING
    text = str(text)
    return text if len(text) <= limit else f"{text[:limit]}..."


st.set_page_config(page_title="FinScientist", page_icon="📈", layout="wide")

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

st.title("FinScientist")
st.subheader("AI-assisted financial research workspace")
st.caption("V0.7 新增简单策略回测模块；仍为本地规则化研究原型，不调用 AI API。")

with st.sidebar:
    st.header("研究参数")
    market = st.selectbox("市场类型", options=MARKET_OPTIONS, index=0)
    input_mode = st.radio("输入方式", options=["股票代码", "股票名称"], horizontal=True)
    user_input = st.text_input(
        "股票代码或股票名称",
        value="NVDA" if input_mode == "股票代码" else "英伟达",
        placeholder="例如：NVDA、0700、600519、英伟达、贵州茅台",
    )
    period_label = st.selectbox("时间范围", options=list(PERIOD_OPTIONS.keys()), index=2)
    analysis_style = st.selectbox("分析风格", options=ANALYSIS_STYLES, index=0)
    dimensions = st.multiselect(
        "分析维度",
        options=ANALYSIS_DIMENSIONS,
        default=["趋势", "波动", "基本面", "板块", "风险"],
    )
    show_description = st.checkbox("显示公司简介", value=True)
    show_financials = st.checkbox("显示财务摘要", value=True)
    show_sector = st.checkbox("显示板块观察", value=True)
    show_events = st.checkbox("显示近期重大消息", value=True)
    enable_manual_event = st.checkbox("启用手动事件分析", value=True)
    event_analysis_style = st.selectbox(
        "事件分析风格",
        options=["保守解读", "中性解读", "积极解读"],
        index=1,
    )
    manual_event_text = st.text_area(
        "手动输入重大事件",
        placeholder="例如：公司发布超预期财报，AI 服务器需求持续增长，管理层上调全年收入指引。",
        height=120,
    )
    run_button = st.button("生成研究工作台", type="primary")

    st.divider()
    st.header("多股票对比")
    comparison_input = st.text_area(
        "多股票代码",
        value="NVDA, AAPL, MSFT",
        help="可用英文逗号、中文逗号、空格或换行分隔多个股票代码。美股输入 NVDA；港股输入 0700；A股输入 600519。",
        height=90,
    )
    comparison_market = st.selectbox("多股票市场类型", options=MARKET_OPTIONS, index=0)
    run_comparison_button = st.button("运行多股票对比")
    add_current_button = st.button("加入当前标的到自选股")
    st.caption(f"当前自选股数量：{len(st.session_state.watchlist)}")
    if st.session_state.watchlist:
        st.write("、".join(st.session_state.watchlist))
    run_watchlist_comparison_button = st.button(
        "基于自选股运行对比",
        disabled=not bool(st.session_state.watchlist),
    )
    clear_watchlist_button = st.button(
        "清空自选股",
        disabled=not bool(st.session_state.watchlist),
    )

    st.divider()
    st.header("策略回测")
    enable_backtest = st.checkbox("启用策略回测", value=True)
    backtest_strategy = st.selectbox("回测策略", options=BACKTEST_STRATEGIES, index=0)
    initial_capital = st.number_input("初始资金", min_value=10000, value=100000, step=10000)
    trading_cost = st.number_input(
        "单边交易成本",
        min_value=0.0,
        max_value=0.05,
        value=0.001,
        step=0.0005,
        format="%.4f",
        help="例如 0.001 表示单边交易成本 0.1%。",
    )
    backtest_period_label = st.selectbox("回测时间范围", options=BACKTEST_PERIOD_OPTIONS, index=1)
    run_backtest_button = st.button("运行回测", disabled=not enable_backtest)

if clear_watchlist_button:
    clear_watchlist()
    st.success("已清空自选股列表。")

selected_market = market
raw_symbol = ""
symbol = ""
input_error = ""
if not user_input.strip():
    input_error = "请输入股票代码或股票名称。"
elif input_mode == "股票名称":
    resolved = resolve_name_to_ticker(user_input)
    if not resolved:
        input_error = "当前版本暂不支持该名称搜索，请改用股票代码输入。"
    else:
        selected_market, raw_symbol = resolved
else:
    raw_symbol = user_input

if raw_symbol:
    symbol = normalize_ticker(raw_symbol, selected_market)

if add_current_button:
    if symbol:
        add_to_watchlist(symbol)
        st.success(f"已加入自选股：{symbol}")
    else:
        st.warning(input_error or "请输入有效股票代码后再加入自选股。")

comparison_tickers = []
if run_comparison_button:
    comparison_tickers = parse_ticker_list(comparison_input, comparison_market)
    if not comparison_tickers:
        st.warning("请输入至少一只股票代码后再运行多股票对比。")
elif run_watchlist_comparison_button:
    comparison_tickers = parse_ticker_list(" ".join(st.session_state.watchlist), comparison_market)
    if not comparison_tickers:
        st.warning("当前暂无可用于对比的自选股。")

if not run_button:
    if comparison_tickers:
        render_watchlist_panel()
        render_comparison_section(comparison_tickers, comparison_market, period_label)
        if run_backtest_button:
            run_backtest_section(symbol, selected_market, backtest_strategy, backtest_period_label, initial_capital, trading_cost)
    elif run_backtest_button:
        render_watchlist_panel()
        run_backtest_section(symbol, selected_market, backtest_strategy, backtest_period_label, initial_capital, trading_cost)
    else:
        st.info("在侧边栏选择市场和输入方式后，点击“生成研究工作台”；也可以直接运行多股票对比或策略回测。")
        render_watchlist_panel()
    st.stop()

if input_error:
    st.warning(input_error)
    st.stop()

if not symbol:
    st.warning("请输入股票代码。")
    st.stop()

try:
    with st.spinner(f"正在获取 {selected_market} 标的 {symbol} 数据..."):
        price_data = fetch_market_data(symbol, selected_market, period_label)
        source_info = (
            fetch_a_share_info(symbol)
            if selected_market == "A股"
            else fetch_yfinance_info(symbol)
        )
except Exception as exc:
    st.error(f"未获取到数据，请检查代码、市场类型或网络连接。错误信息：{exc}")
    st.stop()

if price_data.empty or "Close" not in price_data.columns:
    st.error("未获取到数据，请检查代码、市场类型或网络连接")
    st.stop()

metrics = calculate_indicators(price_data)
profile = fetch_company_profile(symbol, selected_market, source_info)
valuation = fetch_valuation_metrics(symbol, selected_market, source_info, metrics)
financial = fetch_financial_snapshot(selected_market, source_info)
rating, rating_reasons = generate_rating(metrics)
technical_summary = generate_technical_summary(metrics, analysis_style)
fundamental_summary = generate_fundamental_summary(valuation, financial)
sector_summary = generate_sector_summary(profile)
news_items = fetch_news(symbol, selected_market, limit=5)
manual_event_type = classify_event(manual_event_text) if manual_event_text.strip() else "未分类事件"
manual_event_analysis = (
    generate_event_analysis(manual_event_text, manual_event_type, event_analysis_style)
    if enable_manual_event
    else None
)
conclusion = generate_integrated_conclusion(
    rating,
    rating_reasons,
    technical_summary,
    fundamental_summary,
    sector_summary,
    manual_event_analysis,
)

st.divider()
st.header("标的基础信息")
st.caption(f"用户输入：{user_input} | 实际查询代码：{symbol} | 市场类型：{selected_market}")

info_cols = st.columns(4)
info_cols[0].metric("公司名称", profile["company_name"])
info_cols[1].metric("交易所", profile["exchange"])
info_cols[2].metric("国家/地区", profile["country"])
info_cols[3].metric("员工数量", format_large_number(profile["employees"]))

info_cols_2 = st.columns(4)
info_cols_2[0].metric("行业", profile["industry"])
info_cols_2[1].metric("板块", profile["sector"])
info_cols_2[2].metric("官网", profile["website"])
info_cols_2[3].metric("英文名称/简称", profile["short_name"])

if show_description:
    st.write("公司简介")
    st.write(truncate_text(profile["description"]))

st.divider()
st.header("核心价格指标")
price_cols = st.columns(5)
price_cols[0].metric("最新收盘价", format_price(metrics["latest_close"]))
price_cols[1].metric("近5日涨跌幅", format_percent(metrics["return_5d"]))
price_cols[2].metric("近20日涨跌幅", format_percent(metrics["return_20d"]))
price_cols[3].metric("近60日涨跌幅", format_percent(metrics["return_60d"]))
price_cols[4].metric("近120日涨跌幅", format_percent(metrics["return_120d"]))

risk_cols = st.columns(5)
risk_cols[0].metric("年化波动率", format_percent(metrics["annual_volatility"]))
risk_cols[1].metric("最大回撤", format_percent(metrics["max_drawdown"]))
risk_cols[2].metric("区间最高价", format_price(metrics["range_high"]))
risk_cols[3].metric("区间最低价", format_price(metrics["range_low"]))
risk_cols[4].metric("近20日平均成交量", format_large_number(metrics["avg_volume_20d"]))

st.divider()
st.header("均线与趋势指标")
ma_cols = st.columns(6)
ma_cols[0].metric("5日均线", format_price(metrics["ma_5d"]))
ma_cols[1].metric("20日均线", format_price(metrics["ma_20d"]))
ma_cols[2].metric("60日均线", format_price(metrics["ma_60d"]))
ma_cols[3].metric("120日均线", format_price(metrics["ma_120d"]))
ma_cols[4].metric("相对20日均线偏离", format_percent(metrics["bias_20d"]))
ma_cols[5].metric("相对60日均线偏离", format_percent(metrics["bias_60d"]))
trend_text = describe_trend(metrics)
st.write(trend_text)

st.divider()
st.header("估值指标")
valuation_cols = st.columns(5)
valuation_cols[0].metric("市值", format_large_number(valuation["market_cap"]))
valuation_cols[1].metric("PE", format_metric(valuation["pe"]))
valuation_cols[2].metric("Forward PE", format_metric(valuation["forward_pe"]))
valuation_cols[3].metric("PB", format_metric(valuation["pb"]))
valuation_cols[4].metric("PS", format_metric(valuation["ps"]))

valuation_cols_2 = st.columns(5)
valuation_cols_2[0].metric("股息率", format_percent(valuation["dividend_yield"], MISSING))
valuation_cols_2[1].metric("Beta", format_metric(valuation["beta"]))
valuation_cols_2[2].metric("52周最高价", format_price(valuation["high_52w"]))
valuation_cols_2[3].metric("52周最低价", format_price(valuation["low_52w"]))
valuation_cols_2[4].metric("目标价均值", format_price(valuation["target_mean_price"]))

if show_financials:
    st.divider()
    st.header("财务摘要")
    if all(is_missing(value) for value in financial.values()):
        st.info("当前暂未获取到可用财务摘要")
    else:
        financial_cols = st.columns(4)
        financial_cols[0].metric("总收入", format_large_number(financial["total_revenue"]))
        financial_cols[1].metric("毛利率", format_percent(financial["gross_margin"], MISSING))
        financial_cols[2].metric("EBITDA", format_large_number(financial["ebitda"]))
        financial_cols[3].metric("净利润率", format_percent(financial["net_income_margin"], MISSING))

        financial_cols_2 = st.columns(4)
        financial_cols_2[0].metric("总现金", format_large_number(financial["total_cash"]))
        financial_cols_2[1].metric("总债务", format_large_number(financial["total_debt"]))
        financial_cols_2[2].metric("自由现金流", format_large_number(financial["free_cash_flow"]))
        financial_cols_2[3].metric("ROE / ROA", format_percent(financial["roe_roa"], MISSING))

st.divider()
st.header("价格趋势图")
st.line_chart(build_price_frame(price_data))
st.write(trend_text)

st.divider()
st.header("技术面解释")
for title, content in technical_summary.items():
    st.subheader(title)
    st.write(content)

st.divider()
st.header("基本面解释")
for title, content in fundamental_summary.items():
    st.subheader(title)
    st.write(content)

if show_sector:
    st.divider()
    st.header("板块/行业观察")
    for title, content in sector_summary.items():
        st.subheader(title)
        st.write(content)

if show_events:
    st.divider()
    st.header("近期重大消息")
    st.caption("新闻数据可能不完整、延迟或缺失；当前模块仅用于学习演示。")

    if selected_market == "A股":
        st.info("A股实时新闻与公告将在后续版本接入，目前可使用下方手动事件输入进行分析。")
    elif news_items:
        news_frame = pd.DataFrame(news_items)
        st.dataframe(
            news_frame[["标题", "来源", "发布时间"]],
            hide_index=True,
            use_container_width=True,
        )
        with st.expander("新闻链接"):
            for item in news_items:
                link = item.get("链接", MISSING)
                if is_missing(link):
                    st.write(f"- {item['标题']}")
                else:
                    st.write(f"- [{item['标题']}]({link})")
    else:
        st.info("当前暂无可用新闻数据，可能是数据源限制或网络问题。")

if enable_manual_event:
    st.divider()
    st.header("手动事件分析")
    if manual_event_analysis:
        st.write("用户输入的事件")
        st.write(manual_event_text)
        for title, content in manual_event_analysis.items():
            st.subheader(title)
            st.write(content)
    else:
        st.info("可在侧边栏输入公司或行业事件，系统将基于本地规则生成事件解读。")

st.divider()
st.header("综合研究结论")
st.subheader("技术面结论")
st.write(conclusion["技术面结论"])
st.subheader("基本面结论")
st.write(conclusion["基本面结论"])
st.subheader("板块结论")
st.write(conclusion["板块结论"])
st.subheader("事件面结论")
st.write(conclusion["事件面结论"])
st.subheader("综合观察评级")
st.write(f"**{conclusion['综合观察评级']}**")
st.subheader("评级依据")
for item in conclusion["评级依据"]:
    st.write(f"- {item}")
st.caption(conclusion["免责声明"])

st.divider()
render_watchlist_panel()
if comparison_tickers:
    render_comparison_section(comparison_tickers, comparison_market, period_label)
if run_backtest_button:
    run_backtest_section(symbol, selected_market, backtest_strategy, backtest_period_label, initial_capital, trading_cost)

st.divider()
st.header("风险提示")
st.write("- yfinance / akshare 数据可能延迟、缺失或口径不一致。")
st.write("- A股、港股、美股的数据字段存在差异，跨市场指标不能简单横向比较。")
st.write("- 公司基本面字段可能存在缺失、滞后或数据源映射错误。")
st.write("- 新闻数据可能延迟、缺失或来源不完整。")
st.write("- 手动事件分析基于关键词规则，不代表真实因果判断。")
st.write("- 事件影响需要结合财报、公告、行业数据进一步验证。")
st.write("- 策略回测为简化教学模型，未考虑滑点、真实撮合、停牌、涨跌停和复权差异。")
st.write("- 回测结果不代表未来收益，交易成本也只是粗略估计。")
st.write("- 本项目目前是学习原型，不是正式投研系统。")
st.write("- 规则化摘要不能替代专业研究判断。")
st.write("- 本结果不构成投资建议。")
st.write("- 不应据此进行真实交易。")
