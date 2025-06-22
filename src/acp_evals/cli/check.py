"""Provider configuration checker for ACP Evals CLI."""

import os
from pathlib import Path
from typing import Any

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core.config import check_provider_setup, get_provider_config
from ..core.exceptions import format_provider_setup_help
from ..providers import ProviderFactory

console = Console()


def check_env_file() -> Path | None:
    """Check for .env file in current or parent directories."""
    current = Path.cwd()

    # Check up to 4 levels up
    for _ in range(4):
        env_path = current / ".env"
        if env_path.exists():
            return env_path
        current = current.parent

    return None


def check_provider_connectivity(provider_name: str) -> dict[str, Any]:
    """Test connectivity to a provider."""
    result = {"connected": False, "error": None, "model": None, "latency_ms": None}

    try:
        import asyncio
        import time

        # Create provider
        provider = ProviderFactory.create(provider_name)
        result["model"] = provider.model

        # Test with simple prompt
        start = time.time()

        async def test_provider():
            response = await provider.complete(
                "Say 'test successful' and nothing else.", temperature=0.0, max_tokens=10
            )
            return response

        response = asyncio.run(test_provider())

        end = time.time()
        result["latency_ms"] = int((end - start) * 1000)
        result["connected"] = True

        # Check if response is reasonable
        if "test" in response.content.lower():
            result["response_ok"] = True
        else:
            result["response_ok"] = False
            result["error"] = "Unexpected response format"

    except Exception as e:
        result["error"] = str(e)

    return result


@click.command()
@click.option(
    "--test-connection", "-t", is_flag=True, help="Test connection to configured providers"
)
@click.option(
    "--show-setup",
    "-s",
    type=click.Choice(["openai", "anthropic", "ollama"]),
    help="Show setup instructions for a specific provider",
)
@click.pass_context
def check_providers(ctx, test_connection: bool, show_setup: str | None):
    """Check LLM provider configuration and connectivity."""

    # Get flags from context
    quiet = ctx.obj.get("quiet", False)
    verbose = ctx.obj.get("verbose", False)
    ctx.obj.get("debug", False)

    if not quiet:
        console.print("\n[bold]ACP Evals Provider Configuration Check[/bold]\n")

    # Check for .env file
    env_path = check_env_file()
    if not quiet:
        if env_path:
            console.print(f"[green]Found .env file at:[/green] {env_path}")
        else:
            console.print("[yellow]No .env file found in current or parent directories[/yellow]")
            console.print("  Create one from .env.example to configure providers\n")

    # Get provider configuration
    providers = check_provider_setup()
    config = get_provider_config()

    # Create status table
    table = Table(title="Provider Status", box=box.ROUNDED)
    table.add_column("Provider", style="cyan")
    table.add_column("Configured", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("Status", style="blue")

    for provider, configured in providers.items():
        status = "[green]Yes[/green]" if configured else "[red]No[/red]"

        # Get model for configured providers
        model = "—"
        if configured:
            if provider == "openai":
                model = os.getenv("OPENAI_MODEL", "gpt-4o")
            elif provider == "anthropic":
                model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4")
            elif provider == "ollama":
                model = os.getenv("OLLAMA_MODEL", "qwen3:8b")

        # Test connection if requested
        connection_status = ""
        if test_connection and configured:
            if verbose:
                console.print(f"\nTesting {provider}...", style="dim")
            test_result = check_provider_connectivity(provider)

            if test_result["connected"]:
                connection_status = f"Connected ({test_result['latency_ms']}ms)"
            else:
                connection_status = f"Error: {test_result['error'][:30]}..."

        table.add_row(provider.title(), status, model, connection_status or "—")

    if not quiet:
        console.print(table)

    # Show current evaluation provider
    current_provider = config.get("provider")
    if current_provider and not quiet:
        console.print(f"\n[bold]Current default provider:[/bold] {current_provider}")

        if current_provider == "mock":
            console.print("  [yellow]Running in mock mode (no LLM configured)[/yellow]")
        elif not providers.get(current_provider):
            console.print("  [red]Warning: Current provider is not configured![/red]")

    # Show setup instructions if requested
    if show_setup and not quiet:
        console.print(f"\n[bold]Setup Instructions for {show_setup.title()}:[/bold]")
        console.print(
            Panel(format_provider_setup_help(show_setup), box=box.ROUNDED, padding=(1, 2))
        )

    # Show summary and next steps
    configured_count = sum(1 for v in providers.values() if v)

    if not quiet:
        if configured_count == 0:
            console.print("\n[red]No providers configured![/red]")
            console.print("To get started:")
            console.print("  1. Copy .env.example to .env")
            console.print("  2. Add your API keys")
            console.print("  3. Run 'acp-evals check' again")
            console.print("\nFor provider-specific setup: acp-evals check --show-setup <provider>")

        elif configured_count < len(providers):
            console.print(
                f"\n[yellow]{configured_count}/{len(providers)} providers configured[/yellow]"
            )
            console.print("For help setting up other providers:")
            not_configured = [p for p, v in providers.items() if not v]
            for provider in not_configured:
                console.print(f"  acp-evals check --show-setup {provider}")

        else:
            console.print("\n[green]All providers configured![/green]")
            if not test_connection:
                console.print("Run 'acp-evals check --test-connection' to verify connectivity")

    # Check for common issues
    if env_path and configured_count > 0:
        # Check for common configuration issues
        issues = []

        # Check for placeholder values
        if providers.get("openai") and os.getenv("OPENAI_API_KEY") == "your-openai-api-key-here":
            issues.append("OpenAI API key appears to be the placeholder value from .env.example")

        # Check for placeholder values
        if (
            providers.get("anthropic")
            and os.getenv("ANTHROPIC_API_KEY") == "your-anthropic-api-key-here"
        ):
            issues.append("Anthropic API key appears to be the placeholder value from .env.example")

        if issues and not quiet:
            console.print("\n[yellow]Configuration warnings:[/yellow]")
            for issue in issues:
                console.print(f"  - {issue}")


if __name__ == "__main__":
    check_providers()
