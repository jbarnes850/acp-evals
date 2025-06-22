#!/usr/bin/env python3
"""
Simple validation script for ACP Evals simplified framework.

This script validates the basic functionality of the 3 core evaluators.
"""

import asyncio
import sys
from pathlib import Path


class SimpleACPAgent:
    """Mock ACP agent for testing purposes."""

    def __init__(self, name="test-agent"):
        self.name = name
        self.call_count = 0

    async def run(self, input_text: str, **kwargs) -> str:
        """Mock agent response."""
        self.call_count += 1
        return f"Mock response to: {input_text[:50]}..."


async def validate_accuracy_eval():
    """Test AccuracyEval functionality."""
    print("Testing AccuracyEval...")

    try:
        from acp_evals import AccuracyEval

        # Test with mock agent
        agent = SimpleACPAgent()
        eval = AccuracyEval(agent=agent, name="Accuracy Test")

        result = await eval.run(input="What is 2+2?", expected="4")

        if result and hasattr(result, "score"):
            print("  AccuracyEval: PASS")
            return True
        else:
            print("  AccuracyEval: FAIL - Invalid result format")
            return False

    except Exception as e:
        print(f"  AccuracyEval: FAIL - {e}")
        return False


async def validate_performance_eval():
    """Test PerformanceEval functionality."""
    print("Testing PerformanceEval...")

    try:
        from acp_evals import PerformanceEval

        # Test with mock agent
        agent = SimpleACPAgent()
        eval = PerformanceEval(agent=agent, name="Performance Test")

        result = await eval.run(input_text="Test performance")

        if result and hasattr(result, "details"):
            print("  PerformanceEval: PASS")
            return True
        else:
            print("  PerformanceEval: FAIL - Invalid result format")
            return False

    except Exception as e:
        print(f"  PerformanceEval: FAIL - {e}")
        return False


async def validate_reliability_eval():
    """Test ReliabilityEval functionality."""
    print("Testing ReliabilityEval...")

    try:
        from acp_evals import ReliabilityEval

        # Test with mock agent
        agent = SimpleACPAgent()
        eval = ReliabilityEval(agent=agent, name="Reliability Test")

        result = await eval.run(input="Test reliability")

        if result and hasattr(result, "score"):
            print("  ReliabilityEval: PASS")
            return True
        else:
            print("  ReliabilityEval: FAIL - Invalid result format")
            return False

    except Exception as e:
        print(f"  ReliabilityEval: FAIL - {e}")
        return False


def validate_imports():
    """Test that all core imports work."""
    print("Testing core imports...")

    try:
        from acp_evals import (
            AccuracyEval,
            EvalResult,
            MetricResult,
            PerformanceEval,
            ReliabilityEval,
            TokenUsage,
        )

        print("  Core imports: PASS")
        return True

    except Exception as e:
        print(f"  Core imports: FAIL - {e}")
        return False


async def main():
    """Run validation tests."""
    print("=" * 50)
    print("ACP EVALS SIMPLIFIED FRAMEWORK VALIDATION")
    print("=" * 50)

    # Add src to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))

    # Run validation tests
    results = []

    # Test imports
    results.append(validate_imports())

    # Test evaluators
    results.append(await validate_accuracy_eval())
    results.append(await validate_performance_eval())
    results.append(await validate_reliability_eval())

    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("Validation: PASSED")
        return 0
    else:
        print("Validation: FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
