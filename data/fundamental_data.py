"""Fundamental data helpers used by the screening workflow.

This module owns low-risk fundamental-data formatting and sample handling
helpers. Network data fetch functions are still implemented in ``legacy_app.py``
during the V1.2.x transition and are exposed here through lazy compatibility
wrappers.
"""

import math
import re

import pandas as pd

from config.fundamental_samples import FUNDAMENTAL_SAMPLE_DATA
from core.scoring import FUNDAMENTAL_FIELDS

MISSING = "\u6570\u636e\u6682\u7f3a"


def _is_missing(value):
    if value in (None, "", MISSING):
        return True
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False


def _to_number(value):
    if _is_missing(value):
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def clean_metric_value(value):
    number = _to_number(value)
    return number if not pd.isna(number) and math.isfinite(number) else math.nan


def _infer_a_share_sample_suffix(ticker_digits):
    if ticker_digits.startswith("6"):
        return ".SH"
    if ticker_digits.startswith(("0", "2", "3")):
        return ".SZ"
    return ""


def build_fundamental_record(values, source, error_message=""):
    data = dict(zip(FUNDAMENTAL_FIELDS, values)) if isinstance(values, tuple) else {}
    for field in FUNDAMENTAL_FIELDS:
        data.setdefault(field, MISSING)
    data["fundamental_source"] = source
    data["fundamental_error"] = error_message
    return data


def get_fundamental_sample_data(display_ticker):
    normalized = str(display_ticker or "").strip().upper()
    sample = FUNDAMENTAL_SAMPLE_DATA.get(normalized)
    if sample is None and re.fullmatch(r"\d{6}", normalized):
        suffix = _infer_a_share_sample_suffix(normalized)
        sample = FUNDAMENTAL_SAMPLE_DATA.get(f"{normalized}{suffix}")
    if sample is None:
        return None
    return build_fundamental_record(sample, "内置示例数据")


def fetch_a_share_fundamental_data(*args, **kwargs):
    from legacy_app import fetch_a_share_fundamental_data as _impl

    return _impl(*args, **kwargs)


def get_fundamental_data(*args, **kwargs):
    from legacy_app import get_fundamental_data as _impl

    return _impl(*args, **kwargs)


__all__ = [
    "FUNDAMENTAL_FIELDS",
    "build_fundamental_record",
    "clean_metric_value",
    "fetch_a_share_fundamental_data",
    "get_fundamental_data",
    "get_fundamental_sample_data",
]
