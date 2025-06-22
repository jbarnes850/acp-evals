#!/usr/bin/env python3
"""
Comprehensive evaluation command that runs all three evaluators and shows unified results.
"""

import asyncio
from pathlib import Path

import click
from rich.console import Console

from ...api import AccuracyEval, PerformanceEval, ReliabilityEval
from ...utils.logging import get_logger
from ..display import display_comprehensive_evaluation_results

console = Console()
logger = get_logger(__name__)


@click.command()
@click.argument("agent", required=True)
@click.option("-i", "--input", "input_text", required=True, help="Input text to send to the agent")
@click.option("-e", "--expected", help="Expected output for accuracy evaluation")
@click.option(
    "--rubric",
    type=click.Choice(["factual", "research_quality", "code_quality"]),
    default="factual",
    help="Evaluation rubric for accuracy assessment",
)
@click.option("--expected-tools", multiple=True, help="Expected tools for reliability evaluation")
@click.option("--track-tokens", is_flag=True, help="Track token usage in performance evaluation")
@click.option("--track-latency", is_flag=True, default=True, help="Track response latency")
@click.option("--show-details", is_flag=True, help="Show detailed analysis for each dimension")
@click.option("--timeout", default=30, help="Timeout in seconds for each evaluation")
@click.pass_context
def comprehensive(
    ctx,
    agent,
    input_text,
    expected,
    rubric,
    expected_tools,
    track_tokens,
    track_latency,
    show_details,
    timeout,
):
    """Run comprehensive evaluation across all three dimensions (Accuracy, Performance, Reliability).

    This command provides a unified dashboard showing all evaluation scores together with
    visual score bars, making it easy to assess agent performance across all dimensions.

    Examples:
        # Basic comprehensive evaluation
        acp-evals comprehensive agent.py:my_agent -i "What is AI?" -e "Artificial Intelligence"

        # Full evaluation with tools and detailed analysis
        acp-evals comprehensive agent.py:my_agent -i "Search for Python tutorials" \\
            -e "List of Python learning resources" --expected-tools search \\
            --track-tokens --show-details

        # Code quality assessment
        acp-evals comprehensive agent.py:my_agent \\
            -i "Write a function to sort a list" \\
            -e "A working sort function" --rubric code_quality
    """

    if not ctx.obj.get("quiet"):
        console.print("[bold cyan]Running Agent Evaluation[/bold cyan]")
        console.print(f"[dim]Agent: {agent}[/dim]")
        console.print(f"[dim]Input: {input_text}[/dim]")
        console.print()

    # Initialize results
    accuracy_result = None
    performance_result = None
    reliability_result = None

    try:
        # Run all evaluations concurrently for efficiency
        async def run_comprehensive_evaluation():
            tasks = []

            # Accuracy evaluation (only if expected output provided)
            if expected:
                accuracy_eval = AccuracyEval(agent, rubric=rubric)
                accuracy_task = accuracy_eval.run(
                    input=input_text,
                    expected=expected,
                    print_results=False,  # We'll show unified results
                )
                tasks.append(("accuracy", accuracy_task))

            # Performance evaluation
            performance_eval = PerformanceEval(agent, track_tokens=track_tokens, track_memory=True)
            performance_task = performance_eval.run(input_text=input_text, print_results=False)
            tasks.append(("performance", performance_task))

            # Reliability evaluation
            reliability_eval = ReliabilityEval(agent)
            reliability_task = reliability_eval.run(
                input=input_text,
                expected_tools=list(expected_tools) if expected_tools else None,
                print_results=False,
            )
            tasks.append(("reliability", reliability_task))

            # Execute all tasks
            results = {}
            if not ctx.obj.get("quiet"):
                with console.status("[bold blue]Running evaluations...") as status:
                    for eval_type, task in tasks:
                        status.update(f"[bold blue]Running {eval_type} evaluation...")
                        try:
                            result = await task
                            results[eval_type] = result
                            status.update(f"[green]✓[/green] {eval_type.title()} complete")
                        except Exception as e:
                            logger.error(f"Failed {eval_type} evaluation: {e}")
                            if ctx.obj.get("debug"):
                                raise
                            console.print(
                                f"[yellow]Warning: {eval_type.title()} evaluation failed: {e}[/yellow]"
                            )
            else:
                # Run without status in quiet mode
                for eval_type, task in tasks:
                    try:
                        result = await task
                        results[eval_type] = result
                    except Exception as e:
                        logger.error(f"Failed {eval_type} evaluation: {e}")
                        if ctx.obj.get("debug"):
                            raise

            return results

        # Run the comprehensive evaluation
        results = asyncio.run(run_comprehensive_evaluation())

        # Extract results
        accuracy_result = results.get("accuracy")
        performance_result = results.get("performance")
        reliability_result = results.get("reliability")

        # Display unified results
        if not ctx.obj.get("quiet"):
            console.print()

        display_comprehensive_evaluation_results(
            accuracy_result=accuracy_result,
            performance_result=performance_result,
            reliability_result=reliability_result,
            agent_identifier=agent,
            show_individual_details=show_details,
        )

        # Determine exit code
        results_list = [
            r for r in [accuracy_result, performance_result, reliability_result] if r is not None
        ]
        if results_list:
            all_passed = all(getattr(r, "passed", False) for r in results_list)
            if not all_passed:
                ctx.exit(1)
        else:
            console.print("[red]No evaluations completed successfully[/red]")
            ctx.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Evaluation interrupted by user[/yellow]")
        ctx.exit(130)
    except Exception as e:
        logger.error(f"Comprehensive evaluation failed: {e}")
        if ctx.obj.get("debug"):
            raise
        console.print(f"[red]Evaluation failed: {e}[/red]")
        ctx.exit(1)
