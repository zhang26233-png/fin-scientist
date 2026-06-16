import copy
import importlib

import pandas as pd

from pipeline.live_runner import LIVE_PIPELINE_FIELDS, run_live_pipeline


def test_live_runner_importable():
    assert importlib.import_module("pipeline.live_runner")


def test_run_live_pipeline_returns_dataframe():
    result = run_live_pipeline(max_stocks=20)

    assert isinstance(result, pd.DataFrame)


def test_data_source_failure_returns_demo_dataframe(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: pd.DataFrame())
    result = live_runner.run_live_pipeline(max_stocks=20)

    assert result.attrs.get("is_demo") is True
    assert len(result) >= 20


def test_cache_universe_is_not_forced_to_demo(monkeypatch):
    import pipeline.live_runner as live_runner

    rows = [
        {
            "ticker": f"6{index:05d}",
            "name": f"Cached {index}",
            "market": "SH",
            "industry": "",
            "list_date": "2020-01-01",
            "status": "Available",
            "latest_price": 10.0,
            "pct_change": 0.1,
        }
        for index in range(1101)
    ]
    frame = pd.DataFrame(rows)
    frame.attrs["data_source"] = "Local Cache"
    frame.attrs["data_status"] = "Cache"
    frame.attrs["raw_count"] = 1101
    frame.attrs["filtered_count"] = 0
    frame.attrs["final_count"] = 1101
    frame.attrs["cache_status"] = "Available"
    frame.attrs["cache_updated_at"] = "2026-06-15 10:00:00"

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: frame)
    result = live_runner.run_live_pipeline(max_stocks=1101, kline_enabled=False)

    assert result.attrs.get("is_demo") is False
    assert result.attrs["data_source"] == "Local Cache"
    assert result.attrs["data_status"] == "Cache"
    assert result.attrs["cache_status"] == "Available"


def test_demo_dataframe_has_required_selection_explain_and_factor_fields(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: pd.DataFrame())
    result = live_runner.run_live_pipeline(max_stocks=20)

    for field in LIVE_PIPELINE_FIELDS:
        assert field in result.columns
    assert "selection_score" in result.columns
    assert "selection_rank" in result.columns
    assert "selection_bucket" in result.columns
    assert "selection_explanation" in result.columns
    assert "factor_ic" in result.columns
    assert "factor_rank_ic" in result.columns
    assert "factor_effectiveness_label" in result.columns


def test_input_price_history_is_not_mutated(monkeypatch):
    import pipeline.live_runner as live_runner

    history = {"600519": pd.DataFrame({"date": pd.date_range("2024-01-01", periods=80), "close": range(80)})}
    original = copy.deepcopy(history)
    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: pd.DataFrame())

    live_runner.run_live_pipeline(price_history_dict=history)

    pd.testing.assert_frame_equal(history["600519"], original["600519"])


def test_app_importable_after_live_pipeline_addition():
    assert importlib.import_module("app")


def _large_live_universe(rows=1002):
    frame = pd.DataFrame(
        [
            {
                "ticker": f"6{index:05d}",
                "name": f"Live {index}",
                "market": "SH",
                "industry": "",
                "list_date": "2020-01-01",
                "status": "Available",
                "latest_price": 10.0,
                "pct_change": 0.1,
                "volume": 1_000_000,
                "turnover": 20_000_000,
                "open": 9.8,
                "high": 10.2,
                "low": 9.7,
                "prev_close": 9.9,
            }
            for index in range(rows)
        ]
    )
    frame.attrs["data_source"] = "Tencent Realtime"
    frame.attrs["data_status"] = "Live"
    frame.attrs["raw_count"] = rows
    frame.attrs["filtered_count"] = 0
    frame.attrs["final_count"] = rows
    return frame


def test_kline_disabled_does_not_call_history_builder(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())

    def fail_builder(*args, **kwargs):
        raise AssertionError("K-line builder should not be called")

    monkeypatch.setattr(live_runner, "build_price_history_dict", fail_builder)
    result = live_runner.run_live_pipeline(kline_enabled=False)

    assert result.attrs["kline_status"] == "Disabled"


def test_kline_enabled_passes_price_history_dict(monkeypatch):
    import pipeline.live_runner as live_runner

    captured = {}
    history = pd.DataFrame({"date": pd.date_range("2025-01-01", periods=80), "close": range(80), "volume": range(80)})
    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())

    def fake_builder(tickers, **kwargs):
        captured["tickers"] = list(tickers)
        return {"600000": history, "_attrs": {"requested": len(tickers), "loaded": 1, "cache_hits": 0, "failures": 0, "attempts": []}}

    monkeypatch.setattr(live_runner, "build_price_history_dict", fake_builder)
    result = live_runner.run_live_pipeline(kline_enabled=True, max_kline_stocks=1)

    assert captured["tickers"] == ["600000"]
    assert result.attrs["kline_requested"] == 1
    assert result["technical_history_available"].astype(bool).any()


def test_no_kline_data_does_not_crash(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())
    monkeypatch.setattr(
        live_runner,
        "build_price_history_dict",
        lambda *args, **kwargs: {"_attrs": {"requested": 1, "loaded": 0, "cache_hits": 0, "failures": 1, "attempts": []}},
    )

    result = live_runner.run_live_pipeline(kline_enabled=True, max_kline_stocks=1)

    assert isinstance(result, pd.DataFrame)
    assert result.attrs["kline_failures"] == 1


def test_fundamental_disabled_does_not_call_external_builder(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())

    def existing_only(existing_df=None, tickers=None, **kwargs):
        assert kwargs.get("use_external") is False
        return pd.DataFrame([{"ticker": "600000", "pe_ttm": 10, "pb": 1.2, "roe": 18}])

    monkeypatch.setattr(live_runner, "build_fundamental_dataset", existing_only)
    result = live_runner.run_live_pipeline(kline_enabled=False, fundamental_enabled=False)

    assert result.attrs["fundamental_enabled"] is False


def test_fundamental_enabled_passes_fundamental_dataset(monkeypatch):
    import pipeline.live_runner as live_runner

    captured = {}
    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())

    def fake_builder(existing_df=None, tickers=None, **kwargs):
        captured["use_external"] = kwargs.get("use_external")
        frame = pd.DataFrame(
            [
                {
                    "ticker": "600000",
                    "pe_ttm": 10,
                    "pb": 1.2,
                    "roe": 18,
                    "revenue_growth_yoy": 12,
                    "net_profit_growth_yoy": 22,
                    "debt_to_asset": 45,
                    "fundamental_data_source": "Test Fundamental",
                    "fundamental_data_status": "Available",
                }
            ]
        )
        frame.attrs["fundamental_data_source"] = "Test Fundamental"
        frame.attrs["fundamental_data_status"] = "Available"
        frame.attrs["fundamental_rows"] = 1
        return frame

    monkeypatch.setattr(live_runner, "build_fundamental_dataset", fake_builder)
    result = live_runner.run_live_pipeline(kline_enabled=False, fundamental_enabled=True)

    assert captured["use_external"] is True
    assert result.attrs["fundamental_data_source"] == "Test Fundamental"
    assert "activated_fundamental_score" in result.columns
    assert result["fundamental_available"].astype(bool).any()


def test_capital_news_industry_disabled_still_runs(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())
    result = live_runner.run_live_pipeline(
        kline_enabled=False,
        fundamental_enabled=False,
        capital_flow_enabled=False,
        news_enabled=False,
        industry_enabled=False,
    )

    assert isinstance(result, pd.DataFrame)
    assert result.attrs["capital_flow_enabled"] is False
    assert result.attrs["news_enabled"] is False
    assert result.attrs["industry_enabled"] is False
    assert "capital_flow_score" in result.columns
    assert "news_event_score" in result.columns
    assert "industry_strength_score" in result.columns


def test_external_capital_news_industry_failure_still_outputs_research_df(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())
    monkeypatch.setattr(live_runner, "build_capital_flow_dataset", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr(live_runner, "build_news_dataset", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr(live_runner, "build_industry_dataset", lambda *args, **kwargs: pd.DataFrame())

    result = live_runner.run_live_pipeline(kline_enabled=False, fundamental_enabled=False)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "activated_selection_score" in result.columns


def test_news_event_disabled_keeps_pipeline_running(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())
    result = live_runner.run_live_pipeline(kline_enabled=False, fundamental_enabled=False, news_event_enabled=False)

    assert isinstance(result, pd.DataFrame)
    assert result.attrs["news_event_enabled"] is False
    assert "news_event_score" in result.columns


def test_news_event_enabled_generates_score(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())

    def fake_news(*args, **kwargs):
        frame = pd.DataFrame([{"ticker": "600000", "news_title": "公司AI算力订单增长", "news_time": "2026-06-16"}])
        frame.attrs["news_source"] = "Test News"
        frame.attrs["news_status"] = "Available"
        frame.attrs["news_rows"] = 1
        return frame

    monkeypatch.setattr(live_runner, "build_news_dataset", fake_news)
    result = live_runner.run_live_pipeline(kline_enabled=False, fundamental_enabled=False, news_event_enabled=True)

    row = result[result["ticker"].astype(str).eq("600000")].iloc[0]
    assert row["news_event_score"] >= 70
    assert result.attrs["news_status"] == "Available"


def test_news_source_failure_does_not_block_research_df(monkeypatch):
    import pipeline.live_runner as live_runner

    monkeypatch.setattr(live_runner, "load_a_share_universe", lambda: _large_live_universe())

    empty = pd.DataFrame()
    empty.attrs["news_source"] = "Test News"
    empty.attrs["news_status"] = "Error"
    empty.attrs["news_rows"] = 0
    empty.attrs["news_warning"] = "source failed"
    monkeypatch.setattr(live_runner, "build_news_dataset", lambda *args, **kwargs: empty)

    result = live_runner.run_live_pipeline(kline_enabled=False, fundamental_enabled=False, news_event_enabled=True)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "activated_selection_score" in result.columns
