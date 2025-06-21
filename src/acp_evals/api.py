"""
Simple, developer-friendly evaluation API for ACP agents.

This module provides easy-to-use evaluation classes that handle complexity internally,
allowing developers to evaluate their agents with minimal code.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Optional, Dict, Union, Callable

# Import evaluators
from .evaluators.accuracy import AccuracyEval as _BaseAccuracyEval

# Import common components
from .evaluators.common import BatchResult, EvalResult
from .evaluators.performance import PerformanceEval as _BasePerformanceEval

# Re-export quality evaluators
from .evaluators.quality.quality import (
    CompletenessEval,
    GroundednessEval,
    QualityEval,
    TaskAdherenceEval,
    ToolAccuracyEval,
)
from .evaluators.reliability import ReliabilityEval as _BaseReliabilityEval
from .evaluators.safety import SafetyEval as _BaseSafetyEval


@dataclass
class EvalOptions:
    """Configuration options for evaluations."""
    rubric: Optional[str] = None
    threshold: float = 0.7
    judge_model: Optional[str] = None
    binary_mode: bool = False
    max_retries: int = 0
    timeout: Optional[float] = None


class AccuracyEval(_BaseAccuracyEval):
    """Evaluate agent accuracy with minimal configuration."""
    
    def __init__(
        self, 
        agent: Union[str, Callable], 
        options: Optional[EvalOptions] = None
    ):
        """
        Initialize accuracy evaluator.
        
        Args:
            agent: Agent URL or callable function
            options: Optional configuration settings
        """
        options = options or EvalOptions()
        
        # Use sensible defaults
        super().__init__(
            agent=agent,
            judge_model=options.judge_model,
            rubric=options.rubric or "factual",
            pass_threshold=options.threshold,
            binary_mode=options.binary_mode,
            name="Accuracy Evaluation"
        )
    
    async def run(
        self,
        input: str,
        expected: str,
        print_results: bool = True,
        **kwargs
    ) -> EvalResult:
        """
        Run evaluation with minimal parameters.
        
        Args:
            input: Test input
            expected: Expected output
            print_results: Whether to display results
            **kwargs: Additional parameters for advanced usage
        """
        return await super().run(
            input=input,
            expected=expected,
            print_results=print_results,
            **kwargs
        )


class PerformanceEval(_BasePerformanceEval):
    """Evaluate agent performance with minimal configuration."""
    
    def __init__(
        self,
        agent: Union[str, Callable],
        options: Optional[EvalOptions] = None
    ):
        """
        Initialize performance evaluator.
        
        Args:
            agent: Agent URL or callable function
            options: Optional configuration settings
        """
        options = options or EvalOptions()
        
        super().__init__(
            agent=agent,
            judge_model=options.judge_model,
            name="Performance Evaluation"
        )


class ReliabilityEval(_BaseReliabilityEval):
    """Evaluate agent reliability with minimal configuration."""
    
    def __init__(
        self,
        agent: Union[str, Callable],
        options: Optional[EvalOptions] = None
    ):
        """
        Initialize reliability evaluator.
        
        Args:
            agent: Agent URL or callable function
            options: Optional configuration settings
        """
        options = options or EvalOptions()
        
        super().__init__(
            agent=agent,
            judge_model=options.judge_model,
            pass_threshold=options.threshold,
            name="Reliability Evaluation"
        )


class SafetyEval(_BaseSafetyEval):
    """Evaluate agent safety with minimal configuration."""
    
    def __init__(
        self,
        agent: Union[str, Callable],
        options: Optional[EvalOptions] = None
    ):
        """
        Initialize safety evaluator.
        
        Args:
            agent: Agent URL or callable function
            options: Optional configuration settings
        """
        options = options or EvalOptions()
        
        super().__init__(
            agent=agent,
            judge_model=options.judge_model,
            pass_threshold=options.threshold,
            name="Safety Evaluation"
        )


# Export all evaluators
__all__ = [
    # Common
    "EvalResult",
    "BatchResult",
    "EvalOptions",
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
    # Helper functions
    "evaluate",
    "test_agent",
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


def test_agent(agent: Union[str, Callable]) -> Dict[str, EvalResult]:
    """
    Run a basic test suite on an agent.
    
    Args:
        agent: Agent URL or callable function
        
    Returns:
        Dictionary of evaluation results
    """
    results = {}
    
    # Basic accuracy test
    accuracy = AccuracyEval(agent)
    results["accuracy"] = evaluate(
        accuracy,
        input="What is the capital of France?",
        expected="Paris"
    )
    
    # Basic performance test
    performance = PerformanceEval(agent)
    results["performance"] = evaluate(
        performance,
        input="Hello, how are you?",
        expected="A friendly greeting response"
    )
    
    return results


# Namespace for cleaner API
class evaluate:
    """Namespace for simple evaluation functions."""
    
    @staticmethod
    def accuracy(
        agent: Union[str, Callable],
        input: str,
        expected: str,
        **kwargs
    ) -> EvalResult:
        """Quick accuracy evaluation."""
        eval_obj = AccuracyEval(agent)
        return asyncio.run(eval_obj.run(input, expected, **kwargs))
    
    @staticmethod
    def performance(
        agent: Union[str, Callable],
        input: str,
        expected: str,
        **kwargs
    ) -> EvalResult:
        """Quick performance evaluation."""
        eval_obj = PerformanceEval(agent)
        return asyncio.run(eval_obj.run(input, expected, **kwargs))
    
    @staticmethod
    def safety(
        agent: Union[str, Callable],
        input: str,
        expected: str,
        **kwargs
    ) -> EvalResult:
        """Quick safety evaluation."""
        eval_obj = SafetyEval(agent)
        return asyncio.run(eval_obj.run(input, expected, **kwargs))
    
    @staticmethod
    def reliability(
        agent: Union[str, Callable],
        input: str,
        expected_tool_calls: list,
        **kwargs
    ) -> EvalResult:
        """Quick reliability evaluation."""
        eval_obj = ReliabilityEval(agent)
        return asyncio.run(eval_obj.run(input, expected_tool_calls, **kwargs))
