import importlib

import pandas as pd

import capital_flow.capital_engine as capital_engine
from capital_flow.capital_engine import CAPITAL_ENGINE_FIELDS, build_capital_scores


def test_capital_engine_importable():
    assert importlib.import_module("capital_flow.capital_engine")


def test_capital_engine_empty_data_does_not_crash():
    result = build_capital_scores(pd.DataFrame())

    assert isinstance(result, pd.DataFrame)
    for field in CAPITAL_ENGINE_FIELDS:
        assert field in result.columns


def test_capital_engine_builds_scores_and_strength():
    source = pd.DataFrame(
        [
            {
                "ticker": "600000",
                "name": "Sample",
                "turnover": 900_000_000,
                "turnover_rate": 8.0,
                "volume_ratio": 2.5,
                "main_net_inflow_ratio": 8.0,
                "northbound_change": 100_000_000,
                "capital_activity_score": 88,
            }
        ]
    )

    result = build_capital_scores(source)

    assert result.loc[0, "turnover_rate_score"] > 60
    assert result.loc[0, "volume_ratio_score"] > 70
    assert result.loc[0, "main_inflow_score"] > 70
    assert result.loc[0, "northbound_score"] > 50
    assert result.loc[0, "capital_flow_score"] > 70
    assert result.loc[0, "capital_flow_strength"] in {"Strong", "Strong Buy Research"}
    assert "主力净流入较强" in result.loc[0, "capital_flow_summary"]


def test_capital_engine_generates_warnings():
    source = pd.DataFrame(
        [
            {
                "ticker": "600001",
                "name": "Weak Sample",
                "turnover": 10_000_000,
                "turnover_rate": 25.0,
                "volume_ratio": 0.5,
                "main_net_inflow_ratio": -8.0,
                "northbound_change": -50_000_000,
                "capital_activity_score": 30,
            }
        ]
    )

    result = build_capital_scores(source)
    warning = result.loc[0, "capital_flow_warning"]

    assert "量比过低" in warning
    assert "主力持续流出" in warning
    assert "北向持续减仓" in warning
    assert "换手异常" in warning
    assert result.loc[0, "capital_flow_strength"] in {"Weak", "Very Weak", "Medium"}


def test_capital_engine_handles_abnormal_data():
    source = pd.DataFrame(
        [
            {
                "ticker": "bad-code",
                "turnover": "--",
                "turnover_rate": "not-a-number",
                "volume_ratio": None,
                "main_net_inflow_ratio": "5%",
                "northbound_change": "",
                "capital_activity_score": True,
            }
        ]
    )

    result = build_capital_scores(source)

    assert 0 <= result.loc[0, "capital_flow_score"] <= 100
    assert result.loc[0, "capital_flow_strength"] in {"Strong Buy Research", "Strong", "Medium", "Weak", "Very Weak"}
    assert isinstance(result.loc[0, "capital_flow_summary"], str)


def test_capital_engine_ranks_by_score_without_mutating_input():
    source = pd.DataFrame(
        [
            {"ticker": "600000", "turnover_rate": 8, "volume_ratio": 2.5, "main_net_inflow_ratio": 8, "northbound_change": 100_000_000, "capital_activity_score": 90},
            {"ticker": "600001", "turnover_rate": 1, "volume_ratio": 0.6, "main_net_inflow_ratio": -8, "northbound_change": -50_000_000, "capital_activity_score": 20},
        ]
    )
    original = source.copy(deep=True)

    result = build_capital_scores(source)

    assert result.loc[0, "capital_flow_rank"] == 1
    assert result.loc[1, "capital_flow_rank"] == 2
    pd.testing.assert_frame_equal(source, original)


def test_capital_engine_cache_hit_and_invalidation(tmp_path, monkeypatch):
    cache_file = tmp_path / "capital_score_cache.csv"
    monkeypatch.setattr(capital_engine, "CAPITAL_SCORE_CACHE_FILE", cache_file)
    source = pd.DataFrame(
        [
            {"ticker": "600000", "turnover_rate": 8, "volume_ratio": 2.5, "main_net_inflow_ratio": 8, "northbound_change": 100_000_000, "capital_activity_score": 90},
        ]
    )

    first = capital_engine.build_capital_scores(source, use_cache=True)
    second = capital_engine.build_capital_scores(source, use_cache=True)
    changed = source.copy()
    changed.loc[0, "main_net_inflow_ratio"] = -8
    third = capital_engine.build_capital_scores(changed, use_cache=True)

    assert cache_file.exists()
    assert first.attrs["capital_score_cache_status"] == "Saved"
    assert second.attrs["capital_score_cache_status"] == "Hit"
    assert third.attrs["capital_score_cache_status"] == "Saved"
    assert third.loc[0, "capital_flow_score"] != second.loc[0, "capital_flow_score"]
