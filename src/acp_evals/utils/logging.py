"""Logging configuration for ACP Evals."""

import logging
import os
import sys


def setup_logging(
    level: str | None = None, log_file: str | None = None, log_llm_calls: bool = False
) -> None:
    """
    Configure logging for ACP Evals.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
        log_llm_calls: Whether to log LLM API calls
    """
    # Get level from parameter or environment
    level = level or os.getenv("LOG_LEVEL", "INFO")
    log_llm_calls = log_llm_calls or os.getenv("LOG_LLM_CALLS", "false").lower() == "true"

    # Configure basic logging
    handlers = []

    # Console handler with custom formatter
    console_handler = logging.StreamHandler(sys.stderr)

    # Different formatters based on log level
    if level == "DEBUG":
        # Include timestamp and module name in debug mode
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s", datefmt="%H:%M:%S"
        )
    elif level == "INFO":
        # Verbose mode - include module name
        console_formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    else:
        # Default/Quiet mode - minimal output
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")

    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File handler if specified
    if log_file or os.getenv("LOG_FILE"):
        log_file = log_file or os.getenv("LOG_FILE")
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=getattr(logging, level.upper()), handlers=handlers)

    # Configure specific loggers
    if log_llm_calls:
        # Enable debug logging for provider modules
        logging.getLogger("acp_evals.providers").setLevel(logging.DEBUG)
        logging.getLogger("acp_evals.evaluators.llm_judge").setLevel(logging.DEBUG)
    else:
        # Reduce noise from HTTP libraries
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("anthropic").setLevel(logging.WARNING)

    # Log startup info
    logger = logging.getLogger("acp_evals")
    logger.debug(
        f"Logging configured: level={level}, log_file={log_file}, log_llm_calls={log_llm_calls}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger
    """
    return logging.getLogger(name)


class CostTracker:
    """Track and log LLM API costs."""

    def __init__(self, warning_threshold: float | None = None):
        """
        Initialize cost tracker.

        Args:
            warning_threshold: Warn if total cost exceeds this (USD)
        """
        self.total_cost = 0.0
        self.warning_threshold = warning_threshold or float(
            os.getenv("COST_WARNING_THRESHOLD", "10.0")
        )
        self.logger = get_logger("acp_evals.costs")
        self._warned = False

    def add_cost(self, cost: float, provider: str, model: str, tokens: int) -> None:
        """
        Add a cost entry.

        Args:
            cost: Cost in USD
            provider: Provider name
            model: Model name
            tokens: Token count
        """
        self.total_cost += cost

        self.logger.debug(
            f"LLM call: provider={provider}, model={model}, "
            f"tokens={tokens}, cost=${cost:.4f}, total=${self.total_cost:.4f}"
        )

        # Check threshold
        if not self._warned and self.total_cost > self.warning_threshold:
            self.logger.warning(
                f"Total evaluation cost (${self.total_cost:.2f}) has exceeded "
                f"warning threshold (${self.warning_threshold:.2f})"
            )
            self._warned = True

    def get_summary(self) -> str:
        """Get cost summary."""
        return f"Total LLM costs: ${self.total_cost:.4f}"


# Global cost tracker instance
_cost_tracker: CostTracker | None = None


def get_cost_tracker() -> CostTracker:
    """Get or create the global cost tracker."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker
