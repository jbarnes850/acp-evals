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
    print("🧪 Running ACP Evals Test Suite\n")
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(script_dir / "tests"),
        "-v",
        "--color=yes",
        "--tb=short",
        "--cov=acp_evals",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed.")
    
    return result.returncode


def run_validation():
    """Run implementation validation."""
    print("\n" + "="*60)
    print("🔍 Running Implementation Validation\n")
    
    script_dir = Path(__file__).parent
    cmd = [sys.executable, str(script_dir / "validate.py")]
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner."""
    print("="*60)
    print("ACP EVALS TEST RUNNER")
    print("="*60)
    
    # Run tests
    test_result = run_tests()
    
    # Run validation
    validation_result = run_validation()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if test_result == 0 and validation_result == 0:
        print("✅ All tests and validation passed!")
        return 0
    else:
        if test_result != 0:
            print("❌ Unit tests failed")
        if validation_result != 0:
            print("❌ Implementation validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())