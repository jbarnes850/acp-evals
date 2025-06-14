"""Ollama provider implementation for local LLMs."""

import os
import json
from typing import Dict, Optional
import httpx

from .base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference."""
    
    def __init__(
        self,
        model: str = "llama2",
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Ollama provider.
        
        Args:
            model: Model to use (default: llama2)
            base_url: Ollama API URL (uses OLLAMA_BASE_URL env var if not provided)
        """
        super().__init__(model, api_key=None, **kwargs)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    @property
    def name(self) -> str:
        return "ollama"
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Get completion from Ollama."""
        try:
            async with httpx.AsyncClient() as client:
                # Prepare request
                payload = {
                    "model": self.model,
                    "prompt": f"You are an expert evaluator.\n\n{prompt}",
                    "temperature": temperature,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                    "stream": False
                }
                
                # Make request
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Ollama API error: {response.status_code} - {response.text}"
                    )
                
                # Parse response
                data = response.json()
                content = data.get("response", "")
                
                # Ollama doesn't provide token counts in the same way
                # Estimate based on response length
                estimated_tokens = len(content.split()) * 1.3
                usage = {
                    "prompt_tokens": len(prompt.split()) * 1.3,
                    "completion_tokens": estimated_tokens,
                    "total_tokens": len(prompt.split()) * 1.3 + estimated_tokens
                }
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    usage=usage,
                    cost=0.0,  # Local inference has no API cost
                    raw_response=data
                )
                
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running (ollama serve)."
            )
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}") from e