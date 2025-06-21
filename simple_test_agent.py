#!/usr/bin/env python3
"""
Simple Test Agent for End-to-End Validation.

This is a minimal ACP-compatible agent that doesn't require BeeAI framework,
useful for testing the enhanced ACP-Evals features.
"""

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server
import asyncio
import re

server = Server()

@server.agent()
async def test_agent(input: list[Message], context) -> Message:
    """Main test agent with various capabilities."""
    # Extract text from ACP message
    input_text = ""
    for msg in input:
        for part in msg.parts:
            if part.content:
                input_text += part.content
    
    input_lower = input_text.lower()
    
    # Math operations
    if "2+2" in input_text or "2 + 2" in input_text:
        response = "4"
    elif "10*5" in input_text or "10 * 5" in input_text:
        response = "50"
    elif re.search(r'what is (\d+)\s*\+\s*(\d+)', input_lower):
        match = re.search(r'what is (\d+)\s*\+\s*(\d+)', input_lower)
        num1, num2 = int(match.group(1)), int(match.group(2))
        response = str(num1 + num2)
    
    # Knowledge questions
    elif "capital of france" in input_lower:
        response = "Paris"
    elif "capital of" in input_lower:
        if "japan" in input_lower:
            response = "Tokyo"
        elif "uk" in input_lower or "united kingdom" in input_lower:
            response = "London"
        else:
            response = "I'm not sure about that capital city."
    
    # Greetings
    elif any(greeting in input_lower for greeting in ["hello", "hi", "hey"]):
        response = "Hello! How can I help you today?"
    elif "how are you" in input_lower:
        response = "I'm doing well, thank you! How can I assist you?"
    
    # Default
    else:
        response = f"I received your message: '{input_text}'. How can I help you with that?"
    
    # Simulate some processing time
    await asyncio.sleep(0.1)
    
    return Message(
        parts=[MessagePart(
            content=response,
            content_type="text/plain"
        )]
    )

@server.agent()
async def calculator(input: list[Message], context) -> Message:
    """Simple calculator agent for accuracy tests."""
    input_text = input[0].parts[0].content
    
    # Basic math operations
    if "2+2" in input_text:
        answer = "4"
    elif "10*5" in input_text:
        answer = "50"
    elif "100/4" in input_text:
        answer = "25"
    elif "7-3" in input_text:
        answer = "4"
    else:
        # Try to extract and calculate
        import re
        pattern = r'(\d+)\s*([\+\-\*\/])\s*(\d+)'
        match = re.search(pattern, input_text)
        if match:
            num1 = int(match.group(1))
            op = match.group(2)
            num2 = int(match.group(3))
            
            if op == '+':
                answer = str(num1 + num2)
            elif op == '-':
                answer = str(num1 - num2)
            elif op == '*':
                answer = str(num1 * num2)
            elif op == '/':
                answer = str(num1 // num2) if num2 != 0 else "Cannot divide by zero"
        else:
            answer = "I can only handle basic arithmetic operations"
    
    return Message(
        parts=[MessagePart(
            content=answer,
            content_type="text/plain"
        )]
    )

@server.agent()
async def greeter(input: list[Message], context) -> Message:
    """Friendly greeter for performance tests."""
    input_text = input[0].parts[0].content.lower()
    
    greetings = {
        "hello": "Hello there! How can I brighten your day?",
        "hi": "Hi! It's great to hear from you!",
        "hey": "Hey! What's on your mind today?",
        "good morning": "Good morning! I hope you're having a wonderful start to your day!",
        "good afternoon": "Good afternoon! How's your day going so far?",
        "good evening": "Good evening! I hope you've had a productive day!"
    }
    
    for greeting, response in greetings.items():
        if greeting in input_text:
            return Message(
                parts=[MessagePart(
                    content=response,
                    content_type="text/plain"
                )]
            )
    
    # Default friendly response
    return Message(
        parts=[MessagePart(
            content="Hello! I'm here to help. Feel free to ask me anything!",
            content_type="text/plain"
        )]
    )

@server.agent()
async def safety_agent(input: list[Message], context) -> Message:
    """Agent for safety evaluation tests."""
    input_text = input[0].parts[0].content.lower()
    
    # Check for harmful content
    harmful_patterns = [
        "how to hack",
        "create malware",
        "exploit vulnerability",
        "steal data",
        "harm someone",
        "illegal activities"
    ]
    
    if any(pattern in input_text for pattern in harmful_patterns):
        response = "I cannot provide assistance with potentially harmful or illegal activities. I'm here to help with constructive and positive tasks."
    elif "jailbreak" in input_text:
        response = "I'm designed to be helpful, harmless, and honest. I cannot assist with attempts to bypass my safety guidelines."
    else:
        response = "I'm here to help with safe and constructive requests. What would you like to know?"
    
    return Message(
        parts=[MessagePart(
            content=response,
            content_type="text/plain"
        )]
    )

@server.agent()
async def echo(input: list[Message], context) -> Message:
    """Simple echo agent for basic tests."""
    # Echo back the input
    return input[0]

if __name__ == "__main__":
    print("Starting Simple Test Agents on http://localhost:8000")
    print("\nAvailable agents:")
    print("  - test_agent: General purpose agent")
    print("  - calculator: Math operations")
    print("  - greeter: Friendly responses")
    print("  - safety_agent: Safety testing")
    print("  - echo: Echoes input")
    print("\nReady for testing!")
    print("Press Ctrl+C to stop")
    
    server.run(host="0.0.0.0", port=8000)