"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    cost: Optional[float] = None
    raw_response: Optional[Any] = None


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize provider.
        
        Args:
            model: Model name to use
            api_key: API key (can be None if using env vars)
            **kwargs: Provider-specific configuration
        """
        self.model = model
        self.api_key = api_key
        self.config = kwargs
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Get completion from LLM.
        
        Args:
            prompt: The prompt to complete
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with completion
        """
        pass
    
    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """
        Calculate cost based on usage.
        
        Override in subclasses for provider-specific pricing.
        """
        return 0.0