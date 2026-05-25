import math

import pandas as pd
import streamlit as st
import yfinance as yf


PERIOD_OPTIONS = {
    "3个月": "3mo",
    "6个月": "6mo",
    "1年": "1y",
    "2年": "2y",
}

ANALYSIS_STYLES = ["稳健型", "成长型", "短线交易型"]
ANALYSIS_DIMENSIONS = ["趋势", "波动", "估值", "成交量", "风险"]


def normalize_yfinance_data(data):
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = data.columns.get_level_values(0)
    return data


def format_price(value):
    if pd.isna(value):
        return "数据不足"
    return f"{value:.2f}"


def format_percent(value):
    if pd.isna(value):
        return "数据不足"
    return f"{value:.2%}"


def format_volume(value):
    if pd.isna(value):
        return "数据不足"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    return f"{value:,.0f}"


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


def calculate_metrics(data):
    close_prices = data["Close"].dropna() if "Close" in data else pd.Series(dtype=float)
    volume = data["Volume"].dropna() if "Volume" in data else pd.Series(dtype=float)
    daily_returns = close_prices.pct_change().dropna()

    latest_close = close_prices.iloc[-1] if len(close_prices) else math.nan
    ma_20d = close_prices.tail(20).mean() if len(close_prices) >= 20 else math.nan
    ma_60d = close_prices.tail(60).mean() if len(close_prices) >= 60 else math.nan

    return {
        "latest_close": latest_close,
        "return_20d": calculate_return(close_prices, 20),
        "return_60d": calculate_return(close_prices, 60),
        "ma_20d": ma_20d,
        "ma_60d": ma_60d,
        "annual_volatility": (
            daily_returns.std() * math.sqrt(252) if len(daily_returns) >= 20 else math.nan
        ),
        "max_drawdown": calculate_max_drawdown(close_prices),
        "high_52w": close_prices.tail(252).max() if len(close_prices) >= 252 else math.nan,
        "low_52w": close_prices.tail(252).min() if len(close_prices) >= 252 else math.nan,
        "avg_volume_20d": volume.tail(20).mean() if len(volume) >= 20 else math.nan,
    }


def build_price_frame(data):
    price_frame = pd.DataFrame(index=data.index)
    price_frame["收盘价"] = data["Close"]
    price_frame["20日均线"] = data["Close"].rolling(20).mean()
    price_frame["60日均线"] = data["Close"].rolling(60).mean()
    return price_frame


def describe_trend(metrics):
    latest_close = metrics["latest_close"]
    ma_20d = metrics["ma_20d"]
    ma_60d = metrics["ma_60d"]

    if pd.isna(latest_close) or pd.isna(ma_20d) or pd.isna(ma_60d):
        return "均线数据不足，暂时无法形成稳定趋势判断。"
    if latest_close > ma_20d and latest_close > ma_60d:
        return "当前价格高于20日和60日均线，短中期趋势偏强。"
    if latest_close < ma_20d and latest_close < ma_60d:
        return "当前价格低于主要均线，趋势偏弱。"
    return "当前价格在均线附近震荡，趋势中性。"


def build_rating(metrics):
    score = 0

    if not pd.isna(metrics["latest_close"]) and not pd.isna(metrics["ma_20d"]):
        score += 1 if metrics["latest_close"] > metrics["ma_20d"] else -1
    if not pd.isna(metrics["latest_close"]) and not pd.isna(metrics["ma_60d"]):
        score += 1 if metrics["latest_close"] > metrics["ma_60d"] else -1
    if not pd.isna(metrics["return_60d"]):
        score += 1 if metrics["return_60d"] > 0 else -1
    if not pd.isna(metrics["max_drawdown"]) and metrics["max_drawdown"] < -0.25:
        score -= 1
    if not pd.isna(metrics["annual_volatility"]) and metrics["annual_volatility"] > 0.45:
        score -= 1

    if score >= 2:
        return "强势观察"
    if score <= -2:
        return "风险观察"
    return "中性观察"


def describe_volatility(metrics, analysis_style):
    volatility = metrics["annual_volatility"]
    max_drawdown = metrics["max_drawdown"]

    if pd.isna(volatility):
        return "波动率数据不足，风险水平暂时无法稳定估计。"

    if analysis_style == "稳健型" and volatility > 0.35:
        style_note = "对稳健型分析而言，该波动水平需要提高风险折扣。"
    elif analysis_style == "短线交易型" and volatility > 0.45:
        style_note = "对短线交易型分析而言，高波动可能带来机会，也会放大止损压力。"
    elif analysis_style == "成长型" and volatility > 0.45:
        style_note = "成长型股票常伴随较高波动，但仍需验证基本面增长能否支撑估值。"
    else:
        style_note = "当前波动水平需结合仓位、持有周期和市场环境一起判断。"

    return (
        f"年化波动率为 {format_percent(volatility)}，最大回撤为 "
        f"{format_percent(max_drawdown)}。{style_note}"
    )


def describe_price_position(metrics):
    latest_close = metrics["latest_close"]
    high_52w = metrics["high_52w"]
    low_52w = metrics["low_52w"]

    if pd.isna(latest_close) or pd.isna(high_52w) or pd.isna(low_52w):
        return "52周高低点数据不足，价格位置暂时无法完整判断。"

    if high_52w == low_52w:
        return "52周价格区间过窄，价格位置参考意义有限。"

    position = (latest_close - low_52w) / (high_52w - low_52w)
    if position > 0.75:
        return "当前价格位于52周区间偏高位置，需关注高位回撤风险。"
    if position < 0.25:
        return "当前价格位于52周区间偏低位置，需判断是修复机会还是基本面压力。"
    return "当前价格位于52周区间中部，价格位置相对中性。"


def build_research_summary(ticker, metrics, analysis_style, dimensions):
    trend_text = describe_trend(metrics)
    volatility_text = describe_volatility(metrics, analysis_style)
    position_text = describe_price_position(metrics)
    rating = build_rating(metrics)
    dimensions_text = "、".join(dimensions) if dimensions else "未选择具体维度"

    if rating == "强势观察":
        overall_text = "规则显示短中期结构相对积极，但仍需确认成交量、财报和市场环境。"
    elif rating == "风险观察":
        overall_text = "规则显示风险因素较多，适合降低预期并优先观察风险释放情况。"
    else:
        overall_text = "规则未形成单边结论，适合继续观察趋势确认和风险变化。"

    return {
        "趋势判断": trend_text,
        "波动风险": volatility_text,
        "价格位置": position_text,
        "综合观察": (
            f"{ticker} 的本地模拟评级为 **{rating}**。当前分析风格为"
            f" **{analysis_style}**，关注维度包括：{dimensions_text}。{overall_text}"
        ),
    }


st.set_page_config(page_title="FinScientist", page_icon="📈", layout="wide")

st.title("FinScientist")
st.subheader("AI-assisted financial research workspace")
st.caption("当前版本基于 yfinance 市场数据和本地规则生成摘要，不调用 AI API。")

with st.sidebar:
    st.header("研究参数")
    ticker = st.text_input("股票代码", value="NVDA", placeholder="例如：NVDA、AAPL、MSFT")
    period_label = st.selectbox("时间范围", options=list(PERIOD_OPTIONS.keys()), index=2)
    analysis_style = st.selectbox("分析风格", options=ANALYSIS_STYLES, index=0)
    dimensions = st.multiselect(
        "分析维度",
        options=ANALYSIS_DIMENSIONS,
        default=["趋势", "波动", "风险"],
    )
    run_button = st.button("生成研究工作台", type="primary")

if not run_button:
    st.info("在侧边栏设置研究参数后，点击“生成研究工作台”。")
    st.stop()

cleaned_ticker = ticker.strip().upper()
if not cleaned_ticker:
    st.warning("请输入股票代码。")
    st.stop()

try:
    with st.spinner(f"正在获取 {cleaned_ticker} 历史行情数据..."):
        stock_data = yf.download(
            cleaned_ticker,
            period=PERIOD_OPTIONS[period_label],
            interval="1d",
            progress=False,
            auto_adjust=False,
        )
        stock_data = normalize_yfinance_data(stock_data)
except Exception:
    st.error("未获取到数据，请检查股票代码或网络")
    st.stop()

if stock_data.empty or "Close" not in stock_data.columns:
    st.error("未获取到数据，请检查股票代码或网络")
    st.stop()

metrics = calculate_metrics(stock_data)
rating = build_rating(metrics)

st.divider()
st.header("核心指标")
rating_col, price_col, ret20_col, ret60_col = st.columns(4)
rating_col.metric("本地模拟评级", rating)
price_col.metric("最新收盘价", format_price(metrics["latest_close"]))
ret20_col.metric("近20日涨跌幅", format_percent(metrics["return_20d"]))
ret60_col.metric("近60日涨跌幅", format_percent(metrics["return_60d"]))

ma20_col, ma60_col, vol_col, drawdown_col = st.columns(4)
ma20_col.metric("20日均线", format_price(metrics["ma_20d"]))
ma60_col.metric("60日均线", format_price(metrics["ma_60d"]))
vol_col.metric("年化波动率", format_percent(metrics["annual_volatility"]))
drawdown_col.metric("最大回撤", format_percent(metrics["max_drawdown"]))

high_col, low_col, volume_col = st.columns(3)
high_col.metric("52周最高价", format_price(metrics["high_52w"]))
low_col.metric("52周最低价", format_price(metrics["low_52w"]))
volume_col.metric("近20日平均成交量", format_volume(metrics["avg_volume_20d"]))

st.divider()
st.header("价格趋势")
st.line_chart(build_price_frame(stock_data))
st.write(describe_trend(metrics))

st.divider()
st.header("规则化研究摘要")
summary = build_research_summary(cleaned_ticker, metrics, analysis_style, dimensions)
for title, content in summary.items():
    st.subheader(title)
    st.write(content)

st.divider()
st.header("风险提示")
st.write("- 数据源稳定性风险：第三方数据服务可能出现访问失败或接口变化。")
st.write("- yfinance 数据延迟或缺失风险：行情、成交量和历史价格可能延迟、不完整或不可用。")
st.write("- 单一技术指标误判风险：均线、涨跌幅和波动率不能单独决定投资价值。")
st.write("- 市场波动风险：宏观环境、财报、政策和流动性变化可能导致价格剧烈波动。")
st.write("- 本项目不构成投资建议：所有评级和摘要仅用于学习演示。")
