"""Run command for direct evaluation from CLI."""

import asyncio
import json
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...api import AccuracyEval, PerformanceEval, ReliabilityEval

console = Console()


def format_result(result: Any) -> None:
    """Format and display evaluation result."""
    # Create result table
    table = Table(title="Evaluation Result", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    # Basic metrics
    table.add_row("Score", f"{result.score:.2f}")
    table.add_row("Passed", "[green]Yes[/green]" if result.passed else "[red]No[/red]")

    # Cost and tokens if available
    if hasattr(result, "cost") and result.cost is not None:
        table.add_row("Cost", f"${result.cost:.4f}")

    if hasattr(result, "tokens") and result.tokens:
        table.add_row("Tokens", str(result.tokens.get("total", "N/A")))

    # Latency if available
    if hasattr(result, "latency_ms") and result.latency_ms:
        table.add_row("Latency", f"{result.latency_ms:.0f}ms")

    console.print(table)

    # Details panel if available
    if hasattr(result, "details") and result.details:
        details_text = ""

        # Format details based on content
        if "judge_reasoning" in result.details:
            details_text += (
                f"[bold]Judge Reasoning:[/bold]\n{result.details['judge_reasoning']}\n\n"
            )

        if "feedback" in result.details:
            details_text += f"[bold]Feedback:[/bold]\n{result.details['feedback']}\n\n"

        if "criteria_scores" in result.details:
            details_text += "[bold]Criteria Scores:[/bold]\n"
            for criterion, score in result.details["criteria_scores"].items():
                details_text += f"  • {criterion}: {score:.2f}\n"

        if details_text:
            console.print(
                Panel(
                    details_text.strip(),
                    title="Evaluation Details",
                    border_style="blue",
                )
            )


@click.command()
@click.argument(
    "evaluator",
    type=click.Choice(["accuracy", "performance", "reliability"]),
)
@click.argument("agent")
@click.option("-i", "--input", "input_text", required=True, help="Input text for evaluation")
@click.option("-e", "--expected", help="Expected output (for accuracy evaluation)")
@click.option(
    "--rubric",
    type=click.Choice(["factual", "research_quality", "code_quality"]),
    default="factual",
)
@click.option("--track-tokens", is_flag=True, help="Track token usage (performance)")
@click.option("--track-latency", is_flag=True, help="Track response latency (performance)")
@click.option("--expected-tools", multiple=True, help="Expected tools for reliability eval")
@click.option("--export", "-o", help="Export result to JSON file")
@click.pass_context
def run(
    ctx,
    evaluator: str,
    agent: str,
    input_text: str,
    expected: str | None,
    rubric: str,
    track_tokens: bool,
    track_latency: bool,
    expected_tools: tuple[str, ...],
    export: str | None,
) -> None:
    """Run a single evaluation directly from CLI.

    Examples:
        acp-evals run accuracy my-agent -i "What is 2+2?" -e "4"
        acp-evals run performance my-agent -i "Complex task" --track-tokens
        acp-evals run reliability my-agent -i "Use search tool" --expected-tools search
    """
    # Get quiet mode from context
    quiet = ctx.obj.get("quiet", False)
    ctx.obj.get("verbose", False)
    debug = ctx.obj.get("debug", False)

    if not quiet:
        console.print(f"\n[bold cyan]Running {evaluator.title()} Evaluation[/bold cyan]")
        console.print(f"Agent: [yellow]{agent}[/yellow]")
        console.print(
            f"Input: [dim]{input_text[:100]}{'...' if len(input_text) > 100 else ''}[/dim]\n"
        )

    try:
        # Create and run appropriate evaluator
        if evaluator == "accuracy":
            if not expected:
                console.print(
                    "[red]Error: Expected output is required for accuracy evaluation[/red]"
                )
                console.print("Use -e/--expected to provide the expected output")
                exit(1)

            eval_instance = AccuracyEval(agent=agent, rubric=rubric)
            result = asyncio.run(
                eval_instance.run(
                    input=input_text,
                    expected=expected,
                    print_results=not quiet,  # Use rich display unless in quiet mode
                )
            )

        elif evaluator == "performance":
            eval_instance = PerformanceEval(agent=agent, track_tokens=track_tokens)
            result = asyncio.run(
                eval_instance.run(
                    input_text=input_text,
                    expected=expected,
                    print_results=not quiet,  # Use rich display unless in quiet mode
                )
            )

        elif evaluator == "reliability":
            eval_instance = ReliabilityEval(
                agent=agent,
                tool_definitions=list(expected_tools) if expected_tools else [],
            )
            result = asyncio.run(
                eval_instance.run(
                    input=input_text,
                    expected_tools=list(expected_tools) if expected_tools else [],
                    print_results=not quiet,  # Use rich display unless in quiet mode
                )
            )

        # Results are already displayed by the evaluators if not in quiet mode

        # Export if requested
        if export:
            export_data = {
                "evaluator": evaluator,
                "agent": agent,
                "input": input_text,
                "expected": expected,
                "result": {
                    "score": result.score,
                    "passed": result.passed,
                    "cost": getattr(result, "cost", None),
                    "tokens": getattr(result, "tokens", None),
                    "details": getattr(result, "details", {}),
                },
            }

            with open(export, "w") as f:
                json.dump(export_data, f, indent=2)

            if not quiet:
                console.print(f"\n[green]Result exported to:[/green] {export}")

        # Exit code based on pass/fail
        exit(0 if result.passed else 1)

    except KeyboardInterrupt:
        if not quiet:
            console.print("\n[yellow]Evaluation interrupted by user[/yellow]")
        exit(1)
    except Exception as e:
        if not quiet:
            console.print(f"\n[red]Evaluation failed: {e}[/red]")
        if debug:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        exit(1)


if __name__ == "__main__":
    run()
