import copy
from pathlib import Path

import pandas as pd

from strategy.preview import (
    PREVIEW_COLUMNS,
    build_strategy_preview,
    build_strategy_preview_row,
    export_strategy_preview_to_csv,
    export_strategy_preview_to_json_like,
)


FORBIDDEN_STRATEGY_PREVIEW_WORDS = [
    "\u4e70\u5165",
    "\u5356\u51fa",
    "\u6ee1\u4ed3",
    "\u68ad\u54c8",
    "\u5fc5\u6da8",
    "\u7a33\u8d5a",
]


def assert_no_forbidden_words(value):
    text = str(value)
    for word in FORBIDDEN_STRATEGY_PREVIEW_WORDS:
        assert word not in text


def make_candidate_pool():
    return pd.DataFrame(
        [
            {
                "symbol": "LOW1",
                "name": "Low Sample",
                "Close": 100,
                "return_20d": -0.08,
                "return_10d": -0.04,
                "return_5d": -0.02,
                "volume": 60_000,
                "amount": 3_000_000,
                "turnover": 0.001,
                "volume_ratio": 0.7,
                "volatility": 0.35,
                "valid_trading_days": 90,
                "score": 42,
            },
            {
                "symbol": "HIGH1",
                "name": "High Sample",
                "Close": 100,
                "return_20d": 0.16,
                "return_10d": 0.09,
                "return_5d": 0.04,
                "volume": 1_500_000,
                "amount": 160_000_000,
                "turnover": 0.04,
                "volume_ratio": 1.4,
                "volatility": 0.25,
                "valid_trading_days": 90,
                "score": 66,
            },
            {
                "symbol": "RISK1",
                "name": "Risk Sample",
                "Close": 100,
                "return_20d": 0.42,
                "return_10d": 0.28,
                "return_5d": 0.18,
                "volume": 1_800_000,
                "amount": 200_000_000,
                "turnover": 0.18,
                "volume_ratio": 2.2,
                "volatility": 0.95,
                "valid_trading_days": 90,
                "score": 72,
            },
        ]
    )


def test_strategy_preview_import_and_empty_dataframe_safe_return():
    preview = build_strategy_preview(pd.DataFrame())

    assert list(preview.columns) == PREVIEW_COLUMNS
    assert preview.empty
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_missing_fields_safe_return():
    preview = build_strategy_preview(pd.DataFrame([{"symbol": "MISSING"}]))

    assert len(preview) == 1
    assert preview.iloc[0]["symbol"] == "MISSING"
    assert preview.iloc[0]["strategy_score"] == 0
    assert preview.iloc[0]["dominant_style"]
    assert isinstance(preview.iloc[0]["data_quality_labels"], list)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_row_contains_core_fields():
    row = build_strategy_preview_row(make_candidate_pool().iloc[1])

    assert row["symbol"] == "HIGH1"
    assert row["strategy_score"] is not None
    assert row["best_preset"]
    assert row["dominant_style"]
    assert row["consensus_level"]
    assert row["balanced_research_score"] is not None
    assert row["trend_momentum_score"] is not None
    assert row["volume_breakout_score"] is not None
    assert row["low_risk_quality_score"] is not None
    assert row["high_elasticity_watch_score"] is not None
    assert_no_forbidden_words(row)


def test_strategy_preview_does_not_modify_source_dataframe():
    frame = make_candidate_pool()
    before = copy.deepcopy(frame)

    build_strategy_preview(frame)

    pd.testing.assert_frame_equal(frame, before)


def test_strategy_preview_preserves_input_order_by_default():
    frame = make_candidate_pool()
    preview = build_strategy_preview(frame)

    assert list(preview["symbol"]) == ["LOW1", "HIGH1", "RISK1"]
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_sort_by_strategy_only_changes_preview_order():
    frame = make_candidate_pool()
    before = copy.deepcopy(frame)
    preview = build_strategy_preview(frame, sort_by_strategy=True)

    assert list(preview["symbol"]) != ["LOW1", "HIGH1", "RISK1"]
    assert preview.iloc[0]["strategy_score"] >= preview.iloc[-1]["strategy_score"]
    pd.testing.assert_frame_equal(frame, before)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_keeps_risk_and_data_quality_labels():
    preview = build_strategy_preview(make_candidate_pool())
    risk_row = preview[preview["symbol"] == "RISK1"].iloc[0]

    assert isinstance(risk_row["risk_labels"], list)
    assert "high_volatility" in risk_row["risk_labels"]
    assert isinstance(risk_row["data_quality_labels"], list)
    assert_no_forbidden_words(preview.to_dict())


def test_strategy_preview_json_like_export_is_stable():
    preview = build_strategy_preview(make_candidate_pool())
    payload = export_strategy_preview_to_json_like(preview)

    assert payload["schema_version"] == "strategy_preview.v1"
    assert payload["metadata"]["record_count"] == 3
    assert payload["metadata"]["uses_real_data_source"] is False
    assert payload["metadata"]["ui_connected"] is False
    assert payload["records"][0]["symbol"] == "LOW1"
    assert "strategy_score" in payload["records"][0]
    assert_no_forbidden_words(payload)


def test_strategy_preview_csv_export_writes_temp_file(tmp_path):
    preview = build_strategy_preview(make_candidate_pool())
    output_path = tmp_path / "strategy_preview.csv"

    result = export_strategy_preview_to_csv(preview, output_path)
    saved = pd.read_csv(output_path)

    assert result["row_count"] == 3
    assert Path(result["path"]).exists()
    assert len(saved) == 3
    assert "strategy_score" in saved.columns
    assert_no_forbidden_words(result)


def test_strategy_preview_not_used_by_legacy_or_screening_ui():
    legacy_text = Path("legacy_app.py").read_text(encoding="utf-8")
    screening_text = Path("ui/screening_ui.py").read_text(encoding="utf-8")

    assert "strategy.preview" not in legacy_text
    assert "build_strategy_preview" not in legacy_text
    assert "strategy.preview" not in screening_text
    assert "build_strategy_preview" not in screening_text
