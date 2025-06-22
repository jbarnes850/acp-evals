"""
ACP-Evals API: Simple, powerful agent evaluation.

Professional developer tools focused on the 3 core evaluation types.
"""

from typing import Any, Optional, Union

from .evaluators.accuracy import AccuracyEval as _BaseAccuracyEval
from .evaluators.common import EvalResult
from .evaluators.performance import PerformanceEval as _BasePerformanceEval
from .evaluators.reliability import ReliabilityEval as _BaseReliabilityEval


class AccuracyEval(_BaseAccuracyEval):
    """
    Evaluate agent accuracy against expected outputs.

    Simple to start:
        eval = AccuracyEval("http://localhost:8000/agent")
        result = await eval.run("What is 2+2?", "4")

    Professional features:
        eval = AccuracyEval(
            agent_url,
            rubric="semantic",
            judge_model="gpt-4",
            pass_threshold=0.8
        )
    """

    def __init__(
        self,
        agent: str | Any,
        rubric: str = "factual",
        judge_model: str | None = None,
        pass_threshold: float = 0.7,
        **kwargs,
    ):
        super().__init__(
            agent=agent,
            rubric=rubric,
            judge_model=judge_model,
            pass_threshold=pass_threshold,
            **kwargs,
        )


class PerformanceEval(_BasePerformanceEval):
    """
    Evaluate agent performance: latency, throughput, resource usage.

    Simple to start:
        eval = PerformanceEval("http://localhost:8000/agent")
        result = await eval.run("Test prompt")

    Professional features:
        eval = PerformanceEval(
            agent_url,
            num_iterations=10,
            track_memory=True,
            warmup_runs=2
        )
    """

    def __init__(
        self,
        agent: str | Any,
        num_iterations: int = 5,
        track_memory: bool = False,
        warmup_runs: int = 1,
        **kwargs,
    ):
        super().__init__(
            agent=agent,
            num_iterations=num_iterations,
            track_memory=track_memory,
            warmup_runs=warmup_runs,
            **kwargs,
        )


class ReliabilityEval(_BaseReliabilityEval):
    """
    Evaluate agent reliability: consistency, error handling, recovery.

    Simple to start:
        eval = ReliabilityEval("http://localhost:8000/agent")
        result = await eval.run("Test prompt")

    Professional features:
        eval = ReliabilityEval(
            agent_url,
            tool_definitions=["search", "summarize"],
            test_error_handling=True
        )
    """

    def __init__(self, agent: str | Any, tool_definitions: list[str] | None = None, **kwargs):
        super().__init__(agent=agent, tool_definitions=tool_definitions, **kwargs)


# Export the simple, focused API
__all__ = ["AccuracyEval", "PerformanceEval", "ReliabilityEval", "EvalResult"]
