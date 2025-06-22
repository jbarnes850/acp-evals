#!/usr/bin/env python3
"""
Example demonstrating error handling and helpful error messages in ACP Evals.
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from acp_evals import AccuracyEval
from acp_evals.core.exceptions import (
    AgentConnectionError,
    InvalidEvaluationInputError,
    ProviderNotConfiguredError,
)
from acp_evals.utils.logging import setup_logging

# Enable debug logging
setup_logging(level="DEBUG", log_llm_calls=True)


async def test_missing_api_key():
    """Test error when API key is missing."""
    print("\n=== Test: Missing API Key ===")

    # Temporarily remove API key
    original_key = os.environ.pop("OPENAI_API_KEY", None)

    try:
        # This should raise ProviderNotConfiguredError
        # AccuracyEval will try to create a provider internally
        # By removing the API key, it should fail
        AccuracyEval(
            agent=lambda x: f"Response to: {x}",
            judge_config={"provider": "openai"},  # Force OpenAI provider
        )
    except ProviderNotConfiguredError as e:
        print(f"✓ Got expected error: {e}")
        print(f"  Missing config: {e.details['missing_config']}")
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
    finally:
        # Restore API key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


async def test_invalid_model():
    """Test warning for invalid model name."""
    print("\n=== Test: Invalid Model Name ===")

    try:
        # This should log a warning but still work
        AccuracyEval(
            agent=lambda x: f"Response to: {x}",
            model="gpt-99-ultra",  # Invalid model
            mock_mode=True,  # Use mock to avoid API calls
        )
        print("✓ Created evaluator with invalid model (check logs for warning)")
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")


async def test_invalid_input():
    """Test validation of invalid inputs."""
    print("\n=== Test: Invalid Input Validation ===")

    # Mock mode is auto-detected when no provider is configured
    eval = AccuracyEval(
        agent=lambda x: f"Response to: {x}",
        judge_model="mock",  # This will trigger mock mode
    )

    # Test 1: Empty input
    try:
        await eval.run(
            input="",  # Empty input
            expected="Some response",
        )
    except InvalidEvaluationInputError as e:
        print(f"✓ Empty input rejected: {e}")

    # Test 2: Invalid expected type
    try:
        await eval.run(
            input="Valid input",
            expected=123,  # Should be string or dict
        )
    except InvalidEvaluationInputError as e:
        print(f"✓ Invalid expected type rejected: {e}")

    # Test 3: Invalid agent type
    try:
        eval = AccuracyEval(
            agent=123,  # Invalid agent type
            judge_model="mock",
        )
    except InvalidEvaluationInputError as e:
        print(f"✓ Invalid agent type rejected: {e}")


async def test_connection_error():
    """Test connection error handling."""
    print("\n=== Test: Connection Error ===")

    # Create evaluation with non-existent agent URL
    try:
        eval = AccuracyEval(
            agent="http://localhost:99999/agents/nonexistent",  # Wrong port
            judge_model="mock",  # Use mock judge to isolate agent connection error
        )

        await eval.run(input="Test input", expected="Test output")
    except AgentConnectionError as e:
        print(f"✓ Connection error handled: {e}")
        print(f"  Agent URL: {e.details['agent_url']}")


async def test_helpful_setup_instructions():
    """Test that setup instructions are helpful."""
    print("\n=== Test: Setup Instructions ===")

    from acp_evals.core.exceptions import format_provider_setup_help

    # Get setup help for each provider
    for provider in ["openai", "anthropic", "ollama"]:
        print(f"\nSetup help for {provider}:")
        help_text = format_provider_setup_help(provider)
        # Just print first few lines
        lines = help_text.strip().split("\n")
        for line in lines[:3]:
            print(f"  {line}")
        print("  ...")


async def test_cost_tracking():
    """Test cost tracking and warnings."""
    print("\n=== Test: Cost Tracking ===")

    from acp_evals.utils.logging import get_cost_tracker

    # Reset cost tracker
    tracker = get_cost_tracker()
    tracker.total_cost = 0.0
    tracker._warned = False

    # Set low warning threshold
    tracker.warning_threshold = 0.01

    # Simulate some costs
    tracker.add_cost(0.005, "openai", "gpt-4", 100)
    print("✓ Added first cost: $0.005")

    tracker.add_cost(0.008, "openai", "gpt-4", 150)
    print("✓ Added second cost: $0.008 (should trigger warning)")

    print(f"  {tracker.get_summary()}")


async def test_mock_fallback():
    """Test behavior when no API keys are available."""
    print("\n=== Test: No API Keys Available ===")

    # Remove all API keys
    keys_to_remove = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    original_keys = {}

    for key in keys_to_remove:
        original_keys[key] = os.environ.pop(key, None)

    try:
        # This should raise an error without API keys
        with pytest.raises(ProviderNotConfiguredError) as exc_info:
            eval = AccuracyEval(agent=lambda x: f"Response to: {x}")
            await eval.run(input="Test input", expected="Test output")

        print("✓ Correctly raised ProviderNotConfiguredError")
        print(f"  Error: {exc_info.value}")

    finally:
        # Restore keys
        for key, value in original_keys.items():
            if value:
                os.environ[key] = value


async def main():
    """Run all error handling tests."""
    print("ACP Evals Error Handling Examples")
    print("=" * 50)

    # Run tests
    await test_missing_api_key()
    await test_invalid_model()
    await test_invalid_input()
    await test_connection_error()
    await test_helpful_setup_instructions()
    await test_cost_tracking()
    await test_mock_fallback()

    print("\n" + "=" * 50)
    print("All error handling tests completed!")
    print("\nKey takeaways:")
    print("- Clear error messages with actionable suggestions")
    print("- Automatic validation of inputs")
    print("- Helpful setup instructions for each provider")
    print("- Cost tracking with configurable warnings")
    print("- Graceful fallback to mock mode when needed")


if __name__ == "__main__":
    asyncio.run(main())
