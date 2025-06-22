"""
Accuracy Evaluation Example

This example demonstrates how to evaluate a simple Q&A agent for accuracy.
It shows ACP Evals' beautiful terminal output and simple API.

Run:
    python accuracy_eval.py
"""

import asyncio

from acp_evals import AccuracyEval, EvalResult


# Simple mock agent for demonstration
async def python_qa_agent(prompt: str) -> str:
    """Simple agent that answers Python programming questions."""
    # In production, this would make an API call to your actual agent
    responses = {
        "What is a Python list?": "A Python list is an ordered, mutable collection that can hold items of different types.",
        "How do you define a function in Python?": "You define a function using the 'def' keyword followed by the function name and parameters.",
        "What is list comprehension?": "List comprehension is a concise way to create lists using a single line of code with syntax: [expression for item in iterable].",
        "What is the difference between a tuple and a list?": "Tuples are immutable and use parentheses (), while lists are mutable and use square brackets [].",
        "How do you import a module?": "You import a module using the 'import' statement, like 'import math' or 'from math import sqrt'.",
    }
    return responses.get(prompt, "I don't know the answer to that question.")


async def main():
    """Run accuracy evaluations."""
    print("\n🎯 Running Accuracy Evaluation Example\n")
    print("This example evaluates a simple Python Q&A agent for accuracy.")
    print("Watch how ACP Evals displays beautiful, informative results!\n")

    # Create evaluator (in production, use your agent URL)
    evaluator = AccuracyEval(python_qa_agent)

    # Define test cases
    test_cases = [
        ("What is a Python list?", "ordered collection that can hold different types"),
        ("How do you define a function in Python?", "def keyword"),
        ("What is list comprehension?", "concise way to create lists"),
        ("What is the difference between a tuple and a list?", "immutable"),
        ("How do you import a module?", "import statement"),
    ]

    # Run evaluations
    results = []
    passed = 0

    for prompt, expected in test_cases:
        print(f"\n📝 Testing: {prompt}")
        result = await evaluator.run(prompt, expected)
        results.append(result)

        if result.passed:
            print(f"✅ PASSED (score: {result.score:.2f})")
            passed += 1
        else:
            print(f"❌ FAILED (score: {result.score:.2f})")
            print(f"   Expected keywords: {expected}")
            if result.metadata and "response" in result.metadata:
                print(f"   Got: {result.metadata['response'][:100]}...")

        if result.details and "feedback" in result.details:
            print(f"   Feedback: {result.details['feedback']}")

    # Summary
    accuracy = passed / len(test_cases)
    print("\n✨ Evaluation Complete!")
    print(f"   Accuracy: {accuracy:.1%}")
    print(f"   Total Cases: {len(test_cases)}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {len(test_cases) - passed}")


if __name__ == "__main__":
    asyncio.run(main())
