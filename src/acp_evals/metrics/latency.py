"""
Latency metric for ACP agent evaluation.

Measures response times and identifies performance bottlenecks.
"""

from datetime import datetime

from acp_sdk.models import Event, Run

from acp_evals.core.base import Metric, MetricResult


class LatencyMetric(Metric):
    """
    Measures various latency aspects of agent execution.

    Tracks:
    - Total run time
    - Time to first token
    - Inter-message latency
    - Tool execution time
    """

    @property
    def name(self) -> str:
        return "latency"

    @property
    def description(self) -> str:
        return "Response time and latency analysis"

    def _parse_timestamp(self, timestamp: any) -> datetime | None:
        """Parse timestamp from various formats."""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return None
        return None

    async def calculate(self, run: Run, events: list[Event]) -> MetricResult:
        """Calculate latency metrics for a run."""
        if not events:
            return MetricResult(
                name=self.name,
                value=0.0,
                unit="seconds",
                breakdown={},
                metadata={"run_id": run.run_id},
            )

        # Get run start and end times
        start_time = run.created_at
        end_time = run.finished_at or datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Track various latency metrics
        first_user_message_time = None
        first_agent_message_time = None
        message_latencies = []
        tool_latencies = []

        last_message_time = start_time

        for event in events:
            event_time = None

            # Extract timestamp from event
            if hasattr(event, "timestamp"):
                event_time = self._parse_timestamp(event.timestamp)
            elif hasattr(event, "created_at"):
                event_time = self._parse_timestamp(event.created_at)

            if not event_time:
                continue

            if event.type == "message.created" and hasattr(event, "message"):
                message = event.message

                # Track first user message
                if message.role == "user" and not first_user_message_time:
                    first_user_message_time = event_time

                # Track first agent response
                if message.role in ["assistant", "agent"] and not first_agent_message_time:
                    first_agent_message_time = event_time

                # Calculate inter-message latency
                latency = (event_time - last_message_time).total_seconds()
                if latency > 0:
                    message_latencies.append(latency)

                last_message_time = event_time

            # Track tool execution time
            elif event.type == "tool.start":
                tool_start_time = event_time
            elif event.type == "tool.end" and tool_start_time:
                tool_duration = (event_time - tool_start_time).total_seconds()
                tool_latencies.append(tool_duration)
                tool_start_time = None

        # Calculate time to first token
        time_to_first_token = 0.0
        if first_user_message_time and first_agent_message_time:
            time_to_first_token = (first_agent_message_time - first_user_message_time).total_seconds()

        # Calculate average latencies
        avg_message_latency = sum(message_latencies) / len(message_latencies) if message_latencies else 0.0
        avg_tool_latency = sum(tool_latencies) / len(tool_latencies) if tool_latencies else 0.0

        breakdown = {
            "total_duration_seconds": total_duration,
            "time_to_first_token": time_to_first_token,
            "average_message_latency": avg_message_latency,
            "max_message_latency": max(message_latencies) if message_latencies else 0.0,
            "min_message_latency": min(message_latencies) if message_latencies else 0.0,
            "average_tool_latency": avg_tool_latency,
            "total_messages": len(message_latencies),
            "total_tool_calls": len(tool_latencies),
        }

        return MetricResult(
            name=self.name,
            value=total_duration,
            unit="seconds",
            breakdown=breakdown,
            metadata={
                "run_id": run.run_id,
                "run_status": run.status.value,
            },
        )
