"""
Enhanced display components console output.

This module provides visual components for displaying evaluation results
in a clear, scannable format without emojis.
"""

from typing import Any, Optional

from rich.align import Align
from rich.box import DOUBLE, MINIMAL, ROUNDED
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

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
        padding=(1, 2),
        width=120,  # Expanded width for better readability
    )


def create_score_summary(results: dict[str, float]) -> Panel:
    """Create a visual summary of evaluation scores with clear dimension breakdown."""
    if not results:
        return Panel("No scores available", title="Score Summary", border_style="red")

    # Create summary text
    summary_lines = []

    # Show scores in order of importance, with clear visual separation
    for i, (metric, score) in enumerate(results.items()):
        color = get_score_color(score)
        bar = create_score_bar(score, width=20)
        label = metric.replace("_", " ").title()

        # Make the first score (usually overall) more prominent
        if i == 0:
            summary_lines.append(f"[bold]{label}[/bold]")
            summary_lines.append(f"{bar} [{color}]{score:.3f}[/{color}] ({score:.1%})")
            summary_lines.append("")  # Space after overall score
        else:
            summary_lines.append(f"{label:<15} {bar} [{color}]{score:.3f}[/{color}]")

    # Determine border color based on primary score
    primary_score = list(results.values())[0]
    border_color = get_score_color(primary_score)

    return Panel(
        "\n".join(summary_lines),
        title="Evaluation Scores",
        border_style=border_color,
        box=ROUNDED,
        padding=(1, 2),
    )


def create_test_details_tree(test_results: list[dict[str, Any]]) -> Panel:
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

        lines.append(
            f"{prefix}{status} {test['name']} → Score: [{score_color}]{score:.2f}[/{score_color}]"
        )

        # Add details if test failed
        if not test.get("passed") and test.get("reason"):
            detail_prefix = "    " if is_last else "│   "
            lines.append(f"{detail_prefix}└── {test['reason']}")

    return Panel(
        "\n".join(lines), title="Test Results", border_style="yellow", box=ROUNDED, padding=(1, 2)
    )


def create_suggestions_panel(suggestions: list[str]) -> Panel | None:
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
        padding=(1, 2),
    )


def create_metrics_table(metrics: dict[str, Any]) -> Table:
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


def create_cost_breakdown(cost_data: dict[str, Any]) -> Panel:
    """Create a visual cost breakdown."""
    lines = []

    total_cost = cost_data.get("total", 0)
    lines.append(f"Total Cost: [bold]${total_cost:.4f}[/bold]\n")

    # Token usage
    if "tokens" in cost_data:
        tokens = cost_data["tokens"]
        if isinstance(tokens, dict):
            lines.append("Token Usage:")
            lines.append(f"  • Input:  {tokens.get('input', 0):,}")
            lines.append(f"  • Output: {tokens.get('output', 0):,}")
            lines.append(f"  • Total:  {tokens.get('total', 0):,}")

    # Cost projections
    if "projections" in cost_data:
        lines.append("\nProjected Costs:")
        proj = cost_data["projections"]
        if isinstance(proj, dict):
            lines.append(f"  • Hourly:   ${proj.get('hourly', 0):.2f}")
            lines.append(f"  • Daily:    ${proj.get('daily', 0):.2f}")
            lines.append(f"  • Monthly:  ${proj.get('monthly', 0):.2f}")

    return Panel(
        "\n".join(lines), title="Cost Analysis", border_style="yellow", box=MINIMAL, padding=(1, 2)
    )


def create_live_progress(task_name: str) -> Progress:
    """Create a live progress display for running evaluations."""
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{task_name}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("[dim]{task.elapsed:.1f}s elapsed"),
        console=console,
        transient=True,
    )


def create_comparison_table(agents: list[str], results: dict[str, dict[str, float]]) -> Table:
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
    results: dict[str, Any],
    show_details: bool = True,
    show_suggestions: bool = True,
    show_costs: bool = True,
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


def create_llm_evaluation_panel(
    input_text: str,
    expected_output: str,
    actual_output: str,
    score: float,
    feedback: str,
    rubric: str = "factual",
    score_breakdown: dict[str, float] = None,
    tokens: dict[str, int] | None = None,
    cost: float | None = None,
) -> Panel:
    """Create LLM evaluation panel with full input/output visibility."""

    # Score visualization
    score_color = get_score_color(score)
    score_bar = create_score_bar(score, width=30)

    panel_content = []

    # Evaluation methodology
    panel_content.append("[bold magenta]EVALUATION METHODOLOGY:[/bold magenta]")
    panel_content.append(f"Rubric: {rubric.upper()}")
    panel_content.append("Judge Model: GPT-4 (LLM-as-Judge)")
    panel_content.append("Evaluation Type: Semantic similarity and quality assessment")
    panel_content.append("")

    # Input section
    panel_content.append("[bold cyan]USER INPUT:[/bold cyan]")
    panel_content.append(f"{input_text}")
    panel_content.append("")
    panel_content.append("[dim]↑ Input provided to agent under evaluation[/dim]")
    panel_content.append("")

    # Expected vs Actual comparison
    panel_content.append("[bold green]EXPECTED OUTPUT:[/bold green]")
    panel_content.append(f"{expected_output}")
    panel_content.append("")
    panel_content.append("[dim]↑ Target response for this evaluation[/dim]")
    panel_content.append("")

    panel_content.append("[bold yellow]AGENT OUTPUT:[/bold yellow]")
    panel_content.append(f"{actual_output}")
    panel_content.append("")
    panel_content.append("[dim]↑ Response generated by agent[/dim]")
    panel_content.append("")

    # LLM Judge evaluation process
    panel_content.append("[bold blue]LLM JUDGE PROCESS:[/bold blue]")
    panel_content.append("1. Input Analysis: Analyzed user input for context and requirements")
    panel_content.append("2. Response Comparison: Compared agent output against expected output")
    panel_content.append(f"3. Quality Assessment: Evaluated response using {rubric} criteria")
    panel_content.append("4. Score Calculation: Assigned numerical scores based on rubric")
    panel_content.append("")

    # Token usage and cost tracking
    if tokens or cost:
        panel_content.append("[bold magenta]EVALUATION USAGE:[/bold magenta]")
        if tokens:
            total_tokens = tokens.get("total", 0)
            input_tokens = tokens.get("input", 0)
            output_tokens = tokens.get("output", 0)
            panel_content.append(
                f"Total Tokens: {total_tokens:,} (Input: {input_tokens:,}, Output: {output_tokens:,})"
            )
        if cost:
            panel_content.append(f"Estimated Cost: ${cost:.4f}")
        panel_content.append("")

    # Final score
    panel_content.append(f"[bold]FINAL SCORE ({rubric.upper()} RUBRIC):[/bold]")
    panel_content.append(f"{score_bar} [{score_color}]{score:.3f}[/{score_color}] ({score:.1%})")
    panel_content.append("")

    # Score breakdown if available
    if score_breakdown:
        panel_content.append("[bold]SCORE BREAKDOWN:[/bold]")
        panel_content.append("[dim]Individual criterion scores:[/dim]")
        for criterion, criterion_score in score_breakdown.items():
            criterion_color = get_score_color(criterion_score)
            criterion_bar = create_score_bar(criterion_score, width=25)
            criterion_name = criterion.replace("_", " ").title()
            panel_content.append(
                f"  {criterion_name:<15}: {criterion_bar} [{criterion_color}]{criterion_score:.3f}[/{criterion_color}]"
            )
        panel_content.append("")

    # LLM Judge reasoning
    panel_content.append("[bold blue]LLM JUDGE REASONING:[/bold blue]")
    panel_content.append("[dim]Explanation of scoring decisions:[/dim]")
    panel_content.append("")
    panel_content.append(f"{feedback}")
    panel_content.append("")
    panel_content.append("[dim]↑ How the LLM judge arrived at the scores above[/dim]")

    return Panel(
        "\n".join(panel_content),
        title="LLM EVALUATION ANALYSIS",
        border_style=score_color,
        box=ROUNDED,
        padding=(1, 3),
        width=120,
    )


def create_performance_metrics_panel(
    latency_ms: float,
    tokens: dict[str, int] | None = None,
    cost: float | None = None,
    memory_usage: float | None = None,
    detailed_metrics: dict[str, Any] | None = None,
) -> Panel:
    """Create a panel showing comprehensive performance metrics with context."""
    lines = []

    # Latency analysis with detailed context
    if latency_ms < 200:
        latency_color = "green"
        latency_status = "Excellent - Sub-200ms response"
        latency_context = "Real-time user experience"
    elif latency_ms < 500:
        latency_color = "yellow"
        latency_status = "Good - Under 500ms"
        latency_context = "Acceptable for most applications"
    elif latency_ms < 1000:
        latency_color = "orange1"
        latency_status = "Moderate - Under 1s"
        latency_context = "Noticeable delay, consider optimization"
    else:
        latency_color = "red"
        latency_status = "Slow - Over 1s"
        latency_context = "Poor user experience, needs optimization"

    lines.append("[bold]Response Time Analysis:[/bold]")
    lines.append(f"Time: [{latency_color}]{latency_ms:.1f}ms[/{latency_color}] - {latency_status}")
    lines.append(f"Impact: {latency_context}")
    lines.append("")

    # Detailed performance metrics if available
    if detailed_metrics:
        lines.append("[bold]Detailed Performance:[/bold]")

        # Latency statistics
        if "latency" in detailed_metrics:
            lat_stats = detailed_metrics["latency"]
            lines.append(f"  Mean: {lat_stats.get('mean_ms', 0):.1f}ms")
            lines.append(f"  P95: {lat_stats.get('p95_ms', 0):.1f}ms")
            lines.append(f"  Std Dev: {lat_stats.get('std_dev_ms', 0):.1f}ms")

        # Memory statistics
        if "memory" in detailed_metrics:
            mem_stats = detailed_metrics["memory"]
            lines.append(f"  Memory (Mean): {mem_stats.get('mean_mb', 0):.2f}MB")
            lines.append(f"  Memory (Peak): {mem_stats.get('max_mb', 0):.2f}MB")

        # Performance feedback
        if "feedback" in detailed_metrics:
            lines.append(f"  Assessment: {detailed_metrics['feedback']}")

        lines.append("")

    # Token usage analysis with efficiency context
    if tokens:
        total_tokens = tokens.get("total", 0)
        input_tokens = tokens.get("input", 0)
        output_tokens = tokens.get("output", 0)

        lines.append("[bold]Token Usage Analysis:[/bold]")
        lines.append(f"Total: {total_tokens:,} tokens")
        lines.append(f"  • Input: {input_tokens:,} tokens")
        lines.append(f"  • Output: {output_tokens:,} tokens")

        # Token efficiency analysis
        if input_tokens > 0:
            output_ratio = output_tokens / input_tokens
            if output_ratio < 0.5:
                efficiency_status = "Concise responses"
                efficiency_color = "green"
            elif output_ratio < 2.0:
                efficiency_status = "Balanced verbosity"
                efficiency_color = "yellow"
            else:
                efficiency_status = "Verbose responses"
                efficiency_color = "orange1"

            lines.append(
                f"Efficiency: [{efficiency_color}]{output_ratio:.1f}x output/input ratio[/{efficiency_color}] - {efficiency_status}"
            )

        lines.append("")

    # Cost analysis with projections
    if cost is not None:
        lines.append("[bold]Cost Analysis:[/bold]")
        lines.append(f"This Query: [bold]${cost:.4f}[/bold]")

        # Cost projections
        hourly_cost = cost * 100  # Assume 100 queries/hour
        daily_cost = hourly_cost * 24
        monthly_cost = daily_cost * 30

        lines.append("Projections (at current rate):")
        lines.append(f"  • 100 queries: ${hourly_cost:.2f}")
        lines.append(f"  • Daily: ${daily_cost:.2f}")
        lines.append(f"  • Monthly: ${monthly_cost:.2f}")
        lines.append("")

    # Memory usage analysis
    if memory_usage is not None:
        lines.append("[bold]Memory Usage:[/bold]")
        if memory_usage < 50:
            memory_status = "Efficient"
            memory_color = "green"
        elif memory_usage < 200:
            memory_status = "Moderate"
            memory_color = "yellow"
        else:
            memory_status = "High usage"
            memory_color = "red"

        lines.append(
            f"Usage: [{memory_color}]{memory_usage:.1f}MB[/{memory_color}] - {memory_status}"
        )

    return Panel(
        "\n".join(lines),
        title="Performance Analysis",
        border_style="blue",
        box=ROUNDED,
        padding=(1, 2),
    )


def create_reliability_assessment_panel(
    expected_tools: list[str],
    actual_tools: list[str],
    consistency_score: float,
    error_rate: float = 0.0,
    tool_calls_details: list[dict[str, Any]] = None,
    event_statistics: dict[str, int] = None,
) -> Panel:
    """Create a panel showing comprehensive reliability assessment with execution traces."""
    lines = []

    # Tool usage analysis with execution details
    if expected_tools or actual_tools:
        lines.append("[bold]Tool Usage Analysis:[/bold]")

        # Expected tools analysis
        if expected_tools:
            for tool in expected_tools:
                if tool in actual_tools:
                    lines.append(f"  [green]✓[/green] {tool} - Used correctly")
                else:
                    lines.append(f"  [red]✗[/red] {tool} - Missing (expected but not used)")

        # Unexpected tools
        unexpected = [t for t in actual_tools if t not in expected_tools]
        if unexpected:
            lines.append("  [yellow]Unexpected tools used:[/yellow]")
            for tool in unexpected:
                lines.append(f"    • {tool} (used but not expected)")

        # Detailed tool execution trace
        if tool_calls_details:
            lines.append("")
            lines.append("[bold]Tool Execution Trace:[/bold]")
            for i, call in enumerate(tool_calls_details):
                tool_name = call.get("tool", "Unknown")
                status = call.get("status", "unknown")
                timestamp = call.get("timestamp", "N/A")

                status_icon = "✓" if status == "success" else "✗" if status == "error" else "~"
                status_color = (
                    "green" if status == "success" else "red" if status == "error" else "yellow"
                )

                lines.append(
                    f"  {i + 1}. [{status_color}]{status_icon}[/{status_color}] {tool_name}"
                )
                if timestamp != "N/A":
                    lines.append(f"     Time: {timestamp}")
                if "confidence" in call:
                    lines.append(f"     Confidence: {call['confidence']}")

        lines.append("")

    # Reliability metrics
    lines.append("[bold]Reliability Metrics:[/bold]")

    # Consistency score
    consistency_color = get_score_color(consistency_score)
    consistency_bar = create_score_bar(consistency_score)
    lines.append(
        f"Consistency: {consistency_bar} [{consistency_color}]{consistency_score:.3f}[/{consistency_color}]"
    )

    # Error rate analysis
    if error_rate > 0:
        error_color = "red" if error_rate > 0.1 else "orange1" if error_rate > 0.05 else "yellow"
        error_status = (
            "Critical" if error_rate > 0.1 else "Concerning" if error_rate > 0.05 else "Acceptable"
        )
        lines.append(
            f"Error Rate: [{error_color}]{error_rate:.1%}[/{error_color}] - {error_status}"
        )
    else:
        lines.append("Error Rate: [green]0.0%[/green] - Excellent")

    # Coverage analysis
    if expected_tools:
        coverage = len([t for t in expected_tools if t in actual_tools]) / len(expected_tools)
        coverage_color = get_score_color(coverage)
        coverage_bar = create_score_bar(coverage)
        lines.append(
            f"Tool Coverage: {coverage_bar} [{coverage_color}]{coverage:.1%}[/{coverage_color}]"
        )

    lines.append("")

    # Event statistics if available
    if event_statistics:
        lines.append("[bold]Event Statistics:[/bold]")
        total_events = sum(event_statistics.values())
        lines.append(f"Total Events: {total_events}")

        for event_type, count in sorted(event_statistics.items()):
            percentage = (count / total_events * 100) if total_events > 0 else 0
            lines.append(f"  • {event_type}: {count} ({percentage:.1f}%)")

    return Panel(
        "\n".join(lines),
        title="Comprehensive Reliability Analysis",
        border_style="purple",
        box=ROUNDED,
        padding=(1, 2),
    )


def display_single_evaluation_result(
    evaluation_type: str,
    agent_identifier: str,
    input_text: str,
    result: Any,
    show_details: bool = True,
    show_performance: bool = True,
) -> None:
    """Display a comprehensive single evaluation result with clear evaluation dimension breakdown."""

    # Header with evaluation type
    header_title = f"{evaluation_type.title()} Evaluation Result"
    console.print(create_evaluation_header(header_title))
    console.print()

    # Agent and input summary
    summary_lines = [
        f"[bold]Agent:[/bold] {agent_identifier}",
        f"[bold]Input:[/bold] {input_text[:100]}{'...' if len(input_text) > 100 else ''}",
    ]

    console.print(
        Panel(
            "\n".join(summary_lines),
            title="Evaluation Context",
            border_style="cyan",
            box=MINIMAL,
            padding=(1, 2),
        )
    )
    console.print()

    # Create clear evaluation dimension scores
    score = getattr(result, "score", 0.0)
    passed = getattr(result, "passed", False)
    details = getattr(result, "details", {})

    # Build comprehensive score breakdown based on evaluation type and available data
    score_data = {}

    # Primary score for this evaluation type - clearly labeled by dimension
    if evaluation_type.lower() == "accuracy":
        score_data["Accuracy Score"] = score

        # Add LLM criteria breakdown if available
        if details and "scores" in details:
            llm_scores = details["scores"]
            if isinstance(llm_scores, dict):
                for criterion, criterion_score in llm_scores.items():
                    if criterion not in ["accuracy", "main_score", "overall"]:  # Avoid duplication
                        criterion_name = criterion.replace("_", " ").title()
                        # Prefix with evaluation type for clarity
                        score_data[f"  {criterion_name}"] = criterion_score

        # Add performance context if available
        if details.get("latency_ms", 0) > 0:
            latency_ms = details["latency_ms"]
            if latency_ms < 200:
                perf_score = 1.0
            elif latency_ms < 1000:
                perf_score = 0.8
            else:
                perf_score = 0.5
            score_data["  Response Speed"] = perf_score

    elif evaluation_type.lower() == "performance":
        score_data["Performance Score"] = score

        # Break down performance metrics
        if details:
            # Extract latency from nested structure if available
            latency_ms = details.get("latency_ms", 0)
            if latency_ms == 0 and "latency" in details:
                latency_stats = details["latency"]
                if isinstance(latency_stats, dict):
                    latency_ms = latency_stats.get("mean_ms", 0)

            if latency_ms > 0:
                if latency_ms < 200:
                    score_data["  Response Time"] = 1.0
                elif latency_ms < 500:
                    score_data["  Response Time"] = 0.8
                elif latency_ms < 1000:
                    score_data["  Response Time"] = 0.6
                else:
                    score_data["  Response Time"] = 0.3

            # Token efficiency if available
            if "tokens" in details or hasattr(result, "tokens"):
                tokens = details.get("tokens") or getattr(result, "tokens", None)
                if tokens and isinstance(tokens, dict):
                    input_tokens = tokens.get("input", 0)
                    output_tokens = tokens.get("output", 0)
                    if input_tokens > 0:
                        ratio = output_tokens / input_tokens
                        if ratio < 1.0:
                            score_data["  Token Efficiency"] = 1.0
                        elif ratio < 3.0:
                            score_data["  Token Efficiency"] = 0.8
                        else:
                            score_data["  Token Efficiency"] = 0.5

            # Memory efficiency if available
            if "memory" in details:
                memory_stats = details["memory"]
                if isinstance(memory_stats, dict) and "max_mb" in memory_stats:
                    max_memory = memory_stats["max_mb"]
                    if max_memory < 50:
                        score_data["  Memory Usage"] = 1.0
                    elif max_memory < 200:
                        score_data["  Memory Usage"] = 0.8
                    else:
                        score_data["  Memory Usage"] = 0.5

    elif evaluation_type.lower() == "reliability":
        score_data["Reliability Score"] = score

        # Break down reliability metrics
        if details:
            # Tool usage accuracy
            expected_tools = details.get("expected_tools", [])
            actual_tools = details.get(
                "tools_used", []
            )  # Reliability evaluator uses 'tools_used' key
            if expected_tools:
                tool_coverage = len([t for t in expected_tools if t in actual_tools]) / len(
                    expected_tools
                )
                score_data["  Tool Usage"] = tool_coverage

            # Consistency score
            consistency_score = details.get("consistency_score")
            if consistency_score is not None:
                score_data["  Consistency"] = consistency_score

            # Error handling
            error_rate = details.get("error_rate", 0.0)
            error_handling_score = max(0.0, 1.0 - error_rate)
            score_data["  Error Handling"] = error_handling_score

    console.print(create_score_summary(score_data))
    console.print()

    # LLM Evaluation Details (for accuracy evaluations)
    if evaluation_type.lower() == "accuracy" and show_details:
        details = getattr(result, "details", {})
        metadata = getattr(result, "metadata", {})

        expected_output = metadata.get("expected", "N/A")
        actual_output = metadata.get("response", "N/A")
        feedback = details.get("feedback", "No feedback available")

        # Get score breakdown if available
        score_breakdown = details.get("scores", {})

        llm_panel = create_llm_evaluation_panel(
            input_text=input_text,
            expected_output=expected_output,
            actual_output=actual_output,
            score=score,
            feedback=feedback,
            rubric=getattr(result, "rubric", "factual"),
            score_breakdown=score_breakdown if score_breakdown else None,
            tokens=getattr(result, "tokens", None),
            cost=getattr(result, "cost", None),
        )
        console.print(llm_panel)
        console.print()

    # Performance Metrics
    if show_performance:
        details = getattr(result, "details", {})

        # Extract latency from details structure (performance eval has nested latency stats)
        latency_ms = details.get("latency_ms", 0)
        if latency_ms == 0 and "latency" in details:
            latency_stats = details["latency"]
            if isinstance(latency_stats, dict):
                latency_ms = latency_stats.get("mean_ms", 0)

        tokens = getattr(result, "tokens", None)
        cost = getattr(result, "cost", None)

        # Show performance panel if we have any performance data
        if latency_ms > 0 or tokens or cost or "latency" in details or "memory" in details:
            perf_panel = create_performance_metrics_panel(
                latency_ms=latency_ms, tokens=tokens, cost=cost, detailed_metrics=details
            )
            console.print(perf_panel)
            console.print()

    # Reliability Details (for reliability evaluations)
    if evaluation_type.lower() == "reliability" and show_details:
        details = getattr(result, "details", {})

        expected_tools = details.get("expected_tools", [])
        actual_tools = details.get("tools_used", [])  # Reliability evaluator uses 'tools_used' key
        consistency_score = details.get("consistency_score", score)
        error_rate = details.get("error_rate", 0.0)

        if expected_tools or actual_tools:
            # Get additional reliability details
            tool_calls_details = details.get("tool_calls", [])
            event_statistics = details.get("event_statistics", {})

            reliability_panel = create_reliability_assessment_panel(
                expected_tools=expected_tools,
                actual_tools=actual_tools,
                consistency_score=consistency_score,
                error_rate=error_rate,
                tool_calls_details=tool_calls_details,
                event_statistics=event_statistics,
            )
            console.print(reliability_panel)
            console.print()

    # Final status
    status_color = "green" if passed else "red"
    status_text = "PASSED" if passed else "FAILED"

    console.print(
        Panel(
            f"[{status_color}]{status_text}[/{status_color}]",
            title="Final Result",
            border_style=status_color,
            box=DOUBLE,
            padding=(0, 2),
        )
    )


def create_comprehensive_evaluation_summary(
    accuracy_result: Any = None,
    performance_result: Any = None,
    reliability_result: Any = None,
    agent_identifier: str = "Agent",
) -> Panel:
    """Create a unified summary showing all three evaluation dimensions with score bars."""

    lines = []

    # Agent identification
    lines.append(f"[bold cyan]Agent:[/bold cyan] {agent_identifier}")
    lines.append("")

    # Collect all scores
    all_scores = {}

    # Accuracy scores
    if accuracy_result:
        accuracy_score = getattr(accuracy_result, "score", 0.0)
        all_scores["Accuracy"] = accuracy_score

        # Add sub-scores if available
        details = getattr(accuracy_result, "details", {})
        if details and "scores" in details:
            llm_scores = details["scores"]
            if isinstance(llm_scores, dict):
                for criterion, score in llm_scores.items():
                    if criterion not in ["accuracy", "main_score", "overall"]:
                        criterion_name = criterion.replace("_", " ").title()
                        all_scores[f"  {criterion_name}"] = score

    # Performance scores
    if performance_result:
        performance_score = getattr(performance_result, "score", 0.0)
        all_scores["Performance"] = performance_score

        # Add performance breakdowns
        details = getattr(performance_result, "details", {})
        if details:
            latency_ms = details.get("latency_ms", 0)
            if latency_ms > 0:
                if latency_ms < 200:
                    response_score = 1.0
                elif latency_ms < 500:
                    response_score = 0.8
                elif latency_ms < 1000:
                    response_score = 0.6
                else:
                    response_score = 0.3
                all_scores["  Response Time"] = response_score

            # Token efficiency
            tokens = getattr(performance_result, "tokens", None) or details.get("tokens")
            if tokens and isinstance(tokens, dict):
                input_tokens = tokens.get("input", 0)
                output_tokens = tokens.get("output", 0)
                if input_tokens > 0:
                    ratio = output_tokens / input_tokens
                    if ratio < 1.0:
                        efficiency_score = 1.0
                    elif ratio < 3.0:
                        efficiency_score = 0.8
                    else:
                        efficiency_score = 0.5
                    all_scores["  Token Efficiency"] = efficiency_score

    # Reliability scores
    if reliability_result:
        reliability_score = getattr(reliability_result, "score", 0.0)
        all_scores["Reliability"] = reliability_score

        # Add reliability breakdowns
        details = getattr(reliability_result, "details", {})
        if details:
            # Tool usage
            expected_tools = details.get("expected_tools", [])
            actual_tools = details.get(
                "tools_used", []
            )  # Reliability evaluator uses 'tools_used' key
            if expected_tools:
                tool_coverage = len([t for t in expected_tools if t in actual_tools]) / len(
                    expected_tools
                )
                all_scores["  Tool Usage"] = tool_coverage

            # Consistency
            consistency_score = details.get("consistency_score")
            if consistency_score is not None:
                all_scores["  Consistency"] = consistency_score

            # Error handling
            error_rate = details.get("error_rate", 0.0)
            error_handling_score = max(0.0, 1.0 - error_rate)
            all_scores["  Error Handling"] = error_handling_score

    # Display all scores with bars
    if all_scores:
        lines.append("[bold]Evaluation Breakdown:[/bold]")
        lines.append("")

        for metric, score in all_scores.items():
            color = get_score_color(score)
            bar = create_score_bar(score, width=20)

            # Main dimensions get bold formatting
            if not metric.startswith("  "):
                lines.append(f"[bold]{metric}[/bold]")
                lines.append(f"{bar} [{color}]{score:.3f}[/{color}] ({score:.1%})")
                lines.append("")
            else:
                # Sub-scores with indentation
                lines.append(f"{metric:<18} {bar} [{color}]{score:.3f}[/{color}]")
    else:
        lines.append("[yellow]No evaluation results available[/yellow]")

    # Overall assessment
    if all_scores:
        main_scores = [score for metric, score in all_scores.items() if not metric.startswith("  ")]
        if main_scores:
            overall_score = sum(main_scores) / len(main_scores)
            overall_color = get_score_color(overall_score)
            overall_bar = create_score_bar(overall_score, width=25)

            lines.append("")
            lines.append("[bold]Overall Assessment:[/bold]")
            lines.append(
                f"{overall_bar} [{overall_color}]{overall_score:.3f}[/{overall_color}] ({overall_score:.1%})"
            )

    return Panel(
        "\n".join(lines),
        title="AGENT EVALUATION DASHBOARD",
        border_style="cyan",
        box=DOUBLE,
        padding=(1, 3),
        width=120,
    )


def display_comprehensive_evaluation_results(
    accuracy_result: Any = None,
    performance_result: Any = None,
    reliability_result: Any = None,
    agent_identifier: str = "Agent",
    show_individual_details: bool = False,
) -> None:
    """Display a master interface showing all evaluation dimensions together."""

    # Header
    console.print(create_evaluation_header("AGENT EVALUATION REPORT"))
    console.print()

    # Comprehensive summary with all scores
    summary_panel = create_comprehensive_evaluation_summary(
        accuracy_result=accuracy_result,
        performance_result=performance_result,
        reliability_result=reliability_result,
        agent_identifier=agent_identifier,
    )
    console.print(summary_panel)
    console.print()

    # Show individual details if requested
    if show_individual_details:
        if accuracy_result:
            console.print("[bold cyan]ACCURACY ANALYSIS:[/bold cyan]")
            display_single_evaluation_result(
                evaluation_type="accuracy",
                agent_identifier=agent_identifier,
                input_text=getattr(accuracy_result, "metadata", {}).get("input", "N/A"),
                result=accuracy_result,
                show_details=True,
                show_performance=False,
            )
            console.print()

        if performance_result:
            console.print("[bold blue]PERFORMANCE ANALYSIS:[/bold blue]")
            display_single_evaluation_result(
                evaluation_type="performance",
                agent_identifier=agent_identifier,
                input_text=getattr(performance_result, "metadata", {}).get("input", "N/A"),
                result=performance_result,
                show_details=True,
                show_performance=True,
            )
            console.print()

        if reliability_result:
            console.print("[bold purple]RELIABILITY ANALYSIS:[/bold purple]")
            display_single_evaluation_result(
                evaluation_type="reliability",
                agent_identifier=agent_identifier,
                input_text=getattr(reliability_result, "metadata", {}).get("input", "N/A"),
                result=reliability_result,
                show_details=True,
                show_performance=False,
            )

    # Final status
    results = [
        r for r in [accuracy_result, performance_result, reliability_result] if r is not None
    ]
    if results:
        all_passed = all(getattr(r, "passed", False) for r in results)
        status_color = "green" if all_passed else "red"
        status_text = "ALL EVALUATIONS PASSED" if all_passed else "SOME EVALUATIONS FAILED"

        console.print(
            Panel(
                f"[{status_color}]{status_text}[/{status_color}]",
                title="FINAL ASSESSMENT",
                border_style=status_color,
                box=DOUBLE,
                padding=(0, 2),
                width=120,
            )
        )


def create_workflow_timeline(steps: list[dict[str, Any]]) -> None:
    """Display a timeline of workflow steps."""
    panels = []

    for i, step in enumerate(steps):
        status_color = (
            "green" if step["passed"] else "red" if step["status"] == "failed" else "yellow"
        )
        status_icon = "✓" if step["passed"] else "✗" if step["status"] == "failed" else "..."

        panel_content = [
            f"[{status_color}]{status_icon}[/{status_color}] Step {i + 1}",
            f"{step['name']}",
            f"Duration: {step.get('duration', 0):.2f}s",
        ]

        if step.get("error"):
            panel_content.append(f"[red]Error: {step['error']}[/red]")

        panel = Panel(
            "\n".join(panel_content), style=status_color, box=MINIMAL, expand=False, padding=(0, 1)
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
    "create_workflow_timeline",
    "create_llm_evaluation_panel",
    "create_performance_metrics_panel",
    "create_reliability_assessment_panel",
    "display_single_evaluation_result",
    "create_comprehensive_evaluation_summary",
    "display_comprehensive_evaluation_results",
]
