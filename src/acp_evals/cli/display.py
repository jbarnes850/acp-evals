"""
Enhanced display components console output.

This module provides visual components for displaying evaluation results
in a clear, scannable format without emojis.
"""

from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, MINIMAL
from rich.padding import Padding

console = Console()


def create_score_bar(score: float, width: int = 20) -> str:
    """Create a visual progress bar for scores."""
    filled = int(score * width)
    empty = width - filled
    return f"[green]{'█' * filled}[/green][dim]{'░' * empty}[/dim]"


def get_score_color(score: float) -> str:
    """Get color based on score value."""
    if score >= 0.9:
        return "green"
    elif score >= 0.7:
        return "yellow"
    elif score >= 0.5:
        return "orange1"
    else:
        return "red"


def create_evaluation_header(title: str = "ACP Evaluation Report") -> Panel:
    """Create a styled header for evaluation reports."""
    header_text = Text(title, style="bold cyan", justify="center")
    return Panel(
        header_text,
        box=DOUBLE,
        style="cyan",
        padding=(1, 2)
    )


def create_score_summary(results: Dict[str, float]) -> Panel:
    """Create a visual summary of evaluation scores."""
    # Calculate overall score
    overall = sum(results.values()) / len(results) if results else 0
    
    # Create summary text
    summary_lines = []
    summary_lines.append(f"Overall Score: {create_score_bar(overall)} {overall:.0%}\n")
    
    # Individual scores
    for metric, score in results.items():
        color = get_score_color(score)
        bar = create_score_bar(score)
        label = metric.replace("_", " ").title()
        summary_lines.append(f"{label:<15} {bar} [{color}]{score:.0%}[/{color}]")
    
    return Panel(
        "\n".join(summary_lines),
        title="Score Summary",
        border_style="green",
        box=ROUNDED,
        padding=(1, 2)
    )


def create_test_details_tree(test_results: List[Dict[str, Any]]) -> Panel:
    """Create a tree view of test results."""
    lines = []
    total_tests = len(test_results)
    passed_tests = sum(1 for t in test_results if t.get("passed", False))
    
    # Summary line
    lines.append(f"Test Details ({passed_tests} passed, {total_tests - passed_tests} failed)\n")
    
    # Individual tests
    for i, test in enumerate(test_results):
        is_last = i == len(test_results) - 1
        prefix = "└── " if is_last else "├── "
        
        status = "[green]✓[/green]" if test.get("passed") else "[red]✗[/red]"
        score = test.get("score", 0)
        score_color = get_score_color(score)
        
        lines.append(f"{prefix}{status} {test['name']} → Score: [{score_color}]{score:.2f}[/{score_color}]")
        
        # Add details if test failed
        if not test.get("passed") and test.get("reason"):
            detail_prefix = "    " if is_last else "│   "
            lines.append(f"{detail_prefix}└── {test['reason']}")
    
    return Panel(
        "\n".join(lines),
        title="Test Results",
        border_style="yellow",
        box=ROUNDED,
        padding=(1, 2)
    )


def create_suggestions_panel(suggestions: List[str]) -> Optional[Panel]:
    """Create a panel with improvement suggestions."""
    if not suggestions:
        return None
    
    formatted_suggestions = []
    for suggestion in suggestions:
        formatted_suggestions.append(f"• {suggestion}")
    
    return Panel(
        "\n".join(formatted_suggestions),
        title="Suggestions",
        border_style="blue",
        box=MINIMAL,
        padding=(1, 2)
    )


def create_metrics_table(metrics: Dict[str, Any]) -> Table:
    """Create a table displaying various metrics."""
    table = Table(title="Evaluation Metrics", box=ROUNDED)
    
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    for key, value in metrics.items():
        formatted_key = key.replace("_", " ").title()
        if isinstance(value, float):
            formatted_value = f"{value:.2f}"
        elif isinstance(value, int):
            formatted_value = str(value)
        else:
            formatted_value = str(value)
        
        table.add_row(formatted_key, formatted_value)
    
    return table


def create_cost_breakdown(cost_data: Dict[str, float]) -> Panel:
    """Create a visual cost breakdown."""
    lines = []
    
    total_cost = cost_data.get("total", 0)
    lines.append(f"Total Cost: [bold]${total_cost:.4f}[/bold]\n")
    
    # Token usage
    if "tokens" in cost_data:
        tokens = cost_data["tokens"]
        lines.append("Token Usage:")
        lines.append(f"  • Input:  {tokens.get('input', 0):,}")
        lines.append(f"  • Output: {tokens.get('output', 0):,}")
        lines.append(f"  • Total:  {tokens.get('total', 0):,}")
    
    # Cost projections
    if "projections" in cost_data:
        lines.append("\nProjected Costs:")
        proj = cost_data["projections"]
        lines.append(f"  • Hourly:   ${proj.get('hourly', 0):.2f}")
        lines.append(f"  • Daily:    ${proj.get('daily', 0):.2f}")
        lines.append(f"  • Monthly:  ${proj.get('monthly', 0):.2f}")
    
    return Panel(
        "\n".join(lines),
        title="Cost Analysis",
        border_style="yellow",
        box=MINIMAL,
        padding=(1, 2)
    )


def create_live_progress(task_name: str) -> Progress:
    """Create a live progress display for running evaluations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("[dim]{task.elapsed:.1f}s elapsed"),
        console=console,
        transient=True
    )


def create_comparison_table(agents: List[str], results: Dict[str, Dict[str, float]]) -> Table:
    """Create a comparison table for multiple agents."""
    table = Table(title="Agent Comparison", box=DOUBLE)
    
    # Add columns
    table.add_column("Metric", style="cyan", no_wrap=True)
    for agent in agents:
        table.add_column(agent, justify="center")
    
    # Get all metrics
    all_metrics = set()
    for agent_results in results.values():
        all_metrics.update(agent_results.keys())
    
    # Add rows
    for metric in sorted(all_metrics):
        row = [metric.replace("_", " ").title()]
        
        # Find best score for highlighting
        scores = [results.get(agent, {}).get(metric, 0) for agent in agents]
        best_score = max(scores) if scores else 0
        
        for agent in agents:
            score = results.get(agent, {}).get(metric, 0)
            color = "green" if score == best_score and score > 0 else get_score_color(score)
            bar = create_score_bar(score, width=10)
            row.append(f"{bar}\n[{color}]{score:.2f}[/{color}]")
        
        table.add_row(*row)
    
    return table


def display_evaluation_report(
    results: Dict[str, Any],
    show_details: bool = True,
    show_suggestions: bool = True,
    show_costs: bool = True
) -> None:
    """Display a comprehensive evaluation report."""
    # Header
    console.print(create_evaluation_header())
    console.print()
    
    # Score summary
    if "scores" in results:
        console.print(create_score_summary(results["scores"]))
        console.print()
    
    # Test details
    if show_details and "test_results" in results:
        console.print(create_test_details_tree(results["test_results"]))
        console.print()
    
    # Metrics table
    if "metrics" in results:
        console.print(create_metrics_table(results["metrics"]))
        console.print()
    
    # Suggestions
    if show_suggestions and "suggestions" in results:
        suggestions_panel = create_suggestions_panel(results["suggestions"])
        if suggestions_panel:
            console.print(suggestions_panel)
            console.print()
    
    # Cost breakdown
    if show_costs and "cost_data" in results:
        console.print(create_cost_breakdown(results["cost_data"]))


def create_workflow_timeline(steps: List[Dict[str, Any]]) -> None:
    """Display a timeline of workflow steps."""
    panels = []
    
    for i, step in enumerate(steps):
        status_color = "green" if step["passed"] else "red" if step["status"] == "failed" else "yellow"
        status_icon = "✓" if step["passed"] else "✗" if step["status"] == "failed" else "..."
        
        panel_content = [
            f"[{status_color}]{status_icon}[/{status_color}] Step {i+1}",
            f"{step['name']}",
            f"Duration: {step.get('duration', 0):.2f}s"
        ]
        
        if step.get("error"):
            panel_content.append(f"[red]Error: {step['error']}[/red]")
        
        panel = Panel(
            "\n".join(panel_content),
            style=status_color,
            box=MINIMAL,
            expand=False,
            padding=(0, 1)
        )
        panels.append(panel)
    
    # Display in columns
    console.print(Columns(panels, equal=True, expand=True))


# Export display functions
__all__ = [
    "console",
    "create_score_bar",
    "create_evaluation_header",
    "create_score_summary", 
    "create_test_details_tree",
    "create_suggestions_panel",
    "create_metrics_table",
    "create_cost_breakdown",
    "create_live_progress",
    "create_comparison_table",
    "display_evaluation_report",
    "create_workflow_timeline"
]