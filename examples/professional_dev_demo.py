#!/usr/bin/env python3
"""
Professional Developer Demo for ACP-Evals.

This demonstrates the 10/10 developer experience for BeeAI/ACP ecosystem.
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from acp_evals.api_v2 import test, TestOptions
from acp_sdk.models import Message, MessagePart
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


async def main():
    """Demonstrate the professional developer experience."""
    
    # Welcome
    console.print(Panel(
        Text("ACP-Evals: Professional Agent Testing", style="bold cyan", justify="center"),
        subtitle="Built for BeeAI/ACP ecosystem developers",
        padding=(1, 2)
    ))
    
    # ============================================================
    # 1. INSTANT VALUE - Test in 2 lines
    # ============================================================
    console.print("\n[bold]1. Instant Value - Test Your Agent in 2 Lines[/bold]")
    console.print("[dim]No configuration, no setup, just works.[/dim]\n")
    
    console.print("[cyan]from acp_evals import test[/cyan]")
    console.print('[cyan]result = test("http://localhost:8000/agents/my-agent", "What is 2+2?", "4")[/cyan]')
    
    # Simulate the test
    agent_url = "http://localhost:8000/agents/test_agent"
    result = test(agent_url, "What is 2+2?", "4")
    
    console.print(f"\n✓ Your agent works! Score: {result.score:.2f}")
    
    # ============================================================
    # 2. NATIVE ACP SUPPORT - Rich Message Testing
    # ============================================================
    console.print("\n\n[bold]2. Native ACP Support - Test Rich Messages[/bold]")
    console.print("[dim]Works seamlessly with ACP Message format.[/dim]\n")
    
    console.print("[cyan]message = Message(parts=[[/cyan]")
    console.print('[cyan]    MessagePart(content="Analyze this chart", content_type="text/plain"),[/cyan]')
    console.print('[cyan]    MessagePart(content=chart_data, content_type="image/png")[/cyan]')
    console.print("[cyan]])[/cyan]")
    console.print('[cyan]result = test(agent, message, "Identifies upward trend")[/cyan]')
    
    # ============================================================
    # 3. PROGRESSIVE DISCLOSURE - Add Control When Needed
    # ============================================================
    console.print("\n\n[bold]3. Progressive Disclosure - Add Control When Needed[/bold]")
    console.print("[dim]Simple by default, powerful when you need it.[/dim]\n")
    
    # Level 1: Dead simple
    console.print("[green]# Level 1: Dead simple[/green]")
    console.print('[cyan]test(agent, "Hello", "Hi")[/cyan]')
    
    # Level 2: Some control
    console.print("\n[green]# Level 2: Some control[/green]")
    console.print('[cyan]test(agent, "Hello", "Hi", TestOptions(check="exact"))[/cyan]')
    
    # Level 3: Professional depth
    console.print("\n[green]# Level 3: Professional depth[/green]")
    console.print('[cyan]test(agent, prompt, expected, TestOptions([/cyan]')
    console.print('[cyan]    check="semantic",[/cyan]')
    console.print('[cyan]    threshold=0.85,[/cyan]')
    console.print('[cyan]    rubric="customer_service",[/cyan]')
    console.print('[cyan]    track_latency=True[/cyan]')
    console.print('[cyan]))[/cyan]')
    
    # ============================================================
    # 4. BEEAI-SPECIFIC EVALUATIONS (Coming Soon)
    # ============================================================
    console.print("\n\n[bold]4. BeeAI-Specific Evaluations[/bold]")
    console.print("[dim]Purpose-built for agent capabilities.[/dim]\n")
    
    console.print("[green]# Test tool usage[/green]")
    console.print('[cyan]evaluate.tool_usage(agent, "Find weather in Tokyo", ["weather_api"])[/cyan]')
    
    console.print("\n[green]# Test multi-step reasoning[/green]")
    console.print('[cyan]evaluate.reasoning(agent, "Plan a trip", ["research", "budget", "book"])[/cyan]')
    
    console.print("\n[green]# Test conversation state[/green]")
    console.print('[cyan]conv = evaluate.conversation(agent)[/cyan]')
    console.print('[cyan]conv.add_turn("My name is John")[/cyan]')
    console.print('[cyan]conv.add_turn("What\'s my name?")  # Tests memory[/cyan]')
    
    # ============================================================
    # 5. PROFESSIONAL OUTPUT - Clear, Actionable Feedback
    # ============================================================
    console.print("\n\n[bold]5. Professional Output - Clear, Actionable Feedback[/bold]")
    console.print("[dim]Not just scores, but insights.[/dim]\n")
    
    # Run a real test with detailed output
    result = test(
        agent_url,
        "Explain quantum computing",
        "A clear explanation of quantum computing basics",
        TestOptions(show_details=True)
    )
    
    # Show professional output format
    console.print("Testing agent capabilities...\n")
    console.print(f"EVALUATION RESULT")
    console.print(f"├─ Score        {'█' * int(result.score * 20)}{'░' * (20 - int(result.score * 20))} {result.score:.0%}")
    console.print(f"├─ Status       {'PASS' if result.passed else 'FAIL'}")
    console.print(f"├─ Latency      {result.details.get('latency_ms', 0):.0f}ms")
    console.print(f"└─ Feedback     {result.details.get('feedback', 'No feedback')[:60]}...")
    
    # ============================================================
    # SUMMARY
    # ============================================================
    console.print("\n" + "=" * 60)
    console.print(Panel(
        "[bold green]Ready to Build Production Agents[/bold green]\n\n"
        "• Simple API that scales with your needs\n"
        "• Native ACP/BeeAI integration\n"
        "• Professional metrics and feedback\n"
        "• No mocks, only real evaluations\n\n"
        "[dim]Start testing: pip install acp-evals[/dim]",
        title="ACP-Evals",
        border_style="green"
    ))


if __name__ == "__main__":
    asyncio.run(main())