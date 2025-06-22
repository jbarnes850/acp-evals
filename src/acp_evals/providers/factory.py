"""LLM provider factory."""

import os

from .anthropic_provider import AnthropicProvider
from .base import LLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


class ProviderFactory:
    """Factory for creating LLM providers."""

    # Registry of available providers
    PROVIDERS: dict[str, type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    @classmethod
    def create(cls, provider: str | None = None, **kwargs) -> LLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider: Provider name (uses EVALUATION_PROVIDER env var if not provided)
            **kwargs: Provider-specific configuration

        Returns:
            LLMProvider instance

        Raises:
            ValueError: If provider is unknown or configuration is missing
        """
        # Determine provider
        provider = provider or os.getenv("EVALUATION_PROVIDER", "openai")

        if provider not in cls.PROVIDERS:
            available = ", ".join(cls.PROVIDERS.keys())
            raise ValueError(f"Unknown provider: {provider}. Available providers: {available}")

        # Get provider class
        provider_class = cls.PROVIDERS[provider]

        # Create instance with environment defaults
        try:
            return provider_class(**kwargs)
        except ValueError as e:
            # Add helpful context
            raise ValueError(
                f"Failed to initialize {provider} provider. {str(e)}\n"
                f"Check your .env file or pass required parameters."
            ) from e

    @classmethod
    def detect_available_providers(cls) -> dict[str, bool]:
        """
        Detect which providers have valid configuration.

        Returns:
            Dict mapping provider names to availability
        """
        available = {}

        # Check OpenAI
        available["openai"] = bool(os.getenv("OPENAI_API_KEY"))

        # Check Anthropic
        available["anthropic"] = bool(os.getenv("ANTHROPIC_API_KEY"))

        # Check Ollama (always available if running)
        available["ollama"] = True  # Will fail on connection if not running

        return available

    @classmethod
    def get_default_provider(cls) -> str | None:
        """
        Get the default provider based on available configuration.

        Returns:
            Provider name or None if no providers configured
        """
        # Check explicit setting first
        if os.getenv("EVALUATION_PROVIDER"):
            return os.getenv("EVALUATION_PROVIDER")

        # Auto-detect based on available API keys
        available = cls.detect_available_providers()

        # Priority order
        priority = ["openai", "anthropic", "ollama"]

        for provider in priority:
            if available.get(provider, False):
                return provider

        return None

    @classmethod
    def get_provider(cls, provider: str | None = None, **kwargs) -> LLMProvider:
        """
        Get a provider instance (alias for create method).

        Args:
            provider: Provider name (uses EVALUATION_PROVIDER env var if not provided)
            **kwargs: Provider-specific configuration

        Returns:
            LLMProvider instance
        """
        return cls.create(provider, **kwargs)
