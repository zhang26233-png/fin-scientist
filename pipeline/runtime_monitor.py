"""Runtime monitoring helpers for scheduled research pipeline runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from time import perf_counter
from typing import Any
from uuid import uuid4

import pandas as pd


SCHEDULER_REPORT_COLUMNS = [
    "run_id",
    "start_time",
    "end_time",
    "total_seconds",
    "stage_name",
    "stage_input_rows",
    "stage_output_rows",
    "stage_seconds",
    "stage_status",
    "stage_warning",
    "data_source_summary",
    "final_rows",
    "core_count",
    "watch_count",
    "exclude_count",
    "max_score",
    "min_score",
    "mean_score",
    "bucket_distribution",
]


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class PipelineRunReport:
    """Collect stage-level scheduler diagnostics."""

    run_id: str = field(default_factory=lambda: uuid4().hex)
    start_time: str = field(default_factory=_now_text)
    end_time: str = ""
    total_seconds: float = 0.0
    data_source_summary: str = ""
    final_summary: dict[str, Any] = field(default_factory=dict)
    _started_at: float = field(default_factory=perf_counter, repr=False)
    _stages: list[dict[str, Any]] = field(default_factory=list, repr=False)

    def add_stage(
        self,
        stage_name: str,
        stage_input_rows: int,
        stage_output_rows: int,
        stage_seconds: float,
        stage_status: str = "OK",
        stage_warning: str = "",
    ) -> None:
        self._stages.append(
            {
                "run_id": self.run_id,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "total_seconds": self.total_seconds,
                "stage_name": stage_name,
                "stage_input_rows": int(stage_input_rows or 0),
                "stage_output_rows": int(stage_output_rows or 0),
                "stage_seconds": max(0.0, round(float(stage_seconds or 0.0), 4)),
                "stage_status": stage_status or "OK",
                "stage_warning": stage_warning or "",
                "data_source_summary": self.data_source_summary or "",
                "final_rows": 0,
                "core_count": 0,
                "watch_count": 0,
                "exclude_count": 0,
                "max_score": None,
                "min_score": None,
                "mean_score": None,
                "bucket_distribution": "",
            }
        )

    def set_final_summary(self, summary: dict[str, Any]) -> None:
        self.final_summary = dict(summary or {})
        for stage in self._stages:
            stage.update(self.final_summary)

    def finish(self, data_source_summary: str = "") -> None:
        self.end_time = _now_text()
        self.total_seconds = max(0.0, round(perf_counter() - self._started_at, 4))
        if data_source_summary:
            self.data_source_summary = data_source_summary
        for stage in self._stages:
            stage["end_time"] = self.end_time
            stage["total_seconds"] = self.total_seconds
            stage["data_source_summary"] = self.data_source_summary
            if self.final_summary:
                stage.update(self.final_summary)

    def to_dataframe(self) -> pd.DataFrame:
        if not self.end_time:
            self.finish(self.data_source_summary)
        return pd.DataFrame(self._stages, columns=SCHEDULER_REPORT_COLUMNS)


__all__ = ["PipelineRunReport", "SCHEDULER_REPORT_COLUMNS"]
