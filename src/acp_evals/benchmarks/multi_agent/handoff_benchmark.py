"""
Handoff quality benchmark for multi-agent systems.

Tests information preservation across agent handoffs based on
Cognition's research on context sharing and decision preservation.
"""

from datetime import datetime
from typing import Any

from acp_evals.core.base import Benchmark, BenchmarkResult, BenchmarkTask
from acp_evals.metrics import HandoffQualityMetric
from acp_evals.patterns import AgentInfo, LinearPattern


class HandoffQualityBenchmark(Benchmark):
    """
    Measures information preservation across agent handoffs.

    Tests the "telephone game" effect in multi-agent systems
    and identifies patterns that best preserve information.
    """

    def __init__(
        self,
        chain_lengths: list[int] | None = None,
        test_scenarios: list[BenchmarkTask] | None = None,
    ):
        """
        Initialize handoff quality benchmark.

        Args:
            chain_lengths: Number of agents in chains to test
            test_scenarios: Custom scenarios (default: built-in)
        """
        self.chain_lengths = chain_lengths or [2, 3, 5]
        self.test_scenarios = test_scenarios or self._create_default_scenarios()
        self.handoff_metric = HandoffQualityMetric()

    @property
    def name(self) -> str:
        return "handoff_quality"

    @property
    def description(self) -> str:
        return "Tests information preservation across agent handoffs"

    @property
    def categories(self) -> list[str]:
        return ["multi_agent", "robustness", "communication"]

    def _create_default_scenarios(self) -> list[BenchmarkTask]:
        """Create scenarios that test different aspects of handoff quality."""
        return [
            # Scenario 1: Preserve specific constraints
            BenchmarkTask(
                id="project_requirements",
                prompt="""You are starting a project with these requirements:
                - Budget: $50,000
                - Deadline: March 15, 2025
                - Team size: 5 developers
                - Technology: Python and React
                - Must include: user authentication, real-time updates, mobile support
                - Security requirement: SOC 2 compliance

                Pass this information to the next agent for implementation planning.""",
                expected_output={
                    "constraints": [
                        "$50,000", "March 15, 2025", "5 developers",
                        "Python", "React", "user authentication",
                        "real-time updates", "mobile support", "SOC 2"
                    ],
                },
                category="constraints",
                metadata={"critical_elements": 9},
            ),

            # Scenario 2: Preserve decisions and rationale
            BenchmarkTask(
                id="technical_decisions",
                prompt="""Based on our analysis, we've made these technical decisions:
                1. Use PostgreSQL for the database (better for complex queries)
                2. Implement microservices architecture (scalability requirement)
                3. Deploy on AWS using EKS (existing team expertise)
                4. Use Redis for caching (performance optimization)
                5. Implement CI/CD with GitHub Actions (cost-effective)

                Each decision was made for the specific reason noted. Ensure the next agent understands both the decisions and their rationale.""",
                expected_output={
                    "decisions": [
                        "PostgreSQL", "microservices", "AWS", "EKS",
                        "Redis", "GitHub Actions"
                    ],
                    "rationales": [
                        "complex queries", "scalability", "team expertise",
                        "performance", "cost-effective"
                    ],
                },
                category="decisions",
                metadata={"decision_count": 5, "requires_rationale": True},
            ),

            # Scenario 3: Complex multi-step instructions
            BenchmarkTask(
                id="deployment_steps",
                prompt="""Follow these deployment steps in order:
                1. First, create a backup of the production database
                2. Then, deploy the new API version to staging
                3. Run the integration test suite (must pass 100%)
                4. If tests pass, create a maintenance window for 2 AM EST
                5. During maintenance, migrate the database schema
                6. Deploy the new frontend to CDN
                7. Clear all caches and restart services
                8. Verify health checks on all endpoints
                9. If any issues, rollback using the backup from step 1

                The order is critical. Pass these instructions to the next agent.""",
                expected_output={
                    "steps": [
                        "backup", "staging", "integration test", "100%",
                        "maintenance window", "2 AM EST", "migrate",
                        "frontend", "CDN", "clear caches", "restart",
                        "health checks", "rollback"
                    ],
                    "order_critical": True,
                },
                category="procedures",
                metadata={"step_count": 9, "order_matters": True},
            ),

            # Scenario 4: Numerical data preservation
            BenchmarkTask(
                id="metrics_report",
                prompt="""Q4 Performance Metrics:
                - Revenue: $2.4M (up 23% YoY)
                - Active users: 45,678 (up 15% QoQ)
                - Churn rate: 2.3% (down from 3.1%)
                - NPS score: 72 (target was 70)
                - Support tickets: 234 (average resolution: 4.5 hours)
                - Uptime: 99.97%

                Pass these metrics to the analyst for quarterly review.""",
                expected_output={
                    "numbers": [
                        "2.4M", "23%", "45,678", "15%", "2.3%",
                        "3.1%", "72", "70", "234", "4.5", "99.97%"
                    ],
                },
                category="data",
                metadata={"precision_required": True},
            ),

            # Scenario 5: Context with dependencies
            BenchmarkTask(
                id="api_dependencies",
                prompt="""API Integration Requirements:
                The payment service depends on the user service for authentication.
                The notification service requires both user and payment services.
                The analytics service consumes events from all other services.
                The admin panel can only be accessed by users with role 'admin' from the user service.
                All services must implement circuit breakers for resilience.

                These dependencies are critical for proper system design.""",
                expected_output={
                    "services": [
                        "payment", "user", "notification", "analytics", "admin panel"
                    ],
                    "dependencies": [
                        "payment depends on user",
                        "notification requires user",
                        "notification requires payment",
                        "analytics consumes events",
                        "admin panel role admin"
                    ],
                    "requirements": ["circuit breakers"],
                },
                category="architecture",
                metadata={"relationship_count": 5},
            ),
        ]

    async def evaluate(self, agent: Any, **kwargs) -> BenchmarkResult:
        """
        Run handoff quality benchmark.

        Args:
            agent: Agent configuration or list of agents
            **kwargs: Additional parameters

        Returns:
            BenchmarkResult with handoff analysis
        """
        # Extract agents
        if isinstance(agent, list):
            base_agents = agent
        else:
            # Single agent - will be replicated for chains
            base_agents = [agent]

        all_results = []
        chain_results = {}

        # Test each chain length
        for chain_length in self.chain_lengths:
            chain_results[chain_length] = []

            # Create agent chain
            if len(base_agents) >= chain_length:
                # Use first N agents
                chain_agents = base_agents[:chain_length]
            else:
                # Replicate agents to reach chain length
                chain_agents = []
                for i in range(chain_length):
                    agent_template = base_agents[i % len(base_agents)]

                    # Create unique agent for chain position
                    if isinstance(agent_template, AgentInfo):
                        chain_agent = AgentInfo(
                            name=f"{agent_template.name}_position_{i}",
                            url=agent_template.url,
                            role=f"Agent {i+1} in handoff chain",
                            capabilities=agent_template.capabilities,
                        )
                    else:
                        # Dictionary format
                        chain_agent = {
                            **agent_template,
                            "name": f"{agent_template.get('name', 'agent')}_position_{i}",
                            "role": f"Agent {i+1} in handoff chain",
                        }

                    chain_agents.append(chain_agent)

            # Convert to AgentInfo if needed
            if all(isinstance(a, dict) for a in chain_agents):
                chain_agents = [
                    AgentInfo(
                        name=a["name"],
                        url=a["url"],
                        role=a.get("role"),
                        capabilities=a.get("capabilities"),
                    )
                    for a in chain_agents
                ]

            # Create linear pattern for handoff chain
            pattern = LinearPattern(chain_agents)

            # Test each scenario with this chain
            for scenario in self.test_scenarios:
                result = await self._evaluate_handoff_scenario(
                    pattern,
                    scenario,
                    chain_length,
                )

                chain_results[chain_length].append(result)
                all_results.append({
                    **result,
                    "chain_length": chain_length,
                })

        # Analyze results
        analysis = self._analyze_handoff_patterns(chain_results)

        # Calculate overall metrics
        total_tasks = len(all_results)
        successful_tasks = sum(1 for r in all_results if r["success"])
        avg_preservation = sum(r["preservation_score"] for r in all_results) / total_tasks

        return BenchmarkResult(
            benchmark_name=self.name,
            agent_name=f"handoff_chain_{base_agents[0].get('name', 'agent') if isinstance(base_agents[0], dict) else base_agents[0].name if hasattr(base_agents[0], 'name') else 'unknown'}",
            tasks_completed=successful_tasks,
            tasks_total=total_tasks,
            overall_score=avg_preservation,
            task_results=all_results,
            metrics={},
            summary={
                "average_preservation": avg_preservation,
                "preservation_by_chain_length": {
                    length: sum(r["preservation_score"] for r in results) / len(results)
                    for length, results in chain_results.items()
                    if results
                },
                "degradation_analysis": analysis,
                "chain_lengths_tested": self.chain_lengths,
                "scenario_count": len(self.test_scenarios),
            },
        )

    async def _evaluate_handoff_scenario(
        self,
        pattern: LinearPattern,
        scenario: BenchmarkTask,
        chain_length: int,
    ) -> dict[str, Any]:
        """Evaluate a single handoff scenario."""
        start_time = datetime.now()

        try:
            # Add handoff instructions to prompt
            handoff_prompt = f"""{scenario.prompt}

Important: You must pass ALL the information above to the next agent.
Be complete and accurate in your communication."""

            # Execute handoff chain
            result = await pattern.execute(
                handoff_prompt,
                context={"preserve": scenario.expected_output},
            )

            # Evaluate preservation
            preservation_score = self._evaluate_preservation(
                result.get("final_output", ""),
                scenario.expected_output,
                result.get("handoffs", []),
            )

            end_time = datetime.now()

            return {
                "scenario_id": scenario.id,
                "category": scenario.category,
                "success": result.get("success", False),
                "preservation_score": preservation_score,
                "information_preservation": result.get("information_preservation", 0),
                "latency": (end_time - start_time).total_seconds(),
                "handoff_count": len(result.get("handoffs", [])),
                "final_output_length": len(result.get("final_output", "")),
                "degradation_per_hop": (1 - preservation_score) / chain_length if chain_length > 0 else 0,
            }

        except Exception as e:
            return {
                "scenario_id": scenario.id,
                "category": scenario.category,
                "success": False,
                "preservation_score": 0.0,
                "error": str(e),
                "latency": (datetime.now() - start_time).total_seconds(),
            }

    def _evaluate_preservation(
        self,
        final_output: str,
        expected: dict[str, Any],
        handoffs: list[dict[str, Any]],
    ) -> float:
        """Evaluate how well information was preserved."""
        if not expected or not final_output:
            return 0.0

        final_lower = final_output.lower()
        scores = []

        # Check each type of expected content
        for content_type, items in expected.items():
            if content_type == "order_critical":
                continue  # Special handling below

            if isinstance(items, list):
                found = sum(1 for item in items if str(item).lower() in final_lower)
                score = found / len(items) if items else 0
                scores.append(score)

            elif isinstance(items, bool):
                # Boolean flags
                if content_type == "order_critical" and items:
                    # Check if order is preserved
                    order_score = self._check_order_preservation(
                        final_output,
                        expected.get("steps", []),
                    )
                    scores.append(order_score)

        # Additional penalty for excessive noise
        if handoffs and len(handoffs) > 1:
            first_length = handoffs[0].get("output_length", 100)
            final_length = handoffs[-1].get("output_length", first_length)

            # Penalize if output grew too much (noise accumulation)
            if final_length > first_length * 2:
                noise_penalty = 0.1 * (final_length / first_length - 2)
                scores.append(max(0, 1 - noise_penalty))

        return sum(scores) / len(scores) if scores else 0.0

    def _check_order_preservation(
        self,
        output: str,
        ordered_items: list[str],
    ) -> float:
        """Check if order of items is preserved."""
        if not ordered_items:
            return 1.0

        # Find positions of each item
        positions = []
        output_lower = output.lower()

        for item in ordered_items:
            pos = output_lower.find(str(item).lower())
            if pos >= 0:
                positions.append(pos)
            else:
                positions.append(float('inf'))  # Not found

        # Check if positions are in increasing order
        correct_order = 0
        for i in range(1, len(positions)):
            if positions[i] > positions[i-1] and positions[i] != float('inf'):
                correct_order += 1

        return correct_order / (len(positions) - 1) if len(positions) > 1 else 1.0

    def _analyze_handoff_patterns(
        self,
        chain_results: dict[int, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        """Analyze degradation patterns across chain lengths."""
        analysis = {
            "exponential_decay_rate": 0.0,
            "category_resilience": {},
            "critical_chain_length": None,
            "recommendations": [],
        }

        # Calculate decay rate
        chain_scores = {}
        for length, results in chain_results.items():
            if results:
                chain_scores[length] = sum(r["preservation_score"] for r in results) / len(results)

        if len(chain_scores) >= 2:
            # Simple exponential decay approximation
            lengths = sorted(chain_scores.keys())
            scores = [chain_scores[l] for l in lengths]

            if scores[0] > 0:
                # Calculate average decay per hop
                decay_rates = []
                for i in range(1, len(scores)):
                    if scores[i-1] > 0:
                        decay = (scores[i-1] - scores[i]) / scores[i-1]
                        decay_rates.append(decay / (lengths[i] - lengths[i-1]))

                if decay_rates:
                    analysis["exponential_decay_rate"] = sum(decay_rates) / len(decay_rates)

        # Analyze by category
        categories = set(s.category for s in self.test_scenarios if s.category)

        for category in categories:
            category_scores = {}

            for length, results in chain_results.items():
                cat_results = [r for r in results if r.get("category") == category]
                if cat_results:
                    category_scores[length] = sum(r["preservation_score"] for r in cat_results) / len(cat_results)

            if category_scores:
                best_length = max(category_scores.items(), key=lambda x: x[1])[0]
                worst_length = min(category_scores.items(), key=lambda x: x[1])[0]

                analysis["category_resilience"][category] = {
                    "best_chain_length": best_length,
                    "worst_chain_length": worst_length,
                    "degradation_range": category_scores[best_length] - category_scores[worst_length],
                }

        # Find critical chain length (where preservation drops below 70%)
        for length in sorted(chain_scores.keys()):
            if chain_scores[length] < 0.7:
                analysis["critical_chain_length"] = length
                break

        # Generate recommendations
        if analysis["exponential_decay_rate"] > 0.1:
            analysis["recommendations"].append(
                "High degradation rate detected. Consider using supervisor pattern for chains > 3 agents."
            )

        if analysis["critical_chain_length"] and analysis["critical_chain_length"] <= 3:
            analysis["recommendations"].append(
                f"Information preservation drops below 70% at {analysis['critical_chain_length']} agents. "
                "Implement explicit context preservation mechanisms."
            )

        return analysis
