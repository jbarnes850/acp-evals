"""
Interactive quick-start wizard for first-time users.

This command provides an interactive setup experience to get users
evaluating their agents as quickly as possible.
"""

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from ...core import config
from ..display import create_evaluation_header

console = Console()


@click.command("quick-start")
@click.pass_context
def quickstart(ctx):
    """Interactive setup wizard for getting started quickly."""

    # Check quiet mode
    if ctx.obj.get("quiet"):
        return

    # Welcome message
    console.print()
    console.print(create_evaluation_header("ACP Evals Quick Start Wizard"))
    console.print()

    console.print(
        Panel(
            "Welcome! This wizard will help you get started with ACP Evals in just a few steps.",
            style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    # Step 1: Check if API keys are configured
    providers = config.get_available_providers()

    if not providers:
        console.print("[yellow]No LLM providers configured.[/yellow]")
        console.print("You must configure an LLM provider to use ACP-Evals.")
        console.print("This tool requires real LLM evaluations for accurate results.")
        console.print()

        # Help configure a provider
        console.print("\nAvailable providers:")
        console.print("  1. OpenAI (recommended)")
        console.print("  2. Anthropic")
        console.print("  3. Ollama (local)")

        choice = Prompt.ask(
            "\nWhich provider would you like to configure?", choices=["1", "2", "3"], default="1"
        )

        if choice == "1":
            api_key = Prompt.ask("Enter your OpenAI API key", password=True)
            # Create or update .env file
            env_path = Path(".env")
            with open(env_path, "a") as f:
                f.write(f"\nOPENAI_API_KEY={api_key}\n")
            console.print("[green]OpenAI configured successfully![/green]")

        elif choice == "2":
            api_key = Prompt.ask("Enter your Anthropic API key", password=True)
            with open(".env", "a") as f:
                f.write(f"\nANTHROPIC_API_KEY={api_key}\n")
            console.print("[green]Anthropic configured successfully![/green]")

        else:
            console.print("\n[cyan]For Ollama, make sure it's running locally:[/cyan]")
            console.print("  ollama serve")
            console.print("\nNo API key needed for Ollama.")

    # Step 2: Choose what to test
    console.print("\n[bold]What would you like to test?[/bold]")
    console.print("  1. An ACP agent (URL)")
    console.print("  2. A Python function")
    console.print("  3. I don't have anything yet (create example)")

    test_choice = Prompt.ask("\nYour choice", choices=["1", "2", "3"], default="3")

    if test_choice == "1":
        # Test an ACP agent
        agent_url = Prompt.ask(
            "\nEnter your agent URL", default="http://localhost:8000/agents/my-agent"
        )

        # Create test script
        script = f"""#!/usr/bin/env python3
\"\"\"Quick test of your ACP agent.\"\"\"

from acp_evals import evaluate

# Test your agent with one line
result = evaluate.accuracy(
    "{agent_url}",
    input="What is 2+2?",
    expected="4"
)

print(f"Score: {{result.score}}")
print(f"Passed: {{result.passed}}")

# Try more tests
print("\\nTesting greeting...")
result2 = evaluate.accuracy(
    "{agent_url}",
    input="Hello, how are you?",
    expected="A friendly greeting response"
)
print(f"Greeting test score: {{result2.score}}")
"""

    elif test_choice == "2":
        # Test a Python function
        func_name = Prompt.ask("\nFunction name", default="my_agent")

        script = f"""#!/usr/bin/env python3
\"\"\"Quick test of your Python function.\"\"\"

from acp_evals import evaluate

def {func_name}(message):
    \"\"\"Your agent function.\"\"\"
    # TODO: Replace with your actual function
    if "2+2" in message:
        return "4"
    return "I don't know"

# Test your function
result = evaluate.accuracy(
    {func_name},
    input="What is 2+2?",
    expected="4"
)

print(f"Score: {{result.score}}")
print(f"Passed: {{result.passed}}")
"""

    else:
        # Create a complete example
        script = """#!/usr/bin/env python3
\"\"\"Complete example to get you started.\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

# Example 1: Simple function agent
def calculator_agent(message):
    \"\"\"A simple calculator agent.\"\"\"
    if "2+2" in message:
        return "4"
    elif "capital of France" in message.lower():
        return "Paris"
    elif "hello" in message.lower():
        return "Hello! I'm a helpful assistant."
    return "I'm not sure about that."

async def main():
    # Test 1: Basic accuracy test
    print("Test 1: Basic accuracy")
    eval = AccuracyEval(calculator_agent)
    result = await eval.run(
        input="What is 2+2?",
        expected="4"
    )
    print(f"Score: {result.score}")

    # Test 2: Performance evaluation
    print("\\nTest 2: Performance")
    perf = PerformanceEval(calculator_agent)
    result = await perf.run("What is the capital of France?")
    print(f"Latency: {result.details.get('latency_ms', 0):.2f}ms")

    # Test 3: Reliability check
    print("\\nTest 3: Reliability")
    reliable = ReliabilityEval(calculator_agent)
    result = await reliable.run("Hello!")
    print(f"Consistency: {result.score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
"""

    # Step 3: Save the script
    filename = Prompt.ask("\nSave test script as", default="test_agent.py")

    with open(filename, "w") as f:
        f.write(script)

    console.print(f"\n[green]Created {filename}![/green]")

    # Make it executable
    Path(filename).chmod(0o755)

    # Step 4: Run it?
    if Confirm.ask("\nWould you like to run the test now?", default=True):
        console.print("\n[cyan]Running test...[/cyan]\n")
        subprocess.run([sys.executable, filename])

    # Step 5: Next steps
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("1. Edit the test script to match your agent")
    console.print("2. Add more test cases")
    console.print("3. Try batch evaluation with 'acp-evals run'")
    console.print("4. Explore other evaluators (performance, safety, reliability)")
    console.print("\n[dim]Run 'acp-evals --help' to see all available commands.[/dim]")


# Export the command
__all__ = ["quickstart"]
