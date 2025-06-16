"""Traces command for production trace ingestion and analysis."""

import json

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ...benchmarks.datasets.trace_recycler import TraceRecycler

console = Console()


@click.group()
def traces():
    """Manage production traces for evaluation."""
    pass


@traces.command()
@click.argument("trace_file", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["auto", "otel", "acp"]), default="auto")
@click.option("--validate", "-v", is_flag=True, help="Validate trace format")
def ingest(trace_file: str, format: str, validate: bool):
    """Ingest traces from a file.


    Examples:
        acp-evals traces ingest production-traces.json
        acp-evals traces ingest agent-traces.json --format acp
        acp-evals traces ingest traces.json --validate
    """
    console.print(f"[bold]Ingesting traces from:[/bold] {trace_file}")

    recycler = TraceRecycler()

    try:
        # Load traces
        with open(trace_file) as f:
            data = json.load(f)

        # Handle different formats
        if isinstance(data, dict) and "traces" in data:
            traces = data["traces"]
        elif isinstance(data, list):
            traces = data
        else:
            traces = [data]

        console.print(f"Found [cyan]{len(traces)}[/cyan] traces")

        # Ingest with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Ingesting traces...", total=len(traces))

            for trace in traces:
                if format == "auto":
                    # Auto-detect format
                    if "spans" in trace or "resource" in trace:
                        detected_format = "otel"
                    else:
                        detected_format = "acp"
                else:
                    detected_format = format

                if detected_format == "otel":
                    recycler.ingest_trace(trace)
                else:
                    # Convert ACP to OTel format
                    recycler.ingest_trace(recycler.convert_acp_trace(trace))

                progress.advance(task)

        # Show summary
        total_traces = len(recycler.traces)
        patterns = recycler.detect_patterns()

        console.print("\n[green]Successfully ingested traces[/green]")
        console.print(f"Total traces in recycler: {total_traces}")
        console.print(f"Patterns detected: {len(patterns)}")

        if validate:
            console.print("\n[bold]Validation Results:[/bold]")
            valid = 0
            for trace in recycler.traces:
                if trace.get("spans") and len(trace["spans"]) > 0:
                    valid += 1
            console.print(f"Valid traces: {valid}/{total_traces}")

    except Exception as e:
        console.print(f"[red]Error ingesting traces: {e}[/red]")
        exit(1)


@traces.command()
@click.option("--output", "-o", required=True, help="Output dataset file")
@click.option("--count", "-c", type=int, default=100, help="Number of examples to generate")
@click.option("--quality-threshold", "-q", type=float, default=0.7, help="Minimum quality score")
@click.option("--format", "-f", type=click.Choice(["json", "jsonl"]), default="jsonl")
def recycle(output: str, count: int, quality_threshold: float, format: str):
    """Recycle traces into evaluation datasets.


    Examples:
        acp-evals traces recycle -o eval-dataset.jsonl
        acp-evals traces recycle -o dataset.json -c 50 -q 0.8
    """
    console.print("[bold]Recycling traces into evaluation dataset[/bold]\n")

    recycler = TraceRecycler()

    # Check if we have traces
    if not recycler.traces:
        console.print("[yellow]No traces found. Run 'acp-evals traces ingest' first.[/yellow]")
        exit(1)

    console.print(f"Total traces available: {len(recycler.traces)}")

    try:
        # Generate dataset
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating dataset...", total=1)

            dataset = recycler.generate_dataset(
                count=count, quality_threshold=quality_threshold, format=format
            )

            progress.advance(task)

        # Save dataset
        with open(output, "w") as f:
            if format == "jsonl":
                for item in dataset:
                    f.write(json.dumps(item) + "\n")
            else:
                json.dump(dataset, f, indent=2)

        console.print(f"\n[green]Generated {len(dataset)} evaluation examples[/green]")
        console.print(f"Saved to: {output}")

        # Show quality distribution
        quality_scores = [item.get("_quality_score", 0) for item in dataset]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            console.print(f"\nAverage quality score: {avg_quality:.2f}")

    except Exception as e:
        console.print(f"[red]Error recycling traces: {e}[/red]")
        exit(1)


@traces.command()
@click.option("--export", "-e", help="Export patterns to file")
@click.option("--min-frequency", "-m", type=int, default=2, help="Minimum pattern frequency")
def patterns(export: str | None, min_frequency: int):
    """Detect and analyze trace patterns.


    Examples:
        acp-evals traces patterns
        acp-evals traces patterns --export patterns.json
        acp-evals traces patterns --min-frequency 5
    """
    console.print("[bold]Analyzing trace patterns[/bold]\n")

    recycler = TraceRecycler()

    if not recycler.traces:
        console.print("[yellow]No traces found. Run 'acp-evals traces ingest' first.[/yellow]")
        exit(1)

    # Detect patterns
    patterns = recycler.detect_patterns()

    # Filter by frequency
    filtered_patterns = {
        sig: data for sig, data in patterns.items() if data["frequency"] >= min_frequency
    }

    console.print(
        f"Found [cyan]{len(filtered_patterns)}[/cyan] patterns (min frequency: {min_frequency})"
    )

    # Display patterns
    table = Table(title="Trace Patterns")
    table.add_column("Pattern", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Frequency", style="green")
    table.add_column("Avg Duration", style="magenta")
    table.add_column("Operations", style="white")

    for sig, data in sorted(
        filtered_patterns.items(), key=lambda x: x[1]["frequency"], reverse=True
    )[:10]:
        ops = ", ".join(data["characteristics"]["operations"][:3])
        if len(data["characteristics"]["operations"]) > 3:
            ops += f" (+{len(data['characteristics']['operations']) - 3} more)"

        table.add_row(
            sig[:20] + "...",
            data["type"],
            str(data["frequency"]),
            f"{data['characteristics']['avg_duration']:.2f}s",
            ops,
        )

    console.print(table)

    # Export if requested
    if export:
        export_data = recycler.export_patterns()
        with open(export, "w") as f:
            json.dump(export_data, f, indent=2)

        console.print(f"\n[green]Patterns exported to:[/green] {export}")

    # Show pattern distribution
    pattern_types = {}
    for data in filtered_patterns.values():
        pattern_types[data["type"]] = pattern_types.get(data["type"], 0) + 1

    console.print("\n[bold]Pattern Distribution:[/bold]")
    for ptype, count in pattern_types.items():
        console.print(f"  {ptype}: {count}")


@traces.command()
@click.argument("baseline_file", type=click.Path(exists=True))
@click.argument("current_file", type=click.Path(exists=True))
@click.option("--report", "-r", help="Save regression report")
def regression(baseline_file: str, current_file: str, report: str | None):
    """Compare baseline traces with current traces for regressions.


    Examples:
        acp-evals traces regression baseline.json current.json
        acp-evals traces regression v1.0-traces.json v2.0-traces.json --report regression.txt
    """
    console.print("[bold]Running regression analysis[/bold]\n")

    recycler = TraceRecycler()

    try:
        # Load baseline traces
        with open(baseline_file) as f:
            baseline_data = json.load(f)

        baseline_traces = (
            baseline_data if isinstance(baseline_data, list) else baseline_data.get("traces", [])
        )

        # Load current traces
        with open(current_file) as f:
            current_data = json.load(f)

        current_traces = (
            current_data if isinstance(current_data, list) else current_data.get("traces", [])
        )

        console.print(f"Baseline traces: {len(baseline_traces)}")
        console.print(f"Current traces: {len(current_traces)}")

        # Detect regressions
        regressions = recycler.detect_regressions(baseline_traces, current_traces)

        if not regressions:
            console.print("\n[green]No regressions detected![/green]")
        else:
            console.print(f"\n[red]Found {len(regressions)} regressions[/red]\n")

            # Display regressions
            for reg in regressions[:5]:  # Show first 5
                console.print(f"[bold]Pattern:[/bold] {reg['pattern_signature'][:40]}...")
                console.print(f"  Type: {reg['regression_type']}")
                console.print(f"  Baseline: {reg['baseline_value']:.2f}")
                console.print(f"  Current: {reg['current_value']:.2f}")
                console.print(f"  Change: {reg['change']:.1%}\n")

            if len(regressions) > 5:
                console.print(f"[dim]... and {len(regressions) - 5} more regressions[/dim]")

        # Save report if requested
        if report:
            report_data = {
                "baseline_file": baseline_file,
                "current_file": current_file,
                "baseline_traces": len(baseline_traces),
                "current_traces": len(current_traces),
                "regressions": regressions,
            }

            with open(report, "w") as f:
                json.dump(report_data, f, indent=2)

            console.print(f"\n[green]Report saved to:[/green] {report}")

    except Exception as e:
        console.print(f"[red]Error analyzing regressions: {e}[/red]")
        exit(1)


if __name__ == "__main__":
    traces()
