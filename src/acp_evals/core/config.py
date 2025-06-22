"""Configuration management for ACP Evals."""

import os
from pathlib import Path

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv

    # Look for .env in current directory and parent directories
    current_dir = Path.cwd()
    env_file = None

    # Search up to 3 levels up for .env file
    for _ in range(4):
        potential_env = current_dir / ".env"
        if potential_env.exists():
            env_file = potential_env
            break
        current_dir = current_dir.parent

    if env_file:
        load_dotenv(env_file)
        print(f"Loaded configuration from {env_file}")
    else:
        # Try default location
        load_dotenv()

except ImportError:
    # python-dotenv not installed, skip
    pass


def get_provider_config() -> dict:
    """Get LLM provider configuration from environment."""
    config = {
        "provider": os.getenv("EVALUATION_PROVIDER"),
        "temperature": float(os.getenv("EVALUATION_TEMPERATURE", "0.0")),
        "max_tokens": int(os.getenv("EVALUATION_MAX_TOKENS", "1000")),
        "timeout": int(os.getenv("EVALUATION_TIMEOUT", "30")),
    }

    # Add provider-specific settings
    provider = config["provider"]

    if provider == "openai":
        config["model"] = os.getenv("OPENAI_MODEL", "gpt-4o")
        config["api_key"] = os.getenv("OPENAI_API_KEY")
        config["api_base"] = os.getenv("OPENAI_API_BASE")

    elif provider == "anthropic":
        config["model"] = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        config["api_key"] = os.getenv("ANTHROPIC_API_KEY")

    elif provider == "ollama":
        config["model"] = os.getenv("OLLAMA_MODEL", "qwen3:8b")
        config["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    return config


def check_provider_setup() -> dict:
    """Check which providers are properly configured."""
    providers = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "ollama": True,  # Always available if server is running
    }

    return providers


def get_available_providers() -> list[str]:
    """Get list of available and configured providers."""
    setup = check_provider_setup()
    return [provider for provider, available in setup.items() if available]
