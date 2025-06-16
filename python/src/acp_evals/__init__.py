"""
ACP Evals: Comprehensive Evaluation Framework for Agent Communication Protocol

A framework for benchmarking, measuring, and analyzing agent performance
in the ACP ecosystem.

Quick Start:
    For most use cases, import the main evaluation classes:
    >>> from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval, SafetyEval
    
    For specialized metrics and advanced evaluators:
    >>> from acp_evals.evaluators import BleuScoreEvaluator, RetrievalEvaluator
"""

__version__ = "0.1.2"

# Load configuration on import
# Core framework classes
from acp_evals.core.base import (
    BenchmarkResult,
    BenchmarkTask,
    MetricResult,
    TokenUsage,
)

# Quality evaluators
from acp_evals.evaluators.quality.quality import (
    CompletenessEval,
    GroundednessEval,
    QualityEval,
    TaskAdherenceEval,
    ToolAccuracyEval,
)

# Simulator for synthetic test data
from acp_evals.pipeline.simulator import Simulator, simulate

# Main API for developer-friendly usage
from acp_evals.api import (
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
    # Main API (primary interface)
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
    from acp_evals.pipeline.continuous import (
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

# Import evaluators if available
try:
    from acp_evals.evaluators import (
        # Core evaluators
        GroundednessEvaluator,
        RetrievalEvaluator,
        DocumentRetrievalEvaluator,
        # Extended evaluators
        IntentResolutionEvaluator,
        ResponseCompletenessEvaluator,
        CodeVulnerabilityEvaluator,
        UngroundedAttributesEvaluator,
        ProtectedMaterialEvaluator,
        ToolCallAccuracyEvaluator,
        # NLP metrics
        BleuScoreEvaluator,
        RougeScoreEvaluator,
        MeteorScoreEvaluator,
        GleuScoreEvaluator,
        F1ScoreEvaluator,
        # Composite evaluators
        QAEvaluator,
        ContentSafetyEvaluator,
        ComprehensiveEvaluator,
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
