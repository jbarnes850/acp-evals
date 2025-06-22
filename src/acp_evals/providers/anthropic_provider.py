"""Anthropic provider implementation."""

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


class AnthropicProvider(LLMProvider):
    """Anthropic API provider."""

    # Pricing per 1K tokens (as of June 2025)
    PRICING = {
        # June 2025 Models - Claude 4 series
        "claude-opus-4": {"input": 0.015, "output": 0.075},  # 32K output
        "claude-sonnet-4": {"input": 0.003, "output": 0.015},  # 64K output, SWE-bench 72.7%
        # Legacy models (still supported)
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }

    # Model mapping to actual API names
    MODEL_MAPPING = {
        "claude-4-opus": "claude-opus-4-20250514",
        "claude-opus-4": "claude-opus-4-20250514",
        "claude-4-sonnet": "claude-sonnet-4-20250514",
        "claude-sonnet-4": "claude-sonnet-4-20250514",
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
    }

    def __init__(self, model: str = "claude-4-sonnet", api_key: str | None = None, **kwargs):
        """
        Initialize Anthropic provider.

        Args:
            model: Model to use (default: claude-4-sonnet)
            api_key: API key (uses ANTHROPIC_API_KEY env var if not provided)
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # Initialize parent class (will call validate_config)
        super().__init__(model, api_key, **kwargs)

        # Import Anthropic library
        self._import_anthropic()

    @property
    def name(self) -> str:
        return "anthropic"

    async def complete(
        self, prompt: str, temperature: float = 0.0, max_tokens: int = 1000, **kwargs
    ) -> LLMResponse:
        """Get completion from Anthropic."""
        try:
            # Configure client
            client = self.anthropic.AsyncAnthropic(api_key=self.api_key)

            # Get actual model name from mapping
            actual_model = self.MODEL_MAPPING.get(self.model, self.model)

            # Make request
            response = await client.messages.create(
                model=actual_model,
                system="You are an expert evaluator.",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Extract response
            content = response.content[0].text
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            # Calculate cost
            cost = self.calculate_cost(usage)

            return LLMResponse(
                content=content, model=response.model, usage=usage, cost=cost, raw_response=response
            )

        except self.anthropic.RateLimitError as e:
            logger.warning(f"Anthropic rate limit hit: {str(e)}")
            # Extract retry after if available
            retry_after = getattr(e.response.headers, "retry-after", None)
            raise ProviderRateLimitError("anthropic", retry_after) from e

        except self.anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            status_code = getattr(e, "status_code", None)
            raise ProviderAPIError("anthropic", status_code, str(e)) from e

        except self.anthropic.APIConnectionError as e:
            logger.error(f"Anthropic connection error: {str(e)}")
            raise ProviderConnectionError("anthropic", e) from e

        except Exception as e:
            logger.error(f"Unexpected Anthropic error: {str(e)}")
            # Re-raise with more context
            raise ProviderAPIError("anthropic", error_message=str(e)) from e

    def calculate_cost(self, usage: dict[str, int]) -> float:
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

    def validate_config(self) -> None:
        """Validate Anthropic configuration."""
        if not self.api_key:
            missing = []
            if not os.getenv("ANTHROPIC_API_KEY"):
                missing.append("ANTHROPIC_API_KEY")

            raise ProviderNotConfiguredError("anthropic", missing_config=missing)

        # Validate model name
        valid_models = [
            "claude-4-opus",
            "claude-4-sonnet",
            "claude-opus-4",
            "claude-sonnet-4",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
        ]
        if not any(model in self.model for model in valid_models):
            logger.warning(
                f"Model '{self.model}' may not be valid. Expected one of: {', '.join(valid_models)}"
            )

    def _import_anthropic(self) -> None:
        """Import Anthropic library with helpful error message."""
        try:
            import anthropic

            self.anthropic = anthropic
        except ImportError:
            raise ImportError(
                "Anthropic provider requires 'anthropic' package.\n"
                "Install with: pip install 'acp-evals[anthropic]' or pip install anthropic"
            )

    @classmethod
    def get_required_env_vars(cls) -> list[str]:
        """Get required environment variables."""
        return ["ANTHROPIC_API_KEY"]

    def get_setup_instructions(self) -> str:
        """Get setup instructions for this provider."""
        return format_provider_setup_help("anthropic")
