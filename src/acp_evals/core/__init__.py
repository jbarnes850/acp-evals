"""
Core functionality for ACP-Evals.

Base classes, exceptions, validation, and configuration.
"""

from acp_evals.core.base import (
    MetricResult,
    TokenUsage,
)
from acp_evals.core.config import (
    check_provider_setup,
    get_provider_config,
)
from acp_evals.core.exceptions import (
    AgentAPIError,
    AgentConnectionError,
    AgentTimeoutError,
    ConfigurationError,
    EvaluationError,
    ProviderAPIError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
    ValidationError,
)
from acp_evals.core.validation import (
    InputValidator,
)

__all__ = [
    # Base classes
    "MetricResult",
    "TokenUsage",
    # Exceptions
    "EvaluationError",
    "ConfigurationError",
    "ProviderError",
    "ValidationError",
    "ProviderTimeoutError",
    "ProviderConnectionError",
    "ProviderAPIError",
    "AgentTimeoutError",
    "AgentConnectionError",
    "AgentAPIError",
    # Validation
    "InputValidator",
    # Config
    "get_provider_config",
    "check_provider_setup",
]
