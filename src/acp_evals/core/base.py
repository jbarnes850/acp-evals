"""
Base classes and data models for ACP evaluation framework.

This module provides the foundational abstractions for evaluation results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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