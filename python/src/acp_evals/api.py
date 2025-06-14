"""
Simple, developer-friendly evaluation API for ACP agents.

This module provides easy-to-use evaluation classes that handle complexity internally,
allowing developers to evaluate their agents with minimal code.
"""

import asyncio
from typing import Any

# Import evaluators
from .evaluators.accuracy import AccuracyEval

# Import common components
from .evaluators.common import BatchResult, EvalResult
from .evaluators.performance import PerformanceEval

# Re-export quality evaluators
from .evaluators.quality.quality import (
    CompletenessEval,
    GroundednessEval,
    QualityEval,
    TaskAdherenceEval,
    ToolAccuracyEval,
)
from .evaluators.reliability import ReliabilityEval
from .evaluators.safety import SafetyEval

# Export all evaluators
__all__ = [
    # Common
    "EvalResult",
    "BatchResult",
    # Core evaluators
    "AccuracyEval",
    "PerformanceEval",
    "ReliabilityEval",
    "SafetyEval",
    # Quality evaluators
    "GroundednessEval",
    "CompletenessEval",
    "TaskAdherenceEval",
    "ToolAccuracyEval",
    "QualityEval",
    # Helper function
    "evaluate",
]


# Convenience function for synchronous usage
def evaluate(eval_obj: Any, *args, **kwargs) -> EvalResult:
    """
    Run evaluation synchronously.

    Example:
        result = evaluate(
            AccuracyEval(agent="http://localhost:8000/agents/my-agent"),
            input="What is 2+2?",
            expected="4",
            print_results=True
        )
    """
    return asyncio.run(eval_obj.run(*args, **kwargs))

