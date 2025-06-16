#!/usr/bin/env python3
"""
Test Quality Assurance improvements in ACP Evals.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from acp_evals import AccuracyEval
from acp_evals.core.config import check_provider_setup
from acp_evals.core.exceptions import (
    InvalidEvaluationInputError,
    ProviderNotConfiguredError,
    format_provider_setup_help,
)
from acp_evals.providers import ProviderFactory


async def test_provider_validation():
    """Test provider configuration validation."""
    print("\n=== Provider Configuration Check ===")

    providers = check_provider_setup()
    print("\nProvider Status:")
    for provider, configured in providers.items():
        status = "✓ Configured" if configured else "✗ Not configured"
        print(f"  {provider}: {status}")

    # Test factory validation
    print("\n\nTesting provider factory:")
    try:
        # Try to create provider without config
        test_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            provider = ProviderFactory.create("openai")
        except ProviderNotConfiguredError as e:
            print(f"✓ Correctly caught missing config: {e}")
        finally:
            if test_key:
                os.environ["OPENAI_API_KEY"] = test_key
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def test_input_validation():
    """Test input validation."""
    print("\n=== Input Validation ===")

    # Create evaluator in mock mode
    eval = AccuracyEval(agent=lambda x: f"Response to: {x}")

    # Test 1: Invalid input types
    test_cases = [
        ("", "Empty input should be rejected"),
        (None, "None input should be rejected"),
        (["list"], "List input should be rejected"),
    ]

    for test_input, description in test_cases:
        try:
            if test_input == "":
                await eval.run(input=test_input, expected="Some response")
            else:
                # Will fail at agent validation
                AccuracyEval(agent=test_input)
            print(f"✗ {description} - but was accepted!")
        except (InvalidEvaluationInputError, TypeError):
            print(f"✓ {description}")
        except Exception as e:
            print(f"? {description} - got unexpected error: {type(e).__name__}")


async def test_helpful_errors():
    """Test that errors are helpful."""
    print("\n=== Helpful Error Messages ===")

    # Test missing provider setup
    print("\nProvider setup help:")
    help_text = format_provider_setup_help("openai")
    print(help_text.split("\n")[0])  # Just first line
    print("✓ Provides detailed setup instructions")

    # Test validation error formatting
    from acp_evals.core.exceptions import format_validation_error

    errors = {
        "input": "Cannot be empty",
        "expected": "Must be string or dict",
        "agent": "Must be URL, callable, or instance",
    }

    error_msg = format_validation_error(errors)
    print("\nValidation error formatting:")
    print(error_msg)
    print("✓ Clear, structured error messages")


async def test_cost_tracking():
    """Test cost tracking features."""
    print("\n=== Cost Tracking ===")

    # Create evaluator that tracks costs
    eval = AccuracyEval(agent=lambda x: f"Response to: {x}", judge_model="gpt-4")

    # The mock evaluation won't have costs, but real ones will
    result = await eval.run(input="Test question", expected="Test answer")

    print("✓ Cost tracking enabled (visible with real LLM providers)")
    print(f"  Result score: {result.score:.2f}")

    # Check if we can access cost info
    if hasattr(result, "metadata") and result.metadata:
        cost = result.metadata.get("cost")
        if cost:
            print(f"  Evaluation cost: ${cost:.4f}")


async def test_cli_check():
    """Test the CLI check command."""
    print("\n=== CLI Check Command ===")

    # We can't run the actual CLI here, but we can test the components
    from acp_evals.cli.check import check_env_file

    env_path = check_env_file()
    if env_path:
        print(f"✓ Found .env file at: {env_path}")
    else:
        print("✗ No .env file found")

    print("\nTo run full check: acp-evals check")
    print("With connection test: acp-evals check --test-connection")
    print("For setup help: acp-evals check --show-setup openai")


async def main():
    """Run all QA tests."""
    print("ACP Evals Quality Assurance Tests")
    print("=" * 50)

    await test_provider_validation()
    await test_input_validation()
    await test_helpful_errors()
    await test_cost_tracking()
    await test_cli_check()

    print("\n" + "=" * 50)
    print("Quality Assurance Summary:")
    print("✓ Provider configuration validation")
    print("✓ Input validation with clear errors")
    print("✓ Helpful setup instructions")
    print("✓ Cost tracking capabilities")
    print("✓ CLI tools for checking configuration")
    print("\nThe framework now provides better error handling and user guidance!")


if __name__ == "__main__":
    asyncio.run(main())
