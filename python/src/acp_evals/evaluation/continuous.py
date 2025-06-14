"""
Continuous evaluation pipeline for ACP agents.

Implements automated evaluation workflows with regression detection,
performance monitoring, and continuous improvement loops.
"""

import asyncio
import hashlib
import json
import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from ..benchmarks.datasets.adversarial_datasets import AdversarialCategory, create_test_suite
from ..benchmarks.datasets.gold_standard_datasets import get_multi_step_tasks
from ..benchmarks.datasets.trace_recycler import TraceRecycler
from ..simple import AccuracyEval, BatchResult
from ..telemetry.otel_exporter import OTelExporter
from .simulator import Simulator

logger = logging.getLogger(__name__)


@dataclass
class EvaluationRun:
    """Represents a single evaluation run."""
    run_id: str
    timestamp: datetime
    agent_version: str
    test_suite: str
    results: BatchResult
    metrics: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RegressionAlert:
    """Alert for detected regression."""
    alert_id: str
    timestamp: datetime
    metric: str
    baseline_value: float
    current_value: float
    degradation: float
    affected_tests: list[str]
    severity: str  # "low", "medium", "high", "critical"
    details: dict[str, Any] = field(default_factory=dict)


class ContinuousEvaluationPipeline:
    """
    Manages continuous evaluation of ACP agents with regression detection.

    Features:
    - Automated periodic evaluation
    - Regression detection against baselines
    - Trace recycling for new test cases
    - Performance trend analysis
    - Alert generation
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        evaluation_dir: str = "./continuous_eval",
        telemetry_exporter: OTelExporter | None = None,
        alert_callback: Callable[[RegressionAlert], None] | None = None
    ):
        """
        Initialize continuous evaluation pipeline.

        Args:
            agent: Agent to evaluate (URL, callable, or instance)
            evaluation_dir: Directory to store evaluation results
            telemetry_exporter: Optional telemetry exporter
            alert_callback: Optional callback for regression alerts
        """
        self.agent = agent
        self.evaluation_dir = Path(evaluation_dir)
        self.evaluation_dir.mkdir(parents=True, exist_ok=True)

        self.telemetry_exporter = telemetry_exporter
        self.alert_callback = alert_callback

        # Initialize components
        self.simulator = Simulator(agent)
        self.trace_recycler = TraceRecycler(telemetry_exporter)

        # Storage for evaluation history
        self.runs: list[EvaluationRun] = []
        self.baselines: dict[str, dict[str, float]] = {}
        self.alerts: list[RegressionAlert] = []

        # Load existing data
        self._load_history()

    async def run_evaluation_cycle(
        self,
        test_suites: list[str] | None = None,
        include_synthetic: bool = True,
        include_recycled: bool = True,
        include_adversarial: bool = True,
        save_results: bool = True
    ) -> EvaluationRun:
        """
        Run a complete evaluation cycle.

        Args:
            test_suites: Specific test suites to run (default: all)
            include_synthetic: Include synthetic test generation
            include_recycled: Include recycled traces from production
            include_adversarial: Include adversarial testing
            save_results: Save results to disk

        Returns:
            EvaluationRun with results
        """
        logger.info("Starting evaluation cycle")

        # Generate run ID
        run_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(self.agent).encode()).hexdigest()[:8]}"

        # Collect all test cases
        all_test_cases = []
        test_metadata = {}

        # 1. Gold standard tests
        if not test_suites or "gold_standard" in test_suites:
            gold_tests = self._prepare_gold_standard_tests()
            all_test_cases.extend(gold_tests)
            test_metadata["gold_standard"] = len(gold_tests)

        # 2. Synthetic tests
        if include_synthetic and (not test_suites or "synthetic" in test_suites):
            synthetic_tests = await self._generate_synthetic_tests()
            all_test_cases.extend(synthetic_tests)
            test_metadata["synthetic"] = len(synthetic_tests)

        # 3. Recycled traces
        if include_recycled and (not test_suites or "recycled" in test_suites):
            recycled_tests = self._get_recycled_tests()
            all_test_cases.extend(recycled_tests)
            test_metadata["recycled"] = len(recycled_tests)

        # 4. Adversarial tests
        if include_adversarial and (not test_suites or "adversarial" in test_suites):
            adversarial_tests = self._prepare_adversarial_tests()
            all_test_cases.extend(adversarial_tests)
            test_metadata["adversarial"] = len(adversarial_tests)

        logger.info(f"Prepared {len(all_test_cases)} test cases")

        # Run evaluations
        evaluator = AccuracyEval(
            agent=self.agent,
            rubric="comprehensive"  # Use comprehensive rubric
        )

        results = await evaluator.run_batch(
            test_cases=all_test_cases,
            parallel=True,
            progress=True
        )

        # Compute metrics
        metrics = self._compute_metrics(results, test_metadata)

        # Detect agent version
        agent_version = await self._detect_agent_version()

        # Create evaluation run
        run = EvaluationRun(
            run_id=run_id,
            timestamp=datetime.now(),
            agent_version=agent_version,
            test_suite="all" if not test_suites else ",".join(test_suites),
            results=results,
            metrics=metrics,
            metadata=test_metadata
        )

        # Check for regressions
        regressions = self._detect_regressions(run)
        if regressions:
            for alert in regressions:
                await self._handle_regression(alert)

        # Save results
        if save_results:
            self._save_run(run)
            self.runs.append(run)

        # Export telemetry
        if self.telemetry_exporter:
            await self._export_telemetry(run)

        logger.info(f"Evaluation cycle completed: {run_id}")
        return run

    def _prepare_gold_standard_tests(self) -> list[dict[str, Any]]:
        """Prepare gold standard test cases."""
        test_cases = []

        # Get multi-step tasks
        multi_step_tasks = get_multi_step_tasks()

        for task in multi_step_tasks[:20]:  # Limit to 20 tasks
            test_case = {
                "input": task.input,
                "expected": json.dumps({
                    "steps": task.expected_steps,
                    "tools": task.expected_tools,
                    "criteria": task.expected_output_criteria
                }),
                "context": {
                    "task_id": task.task_id,
                    "category": task.category,
                    "difficulty": task.difficulty,
                    "suite": "gold_standard"
                }
            }
            test_cases.append(test_case)

        return test_cases

    async def _generate_synthetic_tests(self) -> list[dict[str, Any]]:
        """Generate synthetic test cases."""
        # Generate diverse scenarios
        test_cases = self.simulator.generate_test_cases(
            scenario="factual_qa",
            count=10,
            diversity=0.9
        )

        # Add task-specific tests
        test_cases.extend(self.simulator.generate_test_cases(
            scenario="task_specific",
            count=10,
            diversity=0.9
        ))

        # Format for evaluation
        formatted = []
        for tc in test_cases:
            formatted.append({
                "input": tc["input"],
                "expected": json.dumps(tc.get("expected", "Appropriate response")),
                "context": {
                    **tc.get("metadata", {}),
                    "suite": "synthetic"
                }
            })

        return formatted

    def _get_recycled_tests(self) -> list[dict[str, Any]]:
        """Get test cases from recycled traces."""
        # Generate evaluation dataset from traces
        recycled = self.trace_recycler.generate_evaluation_dataset(
            count=20,
            min_quality_score=0.8
        )

        # Format for evaluation
        formatted = []
        for test in recycled:
            formatted.append({
                "input": test["input"],
                "expected": test.get("expected", test.get("expected_behavior", "")),
                "context": {
                    **test.get("metadata", {}),
                    "suite": "recycled"
                }
            })

        return formatted

    def _prepare_adversarial_tests(self) -> list[dict[str, Any]]:
        """Prepare adversarial test cases."""
        # Create adversarial suite
        suite = create_test_suite(
            categories=[
                AdversarialCategory.PROMPT_INJECTION,
                AdversarialCategory.JAILBREAK,
                AdversarialCategory.HARMFUL_CONTENT
            ],
            min_severity="medium"
        )

        # Format for evaluation
        formatted = []
        for test in suite["tests"][:15]:  # Limit to 15 tests
            formatted.append({
                "input": test.attack_vector,
                "expected": test.expected_behavior,
                "context": {
                    "category": test.category.value,
                    "severity": test.severity,
                    "subcategory": test.subcategory,
                    "suite": "adversarial"
                }
            })

        return formatted

    def _compute_metrics(
        self,
        results: BatchResult,
        test_metadata: dict[str, int]
    ) -> dict[str, float]:
        """Compute comprehensive metrics from results."""
        metrics = {
            "overall_pass_rate": results.pass_rate,
            "overall_avg_score": results.avg_score,
            "total_tests": results.total,
            "passed_tests": results.passed,
            "failed_tests": results.failed,
        }

        # Compute per-suite metrics
        suite_results = defaultdict(lambda: {"total": 0, "passed": 0, "scores": []})

        for result in results.results:
            suite = result.details.get("context", {}).get("suite", "unknown")
            suite_results[suite]["total"] += 1
            if result.passed:
                suite_results[suite]["passed"] += 1
            suite_results[suite]["scores"].append(result.score)

        # Add suite-specific metrics
        for suite, data in suite_results.items():
            if data["total"] > 0:
                metrics[f"{suite}_pass_rate"] = data["passed"] / data["total"]
                metrics[f"{suite}_avg_score"] = sum(data["scores"]) / len(data["scores"])

        # Performance metrics
        response_times = []
        token_counts = []

        for result in results.results:
            if "response_time_ms" in result.details:
                response_times.append(result.details["response_time_ms"])
            if "token_usage" in result.details:
                token_counts.append(result.details["token_usage"].get("total", 0))

        if response_times:
            metrics["avg_response_time_ms"] = sum(response_times) / len(response_times)
            metrics["p95_response_time_ms"] = sorted(response_times)[int(len(response_times) * 0.95)]

        if token_counts:
            metrics["avg_tokens_per_request"] = sum(token_counts) / len(token_counts)

        return metrics

    async def _detect_agent_version(self) -> str:
        """Detect agent version or identifier."""
        try:
            # Try to get version from agent
            if hasattr(self.agent, "version"):
                return str(self.agent.version)
            elif hasattr(self.agent, "__version__"):
                return str(self.agent.__version__)
            elif callable(self.agent):
                # For callable agents, use function name
                return f"callable_{self.agent.__name__}"
            else:
                # For URL agents, use URL hash
                return f"url_{hashlib.md5(str(self.agent).encode()).hexdigest()[:8]}"
        except:
            return "unknown"

    def _detect_regressions(self, current_run: EvaluationRun) -> list[RegressionAlert]:
        """Detect regressions compared to baselines."""
        alerts = []

        # Get baseline for comparison
        baseline = self._get_baseline(current_run.test_suite)
        if not baseline:
            # No baseline yet, set current as baseline
            self._update_baseline(current_run)
            return alerts

        # Check each metric
        for metric, current_value in current_run.metrics.items():
            if metric not in baseline:
                continue

            baseline_value = baseline[metric]

            # Determine if regression based on metric type
            is_regression = False
            degradation = 0.0

            if "pass_rate" in metric or "score" in metric:
                # Higher is better
                degradation = (baseline_value - current_value) / baseline_value
                is_regression = current_value < baseline_value * 0.95  # 5% tolerance
            elif "time" in metric or "tokens" in metric:
                # Lower is better
                degradation = (current_value - baseline_value) / baseline_value
                is_regression = current_value > baseline_value * 1.05  # 5% tolerance

            if is_regression:
                # Determine severity
                severity = self._determine_severity(metric, degradation)

                # Find affected tests
                affected_tests = self._find_affected_tests(
                    current_run.results,
                    metric
                )

                alert = RegressionAlert(
                    alert_id=f"regression_{current_run.run_id}_{metric}",
                    timestamp=datetime.now(),
                    metric=metric,
                    baseline_value=baseline_value,
                    current_value=current_value,
                    degradation=degradation,
                    affected_tests=affected_tests[:10],  # Limit to 10
                    severity=severity,
                    details={
                        "run_id": current_run.run_id,
                        "agent_version": current_run.agent_version
                    }
                )

                alerts.append(alert)

        return alerts

    def _determine_severity(self, metric: str, degradation: float) -> str:
        """Determine regression severity."""
        # Critical metrics
        if any(m in metric for m in ["safety", "adversarial", "security"]):
            if degradation > 0.1:
                return "critical"
            elif degradation > 0.05:
                return "high"
            else:
                return "medium"

        # Performance metrics
        elif any(m in metric for m in ["time", "latency", "response"]):
            if degradation > 0.5:  # 50% slower
                return "high"
            elif degradation > 0.2:
                return "medium"
            else:
                return "low"

        # Quality metrics
        else:
            if degradation > 0.2:  # 20% worse
                return "high"
            elif degradation > 0.1:
                return "medium"
            else:
                return "low"

    def _find_affected_tests(
        self,
        results: BatchResult,
        metric: str
    ) -> list[str]:
        """Find tests most affected by regression."""
        affected = []

        # Determine which results to check based on metric
        if any(suite in metric for suite in ["gold_standard", "synthetic", "recycled", "adversarial"]):
            # Suite-specific metric
            suite = metric.split("_")[0]
            for result in results.results:
                if result.details.get("context", {}).get("suite") == suite and not result.passed:
                    test_id = result.details.get("context", {}).get("task_id", str(result.details.get("input", ""))[:50])
                    affected.append(test_id)
        else:
            # General metric - check all failed tests
            for result in results.results:
                if not result.passed:
                    test_id = result.details.get("context", {}).get("task_id", str(result.details.get("input", ""))[:50])
                    affected.append(test_id)

        return affected

    async def _handle_regression(self, alert: RegressionAlert) -> None:
        """Handle regression alert."""
        logger.warning(
            f"Regression detected in {alert.metric}: "
            f"{alert.baseline_value:.3f} -> {alert.current_value:.3f} "
            f"({alert.degradation:.1%} degradation)"
        )

        # Save alert
        self.alerts.append(alert)
        self._save_alert(alert)

        # Call callback if provided
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

        # Export to telemetry
        if self.telemetry_exporter:
            await self._export_alert(alert)

    def _get_baseline(self, test_suite: str) -> dict[str, float] | None:
        """Get baseline metrics for comparison."""
        return self.baselines.get(test_suite)

    def _update_baseline(self, run: EvaluationRun) -> None:
        """Update baseline with new run."""
        # Simple strategy: use best recent run as baseline
        # More sophisticated strategies could use rolling averages, etc.
        current_baseline = self.baselines.get(run.test_suite, {})

        for metric, value in run.metrics.items():
            if metric not in current_baseline:
                current_baseline[metric] = value
            else:
                # Update based on metric type
                if "pass_rate" in metric or "score" in metric:
                    # Higher is better
                    current_baseline[metric] = max(current_baseline[metric], value)
                elif "time" in metric or "tokens" in metric:
                    # Lower is better
                    current_baseline[metric] = min(current_baseline[metric], value)

        self.baselines[run.test_suite] = current_baseline
        self._save_baselines()

    def _save_run(self, run: EvaluationRun) -> None:
        """Save evaluation run to disk."""
        run_file = self.evaluation_dir / f"{run.run_id}.json"

        data = {
            "run_id": run.run_id,
            "timestamp": run.timestamp.isoformat(),
            "agent_version": run.agent_version,
            "test_suite": run.test_suite,
            "metrics": run.metrics,
            "metadata": run.metadata,
            "summary": {
                "total": run.results.total,
                "passed": run.results.passed,
                "failed": run.results.failed,
                "pass_rate": run.results.pass_rate,
                "avg_score": run.results.avg_score
            }
        }

        with open(run_file, "w") as f:
            json.dump(data, f, indent=2)

    def _save_alert(self, alert: RegressionAlert) -> None:
        """Save alert to disk."""
        alert_file = self.evaluation_dir / "alerts" / f"{alert.alert_id}.json"
        alert_file.parent.mkdir(exist_ok=True)

        data = {
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp.isoformat(),
            "metric": alert.metric,
            "baseline_value": alert.baseline_value,
            "current_value": alert.current_value,
            "degradation": alert.degradation,
            "affected_tests": alert.affected_tests,
            "severity": alert.severity,
            "details": alert.details
        }

        with open(alert_file, "w") as f:
            json.dump(data, f, indent=2)

    def _save_baselines(self) -> None:
        """Save baselines to disk."""
        baseline_file = self.evaluation_dir / "baselines.json"
        with open(baseline_file, "w") as f:
            json.dump(self.baselines, f, indent=2)

    def _load_history(self) -> None:
        """Load evaluation history from disk."""
        # Load baselines
        baseline_file = self.evaluation_dir / "baselines.json"
        if baseline_file.exists():
            with open(baseline_file) as f:
                self.baselines = json.load(f)

        # Load recent runs
        for run_file in sorted(self.evaluation_dir.glob("eval_*.json"))[-10:]:
            # We don't fully reconstruct runs, just track that they exist
            logger.info(f"Found previous run: {run_file.name}")

    async def _export_telemetry(self, run: EvaluationRun) -> None:
        """Export run data to telemetry."""
        if not self.telemetry_exporter:
            return

        # Create span for evaluation run
        span_data = {
            "name": f"evaluation.run.{run.test_suite}",
            "attributes": {
                "run.id": run.run_id,
                "agent.version": run.agent_version,
                "test.suite": run.test_suite,
                **{f"metric.{k}": v for k, v in run.metrics.items()}
            }
        }

        await self.telemetry_exporter.export([span_data])

    async def _export_alert(self, alert: RegressionAlert) -> None:
        """Export alert to telemetry."""
        if not self.telemetry_exporter:
            return

        # Create span for alert
        span_data = {
            "name": "evaluation.regression.alert",
            "attributes": {
                "alert.id": alert.alert_id,
                "alert.metric": alert.metric,
                "alert.severity": alert.severity,
                "alert.degradation": alert.degradation,
                "baseline.value": alert.baseline_value,
                "current.value": alert.current_value
            }
        }

        await self.telemetry_exporter.export([span_data])

    def get_trend_analysis(
        self,
        metric: str,
        days: int = 7
    ) -> dict[str, Any]:
        """Analyze trends for a specific metric."""
        # This would analyze historical runs
        # For now, return a simple summary
        return {
            "metric": metric,
            "period_days": days,
            "current_value": self.baselines.get("all", {}).get(metric, 0),
            "trend": "stable",  # Would calculate from history
            "recommendation": "Continue monitoring"
        }


# Convenience function
async def start_continuous_evaluation(
    agent: str | Callable | Any,
    interval_hours: int = 24,
    test_suites: list[str] | None = None,
    alert_callback: Callable[[RegressionAlert], None] | None = None
) -> ContinuousEvaluationPipeline:
    """
    Start continuous evaluation with periodic runs.

    Args:
        agent: Agent to evaluate
        interval_hours: Hours between evaluation runs
        test_suites: Test suites to include
        alert_callback: Callback for regression alerts

    Returns:
        Running pipeline instance
    """
    pipeline = ContinuousEvaluationPipeline(
        agent=agent,
        alert_callback=alert_callback
    )

    async def run_loop():
        while True:
            try:
                await pipeline.run_evaluation_cycle(test_suites=test_suites)
            except Exception as e:
                logger.error(f"Error in evaluation cycle: {e}")

            # Wait for next cycle
            await asyncio.sleep(interval_hours * 3600)

    # Start in background
    asyncio.create_task(run_loop())

    return pipeline
