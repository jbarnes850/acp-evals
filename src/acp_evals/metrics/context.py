"""
Context efficiency metric for ACP agent evaluation.

Measures how efficiently agents use their context window and handle
context degradation.
"""


from acp_sdk.models import Event, Message, Run

from acp_evals.core.base import Metric, MetricResult


class ContextEfficiencyMetric(Metric):
    """
    Measures context window utilization and efficiency.

    Key measurements:
    - Context window usage percentage
    - Context compression effectiveness
    - Redundant information ratio
    - Context switching overhead
    """

    def __init__(self, context_window_size: int | None = None):
        """
        Initialize context efficiency metric.

        Args:
            context_window_size: Override context window size (in tokens)
        """
        self.context_window_size = context_window_size

    @property
    def name(self) -> str:
        return "context_efficiency"

    @property
    def description(self) -> str:
        return "Context window utilization and management efficiency"

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation without tiktoken."""
        # Approximate: 1 token ≈ 4 characters
        return len(text) // 4

    def _calculate_message_tokens(self, message: Message) -> int:
        """Estimate tokens in a message."""
        tokens = 0
        for part in message.parts:
            if part.content:
                tokens += self._estimate_tokens(part.content)
        return tokens

    def _analyze_redundancy(self, messages: list[Message]) -> float:
        """Calculate redundancy ratio in message history."""
        if len(messages) < 2:
            return 0.0

        # Track unique content chunks
        content_chunks = set()
        total_chunks = 0

        for message in messages:
            for part in message.parts:
                if part.content:
                    # Split into sentences/chunks
                    chunks = part.content.split('. ')
                    for chunk in chunks:
                        chunk = chunk.strip()
                        if len(chunk) > 10:  # Ignore very short chunks
                            total_chunks += 1
                            content_chunks.add(chunk.lower())

        if total_chunks == 0:
            return 0.0

        unique_ratio = len(content_chunks) / total_chunks
        redundancy_ratio = 1.0 - unique_ratio

        return redundancy_ratio

    def _identify_context_switches(self, events: list[Event]) -> list[dict[str, any]]:
        """Identify context switches in the conversation."""
        switches = []
        last_topic = None

        for i, event in enumerate(events):
            if event.type == "message.created" and hasattr(event, "message"):
                message = event.message

                # Simple topic detection based on keywords
                content = " ".join(part.content or "" for part in message.parts)

                # Detect major topic shifts (simplified)
                current_topic = self._extract_topic(content)

                if last_topic and current_topic != last_topic:
                    switches.append({
                        "event_index": i,
                        "from_topic": last_topic,
                        "to_topic": current_topic,
                        "message_role": message.role,
                    })

                if current_topic:
                    last_topic = current_topic

        return switches

    def _extract_topic(self, content: str) -> str | None:
        """Simple topic extraction (can be enhanced)."""
        content_lower = content.lower()

        # Define topic keywords
        topics = {
            "code": ["function", "class", "code", "program", "script", "debug"],
            "data": ["data", "database", "query", "table", "csv", "json"],
            "config": ["config", "setting", "parameter", "option", "preference"],
            "error": ["error", "exception", "bug", "issue", "problem"],
            "help": ["help", "how", "what", "explain", "understand"],
        }

        for topic, keywords in topics.items():
            if any(keyword in content_lower for keyword in keywords):
                return topic

        return "general"

    async def calculate(self, run: Run, events: list[Event]) -> MetricResult:
        """Calculate context efficiency metrics."""
        messages = []
        cumulative_tokens = 0
        max_tokens = 0
        token_history = []

        # Extract messages and calculate token usage
        for event in events:
            if event.type == "message.created" and hasattr(event, "message"):
                message = event.message
                messages.append(message)

                # Calculate tokens for this message
                message_tokens = self._calculate_message_tokens(message)
                cumulative_tokens += message_tokens
                max_tokens = max(max_tokens, cumulative_tokens)

                token_history.append({
                    "cumulative": cumulative_tokens,
                    "message_tokens": message_tokens,
                    "role": message.role,
                })

        # Determine context window size
        if self.context_window_size:
            window_size = self.context_window_size
        else:
            # Default to 8K tokens if not specified
            window_size = 8192

        # Calculate metrics
        utilization_percentage = (max_tokens / window_size) * 100 if window_size > 0 else 0.0
        redundancy_ratio = self._analyze_redundancy(messages)
        context_switches = self._identify_context_switches(events)

        # Calculate average tokens per message by role
        role_tokens = {"user": [], "assistant": [], "tool": []}
        for item in token_history:
            role = item["role"]
            if role in role_tokens:
                role_tokens[role].append(item["message_tokens"])
            elif role.startswith("agent"):
                role_tokens["assistant"].append(item["message_tokens"])

        avg_tokens_by_role = {
            role: sum(tokens) / len(tokens) if tokens else 0
            for role, tokens in role_tokens.items()
        }

        # Context compression ratio (how much context grows vs information added)
        if len(token_history) > 1:
            first_quarter_tokens = token_history[len(token_history)//4]["cumulative"]
            last_quarter_tokens = token_history[-1]["cumulative"] - token_history[3*len(token_history)//4]["cumulative"]
            compression_ratio = first_quarter_tokens / last_quarter_tokens if last_quarter_tokens > 0 else 1.0
        else:
            compression_ratio = 1.0

        breakdown = {
            "utilization_percentage": utilization_percentage,
            "max_tokens_used": max_tokens,
            "context_window_size": window_size,
            "redundancy_ratio": redundancy_ratio,
            "context_switches": len(context_switches),
            "compression_ratio": compression_ratio,
            "average_tokens_by_role": avg_tokens_by_role,
            "total_messages": len(messages),
            "tokens_at_completion": cumulative_tokens,
        }

        # Add warnings if context is near limits
        if utilization_percentage > 90:
            breakdown["warning"] = "Context window nearly full - may impact performance"
        elif utilization_percentage > 75:
            breakdown["warning"] = "High context utilization - consider context management"

        return MetricResult(
            name=self.name,
            value=utilization_percentage,
            unit="percentage",
            breakdown=breakdown,
            metadata={
                "run_id": run.run_id,
                "run_status": run.status.value,
                "message_count": len(messages),
            },
        )
