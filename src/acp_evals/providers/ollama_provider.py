"""Ollama provider implementation for local LLMs."""

import logging
import os

import httpx

from ..core.exceptions import ProviderAPIError, ProviderConnectionError, format_provider_setup_help
from .base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference."""

    def __init__(self, model: str = "qwen3:30b-a3b", base_url: str | None = None, **kwargs):
        """
        Initialize Ollama provider.

        Args:
            model: Model to use (default: qwen3:30b-a3b)
            base_url: Ollama API URL (uses OLLAMA_BASE_URL env var if not provided)
        """
        super().__init__(model, api_key=None, **kwargs)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    @property
    def name(self) -> str:
        return "ollama"

    async def complete(
        self, prompt: str, temperature: float = 0.0, max_tokens: int = 1000, **kwargs
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
                    "stream": False,
                }

                # Make request
                response = await client.post(
                    f"{self.base_url}/api/generate", json=payload, timeout=60.0
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
                    "total_tokens": len(prompt.split()) * 1.3 + estimated_tokens,
                }

                return LLMResponse(
                    content=content,
                    model=self.model,
                    usage=usage,
                    cost=0.0,  # Local inference has no API cost
                    raw_response=data,
                )

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise ProviderConnectionError(
                "ollama",
                Exception(
                    f"Cannot connect to {self.base_url}. Make sure Ollama is running (ollama serve)."
                ),
            ) from e

        except httpx.TimeoutException as e:
            logger.error("Ollama request timed out")
            raise ProviderAPIError(
                "ollama",
                error_message="Request timed out. The model may be loading or the response is taking too long.",
            ) from e

        except Exception as e:
            logger.error(f"Unexpected Ollama error: {str(e)}")
            raise ProviderAPIError("ollama", error_message=str(e)) from e

    def validate_config(self) -> None:
        """Validate Ollama configuration."""
        # Ollama doesn't require API keys, just check URL format
        if not self.base_url:
            logger.warning("No Ollama base URL configured, using default: http://localhost:11434")

    @classmethod
    def get_required_env_vars(cls) -> list[str]:
        """Get required environment variables."""
        # Ollama doesn't require any env vars, but can use OLLAMA_BASE_URL
        return []

    def get_setup_instructions(self) -> str:
        """Get setup instructions for this provider."""
        return format_provider_setup_help("ollama")

    async def check_connection(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
