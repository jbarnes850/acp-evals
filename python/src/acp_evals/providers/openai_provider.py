"""OpenAI provider implementation."""

import os
from typing import Dict, Optional

from .base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model to use (default: gpt-4)
            api_key: API key (uses OPENAI_API_KEY env var if not provided)
            api_base: API base URL (uses OPENAI_API_BASE env var if not provided)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        super().__init__(model, api_key, **kwargs)
        self.api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
        # Import here to avoid dependency if not using OpenAI
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise ImportError(
                "OpenAI provider requires 'openai' package. "
                "Install with: pip install openai"
            )
    
    @property
    def name(self) -> str:
        return "openai"
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Get completion from OpenAI."""
        try:
            # Configure client
            client = self.openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            
            # Make request
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Extract response
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
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
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
    
    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost based on OpenAI pricing."""
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