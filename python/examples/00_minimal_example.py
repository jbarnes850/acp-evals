"""
ACP Evals Quickstart - Zero to Eval in 5 Lines

This demonstrates the simplest way to evaluate an ACP agent.
"""

import asyncio
from acp_evals import AccuracyEval, evaluate

# Example 1: Evaluate any function as an agent (5 lines)
async def my_agent(question: str) -> str:
    """Your agent that answers questions."""
    if "capital of France" in question:
        return "Paris is the capital of France."
    return "I don't know."

# That's it! Now evaluate:
result = evaluate(
    AccuracyEval(agent=my_agent),
    input="What is the capital of France?", 
    expected="Paris",
    print_results=True
)

# Example 2: Evaluate an ACP agent by URL
eval = AccuracyEval(agent="http://localhost:8000/agents/my-agent")
result = asyncio.run(eval.run(
    input="What is 2+2?",
    expected="4",
    print_results=True
))

# Example 3: Batch evaluation with test data
test_cases = [
    {"input": "What is 2+2?", "expected": "4"},
    {"input": "What is the capital of France?", "expected": "Paris"},
]

batch_result = asyncio.run(eval.run_batch(
    test_cases=test_cases,
    print_results=True
))

print(f"\nPass rate: {batch_result.pass_rate}%")