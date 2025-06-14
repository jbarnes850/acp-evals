"""
Simple accuracy evaluation example.

This demonstrates how to evaluate an agent's accuracy with minimal code.
"""

import asyncio
import os
from acp_evals import AccuracyEval, evaluate


async def example_agent(input_text: str) -> str:
    """A simple example agent that answers questions."""
    responses = {
        "What is the capital of France?": "Paris is the capital of France.",
        "What is 2+2?": "2+2 equals 4.",
        "Explain quantum computing": "Quantum computing uses quantum mechanics principles like superposition and entanglement to process information in ways classical computers cannot.",
    }
    return responses.get(input_text, "I don't know the answer to that question.")


async def main():
    print("=== ACP Evals Simple Accuracy Example ===\n")
    
    # Example 1: Evaluate a callable agent
    print("1. Testing with a callable agent:")
    eval1 = AccuracyEval(
        agent=example_agent,
        rubric="factual",  # Use built-in factual rubric
        pass_threshold=0.8
    )
    
    result1 = await eval1.run(
        input="What is the capital of France?",
        expected="Paris",
        print_results=True
    )
    
    # Example 2: Batch evaluation
    print("\n2. Running batch evaluation:")
    test_cases = [
        {
            "input": "What is the capital of France?",
            "expected": "Paris is the capital of France.",
        },
        {
            "input": "What is 2+2?",
            "expected": "4",
        },
        {
            "input": "Explain quantum computing",
            "expected": {
                "keywords": ["quantum", "superposition", "entanglement"],
                "min_length": 50
            },
        },
    ]
    
    batch_result = await eval1.run_batch(
        test_cases=test_cases,
        parallel=True,
        print_results=True,
        export="accuracy_results.json"
    )
    
    # Example 3: Using synchronous evaluate function
    print("\n3. Using synchronous evaluate:")
    result3 = evaluate(
        eval1,
        input="What is 2+2?",
        expected="The answer is 4",
        print_results=True
    )
    
    # Example 4: Custom rubric for research quality
    print("\n4. Testing with research quality rubric:")
    eval2 = AccuracyEval(
        agent=example_agent,
        rubric="research_quality",
        pass_threshold=0.7
    )
    
    result4 = await eval2.run(
        input="Explain quantum computing",
        expected="A comprehensive explanation covering quantum mechanics principles, qubits, superposition, entanglement, and potential applications",
        context={"expected_depth": "intermediate", "target_audience": "technical"},
        print_results=True
    )
    
    print("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    # Note: Set up proper OpenAI/Anthropic/Ollama credentials in your .env file
    # This example uses a callable agent function
    asyncio.run(main())