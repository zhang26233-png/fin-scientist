"""Stock display-name mappings for FinScientist screening."""

import re

A_SHARE_STOCK_NAME_MAP = {
    "600519.SH": "贵州茅台", "300750.SZ": "宁德时代", "601318.SH": "中国平安", "600036.SH": "招商银行",
    "000858.SZ": "五粮液", "002594.SZ": "比亚迪", "688981.SH": "中芯国际", "300760.SZ": "迈瑞医疗",
    "600276.SH": "恒瑞医药", "000333.SZ": "美的集团", "601899.SH": "紫金矿业", "601088.SH": "中国神华",
    "600900.SH": "长江电力", "601012.SH": "隆基绿能", "600887.SH": "伊利股份", "600309.SH": "万华化学",
    "000651.SZ": "格力电器", "000001.SZ": "平安银行", "601166.SH": "兴业银行", "600031.SH": "三一重工",
    "002415.SZ": "海康威视", "000938.SZ": "紫光股份", "002230.SZ": "科大讯飞", "300308.SZ": "中际旭创",
    "300033.SZ": "同花顺", "688111.SH": "金山办公", "688012.SH": "中微公司", "688041.SH": "海光信息",
    "603501.SH": "韦尔股份", "002371.SZ": "北方华创", "300124.SZ": "汇川技术", "002049.SZ": "紫光国微",
    "002050.SZ": "三花智控", "300274.SZ": "阳光电源", "300502.SZ": "新易盛", "688008.SH": "澜起科技",
    "688256.SH": "寒武纪", "600809.SH": "山西汾酒", "000568.SZ": "泸州老窖", "603288.SH": "海天味业",
    "603259.SH": "药明康德", "300015.SZ": "爱尔眼科", "000538.SZ": "云南白药", "600436.SH": "片仔癀",
    "000661.SZ": "长春高新", "002821.SZ": "凯莱英", "688271.SH": "联影医疗", "300122.SZ": "智飞生物",
    "600763.SH": "通策医疗", "002422.SZ": "科伦药业", "601398.SH": "工商银行", "601939.SH": "建设银行",
    "600030.SH": "中信证券", "601688.SH": "华泰证券", "600999.SH": "招商证券", "601601.SH": "中国太保",
    "600028.SH": "中国石化", "601857.SH": "中国石油", "600019.SH": "宝钢股份", "600585.SH": "海螺水泥",
    "601390.SH": "中国中铁", "601668.SH": "中国建筑", "000002.SZ": "万科A", "300418.SZ": "昆仑万维",
    "300454.SZ": "深信服", "300496.SZ": "中科创达", "688525.SH": "佰维存储", "688327.SH": "云从科技",
    "688318.SH": "财富趋势",
}


def _infer_a_share_suffix(ticker_digits):
    if ticker_digits.startswith("6"):
        return ".SH"
    if ticker_digits.startswith(("0", "3")):
        return ".SZ"
    return ""

def get_stock_display_name(ticker, market):
    if market == "A股":
        normalized = str(ticker or "").strip().upper()
        clean_code = normalized.replace(".SH", "").replace(".SZ", "")
        if not re.fullmatch(r"\d{6}", clean_code):
            return "名称暂缺"
        suffix = ".SH" if normalized.endswith(".SH") else ".SZ" if normalized.endswith(".SZ") else _infer_a_share_suffix(clean_code)
        display_code = f"{clean_code}{suffix}" if suffix else clean_code
        return A_SHARE_STOCK_NAME_MAP.get(display_code, "名称暂缺")
    return "名称暂缺"



__all__ = ["A_SHARE_STOCK_NAME_MAP", "get_stock_display_name"]
