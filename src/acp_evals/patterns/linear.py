"""
Linear pattern: Sequential agent execution.

Each agent processes the output of the previous agent, similar to a pipeline.
Based on Cognition's finding that linear often beats parallel for many tasks.
"""

from datetime import datetime
from typing import Any

from acp_evals.patterns.base import AgentPattern


class LinearPattern(AgentPattern):
    """
    Linear/sequential multi-agent pattern.

    Agents process tasks one after another, with each agent
    receiving the previous agent's output as input.
    """

    @property
    def pattern_type(self) -> str:
        return "linear"

    async def execute(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute agents sequentially.

        Args:
            task: Initial task
            context: Optional context

        Returns:
            Execution results with handoff tracking
        """
        start_time = datetime.now()
        handoffs = []
        current_input = task

        # Track context that should be preserved
        if context:
            preserved_context = context.get("preserve", {})
        else:
            preserved_context = {}

        for i, agent in enumerate(self.agents):
            agent_start = datetime.now()

            # Prepare input for agent
            if i == 0:
                # First agent gets original task
                agent_input = current_input
            else:
                # Subsequent agents get previous output + any preserved context
                agent_input = f"""Previous agent output:
{current_input}

Original task: {task}
{f"Context to preserve: {preserved_context}" if preserved_context else ""}

Your role: {agent.role or 'Process the above information'}"""

            # Execute agent
            client = self._get_client(agent)
            message = self._create_message(agent_input)

            try:
                run = await client.run_sync(
                    agent=agent.name,
                    input=[message]
                )

                # Extract response
                if run.output and run.output[0].parts:
                    response = run.output[0].parts[0].content
                else:
                    response = ""

                agent_end = datetime.now()

                # Track handoff
                handoff = {
                    "step": i,
                    "agent": agent.name,
                    "input_length": len(agent_input),
                    "output_length": len(response),
                    "latency": (agent_end - agent_start).total_seconds(),
                    "preserved_context": self._check_context_preservation(
                        response, preserved_context
                    ) if i > 0 else None,
                }
                handoffs.append(handoff)

                # Update input for next agent
                current_input = response

            except Exception as e:
                # Handle failures
                handoff = {
                    "step": i,
                    "agent": agent.name,
                    "error": str(e),
                    "latency": (datetime.now() - agent_start).total_seconds(),
                }
                handoffs.append(handoff)
                break

        end_time = datetime.now()

        # Calculate information preservation across chain
        preservation_scores = [
            h["preserved_context"]
            for h in handoffs
            if h.get("preserved_context") is not None
        ]

        avg_preservation = (
            sum(preservation_scores) / len(preservation_scores)
            if preservation_scores else None
        )

        return {
            "pattern": self.pattern_type,
            "final_output": current_input,
            "handoffs": handoffs,
            "total_latency": (end_time - start_time).total_seconds(),
            "agents_used": len(handoffs),
            "information_preservation": avg_preservation,
            "success": not any(h.get("error") for h in handoffs),
        }

    def _check_context_preservation(
        self,
        response: str,
        preserved_context: dict[str, Any]
    ) -> float:
        """Check how well context was preserved in response."""
        if not preserved_context:
            return 1.0

        preserved_count = 0
        total_items = 0

        for key, value in preserved_context.items():
            total_items += 1
            if str(value).lower() in response.lower():
                preserved_count += 1

        return preserved_count / total_items if total_items > 0 else 1.0
