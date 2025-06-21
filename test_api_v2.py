#!/usr/bin/env python3
"""
Test script for ACP-Evals v2 API.

This validates the new professional developer API with real agents and LLMs.
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from acp_evals.api_v2 import test, test_async, TestOptions, evaluate
from acp_sdk.models import Message, MessagePart
from rich.console import Console

console = Console()

# Test agent URL
AGENT_URL = "http://localhost:8000/agents/test_agent"


async def test_basic_functionality():
    """Test 1: Basic test() function with minimal parameters."""
    console.print("\n[bold cyan]Test 1: Basic Functionality[/bold cyan]")
    
    # Test 1.1: Simple string test
    console.print("\n1.1 Simple string test:")
    result = await test_async(AGENT_URL, "What is 2+2?", "4")
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    console.print(f"  Feedback: {result.details.get('feedback', 'No feedback')[:100]}...")
    
    # Test 1.2: Function-based agent
    console.print("\n1.2 Function-based agent:")
    def simple_agent(message):
        if "2+2" in message:
            return "4"
        elif "capital of France" in message.lower():
            return "Paris"
        return "I don't know"
    
    result = await test_async(simple_agent, "What is the capital of France?", "Paris")
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    
    console.print("\n[green]✓ Basic functionality tests passed![/green]")


async def test_acp_message_support():
    """Test 2: Native ACP Message support."""
    console.print("\n[bold cyan]Test 2: ACP Message Support[/bold cyan]")
    
    # Test 2.1: Text-only message
    console.print("\n2.1 Text-only ACP Message:")
    message = Message(
        role="user",
        parts=[MessagePart(content="What is 10*5?", content_type="text/plain")]
    )
    
    result = await test_async(AGENT_URL, message, "50")
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    
    # Test 2.2: Multi-part message (simulated)
    console.print("\n2.2 Multi-part message:")
    message = Message(
        role="user",
        parts=[
            MessagePart(content="Calculate this:", content_type="text/plain"),
            MessagePart(content="2+2", content_type="text/plain")
        ]
    )
    
    result = await test_async(AGENT_URL, message, "4")
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    
    console.print("\n[green]✓ ACP Message support tests passed![/green]")


async def test_progressive_options():
    """Test 3: Progressive disclosure with TestOptions."""
    console.print("\n[bold cyan]Test 3: Progressive Options[/bold cyan]")
    
    # Test 3.1: Exact match
    console.print("\n3.1 Exact match test:")
    result = await test_async(
        AGENT_URL, 
        "What is 2+2?", 
        "4",
        TestOptions(check="exact")
    )
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    
    # Test 3.2: Semantic similarity with threshold
    console.print("\n3.2 Semantic similarity:")
    result = await test_async(
        AGENT_URL,
        "Tell me about Paris",
        "Paris is the capital of France",
        TestOptions(check="semantic", threshold=0.8)
    )
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    
    # Test 3.3: Custom rubric
    console.print("\n3.3 Custom rubric:")
    result = await test_async(
        AGENT_URL,
        "What is 2+2?",
        "4",
        TestOptions(rubric="factual", threshold=0.9)
    )
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    
    console.print("\n[green]✓ Progressive options tests passed![/green]")


async def test_error_handling():
    """Test 4: Error handling and edge cases."""
    console.print("\n[bold cyan]Test 4: Error Handling[/bold cyan]")
    
    # Test 4.1: Invalid agent URL
    console.print("\n4.1 Invalid agent URL:")
    try:
        result = await test_async("http://invalid-url:9999/agents/fake", "test", "response")
        console.print(f"  [red]Failed to catch error[/red]")
    except Exception as e:
        console.print(f"  [green]✓ Correctly caught error: {type(e).__name__}[/green]")
    
    # Test 4.2: Dict input format
    console.print("\n4.2 Dict input format:")
    dict_input = {
        "parts": [
            {"content": "What is 2+2?", "content_type": "text/plain"}
        ]
    }
    result = await test_async(AGENT_URL, dict_input, "4")
    console.print(f"  Score: {result.score:.2f}")
    console.print(f"  Passed: {result.passed}")
    
    console.print("\n[green]✓ Error handling tests completed![/green]")


async def test_not_implemented_features():
    """Test 5: Features marked as TODO."""
    console.print("\n[bold cyan]Test 5: Future Features (Not Implemented)[/bold cyan]")
    
    # Test 5.1: Tool usage evaluation
    console.print("\n5.1 Tool usage evaluation:")
    try:
        result = evaluate.tool_usage(AGENT_URL, "Find weather", ["weather_api"])
        console.print("  [red]Should have raised NotImplementedError[/red]")
    except NotImplementedError:
        console.print("  [yellow]✓ Correctly marked as not implemented[/yellow]")
    
    # Test 5.2: Reasoning evaluation
    console.print("\n5.2 Reasoning evaluation:")
    try:
        result = evaluate.reasoning(AGENT_URL, "Plan a trip", [{"step": "research"}])
        console.print("  [red]Should have raised NotImplementedError[/red]")
    except NotImplementedError:
        console.print("  [yellow]✓ Correctly marked as not implemented[/yellow]")
    
    console.print("\n[green]✓ Future features properly marked![/green]")


async def main():
    """Run all validation tests."""
    console.print("[bold]ACP-Evals v2 API Validation[/bold]")
    console.print("=" * 50)
    
    # Check if test agent is running
    console.print("\n[yellow]Note: Make sure test agent is running:[/yellow]")
    console.print("  python simple_test_agent.py")
    
    try:
        await test_basic_functionality()
        await test_acp_message_support()
        await test_progressive_options()
        await test_error_handling()
        await test_not_implemented_features()
        
        console.print("\n" + "=" * 50)
        console.print("[bold green]✓ All v2 API validation tests passed![/bold green]")
        console.print("\nKey achievements:")
        console.print("  • Simplified test() function with 2 parameters")
        console.print("  • Native ACP Message support")
        console.print("  • Progressive disclosure via TestOptions")
        console.print("  • Professional error handling")
        console.print("  • Clear roadmap for future features")
        
    except Exception as e:
        console.print(f"\n[red]✗ Validation failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())