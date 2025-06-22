#!/usr/bin/env python3
"""
Simple test agent for comprehensive evaluation demonstration.
"""

import random
import time


def calculator_agent(input_text: str) -> str:
    """
    A calculator agent that performs mathematical operations.

    Args:
        input_text: Mathematical expression or query

    Returns:
        str: The result of the calculation
    """
    time.sleep(0.05)  # Simulate fast processing

    input_lower = input_text.lower()

    # Handle specific calculations
    if "25% of 80" in input_lower or "25 percent of 80" in input_lower:
        return "20"
    elif "15% of 200" in input_lower:
        return "30"
    elif "compound interest" in input_lower and "1000" in input_lower:
        return "1628.89"
    elif "factorial" in input_lower and "5" in input_lower:
        return "120"
    else:
        # Try to extract numbers and operations
        try:
            # Simple evaluation for basic math
            result = eval(input_text.replace("^", "**"), {"__builtins__": {}}, {})
            return str(result)
        except Exception:
            return f"I can help you calculate: {input_text}"


def research_agent(input_text: str) -> str:
    """
    A research agent that simulates using search and summarize tools.

    Args:
        input_text: Research query

    Returns:
        str: Research results with tool usage indicators
    """
    time.sleep(0.2)  # Simulate research time

    input_lower = input_text.lower()
    tools_used = []

    # Detect tool usage
    if "search" in input_lower or "find" in input_lower or "latest" in input_lower:
        tools_used.append("search")
    if "summarize" in input_lower or "summary" in input_lower:
        tools_used.append("summarize")

    # Generate response
    if "ai news" in input_lower:
        response = (
            "Recent AI developments include advances in large language models, "
            "multimodal AI systems, and increased focus on AI safety."
        )
    elif "quantum computing" in input_lower:
        response = (
            "Quantum computing leverages quantum mechanical phenomena like "
            "superposition and entanglement for computational advantage."
        )
    else:
        response = f"Research findings for '{input_text}': This topic requires detailed analysis."

    # Add tool usage indicators for reliability detection
    if tools_used:
        response += f" [Tools used: {', '.join(tools_used)}]"

    return response


def smart_agent(input_text: str) -> str:
    """
    A smart agent that can answer questions and provides realistic responses.

    Args:
        input_text: The user's question or request

    Returns:
        str: The agent's response
    """
    # Simulate processing time
    time.sleep(0.1)

    input_lower = input_text.lower()

    # Handle capital city questions
    if "capital" in input_lower and "france" in input_lower:
        return (
            "Paris is the capital of France. It's home to famous landmarks including "
            "the Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, Arc de Triomphe, "
            "Champs-Élysées, and Sacré-Cœur Basilica. The city is known for its rich "
            "history, art, culture, and cuisine."
        )

    # Handle math questions
    elif "2+2" in input_text or "2 + 2" in input_text:
        return "4"

    # Handle what is questions
    elif input_lower.startswith("what is"):
        topic = input_text[8:].strip()
        if "machine learning" in topic.lower():
            return (
                "Machine learning is a subset of artificial intelligence that enables "
                "computers to learn and make decisions from data without being explicitly "
                "programmed for every task. The three primary approaches are: "
                "(1) Supervised Learning - algorithms learn from labeled training data, "
                "(2) Unsupervised Learning - algorithms find patterns in unlabeled data, "
                "(3) Reinforcement Learning - agents learn through trial and error with rewards."
            )
        else:
            return f"I can provide information about {topic}. Could you be more specific about what aspect interests you?"

    # Handle prime number questions
    elif "prime" in input_lower and "11" in input_text:
        return (
            "Yes, 11 is a prime number because it has no positive divisors other than 1 and itself."
        )

    # Handle code generation requests
    elif "python function" in input_lower and "prime" in input_lower:
        return """def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True"""

    # Handle general questions
    elif "hello" in input_lower or "hi" in input_lower:
        return "Hello! How can I help you today?"

    # Handle search-related queries
    elif "search" in input_lower or "find" in input_lower:
        return f"I would search for information about: {input_text}"

    # Default response for other queries
    else:
        return f"I understand you're asking about: {input_text}. Let me provide a helpful response based on my knowledge."


if __name__ == "__main__":
    # Test the agent
    test_inputs = [
        "What is the capital of France?",
        "What is 2+2?",
        "What is machine learning?",
        "Is 11 a prime number?",
    ]

    for test_input in test_inputs:
        print(f"Input: {test_input}")
        print(f"Output: {smart_agent(test_input)}")
        print()
