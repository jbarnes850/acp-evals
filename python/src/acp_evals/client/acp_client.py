"""
ACP client wrapper for evaluation framework.

Provides enhanced client functionality for tracking events and metrics
during agent evaluation.
"""

import asyncio
from typing import Any

from acp_sdk.client import Client
from acp_sdk.models import (
    Agent as AgentManifest,
)
from acp_sdk.models import (
    Event,
    Message,
    MessagePart,
    Run,
)

from acp_evals.core.base import Metric, MetricResult


class ACPEvaluationClient:
    """
    Enhanced ACP client for evaluation purposes.

    Features:
    - Event collection during runs
    - Automatic metric calculation
    - Multi-agent support
    - Streaming and async evaluation
    """

    def __init__(
        self,
        base_url: str,
        metrics: list[Metric] | None = None,
        collect_events: bool = True,
    ):
        """
        Initialize evaluation client.

        Args:
            base_url: URL of the ACP server
            metrics: List of metrics to calculate automatically
            collect_events: Whether to collect events during runs
        """
        self.client = Client(base_url=base_url)
        self.metrics = metrics or []
        self.collect_events = collect_events
        self.events: list[Event] = []
        self._event_lock = asyncio.Lock()

    async def list_agents(self) -> list[AgentManifest]:
        """List available agents on the server."""
        return await self.client.agents()

    async def get_agent(self, agent_name: str) -> AgentManifest | None:
        """Get a specific agent by name."""
        agents = await self.list_agents()
        for agent in agents:
            if agent.name == agent_name:
                return agent
        return None

    def _create_message(self, content: str) -> Message:
        """Create a message from string content."""
        return Message(
            role="user",
            parts=[MessagePart(content=content, content_type="text/plain")],
        )

    async def run_with_tracking(
        self,
        agent_name: str,
        input: str | list[Message],
        session_id: str | None = None,
        run_options: dict[str, Any] | None = None,
    ) -> tuple[Run, list[Event], dict[str, MetricResult]]:
        """
        Run an agent with full event tracking and metric calculation.

        Args:
            agent_name: Name of the agent to run
            input: Input prompt or messages
            session_id: Optional session ID for continuity
            run_options: Additional options for the run

        Returns:
            Tuple of (run, events, metrics)
        """
        # Reset events for new run
        async with self._event_lock:
            self.events = []

        # Convert string input to messages
        if isinstance(input, str):
            messages = [self._create_message(input)]
        else:
            messages = input

        # Start the run
        run = await self.client.run_async(
            agent=agent_name,
            input=messages,
            session_id=session_id,
            **(run_options or {}),
        )

        # Collect events if enabled
        if self.collect_events:
            await self._collect_events(run.run_id)

        # Wait for run completion
        final_run = await self._wait_for_completion(run.run_id)

        # Calculate metrics
        metric_results = {}
        if self.metrics:
            for metric in self.metrics:
                try:
                    result = await metric.calculate(final_run, self.events)
                    metric_results[metric.name] = result
                except Exception as e:
                    print(f"Error calculating metric {metric.name}: {e}")

        return final_run, self.events, metric_results

    async def run_sync_simple(
        self,
        agent_name: str,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Simple synchronous run that returns just the response text.

        Args:
            agent_name: Name of the agent
            prompt: Input prompt
            **kwargs: Additional arguments

        Returns:
            Response text
        """
        run = await self.client.run_sync(
            agent=agent_name,
            input=[self._create_message(prompt)],
            **kwargs
        )

        # Extract response text
        if run.output:
            parts = []
            for message in run.output:
                for part in message.parts:
                    if part.content:
                        parts.append(part.content)
            return " ".join(parts)

        return ""

    async def _collect_events(self, run_id: str):
        """Collect events for a run."""
        try:
            async for event in self.client.run_events_stream(run_id=run_id):
                async with self._event_lock:
                    self.events.append(event)

                # Process specific event types if needed
                if event.type == "run.completed" or event.type == "run.failed":
                    break

        except Exception as e:
            print(f"Error collecting events: {e}")

    async def _wait_for_completion(
        self,
        run_id: str,
        timeout: float = 300.0,
        poll_interval: float = 0.5,
    ) -> Run:
        """Wait for a run to complete."""
        start_time = asyncio.get_event_loop().time()

        while True:
            run = await self.client.run(run_id=run_id)

            if run.status.is_terminal:
                return run

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")

            await asyncio.sleep(poll_interval)

    async def evaluate_streaming(
        self,
        agent_name: str,
        input: str | list[Message],
        callback: Any | None = None,
    ) -> tuple[Run, list[Event], dict[str, MetricResult]]:
        """
        Evaluate with streaming support.

        Args:
            agent_name: Name of the agent
            input: Input prompt or messages
            callback: Callback for streaming events

        Returns:
            Tuple of (run, events, metrics)
        """
        # Convert input
        if isinstance(input, str):
            messages = [self._create_message(input)]
        else:
            messages = input

        # Reset events
        async with self._event_lock:
            self.events = []

        # Start streaming run
        run = None
        async for event in self.client.run_stream(agent=agent_name, input=messages):
            async with self._event_lock:
                self.events.append(event)

            # Track run
            if event.type == "run.created":
                run = event.run
            elif event.type in ["run.completed", "run.failed"]:
                run = event.run

            # Call callback if provided
            if callback:
                await callback(event)

        # Calculate metrics
        metric_results = {}
        if self.metrics and run:
            for metric in self.metrics:
                try:
                    result = await metric.calculate(run, self.events)
                    metric_results[metric.name] = result
                except Exception as e:
                    print(f"Error calculating metric {metric.name}: {e}")

        return run, self.events, metric_results

    async def run_benchmark(
        self,
        agent_name: str,
        benchmark: Any,
        **benchmark_kwargs
    ) -> Any:
        """
        Run a benchmark against an agent.

        Args:
            agent_name: Name of the agent
            benchmark: Benchmark instance
            **benchmark_kwargs: Additional arguments for the benchmark

        Returns:
            BenchmarkResult
        """
        # Create agent wrapper that benchmark can use
        agent_wrapper = AgentWrapper(self, agent_name)

        # Run benchmark
        result = await benchmark.evaluate(agent_wrapper, **benchmark_kwargs)

        # Add metrics to benchmark result if available
        if hasattr(result, "metrics") and isinstance(result.metrics, dict):
            for metric in self.metrics:
                if metric.name not in result.metrics:
                    # Calculate aggregate metrics across all runs
                    # This is a simplified version - real implementation would aggregate properly
                    pass

        return result


class AgentWrapper:
    """Wrapper to make ACP client compatible with benchmark interfaces."""

    def __init__(self, client: ACPEvaluationClient, agent_name: str):
        self.client = client
        self.agent_name = agent_name
        self.name = agent_name

    async def run(self, prompt: str) -> str:
        """Run agent with a simple prompt."""
        return await self.client.run_sync_simple(self.agent_name, prompt)

    async def __call__(self, prompt: str) -> str:
        """Make wrapper callable."""
        return await self.run(prompt)
