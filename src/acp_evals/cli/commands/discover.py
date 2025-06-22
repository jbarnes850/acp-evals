"""Discover command for finding and testing ACP agents."""

import asyncio
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ...api import AccuracyEval

try:
    from acp_sdk.client import Client

    ACP_SDK_AVAILABLE = True
except ImportError:
    ACP_SDK_AVAILABLE = False
    import aiohttp

console = Console()


async def discover_agents(server_url: str) -> list[dict[str, Any]]:
    """Discover available agents from an ACP server."""
    try:
        if ACP_SDK_AVAILABLE:
            # Use official ACP SDK
            client = Client(base_url=server_url)
            agents = []

            # Use async iterator to get agents
            async for agent in client.agents():
                agent_dict = {
                    "name": agent.name,
                    "description": getattr(agent, "description", "No description"),
                    "version": getattr(agent, "version", "Unknown"),
                    "url": f"{server_url}/agents/{agent.name}",
                    "tags": getattr(agent, "tags", []),
                    "framework": getattr(agent, "framework", "Unknown"),
                }
                agents.append(agent_dict)

            return agents
        else:
            # Fallback HTTP implementation
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{server_url}/agents") as response:
                    if response.status == 200:
                        data = await response.json()
                        agents = []

                        # Handle different response formats
                        agent_data = data if isinstance(data, list) else data.get("agents", [])

                        for agent in agent_data:
                            if isinstance(agent, dict):
                                agent_dict = {
                                    "name": agent.get("name", "Unknown"),
                                    "description": agent.get("description", "No description"),
                                    "version": agent.get("version", "Unknown"),
                                    "url": f"{server_url}/agents/{agent.get('name', 'unknown')}",
                                    "tags": agent.get("tags", []),
                                    "framework": agent.get("framework", "Unknown"),
                                }
                                agents.append(agent_dict)

                        return agents
                    else:
                        console.print(f"[red]Server returned status {response.status}[/red]")
                        return []

    except Exception as e:
        console.print(f"[red]Failed to connect to ACP server: {e}[/red]")
        return []


async def test_agent(agent_url: str, agent_name: str) -> dict[str, Any]:
    """Run a quick test on an agent."""
    try:
        # Simple test
        eval_instance = AccuracyEval(agent=agent_url)
        result = await eval_instance.run(
            input="What is 2+2?",
            expected="4",
        )

        return {
            "name": agent_name,
            "url": agent_url,
            "status": "operational" if result.passed else "failing",
            "score": result.score,
            "latency_ms": getattr(result, "latency_ms", None),
        }

    except Exception as e:
        return {
            "name": agent_name,
            "url": agent_url,
            "status": "error",
            "error": str(e),
        }


def display_agents(
    agents: list[dict[str, Any]], test_results: list[dict[str, Any]] | None = None
) -> None:
    """Display discovered agents in a table."""
    if not agents:
        console.print("[yellow]No agents found[/yellow]")
        return

    # Create table
    table = Table(title="Discovered ACP Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Version", style="yellow")

    if test_results:
        table.add_column("Status", style="green")
        table.add_column("Test Score", style="magenta")

        # Create lookup for test results
        test_lookup = {r["name"]: r for r in test_results}

    for agent in agents:
        row = [
            agent["name"],
            agent["description"][:50] + "..."
            if len(agent["description"]) > 50
            else agent["description"],
            agent["version"],
        ]

        if test_results and agent["name"] in test_lookup:
            result = test_lookup[agent["name"]]

            # Status
            if result["status"] == "operational":
                status = "[green]✓ Operational[/green]"
            elif result["status"] == "failing":
                status = "[yellow]⚠ Failing Tests[/yellow]"
            else:
                status = "[red]✗ Error[/red]"

            # Score
            score = f"{result.get('score', 0):.2f}" if result.get("score") else "N/A"

            row.extend([status, score])

        table.add_row(*row)

    console.print(table)

    # Summary
    summary_text = f"Total agents discovered: [bold]{len(agents)}[/bold]"

    if test_results:
        operational = sum(1 for r in test_results if r["status"] == "operational")
        summary_text += f"\nOperational: [green]{operational}[/green]"
        summary_text += f"\nWith issues: [yellow]{len(test_results) - operational}[/yellow]"

    console.print(
        Panel(
            summary_text,
            title="Discovery Summary",
            border_style="blue",
        )
    )


@click.command()
@click.option(
    "--server",
    "-s",
    default="http://localhost:8000",
    help="ACP server URL",
)
@click.option(
    "--test-all",
    is_flag=True,
    help="Run quick test on all discovered agents",
)
@click.option(
    "--export",
    "-e",
    help="Export discovered agents to JSON file",
)
@click.option(
    "--filter",
    "-f",
    help="Filter agents by name pattern",
)
@click.pass_context
def discover(ctx, server: str, test_all: bool, export: str | None, filter: str | None) -> None:
    """Discover and list available ACP agents.

    Examples:
        acp-evals discover
        acp-evals discover --server http://acp.example.com
        acp-evals discover --test-all
        acp-evals discover --filter "research*" --export agents.json
    """
    # Get flags from context
    quiet = ctx.obj.get("quiet", False)
    ctx.obj.get("verbose", False)
    ctx.obj.get("debug", False)

    if not quiet:
        console.print("\n[bold cyan]ACP Agent Discovery[/bold cyan]")
        console.print(f"Server: [yellow]{server}[/yellow]\n")

    # Discover agents
    with console.status("Discovering agents..."):
        agents = asyncio.run(discover_agents(server))

    if not agents:
        console.print("[red]No agents discovered. Check server URL and connectivity.[/red]")
        exit(1)

    # Apply filter if provided
    if filter:
        import fnmatch

        agents = [a for a in agents if fnmatch.fnmatch(a["name"], filter)]
        console.print(f"Filtered to {len(agents)} agents matching '{filter}'\n")

    # Test all agents if requested
    test_results = None
    if test_all:
        console.print("[bold]Testing all agents...[/bold]\n")

        test_results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Testing agents...", total=len(agents))

            for i, agent in enumerate(agents):
                progress.update(
                    task,
                    description=f"Testing {agent['name']} ({i + 1}/{len(agents)})",
                )

                result = asyncio.run(test_agent(agent["url"], agent["name"]))
                test_results.append(result)

    # Display results
    display_agents(agents, test_results)

    # Export if requested
    if export:
        import json

        export_data = {
            "server": server,
            "agents": agents,
        }

        if test_results:
            export_data["test_results"] = test_results

        with open(export, "w") as f:
            json.dump(export_data, f, indent=2)

        console.print(f"\n[green]Agents exported to:[/green] {export}")

    # Print connection examples
    if agents and not test_all:
        console.print("\n[bold]Quick Start:[/bold]")
        first_agent = agents[0]
        console.print(f"Test an agent: [dim]acp-evals test {first_agent['url']}[/dim]")
        console.print(
            f'Run evaluation: [dim]acp-evals run accuracy {first_agent["url"]} -i "What is AI?" -e "Artificial Intelligence"[/dim]'
        )


if __name__ == "__main__":
    discover()
