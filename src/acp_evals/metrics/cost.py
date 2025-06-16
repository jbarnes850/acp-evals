"""
Cost metric for ACP agent evaluation.

Provides detailed cost analysis and projections for agent operations.
"""


from acp_sdk.models import Event, Run

from acp_evals.core.base import Metric, MetricResult


class CostMetric(Metric):
    """
    Comprehensive cost analysis for agent operations.

    Features:
    - Per-run cost calculation
    - Cost projections (hourly, daily, monthly)
    - Cost per successful completion
    - Multi-agent cost multiplication analysis
    """

    def __init__(self, base_costs: dict[str, float] | None = None):
        """
        Initialize cost metric.

        Args:
            base_costs: Override default cost structure
        """
        self.base_costs = base_costs or {
            "token_multiplier": 1.0,  # Adjust for specific pricing
            "fixed_per_run": 0.0,     # Fixed cost per run if any
            "tool_call_cost": 0.0001,  # Cost per tool call
        }

    @property
    def name(self) -> str:
        return "cost_analysis"

    @property
    def description(self) -> str:
        return "Comprehensive cost analysis with projections and efficiency metrics"

    def _calculate_projections(self, run_cost: float, run_duration_seconds: float) -> dict[str, float]:
        """Calculate cost projections for various time periods."""
        if run_duration_seconds <= 0:
            return {
                "per_hour": 0.0,
                "per_day": 0.0,
                "per_week": 0.0,
                "per_month": 0.0,
                "per_year": 0.0,
            }

        runs_per_hour = 3600 / run_duration_seconds

        return {
            "per_hour": run_cost * runs_per_hour,
            "per_day": run_cost * runs_per_hour * 24,
            "per_week": run_cost * runs_per_hour * 24 * 7,
            "per_month": run_cost * runs_per_hour * 24 * 30,
            "per_year": run_cost * runs_per_hour * 24 * 365,
        }

    def _analyze_cost_drivers(self, events: list[Event], token_cost: float) -> dict[str, any]:
        """Identify primary cost drivers."""
        tool_calls = 0
        message_count = 0
        agents_involved = set()

        for event in events:
            if event.type == "message.created":
                message_count += 1
                # Track unique agents
                if hasattr(event, "message") and hasattr(event.message, "role"):
                    role = event.message.role
                    if role.startswith("agent/"):
                        agents_involved.add(role)
            elif event.type in ["tool.call", "function.call"]:
                tool_calls += 1

        # Calculate cost breakdown
        tool_cost = tool_calls * self.base_costs.get("tool_call_cost", 0)
        fixed_cost = self.base_costs.get("fixed_per_run", 0)

        total_cost = token_cost + tool_cost + fixed_cost

        drivers = {
            "token_cost": token_cost,
            "token_cost_percentage": (token_cost / total_cost * 100) if total_cost > 0 else 0,
            "tool_cost": tool_cost,
            "tool_cost_percentage": (tool_cost / total_cost * 100) if total_cost > 0 else 0,
            "fixed_cost": fixed_cost,
            "message_count": message_count,
            "tool_calls": tool_calls,
            "agents_involved": len(agents_involved),
        }

        # Identify primary driver
        if drivers["token_cost_percentage"] > 80:
            drivers["primary_driver"] = "tokens"
            drivers["optimization_suggestion"] = "Focus on reducing token usage through better prompts or context management"
        elif drivers["tool_cost_percentage"] > 50:
            drivers["primary_driver"] = "tools"
            drivers["optimization_suggestion"] = "Optimize tool usage patterns or batch tool calls"
        else:
            drivers["primary_driver"] = "balanced"
            drivers["optimization_suggestion"] = "Cost is well-balanced; optimize based on use case"

        return drivers

    async def calculate(self, run: Run, events: list[Event]) -> MetricResult:
        """Calculate comprehensive cost metrics."""
        # First, we need token cost from events
        # In a real implementation, this would come from TokenUsageMetric
        token_cost = 0.0
        token_count = 0

        # Estimate token cost from events
        for event in events:
            if hasattr(event, "metadata") and isinstance(event.metadata, dict):
                # Look for token usage in metadata
                token_cost += event.metadata.get("token_cost", 0.0)
                token_count += event.metadata.get("token_count", 0)

        # If no token cost in metadata, estimate
        if token_cost == 0.0:
            # Rough estimation: 1000 tokens ≈ $0.03
            estimated_tokens = len(events) * 50  # Rough estimate
            token_cost = (estimated_tokens / 1000) * 0.03 * self.base_costs["token_multiplier"]
            token_count = estimated_tokens

        # Calculate run duration
        if run.finished_at and run.created_at:
            run_duration = (run.finished_at - run.created_at).total_seconds()
        else:
            run_duration = 60  # Default 1 minute if not available

        # Analyze cost drivers
        cost_drivers = self._analyze_cost_drivers(events, token_cost)
        total_cost = cost_drivers["token_cost"] + cost_drivers["tool_cost"] + cost_drivers["fixed_cost"]

        # Calculate projections
        projections = self._calculate_projections(total_cost, run_duration)

        # Calculate efficiency metrics
        cost_per_token = total_cost / token_count if token_count > 0 else 0

        # Cost per completion (only for successful runs)
        if run.status.value == "completed":
            cost_per_success = total_cost
        else:
            cost_per_success = float('inf')  # Infinite cost for failed runs

        breakdown = {
            "total_cost": total_cost,
            "cost_drivers": cost_drivers,
            "projections": projections,
            "cost_per_token": cost_per_token,
            "cost_per_success": cost_per_success,
            "run_duration_seconds": run_duration,
            "multi_agent_multiplier": cost_drivers["agents_involved"] if cost_drivers["agents_involved"] > 1 else 1,
        }

        # Add recommendations based on cost
        if total_cost > 0.10:  # More than 10 cents per run
            breakdown["recommendation"] = "High cost per run - consider optimization"
        elif projections["per_month"] > 1000:  # More than $1000/month at current rate
            breakdown["recommendation"] = "Projected monthly cost exceeds $1000 - review architecture"

        return MetricResult(
            name=self.name,
            value=total_cost,
            unit="USD",
            breakdown=breakdown,
            metadata={
                "run_id": run.run_id,
                "run_status": run.status.value,
                "token_count_estimated": token_count,
            },
        )
