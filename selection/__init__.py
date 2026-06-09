"""Read-only stock selection research package."""

from selection.explain_engine import EXPLAIN_SELECTION_FIELDS, build_explainable_selection
from selection.stock_selection import STOCK_SELECTION_FIELDS, build_stock_selection

__all__ = [
    "EXPLAIN_SELECTION_FIELDS",
    "STOCK_SELECTION_FIELDS",
    "build_explainable_selection",
    "build_stock_selection",
]
