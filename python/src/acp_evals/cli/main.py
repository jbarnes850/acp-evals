#!/usr/bin/env python3
"""
CLI tool for ACP evaluations.

Commands:
    acp-evals init [template] - Generate starter evaluation template
    acp-evals check - Check provider configuration
"""

import os
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

TEMPLATES = {
    "simple": """#!/usr/bin/env python3
\"\"\"
Simple evaluation example for {agent_name}.

This template shows how to evaluate a basic agent.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, evaluate

# Define your agent
async def {agent_function}(input_text: str) -> str:
    \"\"\"Your agent implementation.\"\"\"
    # TODO: Implement your agent logic here
    return f"Response to: {{input_text}}"

# Simple evaluation
def test_basic():
    result = evaluate(
        AccuracyEval(agent={agent_function}),
        input="What is 2+2?",
        expected="4",
        print_results=True
    )
    assert result.passed, f"Test failed with score {{result.score}}"

# Batch evaluation
async def test_batch():
    eval = AccuracyEval(agent={agent_function}, rubric="factual")

    test_cases = [
        {{"input": "What is 2+2?", "expected": "4"}},
        {{"input": "What is the capital of France?", "expected": "Paris"}},
        # Add more test cases
    ]

    batch_result = await eval.run_batch(
        test_cases=test_cases,
        print_results=True,
        export="results.json"
    )

    print(f"\\nPass rate: {{batch_result.pass_rate:.1f}}%")
    print(f"Average score: {{batch_result.avg_score:.2f}}")

if __name__ == "__main__":
    print("Running basic test...")
    test_basic()

    print("\\nRunning batch test...")
    asyncio.run(test_batch())
""",

    "comprehensive": """#!/usr/bin/env python3
\"\"\"
Comprehensive evaluation suite for {agent_name}.

This template includes accuracy, performance, and reliability testing.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

class {agent_class}:
    \"\"\"Your agent implementation.\"\"\"

    def __init__(self):
        # TODO: Initialize your agent
        pass

    async def run(self, input_text: str) -> str:
        \"\"\"Process input and return response.\"\"\"
        # TODO: Implement your agent logic
        return f"Response to: {{input_text}}"

async def evaluate_agent():
    \"\"\"Run comprehensive evaluation suite.\"\"\"
    agent = {agent_class}()

    # 1. Accuracy Evaluation
    print("=== Accuracy Evaluation ===")
    accuracy_eval = AccuracyEval(
        agent=agent,
        rubric={rubric_choice}
    )

    accuracy_result = await accuracy_eval.run(
        input="{sample_input}",
        expected="{sample_expected}",
        print_results=True
    )

    # 2. Performance Evaluation
    print("\\n=== Performance Evaluation ===")
    perf_eval = PerformanceEval(agent=agent)

    perf_result = await perf_eval.run(
        input="{sample_input}",
        track_tokens=True,
        track_latency=True,
        print_results=True
    )

    # 3. Reliability Evaluation
    print("\\n=== Reliability Evaluation ===")
    reliability_eval = ReliabilityEval(
        agent=agent,
        tool_definitions=["search", "calculate", "database"]  # Update with your tools
    )

    reliability_result = await reliability_eval.run(
        input="{sample_input}",
        expected_tools=["search"],  # Update with expected tools
        print_results=True
    )

    # 4. Batch Testing
    print("\\n=== Batch Testing ===")
    test_cases = [
        {{"input": "{sample_input}", "expected": "{sample_expected}"}},
        # Add more test cases here
    ]

    batch_result = await accuracy_eval.run_batch(
        test_cases=test_cases,
        parallel=True,
        print_results=True,
        export="evaluation_results.json"
    )

    return {{
        "accuracy": accuracy_result,
        "performance": perf_result,
        "reliability": reliability_result,
        "batch": batch_result
    }}

if __name__ == "__main__":
    results = asyncio.run(evaluate_agent())
    print("\\nEvaluation complete!")
""",

    "research": """#!/usr/bin/env python3
\"\"\"
Research agent evaluation template.

Specialized for evaluating agents that do research, analysis, and information synthesis.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval

class ResearchAgent:
    \"\"\"Research agent that searches and synthesizes information.\"\"\"

    async def run(self, query: str) -> str:
        \"\"\"Research a topic and return comprehensive analysis.\"\"\"
        # TODO: Implement your research logic
        # This could include:
        # - Web search
        # - Document analysis
        # - Information synthesis
        # - Source citation

        return f"\"\"\"
## Research Results for: {{query}}

### Summary
[Your research summary here]

### Key Findings
1. Finding 1
2. Finding 2
3. Finding 3

### Sources
- Source 1
- Source 2
\"\"\"

async def evaluate_research_agent():
    agent = ResearchAgent()

    # Use research quality rubric
    eval = AccuracyEval(
        agent=agent,
        rubric="research_quality",
        pass_threshold=0.75
    )

    # Test cases for research evaluation
    test_cases = [
        {{
            "input": "What are the latest developments in quantum computing?",
            "expected": {{
                "topics": ["quantum supremacy", "error correction", "hardware advances"],
                "depth": "comprehensive",
                "sources": "multiple credible sources"
            }}
        }},
        {{
            "input": "Compare transformer vs RNN architectures for NLP",
            "expected": {{
                "comparison_aspects": ["performance", "training time", "context window"],
                "balanced": True,
                "technical_accuracy": "high"
            }}
        }}
    ]

    # Run evaluation
    results = await eval.run_batch(
        test_cases=test_cases,
        print_results=True,
        export="research_eval_results.json"
    )

    # Performance testing for research tasks
    perf_eval = PerformanceEval(agent=agent)

    perf_result = await perf_eval.run(
        input="Research the environmental impact of electric vehicles",
        track_latency=True,
        print_results=True
    )

    print(f"\\nResearch Quality Score: {{results.avg_score:.2f}}")
    print(f"Average Response Time: {{perf_result.details['latency_ms']:.0f}}ms")

if __name__ == "__main__":
    asyncio.run(evaluate_research_agent())
""",

    "tool": """#!/usr/bin/env python3
\"\"\"
Tool-using agent evaluation template.

For agents that use external tools like calculators, APIs, databases, etc.
\"\"\"

import asyncio
from typing import Dict, Any, List
from acp_evals import AccuracyEval, ReliabilityEval, PerformanceEval

class ToolAgent:
    \"\"\"Agent that uses various tools to complete tasks.\"\"\"

    def __init__(self):
        self.tools = {{
            "calculator": self._calculator,
            "search": self._search,
            "database": self._database,
            # Add your tools here
        }}
        self.tool_calls = []

    async def _calculator(self, expression: str) -> float:
        \"\"\"Calculator tool.\"\"\"
        # TODO: Implement calculator logic
        return eval(expression)  # Simple example - use safe parser in production

    async def _search(self, query: str) -> List[Dict[str, str]]:
        \"\"\"Search tool.\"\"\"
        # TODO: Implement search logic
        return [{{"title": "Result 1", "snippet": "..."}}]

    async def _database(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"Database tool.\"\"\"
        # TODO: Implement database logic
        return []

    async def run(self, input_text: str) -> str:
        \"\"\"Process input using appropriate tools.\"\"\"
        self.tool_calls = []  # Reset for tracking

        # TODO: Implement tool selection and usage logic
        # Example:
        if "calculate" in input_text.lower():
            result = await self.tools["calculator"]("2+2")
            self.tool_calls.append(("calculator", "2+2"))
            return f"The result is {{result}}"

        return "I need to use tools to answer this."

async def evaluate_tool_agent():
    agent = ToolAgent()

    # 1. Tool Usage Reliability
    print("=== Tool Usage Evaluation ===")
    reliability_eval = ReliabilityEval(
        agent=agent,
        tool_definitions=list(agent.tools.keys())
    )

    tool_test_cases = [
        {{
            "input": "Calculate 25 * 4 + sqrt(16)",
            "expected_tools": ["calculator"],
            "expected_calls": 3
        }},
        {{
            "input": "Search for information about climate change",
            "expected_tools": ["search"],
            "expected_calls": 1
        }}
    ]

    for test in tool_test_cases:
        agent.tool_calls = []
        result = await reliability_eval.run(
            input=test["input"],
            expected_tools=test["expected_tools"],
            print_results=True
        )

        actual_tools = [call[0] for call in agent.tool_calls]
        print(f"Expected tools: {{test['expected_tools']}}")
        print(f"Actually used: {{list(set(actual_tools))}}")
        print(f"Tool calls: {{len(agent.tool_calls)}}\\n")

    # 2. Accuracy with Tools
    print("=== Accuracy Evaluation ===")
    accuracy_eval = AccuracyEval(
        agent=agent,
        rubric={{
            "correctness": {{"weight": 0.5, "criteria": "Are results correct?"}},
            "tool_usage": {{"weight": 0.3, "criteria": "Are tools used appropriately?"}},
            "efficiency": {{"weight": 0.2, "criteria": "Are tools used efficiently?"}}
        }}
    )

    accuracy_result = await accuracy_eval.run(
        input="What is 100 * 50?",
        expected="5000",
        print_results=True
    )

    print(f"\\nOverall tool agent score: {{accuracy_result.score:.2f}}")

if __name__ == "__main__":
    asyncio.run(evaluate_tool_agent())
"""
}


@click.group()
def cli():
    """ACP Evaluations CLI - Tools for evaluating ACP agents."""
    pass


# Import check command
from .check import check_providers

cli.add_command(check_providers, name='check')


@cli.command()
@click.argument('template', type=click.Choice(['simple', 'comprehensive', 'research', 'tool']), default='simple')
@click.option('--name', '-n', help='Name for your agent/evaluation')
@click.option('--output', '-o', help='Output file path', default='agent_eval.py')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode with prompts')
def init(template, name, output, interactive):
    """Generate a starter evaluation template.

    Templates:
    - simple: Basic evaluation with accuracy testing
    - comprehensive: Full suite with accuracy, performance, reliability
    - research: Specialized for research/analysis agents
    - tool: For agents that use external tools
    """
    console.print("[bold cyan]ACP Evaluations Template Generator[/bold cyan]\n")

    # Interactive mode
    if interactive:
        template = Prompt.ask(
            "Select template type",
            choices=['simple', 'comprehensive', 'research', 'tool'],
            default='simple'
        )

        name = Prompt.ask("Agent name", default="MyAgent")
        output = Prompt.ask("Output file", default=f"{name.lower()}_eval.py")

    # Generate names from agent name
    if not name:
        name = Path(output).stem.replace('_eval', '').replace('-', '_').title()

    agent_function = name.lower().replace(' ', '_')
    agent_class = name.replace(' ', '')

    # Get template
    template_content = TEMPLATES[template]

    # Customize template
    replacements = {
        "{agent_name}": name,
        "{agent_function}": agent_function,
        "{agent_class}": agent_class,
    }

    # Additional prompts for comprehensive template
    if template == 'comprehensive' and interactive:
        rubric_choice = Prompt.ask(
            "Select evaluation rubric",
            choices=['factual', 'research_quality', 'code_quality', 'custom'],
            default='factual'
        )

        if rubric_choice == 'custom':
            replacements["{rubric_choice}"] = """{
            "accuracy": {"weight": 0.5, "criteria": "Is the response accurate?"},
            "completeness": {"weight": 0.3, "criteria": "Is the response complete?"},
            "clarity": {"weight": 0.2, "criteria": "Is the response clear?"}
        }"""
        else:
            replacements["{rubric_choice}"] = f'"{rubric_choice}"'

        replacements["{sample_input}"] = Prompt.ask(
            "Sample test input",
            default="What is the capital of France?"
        )
        replacements["{sample_expected}"] = Prompt.ask(
            "Expected output",
            default="Paris"
        )
    else:
        # Defaults for non-interactive mode
        replacements["{rubric_choice}"] = '"factual"'
        replacements["{sample_input}"] = "What is the capital of France?"
        replacements["{sample_expected}"] = "Paris"

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
            console.print(f"[yellow]Warning: {output} already exists. Use -i for interactive mode.[/yellow]")
            return

    # Write file
    output_path.write_text(template_content)

    # Make executable
    os.chmod(output_path, 0o755)

    # Success message
    console.print(f"\n[green]Created evaluation template:[/green] [bold]{output}[/bold]")
    console.print(f"\nTemplate type: [cyan]{template}[/cyan]")
    console.print(f"Agent name: [cyan]{name}[/cyan]")

    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Edit the file to implement your agent logic")
    console.print("2. Update test cases with your specific scenarios")
    console.print("3. Run the evaluation:")
    console.print(f"   [dim]python {output}[/dim]")

    if template == 'simple':
        console.print("\n[dim]Tip: Use -t comprehensive for a full evaluation suite[/dim]")


@cli.command()
def list_rubrics():
    """List available evaluation rubrics."""
    from acp_evals.simple import AccuracyEval

    console.print("[bold cyan]Available Evaluation Rubrics[/bold cyan]\n")

    for name, rubric in AccuracyEval.RUBRICS.items():
        console.print(f"[bold]{name}[/bold]")
        console.print(f"  Best for: {rubric.get('description', 'General evaluation')}")
        console.print("  Criteria:")
        for criterion, details in rubric.items():
            if criterion != 'description' and isinstance(details, dict):
                console.print(f"    - {criterion} (weight: {details['weight']})")
                console.print(f"      {details['criteria']}")
        console.print()


@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['summary', 'detailed', 'markdown']), default='summary')
def report(results_file, format):
    """Generate a report from evaluation results."""
    import json

    from rich.markdown import Markdown
    from rich.table import Table

    # Load results
    with open(results_file) as f:
        data = json.load(f)

    if format == 'summary':
        # Summary table
        table = Table(title="Evaluation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        summary = data.get('summary', {})
        table.add_row("Total Tests", str(summary.get('total', 0)))
        table.add_row("Passed", f"[green]{summary.get('passed', 0)}[/green]")
        table.add_row("Failed", f"[red]{summary.get('failed', 0)}[/red]")
        table.add_row("Pass Rate", f"{summary.get('pass_rate', 0):.1f}%")
        table.add_row("Average Score", f"{summary.get('avg_score', 0):.2f}")

        console.print(table)

    elif format == 'detailed':
        # Detailed results
        console.print("[bold]Detailed Evaluation Results[/bold]\n")

        for i, result in enumerate(data.get('results', [])):
            status = "[green]PASSED[/green]" if result['passed'] else "[red]FAILED[/red]"
            console.print(f"Test {i+1}: {status} (Score: {result['score']:.2f})")
            console.print(f"  Input: {result.get('metadata', {}).get('input', 'N/A')}")
            console.print(f"  Expected: {result.get('metadata', {}).get('expected', 'N/A')}")
            console.print(f"  Feedback: {result.get('details', {}).get('feedback', 'N/A')}")
            console.print()

    elif format == 'markdown':
        # Markdown report
        md_content = f"""# Evaluation Report

## Summary
- **Total Tests**: {data.get('summary', {}).get('total', 0)}
- **Passed**: {data.get('summary', {}).get('passed', 0)}
- **Failed**: {data.get('summary', {}).get('failed', 0)}
- **Pass Rate**: {data.get('summary', {}).get('pass_rate', 0):.1f}%
- **Average Score**: {data.get('summary', {}).get('avg_score', 0):.2f}

## Detailed Results
"""

        for i, result in enumerate(data.get('results', [])):
            md_content += f"""
### Test {i+1}
- **Status**: {'Passed' if result['passed'] else 'Failed'}
- **Score**: {result['score']:.2f}
- **Input**: `{result.get('metadata', {}).get('input', 'N/A')}`
- **Expected**: `{result.get('metadata', {}).get('expected', 'N/A')}`
- **Feedback**: {result.get('details', {}).get('feedback', 'N/A')}
"""

        console.print(Markdown(md_content))


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
