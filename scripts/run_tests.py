#!/usr/bin/env python3
"""
Test runner for ACP Evals.

This script runs all tests and provides a summary of results.
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run all tests with pytest."""
    print("Running ACP Evals Test Suite\n")

    # Get the project root directory
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(tests_dir),
        "-v",
        "--color=yes",
        "--tb=short",
        "--cov=acp_evals",
        "--cov-report=term-missing",
    ]

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(project_root))

    if result.returncode == 0:
        print("\nAll tests passed!")
        print("\nCoverage report displayed above")
    else:
        print("\nSome tests failed.")

    return result.returncode


def run_basic_validation():
    """Run basic validation of the simplified framework."""
    print("\n" + "=" * 60)
    print("Running Basic Framework Validation\n")

    project_root = Path(__file__).parent.parent

    try:
        # Try to import the simplified API
        import sys

        sys.path.insert(0, str(project_root / "src"))

        from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

        print("Core evaluators imported successfully")

        # Try to create evaluator instances with mock callable
        def mock_agent():
            return "Mock response"

        AccuracyEval(mock_agent)
        PerformanceEval(mock_agent)
        ReliabilityEval(mock_agent)
        print("Evaluator instances created successfully")

        print("Basic validation PASSED")
        return 0

    except Exception as e:
        print(f"Basic validation FAILED: {e}")
        return 1


def main():
    """Main test runner."""
    print("=" * 60)
    print("ACP EVALS TEST RUNNER")
    print("=" * 60)

    # Run tests
    test_result = run_tests()

    # Run basic validation
    validation_result = run_basic_validation()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if test_result == 0 and validation_result == 0:
        print("All tests and validation passed!")
        return 0
    else:
        if test_result != 0:
            print("Unit tests failed")
        if validation_result != 0:
            print("Basic validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
