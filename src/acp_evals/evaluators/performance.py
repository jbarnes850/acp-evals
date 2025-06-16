"""
Performance evaluation for agent metrics.

This module provides the PerformanceEval class for tracking token usage,
latency, and costs during agent execution.
"""

from collections.abc import Callable
from typing import Any

from rich.progress import Progress, SpinnerColumn, TextColumn

from ..metrics.token_usage import TokenUsageMetric
from .common import BaseEval, EvalResult, console


class PerformanceEval(BaseEval):
    """
    Evaluate agent performance metrics.

    Example:
        perf = PerformanceEval(agent=my_agent)
        result = await perf.run(
            input="Analyze this document...",
            track_tokens=True,
            track_latency=True,
            print_results=True
        )
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        model: str = "gpt-4",
        name: str = "Performance Evaluation",
    ):
        """
        Initialize performance evaluator.

        Args:
            agent: Agent to evaluate
            model: Model name for token pricing
            name: Name of the evaluation
        """
        super().__init__(agent, name)
        self.model = model
        self.token_metric = TokenUsageMetric(model=model)

    async def run(
        self,
        input: str,
        track_tokens: bool = True,
        track_latency: bool = True,
        track_memory: bool = False,
        print_results: bool = False,
    ) -> EvalResult:
        """
        Run performance evaluation.

        Args:
            input: Input to send to agent
            track_tokens: Track token usage and costs
            track_latency: Track response time
            track_memory: Track memory usage (not implemented)
            print_results: Whether to print results

        Returns:
            EvalResult with performance metrics
        """

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running performance test...", total=None)

            # Run agent
            agent_result = await self._run_agent(input)

            progress.update(task, description="Analyzing metrics...")

        details = {}

        # Latency tracking
        if track_latency:
            details["latency_ms"] = agent_result["latency_ms"]
            details["latency_seconds"] = agent_result["latency_ms"] / 1000

        # Token tracking
        if track_tokens:
            response_tokens = self.token_metric._count_tokens(agent_result["response"])
            input_tokens = self.token_metric._count_tokens(input)
            total_tokens = input_tokens + response_tokens

            # Calculate cost
            costs = self.token_metric._get_model_costs(self.model)
            input_cost = (input_tokens / 1000) * costs["input"]
            output_cost = (response_tokens / 1000) * costs["output"]
            total_cost = input_cost + output_cost

            details["tokens"] = {
                "input": input_tokens,
                "output": response_tokens,
                "total": total_tokens,
            }
            details["cost_usd"] = total_cost
            details["cost_per_1k_tokens"] = (
                (total_cost / total_tokens) * 1000 if total_tokens > 0 else 0
            )

        # Memory tracking (placeholder)
        if track_memory:
            details["memory_mb"] = "Not implemented"

        # Determine pass/fail based on thresholds
        passed = True
        score = 1.0

        # Check latency threshold (10 seconds)
        if track_latency and details["latency_seconds"] > 10:
            passed = False
            score *= 0.5

        # Check token threshold (10k tokens)
        if track_tokens and details["tokens"]["total"] > 10000:
            passed = False
            score *= 0.5

        result = EvalResult(
            name=self.name,
            passed=passed,
            score=score,
            details=details,
            metadata={
                "input": input,
                "response": agent_result["response"],
                "run_id": agent_result.get("run_id"),
            },
        )

        if print_results:
            result.print_summary()

        return result
