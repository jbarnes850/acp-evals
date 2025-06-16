"""OpenAI provider implementation."""

import logging
import os

from ..core.exceptions import (
    ProviderAPIError,
    ProviderConnectionError,
    ProviderNotConfiguredError,
    ProviderRateLimitError,
    format_provider_setup_help,
)
from .base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    # Pricing per 1K tokens (as of June 2025)
    PRICING = {
        # June 2025 Models
        "gpt-4.1": {"input": 0.01, "output": 0.03},
        "gpt-4.1-nano": {"input": 0.005, "output": 0.015},
        "o3": {"input": 0.015, "output": 0.075},
        "o3-mini": {"input": 0.003, "output": 0.015},
        "o4-mini": {"input": 0.002, "output": 0.010},
    }

    def __init__(
        self,
        model: str = "gpt-4.1",
        api_key: str | None = None,
        api_base: str | None = None,
        **kwargs,
    ):
        """
        Initialize OpenAI provider.

        Args:
            model: Model to use (default: gpt-4.1)
            api_key: API key (uses OPENAI_API_KEY env var if not provided)
            api_base: API base URL (uses OPENAI_API_BASE env var if not provided)
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Initialize parent class (will call validate_config)
        super().__init__(model, api_key, **kwargs)
        self.api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

        # Import OpenAI library
        self._import_openai()

    @property
    def name(self) -> str:
        return "openai"

    async def complete(
        self, prompt: str, temperature: float = 0.0, max_tokens: int = 1000, **kwargs
    ) -> LLMResponse:
        """Get completion from OpenAI."""
        try:
            # Configure client
            client = self.openai.AsyncOpenAI(api_key=self.api_key, base_url=self.api_base)

            # Make request
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Extract response
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            # Calculate cost
            cost = self.calculate_cost(usage)

            return LLMResponse(
                content=content, model=response.model, usage=usage, cost=cost, raw_response=response
            )

        except self.openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit hit: {str(e)}")
            # Extract retry after if available
            retry_after = getattr(e, "retry_after", None)
            raise ProviderRateLimitError("openai", retry_after) from e

        except self.openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            status_code = getattr(e, "status_code", None)
            raise ProviderAPIError("openai", status_code, str(e)) from e

        except self.openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {str(e)}")
            raise ProviderConnectionError("openai", e) from e

        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {str(e)}")
            # Re-raise with more context
            raise ProviderAPIError("openai", error_message=str(e)) from e

    def calculate_cost(self, usage: dict[str, int]) -> float:
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

    def validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.api_key:
            missing = []
            if not os.getenv("OPENAI_API_KEY"):
                missing.append("OPENAI_API_KEY")

            raise ProviderNotConfiguredError("openai", missing_config=missing)

        # Validate model name
        valid_models = [
            "gpt-4.1",
            "gpt-4.1-nano",
            "o3",
            "o3-mini",
            "o4-mini",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ]
        if not any(model in self.model for model in valid_models):
            logger.warning(
                f"Model '{self.model}' may not be valid. Expected one of: {', '.join(valid_models)}"
            )

    def _import_openai(self) -> None:
        """Import OpenAI library with helpful error message."""
        try:
            import openai

            self.openai = openai
        except ImportError:
            raise ImportError(
                "OpenAI provider requires 'openai' package.\n"
                "Install with: pip install 'acp-evals[openai]' or pip install openai"
            )

    @classmethod
    def get_required_env_vars(cls) -> list[str]:
        """Get required environment variables."""
        return ["OPENAI_API_KEY"]

    def get_setup_instructions(self) -> str:
        """Get setup instructions for this provider."""
        return format_provider_setup_help("openai")
