"""
ACP Evals: Comprehensive Evaluation Framework for Agent Communication Protocol

A framework for benchmarking, measuring, and analyzing agent performance
in the ACP ecosystem.
"""

__version__ = "0.1.0"

# Load configuration on import
# Core framework classes
from acp_evals.core.base import (
    BenchmarkResult,
    BenchmarkTask,
    MetricResult,
    TokenUsage,
)

# Quality evaluators
from acp_evals.evaluation.quality import (
    CompletenessEval,
    GroundednessEval,
    QualityEval,
    TaskAdherenceEval,
    ToolAccuracyEval,
)

# Simulator for synthetic test data
from acp_evals.evaluation.simulator import Simulator, simulate

# Simple API for developer-friendly usage
from acp_evals.simple import (
    AccuracyEval,
    BatchResult,
    EvalResult,
    PerformanceEval,
    ReliabilityEval,
    SafetyEval,
    evaluate,
)

from .core import config

__all__ = [
    # Simple API (primary interface)
    "AccuracyEval",
    "PerformanceEval",
    "ReliabilityEval",
    "SafetyEval",
    "EvalResult",
    "BatchResult",
    "evaluate",
    # Simulator
    "Simulator",
    "simulate",
    # Quality evaluators
    "GroundednessEval",
    "CompletenessEval",
    "TaskAdherenceEval",
    "ToolAccuracyEval",
    "QualityEval",
    # Core classes
    "MetricResult",
    "TokenUsage",
    "BenchmarkResult",
    "BenchmarkTask",
]

# Import continuous evaluation
try:
    from acp_evals.evaluation.continuous import (
        ContinuousEvaluationPipeline,
        EvaluationRun,
        RegressionAlert,
        start_continuous_evaluation,
    )
    __all__.extend([
        "ContinuousEvaluationPipeline",
        "start_continuous_evaluation",
        "EvaluationRun",
        "RegressionAlert",
    ])
except ImportError:
    # Continuous evaluation requires additional dependencies
    pass

# Import new evaluators
try:
    from acp_evals.evaluators import (
        # NLP metrics
        BleuScoreEvaluator,
        CodeVulnerabilityEvaluator,
        ComprehensiveEvaluator,
        ContentSafetyEvaluator,
        DocumentRetrievalEvaluator,
        F1ScoreEvaluator,
        GleuScoreEvaluator,
        GroundednessEvaluator,
        # Extended evaluators
        IntentResolutionEvaluator,
        MeteorScoreEvaluator,
        ProtectedMaterialEvaluator,
        # Composite evaluators
        QAEvaluator,
        ResponseCompletenessEvaluator,
        RetrievalEvaluator,
        RougeScoreEvaluator,
        ToolCallAccuracyEvaluator,
        UngroundedAttributesEvaluator,
    )
    __all__.extend([
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
    ])
except ImportError:
    # Evaluators available but not required
    pass
