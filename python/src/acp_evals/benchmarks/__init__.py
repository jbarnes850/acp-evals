"""
Benchmarks for evaluating ACP agents.

This package provides various benchmarks to test agent capabilities
across different dimensions.
"""

from acp_evals.benchmarks.context_scaling import ContextScalingBenchmark
from acp_evals.benchmarks.multi_agent import HandoffQualityBenchmark, PatternComparisonBenchmark

__all__ = [
    "ContextScalingBenchmark",
    "HandoffQualityBenchmark",
    "PatternComparisonBenchmark",
]