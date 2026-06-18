"""Research activation helpers for Fin-Scientist."""

from research.score_activation import ACTIVATED_RESEARCH_FIELDS, activate_research_scores
from research.research_explainer import RESEARCH_EXPLAINER_FIELDS, build_research_explanation
from research.unified_ranking_engine import UNIFIED_RESEARCH_FIELDS, build_unified_research_score

__all__ = [
    "ACTIVATED_RESEARCH_FIELDS",
    "RESEARCH_EXPLAINER_FIELDS",
    "UNIFIED_RESEARCH_FIELDS",
    "activate_research_scores",
    "build_research_explanation",
    "build_unified_research_score",
]
