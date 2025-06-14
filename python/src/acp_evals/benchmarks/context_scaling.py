"""
Context scaling benchmark for ACP agent evaluation.

Tests how agents handle increasing amounts of irrelevant context,
based on tau-bench methodology and LangChain research.
"""

import random
from datetime import datetime
from typing import Any

from acp_evals.benchmarks.datasets.core_tasks import CORE_TASKS, DISTRACTOR_CONTEXTS
from acp_evals.core.base import Benchmark, BenchmarkResult, BenchmarkTask


class ContextScalingBenchmark(Benchmark):
    """
    Tests performance degradation with increasing irrelevant context.

    This benchmark progressively adds distractor information to test:
    - Accuracy degradation with noise
    - Latency increase with context
    - Token efficiency under pressure
    - Focus maintenance capabilities
    """

    def __init__(
        self,
        distractor_levels: list[int] | None = None,
        task_categories: list[str] | None = None,
        randomize_distractors: bool = True,
        distractor_domains: list[str] | None = None,
        tasks: list[BenchmarkTask] | None = None,
    ):
        """
        Initialize context scaling benchmark.

        Args:
            distractor_levels: Number of distractors to test (default: [0, 1, 3, 5, 10])
            task_categories: Categories to include (default: all)
            randomize_distractors: Whether to randomize distractor selection
            distractor_domains: Domains for distractor generation
            tasks: Custom tasks to use
        """
        self.distractor_levels = distractor_levels or [0, 1, 3, 5, 10]
        self.context_levels = self.distractor_levels  # Alias for compatibility
        self.task_categories = task_categories
        self.randomize_distractors = randomize_distractors
        self.distractor_domains = distractor_domains or ["general", "technical", "business"]
        self.tasks = tasks or self._load_tasks()
        self._tasks = self.tasks  # Internal reference

    @property
    def name(self) -> str:
        return "context_scaling"

    @property
    def description(self) -> str:
        return "Measures performance degradation with increasing irrelevant context"

    @property
    def categories(self) -> list[str]:
        return ["robustness", "efficiency", "focus"]

    def _load_tasks(self) -> list[BenchmarkTask]:
        """Load core tasks based on selected categories."""
        tasks = []

        for task_data in CORE_TASKS:
            # Filter by category if specified
            if self.task_categories and task_data["category"] not in self.task_categories:
                continue

            task = BenchmarkTask(
                id=task_data["id"],
                prompt=task_data["prompt"],
                expected_output=task_data.get("expected"),
                category=task_data["category"],
                difficulty=task_data.get("difficulty", "medium"),
                metadata=task_data.get("metadata", {}),
            )
            tasks.append(task)

        return tasks

    def _select_distractors(self, num_distractors: int) -> list[str]:
        """Select distractor contexts."""
        available_distractors = DISTRACTOR_CONTEXTS.copy()

        if self.randomize_distractors:
            random.shuffle(available_distractors)

        return available_distractors[:num_distractors]

    def _build_prompt_with_distractors(self, task: BenchmarkTask, distractors: list[str]) -> str:
        """Build a prompt with distractor contexts prepended."""
        if not distractors:
            return task.prompt

        # Join distractors with clear separators
        distractor_text = "\n\n---\n\n".join(distractors)

        # Build final prompt
        full_prompt = f"""Context Information:
{distractor_text}

---

Task: {task.prompt}"""

        return full_prompt

    async def _evaluate_task(
        self,
        agent: Any,
        task: BenchmarkTask,
        num_distractors: int,
        metrics: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate a single task with specified number of distractors."""
        # Select and apply distractors
        distractors = self._select_distractors(num_distractors)
        prompt = self._build_prompt_with_distractors(task, distractors)

        # Time the execution
        start_time = datetime.now()

        try:
            # Run the agent
            # This assumes agent has a run method or is an ACP client
            if hasattr(agent, 'run'):
                result = await agent.run(prompt)
                response = str(result)
            elif hasattr(agent, 'run_sync'):
                result = await agent.run_sync(agent_name="default", input=[{"parts": [{"content": prompt}]}])
                response = result.output[0].parts[0].content if result.output else ""
            else:
                # Assume it's a callable
                response = await agent(prompt)

            end_time = datetime.now()
            latency = (end_time - start_time).total_seconds()

            # Evaluate response
            score = self._evaluate_response(task, response)

            return {
                "task_id": task.id,
                "num_distractors": num_distractors,
                "score": score,
                "latency": latency,
                "response_length": len(response),
                "success": score >= 0.7,  # 70% threshold for success
                "response": response[:500],  # First 500 chars for inspection
            }

        except Exception as e:
            return {
                "task_id": task.id,
                "num_distractors": num_distractors,
                "score": 0.0,
                "latency": (datetime.now() - start_time).total_seconds(),
                "response_length": 0,
                "success": False,
                "error": str(e),
            }

    def _evaluate_response(self, task: BenchmarkTask, response: str) -> float:
        """Evaluate response accuracy against expected output."""
        if not task.expected_output:
            # No expected output defined, return 1.0 if response is non-empty
            return 1.0 if response.strip() else 0.0

        response_lower = response.lower()

        # Handle different types of expected output
        if isinstance(task.expected_output, list):
            # Check how many expected elements are present
            found = sum(1 for expected in task.expected_output if expected.lower() in response_lower)
            score = found / len(task.expected_output)
        elif isinstance(task.expected_output, dict):
            # For dict, check required keys
            required = task.expected_output.get("required", [])
            optional = task.expected_output.get("optional", [])

            required_found = sum(1 for item in required if item.lower() in response_lower)
            optional_found = sum(1 for item in optional if item.lower() in response_lower)

            required_score = required_found / len(required) if required else 1.0
            optional_score = optional_found / len(optional) if optional else 0.0

            # Weight required more heavily
            score = (0.8 * required_score) + (0.2 * optional_score)
        else:
            # String comparison
            score = 1.0 if str(task.expected_output).lower() in response_lower else 0.0

        return score

    def _generate_distractors(self, num_distractors: int) -> list[str]:
        """Generate distractor content based on domains."""
        distractors = []

        for _ in range(num_distractors):
            domain = random.choice(self.distractor_domains)

            if domain in DISTRACTOR_CONTEXTS:
                distractor = random.choice(DISTRACTOR_CONTEXTS[domain])
            else:
                # Fallback to generic distractors
                distractor = f"In the field of {domain}, recent developments have shown significant progress."

            distractors.append(distractor)

        return distractors

    def _calculate_degradation(self, results_by_level: dict[int, list[dict]]) -> dict[str, float]:
        """Calculate performance degradation metrics."""
        baseline_scores = []
        baseline_latencies = []

        # Get baseline (0 distractors) performance
        if 0 in results_by_level:
            for result in results_by_level[0]:
                baseline_scores.append(result["score"])
                baseline_latencies.append(result["latency"])

        if not baseline_scores:
            return {"error": "No baseline results available"}

        avg_baseline_score = sum(baseline_scores) / len(baseline_scores)
        avg_baseline_latency = sum(baseline_latencies) / len(baseline_latencies)

        degradation_metrics = {}

        for level, results in results_by_level.items():
            if level == 0:
                continue

            scores = [r["score"] for r in results]
            latencies = [r["latency"] for r in results]

            avg_score = sum(scores) / len(scores) if scores else 0
            avg_latency = sum(latencies) / len(latencies) if latencies else 0

            # Calculate degradation percentages
            score_degradation = ((avg_baseline_score - avg_score) / avg_baseline_score * 100) if avg_baseline_score > 0 else 0
            latency_increase = ((avg_latency - avg_baseline_latency) / avg_baseline_latency * 100) if avg_baseline_latency > 0 else 0

            degradation_metrics[f"score_degradation_{level}_distractors"] = score_degradation
            degradation_metrics[f"latency_increase_{level}_distractors"] = latency_increase

        return degradation_metrics

    async def evaluate(self, agent: Any, **kwargs) -> BenchmarkResult:
        """
        Run the context scaling benchmark.

        Args:
            agent: The agent to evaluate
            **kwargs: Additional parameters (e.g., specific metrics to calculate)

        Returns:
            BenchmarkResult with detailed performance analysis
        """
        all_results = []
        results_by_level = {level: [] for level in self.distractor_levels}

        # Get metrics if provided
        metrics = kwargs.get("metrics", [])

        # Run each task with each distractor level
        for task in self._tasks:
            for num_distractors in self.distractor_levels:
                result = await self._evaluate_task(agent, task, num_distractors, metrics)
                all_results.append(result)
                results_by_level[num_distractors].append(result)

        # Calculate aggregate metrics
        total_tasks = len(all_results)
        successful_tasks = sum(1 for r in all_results if r.get("success", False))
        overall_score = sum(r.get("score", 0) for r in all_results) / total_tasks if total_tasks > 0 else 0

        # Calculate degradation metrics
        degradation_metrics = self._calculate_degradation(results_by_level)

        # Find optimal context size (highest score)
        avg_scores_by_level = {}
        for level, results in results_by_level.items():
            if results:
                avg_scores_by_level[level] = sum(r["score"] for r in results) / len(results)

        optimal_context_level = max(avg_scores_by_level.items(), key=lambda x: x[1])[0] if avg_scores_by_level else 0

        # Build summary
        summary = {
            "average_scores_by_distractor_level": avg_scores_by_level,
            "optimal_distractor_level": optimal_context_level,
            "total_degradation": degradation_metrics.get(f"score_degradation_{max(self.distractor_levels)}_distractors", 0),
            **degradation_metrics,
        }

        # Get agent name
        agent_name = getattr(agent, "name", "unknown")
        if hasattr(agent, "manifest") and hasattr(agent.manifest, "name"):
            agent_name = agent.manifest.name

        return BenchmarkResult(
            benchmark_name=self.name,
            agent_name=agent_name,
            tasks_completed=successful_tasks,
            tasks_total=total_tasks,
            overall_score=overall_score,
            task_results=all_results,
            metrics={},  # Will be populated by evaluation framework
            summary=summary,
        )
