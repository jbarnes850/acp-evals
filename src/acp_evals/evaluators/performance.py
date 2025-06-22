"""
Performance evaluator for measuring agent latency and resource usage.

Competes with Agno's PerfEval but with ACP/BeeAI-specific enhancements.
"""

import asyncio
import statistics
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional, Union

from acp_sdk.models import Message, MessagePart

from ..evaluators.common import BaseEval, EvalResult

# Import display components
try:
    from ..cli.display import console, create_metrics_table, create_score_bar

    HAS_DISPLAY = True
except ImportError:
    HAS_DISPLAY = False


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""

    latency_ms: float
    memory_mb: float
    tokens_per_second: float | None = None
    time_to_first_token_ms: float | None = None


class PerformanceEval(BaseEval):
    """
    Evaluates agent performance metrics including latency and memory usage.

    This is ACP-Evals' answer to Agno's PerfEval, with additional
    metrics relevant to the BeeAI/ACP ecosystem.
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        num_iterations: int = 5,
        warmup_runs: int = 1,
        track_memory: bool = True,
        track_tokens: bool = True,
        name: str = "Performance Evaluation",
    ):
        """
        Initialize performance evaluator.

        Args:
            agent: Agent URL, callable, or instance
            num_iterations: Number of test iterations
            warmup_runs: Number of warmup runs before measurement
            track_memory: Whether to track memory usage
            track_tokens: Whether to track token metrics
            name: Name of the evaluation
        """
        super().__init__(agent, name)
        self.num_iterations = num_iterations
        self.warmup_runs = warmup_runs
        self.track_memory = track_memory
        self.track_tokens = track_tokens

    async def run(
        self, input_text: str | list[str], expected: str | None = None, print_results: bool = False
    ) -> EvalResult:
        """
        Run performance evaluation.

        Args:
            input_text: Input text or list of inputs for varied testing
            expected: Optional expected output (not used for scoring)
            print_results: Whether to print results using rich display

        Returns:
            EvalResult with performance metrics
        """
        # Convert single input to list
        inputs = [input_text] if isinstance(input_text, str) else input_text

        # Warmup runs
        for _ in range(self.warmup_runs):
            for inp in inputs:
                await self._run_agent(inp)

        # Measurement runs
        all_metrics: list[PerformanceMetrics] = []

        for i in range(self.num_iterations):
            for inp in inputs:
                metrics = await self._measure_single_run(inp)
                all_metrics.append(metrics)

        # Calculate statistics
        result = self._calculate_statistics(all_metrics)

        if print_results:
            # Use rich display components for comprehensive performance evaluation details
            from ..cli.display import display_single_evaluation_result

            display_single_evaluation_result(
                evaluation_type="performance",
                agent_identifier=str(self.agent),
                input_text=str(input_text),
                result=result,
                show_details=True,
                show_performance=True,
            )

        return result

    async def _measure_single_run(self, input_text: str) -> PerformanceMetrics:
        """Measure performance for a single run."""
        # Start memory tracking
        if self.track_memory:
            tracemalloc.start()
            start_memory = tracemalloc.get_traced_memory()[0]

        # Measure latency
        start_time = time.time()
        result = await self._run_agent(input_text)
        end_time = time.time()

        latency_ms = (end_time - start_time) * 1000

        # Measure memory
        memory_mb = 0.0
        if self.track_memory:
            current_memory = tracemalloc.get_traced_memory()[0]
            memory_mb = (current_memory - start_memory) / 1024 / 1024
            tracemalloc.stop()

        # Extract token metrics if available
        tokens_per_second = None
        time_to_first_token_ms = None

        if self.track_tokens and isinstance(result, dict):
            # Look for token metrics in response
            if "tokens_per_second" in result:
                tokens_per_second = result["tokens_per_second"]
            if "time_to_first_token_ms" in result:
                time_to_first_token_ms = result["time_to_first_token_ms"]

        return PerformanceMetrics(
            latency_ms=latency_ms,
            memory_mb=memory_mb,
            tokens_per_second=tokens_per_second,
            time_to_first_token_ms=time_to_first_token_ms,
        )

    def _calculate_statistics(self, metrics: list[PerformanceMetrics]) -> EvalResult:
        """Calculate statistics from collected metrics."""
        # Calculate latency stats
        latencies = [m.latency_ms for m in metrics]
        latency_stats = {
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "std_dev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)]
            if len(latencies) > 1
            else latencies[0],
        }

        # Calculate memory stats
        memory_stats = {}
        if self.track_memory:
            memories = [m.memory_mb for m in metrics]
            memory_stats = {"mean_mb": statistics.mean(memories), "max_mb": max(memories)}

        # Calculate token stats
        token_stats = {}
        if self.track_tokens:
            tps_values = [m.tokens_per_second for m in metrics if m.tokens_per_second]
            ttft_values = [m.time_to_first_token_ms for m in metrics if m.time_to_first_token_ms]

            if tps_values:
                token_stats["tokens_per_second"] = {
                    "mean": statistics.mean(tps_values),
                    "median": statistics.median(tps_values),
                }

            if ttft_values:
                token_stats["time_to_first_token_ms"] = {
                    "mean": statistics.mean(ttft_values),
                    "median": statistics.median(ttft_values),
                }

        # Determine pass/fail based on latency threshold
        # Default: pass if p95 latency < 2 seconds
        passed = latency_stats["p95_ms"] < 2000

        # Calculate a performance score (0-1)
        # Based on latency targets: <500ms = 1.0, >2000ms = 0.0
        if latency_stats["mean_ms"] <= 500:
            score = 1.0
        elif latency_stats["mean_ms"] >= 2000:
            score = 0.0
        else:
            score = 1.0 - (latency_stats["mean_ms"] - 500) / 1500

        return EvalResult(
            name=self.name,
            passed=passed,
            score=score,
            details={
                "iterations": self.num_iterations * len(metrics) // self.num_iterations,
                "latency": latency_stats,
                "memory": memory_stats,
                "tokens": token_stats,
                "feedback": self._generate_feedback(latency_stats, memory_stats),
            },
            metadata={
                "warmup_runs": self.warmup_runs,
                "track_memory": self.track_memory,
                "track_tokens": self.track_tokens,
            },
        )

    def _generate_feedback(
        self, latency_stats: dict[str, float], memory_stats: dict[str, float]
    ) -> str:
        """Generate performance feedback."""
        feedback = []

        # Latency feedback
        mean_latency = latency_stats["mean_ms"]
        if mean_latency < 200:
            feedback.append("Excellent response time (<200ms)")
        elif mean_latency < 500:
            feedback.append("Good response time (<500ms)")
        elif mean_latency < 1000:
            feedback.append("Acceptable response time (<1s)")
        else:
            feedback.append("Response time needs improvement (>1s)")

        # Consistency feedback
        if latency_stats["std_dev_ms"] > mean_latency * 0.5:
            feedback.append("High latency variance - consider optimizing for consistency")

        # Memory feedback
        if memory_stats and memory_stats.get("max_mb", 0) > 100:
            feedback.append(f"High memory usage: {memory_stats['max_mb']:.1f}MB")

        return " | ".join(feedback)


class PerfEval(PerformanceEval):
    """
    Alias for PerformanceEval to match Agno's naming.

    Provides an easier migration path from Agno.
    """

    pass
