"""
ACP Evals: Comprehensive Evaluation Framework for Agent Communication Protocol

A framework for benchmarking, measuring, and analyzing agent performance
in the ACP ecosystem.
"""

__version__ = "0.1.0"

# Simple API for developer-friendly usage
from acp_evals.simple import (
    AccuracyEval,
    PerformanceEval,
    ReliabilityEval,
    SafetyEval,
    EvalResult,
    BatchResult,
    evaluate,
)

# Simulator for synthetic test data
from acp_evals.simulator import Simulator, simulate

# Quality evaluators
from acp_evals.quality import (
    GroundednessEval,
    CompletenessEval,
    TaskAdherenceEval,
    ToolAccuracyEval,
    QualityEval,
)

# Core framework classes
from acp_evals.base import (
    BenchmarkResult,
    BenchmarkTask,
    MetricResult,
    TokenUsage,
)

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