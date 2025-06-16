"""Dataset command for managing evaluation datasets."""

import json
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...benchmarks.datasets import gold_standard_datasets
from ...benchmarks.datasets.dataset_loader import DatasetLoader


def validate_file_path(file_path: str, allowed_extensions: set = None) -> str:
    """Validate file path to prevent directory traversal attacks."""
    if not file_path:
        return ""

    # Convert to Path object for safer handling
    path = Path(file_path).resolve()

    # Prevent directory traversal - keep within reasonable bounds
    try:
        path.relative_to(Path.cwd().parent.parent)  # Allow up to 2 levels up
    except ValueError:
        # If path is outside allowed area, use just the filename in current dir
        path = Path.cwd() / Path(file_path).name

    # Validate extension if specified
    if allowed_extensions and path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Invalid file extension. Allowed: {allowed_extensions}")

    return str(path)


console = Console()


@click.group()
def dataset():
    """Manage evaluation datasets."""
    pass


@dataset.command()
@click.option("--path", "-p", default="datasets", help="Path to datasets directory")
def local(path: str):
    """List locally generated synthetic datasets.

    Examples:
        acp-evals dataset local
        acp-evals dataset local --path ./my-datasets
    """
    datasets_dir = Path(path)

    if not datasets_dir.exists():
        console.print(f"[yellow]No datasets directory found at: {path}[/yellow]")
        console.print("[dim]Generate datasets using: acp-evals generate tests[/dim]")
        return

    console.print("[bold cyan]Local Synthetic Datasets[/bold cyan]")
    console.print(f"Directory: {datasets_dir.absolute()}\n")

    # Find all dataset files
    dataset_files = list(datasets_dir.glob("*.json")) + list(datasets_dir.glob("*.jsonl"))

    if not dataset_files:
        console.print("[yellow]No datasets found.[/yellow]")
        console.print("[dim]Generate datasets using: acp-evals generate tests[/dim]")
        return

    # Create table
    table = Table(title="Generated Datasets")
    table.add_column("Filename", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Size", style="green")
    table.add_column("Created", style="magenta")
    table.add_column("Test Cases", style="blue")

    for file_path in sorted(dataset_files):
        # Get file info
        stat = file_path.stat()
        size_kb = stat.st_size / 1024
        created = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

        # Count test cases
        try:
            if file_path.suffix == ".jsonl":
                with open(file_path) as f:
                    count = sum(1 for _ in f)
            else:
                with open(file_path) as f:
                    data = json.load(f)
                    count = len(data) if isinstance(data, list) else len(data.get("tests", []))
        except (json.JSONDecodeError, FileNotFoundError, PermissionError, OSError):
            count = "?"

        # Determine type from filename
        file_type = "Unknown"
        if "qa_" in file_path.name:
            file_type = "Q&A"
        elif "research_" in file_path.name:
            file_type = "Research"
        elif "code_" in file_path.name:
            file_type = "Code"
        elif "adversarial_" in file_path.name:
            file_type = "Adversarial"
        elif "scenario_" in file_path.name:
            file_type = "Scenarios"

        table.add_row(file_path.name, file_type, f"{size_kb:.1f} KB", created, str(count))

    console.print(table)
    console.print(f"\nTotal datasets: [bold]{len(dataset_files)}[/bold]")


@dataset.command()
@click.option("--task-type", type=click.Choice(["qa", "code", "reasoning", "all"]), default="all")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table")
def list(task_type: str, format: str):
    """List available datasets with metadata.

    Examples:
        acp-evals dataset list
        acp-evals dataset list --task-type qa
        acp-evals dataset list --format json
    """
    console.print("[bold cyan]Available Datasets[/bold cyan]\n")

    # Get external datasets
    loader = DatasetLoader()
    dataset_infos = loader.list_datasets(task_type=None if task_type == "all" else task_type)

    # Convert DatasetInfo objects to dicts
    datasets = []
    for info in dataset_infos:
        datasets.append(
            {
                "name": info.name,
                "task_type": info.task_type,
                "description": info.description,
                "size": info.size or 0,
                "source": info.source,
            }
        )

    # Add gold standard dataset info
    datasets.append(
        {
            "name": "gold-standard",
            "task_type": "mixed",
            "description": "Production-ready agent tasks",
            "size": len(gold_standard_datasets.GOLD_STANDARD_TASKS),
            "source": "ACP Evals Internal",
        }
    )

    if format == "json":
        console.print_json(json.dumps(datasets, indent=2))
    else:
        # Create table
        table = Table(title="Evaluation Datasets")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Size", style="green")
        table.add_column("Description", style="white")

        for ds in datasets:
            table.add_row(
                ds["name"],
                ds["task_type"],
                str(ds["size"]),
                ds["description"][:60] + "..."
                if len(ds["description"]) > 60
                else ds["description"],
            )

        console.print(table)
        console.print(f"\nTotal datasets: [bold]{len(datasets)}[/bold]")


@dataset.command()
@click.argument("name")
@click.option("--split", default="test", help="Dataset split to load")
@click.option("--limit", type=int, help="Limit number of examples")
@click.option("--preview", "-p", is_flag=True, help="Show preview of examples")
@click.option("--export", "-e", help="Export to file")
def load(name: str, split: str, limit: int | None, preview: bool, export: str | None):
    """Load a dataset and optionally export it.

    Examples:
        acp-evals dataset load GAIA --preview
        acp-evals dataset load gold-standard --limit 10 --export tasks.jsonl
        acp-evals dataset load TRAIL --split test
    """
    console.print(f"[bold]Loading dataset:[/bold] {name}")

    try:
        if name == "gold-standard":
            # Load internal gold standard dataset
            examples = []
            tasks = (
                gold_standard_datasets.GOLD_STANDARD_TASKS[:limit]
                if limit
                else gold_standard_datasets.GOLD_STANDARD_TASKS
            )
            for task in tasks:
                examples.append(
                    {
                        "id": task.task_id,
                        "input": task.input,
                        "category": task.category,
                        "expected": {
                            "tools": task.expected_tools,
                            "criteria": task.expected_output_criteria,
                            "steps": len(task.expected_steps),
                        },
                        "metadata": task.metadata,
                    }
                )

            console.print(f"Loaded [green]{len(examples)}[/green] examples")
        else:
            # Load external dataset
            loader = DatasetLoader()
            examples = loader.load_dataset(name, split=split, limit=limit)
            console.print(f"Loaded [green]{len(examples)}[/green] examples from {name}/{split}")

        # Preview if requested
        if preview:
            console.print("\n[bold]Preview:[/bold]")
            for i, example in enumerate(examples[:3]):
                console.print(f"\n[cyan]Example {i + 1}:[/cyan]")
                console.print(
                    f"Input: {example.get('input', example.get('question', 'N/A'))[:100]}..."
                )
                if "expected" in example or "answer" in example:
                    console.print(
                        f"Expected: {example.get('expected', example.get('answer', 'N/A'))[:100]}..."
                    )

        # Export if requested
        if export:
            export_path = Path(export)
            if export_path.suffix == ".jsonl":
                with open(export_path, "w") as f:
                    for example in examples:
                        f.write(json.dumps(example) + "\n")
            else:
                with open(export_path, "w") as f:
                    json.dump(examples, f, indent=2)

            console.print(f"\n[green]Exported to:[/green] {export}")

        # Show summary
        if not preview and not export:
            console.print("\n[dim]Use --preview to see examples or --export to save[/dim]")

    except Exception as e:
        console.print(f"[red]Error loading dataset: {e}[/red]")
        exit(1)


@dataset.command(name="create-suite")
@click.option("--datasets", "-d", multiple=True, required=True, help="Datasets to include")
@click.option("--samples-per-dataset", "-s", type=int, default=50)
@click.option("--export", "-e", required=True, help="Export path for suite")
@click.option("--shuffle", is_flag=True, help="Shuffle examples")
def create_suite(datasets: tuple[str, ...], samples_per_dataset: int, export: str, shuffle: bool):
    """Create a benchmark suite from multiple datasets.

    Examples:
        acp-evals dataset create-suite -d GAIA -d TRAIL -e suite.jsonl
        acp-evals dataset create-suite -d gold-standard -d GSM8K -s 100 -e math-suite.json
    """
    console.print("[bold]Creating benchmark suite[/bold]\n")

    loader = DatasetLoader()
    all_examples = []

    for dataset_name in datasets:
        console.print(f"Loading {dataset_name}...", end=" ")

        try:
            if dataset_name == "gold-standard":
                examples = []
                tasks = gold_standard_datasets.GOLD_STANDARD_TASKS[:samples_per_dataset]
                for task in tasks:
                    examples.append(
                        {
                            "id": task.task_id,
                            "input": task.input,
                            "category": task.category,
                            "expected": {
                                "tools": task.expected_tools,
                                "criteria": task.expected_output_criteria,
                                "steps": len(task.expected_steps),
                            },
                            "metadata": task.metadata,
                        }
                    )
            else:
                examples = loader.load_dataset(dataset_name, limit=samples_per_dataset)

            # Add source metadata
            for ex in examples:
                ex["_source_dataset"] = dataset_name

            all_examples.extend(examples)
            console.print(f"[green]{len(examples)} examples[/green]")

        except Exception as e:
            console.print(f"[red]Failed: {e}[/red]")

    # Shuffle if requested
    if shuffle:
        import random

        random.shuffle(all_examples)

    # Export suite
    export_path = Path(export)
    if export_path.suffix == ".jsonl":
        with open(export_path, "w") as f:
            for example in all_examples:
                f.write(json.dumps(example) + "\n")
    else:
        with open(export_path, "w") as f:
            json.dump(all_examples, f, indent=2)

    console.print(f"\n[green]Created suite with {len(all_examples)} examples[/green]")
    console.print(f"Exported to: {export}")


@dataset.command()
@click.argument("dataset_file", type=click.Path(exists=True))
@click.option("--report", "-r", help="Save analysis report")
def analyze(dataset_file: str, report: str | None):
    """Analyze dataset statistics and characteristics.

    Examples:
        acp-evals dataset analyze my-dataset.jsonl
        acp-evals dataset analyze tasks.json --report analysis.txt
    """
    console.print(f"[bold]Analyzing dataset:[/bold] {dataset_file}\n")

    # Load dataset
    path = Path(dataset_file)
    if path.suffix == ".jsonl":
        examples = []
        with open(path) as f:
            for line in f:
                examples.append(json.loads(line))
    else:
        with open(path) as f:
            examples = json.load(f)

    # Analyze
    analysis = {
        "total_examples": len(examples),
        "field_counts": {},
        "avg_input_length": 0,
        "avg_expected_length": 0,
        "sources": {},
        "categories": {},
    }

    input_lengths = []
    expected_lengths = []

    for ex in examples:
        # Count fields
        for field in ex:
            analysis["field_counts"][field] = analysis["field_counts"].get(field, 0) + 1

        # Input/expected lengths
        input_text = ex.get("input", ex.get("question", ""))
        expected_text = ex.get("expected", ex.get("answer", ""))

        if input_text:
            input_lengths.append(len(input_text))
        if expected_text:
            expected_lengths.append(len(str(expected_text)))

        # Sources
        source = ex.get("_source_dataset", "unknown")
        analysis["sources"][source] = analysis["sources"].get(source, 0) + 1

        # Categories
        category = ex.get("category", ex.get("task_type", "uncategorized"))
        analysis["categories"][category] = analysis["categories"].get(category, 0) + 1

    # Calculate averages
    if input_lengths:
        analysis["avg_input_length"] = sum(input_lengths) / len(input_lengths)
    if expected_lengths:
        analysis["avg_expected_length"] = sum(expected_lengths) / len(expected_lengths)

    # Display results
    console.print(
        Panel(f"Total Examples: [bold]{analysis['total_examples']}[/bold]", title="Dataset Size")
    )

    # Field coverage
    table = Table(title="Field Coverage")
    table.add_column("Field", style="cyan")
    table.add_column("Count", style="yellow")
    table.add_column("Coverage", style="green")

    for field, count in sorted(analysis["field_counts"].items(), key=lambda x: x[1], reverse=True):
        coverage = f"{count / len(examples) * 100:.1f}%"
        table.add_row(field, str(count), coverage)

    console.print(table)

    # Statistics
    console.print("\n[bold]Statistics:[/bold]")
    console.print(f"Average input length: {analysis['avg_input_length']:.0f} chars")
    console.print(f"Average expected length: {analysis['avg_expected_length']:.0f} chars")

    # Sources
    if analysis["sources"]:
        console.print("\n[bold]Data Sources:[/bold]")
        for source, count in analysis["sources"].items():
            console.print(f"  {source}: {count} ({count / len(examples) * 100:.1f}%)")

    # Categories
    if analysis["categories"]:
        console.print("\n[bold]Categories:[/bold]")
        for category, count in sorted(
            analysis["categories"].items(), key=lambda x: x[1], reverse=True
        ):
            console.print(f"  {category}: {count} ({count / len(examples) * 100:.1f}%)")

    # Save report if requested
    if report:
        with open(report, "w") as f:
            f.write("Dataset Analysis Report\n")
            f.write("======================\n\n")
            f.write(f"File: {dataset_file}\n")
            f.write(f"Total Examples: {analysis['total_examples']}\n\n")
            f.write(json.dumps(analysis, indent=2))

        console.print(f"\n[green]Report saved to:[/green] {report}")


if __name__ == "__main__":
    dataset()
