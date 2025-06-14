"""
Example: Quick token usage analysis for ACP agents.

This example shows how to analyze token usage patterns and costs
for different types of prompts.
"""

import asyncio
from rich.console import Console
from rich.table import Table
from rich import box

from acp_evals.client import ACPEvaluationClient
from acp_evals.metrics import TokenUsageMetric


console = Console()


# Test prompts of varying complexity
TEST_PROMPTS = [
    {
        "name": "Simple Question",
        "prompt": "What is 2 + 2?",
        "category": "math",
    },
    {
        "name": "Code Generation",
        "prompt": "Write a Python function to calculate factorial of a number.",
        "category": "coding",
    },
    {
        "name": "Complex Reasoning",
        "prompt": "Explain the difference between machine learning and deep learning, including examples of when to use each approach.",
        "category": "explanation",
    },
    {
        "name": "Creative Task",
        "prompt": "Write a haiku about artificial intelligence.",
        "category": "creative",
    },
]


async def analyze_token_usage(client: ACPEvaluationClient, agent_name: str):
    """Analyze token usage for different prompt types."""
    
    results = []
    
    for test in TEST_PROMPTS:
        console.print(f"\n Testing: [cyan]{test['name']}[/cyan]")
        console.print(f"Prompt: {test['prompt'][:50]}...", style="dim")
        
        try:
            # Run with tracking
            run, events, metrics = await client.run_with_tracking(
                agent_name=agent_name,
                input=test["prompt"],
            )
            
            # Extract token metrics
            if "token_usage" in metrics:
                token_result = metrics["token_usage"]
                
                results.append({
                    "name": test["name"],
                    "category": test["category"],
                    "input_tokens": token_result.breakdown.get("input_tokens", 0),
                    "output_tokens": token_result.breakdown.get("output_tokens", 0),
                    "total_tokens": token_result.value,
                    "cost_usd": token_result.breakdown.get("cost_usd", 0),
                    "efficiency": token_result.breakdown.get("efficiency_score", 0),
                })
                
                console.print(f"✓ Tokens: {token_result.value}, Cost: ${token_result.breakdown.get('cost_usd', 0):.4f}", style="green")
            else:
                console.print("⚠️  No token metrics available", style="yellow")
                
        except Exception as e:
            console.print(f"✗ Error: {e}", style="red")
    
    return results


def display_analysis(results: list):
    """Display token analysis results."""
    
    if not results:
        console.print("\n[red]No results to display[/red]")
        return
    
    # Create summary table
    table = Table(
        title="Token Usage Analysis",
        box=box.ROUNDED,
        show_footer=True,
    )
    
    table.add_column("Task", style="cyan", footer="Total/Avg")
    table.add_column("Category", style="magenta")
    table.add_column("Input", style="yellow", justify="right", footer="")
    table.add_column("Output", style="green", justify="right", footer="")
    table.add_column("Total", style="blue", justify="right", footer="")
    table.add_column("Cost", style="red", justify="right", footer="")
    
    total_input = 0
    total_output = 0
    total_tokens = 0
    total_cost = 0
    
    for result in results:
        table.add_row(
            result["name"],
            result["category"],
            str(result["input_tokens"]),
            str(result["output_tokens"]),
            str(result["total_tokens"]),
            f"${result['cost_usd']:.4f}",
        )
        
        total_input += result["input_tokens"]
        total_output += result["output_tokens"]
        total_tokens += result["total_tokens"]
        total_cost += result["cost_usd"]
    
    # Add footer with totals
    table.columns[2].footer = str(total_input)
    table.columns[3].footer = str(total_output)
    table.columns[4].footer = str(total_tokens)
    table.columns[5].footer = f"${total_cost:.4f}"
    
    console.print("\n")
    console.print(table)
    
    # Category analysis
    console.print("\n[bold]Token Usage by Category:[/bold]")
    
    category_stats = {}
    for result in results:
        cat = result["category"]
        if cat not in category_stats:
            category_stats[cat] = {"count": 0, "tokens": 0, "cost": 0}
        
        category_stats[cat]["count"] += 1
        category_stats[cat]["tokens"] += result["total_tokens"]
        category_stats[cat]["cost"] += result["cost_usd"]
    
    for cat, stats in category_stats.items():
        avg_tokens = stats["tokens"] / stats["count"]
        avg_cost = stats["cost"] / stats["count"]
        console.print(f"  • {cat}: {avg_tokens:.0f} tokens/query, ${avg_cost:.4f}/query")
    
    # Cost projections
    console.print("\n[bold]Cost Projections:[/bold]")
    
    avg_cost_per_query = total_cost / len(results)
    projections = {
        "100 queries/day": avg_cost_per_query * 100 * 30,
        "1,000 queries/day": avg_cost_per_query * 1000 * 30,
        "10,000 queries/day": avg_cost_per_query * 10000 * 30,
    }
    
    for scenario, monthly_cost in projections.items():
        console.print(f"  • {scenario}: ${monthly_cost:,.2f}/month")
    
    # Efficiency insights
    console.print("\n[bold]Efficiency Insights:[/bold]")
    
    most_efficient = min(results, key=lambda x: x["total_tokens"])
    least_efficient = max(results, key=lambda x: x["total_tokens"])
    
    console.print(f"  • Most token-efficient: {most_efficient['name']} ({most_efficient['total_tokens']} tokens)")
    console.print(f"  • Least token-efficient: {least_efficient['name']} ({least_efficient['total_tokens']} tokens)")
    
    # Token ratio analysis
    avg_output_ratio = sum(r["output_tokens"] / r["total_tokens"] for r in results) / len(results)
    console.print(f"  • Average output/total ratio: {avg_output_ratio:.1%}")


async def main():
    """Run token usage analysis."""
    
    # Configuration
    agent_url = "http://localhost:8000"  # Update with your agent URL
    agent_name = "echo"  # Update with your agent name
    
    console.print("[bold magenta]🔍 ACP Token Usage Analysis[/bold magenta]\n")
    
    # Initialize client with token metric
    client = ACPEvaluationClient(
        base_url=agent_url,
        metrics=[TokenUsageMetric(model="gpt-4")],
    )
    
    try:
        # Check connection
        agents = await client.list_agents()
        console.print(f"✓ Connected to ACP server ({len(agents)} agents available)", style="green")
        
        # Check if agent exists
        if not await client.get_agent(agent_name):
            console.print(f"\n[red]Agent '{agent_name}' not found![/red]")
            console.print("Available agents:", ", ".join(a.name for a in agents))
            return
        
        console.print(f"✓ Using agent: [cyan]{agent_name}[/cyan]\n")
        
        # Run analysis
        results = await analyze_token_usage(client, agent_name)
        
        # Display results
        display_analysis(results)
        
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())