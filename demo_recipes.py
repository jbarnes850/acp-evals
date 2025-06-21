#!/usr/bin/env python3
"""
Demo script showcasing BeeAI evaluation recipes.

Shows how developers can test their agents with one line of code
for common patterns in the BeeAI/ACP ecosystem.
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from acp_evals import recipes
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# Test agent URL
AGENT_URL = "http://localhost:8000/agents/test_agent"


async def demo_customer_support():
    """Demo customer support agent evaluation."""
    console.print("\n[bold cyan]1. Customer Support Agent Testing[/bold cyan]")
    console.print("[dim]One-line evaluation for customer service agents[/dim]\n")
    
    # Show the code
    code = '''# Test escalation handling with one line
result = await recipes.customer_support.test_escalation(agent, severity="high")'''
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=False)
    console.print(syntax)
    console.print()
    
    # Run the test
    console.print("Running escalation test...")
    result = await recipes.customer_support.test_escalation(AGENT_URL, severity="high")
    
    # Show results
    console.print(f"✓ Score: {result.score:.0%}")
    console.print(f"✓ Passed: {result.passed}")
    console.print(f"✓ Feedback: {result.details.get('feedback', 'See details')}")
    
    # Show comprehensive suite option
    console.print("\n[dim]Or run a comprehensive suite:[/dim]")
    code2 = '''# Full customer support evaluation suite
results = await recipes.customer_support.comprehensive_suite(agent)'''
    
    syntax2 = Syntax(code2, "python", theme="monokai", line_numbers=False)
    console.print(syntax2)


async def demo_code_assistant():
    """Demo code assistant evaluation."""
    console.print("\n\n[bold cyan]2. Code Assistant Testing[/bold cyan]")
    console.print("[dim]Test debugging, code generation, and best practices[/dim]\n")
    
    # Show the code
    code = '''# Test debugging capabilities
result = await recipes.code_assistant.test_debugging(agent, difficulty="medium")

# Test code generation
result = await recipes.code_assistant.test_code_generation(agent, task_type="api")'''
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=False)
    console.print(syntax)
    console.print()
    
    # Run debugging test
    console.print("Running debugging test...")
    result = await recipes.code_assistant.test_debugging(AGENT_URL, difficulty="easy")
    
    console.print(f"✓ Debugging Score: {result.score:.0%}")
    console.print(f"✓ Identifies issues: {'Yes' if result.score > 0.5 else 'Needs improvement'}")


async def demo_research_agent():
    """Demo research agent evaluation."""
    console.print("\n\n[bold cyan]3. Research Agent Testing[/bold cyan]")
    console.print("[dim]Evaluate information gathering and synthesis[/dim]\n")
    
    # Show the code
    code = '''# Test information gathering
result = await recipes.research.test_information_gathering(
    agent, 
    topic_complexity="medium"
)

# Test fact-checking abilities
result = await recipes.research.test_fact_checking(agent)'''
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=False)
    console.print(syntax)
    console.print()
    
    # Run fact-checking test
    console.print("Running fact-checking test...")
    result = await recipes.research.test_fact_checking(AGENT_URL)
    
    console.print(f"✓ Fact-checking Score: {result.score:.0%}")
    console.print(f"✓ Accuracy: {'High' if result.score > 0.8 else 'Moderate'}")


async def demo_multi_agent():
    """Demo multi-agent workflow evaluation."""
    console.print("\n\n[bold cyan]4. Multi-Agent Workflow Testing[/bold cyan]")
    console.print("[dim]Test coordination and handoffs in BeeAI workflows[/dim]\n")
    
    # Show the code
    code = '''# Test multi-agent coordination
result = await recipes.multi_agent.test_coordination(
    workflow_coordinator,
    workflow_type="research_synthesis"
)

# Test handoff quality between agents
result = await recipes.multi_agent.test_handoff_quality(agent)'''
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=False)
    console.print(syntax)
    console.print()
    
    console.print("[dim]Perfect for testing BeeAI AgentWorkflow patterns![/dim]")


async def show_benefits():
    """Show the benefits of using recipes."""
    console.print("\n\n")
    console.print(Panel(
        "[bold green]Why Use ACP-Evals Recipes?[/bold green]\n\n"
        "• [cyan]One-line testing[/cyan] for common agent patterns\n"
        "• [cyan]BeeAI-specific[/cyan] evaluations (tools, workflows)\n" 
        "• [cyan]Production-ready[/cyan] test scenarios\n"
        "• [cyan]Progressive disclosure[/cyan] - simple to advanced\n"
        "• [cyan]Real LLM evaluations[/cyan] - no mocks\n\n"
        "Perfect for the BeeAI/ACP ecosystem!",
        title="ACP-Evals Recipes",
        border_style="green",
        padding=(1, 2)
    ))


async def main():
    """Run the recipe demos."""
    console.print("[bold]ACP-Evals Recipe Demo[/bold]")
    console.print("=" * 50)
    console.print("\nShowcasing one-line agent testing for common patterns")
    
    try:
        # Demo each recipe type
        await demo_customer_support()
        await demo_code_assistant()
        await demo_research_agent()
        await demo_multi_agent()
        
        # Show benefits
        await show_benefits()
        
        # Show import statement
        console.print("\n[bold]Get started:[/bold]")
        console.print(Syntax("from acp_evals import recipes", "python", theme="monokai"))
        
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")
        console.print("[yellow]Make sure the test agent is running![/yellow]")
        raise


if __name__ == "__main__":
    asyncio.run(main())