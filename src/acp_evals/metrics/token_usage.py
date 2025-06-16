"""
Token usage metric for ACP agent evaluation.

This metric tracks token consumption across all aspects of agent execution,
providing detailed breakdowns and cost analysis.
"""

from collections import defaultdict

import tiktoken
from acp_sdk.models import Event, Message, MessagePart, Run

from acp_evals.core.base import Metric, MetricResult, TokenUsage


class TokenUsageMetric(Metric):
    """
    Primary metric for tracking token consumption with cost analysis.

    Features:
    - Accurate token counting using tiktoken
    - Model-specific pricing
    - Agent/subagent breakdown for multi-agent systems
    - Context window utilization tracking
    - Efficiency scoring
    """

    # Model pricing per 1K tokens (update as needed)
    MODEL_COSTS = {
        # OpenAI models
        "gpt-4.1": {"input": 0.03, "output": 0.06},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        # Anthropic models
        "claude-4-opus": {"input": 0.015, "output": 0.075},
        "claude-4-sonnet": {"input": 0.003, "output": 0.015},
        "claude-4-haiku": {"input": 0.00025, "output": 0.00125},
        # Default for unknown models
        "default": {"input": 0.01, "output": 0.03},
    }

    # Context window sizes (in tokens)
    CONTEXT_WINDOWS = {
        "gpt-4.1": 1000000,
        "gpt-4o": 128000,
        "claude-4-opus": 200000,
        "claude-4-sonnet": 200000,
        "claude-3.5-haiku": 200000,
        "default": 8192,
    }

    def __init__(self, model: str = "gpt-4.1", encoding: str | None = None):
        """
        Initialize the token usage metric.

        Args:
            model: The model being evaluated
            encoding: Tiktoken encoding to use (defaults to cl100k_base)
        """
        self.model = model
        self.encoding_name = encoding or "cl100k_base"

        try:
            self.encoder = tiktoken.get_encoding(self.encoding_name)
        except Exception:
            # Fallback to cl100k_base if specified encoding not available
            self.encoder = tiktoken.get_encoding("cl100k_base")

    @property
    def name(self) -> str:
        return "token_usage"

    @property
    def description(self) -> str:
        return "Comprehensive token usage tracking with cost analysis and efficiency scoring"

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        if not text:
            return 0
        return len(self.encoder.encode(text))

    def _count_message_part_tokens(self, part: MessagePart) -> int:
        """Count tokens in a message part."""
        tokens = 0

        # Count content tokens
        if part.content:
            tokens += self._count_tokens(part.content)

        # Add overhead for part structure (approximate)
        if part.name:
            tokens += self._count_tokens(part.name) + 1

        # Add tokens for content type specification
        if part.content_type and part.content_type != "text/plain":
            tokens += 2  # Approximate overhead for non-text content

        return tokens

    def _count_message_tokens(self, message: Message) -> int:
        """Count total tokens in a message."""
        tokens = 0

        # Count tokens in all parts
        for part in message.parts:
            tokens += self._count_message_part_tokens(part)

        # Add overhead for message structure
        # Role tokens (user/assistant/system)
        tokens += self._count_tokens(message.role) + 2

        # Message wrapper overhead (approximate)
        tokens += 3

        return tokens

    def _extract_agent_info(self, event: Event) -> tuple[str, str | None]:
        """Extract agent and subagent information from an event."""
        # Default agent
        agent_id = "main"
        subagent_id = None

        # Try to extract from event metadata or attributes
        if hasattr(event, "agent_id"):
            agent_id = event.agent_id
        elif hasattr(event, "metadata") and isinstance(event.metadata, dict):
            agent_id = event.metadata.get("agent_id", agent_id)
            subagent_id = event.metadata.get("subagent_id")

        # Parse agent role for multi-agent patterns (e.g., "agent/supervisor")
        if hasattr(event, "message") and hasattr(event.message, "role"):
            role = event.message.role
            if "/" in role and role.startswith("agent/"):
                parts = role.split("/", 1)
                if len(parts) > 1:
                    subagent_id = parts[1]

        return agent_id, subagent_id

    def _get_model_costs(self, model: str) -> dict[str, float]:
        """Get cost per 1K tokens for a model."""
        # Try exact match first
        if model in self.MODEL_COSTS:
            return self.MODEL_COSTS[model]

        # Try partial match (e.g., "gpt-4.1" matches "gpt-4.1")
        for model_key in self.MODEL_COSTS:
            if model.startswith(model_key):
                return self.MODEL_COSTS[model_key]

        # Default costs
        return self.MODEL_COSTS["default"]

    def _get_context_window(self, model: str) -> int:
        """Get context window size for a model."""
        # Try exact match first
        if model in self.CONTEXT_WINDOWS:
            return self.CONTEXT_WINDOWS[model]

        # Try partial match
        for model_key in self.CONTEXT_WINDOWS:
            if model.startswith(model_key):
                return self.CONTEXT_WINDOWS[model_key]

        # Default context window
        return self.CONTEXT_WINDOWS["default"]

    def _calculate_cost(self, usage: TokenUsage) -> float:
        """Calculate total cost in USD."""
        costs = self._get_model_costs(usage.model)

        input_cost = (usage.input_tokens / 1000) * costs["input"]
        output_cost = (usage.output_tokens / 1000) * costs["output"]

        # Tool tokens typically count as input tokens for pricing
        tool_cost = (usage.tool_tokens / 1000) * costs["input"]

        return input_cost + output_cost + tool_cost

    async def calculate(self, run: Run, events: list[Event]) -> MetricResult:
        """
        Calculate token usage metrics for a run.

        Args:
            run: The ACP run to analyze
            events: List of events from the run

        Returns:
            MetricResult with detailed token usage breakdown
        """
        usage = TokenUsage(
            input_tokens=0,
            output_tokens=0,
            tool_tokens=0,
            total_tokens=0,
            cost_usd=0.0,
            model=self.model,
            context_percentage=0.0,
            agent_breakdown=defaultdict(lambda: {"input": 0, "output": 0, "tool": 0}),
        )

        # Track cumulative context size
        cumulative_tokens = 0
        max_context_used = 0

        for event in events:
            if event.type == "message.created" and hasattr(event, "message"):
                message = event.message

                agent_id, subagent_id = self._extract_agent_info(event)

                # Check if pre-calculated tokens are available
                if hasattr(event, "data") and "tokens" in event.data:
                    token_data = event.data["tokens"]
                    input_tokens = token_data.get("input", 0)
                    output_tokens = token_data.get("output", 0)

                    usage.input_tokens += input_tokens
                    usage.output_tokens += output_tokens
                    usage.agent_breakdown[agent_id]["input"] += input_tokens
                    usage.agent_breakdown[agent_id]["output"] += output_tokens
                    if subagent_id:
                        usage.agent_breakdown[f"{agent_id}/{subagent_id}"]["input"] += input_tokens
                        usage.agent_breakdown[f"{agent_id}/{subagent_id}"]["output"] += output_tokens

                    tokens = input_tokens + output_tokens
                else:
                    # Count tokens from message content
                    tokens = self._count_message_tokens(message)

                    # Categorize tokens by message role
                    if message.role == "user":
                        usage.input_tokens += tokens
                        usage.agent_breakdown[agent_id]["input"] += tokens
                        if subagent_id:
                            usage.agent_breakdown[f"{agent_id}/{subagent_id}"]["input"] += tokens

                    elif message.role.startswith("agent") or message.role == "assistant":
                        usage.output_tokens += tokens
                        usage.agent_breakdown[agent_id]["output"] += tokens
                        if subagent_id:
                            usage.agent_breakdown[f"{agent_id}/{subagent_id}"]["output"] += tokens

                    elif message.role == "tool" or message.role == "function":
                        usage.tool_tokens += tokens
                        usage.agent_breakdown[agent_id]["tool"] += tokens
                        if subagent_id:
                            usage.agent_breakdown[f"{agent_id}/{subagent_id}"]["tool"] += tokens

                # Track cumulative context
                cumulative_tokens += tokens
                max_context_used = max(max_context_used, cumulative_tokens)

            # Handle tool events
            elif event.type == "tool.called" and hasattr(event, "data") and "tokens" in event.data:
                token_data = event.data["tokens"]
                input_tokens = token_data.get("input", 0)
                output_tokens = token_data.get("output", 0)

                usage.tool_tokens += input_tokens + output_tokens

                agent_id, subagent_id = self._extract_agent_info(event)
                usage.agent_breakdown[agent_id]["tool"] += input_tokens + output_tokens
                if subagent_id:
                    usage.agent_breakdown[f"{agent_id}/{subagent_id}"]["tool"] += input_tokens + output_tokens

                cumulative_tokens += input_tokens + output_tokens
                max_context_used = max(max_context_used, cumulative_tokens)

            # Handle message parts separately if needed
            elif event.type == "message.part" and hasattr(event, "part"):
                # These are typically streamed parts, count them as output
                tokens = self._count_message_part_tokens(event.part)
                usage.output_tokens += tokens
                cumulative_tokens += tokens
                max_context_used = max(max_context_used, cumulative_tokens)

        # Calculate totals
        usage.total_tokens = usage.input_tokens + usage.output_tokens + usage.tool_tokens
        usage.cost_usd = self._calculate_cost(usage)

        # Calculate context window utilization
        context_window = self._get_context_window(self.model)
        usage.context_percentage = (max_context_used / context_window) * 100 if context_window > 0 else 0.0

        # Calculate efficiency score
        efficiency_score = usage.efficiency_score

        # Prepare breakdown
        breakdown = {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "tool_tokens": usage.tool_tokens,
            "cost_usd": usage.cost_usd,
            "efficiency_score": efficiency_score,
            "agent_breakdown": dict(usage.agent_breakdown),
            "tokens_per_message": usage.total_tokens / len(events) if events else 0,
            "context_percentage": usage.context_percentage,
            "max_context_tokens": max_context_used,
            "cost_per_1k_tokens": (usage.cost_usd / usage.total_tokens) * 1000 if usage.total_tokens > 0 else 0,
        }

        # Add multi-agent specific metrics if applicable
        if len(usage.agent_breakdown) > 1:
            breakdown["multi_agent_overhead"] = self._calculate_multi_agent_overhead(usage)
            breakdown["agent_token_distribution"] = self._calculate_agent_distribution(usage)

        return MetricResult(
            name=self.name,
            value=usage.total_tokens,
            unit="tokens",
            breakdown=breakdown,
            metadata={
                "model": self.model,
                "run_id": run.run_id,
                "run_status": run.status.value if hasattr(run.status, 'value') else run.status,
                "encoding": self.encoding_name,
            },
        )

    def _calculate_multi_agent_overhead(self, usage: TokenUsage) -> float:
        """Calculate the overhead of multi-agent vs single agent (as percentage)."""
        if not usage.agent_breakdown:
            return 0.0

        # Estimate single-agent tokens (main agent only)
        main_agent_tokens = usage.agent_breakdown.get("main", {})
        single_agent_estimate = sum(main_agent_tokens.values())

        if single_agent_estimate == 0:
            # Use the agent with most tokens as baseline
            totals = {
                agent: sum(tokens.values())
                for agent, tokens in usage.agent_breakdown.items()
            }
            single_agent_estimate = max(totals.values()) if totals else 0

        # Calculate overhead
        if single_agent_estimate > 0:
            overhead = ((usage.total_tokens - single_agent_estimate) / single_agent_estimate) * 100
            return max(0.0, overhead)  # Ensure non-negative

        return 0.0

    def _calculate_agent_distribution(self, usage: TokenUsage) -> dict[str, float]:
        """Calculate token distribution across agents (as percentages)."""
        distribution = {}

        for agent, tokens in usage.agent_breakdown.items():
            agent_total = sum(tokens.values())
            if usage.total_tokens > 0:
                distribution[agent] = (agent_total / usage.total_tokens) * 100
            else:
                distribution[agent] = 0.0

        return distribution
