import math
from datetime import date

import akshare as ak
import pandas as pd
import streamlit as st
import yfinance as yf


APP_VERSION = "V0.5"
MISSING = "数据暂缺"
INSUFFICIENT = "数据不足"

MARKET_OPTIONS = ["美股", "港股", "A股"]
PERIOD_OPTIONS = {"3个月": "3mo", "6个月": "6mo", "1年": "1y", "2年": "2y"}
PERIOD_MONTHS = {"3个月": 3, "6个月": 6, "1年": 12, "2年": 24}
ANALYSIS_STYLES = ["稳健型", "成长型", "短线交易型"]
ANALYSIS_DIMENSIONS = ["趋势", "波动", "估值", "成交量", "基本面", "板块", "风险"]

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

st.title("FinScientist")
st.subheader("AI-assisted financial research workspace")
st.caption("V0.5 增强近期重大消息与事件驱动分析，但仍为本地规则化研究原型，不调用 AI API。")

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

if not run_button:
    st.info("在侧边栏选择市场和输入方式后，点击“生成研究工作台”。")
    st.stop()

if not user_input.strip():
    st.warning("请输入股票代码或股票名称。")
    st.stop()

selected_market = market
if input_mode == "股票名称":
    resolved = resolve_name_to_ticker(user_input)
    if not resolved:
        st.warning("当前版本暂不支持该名称搜索，请改用股票代码输入。")
        st.stop()
    selected_market, raw_symbol = resolved
else:
    raw_symbol = user_input

symbol = normalize_ticker(raw_symbol, selected_market)
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
st.header("风险提示")
st.write("- yfinance / akshare 数据可能延迟、缺失或口径不一致。")
st.write("- A股、港股、美股的数据字段存在差异，跨市场指标不能简单横向比较。")
st.write("- 公司基本面字段可能存在缺失、滞后或数据源映射错误。")
st.write("- 新闻数据可能延迟、缺失或来源不完整。")
st.write("- 手动事件分析基于关键词规则，不代表真实因果判断。")
st.write("- 事件影响需要结合财报、公告、行业数据进一步验证。")
st.write("- 本项目目前是学习原型，不是正式投研系统。")
st.write("- 规则化摘要不能替代专业研究判断。")
st.write("- 本结果不构成投资建议。")
st.write("- 不应据此进行真实交易。")
