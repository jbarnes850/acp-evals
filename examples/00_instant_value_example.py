"""
Instant value example - evaluate an agent in 3 lines of code.

This example shows how to get started with ACP-Evals immediately,
without any configuration or setup beyond installing the package.
"""

from acp_evals import AccuracyEval, evaluate

# Example 1: Minimal evaluation - just 3 lines
eval = AccuracyEval("http://localhost:8000/agents/my-agent")
result = evaluate(eval, input="What is 2+2?", expected="4")
print(f"Score: {result.score}")

# Example 2: Even simpler with namespace
from acp_evals import evaluate as ev

result = ev.accuracy(
    agent="http://localhost:8000/agents/my-agent",
    input="What is the capital of France?",
    expected="Paris"
)

# Example 3: Test any function
def my_agent(message):
    """Simple function that acts as an agent."""
    if "capital" in message.lower() and "france" in message.lower():
        return "Paris"
    return "I don't know"

result = ev.accuracy(
    agent=my_agent,
    input="What is the capital of France?", 
    expected="Paris"
)

# Example 4: Quick test suite
from acp_evals import test_agent

results = test_agent("http://localhost:8000/agents/my-agent")
for eval_type, result in results.items():
    print(f"{eval_type}: {result.score:.2f}")

# Example 5: Progressive complexity with options
from acp_evals import AccuracyEval, EvalOptions

options = EvalOptions(
    rubric="code_quality",  # Use different evaluation criteria
    threshold=0.9,          # Higher pass threshold
    binary_mode=True        # Pass/fail instead of score
)

eval = AccuracyEval("http://localhost:8000/agents/my-agent", options)
result = evaluate(
    eval,
    input="Write a function to calculate factorial",
    expected="A working factorial implementation"
)