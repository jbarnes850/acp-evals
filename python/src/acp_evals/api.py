"""
Simple, developer-friendly evaluation API for ACP agents.

This module provides easy-to-use evaluation classes that handle complexity internally,
allowing developers to evaluate their agents with minimal code.
"""

import asyncio
from typing import Any

# Import common components
from .evaluators.common import EvalResult, BatchResult

# Import evaluators
from .evaluators.accuracy import AccuracyEval
from .evaluators.performance import PerformanceEval
from .evaluators.reliability import ReliabilityEval
from .evaluators.safety import SafetyEval

# Re-export quality evaluators
from .evaluators.quality.quality import (
    GroundednessEval,
    RelevanceEval,
    CoherenceEval,
    FluencyEval,
    RetrievalEval,
    SimilarityEval,
    DocumentRetrievalEval,
)

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
    "RelevanceEval", 
    "CoherenceEval",
    "FluencyEval",
    "RetrievalEval",
    "SimilarityEval",
    "DocumentRetrievalEval",
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