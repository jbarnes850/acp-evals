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
from rich.table import Table

from ..core.exceptions import AgentConnectionError, AgentTimeoutError
from ..core.validation import InputValidator

console = Console()


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
        """Print a summary of the result."""
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
        """Print a summary table of batch results."""
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
            # Agent is a URL - use ACP client
            client = await self._get_client()
            agent_name = self.agent.split("/agents/")[-1]

            message = Message(parts=[
                MessagePart(content=input_text, content_type="text/plain")
            ])

            try:
                run = await client.run_sync(
                    agent=agent_name,
                    input=[message],
                    **kwargs
                )
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
                        self.agent,
                        Exception(f"Agent run failed with status: {run.status}")
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

        elif callable(self.agent):
            # Agent is a callable function
            if asyncio.iscoroutinefunction(self.agent):
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

    async def _cleanup(self):
        """Cleanup resources."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None