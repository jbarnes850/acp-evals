"""
Base evaluator classes for ACP agent evaluation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class EvaluationResult:
    """Result of an evaluation."""
    score: float  # 0.0 to 1.0
    passed: bool
    breakdown: Dict[str, float]
    feedback: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Evaluator(ABC):
    """Base class for all evaluators."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the evaluator."""
        pass
    
    @abstractmethod
    async def evaluate(
        self,
        task: str,
        response: str,
        reference: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """
        Evaluate an agent response.
        
        Args:
            task: The task/prompt given to the agent
            response: The agent's response
            reference: Optional reference answer
            context: Optional additional context
            
        Returns:
            EvaluationResult with score and breakdown
        """
        pass