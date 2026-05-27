"""Stock pool configuration for FinScientist screening."""

DEFAULT_A_SHARE_POOL_TYPE = "A股核心资产观察池"
A_SHARE_SCREENING_POOLS = {
    "A股核心资产观察池": {
        "pool_name": "A股核心资产观察池",
        "pool_description": "大盘蓝筹、行业龙头、长期观察。",
        "pool_warning": "该股票池仅作为研究样本，不代表投资建议。",
        "tickers": ["600519.SH", "300750.SZ", "601318.SH", "600036.SH", "000858.SZ", "002594.SZ", "688981.SH", "300760.SZ", "600276.SH", "000333.SZ", "601899.SH", "601088.SH", "600900.SH", "601012.SH", "600887.SH", "600309.SH", "000651.SZ", "000001.SZ", "601166.SH", "600031.SH"],
    },
    "A股科技成长观察池": {
        "pool_name": "A股科技成长观察池",
        "pool_description": "半导体、AI、电子、计算机、新能源、高端制造等成长方向。",
        "pool_warning": "成长方向标的波动可能较高，仅用于研究观察，不代表投资建议。",
        "tickers": ["688981.SH", "300750.SZ", "002594.SZ", "002415.SZ", "000938.SZ", "002230.SZ", "300308.SZ", "300033.SZ", "688111.SH", "688012.SH", "688041.SH", "603501.SH", "002371.SZ", "300124.SZ", "002049.SZ", "002050.SZ", "300274.SZ", "300502.SZ", "688008.SH", "688256.SH"],
    },
    "A股消费医药观察池": {
        "pool_name": "A股消费医药观察池",
        "pool_description": "消费、白酒、医药、医疗器械、CXO、中药等方向。",
        "pool_warning": "消费与医药标的仍需结合估值、政策、业绩和行业景气继续验证。",
        "tickers": ["600519.SH", "000858.SZ", "600809.SH", "000568.SZ", "600887.SH", "603288.SH", "000333.SZ", "000651.SZ", "600276.SH", "300760.SZ", "603259.SH", "300015.SZ", "000538.SZ", "600436.SH", "000661.SZ", "002821.SZ", "688271.SH", "300122.SZ", "600763.SH", "002422.SZ"],
    },
    "A股金融地产周期观察池": {
        "pool_name": "A股金融地产周期观察池",
        "pool_description": "银行、保险、券商、地产链、资源周期、基建等方向。",
        "pool_warning": "金融、地产链和周期方向受宏观、信用、政策和商品价格影响较大，仅用于研究观察。",
        "tickers": ["601318.SH", "600036.SH", "000001.SZ", "601166.SH", "601398.SH", "601939.SH", "600030.SH", "601688.SH", "600999.SH", "601601.SH", "601899.SH", "601088.SH", "600028.SH", "601857.SH", "600019.SH", "600585.SH", "600309.SH", "601390.SH", "601668.SH", "000002.SZ"],
    },
    "A股高弹性主题观察池": {
        "pool_name": "A股高弹性主题观察池",
        "pool_description": "短期主题、成长弹性和波动较高标的，仅用于研究观察。",
        "pool_warning": "A股高弹性主题观察池中的标的波动可能较高，仅用于研究观察，不代表投资建议。",
        "tickers": ["300308.SZ", "300033.SZ", "300274.SZ", "300502.SZ", "688256.SH", "688041.SH", "688012.SH", "688111.SH", "002230.SZ", "002415.SZ", "002371.SZ", "300124.SZ", "300418.SZ", "300454.SZ", "300496.SZ", "688008.SH", "688981.SH", "688525.SH", "688327.SH", "688318.SH"],
    },
}
DEFAULT_SCREENING_UNIVERSES = {
    "A股": A_SHARE_SCREENING_POOLS[DEFAULT_A_SHARE_POOL_TYPE]["tickers"],
    "港股": [
        "0700.HK",
        "9988.HK",
        "3690.HK",
        "1810.HK",
        "0981.HK",
        "1211.HK",
        "2269.HK",
        "9999.HK",
        "9618.HK",
        "1024.HK",
    ],
    "美股": [
        "AAPL",
        "MSFT",
        "NVDA",
        "GOOGL",
        "AMZN",
        "META",
        "TSLA",
        "AMD",
        "AVGO",
        "NFLX",
    ],
}
def get_default_universe(market, pool_type=None):
    if market == "A股":
        selected_pool_type = pool_type if pool_type in A_SHARE_SCREENING_POOLS else DEFAULT_A_SHARE_POOL_TYPE
        pool = A_SHARE_SCREENING_POOLS[selected_pool_type]
        return {
            "tickers": pool["tickers"].copy(),
            "pool_name": pool["pool_name"],
            "pool_description": pool["pool_description"],
            "pool_warning": pool["pool_warning"],
        }
    tickers = DEFAULT_SCREENING_UNIVERSES.get(market, []).copy()
    return {
        "tickers": tickers,
        "pool_name": f"{market}默认示例股票池",
        "pool_description": "默认示例股票池，保留当前简化配置。",
        "pool_warning": "该股票池仅作为研究样本，不代表投资建议。",
    }



__all__ = [
    "A_SHARE_SCREENING_POOLS",
    "DEFAULT_A_SHARE_POOL_TYPE",
    "DEFAULT_SCREENING_UNIVERSES",
    "get_default_universe",
]
