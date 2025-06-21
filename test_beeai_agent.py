#!/usr/bin/env python3
"""
BeeAI Test Agent for End-to-End Validation.

This agent uses the BeeAI framework to create a real ACP-compatible agent
for testing the enhanced ACP-Evals features with live LLMs.
"""

from beeai_framework import Agent
from beeai_framework.tools import CalculatorTools
from beeai_framework.models.openai import OpenAIChat
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize BeeAI agent with OpenAI
bee_agent = Agent(
    name="TestAgent",
    model=OpenAIChat(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    ),
    tools=[CalculatorTools()],
    instructions=[
        "You are a helpful test agent for validating the ACP-Evals framework.",
        "Answer questions accurately and concisely.",
        "Use the calculator tool when needed for math operations.",
        "Be friendly but professional in your responses."
    ]
)

# Create ACP server
server = Server()

@server.agent()
async def test_agent(input: list[Message], context) -> Message:
    """ACP-compatible wrapper for BeeAI agent."""
    # Extract text from ACP message
    input_text = ""
    for msg in input:
        for part in msg.parts:
            if part.content:
                input_text += part.content + "\n"
    
    # Run BeeAI agent
    response = await bee_agent.arun(input_text.strip())
    
    # Convert response to ACP message
    return Message(
        parts=[MessagePart(
            content=response.content,
            content_type="text/plain"
        )]
    )

# Alternative simpler agents for specific test cases
@server.agent()
async def calculator(input: list[Message], context) -> Message:
    """Simple calculator agent for math tests."""
    input_text = input[0].parts[0].content.lower()
    
    # Basic calculator logic
    if "2+2" in input_text or "2 + 2" in input_text:
        answer = "4"
    elif "10*5" in input_text or "10 * 5" in input_text:
        answer = "50"
    elif "capital of france" in input_text:
        answer = "Paris"
    else:
        # Fall back to BeeAI agent for complex calculations
        response = await bee_agent.arun(input_text)
        answer = response.content
    
    return Message(
        parts=[MessagePart(
            content=answer,
            content_type="text/plain"
        )]
    )

@server.agent() 
async def greeter(input: list[Message], context) -> Message:
    """Friendly greeter agent for performance tests."""
    input_text = input[0].parts[0].content.lower()
    
    if "hello" in input_text or "hi" in input_text:
        response = "Hello! I'm here to help. How are you doing today?"
    elif "how are you" in input_text:
        response = "I'm doing great, thank you for asking! How can I assist you?"
    else:
        response = "I'm a friendly assistant. Feel free to say hello or ask me anything!"
    
    return Message(
        parts=[MessagePart(
            content=response,
            content_type="text/plain"
        )]
    )

@server.agent()
async def safety_tester(input: list[Message], context) -> Message:
    """Agent for testing safety evaluations."""
    input_text = input[0].parts[0].content.lower()
    
    # Refuse harmful requests
    harmful_keywords = ["hack", "exploit", "attack", "steal", "harm"]
    if any(keyword in input_text for keyword in harmful_keywords):
        response = "I cannot and will not provide assistance with harmful or malicious activities."
    else:
        response = "I'm here to help with safe and constructive tasks. What would you like to know?"
    
    return Message(
        parts=[MessagePart(
            content=response,
            content_type="text/plain"
        )]
    )

if __name__ == "__main__":
    print("Starting BeeAI test agents on http://localhost:8000")
    print("\nAvailable agents:")
    print("  - test_agent: Full-featured agent with tool use")
    print("  - calculator: Simple math agent") 
    print("  - greeter: Friendly greeting agent")
    print("  - safety_tester: Safety evaluation agent")
    print("\nPress Ctrl+C to stop")
    
    server.run(host="0.0.0.0", port=8000)