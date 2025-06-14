"""
Example: Evaluating a single ACP agent with comprehensive metrics.

This example demonstrates how to use the ACP Evals framework to evaluate
an agent's performance across multiple dimensions.
"""

import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

from acp_evals.client import ACPEvaluationClient
from acp_evals.metrics import TokenUsageMetric, LatencyMetric, ContextEfficiencyMetric
from acp_evals.benchmarks import ContextScalingBenchmark


console = Console()


async def display_metric_result(name: str, result):
    """Display a metric result in a formatted panel."""
    content = f"Value: {result.value:.2f} {result.unit}\n"
    
    if result.breakdown:
        content += "\nBreakdown:\n"
        for key, value in result.breakdown.items():
            if isinstance(value, float):
                content += f"  • {key}: {value:.2f}\n"
            elif isinstance(value, dict):
                content += f"  • {key}:\n"
                for k, v in value.items():
                    content += f"    - {k}: {v}\n"
            else:
                content += f"  • {key}: {value}\n"
    
    panel = Panel(content, title=f"[bold cyan]{name}[/bold cyan]", border_style="cyan")
    console.print(panel)


async def main():
    """Run comprehensive evaluation of an ACP agent."""
    
    # Configuration
    agent_url = "http://localhost:8000"  # Update with your agent URL
    agent_name = "echo"  # Update with your agent name
    
    console.print("[bold magenta]🔍 ACP Agent Evaluation Framework[/bold magenta]\n")
    
    # Initialize metrics
    metrics = [
        TokenUsageMetric(model="gpt-4"),
        LatencyMetric(),
        ContextEfficiencyMetric(),
    ]
    
    # Initialize client
    console.print("Connecting to ACP agent...", style="yellow")
    client = ACPEvaluationClient(
        base_url=agent_url,
        metrics=metrics,
    )
    
    # List available agents
    try:
        agents = await client.list_agents()
        console.print(f"✓ Found {len(agents)} agents", style="green")
        
        # Display agents table
        table = Table(title="Available Agents")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        
        for agent in agents:
            table.add_row(agent.name, agent.description or "No description")
        
        console.print(table)
        console.print()
        
        # Check if target agent exists
        target_agent = await client.get_agent(agent_name)
        if not target_agent:
            console.print(f"[red]Agent '{agent_name}' not found![/red]")
            return
            
    except Exception as e:
        console.print(f"[red]Failed to connect to agent: {e}[/red]")
        return
    
    # Run simple evaluation
    console.print(f"\n[bold]Running Simple Evaluation on '{agent_name}'[/bold]\n")
    
    test_prompt = "What is the capital of France?"
    
    try:
        # Run with tracking
        run, events, metric_results = await client.run_with_tracking(
            agent_name=agent_name,
            input=test_prompt,
        )
        
        # Display response
        console.print(Panel(
            f"Prompt: {test_prompt}\n\nResponse: {run.output[0].parts[0].content if run.output else 'No response'}",
            title="Agent Response",
            border_style="green"
        ))
        
        # Display metrics
        console.print("\n[bold]Metrics Results:[/bold]\n")
        for metric_name, result in metric_results.items():
            await display_metric_result(metric_name, result)
        
    except Exception as e:
        console.print(f"[red]Error during evaluation: {e}[/red]")
        return
    
    # Run context scaling benchmark
    console.print("\n[bold]Running Context Scaling Benchmark[/bold]\n")
    
    benchmark = ContextScalingBenchmark(
        distractor_levels=[0, 1, 3, 5],  # Test with different context levels
        task_categories=["information_retrieval", "reasoning"],  # Focus on specific categories
    )
    
    try:
        # Run benchmark
        console.print("Running benchmark tasks...", style="yellow")
        benchmark_result = await client.run_benchmark(
            agent_name=agent_name,
            benchmark=benchmark,
        )
        
        # Display benchmark results
        console.print("\n[bold cyan]Benchmark Results[/bold cyan]\n")
        
        # Summary table
        summary_table = Table(title="Context Scaling Performance")
        summary_table.add_column("Distractors", style="cyan", justify="center")
        summary_table.add_column("Avg Score", style="green", justify="center")
        summary_table.add_column("Success Rate", style="yellow", justify="center")
        
        for level, score in benchmark_result.summary["average_scores_by_distractor_level"].items():
            # Calculate success rate for this level
            level_results = [r for r in benchmark_result.task_results if r["num_distractors"] == level]
            success_rate = sum(1 for r in level_results if r["success"]) / len(level_results) * 100 if level_results else 0
            
            summary_table.add_row(
                str(level),
                f"{score:.2%}",
                f"{success_rate:.0f}%"
            )
        
        console.print(summary_table)
        
        # Key insights
        insights = []
        
        total_degradation = benchmark_result.summary.get("total_degradation", 0)
        if total_degradation > 20:
            insights.append(f"⚠️  High context sensitivity: {total_degradation:.1f}% performance drop with distractors")
        else:
            insights.append(f"✓ Good context handling: Only {total_degradation:.1f}% degradation")
        
        optimal_level = benchmark_result.summary.get("optimal_distractor_level", 0)
        insights.append(f"📊 Optimal performance at {optimal_level} distractors")
        
        console.print("\n[bold]Key Insights:[/bold]")
        for insight in insights:
            console.print(f"  {insight}")
        
        # Cost projection
        if "token_usage" in metric_results:
            token_result = metric_results["token_usage"]
            cost_per_run = token_result.breakdown.get("cost_usd", 0)
            monthly_cost = cost_per_run * 1000 * 30  # 1000 queries per day
            
            console.print(f"\n💰 Cost Projection: ${monthly_cost:.2f}/month (1000 queries/day)")
        
    except Exception as e:
        console.print(f"[red]Error running benchmark: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())