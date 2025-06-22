"""
Common classes and utilities for evaluators.
"""

import asyncio
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core.exceptions import AgentConnectionError, AgentTimeoutError
from ..core.validation import InputValidator

# Import display components conditionally to avoid circular imports
try:
    from ..cli.display import console as display_console
    from ..cli.display import (
        create_evaluation_header,
        create_score_bar,
        create_score_summary,
        create_suggestions_panel,
        create_test_details_tree,
    )

    HAS_DISPLAY = True
except ImportError:
    HAS_DISPLAY = False
    from rich.console import Console

    display_console = Console()

# Use display console if available, otherwise create new one
console = display_console


class EvalResult:
    """Simple result container with pretty printing."""

    def __init__(
        self,
        name: str,
        passed: bool,
        score: float,
        details: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ):
        self.name = name
        self.passed = passed
        self.score = score
        self.details = details
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"EvalResult(name='{self.name}', passed={self.passed}, score={self.score:.2f})"

    def assert_passed(self):
        """Assert that the evaluation passed."""
        if not self.passed:
            raise AssertionError(f"Evaluation '{self.name}' failed with score {self.score:.2f}")

    def print_summary(self):
        """Print a summary of the result with enhanced visualization."""
        if HAS_DISPLAY:
            # Use enhanced display components
            # Create score bar
            score_bar = create_score_bar(self.score)

            # Create result panel
            status_text = "PASS" if self.passed else "FAIL"
            status_color = "green" if self.passed else "red"

            # Build content lines
            content_lines = [
                f"Score: {score_bar} [{status_color}]{self.score:.2f}[/{status_color}]",
                f"Status: [{status_color}]{status_text}[/{status_color}]",
            ]

            # Add details if available
            if self.details:
                # Handle feedback separately
                feedback = self.details.get("feedback", "")
                if feedback:
                    content_lines.append(f"\nFeedback:\n{feedback}")

                # Handle scores breakdown
                scores = self.details.get("scores", {})
                if scores:
                    content_lines.append("\nCriteria Scores:")
                    for criterion, score in scores.items():
                        criterion_bar = create_score_bar(score, width=10)
                        content_lines.append(f"  {criterion}: {criterion_bar} {score:.2f}")

                # Add other details
                for key, value in self.details.items():
                    if key not in ["feedback", "scores", "latency_ms"]:
                        content_lines.append(f"\n{key.replace('_', ' ').title()}: {value}")

            # Create and display panel
            panel = Panel(
                "\n".join(content_lines),
                title=f"Evaluation Result - {self.name}",
                border_style=status_color,
                expand=False,
                padding=(1, 2),
            )

            console.print()
            console.print(panel)
        else:
            # Fallback to simple display
            status = "[green]PASSED[/green]" if self.passed else "[red]FAILED[/red]"
            console.print(f"\n{status} {self.name}: {self.score:.2f}")

            if self.details:
                console.print("\nDetails:")
                for key, value in self.details.items():
                    console.print(f"  - {key}: {value}")


class BatchResult:
    """Container for batch evaluation results."""

    def __init__(self, results: list[EvalResult]):
        self.results = results
        self.total = len(results)
        self.passed = sum(1 for r in results if r.passed)
        self.failed = self.total - self.passed
        self.pass_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        self.avg_score = sum(r.score for r in results) / self.total if self.total > 0 else 0

    def print_summary(self):
        """Print an enhanced summary of batch results."""
        if HAS_DISPLAY:
            # Use enhanced display components
            # Header
            console.print()
            console.print(create_evaluation_header("Batch Evaluation Results"))
            console.print()

            # Overall score summary
            overall_bar = create_score_bar(self.avg_score)
            overall_color = (
                "green" if self.pass_rate >= 80 else "yellow" if self.pass_rate >= 60 else "red"
            )

            summary_text = [
                f"Overall Score: {overall_bar} {self.avg_score:.2f}",
                f"\nTests Run: {self.total}",
                f"Passed: [green]{self.passed}[/green]",
                f"Failed: [red]{self.failed}[/red]",
                f"Pass Rate: [{overall_color}]{self.pass_rate:.1f}%[/{overall_color}]",
            ]

            summary_panel = Panel(
                "\n".join(summary_text),
                title="Summary",
                border_style=overall_color,
                expand=False,
                padding=(1, 2),
            )
            console.print(summary_panel)
            console.print()

            # Individual test results
            if self.results:
                test_details = []
                for result in self.results:
                    test_details.append(
                        {
                            "name": result.name,
                            "passed": result.passed,
                            "score": result.score,
                            "reason": result.details.get("feedback", "")[:100] + "..."
                            if len(result.details.get("feedback", "")) > 100
                            else result.details.get("feedback", ""),
                        }
                    )

                details_panel = create_test_details_tree(test_details)
                console.print(details_panel)
        else:
            # Fallback to simple table display
            table = Table(title="Batch Evaluation Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Total Tests", str(self.total))
            table.add_row("Passed", f"[green]{self.passed}[/green]")
            table.add_row("Failed", f"[red]{self.failed}[/red]")
            table.add_row("Pass Rate", f"{self.pass_rate:.1f}%")
            table.add_row("Average Score", f"{self.avg_score:.2f}")

            console.print(table)

    def export(self, path: str):
        """Export results to JSON file."""
        import json

        data = {
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "pass_rate": self.pass_rate,
                "avg_score": self.avg_score,
            },
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "score": r.score,
                    "details": r.details,
                    "metadata": r.metadata,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.results
            ],
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        console.print(f"\n[green]Results exported to {path}[/green]")


class BaseEval:
    """Base class for all simple evaluators."""

    def __init__(
        self,
        agent: str | Callable | Any,
        name: str = "Evaluation",
    ):
        """
        Initialize evaluator.

        Args:
            agent: Agent URL, callable function, or agent instance
            name: Name of the evaluation
        """
        # Validate agent input
        InputValidator.validate_agent_input(agent)

        self.agent = agent
        self.name = name
        self._client = None

    async def _get_client(self) -> Client | None:
        """Get or create ACP client if agent is a URL."""
        if isinstance(self.agent, str):
            if not self._client:
                self._client = Client(base_url=self.agent.rsplit("/agents", 1)[0])
            return self._client
        return None

    async def _run_agent(self, input_text: str, **kwargs) -> dict[str, Any]:
        """Run the agent and return response with metadata."""
        start_time = time.time()

        if isinstance(self.agent, str):
            if self.agent.startswith(("http://", "https://")):
                # Agent is a URL - use ACP client
                client = await self._get_client()
                agent_name = self.agent.split("/agents/")[-1]

                message = Message(
                    parts=[MessagePart(content=input_text, content_type="text/plain")]
                )

                try:
                    run = await client.run_sync(agent=agent_name, input=[message], **kwargs)
                except Exception as e:
                    # Wrap connection errors
                    raise AgentConnectionError(self.agent, e)

                # Wait for completion
                while run.status not in ["completed", "failed", "cancelled"]:
                    await asyncio.sleep(0.1)
                    run = await client.run_status(run_id=run.run_id)

                if run.status != "completed":
                    if run.status == "timeout":
                        raise AgentTimeoutError(self.agent, timeout_seconds=30)
                    else:
                        raise AgentConnectionError(
                            self.agent, Exception(f"Agent run failed with status: {run.status}")
                        )

                # Extract response text
                response_text = ""
                if run.output:
                    for msg in run.output:
                        for part in msg.parts:
                            if part.content:
                                response_text += part.content + "\n"

                return {
                    "response": response_text.strip(),
                    "run_id": str(run.run_id),
                    "latency_ms": (time.time() - start_time) * 1000,
                    "status": run.status,
                }
            else:
                # Agent is a string identifier - try to resolve it
                resolved_agent = self._resolve_agent_string(self.agent)

                # Call the resolved agent
                if asyncio.iscoroutinefunction(resolved_agent):
                    response = await resolved_agent(input_text, **kwargs)
                else:
                    response = resolved_agent(input_text, **kwargs)

                return {
                    "response": response,
                    "latency_ms": (time.time() - start_time) * 1000,
                }

        elif callable(self.agent):
            # Agent is a callable function
            if asyncio.iscoroutinefunction(self.agent) or (
                hasattr(self.agent, "__call__") and asyncio.iscoroutinefunction(self.agent.__call__)
            ):
                response = await self.agent(input_text, **kwargs)
            else:
                response = self.agent(input_text, **kwargs)

            return {
                "response": response,
                "latency_ms": (time.time() - start_time) * 1000,
            }

        else:
            # Agent is an instance with a run method
            if hasattr(self.agent, "run"):
                response = await self.agent.run(input_text, **kwargs)
            else:
                raise ValueError(f"Agent {type(self.agent)} does not have a run method")

            return {
                "response": response,
                "latency_ms": (time.time() - start_time) * 1000,
            }

    def _resolve_agent_string(self, agent_str: str):
        """Resolve a string identifier to an agent function."""
        import importlib.util
        import sys
        from pathlib import Path

        # Handle different formats:
        # 1. "file.py:function_name" - import function from file
        # 2. "module.function" - import from module
        # 3. "simple_name" - try to find locally

        if ":" in agent_str:
            # Format: file.py:function_name
            file_path, func_name = agent_str.split(":", 1)

            # Convert relative to absolute path
            if not file_path.startswith("/"):
                file_path = str(Path.cwd() / file_path)

            if not Path(file_path).exists():
                raise AgentConnectionError(agent_str, f"File not found: {file_path}")

            # Import the module
            spec = importlib.util.spec_from_file_location("agent_module", file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["agent_module"] = module
            spec.loader.exec_module(module)

            if not hasattr(module, func_name):
                raise AgentConnectionError(
                    agent_str, f"Function {func_name} not found in {file_path}"
                )

            return getattr(module, func_name)

        elif "." in agent_str:
            # Format: module.function
            try:
                module_name, func_name = agent_str.rsplit(".", 1)
                module = importlib.import_module(module_name)
                return getattr(module, func_name)
            except (ImportError, AttributeError) as e:
                raise AgentConnectionError(agent_str, f"Failed to import {agent_str}: {e}")

        else:
            # Simple name - try to find in current working directory
            potential_files = [
                f"{agent_str}.py",
                f"mock_{agent_str}.py",
                f"test_{agent_str}.py",
            ]

            for file_name in potential_files:
                file_path = Path.cwd() / file_name
                if file_path.exists():
                    # Import and look for function with same name
                    spec = importlib.util.spec_from_file_location("agent_module", file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Try different function name patterns
                    potential_func_names = [
                        agent_str,
                        f"my_{agent_str}",
                        f"{agent_str}_agent",
                        f"simple_{agent_str}",
                    ]

                    for func_name in potential_func_names:
                        if hasattr(module, func_name):
                            return getattr(module, func_name)

            raise AgentConnectionError(
                agent_str,
                f"Could not resolve agent '{agent_str}'. "
                f"Expected format: 'file.py:function', 'module.function', or existing file with function",
            )

    async def _cleanup(self):
        """Cleanup resources."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
