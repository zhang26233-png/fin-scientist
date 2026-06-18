"""Compatibility layer for the pre-module FinScientist implementation.

This file is not a backup. In V2.0.0 it is the explicit compatibility layer for
the old research workbench, the legacy screening renderer, and network-adjacent
fetch orchestration that has not yet been migrated. Keep changes conservative;
future releases should move functions into config/, data/, core/, and ui/ in
small batches after focused tests exist.
"""

import math
import os
import re
import time
from datetime import date

import akshare as ak
import pandas as pd
import streamlit as st
import yfinance as yf

try:
    import baostock as bs
except Exception:
    bs = None

APP_VERSION = "v7.0.3"
LEGACY_COMPATIBILITY_SURFACE = (
    "render_legacy_workbench",
    "render_legacy_app",
    "render_screening_section",
    "calculate_indicators",
    "calculate_backtest_metrics",
    "generate_backtest_signals",
    "check_price_data_quality",
    "fetch_market_data",
    "fetch_screening_price_data",
    "get_fundamental_data",
    "fetch_a_share_fundamental_data",
)
MISSING = "数据暂缺"
INSUFFICIENT = "数据不足"

MARKET_OPTIONS = ["美股", "港股", "A股"]
PERIOD_OPTIONS = {"3个月": "3mo", "6个月": "6mo", "1年": "1y", "2年": "2y", "5年": "5y"}
PERIOD_MONTHS = {"3个月": 3, "6个月": 6, "1年": 12, "2年": 24, "5年": 60}
ANALYSIS_STYLES = ["稳健型", "成长型", "短线交易型"]
ANALYSIS_DIMENSIONS = ["趋势", "波动", "估值", "成交量", "基本面", "板块", "风险"]
BACKTEST_STRATEGIES = ["均线趋势策略", "双均线策略", "动量策略"]
BACKTEST_PERIOD_OPTIONS = ["6个月", "1年", "2年", "5年"]
SCREENING_MARKET_OPTIONS = ["A股", "港股", "美股"]
SCREENING_POOL_OPTIONS = ["默认示例股票池", "自定义股票池"]
SCREENING_TOP_OPTIONS = ["Top 10", "Top 20", "Top 30"]
SCREENING_MAX_PROCESS_OPTIONS = [10, 20, 30, 50]
SCREENING_RUN_MODE_OPTIONS = ["快速模式", "完整模式"]
A_SHARE_SCREENING_SOURCE_MODES = [
    "自动：AkShare → BaoStock → yfinance",
    "仅 AkShare",
    "仅 BaoStock",
    "仅 yfinance",
]
from config.stock_pools import A_SHARE_SCREENING_POOLS, DEFAULT_A_SHARE_POOL_TYPE, DEFAULT_SCREENING_UNIVERSES, get_default_universe
from config.stock_names import A_SHARE_STOCK_NAME_MAP, get_stock_display_name
from config.sector_mapping import A_SHARE_SECTOR_INFO_MAP, attach_sector_fields, get_stock_sector_info
from config.fundamental_samples import FUNDAMENTAL_SAMPLE_DATA
from core.scoring import FUNDAMENTAL_FIELDS, calculate_composite_research_score, calculate_fundamental_quality_score, calculate_research_priority_score
from core.sector_strength import generate_sector_strength_summary, generate_sector_strength_text
from core.explanations import generate_fundamental_summary, generate_screening_risk_warnings, generate_screening_summary, generate_selection_reasons, join_explanation_items
from data.market_data import convert_a_share_to_baostock_code, convert_a_share_to_yfinance_ticker, get_screening_fallback_source, infer_a_share_yfinance_suffix, keep_recent_rows, normalize_a_share_symbol_for_akshare, normalize_a_share_symbol_for_yfinance, normalize_hk_symbol_for_akshare, normalize_price_dataframe, normalize_yfinance_data
from data.fundamental_data import build_fundamental_record, clean_metric_value, get_fundamental_sample_data
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


def parse_display_percent(value):
    if is_missing(value):
        return math.nan
    text = str(value).strip()
    if text.endswith("%"):
        return to_number(text[:-1]) / 100
    return to_number(value)


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


def validate_ticker_input(raw_ticker, market):
    ticker = (raw_ticker or "").strip().upper()
    if not ticker:
        return False, "股票代码不能为空。"
    if len(ticker) > 20:
        return False, "股票代码过长，请检查输入。"
    if market == "A股":
        clean_ticker = ticker.replace(".SS", "").replace(".SZ", "")
        if not re.fullmatch(r"\d{6}", clean_ticker):
            return False, "A股代码应为 6 位数字，例如 600519、000001。"
        return True, ""
    if market == "港股":
        clean_ticker = ticker.replace(".HK", "")
        if not re.fullmatch(r"\d{1,5}", clean_ticker):
            return False, "港股代码应为数字，例如 0700、9988、3690。"
        return True, ""
    if not re.fullmatch(r"[A-Z0-9.\-]{1,12}", ticker):
        return False, "美股代码仅支持字母、数字、点号和短横线，例如 NVDA、BRK-B。"
    return True, ""


def validate_name_input(name):
    clean_name = (name or "").strip()
    if not clean_name:
        return False, "股票名称不能为空。"
    if len(clean_name) > 30:
        return False, "股票名称过长，请改用股票代码。"
    if re.search(r"[<>{}\\[\];`$]", clean_name):
        return False, "股票名称包含不支持的特殊字符，请检查输入。"
    return True, ""


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




def get_data_source(market):
    if market == "A股":
        return "AkShare"
    if market == "港股":
        return "AkShare 优先，yfinance 备用"
    return "yfinance"


def get_market_currency(market):
    if market == "美股":
        return "USD"
    if market == "港股":
        return "HKD"
    if market == "A股":
        return "CNY"
    return MISSING


def get_primary_source(market):
    if market == "美股":
        return "yfinance"
    if market in ("港股", "A股"):
        return "AkShare"
    return "数据源默认"


def get_fallback_source(market):
    return "yfinance" if market == "港股" else "无"




def is_network_error_message(error_text):
    text = str(error_text or "").lower()
    network_keywords = [
        "connection aborted",
        "remotedisconnected",
        "connectionreseterror",
        "forcibly closed",
        "远程主机强迫关闭",
        "without response",
        "connection reset",
        "timeout",
        "timed out",
        "proxy",
        "ssl",
    ]
    return any(keyword in text for keyword in network_keywords)


def get_network_diagnostic_text():
    return "AkShare 网络连接失败或远端断开，可能与接口稳定性、请求频率、代理/VPN 或网络环境有关。"




def check_data_freshness(price_df, market_type):
    if price_df is None or price_df.empty:
        return {
            "latest_trade_date": INSUFFICIENT,
            "days_since_latest": math.nan,
            "freshness_note": "未获取到最新交易日，无法判断数据时效性。",
        }

    try:
        dates = pd.to_datetime(price_df["Date"] if "Date" in price_df else price_df.index, errors="coerce")
        dates = pd.Series(dates).dropna()
        if dates.empty:
            raise ValueError("empty dates")
        latest_trade_date = dates.max().date()
        days_since_latest = (date.today() - latest_trade_date).days
    except Exception:
        return {
            "latest_trade_date": INSUFFICIENT,
            "days_since_latest": math.nan,
            "freshness_note": "交易日期字段不可用，无法判断数据时效性。",
        }

    if days_since_latest <= 5:
        note = "数据时效性正常，但免费数据源仍可能存在延迟。"
    elif days_since_latest <= 15:
        note = "最新交易日距离当前日期较久，数据可能不是最新。"
    else:
        note = "数据明显滞后，请检查代码、市场类型或数据源。"

    return {
        "latest_trade_date": latest_trade_date.strftime("%Y-%m-%d"),
        "days_since_latest": days_since_latest,
        "freshness_note": f"{note} 不同市场存在节假日差异，本提示仅用于风险识别。",
    }


def build_data_source_meta(
    price_df,
    market,
    primary_source,
    fallback_source,
    actual_source,
    fallback_used=False,
    adjustment="数据源默认口径",
    source_warning=None,
):
    freshness = check_data_freshness(price_df, market)
    warning = source_warning or "免费数据源可能延迟、缺失，且不同来源的复权口径和字段口径可能不一致。"
    if fallback_used and source_warning is None:
        warning = f"主数据源 {primary_source} 获取失败，当前使用备用数据源 {actual_source}。{warning}"
    return {
        "primary_source": primary_source,
        "fallback_source": fallback_source or "无",
        "actual_source": actual_source or "无",
        "fallback_used": bool(fallback_used),
        "latest_trade_date": freshness["latest_trade_date"],
        "data_frequency": "日线",
        "currency": get_market_currency(market) or "数据源默认",
        "adjustment": adjustment or "数据源默认口径",
        "freshness_note": freshness["freshness_note"],
        "source_warning": warning,
    }


def get_price_data_metadata(data, symbol, market):
    source_meta = data.attrs.get("data_source_meta", {}) if data is not None else {}
    clean_index = pd.to_datetime(data.index, errors="coerce") if data is not None and not data.empty else pd.Index([])
    clean_index = pd.Series(clean_index).dropna()
    return {
        "数据来源": source_meta.get("actual_source", get_data_source(market)),
        "主数据源": source_meta.get("primary_source", get_primary_source(market)),
        "备用数据源": source_meta.get("fallback_source", get_fallback_source(market)),
        "是否使用备用源": "是" if source_meta.get("fallback_used") else "否",
        "最近更新时间": source_meta.get("latest_trade_date") or (clean_index.max().strftime("%Y-%m-%d") if len(clean_index) else INSUFFICIENT),
        "市场类型": market,
        "币种": source_meta.get("currency", get_market_currency(market)),
        "数据频率": source_meta.get("data_frequency", "日线"),
        "复权口径": source_meta.get("adjustment", "数据源默认口径"),
        "时效性说明": source_meta.get("freshness_note", check_data_freshness(data, market)["freshness_note"]),
        "数据源风险提示": source_meta.get("source_warning", "免费数据源可能延迟、缺失或口径不一致。"),
        "起始日期": clean_index.min().strftime("%Y-%m-%d") if len(clean_index) else INSUFFICIENT,
        "结束日期": clean_index.max().strftime("%Y-%m-%d") if len(clean_index) else INSUFFICIENT,
        "实际查询代码": symbol,
    }


def check_price_data_quality(data):
    report = generate_data_quality_report(data)
    return {
        "数据行数": report["总交易日数量"],
        "缺失收盘价数量": report["收盘价为空的行数"],
        "重复日期数量": report["重复日期数量"],
        "异常日涨跌幅数量": report["单日涨跌幅超过20%的异常记录数量"],
        "质量提示": report["数据质量结论"],
    }


def generate_data_quality_report(price_df):
    if price_df is None or price_df.empty:
        return {
            "数据起始日期": INSUFFICIENT,
            "数据结束日期": INSUFFICIENT,
            "总交易日数量": 0,
            "缺失值总数": INSUFFICIENT,
            "重复日期数量": INSUFFICIENT,
            "收盘价为空的行数": INSUFFICIENT,
            "成交量为0的行数": INSUFFICIENT,
            "单日涨跌幅超过20%的异常记录数量": INSUFFICIENT,
            "是否足够计算MA20": "否",
            "是否足够计算MA60": "否",
            "是否足够计算MA120": "否",
            "是否足够计算年化波动率": "否",
            "是否足够计算最大回撤": "否",
            "数据质量结论": "数据不足，请谨慎使用",
        }

    data = price_df.copy()
    dates = pd.to_datetime(data["Date"] if "Date" in data else data.index, errors="coerce")
    valid_dates = pd.Series(dates).dropna()
    close_prices = pd.to_numeric(data["Close"], errors="coerce") if "Close" in data else pd.Series(index=data.index, dtype=float)
    volume = pd.to_numeric(data["Volume"], errors="coerce") if "Volume" in data else pd.Series(index=data.index, dtype=float)
    daily_returns = close_prices.pct_change(fill_method=None).replace([math.inf, -math.inf], math.nan)

    total_days = int(len(data))
    missing_total = int(data.isna().sum().sum())
    duplicate_dates = int(pd.Series(dates).duplicated().sum()) + int(data.attrs.get("duplicate_dates_removed", 0))
    missing_close = int(close_prices.isna().sum())
    zero_volume = int((volume == 0).sum()) if "Volume" in data else INSUFFICIENT
    abnormal_count = int((daily_returns.abs() > 0.2).sum())
    valid_close_count = int(close_prices.dropna().shape[0])

    serious_issues = total_days < 20 or missing_close > 0.2 * max(total_days, 1)
    minor_issues = missing_total > 0 or duplicate_dates > 0 or abnormal_count > 0 or valid_close_count < 60
    if serious_issues:
        conclusion = "数据不足，请谨慎使用"
    elif minor_issues:
        conclusion = "数据基本可用但存在缺陷"
    else:
        conclusion = "数据较完整"

    return {
        "数据起始日期": valid_dates.min().strftime("%Y-%m-%d") if len(valid_dates) else INSUFFICIENT,
        "数据结束日期": valid_dates.max().strftime("%Y-%m-%d") if len(valid_dates) else INSUFFICIENT,
        "总交易日数量": total_days,
        "缺失值总数": missing_total,
        "重复日期数量": duplicate_dates,
        "收盘价为空的行数": missing_close,
        "成交量为0的行数": zero_volume,
        "单日涨跌幅超过20%的异常记录数量": abnormal_count,
        "是否足够计算MA20": "是" if valid_close_count >= 20 else "否",
        "是否足够计算MA60": "是" if valid_close_count >= 60 else "否",
        "是否足够计算MA120": "是" if valid_close_count >= 120 else "否",
        "是否足够计算年化波动率": "是" if valid_close_count >= 21 else "否",
        "是否足够计算最大回撤": "是" if valid_close_count >= 2 else "否",
        "数据质量结论": conclusion,
    }


def fetch_yfinance_history(symbol, period):
    data = yf.download(
        symbol,
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=False,
    )
    return normalize_price_dataframe(data)


def fetch_a_share_baostock_data(query_ticker, start_date, end_date):
    query_symbol = normalize_a_share_symbol_for_akshare(query_ticker)
    bs_code, code_error = convert_a_share_to_baostock_code(query_symbol)
    if code_error:
        empty = pd.DataFrame()
        empty.attrs.update(
            {
                "query_symbol": query_symbol,
                "baostock_code": "",
                "attempt_params": "BaoStock 未请求",
                "failure_stage": "BaoStock 代码转换失败",
                "error_message": code_error,
            }
        )
        return empty

    if bs is None:
        empty = pd.DataFrame()
        empty.attrs.update(
            {
                "query_symbol": query_symbol,
                "baostock_code": bs_code,
                "attempt_params": f"BaoStock({bs_code})",
                "failure_stage": "BaoStock 依赖不可用",
                "error_message": "未安装 baostock 依赖，请先安装 requirements.txt。",
            }
        )
        return empty

    login_result = None
    try:
        login_result = bs.login()
        if getattr(login_result, "error_code", "0") != "0":
            raise RuntimeError(getattr(login_result, "error_msg", "BaoStock 登录失败"))

        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,open,high,low,close,volume",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            frequency="d",
            adjustflag="2",
        )
        if getattr(rs, "error_code", "0") != "0":
            raise RuntimeError(getattr(rs, "error_msg", "BaoStock 查询失败"))

        rows = []
        while rs.next():
            rows.append(rs.get_row_data())
        if not rows:
            empty = pd.DataFrame()
            empty.attrs.update(
                {
                    "query_symbol": query_symbol,
                    "baostock_code": bs_code,
                    "attempt_params": f"BaoStock({bs_code}, adjustflag=2)",
                    "failure_stage": "BaoStock 返回空数据",
                    "error_message": "BaoStock 未返回可用历史行情。",
                }
            )
            return empty

        raw = pd.DataFrame(rows, columns=rs.fields)
        raw = raw.rename(
            columns={
                "date": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
        )
        data = normalize_price_dataframe(raw)
        if not data.empty:
            data = keep_recent_rows(data, 120)
        data.attrs.update(
            {
                "query_symbol": query_symbol,
                "baostock_code": bs_code,
                "attempt_params": f"BaoStock({bs_code}, adjustflag=2)",
                "successful_adjust": "BaoStock 后复权 adjustflag=2",
                "actual_query_symbol": bs_code,
            }
        )
        return data
    except Exception as exc:
        empty = pd.DataFrame()
        empty.attrs.update(
            {
                "query_symbol": query_symbol,
                "baostock_code": bs_code,
                "attempt_params": f"BaoStock({bs_code}, adjustflag=2)",
                "failure_stage": "BaoStock 请求失败",
                "error_message": str(exc),
            }
        )
        return empty
    finally:
        try:
            if login_result is not None and bs is not None:
                bs.logout()
        except Exception:
            pass


def fetch_a_share_history(symbol, period_label, lookback_days=None, limit_rows=None):
    end_date = date.today()
    start_date = (
        end_date - pd.DateOffset(days=lookback_days)
        if lookback_days
        else end_date - pd.DateOffset(months=PERIOD_MONTHS[period_label])
    )
    query_symbol = normalize_a_share_symbol_for_akshare(symbol)
    attempts = []
    last_error = ""

    if not re.fullmatch(r"\d{6}", query_symbol):
        empty = pd.DataFrame()
        empty.attrs.update(
            {
                "query_symbol": query_symbol,
                "attempt_params": "未请求",
                "failure_stage": "代码标准化失败",
                "error_message": "A股 AkShare 查询代码必须为 6 位数字。",
            }
        )
        return empty

    for adjust in ["", "qfq", "hfq"]:
        adjust_label = 'adjust=""' if adjust == "" else f'adjust="{adjust}"'
        attempts.append(adjust_label)
        try:
            raw = ak.stock_zh_a_hist(
                symbol=query_symbol,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust=adjust,
            )
        except Exception as exc:
            last_error = str(exc)
            if is_network_error_message(last_error):
                last_error = f"AkShare 网络连接异常：{last_error}"
            continue

        if raw is None or raw.empty:
            last_error = "AkShare 返回空数据"
            continue

        data = normalize_price_dataframe(raw)
        data.attrs["query_symbol"] = query_symbol
        data.attrs["attempt_params"] = ", ".join(attempts)
        data.attrs["successful_adjust"] = adjust_label

        if data.empty:
            data.attrs["failure_stage"] = "数据清洗后为空"
            data.attrs["error_message"] = "AkShare 返回数据在日期清洗后为空。"
            last_error = data.attrs["error_message"]
            continue
        if "Date" not in data.columns:
            data.attrs["failure_stage"] = "Date 字段缺失"
            data.attrs["error_message"] = "字段映射后缺少 Date 字段。"
            last_error = data.attrs["error_message"]
            continue
        if "Close" not in data.columns:
            data.attrs["failure_stage"] = "Close 字段缺失"
            data.attrs["error_message"] = "字段映射后缺少 Close 字段。"
            last_error = data.attrs["error_message"]
            continue
        if "Volume" not in data.columns:
            data["Volume"] = math.nan
            data.attrs["volume_warning"] = "Volume 字段缺失，已用空值占位。"

        if limit_rows:
            data = data.tail(limit_rows)
            data.attrs["query_symbol"] = query_symbol
            data.attrs["attempt_params"] = ", ".join(attempts)
            data.attrs["successful_adjust"] = adjust_label
            data.attrs["volume_warning"] = data.attrs.get("volume_warning", "")
        return data

    empty = pd.DataFrame()
    empty.attrs.update(
        {
            "query_symbol": query_symbol,
            "attempt_params": ", ".join(attempts),
            "failure_stage": (
                "AkShare 网络请求失败"
                if is_network_error_message(last_error)
                else "AkShare 返回空数据" if last_error == "AkShare 返回空数据" else "AkShare 请求失败"
            ),
            "error_message": last_error or "AkShare 未返回可用数据。",
        }
    )
    return empty


def fetch_hk_akshare_history(symbol, period_label):
    end_date = date.today()
    start_date = end_date - pd.DateOffset(months=PERIOD_MONTHS[period_label])
    raw = ak.stock_hk_hist(
        symbol=normalize_hk_symbol_for_akshare(symbol),
        period="daily",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        adjust="qfq",
    )
    if raw.empty:
        return pd.DataFrame()
    return normalize_price_dataframe(raw)


def fetch_market_data(symbol, market, period_label):
    primary_source = get_primary_source(market)
    fallback_source = get_fallback_source(market)

    try:
        if market == "A股":
            data = fetch_a_share_history(symbol, period_label)
            data.attrs["data_source_meta"] = build_data_source_meta(
                data,
                market,
                primary_source,
                fallback_source,
                "AkShare" if not data.empty else "无",
                adjustment=data.attrs.get("successful_adjust", "AkShare 参数自动尝试"),
            )
            return data

        if market == "港股":
            try:
                data = fetch_hk_akshare_history(symbol, period_label)
                if not data.empty:
                    data.attrs["data_source_meta"] = build_data_source_meta(
                        data,
                        market,
                        primary_source,
                        fallback_source,
                        "AkShare",
                        fallback_used=False,
                        adjustment="前复权 qfq",
                    )
                    return data
            except Exception:
                data = pd.DataFrame()

            fallback_data = fetch_yfinance_history(normalize_ticker(symbol, "港股"), PERIOD_OPTIONS[period_label])
            fallback_data.attrs["data_source_meta"] = build_data_source_meta(
                fallback_data,
                market,
                primary_source,
                fallback_source,
                "yfinance" if not fallback_data.empty else "无",
                fallback_used=not fallback_data.empty,
                adjustment="yfinance 默认口径",
            )
            return fallback_data

        data = fetch_yfinance_history(symbol, PERIOD_OPTIONS[period_label])
        data.attrs["data_source_meta"] = build_data_source_meta(
            data,
            market,
            primary_source,
            fallback_source,
            "yfinance" if not data.empty else "无",
            adjustment="yfinance 默认口径",
        )
        return data
    except Exception:
        empty = pd.DataFrame()
        empty.attrs["data_source_meta"] = build_data_source_meta(
            empty,
            market,
            primary_source,
            fallback_source,
            "无",
            source_warning="主数据源和备用数据源均未返回可用行情，请检查代码、市场类型或网络连接。",
        )
        return empty


def compare_hk_sources_if_available(ticker):
    try:
        ak_data = fetch_hk_akshare_history(ticker, "6个月")
        yf_data = fetch_yfinance_history(normalize_ticker(ticker, "港股"), "6mo")
        if ak_data.empty or yf_data.empty or "Close" not in ak_data or "Close" not in yf_data:
            return {
                "status": "unavailable",
                "message": "主备数据源未能同时获取，暂无法完成交叉校验。",
            }

        ak_close = ak_data[["Date", "Close"]].dropna()
        yf_close = yf_data[["Date", "Close"]].dropna()
        if ak_close.empty or yf_close.empty:
            return {
                "status": "unavailable",
                "message": "主备数据源未能同时获取，暂无法完成交叉校验。",
            }

        merged = pd.merge(ak_close, yf_close, on="Date", how="inner", suffixes=("_akshare", "_yfinance"))
        if not merged.empty:
            compare_row = merged.sort_values("Date").iloc[-1]
            compare_date = compare_row["Date"]
            ak_price = compare_row["Close_akshare"]
            yf_price = compare_row["Close_yfinance"]
        else:
            ak_latest = ak_close.sort_values("Date").iloc[-1]
            yf_latest = yf_close.sort_values("Date").iloc[-1]
            compare_date = min(ak_latest["Date"], yf_latest["Date"])
            ak_price = ak_latest["Close"]
            yf_price = yf_latest["Close"]

        if pd.isna(ak_price) or pd.isna(yf_price) or yf_price == 0:
            raise ValueError("invalid compare price")
        diff_pct = abs(ak_price / yf_price - 1)
        if diff_pct <= 0.01:
            message = "AkShare 与 yfinance 最近收盘价差异较小。"
            status = "ok"
        else:
            message = "不同数据源存在超过 1% 的价格差异，请谨慎使用。"
            status = "warning"

        return {
            "status": status,
            "message": message,
            "compare_date": pd.to_datetime(compare_date).strftime("%Y-%m-%d"),
            "akshare_close": ak_price,
            "yfinance_close": yf_price,
            "diff_pct": diff_pct,
        }
    except Exception:
        return {
            "status": "unavailable",
            "message": "主备数据源未能同时获取，暂无法完成交叉校验。",
        }


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
    """Calculate point-to-point return over a fixed number of trading days."""
    clean_prices = pd.to_numeric(close_prices, errors="coerce").dropna()
    if len(clean_prices) <= days:
        return math.nan
    base_price = clean_prices.iloc[-days - 1]
    latest_price = clean_prices.iloc[-1]
    if pd.isna(base_price) or base_price == 0:
        return math.nan
    return latest_price / base_price - 1


def calculate_max_drawdown(close_prices):
    """Calculate the worst peak-to-trough drawdown for a price series."""
    clean_prices = pd.to_numeric(close_prices, errors="coerce").dropna()
    clean_prices = clean_prices[clean_prices > 0]
    if len(clean_prices) < 2:
        return math.nan
    running_high = clean_prices.cummax()
    drawdown = clean_prices / running_high - 1
    return drawdown.min()


def calculate_indicators(data):
    """Build the core technical indicator dictionary from historical prices."""
    close_prices = pd.to_numeric(data["Close"], errors="coerce").dropna() if "Close" in data else pd.Series(dtype=float)
    volume = pd.to_numeric(data["Volume"], errors="coerce").dropna() if "Volume" in data else pd.Series(dtype=float)
    daily_returns = close_prices.pct_change(fill_method=None).replace([math.inf, -math.inf], math.nan).dropna()
    latest_close = close_prices.iloc[-1] if len(close_prices) else math.nan
    ma_20d = close_prices.tail(20).mean() if len(close_prices) >= 20 else math.nan
    ma_60d = close_prices.tail(60).mean() if len(close_prices) >= 60 else math.nan

    return {
        "latest_close": latest_close,
        "return_5d": calculate_return(close_prices, 5),
        "return_20d": calculate_return(close_prices, 20),
        "return_60d": calculate_return(close_prices, 60),
        "return_120d": calculate_return(close_prices, 120),
        "ma_5d": close_prices.tail(5).mean() if len(close_prices) >= 5 else math.nan,
        "ma_20d": ma_20d,
        "ma_60d": ma_60d,
        "ma_120d": close_prices.tail(120).mean() if len(close_prices) >= 120 else math.nan,
        "bias_20d": latest_close / ma_20d - 1 if len(close_prices) >= 20 and ma_20d else math.nan,
        "bias_60d": latest_close / ma_60d - 1 if len(close_prices) >= 60 and ma_60d else math.nan,
        "annual_volatility": daily_returns.std() * math.sqrt(252) if len(daily_returns) >= 20 else math.nan,
        "max_drawdown": calculate_max_drawdown(close_prices),
        "range_high": close_prices.max() if len(close_prices) else math.nan,
        "range_low": close_prices.min() if len(close_prices) else math.nan,
        "high_52w": close_prices.tail(252).max() if len(close_prices) >= 60 else math.nan,
        "low_52w": close_prices.tail(252).min() if len(close_prices) >= 60 else math.nan,
        "avg_volume_20d": volume.tail(20).mean() if len(volume) >= 20 else math.nan,
        "data_points": len(close_prices),
    }




def format_screening_bool(value):
    if value is True:
        return "是"
    if value is False:
        return "否"
    return INSUFFICIENT


def calculate_screening_metrics(price_df):
    metrics = {
        "最新价格": math.nan,
        "近 5 日涨跌幅": math.nan,
        "近 20 日涨跌幅": math.nan,
        "近 60 日涨跌幅": math.nan,
        "MA20": math.nan,
        "MA60": math.nan,
        "当前价格是否高于 MA20": None,
        "当前价格是否高于 MA60": None,
        "MA20 是否高于 MA60": None,
        "最近 5 日平均成交量": math.nan,
        "最近 20 日平均成交量": math.nan,
        "成交量放大倍数": math.nan,
        "年化波动率": math.nan,
        "最大回撤": math.nan,
        "有效交易日数量": 0,
        "成交量数据缺失": True,
        "无法评分原因": "",
    }

    if price_df is None or price_df.empty:
        metrics["无法评分原因"] = "行情数据为空"
        return metrics
    if "Close" not in price_df.columns:
        metrics["无法评分原因"] = "Close 字段缺失"
        return metrics

    close_prices = pd.to_numeric(price_df["Close"], errors="coerce").dropna()
    close_prices = close_prices.replace([math.inf, -math.inf], math.nan).dropna()
    metrics["有效交易日数量"] = int(len(close_prices))
    if close_prices.empty:
        metrics["无法评分原因"] = "Close 字段无有效数据"
        return metrics

    latest_price = clean_metric_value(close_prices.iloc[-1])
    metrics["最新价格"] = latest_price
    metrics["近 5 日涨跌幅"] = clean_metric_value(calculate_return(close_prices, 5))
    metrics["近 20 日涨跌幅"] = clean_metric_value(calculate_return(close_prices, 20))
    metrics["近 60 日涨跌幅"] = clean_metric_value(calculate_return(close_prices, 60))
    metrics["MA20"] = clean_metric_value(close_prices.tail(20).mean()) if len(close_prices) >= 20 else math.nan
    metrics["MA60"] = clean_metric_value(close_prices.tail(60).mean()) if len(close_prices) >= 60 else math.nan
    metrics["年化波动率"] = clean_metric_value(
        close_prices.pct_change(fill_method=None).replace([math.inf, -math.inf], math.nan).dropna().std() * math.sqrt(252)
        if len(close_prices) >= 21
        else math.nan
    )
    metrics["最大回撤"] = clean_metric_value(calculate_max_drawdown(close_prices))

    if not pd.isna(latest_price) and not pd.isna(metrics["MA20"]):
        metrics["当前价格是否高于 MA20"] = latest_price > metrics["MA20"]
    if not pd.isna(latest_price) and not pd.isna(metrics["MA60"]):
        metrics["当前价格是否高于 MA60"] = latest_price > metrics["MA60"]
    if not pd.isna(metrics["MA20"]) and not pd.isna(metrics["MA60"]):
        metrics["MA20 是否高于 MA60"] = metrics["MA20"] > metrics["MA60"]

    if "Volume" in price_df.columns:
        volume = pd.to_numeric(price_df["Volume"], errors="coerce").replace([math.inf, -math.inf], math.nan).dropna()
        volume = volume[volume >= 0]
        if not volume.empty:
            metrics["成交量数据缺失"] = False
            metrics["最近 5 日平均成交量"] = clean_metric_value(volume.tail(5).mean()) if len(volume) >= 5 else math.nan
            metrics["最近 20 日平均成交量"] = clean_metric_value(volume.tail(20).mean()) if len(volume) >= 20 else math.nan
            avg_20 = metrics["最近 20 日平均成交量"]
            if not pd.isna(metrics["最近 5 日平均成交量"]) and not pd.isna(avg_20) and avg_20 > 0:
                metrics["成交量放大倍数"] = clean_metric_value(metrics["最近 5 日平均成交量"] / avg_20)

    if metrics["有效交易日数量"] < 20:
        metrics["无法评分原因"] = "有效交易日少于 20"
    return metrics




def fetch_a_share_fundamental_data(display_ticker, query_ticker):
    try:
        info = fetch_a_share_info(query_ticker)
        if not info:
            return None, "AkShare 未返回基础信息。"
        values = (
            to_number(safe_get(info, "总市值")) / 100000000 if not pd.isna(to_number(safe_get(info, "总市值"))) else MISSING,
            safe_get(info, "市盈率"),
            safe_get(info, "市净率"),
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
        )
        data = build_fundamental_record(values, "AkShare")
        if all(is_missing(data[field]) for field in FUNDAMENTAL_FIELDS):
            return None, "AkShare 基本面字段为空。"
        return data, ""
    except Exception as exc:
        return None, str(exc)


@st.cache_data(ttl=3600, show_spinner=False)
def get_fundamental_data(display_ticker, query_ticker, market):
    if market != "A股":
        return build_fundamental_record((), "数据暂缺", "港股和美股基本面筛选暂未启用。")
    ak_data, ak_error = fetch_a_share_fundamental_data(display_ticker, query_ticker)
    if ak_data:
        sample_data = get_fundamental_sample_data(display_ticker)
        if sample_data:
            for field in FUNDAMENTAL_FIELDS:
                if is_missing(ak_data.get(field)):
                    ak_data[field] = sample_data.get(field, MISSING)
            ak_data["fundamental_source"] = "AkShare + 内置示例数据"
            ak_data["fundamental_error"] = ak_error
        return ak_data
    sample_data = get_fundamental_sample_data(display_ticker)
    if sample_data:
        sample_data["fundamental_error"] = ak_error
        return sample_data
    return build_fundamental_record((), "数据暂缺", ak_error or "未找到可用基本面数据。")




def parse_ticker_list(input_text, market_type="美股"):
    raw_items = re.split(r"[,，\s]+", input_text or "")
    tickers = []
    seen = set()
    invalid_items = []

    for raw_item in raw_items:
        item = raw_item.strip().upper()
        if not item:
            continue
        is_valid, _ = validate_ticker_input(item, market_type)
        if not is_valid:
            invalid_items.append(item)
            continue
        normalized = normalize_ticker(item, market_type)
        if normalized and normalized not in seen:
            tickers.append(normalized)
            seen.add(normalized)

    if invalid_items:
        st.warning(f"以下代码格式不符合 {market_type} 规则，已跳过：{', '.join(invalid_items[:5])}")

    if len(tickers) > 10:
        st.warning("多股票对比最多支持 10 只股票，本次仅处理前 10 只。")
        tickers = tickers[:10]

    return tickers


def infer_a_share_suffix(ticker_digits):
    if ticker_digits.startswith("6"):
        return ".SH", "根据首位数字推断为上海市场。"
    if ticker_digits.startswith(("0", "3")):
        return ".SZ", "根据首位数字推断为深圳市场。"
    return "", "格式需进一步确认"


def normalize_screening_ticker(ticker, market):
    raw_value = str(ticker or "").strip()
    normalized = raw_value.upper()
    if not normalized:
        return attach_sector_fields({
            "原始输入": raw_value,
            "股票名称": "名称暂缺",
            "stock_name": "名称暂缺",
            "展示代码": "",
            "内部查询代码": "",
            "市场": market,
            "备注": "空代码，已跳过",
            "is_valid": False,
        }, raw_value, market)

    if market == "A股":
        clean_code = normalized.replace(".SH", "").replace(".SZ", "")
        if re.fullmatch(r"\d{6}", clean_code):
            suffix = ""
            note = "已标准化"
            if normalized.endswith(".SH"):
                suffix = ".SH"
            elif normalized.endswith(".SZ"):
                suffix = ".SZ"
            else:
                suffix, note = infer_a_share_suffix(clean_code)
            display_code = f"{clean_code}{suffix}" if suffix else raw_value
            stock_name = get_stock_display_name(display_code, market)
            return attach_sector_fields({
                "原始输入": raw_value,
                "股票名称": stock_name,
                "stock_name": stock_name,
                "展示代码": display_code,
                "内部查询代码": clean_code,
                "市场": market,
                "备注": note,
                "is_valid": bool(suffix),
            }, display_code, market)
        return attach_sector_fields({
            "原始输入": raw_value,
            "股票名称": "名称暂缺",
            "stock_name": "名称暂缺",
            "展示代码": raw_value,
            "内部查询代码": clean_code or raw_value,
            "市场": market,
            "备注": "格式需进一步确认",
            "is_valid": False,
        }, raw_value, market)

    if market == "港股":
        clean_code = normalized.replace(".HK", "")
        if re.fullmatch(r"\d{1,5}", clean_code):
            display_code = f"{clean_code.zfill(4)}.HK"
            return attach_sector_fields({
                "原始输入": raw_value,
                "股票名称": get_stock_display_name(display_code, market),
                "stock_name": get_stock_display_name(display_code, market),
                "展示代码": display_code,
                "内部查询代码": display_code,
                "市场": market,
                "备注": "已标准化",
                "is_valid": True,
            }, display_code, market)
        return attach_sector_fields({
            "原始输入": raw_value,
            "股票名称": "名称暂缺",
            "stock_name": "名称暂缺",
            "展示代码": raw_value,
            "内部查询代码": raw_value,
            "市场": market,
            "备注": "格式需进一步确认",
            "is_valid": False,
        }, raw_value, market)

    clean_code = normalized.strip()
    if re.fullmatch(r"[A-Z0-9.\-]{1,12}", clean_code):
        return attach_sector_fields({
            "原始输入": raw_value,
            "股票名称": get_stock_display_name(clean_code, market),
            "stock_name": get_stock_display_name(clean_code, market),
            "展示代码": clean_code,
            "内部查询代码": clean_code,
            "市场": market,
            "备注": "已标准化",
            "is_valid": True,
        }, clean_code, market)

    return attach_sector_fields({
        "原始输入": raw_value,
        "股票名称": "名称暂缺",
        "stock_name": "名称暂缺",
        "展示代码": raw_value,
        "内部查询代码": raw_value,
        "市场": market,
        "备注": "格式需进一步确认",
        "is_valid": False,
    }, raw_value, market)


def parse_screening_universe(input_text, market):
    raw_items = [item.strip() for item in re.split(r"[,，\s]+", input_text or "") if item.strip()]
    warnings = []
    parsed_items = []
    seen = set()

    if len(raw_items) > 50:
        warnings.append("股票池最多解析 50 只，本次仅保留前 50 只。")
        raw_items = raw_items[:50]

    for raw_item in raw_items:
        parsed = normalize_screening_ticker(raw_item, market)
        dedupe_key = parsed["展示代码"] or parsed["原始输入"].upper()
        if not dedupe_key or dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        parsed_items.append(parsed)

    if not parsed_items:
        warnings.append("未解析到有效股票代码。")

    if any(item["备注"] == "格式需进一步确认" for item in parsed_items):
        warnings.append("部分代码格式需进一步确认，本版本仍会在解析表中展示。")

    return {
        "parsed_items": parsed_items,
        "warnings": warnings,
    }




@st.cache_data(ttl=1800, show_spinner=False)
def fetch_screening_price_data(ticker_item, market, a_share_source_mode="自动：AkShare → BaoStock → yfinance"):
    original_input = ticker_item.get("原始输入", "")
    display_ticker = ticker_item.get("展示代码", original_input)
    query_ticker = ticker_item.get("内部查询代码", display_ticker)
    stock_name = ticker_item.get("stock_name") or ticker_item.get("股票名称") or get_stock_display_name(display_ticker, market)
    base_result = {
        "success": False,
        "original_input": original_input,
        "stock_name": stock_name,
        "industry": ticker_item.get("industry", "行业暂缺"),
        "sector": ticker_item.get("sector", "板块暂缺"),
        "themes": ticker_item.get("themes", "主题暂缺"),
        "display_ticker": display_ticker,
        "query_ticker": query_ticker,
        "market": market,
        "data_source": INSUFFICIENT,
        "primary_source": get_primary_source(market),
        "fallback_source": get_screening_fallback_source(market),
        "fallback_used": False,
        "latest_trade_date": INSUFFICIENT,
        "valid_trading_days": 0,
        "data_quality": "数据不足，请谨慎使用",
        "source_note": "",
        "price_df": pd.DataFrame(),
        "error_message": "",
        "attempt_params": "",
        "attempted_sources": "",
        "failure_stage": "",
        "network_diagnostic": "",
        "akshare_error_summary": "",
        "baostock_error_summary": "",
        "yfinance_error_summary": "",
        "source_mode": a_share_source_mode if market == "A股" else "默认",
        "a_share_yfinance_ticker": "",
    }

    if not ticker_item.get("is_valid", False):
        base_result["error_message"] = ticker_item.get("备注") or "代码格式需进一步确认"
        base_result["failure_stage"] = "代码标准化失败"
        return base_result

    try:
        if market == "A股":
            query_ticker = normalize_a_share_symbol_for_akshare(query_ticker)
            base_result["query_ticker"] = query_ticker
            yf_symbol, yf_code_error = convert_a_share_to_yfinance_ticker(query_ticker)
            base_result["a_share_yfinance_ticker"] = yf_symbol or ""
            end_date = date.today()
            start_date = end_date - pd.DateOffset(days=240)
            attempts = []
            errors = []
            source_errors = {"AkShare": "", "BaoStock": "", "yfinance": ""}

            def record_failed_attempt(source_name, data_frame):
                attempt = data_frame.attrs.get("attempt_params", source_name)
                stage = data_frame.attrs.get("failure_stage", f"{source_name} 获取失败")
                error = data_frame.attrs.get("error_message", f"{source_name} 未返回可用数据")
                summary = f"{stage}：{error}"
                attempts.append(attempt)
                errors.append(f"{source_name}: {summary}")
                source_errors[source_name] = summary

            def try_akshare():
                data_frame = fetch_a_share_history(query_ticker, "6个月", lookback_days=240, limit_rows=120)
                if data_frame is not None and not data_frame.empty:
                    data_frame.attrs["data_source_meta"] = build_data_source_meta(
                        data_frame,
                        market,
                        "AkShare",
                        "BaoStock / yfinance" if a_share_source_mode.startswith("自动") else "无",
                        "AkShare",
                        fallback_used=False,
                        adjustment=data_frame.attrs.get("successful_adjust", "AkShare 参数自动尝试"),
                        source_warning="A股为本项目重点研究市场。免费数据源可能存在延迟、字段差异、复权口径差异和接口不稳定，本结果仅用于研究准备，不构成投资建议。",
                    )
                    data_frame.attrs["source_note"] = "AkShare 获取成功"
                    return data_frame
                record_failed_attempt("AkShare", data_frame if data_frame is not None else pd.DataFrame())
                return pd.DataFrame()

            def try_baostock():
                data_frame = fetch_a_share_baostock_data(query_ticker, start_date, end_date)
                if data_frame is not None and not data_frame.empty:
                    data_frame.attrs["data_source_meta"] = build_data_source_meta(
                        data_frame,
                        market,
                        "AkShare" if a_share_source_mode.startswith("自动") else "BaoStock",
                        "BaoStock" if a_share_source_mode.startswith("自动") else "无",
                        "BaoStock",
                        fallback_used=a_share_source_mode.startswith("自动"),
                        adjustment=data_frame.attrs.get("successful_adjust", "BaoStock 默认口径"),
                        source_warning="AkShare 失败后使用 BaoStock 备用数据源。A股免费数据源可能存在延迟、字段差异、复权口径差异和接口不稳定，本结果仅用于研究准备，不构成投资建议。",
                    )
                    data_frame.attrs["source_note"] = (
                        "AkShare 失败后使用 BaoStock 备用数据源"
                        if a_share_source_mode.startswith("自动")
                        else "BaoStock 获取成功"
                    )
                    return data_frame
                record_failed_attempt("BaoStock", data_frame if data_frame is not None else pd.DataFrame())
                return pd.DataFrame()

            def try_yfinance():
                if not yf_symbol:
                    empty_frame = pd.DataFrame()
                    empty_frame.attrs.update(
                        {
                            "attempt_params": "yfinance 未请求",
                            "failure_stage": "yfinance 代码转换失败",
                            "error_message": yf_code_error or "无法生成 yfinance A股代码。",
                        }
                    )
                    record_failed_attempt("yfinance", empty_frame)
                    return pd.DataFrame()
                try:
                    data_frame = keep_recent_rows(fetch_yfinance_history(yf_symbol, "1y"), 120)
                    data_frame.attrs["attempt_params"] = f"yfinance({yf_symbol})"
                    if data_frame is not None and not data_frame.empty:
                        data_frame.attrs["actual_query_symbol"] = yf_symbol
                        data_frame.attrs["data_source_meta"] = build_data_source_meta(
                            data_frame,
                            market,
                            "AkShare" if a_share_source_mode.startswith("自动") else "yfinance",
                            "BaoStock / yfinance" if a_share_source_mode.startswith("自动") else "无",
                            "yfinance",
                            fallback_used=a_share_source_mode.startswith("自动"),
                            adjustment="yfinance 默认口径",
                            source_warning="AkShare 和 BaoStock 失败后使用 yfinance 兜底。A股免费数据源可能存在延迟、字段差异、复权口径差异和接口不稳定，本结果仅用于研究准备，不构成投资建议。",
                        )
                        data_frame.attrs["source_note"] = (
                            "AkShare 和 BaoStock 失败后使用 yfinance 兜底"
                            if a_share_source_mode.startswith("自动")
                            else "yfinance 获取成功"
                        )
                        return data_frame
                    data_frame = data_frame if data_frame is not None else pd.DataFrame()
                    data_frame.attrs["attempt_params"] = f"yfinance({yf_symbol})"
                    data_frame.attrs["failure_stage"] = "yfinance 返回空数据"
                    data_frame.attrs["error_message"] = "yfinance 未返回可用 A股行情。"
                    record_failed_attempt("yfinance", data_frame)
                    return pd.DataFrame()
                except Exception as exc:
                    empty_frame = pd.DataFrame()
                    empty_frame.attrs.update(
                        {
                            "attempt_params": f"yfinance({yf_symbol})",
                            "failure_stage": "yfinance 请求失败",
                            "error_message": str(exc),
                        }
                    )
                    record_failed_attempt("yfinance", empty_frame)
                    return pd.DataFrame()

            price_df = pd.DataFrame()
            if a_share_source_mode == "仅 AkShare":
                price_df = try_akshare()
            elif a_share_source_mode == "仅 BaoStock":
                price_df = try_baostock()
            elif a_share_source_mode == "仅 yfinance":
                price_df = try_yfinance()
            else:
                for fetcher in [try_akshare, try_baostock, try_yfinance]:
                    price_df = fetcher()
                    if price_df is not None and not price_df.empty:
                        break

            if price_df is None or price_df.empty:
                price_df = pd.DataFrame()
                price_df.attrs.update(
                    {
                        "attempt_params": "; ".join(attempts),
                        "failure_stage": "A股可用数据源均失败",
                        "error_message": "；".join(errors) or "A股数据源均未返回可用行情。",
                        "attempted_sources": "AkShare → BaoStock → yfinance",
                        "akshare_error_summary": source_errors["AkShare"],
                        "baostock_error_summary": source_errors["BaoStock"],
                        "yfinance_error_summary": source_errors["yfinance"],
                    }
                )
        else:
            price_df = fetch_market_data(query_ticker, market, "6个月")
            price_df = keep_recent_rows(price_df, 120)

        base_result["attempt_params"] = price_df.attrs.get("attempt_params", "")
        base_result["attempted_sources"] = price_df.attrs.get("attempted_sources", "")
        base_result["failure_stage"] = price_df.attrs.get("failure_stage", "")

        if price_df is None or price_df.empty:
            base_result["data_source"] = price_df.attrs.get("data_source_meta", {}).get("actual_source", get_primary_source(market)) if price_df is not None else get_primary_source(market)
            base_result["error_message"] = price_df.attrs.get("error_message", "数据源返回空数据") if price_df is not None else "数据源返回空数据"
            base_result["failure_stage"] = price_df.attrs.get("failure_stage", "AkShare 返回空数据" if market == "A股" else "数据源返回空数据") if price_df is not None else "数据源返回空数据"
            base_result["attempted_sources"] = price_df.attrs.get("attempted_sources", base_result["attempt_params"]) if price_df is not None else ""
            base_result["akshare_error_summary"] = price_df.attrs.get("akshare_error_summary", "") if price_df is not None else ""
            base_result["baostock_error_summary"] = price_df.attrs.get("baostock_error_summary", "") if price_df is not None else ""
            base_result["yfinance_error_summary"] = price_df.attrs.get("yfinance_error_summary", "") if price_df is not None else ""
            if is_network_error_message(base_result["error_message"]):
                base_result["network_diagnostic"] = "检测到网络连接异常，可能与 AkShare 接口、代理/VPN、网络环境或请求频率有关。"
            return base_result
        if "Date" not in price_df.columns:
            base_result["error_message"] = "行情数据缺少 Date 字段"
            base_result["failure_stage"] = "Date 字段缺失"
            return base_result
        if "Close" not in price_df.columns:
            base_result["error_message"] = "行情数据缺少 Close 字段"
            base_result["failure_stage"] = "Close 字段缺失"
            return base_result

        close_prices = pd.to_numeric(price_df["Close"], errors="coerce").dropna()
        if close_prices.empty:
            base_result["error_message"] = "有效收盘价为空"
            base_result["failure_stage"] = "数据清洗后为空"
            return base_result

        actual_query_ticker = price_df.attrs.get("actual_query_symbol", query_ticker)
        metadata = get_price_data_metadata(price_df, actual_query_ticker, market)
        quality_report = generate_data_quality_report(price_df)
        valid_trading_days = int(len(close_prices))
        base_result.update(
            {
                "success": True,
                "query_ticker": actual_query_ticker,
                "data_source": metadata["数据来源"],
                "primary_source": metadata["主数据源"],
                "fallback_source": metadata["备用数据源"],
                "fallback_used": metadata["是否使用备用源"] == "是",
                "latest_trade_date": metadata["最近更新时间"],
                "valid_trading_days": valid_trading_days,
                "data_quality": quality_report["数据质量结论"],
                "source_note": price_df.attrs.get("source_note", metadata["数据源风险提示"]),
                "price_df": price_df,
                "error_message": "",
                "attempt_params": price_df.attrs.get("attempt_params", ""),
                "attempted_sources": price_df.attrs.get("attempted_sources", ""),
                "failure_stage": "有效交易日不足" if valid_trading_days < 60 else "",
                "network_diagnostic": "",
                "akshare_error_summary": source_errors["AkShare"] if market == "A股" else "",
                "baostock_error_summary": source_errors["BaoStock"] if market == "A股" else "",
                "yfinance_error_summary": source_errors["yfinance"] if market == "A股" else "",
                "source_mode": a_share_source_mode if market == "A股" else "默认",
                "a_share_yfinance_ticker": yf_symbol if market == "A股" and yf_symbol else "",
            }
        )
        return base_result
    except Exception as exc:
        base_result["error_message"] = f"数据获取失败：{exc}"
        base_result["failure_stage"] = "AkShare 请求失败" if market == "A股" else "数据源请求失败"
        if is_network_error_message(str(exc)):
            base_result["network_diagnostic"] = "检测到网络连接异常，可能与 AkShare 接口、代理/VPN、网络环境或请求频率有关。"
        return base_result


def screen_universe_data_fetch(parsed_items, market, max_process_count=50, run_mode="快速模式", progress_callback=None):
    success_items = []
    failed_items = []
    insufficient_items = []

    limited_items = parsed_items[:max_process_count]
    sleep_seconds = 0.2 if run_mode == "快速模式" else 0.5
    for index, ticker_item in enumerate(limited_items):
        result = fetch_screening_price_data(ticker_item, market)
        if result["success"]:
            success_items.append(result)
            if result["valid_trading_days"] < 60:
                insufficient_items.append(result)
        else:
            failed_items.append(result)
        if progress_callback:
            progress_callback(index + 1, len(limited_items), ticker_item)
        if market == "A股" and index < len(limited_items) - 1:
            time.sleep(sleep_seconds)

    summary = {
        "股票池总数": len(limited_items),
        "成功获取数量": len(success_items),
        "失败数量": len(failed_items),
        "数据不足数量": len(insufficient_items),
    }
    return {
        "success_items": success_items,
        "failed_items": failed_items,
        "insufficient_items": insufficient_items,
        "summary": summary,
    }


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
    if price_series_map:
        all_dates = pd.Index([])
        for close_prices in price_series_map.values():
            all_dates = all_dates.append(pd.Index(close_prices.dropna().index))
        all_dates = pd.to_datetime(all_dates, errors="coerce").dropna()
        if len(all_dates):
            comparison_df.attrs["start_date"] = all_dates.min().strftime("%Y-%m-%d")
            comparison_df.attrs["end_date"] = all_dates.max().strftime("%Y-%m-%d")
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
            f"5. 后续研究观察：价格高于20日和60日均线的标的包括 {format_symbol_list(above_ma_symbols)}；更适合进入下一步研究清单的标的包括 {format_symbol_list(research_symbols)}。本摘要不输出具体操作结论或目标价，仅用于学习演示，不构成投资建议。",
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

    st.caption(
        f"数据来源：{get_data_source(market_type)} | 市场类型：{market_type} | "
        f"币种：{get_market_currency(market_type)} | 时间范围：{period_label} | "
        f"起止日期：{comparison_df.attrs.get('start_date', INSUFFICIENT)} 至 {comparison_df.attrs.get('end_date', INSUFFICIENT)}"
    )
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


def parse_screening_top_n(top_n_label):
    match = re.search(r"\d+", str(top_n_label or ""))
    return int(match.group()) if match else 10


def build_screening_priority_rows(success_items, run_mode="快速模式"):
    scored_rows = []
    unscored_rows = []
    include_fundamentals = run_mode == "完整模式"

    for item in success_items:
        try:
            metrics = calculate_screening_metrics(item.get("price_df"))
            metrics["数据质量"] = item.get("data_quality", "")
            metrics["使用备用数据源"] = bool(item.get("fallback_used", False))
            score_result = calculate_research_priority_score(metrics)
            score = score_result["研究优先级评分"]
            if include_fundamentals:
                fundamental_data = get_fundamental_data(item["display_ticker"], item["query_ticker"], item["market"])
                fundamental_score = calculate_fundamental_quality_score(fundamental_data)
            else:
                fundamental_data = build_fundamental_record((), "快速模式未获取")
                fundamental_score = "无法评分"
            composite_score = calculate_composite_research_score(score, fundamental_score)
            fundamental_summary = generate_fundamental_summary(fundamental_data) if include_fundamentals else "快速模式暂不获取基本面明细。"
            missing_fundamental_count = sum(1 for field in FUNDAMENTAL_FIELDS if is_missing(fundamental_data.get(field)))
            metrics["基本面数据源"] = fundamental_data.get("fundamental_source", "数据暂缺")
            metrics["基本面字段缺失较多"] = missing_fundamental_count > len(FUNDAMENTAL_FIELDS) / 2
            try:
                selection_reasons = generate_selection_reasons(metrics)
            except Exception:
                selection_reasons = ["入选理由生成失败，请检查指标完整性。"]
            try:
                risk_warnings = generate_screening_risk_warnings(metrics)
            except Exception:
                risk_warnings = ["风险提示生成失败，请检查指标完整性。", "当前结果只代表研究优先级，不代表具体操作建议。"]
            row = {
                "股票代码": item["display_ticker"],
                "股票名称": item.get("stock_name", "名称暂缺"),
                "行业": item.get("industry", "行业暂缺"),
                "板块": item.get("sector", "板块暂缺"),
                "主题标签": item.get("themes", "主题暂缺"),
                "市场": item["market"],
                "实际查询代码": item["query_ticker"],
                "数据源": item["data_source"],
                "最新交易日": item["latest_trade_date"],
                "最新价格": format_price(metrics["最新价格"]),
                "近 5 日涨跌幅": format_percent(metrics["近 5 日涨跌幅"]),
                "近 20 日涨跌幅": format_percent(metrics["近 20 日涨跌幅"]),
                "近 60 日涨跌幅": format_percent(metrics["近 60 日涨跌幅"]),
                "MA20": format_price(metrics["MA20"]),
                "MA60": format_price(metrics["MA60"]),
                "是否高于 MA20": format_screening_bool(metrics["当前价格是否高于 MA20"]),
                "是否高于 MA60": format_screening_bool(metrics["当前价格是否高于 MA60"]),
                "MA20 是否高于 MA60": format_screening_bool(metrics["MA20 是否高于 MA60"]),
                "成交量放大倍数": format_metric(metrics["成交量放大倍数"])
                if not pd.isna(to_number(metrics["成交量放大倍数"]))
                else INSUFFICIENT,
                "最大回撤": format_percent(metrics["最大回撤"]),
                "年化波动率": format_percent(metrics["年化波动率"]),
                "有效交易日数量": metrics["有效交易日数量"],
                "数据质量": item["data_quality"],
                "研究优先级评分": score,
                "总市值": format_large_number(to_number(fundamental_data.get("market_cap")) * 100000000) if not pd.isna(to_number(fundamental_data.get("market_cap"))) else MISSING,
                "PE_TTM": format_metric(fundamental_data.get("pe_ttm")),
                "PB": format_metric(fundamental_data.get("pb")),
                "ROE": format_percent(fundamental_data.get("roe"), MISSING),
                "营收同比增长率": format_percent(fundamental_data.get("revenue_yoy"), MISSING),
                "归母净利润同比增长率": format_percent(fundamental_data.get("net_profit_yoy"), MISSING),
                "毛利率": format_percent(fundamental_data.get("gross_margin"), MISSING),
                "净利率": format_percent(fundamental_data.get("net_margin"), MISSING),
                "资产负债率": format_percent(fundamental_data.get("debt_asset_ratio"), MISSING),
                "股息率": format_percent(fundamental_data.get("dividend_yield"), MISSING),
                "基本面数据源": fundamental_data.get("fundamental_source", "数据暂缺"),
                "基本面质量评分": fundamental_score,
                "综合研究观察评分": composite_score,
                "基本面观察摘要": fundamental_summary,
                "入选理由": join_explanation_items(selection_reasons),
                "风险提示": join_explanation_items(risk_warnings),
                "_score": score if isinstance(score, int) else math.nan,
                "_composite_score": composite_score if isinstance(composite_score, (int, float)) else math.nan,
                "_unscored_reason": score_result.get("无法评分原因", ""),
            }
            if isinstance(score, int):
                scored_rows.append(row)
            else:
                row["未纳入原因"] = score_result.get("无法评分原因", "无法评分")
                unscored_rows.append(row)
        except Exception as exc:
            unscored_rows.append(
                {
                    "股票代码": item.get("display_ticker", ""),
                    "股票名称": item.get("stock_name", "名称暂缺"),
                    "行业": item.get("industry", "行业暂缺"),
                    "板块": item.get("sector", "板块暂缺"),
                    "主题标签": item.get("themes", "主题暂缺"),
                    "市场": item.get("market", ""),
                    "实际查询代码": item.get("query_ticker", ""),
                    "数据源": item.get("data_source", ""),
                    "有效交易日数量": item.get("valid_trading_days", 0),
                    "最新交易日": item.get("latest_trade_date", INSUFFICIENT),
                    "数据质量": item.get("data_quality", INSUFFICIENT),
                    "研究优先级评分": "无法评分",
                    "未纳入原因": f"指标计算失败：{exc}",
                }
            )

    scored_rows = sorted(scored_rows, key=lambda row: (to_number(row.get("_composite_score")), to_number(row.get("_score"))), reverse=True)
    for index, row in enumerate(scored_rows, start=1):
        row["排名"] = index
    return scored_rows, unscored_rows




def render_screening_section(market, pool_source, top_n_label, input_text, pool_type=None, max_process_count=10, run_mode="快速模式"):
    screening_result_frame = pd.DataFrame()
    st.divider()
    st.header("自动研究对象筛选")
    st.write(
        "本模块用于从股票池中筛选研究优先级较高的候选对象，仅用于学习和研究，"
        "不构成投资建议，也不代表具体操作建议。"
    )
    st.caption(
        "当前 V1.1 在 V1.0 基础上新增性能优化、缓存机制、快速模式和完整模式。"
        "所有内容均由本地规则生成。"
    )
    st.info(
        "为提升运行速度，系统会缓存部分行情和基本面数据。免费数据源可能存在延迟、缺失、限流或接口不稳定。"
        "若结果异常，可清除缓存后重试。"
    )
    if market == "A股":
        st.info(
            "A股为本项目重点研究市场。当前版本使用 AkShare、BaoStock、yfinance 进行多数据源降级。"
            "免费数据源可能存在延迟、字段差异、复权口径差异和接口不稳定，本结果仅用于研究准备，不构成投资建议。"
        )
        st.info(
            "V1.0 新增基本面质量观察。当前基本面数据可能来自 AkShare 或内置示例数据。"
            "内置示例数据仅用于学习和原型演示，不代表最新真实财务数据。"
        )
    if max_process_count >= 30:
        st.warning("处理数量较大，免费数据源请求可能较慢，建议先用快速模式测试。")

    pool_info = {
        "pool_name": "自定义研究股票池",
        "pool_description": "用户输入的自定义股票池。",
        "pool_warning": "自定义股票池仅作为研究样本，不代表投资建议。",
        "tickers": [],
    }
    if pool_source == "默认示例股票池":
        pool_info = get_default_universe(market, pool_type=pool_type)
        source_text = " ".join(pool_info["tickers"])
    else:
        source_text = input_text or ""
        if not source_text.strip():
            st.warning("请选择自定义股票池时，请先输入至少一个股票代码。")
            return screening_result_frame

    result = parse_screening_universe(source_text, market)
    for warning in result["warnings"]:
        st.warning(warning)

    parsed_items = result["parsed_items"]
    if not parsed_items:
        st.warning("解析后没有可展示的候选对象。")
        return screening_result_frame
    total_pool_count = len(parsed_items)
    process_count = min(max_process_count, total_pool_count)

    st.subheader("股票池信息")
    pool_cols = st.columns(5)
    pool_cols[0].metric("股票池名称", pool_info["pool_name"])
    pool_cols[1].metric("股票池总数", total_pool_count)
    pool_cols[2].metric("本次处理数量", process_count)
    pool_cols[3].metric("最大处理数量", max_process_count)
    pool_cols[4].metric("市场类型", market)
    st.caption(f"股票池定位：{pool_info['pool_description']}")
    st.info(pool_info["pool_warning"])
    if total_pool_count > process_count:
        st.warning(
            f"当前股票池共 {total_pool_count} 只，本次处理前 {process_count} 只。"
            "可调整最大处理数量，但免费数据源批量请求可能较慢。"
        )

    st.subheader("初筛结果")
    info_cols = st.columns(4)
    info_cols[0].metric("市场类型", market)
    info_cols[1].metric("股票池来源", pool_source)
    info_cols[2].metric("计划筛选数量", top_n_label)
    info_cols[3].metric("解析后股票数量", len(parsed_items))

    display_frame = pd.DataFrame(parsed_items)
    display_columns = ["原始输入", "股票名称", "行业", "板块", "主题标签", "展示代码", "内部查询代码", "市场", "备注"]
    st.dataframe(display_frame[display_columns], hide_index=True, use_container_width=True)

    progress_bar = st.progress(0)
    progress_text = st.empty()

    def update_screening_progress(done, total, ticker_item):
        progress_bar.progress(done / total if total else 1)
        progress_text.caption(f"正在处理 {done}/{total}：{ticker_item.get('展示代码', '')} {ticker_item.get('stock_name', '')}")

    with st.spinner("正在获取股票池行情数据，请稍候..."):
        fetch_result = screen_universe_data_fetch(
            parsed_items,
            market,
            max_process_count=max_process_count,
            run_mode=run_mode,
            progress_callback=update_screening_progress,
        )
    progress_text.caption("批量处理完成。")

    summary = fetch_result["summary"]
    st.subheader("批量获取概览")
    summary_cols = st.columns(4)
    summary_cols[0].metric("股票池总数", summary["股票池总数"])
    summary_cols[1].metric("成功获取数量", summary["成功获取数量"])
    summary_cols[2].metric("失败数量", summary["失败数量"])
    summary_cols[3].metric("数据不足数量", summary["数据不足数量"])

    success_items = fetch_result["success_items"]
    failed_items = fetch_result["failed_items"]
    insufficient_items = fetch_result["insufficient_items"]

    if success_items:
        scored_rows, unscored_rows = build_screening_priority_rows(success_items, run_mode=run_mode)
        top_n = parse_screening_top_n(top_n_label)
        all_scored_frame = pd.DataFrame(scored_rows)
        all_scored_frame.attrs["total_count"] = summary["股票池总数"]
        if scored_rows:
            priority_frame = pd.DataFrame(scored_rows[:top_n])
            screening_result_frame = priority_frame.copy(deep=True)
            priority_columns = [
                "股票代码",
                "股票名称",
                "行业",
                "板块",
                "数据源",
                "最新交易日",
                "研究优先级评分",
                "基本面质量评分",
                "综合研究观察评分",
                "近 20 日涨跌幅",
                "近 60 日涨跌幅",
                "成交量放大倍数",
                "入选理由",
                "风险提示",
            ]
            st.subheader("Top N 研究候选池表格")
            st.dataframe(priority_frame[priority_columns], hide_index=True, use_container_width=True)
            with st.expander("完整指标表"):
                detail_columns = [col for col in priority_frame.columns if not col.startswith("_")]
                st.dataframe(priority_frame[detail_columns], hide_index=True, use_container_width=True)
            if run_mode == "完整模式":
                with st.expander("基本面详细字段", expanded=False):
                    fundamental_columns = [
                        "股票代码", "股票名称", "总市值", "PE_TTM", "PB", "ROE", "营收同比增长率",
                        "归母净利润同比增长率", "毛利率", "净利率", "资产负债率", "股息率",
                        "基本面数据源", "基本面质量评分", "综合研究观察评分", "基本面观察摘要",
                    ]
                    st.dataframe(priority_frame[fundamental_columns], hide_index=True, use_container_width=True)
                sector_df = generate_sector_strength_summary(priority_frame, all_scored_df=all_scored_frame)
                st.subheader("板块强度初步统计")
                if not sector_df.empty:
                    st.dataframe(sector_df, hide_index=True, use_container_width=True)
                    if (sector_df["股票数量"].apply(to_number) < 2).any():
                        st.caption("部分板块样本数量少于 2，只能作为研究观察参考。")
                    st.subheader("板块强度解释")
                    st.write(generate_sector_strength_text(sector_df))
                else:
                    st.info("当前结果暂无可用于板块强度初步统计的数据。")
            lower_priority_rows = scored_rows[top_n:]
            if lower_priority_rows:
                with st.expander("低优先级或未触发主要筛选条件的股票"):
                    lower_priority_frame = pd.DataFrame(lower_priority_rows)
                    lower_priority_columns = [
                        "排名",
                        "股票代码",
                        "股票名称",
                        "行业",
                        "板块",
                        "主题标签",
                        "市场",
                        "实际查询代码",
                        "数据源",
                        "最新交易日",
                        "有效交易日数量",
                        "数据质量",
                        "研究优先级评分",
                        "基本面质量评分",
                        "综合研究观察评分",
                        "入选理由",
                        "风险提示",
                        "基本面观察摘要",
                    ]
                    st.dataframe(lower_priority_frame[lower_priority_columns], hide_index=True, use_container_width=True)
        else:
            st.warning("本次成功获取行情的候选对象均无法评分，请查看指标不足说明。")

        if run_mode == "完整模式":
            st.subheader("筛选总结")
            st.write(generate_screening_summary(all_scored_frame, failed_items=failed_items, insufficient_items=insufficient_items))

        if unscored_rows:
            with st.expander("无法评分或未纳入候选池的股票"):
                unscored_frame = pd.DataFrame(unscored_rows)
                unscored_columns = ["股票代码", "股票名称", "行业", "板块", "主题标签", "市场", "数据源", "有效交易日数量", "数据质量", "未纳入原因"]
                display_columns = [col for col in unscored_columns if col in unscored_frame.columns]
                st.dataframe(unscored_frame[display_columns], hide_index=True, use_container_width=True)

        success_frame = pd.DataFrame(
            [
                {
                    "股票代码": item["display_ticker"],
                    "股票名称": item.get("stock_name", "名称暂缺"),
                    "行业": item.get("industry", "行业暂缺"),
                    "板块": item.get("sector", "板块暂缺"),
                    "主题标签": item.get("themes", "主题暂缺"),
                    "市场": item["market"],
                    "实际查询代码": item["query_ticker"],
                    "数据源": item["data_source"],
                    "主数据源": item["primary_source"],
                    "备用数据源": item["fallback_source"],
                    "是否使用备用数据源": "是" if item["fallback_used"] else "否",
                    "最新交易日": item["latest_trade_date"],
                    "有效交易日数量": item["valid_trading_days"],
                    "数据质量": item["data_quality"],
                    "数据源说明": item.get("source_note", ""),
                }
                for item in success_items
            ]
        )
        if run_mode == "完整模式":
            with st.expander("数据源诊断 / 成功获取明细"):
                st.dataframe(success_frame, hide_index=True, use_container_width=True)
    else:
        st.warning("本次股票池未成功获取到可用行情数据。")
        if run_mode == "完整模式":
            st.subheader("筛选总结")
            st.write(generate_screening_summary(pd.DataFrame(), failed_items=failed_items, insufficient_items=insufficient_items))

    if failed_items and run_mode == "完整模式":
        with st.expander("获取失败的股票及原因"):
            if market == "A股":
                st.info("如果大量 A股返回空数据，请先用少量代码测试 AkShare、BaoStock、yfinance 的连接状态，例如 600519、300750、000001。")
            failed_frame = pd.DataFrame(
                [
                    {
                        "股票代码": item["display_ticker"],
                        "股票名称": item.get("stock_name", "名称暂缺"),
                        "行业": item.get("industry", "行业暂缺"),
                        "板块": item.get("sector", "板块暂缺"),
                        "主题标签": item.get("themes", "主题暂缺"),
                        "实际查询代码": item["query_ticker"],
                        "市场": item["market"],
                        "尝试过的数据源": item.get("attempted_sources", item.get("attempt_params", "")),
                        "失败阶段": item.get("failure_stage", ""),
                        "失败原因摘要": item["error_message"] or "数据获取失败",
                        "AkShare 错误摘要": item.get("akshare_error_summary", ""),
                        "BaoStock 错误摘要": item.get("baostock_error_summary", ""),
                        "yfinance 错误摘要": item.get("yfinance_error_summary", ""),
                    }
                    for item in failed_items
                ]
            )
            st.dataframe(failed_frame, hide_index=True, use_container_width=True)
    elif failed_items:
        st.warning(f"本次有 {len(failed_items)} 只股票获取失败。切换到完整模式可查看详细诊断。")

    st.info(
        "当前 V1.1 在 V1.0 基础上新增性能优化、缓存机制、快速模式和完整模式。"
        "所有内容均由本地规则生成，仅用于学习和研究，不构成投资建议。"
    )
    return screening_result_frame


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
    metadata = get_price_data_metadata(backtest_price_data, actual_ticker, market_type)
    quality_report = generate_data_quality_report(backtest_price_data)

    st.subheader("回测说明")
    st.write(
        f"策略名称：{strategy_name} | 股票代码：{actual_ticker} | 市场类型：{market_type} | "
        f"回测时间范围：{period_label} | 初始资金：{initial_capital:,.0f} | 单边交易成本：{trading_cost:.4f}"
    )
    st.write(
        f"实际数据源：{metadata['数据来源']} | 主数据源：{metadata['主数据源']} | "
        f"备用数据源：{metadata['备用数据源']} | 是否使用备用源：{metadata['是否使用备用源']} | "
        f"最近交易日：{metadata['最近更新时间']} | 币种：{metadata['币种']}"
    )
    with st.expander("回测数据质量检查"):
        st.dataframe(pd.DataFrame([quality_report]), hide_index=True, use_container_width=True)
        if quality_report["数据质量结论"] != "数据较完整":
            st.warning(quality_report["数据质量结论"])
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
            "positive": "放量突破或资金流入可能强化趋势关注线索，提高短期关注度。",
            "negative": "跌破关键位置、放量下跌或高换手回落可能意味着情绪退潮和回撤风险。",
            "verify": "需要验证成交量、换手率、关键均线、支撑压力位和后续价格确认。",
            "short": "短期影响主要体现在交易情绪、趋势延续和波动率变化。",
            "long": "中长期基本面影响有限，除非价格和成交量线索背后有基本面或事件催化支撑。",
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


def render_legacy_app():

        if "watchlist" not in st.session_state:
            st.session_state.watchlist = []

        st.title("FinScientist")
        st.subheader("AI-assisted financial research workspace")
        st.caption("V1.1 增强性能优化与缓存机制；仍为本地规则化研究原型，不调用 AI API。")

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

            st.divider()
            st.info(
                "该筛选区域是旧版兼容入口，建议使用页面导航中的"
                "“自动研究对象筛选”模块。"
            )
            st.header("自动研究对象筛选")
            screening_market = st.selectbox("筛选市场", options=SCREENING_MARKET_OPTIONS, index=0)
            screening_run_mode = st.selectbox("运行模式", options=SCREENING_RUN_MODE_OPTIONS, index=0)
            screening_pool_source = st.selectbox("股票池选择", options=SCREENING_POOL_OPTIONS, index=0)
            screening_a_share_pool_type = DEFAULT_A_SHARE_POOL_TYPE
            if screening_market == "A股" and screening_pool_source == "默认示例股票池":
                screening_a_share_pool_type = st.selectbox(
                    "股票池类型",
                    options=list(A_SHARE_SCREENING_POOLS.keys()),
                    index=0,
                )
            screening_custom_input = st.text_area(
                "自定义股票池",
                value="",
                placeholder="例如：NVDA, AAPL, MSFT\n例如：600519.SH, 300750.SZ\n例如：0700.HK, 9988.HK",
                height=90,
                disabled=screening_pool_source == "默认示例股票池",
            )
            screening_top_n = st.selectbox("筛选数量", options=SCREENING_TOP_OPTIONS, index=0)
            screening_max_process_count = st.selectbox("最大处理数量", options=SCREENING_MAX_PROCESS_OPTIONS, index=0)
            clear_screening_cache_button = st.button("清除缓存并重新获取数据")
            run_screening_button = st.button("生成研究候选池")

        if clear_watchlist_button:
            clear_watchlist()
            st.success("已清空自选股列表。")
        if clear_screening_cache_button:
            try:
                st.cache_data.clear()
                st.success("缓存已清除，请重新运行筛选。")
            except Exception as exc:
                st.warning(f"缓存清除失败，请稍后重试：{exc}")

        selected_market = market
        raw_symbol = ""
        symbol = ""
        input_error = ""
        if not user_input.strip():
            input_error = "请输入股票代码或股票名称。"
        elif input_mode == "股票名称":
            is_valid_name, name_error = validate_name_input(user_input)
            if not is_valid_name:
                input_error = name_error
            else:
                resolved = resolve_name_to_ticker(user_input)
                if not resolved:
                    input_error = "当前版本暂不支持该名称搜索，请改用股票代码输入。"
                else:
                    selected_market, raw_symbol = resolved
        else:
            is_valid_ticker, ticker_error = validate_ticker_input(user_input, selected_market)
            if not is_valid_ticker:
                input_error = ticker_error
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
            if run_screening_button:
                render_watchlist_panel()
                render_screening_section(
                    screening_market,
                    screening_pool_source,
                    screening_top_n,
                    screening_custom_input,
                    screening_a_share_pool_type,
                    screening_max_process_count,
                    screening_run_mode,
                )
            elif comparison_tickers:
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

        metadata = get_price_data_metadata(price_data, symbol, selected_market)
        quality_report = generate_data_quality_report(price_data)
        st.subheader("数据源与可靠性")
        meta_cols = st.columns(5)
        meta_cols[0].metric("实际使用的数据源", metadata["数据来源"])
        meta_cols[1].metric("主数据源", metadata["主数据源"])
        meta_cols[2].metric("备用数据源", metadata["备用数据源"])
        meta_cols[3].metric("是否使用备用源", metadata["是否使用备用源"])
        meta_cols[4].metric("最近交易日", metadata["最近更新时间"])

        meta_cols_2 = st.columns(5)
        meta_cols_2[0].metric("数据频率", metadata["数据频率"])
        meta_cols_2[1].metric("币种", metadata["币种"])
        meta_cols_2[2].metric("复权口径", metadata["复权口径"])
        meta_cols_2[3].metric("起始日期", metadata["起始日期"])
        meta_cols_2[4].metric("结束日期", metadata["结束日期"])
        st.info(metadata["时效性说明"])
        st.warning(metadata["数据源风险提示"])

        with st.expander("数据质量报告 Data Quality Report"):
            st.dataframe(pd.DataFrame([quality_report]), hide_index=True, use_container_width=True)
            st.write(f"数据质量结论：**{quality_report['数据质量结论']}**")
            if quality_report["数据质量结论"] != "数据较完整":
                st.warning(quality_report["数据质量结论"])

        if selected_market == "港股":
            with st.expander("港股主备数据源校验"):
                hk_compare = compare_hk_sources_if_available(symbol)
                if hk_compare["status"] == "warning":
                    st.warning(hk_compare["message"])
                else:
                    st.info(hk_compare["message"])
                if hk_compare.get("compare_date"):
                    st.write(
                        f"可比日期：{hk_compare['compare_date']} | AkShare 收盘价：{format_price(hk_compare['akshare_close'])} | "
                        f"yfinance 收盘价：{format_price(hk_compare['yfinance_close'])} | 差异：{format_percent(hk_compare['diff_pct'])}"
                    )

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
        if run_screening_button:
                render_screening_section(
                    screening_market,
                    screening_pool_source,
                    screening_top_n,
                    screening_custom_input,
                    screening_a_share_pool_type,
                    screening_max_process_count,
                    screening_run_mode,
                )

        st.divider()
        st.header("风险提示")
        st.write("- yfinance / akshare / baostock 数据可能延迟、缺失或口径不一致。")
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


def render_legacy_workbench():
    """Render the old research workbench through an explicit compatibility API."""
    render_legacy_app()
