"""Workflow command for multi-agent pattern testing."""

import asyncio
import json

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...benchmarks.multi_agent import HandoffQualityBenchmark, PatternComparisonBenchmark
from ...patterns import LinearPattern, SupervisorPattern, SwarmPattern
from ...patterns.base import AgentInfo

console = Console()


@click.group()
def workflow():
    """Test and analyze multi-agent workflows."""
    pass


@workflow.command()
@click.option('--pattern', '-p',
              type=click.Choice(['linear', 'supervisor', 'swarm']),
              required=True)
@click.option('--agents', '-a', multiple=True, required=True, help='Agent URLs')
@click.option('--task', '-t', required=True, help='Task to execute')
@click.option('--export', '-e', help='Export results')
def test(pattern: str, agents: tuple[str, ...], task: str, export: str | None):
    """Test a workflow pattern with agents.

    Examples:
        acp-evals workflow test -p linear -a agent1 -a agent2 -t "Research AI"
        acp-evals workflow test -p supervisor -a supervisor -a worker1 -a worker2 -t "Complex task"
        acp-evals workflow test -p swarm -a agent1 -a agent2 -a agent3 -t "Brainstorm" -e results.json
    """
    console.print(f"[bold]Testing {pattern} workflow pattern[/bold]")
    console.print(f"Agents: {', '.join(agents)}")
    console.print(f"Task: {task[:100]}...\n")

    # Validate agent count
    if pattern == 'linear' and len(agents) < 2:
        console.print("[red]Linear pattern requires at least 2 agents[/red]")
        exit(1)
    elif pattern == 'supervisor' and len(agents) < 2:
        console.print("[red]Supervisor pattern requires at least 2 agents (supervisor + workers)[/red]")
        exit(1)
    elif pattern == 'swarm' and len(agents) < 2:
        console.print("[red]Swarm pattern requires at least 2 agents[/red]")
        exit(1)

    try:
        # Create pattern instance
        # Convert agent URLs to AgentInfo objects
        agent_infos = [AgentInfo(name=f"agent_{i+1}", url=url) for i, url in enumerate(agents)]

        if pattern == 'linear':
            pattern_instance = LinearPattern(agent_infos)
        elif pattern == 'supervisor':
            supervisor_info = AgentInfo(name="supervisor", url=agents[0], role="supervisor")
            worker_infos = [AgentInfo(name=f"worker_{i+1}", url=url, role="worker") for i, url in enumerate(agents[1:])]
            pattern_instance = SupervisorPattern(
                supervisor=supervisor_info,
                workers=worker_infos
            )
        else:  # swarm
            pattern_instance = SwarmPattern(agent_infos)

        # Run workflow
        console.print("[yellow]Running workflow...[/yellow]")
        result = asyncio.run(pattern_instance.execute(task))

        # Display results
        console.print("\n[green]Workflow completed![/green]\n")

        # Show response
        final_output = result.get('final_output', 'No output')
        console.print(Panel(
            final_output[:500] + "..." if len(final_output) > 500 else final_output,
            title="Response",
            border_style="green"
        ))

        # Show metadata
        console.print("\n[bold]Workflow Metadata:[/bold]")
        console.print(f"Pattern: {result.get('pattern', 'N/A')}")
        console.print(f"Agents used: {result.get('agents_used', 'N/A')}")
        console.print(f"Total latency: {result.get('total_latency', 0):.2f}s")
        console.print(f"Success: {result.get('success', False)}")

        if 'handoffs' in result:
            console.print("\n[bold]Handoffs:[/bold]")
            for i, handoff in enumerate(result['handoffs']):
                if i > 0:
                    prev_agent = result['handoffs'][i-1]['agent']
                    curr_agent = handoff['agent']
                    console.print(f"  {prev_agent} → {curr_agent}")
                    if 'preserved_context' in handoff and handoff['preserved_context'] is not None:
                        console.print(f"    Context preserved: {handoff['preserved_context']:.2f}")

        # Export if requested
        if export:
            export_data = {
                'pattern': pattern,
                'agents': list(agents),
                'task': task,
                'result': result
            }

            with open(export, 'w') as f:
                json.dump(export_data, f, indent=2)

            console.print(f"\n[green]Results exported to:[/green] {export}")

    except Exception as e:
        console.print(f"[red]Workflow failed: {e}[/red]")
        exit(1)


@workflow.command()
@click.option('--agents', '-a', multiple=True, required=True, help='Agent URLs to compare')
@click.option('--tasks', '-t', multiple=True, help='Tasks to test (or use defaults)')
@click.option('--export', '-e', help='Export comparison results')
def compare(agents: tuple[str, ...], tasks: tuple[str, ...], export: str | None):
    """Compare workflow patterns on the same tasks.

    Examples:
        acp-evals workflow compare -a agent1 -a agent2 -a agent3
        acp-evals workflow compare -a url1 -a url2 -t "Research task" -t "Analysis task"
        acp-evals workflow compare -a agent1 -a agent2 -a agent3 -e comparison.json
    """
    console.print("[bold]Comparing workflow patterns[/bold]")
    console.print(f"Agents: {len(agents)}")

    if len(agents) < 3:
        console.print("[yellow]Warning: Using fewer than 3 agents limits pattern options[/yellow]")

    # Use default tasks if none provided
    if not tasks:
        tasks = (
            "Analyze the pros and cons of renewable energy",
            "Create a marketing strategy for a new product",
            "Debug a complex software issue"
        )
        console.print("Using default comparison tasks")

    console.print(f"Tasks: {len(tasks)}\n")

    try:
        # Create comparison benchmark
        agents_dict = {f"agent_{i+1}": url for i, url in enumerate(agents)}

        comparison = PatternComparisonBenchmark(
            agents=agents_dict,
            patterns=['linear', 'supervisor', 'swarm']
        )

        # Run comparison
        console.print("[yellow]Running pattern comparison...[/yellow]")
        results = asyncio.run(comparison.run_comparison(
            tasks=list(tasks),
            metrics=['quality', 'efficiency', 'coordination']
        ))

        # Display results table
        table = Table(title="Pattern Comparison Results")
        table.add_column("Pattern", style="cyan")
        table.add_column("Quality", style="yellow")
        table.add_column("Efficiency", style="green")
        table.add_column("Coordination", style="magenta")
        table.add_column("Overall", style="bold")

        for pattern_name, scores in results.items():
            overall = sum(scores.values()) / len(scores)
            table.add_row(
                pattern_name.title(),
                f"{scores.get('quality', 0):.2f}",
                f"{scores.get('efficiency', 0):.2f}",
                f"{scores.get('coordination', 0):.2f}",
                f"{overall:.2f}"
            )

        console.print(table)

        # Show recommendations
        console.print("\n[bold]Pattern Recommendations:[/bold]")

        # Determine best pattern for each metric
        for metric in ['quality', 'efficiency', 'coordination']:
            best_pattern = max(results.items(), key=lambda x: x[1].get(metric, 0))
            console.print(f"  Best for {metric}: [green]{best_pattern[0]}[/green]")

        # Overall recommendation
        overall_scores = {p: sum(s.values())/len(s) for p, s in results.items()}
        best_overall = max(overall_scores.items(), key=lambda x: x[1])
        console.print(f"\n[bold]Overall recommendation:[/bold] [green]{best_overall[0]}[/green]")

        # Export if requested
        if export:
            export_data = {
                'agents': agents_dict,
                'tasks': list(tasks),
                'results': results,
                'recommendations': {
                    'overall': best_overall[0],
                    'by_metric': {
                        metric: max(results.items(), key=lambda x: x[1].get(metric, 0))[0]
                        for metric in ['quality', 'efficiency', 'coordination']
                    }
                }
            }

            with open(export, 'w') as f:
                json.dump(export_data, f, indent=2)

            console.print(f"\n[green]Comparison exported to:[/green] {export}")

    except Exception as e:
        console.print(f"[red]Comparison failed: {e}[/red]")
        exit(1)


@workflow.command()
@click.option('--agents', '-a', multiple=True, required=True, help='Agents in handoff chain')
@click.option('--task', '-t', default="Preserve this information through the chain", help='Task with info to preserve')
@click.option('--export', '-e', help='Export handoff analysis')
def handoff(agents: tuple[str, ...], task: str, export: str | None):
    """Test information preservation in agent handoffs.

    Examples:
        acp-evals workflow handoff -a agent1 -a agent2 -a agent3
        acp-evals workflow handoff -a url1 -a url2 -t "Complex requirements to preserve"
        acp-evals workflow handoff -a agent1 -a agent2 -a agent3 -e handoff-analysis.json
    """
    console.print("[bold]Testing handoff quality[/bold]")
    console.print(f"Chain length: {len(agents)} agents")
    console.print(f"Task: {task[:100]}...\n")

    try:
        # Create linear pattern for handoff testing
        agent_infos = [AgentInfo(name=f"agent_{i+1}", url=url) for i, url in enumerate(agents)]
        pattern = LinearPattern(agent_infos)

        # Create handoff benchmark
        benchmark = HandoffQualityBenchmark(
            pattern=pattern,
            endpoint=""  # Using direct URLs
        )

        # Run handoff test
        console.print("[yellow]Running handoff test...[/yellow]")

        # Create expected handoffs
        expected_handoffs = []
        for i in range(len(agents) - 1):
            expected_handoffs.append(f"agent_{i+1}->agent_{i+2}")

        result = asyncio.run(benchmark.evaluate_single(
            task=task,
            expected_handoffs=expected_handoffs
        ))

        # Display results
        console.print("\n[green]Handoff test completed![/green]\n")

        console.print(f"[bold]Overall Score:[/bold] {result.score:.2f}")
        console.print(f"[bold]Information Preserved:[/bold] {result.details.get('preservation_score', 0):.2f}")

        # Show handoff details
        if 'handoffs_completed' in result.details:
            console.print("\n[bold]Handoff Details:[/bold]")
            for handoff in result.details['handoffs_completed']:
                console.print(f"  • {handoff}")

        # Show degradation analysis
        if 'degradation_points' in result.details:
            console.print("\n[bold]Information Loss Points:[/bold]")
            for point in result.details['degradation_points']:
                console.print(f"  • {point}")

        # Recommendations
        console.print("\n[bold]Recommendations:[/bold]")
        if result.score < 0.7:
            console.print("  [yellow]⚠ Significant information loss detected[/yellow]")
            console.print("  Consider:")
            console.print("  - Using structured data formats")
            console.print("  - Adding validation between handoffs")
            console.print("  - Reducing chain length")
        else:
            console.print("  [green]✓ Good information preservation[/green]")

        # Export if requested
        if export:
            export_data = {
                'agents': list(agents),
                'task': task,
                'score': result.score,
                'preservation_score': result.details.get('preservation_score', 0),
                'handoffs': result.details.get('handoffs_completed', []),
                'degradation_points': result.details.get('degradation_points', []),
                'metadata': result.metadata
            }

            with open(export, 'w') as f:
                json.dump(export_data, f, indent=2)

            console.print(f"\n[green]Analysis exported to:[/green] {export}")

    except Exception as e:
        console.print(f"[red]Handoff test failed: {e}[/red]")
        exit(1)


if __name__ == "__main__":
    workflow()

