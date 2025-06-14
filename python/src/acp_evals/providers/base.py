"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
import os


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
        
        # Validate configuration on initialization
        self.validate_config()
    
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
    
    def validate_config(self) -> None:
        """
        Validate provider configuration.
        
        Override in subclasses to add provider-specific validation.
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_required_env_vars(cls) -> List[str]:
        """
        Get list of required environment variables.
        
        Returns:
            List of environment variable names
        """
        pass
    
    @classmethod
    def check_env_vars(cls) -> Dict[str, bool]:
        """
        Check if required environment variables are set.
        
        Returns:
            Dict mapping env var names to whether they're set
        """
        required = cls.get_required_env_vars()
        return {var: bool(os.getenv(var)) for var in required}
    
    @classmethod
    def is_configured(cls) -> bool:
        """
        Check if provider is properly configured.
        
        Returns:
            True if all required env vars are set
        """
        check = cls.check_env_vars()
        return all(check.values())