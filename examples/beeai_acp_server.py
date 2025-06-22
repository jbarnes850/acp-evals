#!/usr/bin/env python3
"""
BeeAI Agent with ACP Server Example

This example demonstrates how to create and run a BeeAI agent
that's accessible via the ACP protocol, perfect for testing with acp-evals.

Requirements:
- pip install beeai-framework ollama
- ollama pull granite3.3:8b
"""

import asyncio
import logging
import sys
from typing import Any

# Check if BeeAI framework is installed
try:
    from beeai_framework.adapters.acp import ACPServer, ACPServerConfig
    from beeai_framework.agents import ToolCallingAgent
    from beeai_framework.agents.types import AgentMeta
    from beeai_framework.backend import ChatModel
    from beeai_framework.memory import UnconstrainedMemory
    from beeai_framework.tools import tool
    from beeai_framework.tools.types import StringToolOutput
except ImportError:
    print("Error: BeeAI framework is not installed.")
    print("Please install it with: pip install beeai-framework")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define some custom tools
@tool
def calculate(expression: str) -> StringToolOutput:
    """
    Calculate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2")

    Returns:
        The result of the calculation
    """
    try:
        # Safe evaluation of mathematical expressions
        result = eval(expression, {"__builtins__": {}}, {})
        return StringToolOutput(result=f"The result of {expression} is {result}")
    except Exception as e:
        return StringToolOutput(result=f"Error calculating {expression}: {str(e)}")


@tool
def get_weather(location: str) -> StringToolOutput:
    """
    Get weather information for a location (mock implementation).

    Args:
        location: The location to get weather for

    Returns:
        Weather information for the location
    """
    # Mock weather data
    weather_data = {
        "Paris": "Sunny, 22°C, light breeze",
        "London": "Cloudy, 18°C, chance of rain",
        "New York": "Clear, 25°C, humid",
        "Tokyo": "Rainy, 20°C, heavy precipitation",
    }

    weather = weather_data.get(location, f"Weather data not available for {location}")
    return StringToolOutput(result=f"Weather in {location}: {weather}")


@tool
def search(query: str) -> StringToolOutput:
    """
    Search for information (mock implementation).

    Args:
        query: The search query

    Returns:
        Search results
    """
    # Mock search results
    results = {
        "capital of France": "The capital of France is Paris, known for the Eiffel Tower and Louvre Museum.",
        "largest planet": "Jupiter is the largest planet in our solar system, with a diameter of about 142,984 km.",
        "Python programming": "Python is a high-level, interpreted programming language known for its simplicity.",
        "BeeAI framework": "BeeAI is a framework for building production-ready AI agents in Python and TypeScript.",
    }

    # Simple keyword matching
    for key, value in results.items():
        if key.lower() in query.lower():
            return StringToolOutput(result=value)

    return StringToolOutput(
        result=f"No specific results found for '{query}'. This is a mock search implementation."
    )


def create_agent() -> ToolCallingAgent:
    """Create a BeeAI agent with tools."""
    # Initialize the LLM
    llm = ChatModel.from_name("ollama:granite3.3:8b")

    # Create the agent with tools
    agent = ToolCallingAgent(
        llm=llm,
        tools=[calculate, get_weather, search],
        memory=UnconstrainedMemory(),
        meta=AgentMeta(
            name="demo_agent",
            description="A demonstration agent with calculation, weather, and search capabilities",
            tools=["calculate", "get_weather", "search"],
        ),
    )

    return agent


def main():
    """Run the ACP server with the BeeAI agent."""
    logger.info("Starting BeeAI ACP Server...")

    # Create the agent
    agent = create_agent()

    # Create and configure the ACP server
    server = ACPServer(config=ACPServerConfig(port=8001, host="127.0.0.1"))

    # Register the agent
    server.register(agent, name="demo_agent", tags=["demo", "testing", "acp-evals"])

    logger.info("ACP Server running on http://127.0.0.1:8001")
    logger.info("Agent 'demo_agent' is available at: http://127.0.0.1:8001/agents/demo_agent")
    logger.info("\nYou can now test this agent with acp-evals!")
    logger.info(
        "Example: acp-evals run accuracy http://127.0.0.1:8001/agents/demo_agent -i 'What is 15 + 27?' -e '42'"
    )

    # Start serving
    server.serve()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)
