"""
Base classes and data models for ACP evaluation framework.

This module provides the foundational abstractions for evaluation results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Union


@dataclass
class TokenUsage:
    """Token usage information for agent execution."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float = 0.0
    model: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "model": self.model,
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


@dataclass
class BenchmarkTask:
    """A benchmark task for evaluation."""

    id: str
    prompt: str
    expected_output: str | dict
    category: str = "general"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "expected_output": self.expected_output,
            "category": self.category,
            "metadata": self.metadata,
        }


@dataclass
class AgentInfo:
    """Information about an agent."""

    name: str
    url: str
    role: str
    capabilities: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "url": self.url,
            "role": self.role,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }
