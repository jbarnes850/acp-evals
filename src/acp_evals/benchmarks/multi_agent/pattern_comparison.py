"""
Pattern comparison benchmark for multi-agent systems.

Compares supervisor vs swarm patterns on the same tasks to identify
optimal architectures for different scenarios.
"""

from datetime import datetime
from typing import Any

from acp_evals.core.base import Benchmark, BenchmarkResult, BenchmarkTask
from acp_evals.metrics import HandoffQualityMetric, TokenUsageMetric
from acp_evals.patterns import AgentInfo, LinearPattern, SupervisorPattern, SwarmPattern


class PatternComparisonBenchmark(Benchmark):
    """
    Compares different multi-agent patterns on identical tasks.

    Based on LangChain's research showing significant performance
    differences between supervisor and swarm patterns.
    """

    def __init__(
        self,
        patterns_to_test: list[str] | None = None,
        test_tasks: list[BenchmarkTask] | None = None,
    ):
        """
        Initialize pattern comparison benchmark.

        Args:
            patterns_to_test: Which patterns to compare (default: all)
            test_tasks: Custom tasks (default: built-in suite)
        """
        self.patterns_to_test = patterns_to_test or ["linear", "supervisor", "swarm"]
        self.test_tasks = test_tasks or self._create_default_tasks()

    @property
    def name(self) -> str:
        return "pattern_comparison"

    @property
    def description(self) -> str:
        return "Compares multi-agent patterns to identify optimal architectures"

    @property
    def categories(self) -> list[str]:
        return ["architecture", "multi_agent", "performance"]

    def _create_default_tasks(self) -> list[BenchmarkTask]:
        """Create default task suite for pattern comparison."""
        return [
            # Task 1: Sequential processing (favors linear)
            BenchmarkTask(
                id="data_pipeline",
                prompt="Extract key facts from this text, summarize them, then create action items: 'The Q3 report shows 15% revenue growth but customer churn increased by 3%. Marketing budget was underspent by $50K. Three new competitors entered our market.'",
                expected_output={
                    "required": ["15% revenue growth", "3% churn increase", "$50K underspent", "three competitors"],
                    "optional": ["action items", "summary"],
                },
                category="sequential",
                metadata={"expected_best_pattern": "linear"},
            ),

            # Task 2: Parallel research (favors swarm)
            BenchmarkTask(
                id="market_research",
                prompt="Research and provide information about: 1) Current AI trends, 2) Top programming languages in 2024, 3) Cloud computing market size",
                expected_output={
                    "required": ["AI trends", "programming languages", "market size"],
                    "optional": ["specific statistics", "sources"],
                },
                category="parallel",
                metadata={"expected_best_pattern": "swarm"},
            ),

            # Task 3: Coordinated analysis (favors supervisor)
            BenchmarkTask(
                id="complex_analysis",
                prompt="Analyze this business scenario and provide recommendations: A SaaS company with $10M ARR wants to expand internationally. They have 50 employees, strong US presence, and $5M in funding. Consider market entry strategy, resource allocation, and risk assessment.",
                expected_output={
                    "required": ["market entry", "resource allocation", "risks"],
                    "optional": ["specific countries", "timeline", "budget breakdown"],
                },
                category="coordination",
                metadata={"expected_best_pattern": "supervisor"},
            ),

            # Task 4: Creative synthesis (pattern-agnostic)
            BenchmarkTask(
                id="creative_task",
                prompt="Create a product concept for a 'smart garden assistant' including features, target audience, and marketing angle",
                expected_output={
                    "required": ["features", "target audience", "marketing"],
                    "optional": ["pricing", "competition", "technical specs"],
                },
                category="creative",
                metadata={"expected_best_pattern": "any"},
            ),

            # Task 5: Error-prone task (tests robustness)
            BenchmarkTask(
                id="calculation_heavy",
                prompt="Calculate the compound interest on $10,000 at 5% annual rate for 10 years, then determine how many months it would take to double at that rate, and finally suggest investment strategies for different risk profiles",
                expected_output={
                    "required": ["compound interest result", "doubling time", "investment strategies"],
                    "optional": ["exact calculations", "risk profiles"],
                },
                category="calculation",
                metadata={"expected_best_pattern": "supervisor"},  # Supervisor can verify
            ),
        ]

    async def evaluate(self, agent: Any, **kwargs) -> BenchmarkResult:
        """
        Run pattern comparison benchmark.

        Args:
            agent: Agent configuration or list of AgentInfo objects
            **kwargs: Additional parameters

        Returns:
            BenchmarkResult with pattern comparison analysis
        """
        # Extract agents from input
        if isinstance(agent, list) and all(isinstance(a, dict) for a in agent):
            # Convert dicts to AgentInfo
            agents = [
                AgentInfo(
                    name=a["name"],
                    url=a["url"],
                    role=a.get("role"),
                    capabilities=a.get("capabilities"),
                )
                for a in agent
            ]
        elif isinstance(agent, list) and all(isinstance(a, AgentInfo) for a in agent):
            agents = agent
        else:
            raise ValueError("Pattern comparison requires a list of AgentInfo objects")

        if len(agents) < 2:
            raise ValueError("Pattern comparison requires at least 2 agents")

        # Initialize metrics
        token_metric = TokenUsageMetric()
        handoff_metric = HandoffQualityMetric()

        # Results storage
        pattern_results = {}
        all_task_results = []

        # Test each pattern
        for pattern_type in self.patterns_to_test:
            pattern = self._create_pattern(pattern_type, agents)
            if not pattern:
                continue

            pattern_start = datetime.now()
            pattern_task_results = []

            # Run all tasks with this pattern
            for task in self.test_tasks:
                task_result = await self._evaluate_pattern_on_task(
                    pattern,
                    task,
                    token_metric,
                    handoff_metric,
                )
                pattern_task_results.append(task_result)
                all_task_results.append({
                    **task_result,
                    "pattern": pattern_type,
                })

            pattern_end = datetime.now()

            # Aggregate pattern results
            pattern_results[pattern_type] = {
                "tasks_completed": sum(1 for r in pattern_task_results if r["success"]),
                "average_score": sum(r["score"] for r in pattern_task_results) / len(pattern_task_results),
                "average_latency": sum(r["latency"] for r in pattern_task_results) / len(pattern_task_results),
                "total_tokens": sum(r.get("tokens", 0) for r in pattern_task_results),
                "total_cost": sum(r.get("cost", 0) for r in pattern_task_results),
                "pattern_latency": (pattern_end - pattern_start).total_seconds(),
                "task_results": pattern_task_results,
            }

        # Analyze results
        analysis = self._analyze_pattern_performance(pattern_results, self.test_tasks)

        # Determine overall winner
        best_pattern = max(
            pattern_results.items(),
            key=lambda x: x[1]["average_score"]
        )[0]

        return BenchmarkResult(
            benchmark_name=self.name,
            agent_name=f"multi_agent_ensemble_{len(agents)}",
            tasks_completed=len([r for r in all_task_results if r["success"]]),
            tasks_total=len(self.test_tasks) * len(self.patterns_to_test),
            overall_score=sum(r["average_score"] for r in pattern_results.values()) / len(pattern_results),
            task_results=all_task_results,
            metrics={},  # Will be populated by framework
            summary={
                "best_pattern": best_pattern,
                "pattern_scores": {p: r["average_score"] for p, r in pattern_results.items()},
                "pattern_analysis": analysis,
                "pattern_details": pattern_results,
                "agent_count": len(agents),
            },
        )

    def _create_pattern(
        self,
        pattern_type: str,
        agents: list[AgentInfo]
    ) -> Any | None:
        """Create a pattern instance."""
        if pattern_type == "linear":
            return LinearPattern(agents)
        elif pattern_type == "supervisor" and len(agents) >= 2:
            # First agent is supervisor, rest are workers
            return SupervisorPattern(agents[0], agents[1:])
        elif pattern_type == "swarm":
            return SwarmPattern(agents)
        return None

    async def _evaluate_pattern_on_task(
        self,
        pattern: Any,
        task: BenchmarkTask,
        token_metric: TokenUsageMetric,
        handoff_metric: HandoffQualityMetric,
    ) -> dict[str, Any]:
        """Evaluate a single pattern on a single task."""
        start_time = datetime.now()

        try:
            # Execute pattern
            result = await pattern.execute(
                task.prompt,
                context={"task_id": task.id, "expected": task.expected_output}
            )

            # Evaluate output quality
            score = self._evaluate_output(
                result.get("final_output", ""),
                task.expected_output,
            )

            end_time = datetime.now()

            return {
                "task_id": task.id,
                "success": result.get("success", False),
                "score": score,
                "latency": (end_time - start_time).total_seconds(),
                "pattern_latency": result.get("total_latency", 0),
                "tokens": result.get("total_tokens", 0),
                "cost": result.get("total_cost", 0),
                "handoff_quality": result.get("information_preservation", 1.0),
                "pattern_specific": {
                    k: v for k, v in result.items()
                    if k not in ["final_output", "success"]
                },
            }

        except Exception as e:
            return {
                "task_id": task.id,
                "success": False,
                "score": 0.0,
                "latency": (datetime.now() - start_time).total_seconds(),
                "error": str(e),
            }

    def _evaluate_output(
        self,
        output: str,
        expected: Any | None
    ) -> float:
        """Evaluate output quality against expected."""
        if not expected:
            return 0.5 if output else 0.0

        output_lower = output.lower()
        score = 0.0
        total_weight = 0.0

        if isinstance(expected, dict):
            # Check required elements (higher weight)
            required = expected.get("required", [])
            for item in required:
                total_weight += 2.0
                if str(item).lower() in output_lower:
                    score += 2.0

            # Check optional elements (lower weight)
            optional = expected.get("optional", [])
            for item in optional:
                total_weight += 1.0
                if str(item).lower() in output_lower:
                    score += 1.0

        elif isinstance(expected, list):
            # Check all items equally
            for item in expected:
                total_weight += 1.0
                if str(item).lower() in output_lower:
                    score += 1.0

        else:
            # Simple string check
            total_weight = 1.0
            if str(expected).lower() in output_lower:
                score = 1.0

        return score / total_weight if total_weight > 0 else 0.0

    def _analyze_pattern_performance(
        self,
        pattern_results: dict[str, dict[str, Any]],
        tasks: list[BenchmarkTask],
    ) -> dict[str, Any]:
        """Analyze pattern performance across task categories."""
        analysis = {
            "by_category": {},
            "recommendations": [],
            "trade_offs": {},
        }

        # Analyze by task category
        categories = set(task.category for task in tasks if task.category)

        for category in categories:
            category_tasks = [t for t in tasks if t.category == category]
            category_analysis = {}

            for pattern, results in pattern_results.items():
                # Get results for tasks in this category
                task_scores = []
                for task in category_tasks:
                    task_result = next(
                        (r for r in results["task_results"] if r["task_id"] == task.id),
                        None
                    )
                    if task_result:
                        task_scores.append(task_result["score"])

                if task_scores:
                    category_analysis[pattern] = sum(task_scores) / len(task_scores)

            if category_analysis:
                best_for_category = max(category_analysis.items(), key=lambda x: x[1])[0]
                analysis["by_category"][category] = {
                    "scores": category_analysis,
                    "best_pattern": best_for_category,
                }

        # Generate recommendations
        for pattern, results in pattern_results.items():
            if pattern == "linear":
                analysis["recommendations"].append(
                    f"Use {pattern} for sequential tasks with clear dependencies "
                    f"(avg score: {results['average_score']:.2f})"
                )
            elif pattern == "supervisor":
                analysis["recommendations"].append(
                    f"Use {pattern} for complex tasks requiring coordination "
                    f"(avg score: {results['average_score']:.2f})"
                )
            elif pattern == "swarm":
                analysis["recommendations"].append(
                    f"Use {pattern} for parallel, independent subtasks "
                    f"(avg score: {results['average_score']:.2f})"
                )

        # Identify trade-offs
        if "linear" in pattern_results and "swarm" in pattern_results:
            linear_latency = pattern_results["linear"]["average_latency"]
            swarm_latency = pattern_results["swarm"]["average_latency"]

            analysis["trade_offs"]["speed_vs_coordination"] = {
                "linear_latency": linear_latency,
                "swarm_latency": swarm_latency,
                "speedup": linear_latency / swarm_latency if swarm_latency > 0 else 0,
            }

        return analysis
