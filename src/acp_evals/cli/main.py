#!/usr/bin/env python3
"""
CLI tool for ACP evaluations with init command and templates.
"""

import os
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

# Import commands
# Import logging setup
from ..utils.logging import setup_logging
from .check import check_providers
from .commands.discover import discover
from .commands.run import run
from .commands.test import test


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output")
@click.option("--debug", is_flag=True, help="Show debug output including stack traces")
@click.option("-q", "--quiet", is_flag=True, help="Suppress non-essential output")
@click.pass_context
def cli(ctx, verbose, debug, quiet):
    """ACP Evals - Test and benchmark your ACP agents with production-grade evaluations.

    Quick start:
        acp-evals test <agent-url>           # Quick agent testing
        acp-evals comprehensive <agent> -i "What is AI?" -e "Artificial Intelligence"
        acp-evals run accuracy <agent> -i "What is AI?" -e "Artificial Intelligence"
        acp-evals discover                   # Find available agents
        acp-evals check                      # Verify configuration

    Get help:
        acp-evals --help                     # Show all commands
        acp-evals <command> --help           # Show command details
    """
    # Ensure context is available for all subcommands
    ctx.ensure_object(dict)

    # Check for conflicting flags
    if quiet and (verbose or debug):
        raise click.UsageError("--quiet cannot be used with --verbose or --debug")

    # Determine log level based on flags
    if debug:
        log_level = "DEBUG"
    elif verbose:
        log_level = "INFO"
    elif quiet:
        log_level = "ERROR"
    else:
        log_level = "WARNING"  # Default level

    # Setup logging with appropriate level
    setup_logging(level=log_level)

    # Store flags in context for access by subcommands
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["quiet"] = quiet
    ctx.obj["log_level"] = log_level

    # Configure console output based on flags
    if quiet:
        console.quiet = True
    elif verbose or debug:
        console.verbose = True


# Register commands
cli.add_command(check_providers, name="check")
cli.add_command(test)
cli.add_command(run)
cli.add_command(discover)

# Import and register quick-start command
from .commands.quickstart import quickstart

cli.add_command(quickstart)

# Import and register comprehensive evaluation command
from .commands.comprehensive import comprehensive

cli.add_command(comprehensive)


@cli.command()
@click.argument(
    "template",
    type=click.Choice(["simple", "comprehensive", "research", "tool", "acp-agent", "multi-agent"]),
    default="simple",
)
@click.option("--name", "-n", help="Name for your agent/evaluation")
@click.option("--output", "-o", help="Output file path", default="agent_eval.py")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode with prompts")
@click.pass_context
def init(ctx, template, name, output, interactive):
    """Generate a starter evaluation template.

    Templates:
    - simple: Basic evaluation with accuracy testing
    - comprehensive: Full suite with accuracy, performance, reliability
    - research: Specialized for research/analysis agents
    - tool: For agents that use external tools
    - acp-agent: Real ACP protocol agent evaluation
    - multi-agent: Multi-agent coordination patterns
    """
    # Skip intro message in quiet mode
    if not ctx.obj.get("quiet"):
        console.print("[bold cyan]ACP Evaluations Template Generator[/bold cyan]\n")

    # Load templates from external file for maintainability
    from .templates import TEMPLATES

    # Interactive mode
    if interactive:
        template = Prompt.ask(
            "Select template type",
            choices=["simple", "comprehensive", "research", "tool", "acp-agent", "multi-agent"],
            default="simple",
        )

        name = Prompt.ask("Agent name", default="MyAgent")
        output = Prompt.ask("Output file", default=f"{name.lower()}_eval.py")

    # Generate names from agent name
    if not name:
        name = Path(output).stem.replace("_eval", "").replace("-", "_").title()

    agent_function = name.lower().replace(" ", "_")
    agent_class = name.replace(" ", "")

    # Get template
    template_content = TEMPLATES[template]

    # Customize template
    replacements = {
        "{agent_name}": name,
        "{agent_function}": agent_function,
        "{agent_class}": agent_class,
    }

    # Additional prompts for comprehensive template
    if template == "comprehensive" and interactive:
        rubric_choice = Prompt.ask(
            "Select evaluation rubric",
            choices=["factual", "research_quality", "code_quality", "custom"],
            default="factual",
        )

        if rubric_choice == "custom":
            replacements["{rubric_choice}"] = """{
            "accuracy": {"weight": 0.5, "criteria": "Is the response accurate?"},
            "completeness": {"weight": 0.3, "criteria": "Is the response complete?"},
            "clarity": {"weight": 0.2, "criteria": "Is the response clear?"}
        }"""
        else:
            replacements["{rubric_choice}"] = f'"{rubric_choice}"'

        replacements["{sample_input}"] = Prompt.ask(
            "Sample test input", default="What is the capital of France?"
        )
        replacements["{sample_expected}"] = Prompt.ask("Expected output", default="Paris")
    else:
        # Defaults for non-interactive mode
        replacements["{rubric_choice}"] = '"factual"'
        replacements["{sample_input}"] = "What is the capital of France?"
        replacements["{sample_expected}"] = "Paris"

    # Additional replacements for ACP and multi-agent templates
    if template == "acp-agent":
        replacements["{agent_url}"] = "http://localhost:8000/agents/my-agent"
        replacements["{base_url}"] = "http://localhost:8000"
    elif template == "multi-agent":
        replacements["{researcher_url}"] = "http://localhost:8000/agents/researcher"
        replacements["{analyst_url}"] = "http://localhost:8000/agents/analyst"
        replacements["{writer_url}"] = "http://localhost:8000/agents/writer"

    # Apply replacements
    for key, value in replacements.items():
        template_content = template_content.replace(key, value)

    # Check if file exists
    output_path = Path(output)
    if output_path.exists():
        if interactive:
            overwrite = Confirm.ask(f"[yellow]{output}[/yellow] already exists. Overwrite?")
            if not overwrite:
                console.print("[red]Aborted.[/red]")
                return
        else:
            console.print(
                f"[yellow]Warning: {output} already exists. Use -i for interactive mode.[/yellow]"
            )
            return

    # Write file
    output_path.write_text(template_content)

    # Make executable
    os.chmod(output_path, 0o755)

    # Success message (respect quiet mode)
    if not ctx.obj.get("quiet"):
        console.print(f"\n[green]Created evaluation template:[/green] [bold]{output}[/bold]")
        console.print(f"\nTemplate type: [cyan]{template}[/cyan]")
        console.print(f"Agent name: [cyan]{name}[/cyan]")

        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Edit the file to implement your agent logic")
        console.print("2. Update test cases with your specific scenarios")
        console.print("3. Run the evaluation:")
        console.print(f"   [dim]python {output}[/dim]")

        if template == "simple":
            console.print("\n[dim]Tip: Use -t comprehensive for a full evaluation suite[/dim]")


@cli.command()
@click.pass_context
def list_rubrics(ctx):
    """List available evaluation rubrics."""
    from acp_evals.api import AccuracyEval

    if not ctx.obj.get("quiet"):
        console.print("[bold cyan]Available Evaluation Rubrics[/bold cyan]\n")

    for name, rubric in AccuracyEval.RUBRICS.items():
        console.print(f"[bold]{name}[/bold]")
        console.print(f"  Best for: {rubric.get('description', 'General evaluation')}")
        console.print("  Criteria:")
        for criterion, details in rubric.items():
            if criterion != "description" and isinstance(details, dict):
                console.print(f"    - {criterion} (weight: {details['weight']})")
                console.print(f"      {details['criteria']}")
        console.print()


@cli.command()
@click.argument("results_file", type=click.Path(exists=True))
@click.option(
    "--format", "-f", type=click.Choice(["summary", "detailed", "markdown"]), default="summary"
)
@click.pass_context
def report(ctx, results_file, format):
    """Generate a report from evaluation results."""
    import json

    from rich.markdown import Markdown
    from rich.table import Table

    # Load results
    with open(results_file) as f:
        data = json.load(f)

    if format == "summary":
        # Summary table
        table = Table(title="Evaluation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        summary = data.get("summary", {})
        table.add_row("Total Tests", str(summary.get("total", 0)))
        table.add_row("Passed", f"[green]{summary.get('passed', 0)}[/green]")
        table.add_row("Failed", f"[red]{summary.get('failed', 0)}[/red]")
        table.add_row("Pass Rate", f"{summary.get('pass_rate', 0):.1f}%")
        table.add_row("Average Score", f"{summary.get('avg_score', 0):.2f}")

        console.print(table)

    elif format == "detailed":
        # Detailed results
        console.print("[bold]Detailed Evaluation Results[/bold]\n")

        for i, result in enumerate(data.get("results", [])):
            status = "[green]PASSED[/green]" if result["passed"] else "[red]FAILED[/red]"
            console.print(f"Test {i + 1}: {status} (Score: {result['score']:.2f})")
            console.print(f"  Input: {result.get('metadata', {}).get('input', 'N/A')}")
            console.print(f"  Expected: {result.get('metadata', {}).get('expected', 'N/A')}")
            console.print(f"  Feedback: {result.get('details', {}).get('feedback', 'N/A')}")
            console.print()

    elif format == "markdown":
        # Markdown report
        md_content = f"""# Evaluation Report

## Summary
- **Total Tests**: {data.get("summary", {}).get("total", 0)}
- **Passed**: {data.get("summary", {}).get("passed", 0)}
- **Failed**: {data.get("summary", {}).get("failed", 0)}
- **Pass Rate**: {data.get("summary", {}).get("pass_rate", 0):.1f}%
- **Average Score**: {data.get("summary", {}).get("avg_score", 0):.2f}

## Detailed Results
"""

        for i, result in enumerate(data.get("results", [])):
            md_content += f"""
### Test {i + 1}
- **Status**: {"Passed" if result["passed"] else "Failed"}
- **Score**: {result["score"]:.2f}
- **Input**: `{result.get("metadata", {}).get("input", "N/A")}`
- **Expected**: `{result.get("metadata", {}).get("expected", "N/A")}`
- **Feedback**: {result.get("details", {}).get("feedback", "N/A")}
"""

        console.print(Markdown(md_content))


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
