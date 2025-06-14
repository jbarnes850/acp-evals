"""
Evaluators for ACP agent outputs.
"""

from acp_evals.evaluators.base import EvaluationResult, Evaluator

# Composite evaluators
from acp_evals.evaluators.composite_evaluators import (
    CompositeResult,
    ComprehensiveEvaluator,
    ContentSafetyEvaluator,
    QAEvaluator,
)
from acp_evals.evaluators.document_retrieval import DocumentRetrievalEvaluator

# Extended evaluators
from acp_evals.evaluators.extended_evaluators import (
    CodeVulnerabilityEvaluator,
    IntentResolutionEvaluator,
    ProtectedMaterialEvaluator,
    ResponseCompletenessEvaluator,
    ToolCallAccuracyEvaluator,
    UngroundedAttributesEvaluator,
)
from acp_evals.evaluators.groundedness import GroundednessEvaluator
from acp_evals.evaluators.llm_judge import LLMJudge

# NLP metrics
from acp_evals.evaluators.nlp_metrics import (
    BleuScoreEvaluator,
    F1ScoreEvaluator,
    GleuScoreEvaluator,
    MeteorScoreEvaluator,
    RougeScoreEvaluator,
)
from acp_evals.evaluators.retrieval import RetrievalEvaluator

__all__ = [
    # Base
    "Evaluator",
    "EvaluationResult",
    "LLMJudge",

    # Core evaluators
    "GroundednessEvaluator",
    "RetrievalEvaluator",
    "DocumentRetrievalEvaluator",

    # Extended evaluators
    "IntentResolutionEvaluator",
    "ResponseCompletenessEvaluator",
    "CodeVulnerabilityEvaluator",
    "UngroundedAttributesEvaluator",
    "ProtectedMaterialEvaluator",
    "ToolCallAccuracyEvaluator",

    # NLP metrics
    "BleuScoreEvaluator",
    "RougeScoreEvaluator",
    "MeteorScoreEvaluator",
    "GleuScoreEvaluator",
    "F1ScoreEvaluator",

    # Composite evaluators
    "QAEvaluator",
    "ContentSafetyEvaluator",
    "ComprehensiveEvaluator",
    "CompositeResult",
]
