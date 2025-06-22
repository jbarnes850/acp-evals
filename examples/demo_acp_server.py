#!/usr/bin/env python3
"""
Demo ACP server for acp-evals demonstration.
Provides multiple agents with different capabilities for comprehensive testing.
"""

import asyncio
import json
import logging
import random
import time
from typing import Any, Dict, List, Optional

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, Server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server()


@server.agent()
async def simple(input: List[Message], context: Context) -> List[Message]:
    """Simple echo agent for basic testing."""
    if not input:
        return [Message(parts=[MessagePart(content="No input received", content_type="text/plain")])]
    
    # Echo the last message
    last_message = input[-1]
    response = f"I received: {last_message.parts[0].content}"
    
    return [Message(parts=[MessagePart(content=response, content_type="text/plain")])]


@server.agent()
async def calculator(input: List[Message], context: Context) -> List[Message]:
    """Calculator agent that performs mathematical operations."""
    if not input:
        return [Message(parts=[MessagePart(content="Please provide a calculation", content_type="text/plain")])]
    
    query = input[-1].parts[0].content.lower()
    
    # Simulate processing
    await asyncio.sleep(0.1)
    
    # Handle specific calculations
    if "2+2" in query or "2 + 2" in query:
        result = "4"
    elif "25 * 4 + 10" in query:
        result = "110"
    elif "10*5" in query and "power of 2" in query:
        result = "2500"
    elif "15% of 200" in query:
        result = "30"
    elif "25% of 80" in query:
        result = "20"
    elif "compound interest" in query and "1000" in query and "5%" in query and "10 years" in query:
        result = "1628.89"
    elif "factorial" in query and "100" in query:
        # Simulate intensive calculation
        await asyncio.sleep(0.5)
        result = "93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000"
    elif "divide" in query and "zero" in query:
        # Test error handling
        result = "Error: Division by zero is undefined"
    else:
        try:
            # Try to evaluate simple expressions
            result = str(eval(query.replace("^", "**")))
        except:
            result = f"I can help with calculations. You asked about: {query}"
    
    return [Message(parts=[MessagePart(content=result, content_type="text/plain")])]


@server.agent()
async def research(input: List[Message], context: Context) -> List[Message]:
    """Research agent that simulates tool usage for information gathering."""
    if not input:
        return [Message(parts=[MessagePart(content="What would you like me to research?", content_type="text/plain")])]
    
    query = input[-1].parts[0].content.lower()
    
    # Simulate tool usage by returning structured responses
    # The reliability evaluator will look for tool names in the response
    tools_used = []
    
    if "search" in query or "latest" in query or "find" in query:
        tools_used.append("search")
        # Simulate search delay
        await asyncio.sleep(0.3)
    
    if "summarize" in query or "summary" in query:
        tools_used.append("summarize")
        await asyncio.sleep(0.2)
    
    # Generate responses based on query
    if "quantum computing" in query:
        response = (
            "Quantum computing uses quantum mechanics principles like superposition and entanglement "
            "to process information. Unlike classical bits (0 or 1), quantum bits (qubits) can exist "
            "in multiple states simultaneously, enabling parallel computation for certain problems. "
            "Key applications include cryptography, drug discovery, and optimization problems."
        )
    elif "renewable energy" in query:
        response = (
            "Renewable energy reduces carbon emissions and provides sustainable power through sources "
            "like solar, wind, hydro, and geothermal. Benefits include energy independence, job creation, "
            "reduced pollution, and long-term cost savings. Solar and wind are now cost-competitive with "
            "fossil fuels in many markets."
        )
    elif "machine learning" in query:
        response = (
            "Machine learning is a subset of AI that enables systems to learn from data without explicit "
            "programming. It includes supervised learning (labeled data), unsupervised learning (pattern "
            "discovery), and reinforcement learning (reward-based). Applications span from recommendation "
            "systems to autonomous vehicles."
        )
    elif "photosynthesis" in query:
        response = (
            "Photosynthesis is the process where plants convert light energy into chemical energy. "
            "Using chlorophyll, plants capture sunlight and combine CO2 and water to produce glucose "
            "and oxygen. This fundamental process sustains most life on Earth by producing oxygen and "
            "forming the base of food chains."
        )
    elif "dna" in query:
        response = (
            "DNA (deoxyribonucleic acid) stores genetic information in all living organisms. Its "
            "double helix structure contains four nucleotide bases (A, T, G, C) that encode instructions "
            "for building proteins. DNA replication ensures genetic information passes to new cells, "
            "while mutations drive evolution."
        )
    elif "gravity" in query:
        response = (
            "Gravity is the fundamental force that attracts objects with mass. Einstein's general "
            "relativity describes it as spacetime curvature caused by mass and energy. On Earth, "
            "gravity accelerates objects at 9.8 m/s². It governs planetary orbits, tides, and the "
            "structure of galaxies."
        )
    elif "ai news" in query or "latest ai" in query:
        response = (
            "Recent AI developments include advances in large language models, multimodal AI systems, "
            "AI-powered scientific discovery, and increased focus on AI safety and alignment. Major "
            "tech companies are integrating AI into consumer products while researchers explore "
            "AGI possibilities."
        )
    else:
        response = f"Based on my research about {query}: This is a complex topic requiring detailed analysis."
    
    # Include tool usage info in response for reliability detection
    if tools_used:
        response += f" (Tools used: {', '.join(tools_used)})"
    
    return [Message(parts=[MessagePart(content=response, content_type="text/plain")])]


@server.agent()
async def unreliable(input: List[Message], context: Context) -> List[Message]:
    """Unreliable agent for testing error handling and consistency."""
    if not input:
        return [Message(parts=[MessagePart(content="Error: No input", content_type="text/plain")])]
    
    query = input[-1].parts[0].content.lower()
    
    # Random failures for error testing
    if "error" in query or random.random() < 0.2:
        raise Exception("Simulated agent failure")
    
    # Random responses for consistency testing
    if "random" in query:
        responses = [
            "The answer is 42",
            "The answer is 17", 
            "The answer is 99",
            "Unable to compute"
        ]
        return [Message(parts=[MessagePart(content=random.choice(responses), content_type="text/plain")])]
    
    return [Message(parts=[MessagePart(content="Processed successfully", content_type="text/plain")])]


def main():
    """Run the demo ACP server."""
    logger.info("Starting Demo ACP Server...")
    logger.info("Server will be available at: http://localhost:8001")
    logger.info("\nAvailable agents:")
    logger.info("  - simple: Basic echo agent")
    logger.info("  - calculator: Mathematical calculations")
    logger.info("  - research: Information gathering with tool simulation")
    logger.info("  - unreliable: For testing error handling")
    logger.info("\nTest with:")
    logger.info("  acp-evals discover")
    logger.info("  acp-evals run accuracy http://localhost:8001/agents/calculator -i 'What is 25% of 80?' -e '20'")
    
    # Run server
    server.run(host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()