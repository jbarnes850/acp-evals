"""
Reliability evaluation for agent tool usage and error handling.

This module provides the ReliabilityEval class for evaluating agent reliability,
including tool usage tracking, error handling, and retry behavior.
"""

import asyncio
import time
from collections.abc import Callable
from typing import Any

from acp_sdk.models import Message, MessagePart
from rich.progress import Progress, SpinnerColumn, TextColumn

from .common import BaseEval, EvalResult, console


class ReliabilityEval(BaseEval):
    """
    Evaluate agent reliability and tool usage.

    Example:
        reliability = ReliabilityEval(agent=my_agent)
        result = await reliability.run(
            input="Search for papers and summarize",
            expected_tools=["search", "summarize"],
            print_results=True
        )
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        tool_definitions: list[str] | None = None,
        name: str = "Reliability Evaluation",
    ):
        """
        Initialize reliability evaluator.

        Args:
            agent: Agent to evaluate
            tool_definitions: List of available tools
            name: Name of the evaluation
        """
        super().__init__(agent, name)
        self.tool_definitions = tool_definitions or []

    async def run(
        self,
        input: str,
        expected_tools: list[str] | None = None,
        test_error_handling: bool = False,
        test_retry: bool = False,
        print_results: bool = False,
    ) -> EvalResult:
        """
        Run reliability evaluation.

        Args:
            input: Input to send to agent
            expected_tools: Tools expected to be used
            test_error_handling: Test error handling
            test_retry: Test retry behavior
            print_results: Whether to print results

        Returns:
            EvalResult with reliability metrics
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Testing reliability...", total=None)

            # For ACP agents, we need to track events to capture tool usage
            events_collected = []

            if isinstance(self.agent, str) and self.agent.startswith(("http://", "https://")):
                # ACP agent - collect events during execution
                client = await self._get_client()
                if not client:
                    raise ValueError("Failed to create ACP client")

                agent_name = self.agent.split("/agents/")[-1]

                message = Message(parts=[MessagePart(content=input, content_type="text/plain")])

                try:
                    # Start run
                    run = await client.run_async(agent=agent_name, input=[message])

                    # Collect events in parallel with run
                    event_collection_task = asyncio.create_task(
                        self._collect_events(client, str(run.run_id), events_collected)
                    )

                    # Wait for completion
                    while run.status not in ["completed", "failed", "cancelled"]:
                        await asyncio.sleep(0.1)
                        run = await client.run_status(run_id=str(run.run_id))

                    # Stop event collection
                    event_collection_task.cancel()
                    try:
                        await event_collection_task
                    except asyncio.CancelledError:
                        pass

                    # Extract response
                    response_text = ""
                    if run.output:
                        for msg in run.output:
                            for part in msg.parts:
                                if part.content:
                                    response_text += part.content + "\n"

                    agent_result = {
                        "response": response_text.strip(),
                        "run_id": str(run.run_id),
                        "status": run.status,
                        "events": events_collected,
                    }

                except Exception as e:
                    agent_result = {
                        "response": "",
                        "status": "failed",
                        "error": str(e),
                        "events": events_collected,
                    }
            else:
                # Non-ACP agent - run normally
                agent_result = await self._run_agent(input)
                agent_result["events"] = []

            progress.update(task, description="Analyzing behavior...")

        details = {}
        passed = True
        score = 1.0

        # Check if response was successful
        if agent_result.get("status") == "failed":
            passed = False
            score = 0.0
            details["error"] = agent_result.get("error", "Agent failed to respond")
            details["reliability_score"] = 0.0
        else:
            details["reliability_score"] = 1.0

        # Tool usage verification from events
        if expected_tools:
            tools_used = []
            tool_calls_details = []

            # Extract tool usage from events
            for event in agent_result.get("events", []):
                if event.get("type") == "tool.call" or event.get("type") == "tools.use":
                    tool_name = event.get("data", {}).get("tool_name") or event.get("data", {}).get(
                        "name"
                    )
                    if tool_name:
                        tools_used.append(tool_name)
                        tool_calls_details.append(
                            {
                                "tool": tool_name,
                                "timestamp": event.get("timestamp"),
                                "status": event.get("data", {}).get("status", "unknown"),
                            }
                        )

            # If no events but response mentions tools, do text analysis as fallback
            if not tools_used and agent_result.get("response"):
                response_lower = agent_result["response"].lower()
                for tool in expected_tools:
                    if tool.lower() in response_lower:
                        tools_used.append(tool)
                        tool_calls_details.append(
                            {
                                "tool": tool,
                                "source": "text_analysis",
                                "confidence": "low",
                            }
                        )

            # Calculate coverage
            tools_used_set = set(tools_used)
            expected_tools_set = set(expected_tools)
            tools_found = tools_used_set.intersection(expected_tools_set)

            details["expected_tools"] = expected_tools
            details["tools_used"] = list(tools_used_set)
            details["tool_calls"] = tool_calls_details
            details["tool_coverage"] = (
                len(tools_found) / len(expected_tools_set) if expected_tools_set else 1.0
            )
            details["unexpected_tools"] = list(tools_used_set - expected_tools_set)

            # Adjust score based on tool coverage
            if details["tool_coverage"] < 1.0:
                score *= details["tool_coverage"]
                if details["tool_coverage"] < 0.5:
                    passed = False

        # Error handling test
        if test_error_handling:
            error_test_result = await self._test_error_handling(input)
            details["error_handling"] = error_test_result
            if not error_test_result.get("passed", False):
                score *= 0.8

        # Retry test
        if test_retry:
            retry_test_result = await self._test_retry_behavior(input)
            details["retry_behavior"] = retry_test_result
            if not retry_test_result.get("passed", False):
                score *= 0.9

        # Event statistics
        if agent_result.get("events"):
            event_types = {}
            for event in agent_result["events"]:
                event_type = event.get("type", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            details["event_statistics"] = event_types
            details["total_events"] = len(agent_result["events"])

        result = EvalResult(
            name=self.name,
            passed=passed,
            score=score,
            details=details,
            metadata={
                "input": input,
                "response": agent_result.get("response", ""),
                "run_id": agent_result.get("run_id"),
            },
        )

        if print_results:
            # Use rich display components for comprehensive reliability evaluation details
            from ..cli.display import display_single_evaluation_result

            display_single_evaluation_result(
                evaluation_type="reliability",
                agent_identifier=str(self.agent),
                input_text=input,
                result=result,
                show_details=True,
                show_performance=True,
            )

        return result

    async def _collect_events(self, client, run_id: str, events_list: list):
        """Collect events from ACP run."""
        try:
            async for event in client.run_events_stream(run_id=run_id):
                events_list.append(
                    {
                        "type": event.type,
                        "timestamp": event.timestamp.isoformat()
                        if hasattr(event.timestamp, "isoformat")
                        else str(event.timestamp),
                        "data": event.data if hasattr(event, "data") else {},
                    }
                )
        except Exception:
            # Event collection might be cancelled, that's okay
            pass

    async def _test_error_handling(self, original_input: str) -> dict[str, Any]:
        """Test agent's error handling capabilities."""
        # Test with invalid input
        test_inputs = [
            "",  # Empty input
            "a" * 10000,  # Very long input
            "Please divide by zero: 1/0",  # Mathematical error
            "Access undefined variable: {{undefined_var}}",  # Template error
        ]

        errors_handled = 0
        total_tests = len(test_inputs)

        for test_input in test_inputs:
            try:
                result = await self._run_agent(test_input)
                if result.get("response") and "error" not in result.get("response", "").lower():
                    errors_handled += 1
            except Exception:
                # Agent crashed - not handled well
                pass

        return {
            "passed": errors_handled == total_tests,
            "errors_handled": errors_handled,
            "total_tests": total_tests,
            "score": errors_handled / total_tests,
        }

    async def _test_retry_behavior(self, input: str) -> dict[str, Any]:
        """Test agent's retry behavior on transient failures."""
        attempts = []

        for i in range(3):
            start_time = time.time()
            try:
                await self._run_agent(input)
                attempts.append(
                    {
                        "attempt": i + 1,
                        "success": True,
                        "latency": time.time() - start_time,
                    }
                )
                break
            except Exception as e:
                attempts.append(
                    {
                        "attempt": i + 1,
                        "success": False,
                        "error": str(e),
                        "latency": time.time() - start_time,
                    }
                )

        # Check if retry pattern shows backoff
        has_backoff = False
        if len(attempts) > 1:
            latencies = [a["latency"] for a in attempts]
            has_backoff = all(latencies[i] < latencies[i + 1] for i in range(len(latencies) - 1))

        return {
            "passed": any(a["success"] for a in attempts),
            "attempts": attempts,
            "has_backoff": has_backoff,
        }
