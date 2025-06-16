"""Generate command for synthetic test data creation."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ...benchmarks.datasets import adversarial_datasets
from ...pipeline.simulator import Simulator

console = Console()


@click.group()
def generate():
    """Generate synthetic test data."""
    pass


@generate.command()
@click.option('--scenario', '-s', type=click.Choice(['qa', 'research', 'code', 'all']), default='qa')
@click.option('--count', '-c', type=int, default=50, help='Number of tests to generate')
@click.option('--diversity', '-d', type=float, default=0.7, help='Diversity level (0-1)')
@click.option('--export', '-e', required=True, help='Export path')
def tests(scenario: str, count: int, diversity: float, export: str):
    """Generate test cases from templates.

    Examples:
        acp-evals generate tests -e qa-tests.jsonl
        acp-evals generate tests --scenario research -c 100 -e research.json
        acp-evals generate tests --diversity 0.9 -e diverse-tests.jsonl
    """
    console.print(f"[bold]Generating {count} test cases[/bold]")
    console.print(f"Scenario: [cyan]{scenario}[/cyan]")
    console.print(f"Diversity: [yellow]{diversity:.1f}[/yellow]\n")

    # Create a mock agent for the simulator
    simulator = Simulator(agent="mock-agent")

    try:
        # Generate test cases
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Generating {scenario} tests...", total=1)

            if scenario == 'all':
                # Generate mix of scenarios
                test_cases = []
                scenarios = ['factual_qa', 'task_specific', 'multi_turn']
                per_scenario = count // len(scenarios)

                for s in scenarios:
                    cases = simulator.generate_synthetic_tests(
                        scenario=s,
                        count=per_scenario
                    )
                    test_cases.extend(cases)
            else:
                # Map CLI scenario to simulator scenario
                scenario_map = {
                    'qa': 'factual_qa',
                    'research': 'task_specific',
                    'code': 'task_specific'
                }
                test_cases = simulator.generate_synthetic_tests(
                    scenario=scenario_map.get(scenario, 'factual_qa'),
                    count=count
                )

            progress.advance(task)

        # Save test cases
        export_path = Path(export)
        if export_path.suffix == '.jsonl':
            with open(export_path, 'w') as f:
                for test in test_cases:
                    f.write(json.dumps(test) + '\n')
        else:
            with open(export_path, 'w') as f:
                json.dump(test_cases, f, indent=2)

        console.print(f"[green]Generated {len(test_cases)} test cases[/green]")
        console.print(f"Exported to: {export}")

        # Show sample
        console.print("\n[bold]Sample test case:[/bold]")
        sample = test_cases[0]
        console.print(f"Input: {sample['input'][:100]}...")
        if 'expected' in sample:
            console.print(f"Expected: {sample['expected'][:100]}...")

    except Exception as e:
        console.print(f"[red]Error generating tests: {e}[/red]")
        exit(1)


@generate.command()
@click.option('--severity', '-s',
              type=click.Choice(['low', 'medium', 'high', 'critical', 'all']),
              default='all')
@click.option('--category', '-c', help='Specific attack category')
@click.option('--count', '-n', type=int, default=50, help='Number of tests')
@click.option('--export', '-e', required=True, help='Export path')
def adversarial(severity: str, category: str | None, count: int, export: str):
    """Generate adversarial test cases.

    Examples:
        acp-evals generate adversarial -e attacks.jsonl
        acp-evals generate adversarial --severity high -e high-severity.json
        acp-evals generate adversarial --category prompt_injection -n 20 -e injections.jsonl
    """
    console.print("[bold]Generating adversarial test cases[/bold]")

    # Show available categories if requested
    valid_categories = ['prompt_injection', 'harmful_content', 'data_extraction',
                       'jailbreak', 'edge_case', 'encoding_attack', 'role_play', 'indirect_attack']

    if category and category not in valid_categories:
        console.print(f"[red]Invalid category: {category}[/red]")
        console.print("\nAvailable categories:")
        for cat in valid_categories:
            console.print(f"  - {cat}")
        exit(1)

    console.print(f"Severity: [yellow]{severity}[/yellow]")
    if category:
        console.print(f"Category: [cyan]{category}[/cyan]")
    console.print()

    try:
        # Get adversarial examples
        from ...benchmarks.datasets.adversarial_datasets import (
            ADVERSARIAL_TESTS,
            AdversarialCategory,
        )

        # Filter tests based on criteria
        tests = ADVERSARIAL_TESTS

        # Filter by category
        if category:
            # Map string category to enum
            category_map = {
                'prompt_injection': AdversarialCategory.PROMPT_INJECTION,
                'harmful_content': AdversarialCategory.HARMFUL_CONTENT,
                'data_extraction': AdversarialCategory.DATA_EXTRACTION,
                'jailbreak': AdversarialCategory.JAILBREAK,
                'edge_case': AdversarialCategory.EDGE_CASE,
                'encoding_attack': AdversarialCategory.ENCODING_ATTACK,
                'role_play': AdversarialCategory.ROLE_PLAY,
                'indirect_attack': AdversarialCategory.INDIRECT_ATTACK
            }
            if category in category_map:
                tests = adversarial_datasets.get_tests_by_category(category_map[category])

        # Filter by severity
        if severity != 'all':
            tests = [t for t in tests if t.severity == severity]

        # Limit count
        tests = tests[:count]

        # Convert to exportable format
        examples = []
        for test in tests:
            examples.append({
                'id': test.test_id,
                'input': test.attack_vector,
                'category': test.category.value,
                'expected_behavior': test.expected_behavior,
                'severity': test.severity,
                'metadata': test.metadata
            })

        # Save examples
        export_path = Path(export)
        if export_path.suffix == '.jsonl':
            with open(export_path, 'w') as f:
                for ex in examples:
                    f.write(json.dumps(ex) + '\n')
        else:
            with open(export_path, 'w') as f:
                json.dump(examples, f, indent=2)

        console.print(f"[green]Generated {len(examples)} adversarial tests[/green]")
        console.print(f"Exported to: {export}")

        # Show distribution
        console.print("\n[bold]Test Distribution:[/bold]")

        severity_counts = {}
        category_counts = {}

        for ex in examples:
            sev = ex.get('severity', 'unknown')
            cat = ex.get('category', 'unknown')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1

        console.print("\nBy severity:")
        for sev, count in sorted(severity_counts.items()):
            console.print(f"  {sev}: {count}")

        console.print("\nBy category:")
        for cat, count in sorted(category_counts.items()):
            console.print(f"  {cat}: {count}")

    except Exception as e:
        console.print(f"[red]Error generating adversarial tests: {e}[/red]")
        exit(1)


@generate.command()
@click.option('--turns', '-t', type=int, default=3, help='Number of conversation turns')
@click.option('--count', '-c', type=int, default=10, help='Number of scenarios')
@click.option('--export', '-e', required=True, help='Export path')
def scenarios(turns: int, count: int, export: str):
    """Generate multi-turn conversation scenarios.

    Examples:
        acp-evals generate scenarios -e conversations.jsonl
        acp-evals generate scenarios --turns 5 -c 20 -e long-convos.json
    """
    console.print(f"[bold]Generating {count} conversation scenarios[/bold]")
    console.print(f"Turns per conversation: [cyan]{turns}[/cyan]\n")

    simulator = Simulator(agent="mock-agent")

    try:
        # Generate multi-turn conversations
        conversations = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating conversations...", total=count)

            test_cases = simulator.generate_synthetic_tests(
                scenario='multi_turn',
                count=count
            )

            for test in test_cases:
                # Ensure we have the requested number of turns
                if 'conversation' in test:
                    # Trim or extend conversation to match requested turns
                    conv = test['conversation']
                    if len(conv) > turns:
                        test['conversation'] = conv[:turns]
                    elif len(conv) < turns:
                        # Add more turns if needed
                        for i in range(len(conv), turns):
                            role = 'user' if i % 2 == 0 else 'assistant'
                            test['conversation'].append({
                                'role': role,
                                'content': f"Turn {i+1} content"
                            })

                conversations.append(test)
                progress.advance(task)

        # Save conversations
        export_path = Path(export)
        if export_path.suffix == '.jsonl':
            with open(export_path, 'w') as f:
                for conv in conversations:
                    f.write(json.dumps(conv) + '\n')
        else:
            with open(export_path, 'w') as f:
                json.dump(conversations, f, indent=2)

        console.print(f"[green]Generated {len(conversations)} conversation scenarios[/green]")
        console.print(f"Exported to: {export}")

        # Show sample
        if conversations:
            console.print("\n[bold]Sample conversation:[/bold]")
            sample = conversations[0]
            if 'conversation' in sample:
                for turn in sample['conversation'][:2]:
                    console.print(f"{turn['role']}: {turn['content'][:80]}...")
                if len(sample['conversation']) > 2:
                    console.print(f"[dim]... {len(sample['conversation']) - 2} more turns[/dim]")

    except Exception as e:
        console.print(f"[red]Error generating scenarios: {e}[/red]")
        exit(1)


if __name__ == "__main__":
    generate()

