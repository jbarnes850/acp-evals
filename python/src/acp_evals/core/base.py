"""
Base classes and data models for ACP evaluation framework.

This module provides the foundational abstractions for metrics, benchmarks,
and evaluation results.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from acp_sdk import Event, Run
from pydantic import BaseModel


@dataclass
class TokenUsage:
    """Detailed token usage information for agent execution."""

    input_tokens: int
    output_tokens: int
    tool_tokens: int
    total_tokens: int
    cost_usd: float
    model: str
    context_percentage: float  # How full was the context window?
    agent_breakdown: dict[str, dict[str, int]] = field(default_factory=dict)  # For multi-agent

    @property
    def efficiency_score(self) -> float:
        """Calculate tokens per unit of value (lower is better)."""
        if self.total_tokens == 0:
            return 0.0
        return 1.0 / self.total_tokens

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "tool_tokens": self.tool_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "model": self.model,
            "context_percentage": self.context_percentage,
            "agent_breakdown": self.agent_breakdown,
            "efficiency_score": self.efficiency_score,
        }


@dataclass
class MetricResult:
    """Result from a metric calculation."""

    name: str
    value: float
    unit: str
    breakdown: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name}: {self.value:.2f} {self.unit}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "breakdown": self.breakdown,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_otel_attributes(self) -> dict[str, Any]:
        """Convert metric result to OpenTelemetry attributes."""
        attributes = {
            "metric.name": self.name,
            "metric.value": self.value,
            "metric.unit": self.unit,
            "metric.timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

        # Add breakdown values as attributes
        if self.breakdown:
            for key, value in self.breakdown.items():
                if isinstance(value, int | float | str | bool):
                    attributes[f"metric.breakdown.{key}"] = value
                elif isinstance(value, dict):
                    # Flatten nested dicts one level
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, int | float | str | bool):
                            attributes[f"metric.breakdown.{key}.{sub_key}"] = sub_value

        return attributes


class Metric(ABC):
    """Abstract base class for all metrics."""

    @abstractmethod
    async def calculate(self, run: Run, events: list[Event]) -> MetricResult:
        """
        Calculate the metric based on a run and its events.

        Args:
            run: The ACP run to evaluate
            events: List of events from the run

        Returns:
            MetricResult with calculated value and breakdown
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this metric."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this metric measures."""
        pass


@dataclass
class BenchmarkTask:
    """A single task within a benchmark."""

    id: str
    prompt: str
    expected_output: str | list[str] | dict[str, Any] | None = None
    context: str | None = None
    category: str | None = None
    difficulty: str | None = None  # easy, medium, hard
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_context(self, additional_context: str) -> "BenchmarkTask":
        """Create a new task with additional context prepended."""
        new_context = f"{additional_context}\n\n{self.context}" if self.context else additional_context
        return BenchmarkTask(
            id=self.id,
            prompt=self.prompt,
            expected_output=self.expected_output,
            context=new_context,
            category=self.category,
            difficulty=self.difficulty,
            metadata=self.metadata,
        )


@dataclass
class BenchmarkResult:
    """Result from running a benchmark."""

    benchmark_name: str
    agent_name: str
    tasks_completed: int
    tasks_total: int
    overall_score: float  # 0.0 to 1.0
    task_results: list[dict[str, Any]]
    metrics: dict[str, MetricResult]
    summary: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.tasks_total == 0:
            return 0.0
        return (self.tasks_completed / self.tasks_total) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "benchmark_name": self.benchmark_name,
            "agent_name": self.agent_name,
            "tasks_completed": self.tasks_completed,
            "tasks_total": self.tasks_total,
            "overall_score": self.overall_score,
            "success_rate": self.success_rate,
            "task_results": self.task_results,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "summary": self.summary,
            "timestamp": self.timestamp.isoformat(),
        }


class Benchmark(ABC):
    """Abstract base class for all benchmarks."""

    @abstractmethod
    async def evaluate(self, agent: Any, **kwargs) -> BenchmarkResult:
        """
        Run the benchmark against an agent.

        Args:
            agent: The agent to evaluate (can be ACP client, URL, or agent instance)
            **kwargs: Additional benchmark-specific parameters

        Returns:
            BenchmarkResult with scores and detailed results
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this benchmark."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this benchmark tests."""
        pass

    @property
    def categories(self) -> list[str]:
        """Categories this benchmark covers (e.g., reasoning, coding, etc.)."""
        return []


class Evaluator(ABC):
    """Abstract base class for output evaluators."""

    @abstractmethod
    async def evaluate(
        self,
        task: str,
        response: str,
        expected: Any | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Evaluate an agent's response.

        Args:
            task: The task or prompt given to the agent
            response: The agent's response
            expected: Expected output or criteria (optional)
            **kwargs: Additional evaluator-specific parameters

        Returns:
            Dictionary with evaluation results including scores and feedback
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this evaluator."""
        pass


class EvaluationRun(BaseModel):
    """Complete evaluation run with all results."""

    run_id: str
    agent_name: str
    benchmarks: list[BenchmarkResult]
    metrics: dict[str, MetricResult]
    metadata: dict[str, Any]
    timestamp: datetime

    @property
    def total_cost(self) -> float:
        """Calculate total cost across all benchmarks."""
        total = 0.0
        for metric in self.metrics.values():
            if metric.name == "token_usage" and metric.breakdown:
                total += metric.breakdown.get("cost_usd", 0.0)
        return total

    def summary_report(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"Evaluation Run: {self.run_id}",
            f"Agent: {self.agent_name}",
            f"Timestamp: {self.timestamp}",
            "",
            "Benchmark Results:",
        ]

        for benchmark in self.benchmarks:
            lines.append(f"  {benchmark.benchmark_name}: {benchmark.overall_score:.2%} ({benchmark.success_rate:.0f}% success rate)")

        lines.extend([
            "",
            "Key Metrics:",
        ])

        for metric in self.metrics.values():
            lines.append(f"  {metric}")

        if self.total_cost > 0:
            lines.extend([
                "",
                f"Total Cost: ${self.total_cost:.4f}",
            ])

        return "\n".join(lines)


# Import alias for compatibility
