"""
Metrics for evaluating ACP agents.

This package provides various metrics to measure agent performance,
efficiency, and quality.
"""

from acp_evals.metrics.classification import (
    BinaryClassificationCalculator,
    ClassificationMetrics,
    MultiClassMetricsCalculator,
    evaluate_evaluator_performance,
)
from acp_evals.metrics.context import ContextEfficiencyMetric
from acp_evals.metrics.cost import CostMetric
from acp_evals.metrics.handoff_quality import HandoffQualityMetric
from acp_evals.metrics.latency import LatencyMetric
from acp_evals.metrics.token_usage import TokenUsageMetric

__all__ = [
    # Performance metrics
    "TokenUsageMetric",
    "LatencyMetric",
    "ContextEfficiencyMetric",
    "CostMetric",
    "HandoffQualityMetric",
    # Classification metrics
    "ClassificationMetrics",
    "BinaryClassificationCalculator",
    "MultiClassMetricsCalculator",
    "evaluate_evaluator_performance",
]
