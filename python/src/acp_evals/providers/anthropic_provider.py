"""Anthropic provider implementation."""

import os
from typing import Dict, Optional

from .base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Anthropic API provider."""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }
    
    def __init__(
        self,
        model: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            model: Model to use (default: claude-3-opus-20240229)
            api_key: API key (uses ANTHROPIC_API_KEY env var if not provided)
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        super().__init__(model, api_key, **kwargs)
        
        # Import here to avoid dependency if not using Anthropic
        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError:
            raise ImportError(
                "Anthropic provider requires 'anthropic' package. "
                "Install with: pip install anthropic"
            )
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Get completion from Anthropic."""
        try:
            # Configure client
            client = self.anthropic.AsyncAnthropic(api_key=self.api_key)
            
            # Make request
            response = await client.messages.create(
                model=self.model,
                system="You are an expert evaluator.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Extract response
            content = response.content[0].text
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            # Calculate cost
            cost = self.calculate_cost(usage)
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                cost=cost,
                raw_response=response
            )
            
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Anthropic API error: {str(e)}") from e
    
    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost based on Anthropic pricing."""
        model_key = None
        for key in self.PRICING:
            if key in self.model:
                model_key = key
                break
        
        if not model_key:
            return 0.0
        
        pricing = self.PRICING[model_key]
        input_cost = (usage.get("prompt_tokens", 0) / 1000) * pricing["input"]
        output_cost = (usage.get("completion_tokens", 0) / 1000) * pricing["output"]
        
        return input_cost + output_cost