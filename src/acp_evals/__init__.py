"""
ACP-Evals: Simple, powerful agent evaluation.

Professional developer tools for evaluating AI agents:

    from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

    # Test accuracy
    eval = AccuracyEval("http://localhost:8000/agent")
    result = await eval.run("What is 2+2?", "4")

    # Test performance
    perf = PerformanceEval("http://localhost:8000/agent")
    result = await perf.run("Hello")

    # Test reliability
    reliable = ReliabilityEval("http://localhost:8000/agent")
    result = await reliable.run("Handle this edge case")
"""

__version__ = "0.1.2"

# The 3 core evaluation types every professional needs
from .api import (
    AccuracyEval,
    EvalResult,
    PerformanceEval,
    ReliabilityEval,
)

# Keep config available
from .core import config  # noqa: F401

# Core types
from .core.base import (
    AgentInfo,
    BenchmarkTask,
    MetricResult,
    TokenUsage,
)

__all__ = [
    # The essentials - clean, focused, powerful
    "AccuracyEval",
    "PerformanceEval",
    "ReliabilityEval",
    "EvalResult",
    # Core types
    "MetricResult",
    "TokenUsage",
    "BenchmarkTask",
    "AgentInfo",
]
