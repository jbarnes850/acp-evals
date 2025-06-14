"""
Swarm pattern: Decentralized coordination.

Agents work independently on the same task and results are aggregated.
Based on LangChain's research on swarm patterns.
"""

import asyncio
from collections import Counter
from datetime import datetime
from typing import Any

from acp_evals.patterns.base import AgentInfo, AgentPattern


class SwarmPattern(AgentPattern):
    """
    Swarm multi-agent pattern.

    All agents work on the same task independently, with results
    aggregated using various strategies (voting, consensus, etc.).
    """

    def __init__(
        self,
        agents: list[AgentInfo],
        aggregation_strategy: str = "majority_vote",
        name: str | None = None,
    ):
        """
        Initialize swarm pattern.

        Args:
            agents: List of agents in the swarm
            aggregation_strategy: How to combine results
            name: Optional pattern name
        """
        super().__init__(agents, name)
        self.aggregation_strategy = aggregation_strategy

    @property
    def pattern_type(self) -> str:
        return "swarm"

    async def execute(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute swarm pattern.

        Args:
            task: Task to execute
            context: Optional context

        Returns:
            Execution results with consensus tracking
        """
        start_time = datetime.now()

        # Create tasks for all agents
        agent_tasks = []
        for agent in self.agents:
            agent_task = self._execute_agent(agent, task, context)
            agent_tasks.append(agent_task)

        # Execute all agents concurrently
        agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)

        # Separate successful results from errors
        successful_results = []
        failed_results = []

        for result in agent_results:
            if isinstance(result, Exception):
                failed_results.append({"error": str(result)})
            elif isinstance(result, dict) and result.get("success"):
                successful_results.append(result)
            else:
                failed_results.append(result)

        # Aggregate results based on strategy
        if self.aggregation_strategy == "majority_vote":
            final_output, consensus_data = self._aggregate_majority_vote(successful_results)
        elif self.aggregation_strategy == "longest_common":
            final_output, consensus_data = self._aggregate_longest_common(successful_results)
        elif self.aggregation_strategy == "quality_weighted":
            final_output, consensus_data = self._aggregate_quality_weighted(successful_results)
        else:
            # Default to first successful result
            final_output = successful_results[0]["response"] if successful_results else ""
            consensus_data = {"strategy": "first_result"}

        end_time = datetime.now()

        # Calculate metrics
        response_diversity = self._calculate_diversity(successful_results)
        consensus_strength = len(successful_results) / len(self.agents) if self.agents else 0

        # Get average latency
        latencies = [r["latency"] for r in successful_results if "latency" in r]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        return {
            "pattern": self.pattern_type,
            "final_output": final_output,
            "individual_results": agent_results,
            "total_latency": (end_time - start_time).total_seconds(),
            "average_agent_latency": avg_latency,
            "agents_succeeded": len(successful_results),
            "agents_failed": len(failed_results),
            "consensus_strength": consensus_strength,
            "response_diversity": response_diversity,
            "aggregation_strategy": self.aggregation_strategy,
            "consensus_data": consensus_data,
            "success": len(successful_results) > 0,
        }

    async def _execute_agent(
        self,
        agent: AgentInfo,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a single agent in the swarm."""
        start_time = datetime.now()

        # Each agent gets the same prompt
        agent_prompt = f"""You are an agent in a swarm working on this task: {task}

{f"Additional context: {context}" if context else ""}

Provide your independent solution to this task."""

        try:
            client = self._get_client(agent)
            run = await client.run_sync(
                agent=agent.name,
                input=[self._create_message(agent_prompt)]
            )

            response = run.output[0].parts[0].content if run.output else ""

            return {
                "agent": agent.name,
                "response": response,
                "latency": (datetime.now() - start_time).total_seconds(),
                "response_length": len(response),
                "success": True,
            }

        except Exception as e:
            return {
                "agent": agent.name,
                "error": str(e),
                "latency": (datetime.now() - start_time).total_seconds(),
                "success": False,
            }

    def _aggregate_majority_vote(
        self,
        results: list[dict[str, Any]]
    ) -> tuple[str, dict[str, Any]]:
        """Aggregate using majority voting on key points."""
        if not results:
            return "", {"no_results": True}

        # Extract key points from each response
        all_points = []
        for result in results:
            response = result["response"]
            # Simple extraction: split by sentences and take substantive ones
            sentences = [s.strip() for s in response.split(".") if len(s.strip()) > 20]
            all_points.extend(sentences[:5])  # Take top 5 points from each

        # Count occurrences of similar points
        point_counts = Counter(all_points)

        # Build consensus response from most common points
        consensus_points = []
        for point, count in point_counts.most_common(10):
            if count >= len(results) / 2:  # Appears in at least half
                consensus_points.append(point)

        final_output = ". ".join(consensus_points) + "." if consensus_points else results[0]["response"]

        return final_output, {
            "total_points": len(all_points),
            "consensus_points": len(consensus_points),
            "agreement_threshold": 0.5,
        }

    def _aggregate_longest_common(
        self,
        results: list[dict[str, Any]]
    ) -> tuple[str, dict[str, Any]]:
        """Aggregate by finding longest common subsequences."""
        if not results:
            return "", {"no_results": True}

        # For simplicity, use the longest response that has common elements
        responses = [r["response"] for r in results]
        longest_response = max(responses, key=len)

        # Count how many responses share key terms
        key_terms = set(longest_response.lower().split())
        agreement_scores = []

        for response in responses:
            response_terms = set(response.lower().split())
            overlap = len(key_terms & response_terms) / len(key_terms)
            agreement_scores.append(overlap)

        avg_agreement = sum(agreement_scores) / len(agreement_scores)

        return longest_response, {
            "base_response_length": len(longest_response),
            "average_agreement": avg_agreement,
        }

    def _aggregate_quality_weighted(
        self,
        results: list[dict[str, Any]]
    ) -> tuple[str, dict[str, Any]]:
        """Aggregate weighted by response quality metrics."""
        if not results:
            return "", {"no_results": True}

        # Score each response
        scored_results = []
        for result in results:
            response = result["response"]

            # Simple quality heuristics
            score = 0
            score += min(len(response) / 100, 10)  # Length score (up to 10)
            score += response.count(".") * 0.5  # Sentence structure
            score += len(set(response.lower().split())) / 10  # Vocabulary diversity

            scored_results.append((score, result))

        # Sort by score and take the best
        scored_results.sort(key=lambda x: x[0], reverse=True)
        best_result = scored_results[0][1]

        return best_result["response"], {
            "best_score": scored_results[0][0],
            "worst_score": scored_results[-1][0] if scored_results else 0,
            "score_range": scored_results[0][0] - scored_results[-1][0] if len(scored_results) > 1 else 0,
        }

    def _calculate_diversity(self, results: list[dict[str, Any]]) -> float:
        """Calculate diversity of responses (0-1)."""
        if len(results) < 2:
            return 0.0

        # Simple diversity: average pairwise difference in word sets
        diversity_scores = []

        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                words1 = set(results[i]["response"].lower().split())
                words2 = set(results[j]["response"].lower().split())

                union = words1 | words2
                intersection = words1 & words2

                if union:
                    diversity = 1 - (len(intersection) / len(union))
                    diversity_scores.append(diversity)

        return sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0.0
