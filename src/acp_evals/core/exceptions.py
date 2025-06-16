"""Custom exceptions for ACP Evals framework."""

from typing import Any


class ACPEvalsError(Exception):
    """Base exception for all ACP Evals errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


class ProviderError(ACPEvalsError):
    """Base exception for provider-related errors."""

    pass


class ProviderNotConfiguredError(ProviderError):
    """Raised when a provider is not properly configured."""

    def __init__(self, provider: str, missing_config: list | None = None):
        message = f"Provider '{provider}' is not properly configured."

        if missing_config:
            message += f" Missing: {', '.join(missing_config)}"

        details = {
            "provider": provider,
            "missing_config": missing_config or [],
        }

        super().__init__(message, details)


class ProviderConnectionError(ProviderError):
    """Raised when unable to connect to a provider."""

    def __init__(self, provider: str, original_error: Exception | None = None):
        message = f"Failed to connect to {provider} provider"

        if original_error:
            message += f": {str(original_error)}"

        details = {
            "provider": provider,
            "original_error": str(original_error) if original_error else None,
        }

        super().__init__(message, details)


class ProviderRateLimitError(ProviderError):
    """Raised when hitting rate limits."""

    def __init__(self, provider: str, retry_after: int | None = None):
        message = f"Rate limit exceeded for {provider} provider"

        if retry_after:
            message += f". Retry after {retry_after} seconds"

        details = {
            "provider": provider,
            "retry_after": retry_after,
        }

        super().__init__(message, details)


class ProviderAPIError(ProviderError):
    """Raised for API-specific errors."""

    def __init__(
        self, provider: str, status_code: int | None = None, error_message: str | None = None
    ):
        message = f"API error from {provider} provider"

        if status_code:
            message += f" (status {status_code})"

        if error_message:
            message += f": {error_message}"

        details = {
            "provider": provider,
            "status_code": status_code,
            "error_message": error_message,
        }

        super().__init__(message, details)


class ProviderTimeoutError(ProviderError):
    """Raised when provider request times out."""

    def __init__(self, provider: str, timeout_seconds: int):
        message = f"Provider '{provider}' request timed out after {timeout_seconds} seconds"
        details = {
            "provider": provider,
            "timeout_seconds": timeout_seconds,
        }
        super().__init__(message, details)


class EvaluationError(ACPEvalsError):
    """Base exception for evaluation errors."""

    pass


class InvalidEvaluationInputError(EvaluationError):
    """Raised when evaluation input is invalid."""

    def __init__(self, field: str, reason: str):
        message = f"Invalid evaluation input for '{field}': {reason}"
        details = {
            "field": field,
            "reason": reason,
        }
        super().__init__(message, details)


class EvaluationTimeoutError(EvaluationError):
    """Raised when evaluation times out."""

    def __init__(self, timeout_seconds: int):
        message = f"Evaluation timed out after {timeout_seconds} seconds"
        details = {
            "timeout_seconds": timeout_seconds,
        }
        super().__init__(message, details)


class ConfigurationError(ACPEvalsError):
    """Raised for configuration issues."""

    def __init__(self, message: str, suggestion: str | None = None):
        if suggestion:
            message += f"\n\nSuggestion: {suggestion}"

        details = {
            "suggestion": suggestion,
        }

        super().__init__(message, details)


class ValidationError(ACPEvalsError):
    """Raised for validation errors."""

    pass


class AgentError(ACPEvalsError):
    """Base exception for agent-related errors."""

    pass


class AgentConnectionError(AgentError):
    """Raised when unable to connect to an agent."""

    def __init__(self, agent_url: str, original_error: Exception | None = None):
        message = f"Failed to connect to agent at {agent_url}"

        if original_error:
            message += f": {str(original_error)}"

        details = {
            "agent_url": agent_url,
            "original_error": str(original_error) if original_error else None,
        }

        super().__init__(message, details)


class AgentTimeoutError(AgentError):
    """Raised when agent response times out."""

    def __init__(self, agent_url: str, timeout_seconds: int):
        message = f"Agent at {agent_url} timed out after {timeout_seconds} seconds"
        details = {
            "agent_url": agent_url,
            "timeout_seconds": timeout_seconds,
        }
        super().__init__(message, details)


class AgentAPIError(AgentError):
    """Raised for agent API-specific errors."""

    def __init__(
        self, agent_url: str, status_code: int | None = None, error_message: str | None = None
    ):
        message = f"API error from agent at {agent_url}"

        if status_code:
            message += f" (status {status_code})"

        if error_message:
            message += f": {error_message}"

        details = {
            "agent_url": agent_url,
            "status_code": status_code,
            "error_message": error_message,
        }

        super().__init__(message, details)


def format_provider_setup_help(provider: str) -> str:
    """Get helpful setup instructions for a provider."""

    setup_guides = {
        "openai": """
To set up OpenAI:
1. Sign up at https://platform.openai.com
2. Create an API key at https://platform.openai.com/api-keys
3. Set OPENAI_API_KEY in your .env file
4. (Optional) Set OPENAI_MODEL to your preferred model (default: gpt-4)

Example .env:
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
""",
        "anthropic": """
To set up Anthropic:
1. Sign up at https://console.anthropic.com
2. Create an API key in your account settings
3. Set ANTHROPIC_API_KEY in your .env file
4. (Optional) Set ANTHROPIC_MODEL to your preferred model

Example .env:
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229
""",
        "ollama": """
To set up Ollama:
1. Install Ollama from https://ollama.ai
2. Pull a model: ollama pull llama2
3. Start Ollama server (usually runs automatically)
4. (Optional) Set OLLAMA_BASE_URL if not using default localhost:11434

Example .env:
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
""",
    }

    return setup_guides.get(
        provider, f"Please refer to the documentation for setting up {provider}."
    )


def format_validation_error(errors: dict[str, str]) -> str:
    """Format validation errors into a helpful message."""

    if not errors:
        return ""

    message = "Validation errors found:\n"
    for field, error in errors.items():
        message += f"  - {field}: {error}\n"

    return message
