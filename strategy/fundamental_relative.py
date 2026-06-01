"""Read-only industry-relative fundamental comparison helpers."""

import copy
import math

import pandas as pd

from strategy.fundamental import detect_fundamental_fields, normalize_fundamental_value


RELATIVE_FUNDAMENTAL_FIELDS = [
    "relative_profitability_label",
    "relative_growth_label",
    "relative_valuation_label",
    "relative_financial_risk_label",
    "industry_relative_quality_label",
    "industry_relative_summary",
]

INDUSTRY_ALIASES = (
    "industry",
    "industry_name",
    "sector",
    "板块",
    "行业",
    "琛屼笟",
    "鏉垮潡",
)

_DEFAULT_PROFILE = {
    "relative_profitability_label": "insufficient_data",
    "relative_growth_label": "insufficient_data",
    "relative_valuation_label": "insufficient_data",
    "relative_financial_risk_label": "insufficient_data",
    "industry_relative_quality_label": "insufficient_industry_data",
    "industry_relative_summary": "行业字段或同行样本不足，暂不能形成行业相对基本面观察。",
}


def _source_to_frame(source):
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    if isinstance(source, pd.Series):
        return pd.DataFrame([copy.deepcopy(source.to_dict())])
    if isinstance(source, dict):
        return pd.DataFrame([copy.deepcopy(source)])
    if isinstance(source, list):
        return pd.DataFrame(copy.deepcopy(source))
    return pd.DataFrame()


def _find_column(columns, aliases):
    lowered = {str(column).lower(): column for column in columns}
    for alias in aliases:
        if alias in columns:
            return alias
        matched = lowered.get(str(alias).lower())
        if matched is not None:
            return matched
    return None


def _safe_text(value):
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "none", "null", "n/a", "na", "-", "--"}:
        return ""
    return text


def _finite_number(value):
    number = normalize_fundamental_value(value)
    if number is None:
        return None
    try:
        number = float(number)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _average(values):
    clean = [value for value in values if isinstance(value, (int, float)) and math.isfinite(value)]
    if not clean:
        return None
    return sum(clean) / len(clean)


def _metric(row, fields):
    data = detect_fundamental_fields(row)
    return _average(data.get(field) for field in fields)


def _valuation_metric(row):
    data = detect_fundamental_fields(row)
    pe = data.get("pe")
    pb = data.get("pb")
    ps = data.get("ps")
    values = []
    for value in (pe, pb, ps):
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            continue
        values.append(value)
    if not values:
        return None
    return _average(values)


def _risk_metric(row):
    data = detect_fundamental_fields(row)
    parts = []
    debt = data.get("debt_ratio")
    cashflow = data.get("operating_cashflow")
    profit = data.get("net_profit")
    if isinstance(debt, (int, float)) and math.isfinite(debt):
        parts.append(debt)
    if isinstance(cashflow, (int, float)) and math.isfinite(cashflow):
        parts.append(-0.2 if cashflow > 0 else 0.8)
    if isinstance(profit, (int, float)) and math.isfinite(profit):
        parts.append(-0.1 if profit > 0 else 0.8)
    return _average(parts)


def _rank_position(value, peers, higher_is_better=True):
    clean = [item for item in peers if isinstance(item, (int, float)) and math.isfinite(item)]
    if value is None or not clean or len(clean) < 2:
        return None
    if max(clean) == min(clean):
        return 0.5
    below_or_equal = sum(item <= value for item in clean)
    percentile = (below_or_equal - 1) / (len(clean) - 1)
    return percentile if higher_is_better else 1 - percentile


def _profitability_label(position):
    if position is None:
        return "insufficient_data"
    if position >= 0.80:
        return "industry_leading"
    if position >= 0.60:
        return "above_industry_average"
    if position >= 0.35:
        return "around_industry_average"
    return "below_industry_average"


def _growth_label(position, value):
    if position is None or value is None:
        return "insufficient_data"
    if value < 0:
        return "negative_relative_growth"
    if position >= 0.70:
        return "high_relative_growth"
    if position >= 0.40:
        return "moderate_relative_growth"
    return "weak_relative_growth"


def _valuation_label(position, value, profitability_position, growth_position):
    if value is None:
        return "insufficient_data"
    if value <= 0 or value > 120:
        return "abnormal_valuation_data"
    if position is None:
        return "insufficient_data"
    if position <= 0.30:
        if (profitability_position is not None and profitability_position < 0.35) or (
            growth_position is not None and growth_position < 0.35
        ):
            return "relatively_cheap_but_needs_check"
        return "relatively_reasonable"
    if position >= 0.75:
        return "relatively_expensive"
    return "relatively_reasonable"


def _risk_label(position):
    if position is None:
        return "insufficient_data"
    if position >= 0.70:
        return "higher_than_industry_risk"
    if position <= 0.30:
        return "lower_than_industry_risk"
    return "normal_industry_risk"


def _quality_label(profile):
    labels = [
        profile["relative_profitability_label"],
        profile["relative_growth_label"],
        profile["relative_valuation_label"],
        profile["relative_financial_risk_label"],
    ]
    if sum(label == "insufficient_data" for label in labels) >= 3:
        return "insufficient_industry_data"
    strong = profile["relative_profitability_label"] in {"industry_leading", "above_industry_average"} and profile[
        "relative_growth_label"
    ] in {"high_relative_growth", "moderate_relative_growth"}
    weak = (
        profile["relative_profitability_label"] == "below_industry_average"
        or profile["relative_growth_label"] in {"weak_relative_growth", "negative_relative_growth"}
        or profile["relative_financial_risk_label"] == "higher_than_industry_risk"
    )
    if strong and profile["relative_financial_risk_label"] != "higher_than_industry_risk":
        return "industry_relative_strong"
    if weak:
        return "industry_relative_weak"
    return "industry_relative_neutral"


def _summary(profile):
    if profile["industry_relative_quality_label"] == "insufficient_industry_data":
        return "行业字段或同行样本不足，暂不能形成行业相对基本面观察。"
    if profile["relative_valuation_label"] == "relatively_expensive":
        return "该标的盈利或成长字段具备一定相对支撑，但估值水平在同行中偏高，适合继续观察成长兑现情况。"
    if profile["relative_financial_risk_label"] == "higher_than_industry_risk":
        return "该标的财务风险字段在同行中偏高，需要结合负债、现金流和利润字段继续核查。"
    if profile["industry_relative_quality_label"] == "industry_relative_strong":
        return "该标的盈利能力或成长性在同行中相对靠前，可作为基本面相对优势观察对象。"
    if profile["industry_relative_quality_label"] == "industry_relative_weak":
        return "该标的部分基本面字段在同行中相对偏弱，当前更适合做质量和风险复核。"
    return "该标的基本面相对位置接近同行中枢，需结合盈利、成长、估值和风险字段综合观察。"


def build_fundamental_relative_profile(source):
    frame = _source_to_frame(source)
    if frame.empty:
        return pd.DataFrame(columns=RELATIVE_FUNDAMENTAL_FIELDS)

    industry_column = _find_column(list(frame.columns), INDUSTRY_ALIASES)
    if industry_column is None:
        return pd.DataFrame([copy.deepcopy(_DEFAULT_PROFILE) for _ in range(len(frame))], columns=RELATIVE_FUNDAMENTAL_FIELDS)

    rows = [copy.deepcopy(row.to_dict()) for _, row in frame.iterrows()]
    industries = [_safe_text(row.get(industry_column)) for row in rows]
    profiles = []

    metrics = []
    for row in rows:
        metrics.append(
            {
                "profitability": _metric(row, ("roe", "gross_margin", "net_profit", "operating_cashflow")),
                "growth": _metric(row, ("revenue_growth", "profit_growth")),
                "valuation": _valuation_metric(row),
                "risk": _risk_metric(row),
            }
        )

    for index, row in enumerate(rows):
        industry = industries[index]
        peer_indices = [peer_index for peer_index, peer_industry in enumerate(industries) if peer_industry and peer_industry == industry]
        if not industry or len(peer_indices) < 2:
            profiles.append(copy.deepcopy(_DEFAULT_PROFILE))
            continue

        peer_metrics = [metrics[peer_index] for peer_index in peer_indices]
        profitability_position = _rank_position(
            metrics[index]["profitability"], [item["profitability"] for item in peer_metrics], higher_is_better=True
        )
        growth_position = _rank_position(metrics[index]["growth"], [item["growth"] for item in peer_metrics], higher_is_better=True)
        valuation_position = _rank_position(
            metrics[index]["valuation"], [item["valuation"] for item in peer_metrics], higher_is_better=True
        )
        risk_position = _rank_position(metrics[index]["risk"], [item["risk"] for item in peer_metrics], higher_is_better=True)

        profile = {
            "relative_profitability_label": _profitability_label(profitability_position),
            "relative_growth_label": _growth_label(growth_position, metrics[index]["growth"]),
            "relative_valuation_label": _valuation_label(
                valuation_position,
                metrics[index]["valuation"],
                profitability_position,
                growth_position,
            ),
            "relative_financial_risk_label": _risk_label(risk_position),
        }
        profile["industry_relative_quality_label"] = _quality_label(profile)
        profile["industry_relative_summary"] = _summary(profile)
        profiles.append(profile)

    return pd.DataFrame(profiles, columns=RELATIVE_FUNDAMENTAL_FIELDS)


__all__ = ["RELATIVE_FUNDAMENTAL_FIELDS", "build_fundamental_relative_profile"]
