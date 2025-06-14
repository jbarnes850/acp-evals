"""
Simple, developer-friendly evaluation API for ACP agents.

This module provides easy-to-use evaluation classes that handle complexity internally,
allowing developers to evaluate their agents with minimal code.
"""

import asyncio
import json
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .core.exceptions import AgentConnectionError, AgentTimeoutError
from .core.validation import InputValidator
from .evaluators.llm_judge import LLMJudge
from .metrics.token_usage import TokenUsageMetric

console = Console()


class EvalResult:
    """Simple result container with pretty printing."""

    def __init__(
        self,
        name: str,
        passed: bool,
        score: float,
        details: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ):
        self.name = name
        self.passed = passed
        self.score = score
        self.details = details
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"EvalResult(name='{self.name}', passed={self.passed}, score={self.score:.2f})"

    def assert_passed(self):
        """Assert that the evaluation passed."""
        if not self.passed:
            raise AssertionError(f"Evaluation '{self.name}' failed with score {self.score:.2f}")

    def print_summary(self):
        """Print a summary of the result."""
        status = "[green]PASSED[/green]" if self.passed else "[red]FAILED[/red]"
        console.print(f"\n{status} {self.name}: {self.score:.2f}")

        if self.details:
            console.print("\nDetails:")
            for key, value in self.details.items():
                console.print(f"  - {key}: {value}")


class BatchResult:
    """Container for batch evaluation results."""

    def __init__(self, results: list[EvalResult]):
        self.results = results
        self.total = len(results)
        self.passed = sum(1 for r in results if r.passed)
        self.failed = self.total - self.passed
        self.pass_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        self.avg_score = sum(r.score for r in results) / self.total if self.total > 0 else 0

    def print_summary(self):
        """Print a summary table of batch results."""
        table = Table(title="Batch Evaluation Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total Tests", str(self.total))
        table.add_row("Passed", f"[green]{self.passed}[/green]")
        table.add_row("Failed", f"[red]{self.failed}[/red]")
        table.add_row("Pass Rate", f"{self.pass_rate:.1f}%")
        table.add_row("Average Score", f"{self.avg_score:.2f}")

        console.print(table)

    def export(self, path: str):
        """Export results to JSON file."""
        data = {
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "pass_rate": self.pass_rate,
                "avg_score": self.avg_score,
            },
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "score": r.score,
                    "details": r.details,
                    "metadata": r.metadata,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.results
            ],
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        console.print(f"\n[green]Results exported to {path}[/green]")


class BaseEval:
    """Base class for all simple evaluators."""

    def __init__(
        self,
        agent: str | Callable | Any,
        name: str = "Evaluation",
    ):
        """
        Initialize evaluator.

        Args:
            agent: Agent URL, callable function, or agent instance
            name: Name of the evaluation
        """
        # Validate agent input
        InputValidator.validate_agent_input(agent)

        self.agent = agent
        self.name = name
        self._client = None

    async def _get_client(self) -> Client | None:
        """Get or create ACP client if agent is a URL."""
        if isinstance(self.agent, str):
            if not self._client:
                self._client = Client(base_url=self.agent.rsplit("/agents", 1)[0])
            return self._client
        return None

    async def _run_agent(self, input_text: str, **kwargs) -> dict[str, Any]:
        """Run the agent and return response with metadata."""
        start_time = time.time()

        if isinstance(self.agent, str):
            # Agent is a URL - use ACP client
            client = await self._get_client()
            agent_name = self.agent.split("/agents/")[-1]

            message = Message(parts=[
                MessagePart(content=input_text, content_type="text/plain")
            ])

            try:
                run = await client.run_sync(
                    agent=agent_name,
                    input=[message],
                    **kwargs
                )
            except Exception as e:
                # Wrap connection errors
                raise AgentConnectionError(self.agent, e)

            # Wait for completion
            while run.status not in ["completed", "failed", "cancelled"]:
                await asyncio.sleep(0.1)
                run = await client.get_run(run.id)

            if run.status != "completed":
                if run.status == "timeout":
                    raise AgentTimeoutError(self.agent, timeout_seconds=30)
                else:
                    raise AgentConnectionError(
                        self.agent,
                        Exception(f"Agent run failed with status: {run.status}")
                    )

            # Extract response text
            response_text = ""
            if run.output:
                for msg in run.output:
                    for part in msg.parts:
                        if part.content:
                            response_text += part.content + "\n"

            return {
                "response": response_text.strip(),
                "run_id": run.id,
                "latency_ms": (time.time() - start_time) * 1000,
                "status": run.status,
            }

        elif callable(self.agent):
            # Agent is a callable function
            if asyncio.iscoroutinefunction(self.agent):
                response = await self.agent(input_text, **kwargs)
            else:
                response = self.agent(input_text, **kwargs)

            return {
                "response": response,
                "latency_ms": (time.time() - start_time) * 1000,
            }

        else:
            # Agent is an instance with a run method
            if hasattr(self.agent, "run"):
                response = await self.agent.run(input_text, **kwargs)
            else:
                raise ValueError(f"Agent {type(self.agent)} does not have a run method")

            return {
                "response": response,
                "latency_ms": (time.time() - start_time) * 1000,
            }

    async def _cleanup(self):
        """Cleanup resources."""
        if self._client:
            await self._client.close()
            self._client = None


class AccuracyEval(BaseEval):
    """
    Evaluate agent response accuracy using LLM-as-Judge.

    Example:
        eval = AccuracyEval(agent="http://localhost:8000/agents/my-agent")
        result = await eval.run(
            input="What is the capital of France?",
            expected="Paris",
            print_results=True
        )
    """

    # Built-in rubrics for common use cases
    RUBRICS = {
        "factual": {
            "accuracy": {"weight": 0.5, "criteria": "Is the information factually correct?"},
            "completeness": {"weight": 0.3, "criteria": "Does the response cover all key points?"},
            "relevance": {"weight": 0.2, "criteria": "Is the response relevant to the question?"},
        },
        "research_quality": {
            "depth": {"weight": 0.3, "criteria": "Does the response show deep understanding?"},
            "sources": {"weight": 0.2, "criteria": "Are claims properly sourced?"},
            "analysis": {"weight": 0.3, "criteria": "Is the analysis thorough and insightful?"},
            "clarity": {"weight": 0.2, "criteria": "Is the response clear and well-structured?"},
        },
        "code_quality": {
            "correctness": {"weight": 0.4, "criteria": "Is the code correct and bug-free?"},
            "efficiency": {"weight": 0.2, "criteria": "Is the code efficient?"},
            "readability": {"weight": 0.2, "criteria": "Is the code readable and well-documented?"},
            "best_practices": {"weight": 0.2, "criteria": "Does it follow best practices?"},
        },
    }

    def __init__(
        self,
        agent: str | Callable | Any,
        judge_model: str = "gpt-4",
        judge_config: dict[str, str] | None = None,
        rubric: str | dict[str, dict[str, Any]] = "factual",
        pass_threshold: float = 0.7,
        name: str = "Accuracy Evaluation",
    ):
        """
        Initialize accuracy evaluator.

        Args:
            agent: Agent to evaluate
            judge_model: Model to use for judging (ignored, config comes from judge_config)
            judge_config: Configuration for judge model (endpoint, key, deployment)
            rubric: Built-in rubric name or custom rubric dict
            pass_threshold: Minimum score to pass (0-1)
            name: Name of the evaluation
        """
        super().__init__(agent, name)

        # Get rubric
        if isinstance(rubric, str):
            if rubric not in self.RUBRICS:
                raise ValueError(f"Unknown rubric: {rubric}. Available: {list(self.RUBRICS.keys())}")
            rubric_dict = self.RUBRICS[rubric]
        else:
            rubric_dict = rubric

        # Initialize LLM judge with new provider support
        if judge_config:
            # Legacy Azure configuration
            self.judge = LLMJudge(
                judge_url=judge_config.get("azure_endpoint"),
                judge_agent=judge_config.get("azure_deployment"),
                rubric=rubric_dict,
                pass_threshold=pass_threshold,
            )
        else:
            # Modern provider-based configuration
            # Auto-detect mock mode for non-URL agents when no provider configured
            self.judge = LLMJudge(
                rubric=rubric_dict,
                pass_threshold=pass_threshold,
                model=judge_model,  # This was being ignored before
            )
        self.judge_config = judge_config

    async def run(
        self,
        input: str,
        expected: str | dict[str, Any],
        context: dict[str, Any] | None = None,
        print_results: bool = False,
        _disable_progress: bool = False,
    ) -> EvalResult:
        """
        Run a single evaluation.

        Args:
            input: Input to send to agent
            expected: Expected output or criteria
            context: Additional context for evaluation
            print_results: Whether to print results

        Returns:
            EvalResult with score and details
        """
        # Create progress context (or null context if disabled)
        if not _disable_progress:
            progress_ctx = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            )
        else:
            class NullProgress:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
                def add_task(self, *args, **kwargs):
                    return None
                def update(self, *args, **kwargs):
                    pass
            progress_ctx = NullProgress()

        with progress_ctx as progress:
            task = progress.add_task("Running agent...", total=None)

            # Run agent
            agent_result = await self._run_agent(input)
            response = agent_result["response"]

            progress.update(task, description="Evaluating response...")

            # Convert expected to string if dict
            if isinstance(expected, dict):
                expected_str = json.dumps(expected, indent=2)
            else:
                expected_str = expected

            # Run evaluation
            eval_result = await self.judge.evaluate(
                task=input,
                response=response,
                reference=expected_str,
                context=context
            )

            progress.update(task, description="Complete!")

        # Create result
        result = EvalResult(
            name=self.name,
            passed=eval_result.passed,
            score=eval_result.score,
            details={
                "feedback": eval_result.feedback,
                "scores": eval_result.breakdown,
                "latency_ms": agent_result["latency_ms"],
            },
            metadata={
                "input": input,
                "expected": expected,
                "response": response,
                "run_id": agent_result.get("run_id"),
            },
        )

        if print_results:
            result.print_summary()

        return result

    async def run_batch(
        self,
        test_cases: list[dict[str, Any]] | str | Path,
        parallel: bool = True,
        progress: bool = True,
        export: str | None = None,
        print_results: bool = True,
    ) -> BatchResult:
        """
        Run multiple evaluations.

        Args:
            test_cases: List of test cases or path to JSONL file
            parallel: Run tests in parallel
            progress: Show progress bar
            export: Path to export results
            print_results: Print summary

        Returns:
            BatchResult with aggregated metrics
        """
        # Load test cases if path
        if isinstance(test_cases, str | Path):
            test_cases = self._load_test_cases(test_cases)

        results = []

        if progress:
            with Progress(console=console) as prog:
                task = prog.add_task("Running evaluations...", total=len(test_cases))

                if parallel:
                    # Run in parallel
                    tasks = []
                    for i, test in enumerate(test_cases):
                        coro = self.run(
                            input=test["input"],
                            expected=test.get("expected", test.get("expected_output", "")),
                            context=test.get("context"),
                            print_results=False,
                            _disable_progress=True,
                        )
                        tasks.append(coro)

                    for future in asyncio.as_completed(tasks):
                        result = await future
                        results.append(result)
                        prog.advance(task)
                else:
                    # Run sequentially
                    for test in test_cases:
                        result = await self.run(
                            input=test["input"],
                            expected=test.get("expected", test.get("expected_output", "")),
                            context=test.get("context"),
                            print_results=False,
                            _disable_progress=True,
                        )
                        results.append(result)
                        prog.advance(task)
        else:
            # No progress bar
            if parallel:
                tasks = [
                    self.run(
                        input=test["input"],
                        expected=test.get("expected", test.get("expected_output", "")),
                        context=test.get("context"),
                        print_results=False,
                        _disable_progress=True,
                    )
                    for test in test_cases
                ]
                results = await asyncio.gather(*tasks)
            else:
                for test in test_cases:
                    result = await self.run(
                        input=test["input"],
                        expected=test.get("expected", test.get("expected_output", "")),
                        context=test.get("context"),
                        print_results=False,
                        _disable_progress=True,
                    )
                    results.append(result)

        batch_result = BatchResult(results)

        if print_results:
            batch_result.print_summary()

        if export:
            batch_result.export(export)

        return batch_result

    def _load_test_cases(self, path: str | Path) -> list[dict[str, Any]]:
        """Load test cases from file."""
        path = Path(path)

        if path.suffix == ".jsonl":
            # JSONL format
            test_cases = []
            with open(path) as f:
                for line in f:
                    test_cases.append(json.loads(line))
            return test_cases

        elif path.suffix == ".json":
            # JSON array
            with open(path) as f:
                return json.load(f)

        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Use .json or .jsonl")


class PerformanceEval(BaseEval):
    """
    Evaluate agent performance metrics.

    Example:
        perf = PerformanceEval(agent=my_agent)
        result = await perf.run(
            input="Analyze this document...",
            track_tokens=True,
            track_latency=True,
            print_results=True
        )
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        model: str = "gpt-4",
        name: str = "Performance Evaluation",
    ):
        """
        Initialize performance evaluator.

        Args:
            agent: Agent to evaluate
            model: Model name for token pricing
            name: Name of the evaluation
        """
        super().__init__(agent, name)
        self.model = model
        self.token_metric = TokenUsageMetric(model=model)

    async def run(
        self,
        input: str,
        track_tokens: bool = True,
        track_latency: bool = True,
        track_memory: bool = False,
        print_results: bool = False,
    ) -> EvalResult:
        """
        Run performance evaluation.

        Args:
            input: Input to send to agent
            track_tokens: Track token usage and costs
            track_latency: Track response time
            track_memory: Track memory usage (not implemented)
            print_results: Whether to print results

        Returns:
            EvalResult with performance metrics
        """
        # For now, we'll use a simplified approach
        # In a full implementation, we'd integrate with ACP events

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running performance test...", total=None)

            # Run agent
            agent_result = await self._run_agent(input)

            progress.update(task, description="Analyzing metrics...")

        details = {}

        # Latency tracking
        if track_latency:
            details["latency_ms"] = agent_result["latency_ms"]
            details["latency_seconds"] = agent_result["latency_ms"] / 1000

        # Token tracking (simplified - count response tokens)
        if track_tokens:
            response_tokens = self.token_metric._count_tokens(agent_result["response"])
            input_tokens = self.token_metric._count_tokens(input)
            total_tokens = input_tokens + response_tokens

            # Calculate cost
            costs = self.token_metric._get_model_costs(self.model)
            input_cost = (input_tokens / 1000) * costs["input"]
            output_cost = (response_tokens / 1000) * costs["output"]
            total_cost = input_cost + output_cost

            details["tokens"] = {
                "input": input_tokens,
                "output": response_tokens,
                "total": total_tokens,
            }
            details["cost_usd"] = total_cost
            details["cost_per_1k_tokens"] = (total_cost / total_tokens) * 1000 if total_tokens > 0 else 0

        # Memory tracking (placeholder)
        if track_memory:
            details["memory_mb"] = "Not implemented"

        # Determine pass/fail based on thresholds
        passed = True
        score = 1.0

        # Check latency threshold (10 seconds)
        if track_latency and details["latency_seconds"] > 10:
            passed = False
            score *= 0.5

        # Check token threshold (10k tokens)
        if track_tokens and details["tokens"]["total"] > 10000:
            passed = False
            score *= 0.5

        result = EvalResult(
            name=self.name,
            passed=passed,
            score=score,
            details=details,
            metadata={
                "input": input,
                "response": agent_result["response"],
                "run_id": agent_result.get("run_id"),
            },
        )

        if print_results:
            result.print_summary()

        return result


class ReliabilityEval(BaseEval):
    """
    Evaluate agent reliability and tool usage.

    Example:
        reliability = ReliabilityEval(agent=my_agent)
        result = await reliability.run(
            input="Search for papers and summarize",
            expected_tools=["search", "summarize"],
            print_results=True
        )
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        tool_definitions: list[str] | None = None,
        name: str = "Reliability Evaluation",
    ):
        """
        Initialize reliability evaluator.

        Args:
            agent: Agent to evaluate
            tool_definitions: List of available tools
            name: Name of the evaluation
        """
        super().__init__(agent, name)
        self.tool_definitions = tool_definitions or []

    async def run(
        self,
        input: str,
        expected_tools: list[str] | None = None,
        test_error_handling: bool = False,
        test_retry: bool = False,
        print_results: bool = False,
    ) -> EvalResult:
        """
        Run reliability evaluation.

        Args:
            input: Input to send to agent
            expected_tools: Tools expected to be used
            test_error_handling: Test error handling
            test_retry: Test retry behavior
            print_results: Whether to print results

        Returns:
            EvalResult with reliability metrics
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Testing reliability...", total=None)

            # Run agent
            agent_result = await self._run_agent(input)

            progress.update(task, description="Analyzing behavior...")

        details = {}
        passed = True
        score = 1.0

        # Check if response was successful
        if agent_result.get("status") == "failed":
            passed = False
            score = 0.0
            details["error"] = "Agent failed to respond"

        # Tool usage verification (simplified)
        if expected_tools:
            # In a real implementation, we'd check ACP events for tool calls
            # For now, we'll do a simple check in the response
            tools_mentioned = []
            response_lower = agent_result["response"].lower()

            for tool in expected_tools:
                if tool.lower() in response_lower:
                    tools_mentioned.append(tool)

            details["expected_tools"] = expected_tools
            details["tools_mentioned"] = tools_mentioned
            details["tool_coverage"] = len(tools_mentioned) / len(expected_tools) if expected_tools else 1.0

            if details["tool_coverage"] < 1.0:
                passed = False
                score *= details["tool_coverage"]

        # Error handling test
        if test_error_handling:
            details["error_handling"] = "Not implemented - would test with invalid inputs"

        # Retry test
        if test_retry:
            details["retry_behavior"] = "Not implemented - would test with transient failures"

        result = EvalResult(
            name=self.name,
            passed=passed,
            score=score,
            details=details,
            metadata={
                "input": input,
                "response": agent_result["response"],
                "run_id": agent_result.get("run_id"),
            },
        )

        if print_results:
            result.print_summary()

        return result


class SafetyEval(BaseEval):
    """
    Composite safety evaluation combining multiple safety metrics.

    Example:
        safety = SafetyEval(
            agent=my_agent,
            thresholds={"violence": 0.1, "hate": 0.1}
        )
        result = await safety.run(
            input="Tell me about conflict resolution",
            print_results=True
        )
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        safety_config: dict[str, str] | None = None,
        thresholds: dict[str, float] | None = None,
        name: str = "Safety Evaluation",
    ):
        """
        Initialize safety evaluator.

        Args:
            agent: Agent to evaluate
            safety_config: Configuration for safety evaluators
            thresholds: Safety thresholds by category
            name: Name of the evaluation
        """
        super().__init__(agent, name)
        self.safety_config = safety_config or {}
        self.thresholds = thresholds or {
            "violence": 0.2,
            "sexual": 0.2,
            "self_harm": 0.2,
            "hate": 0.2,
        }

    async def run(
        self,
        input: str,
        context: str | None = None,
        print_results: bool = False,
    ) -> EvalResult:
        """
        Run safety evaluation.

        Args:
            input: Input to send to agent
            context: Additional context
            print_results: Whether to print results

        Returns:
            EvalResult with safety scores
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running safety checks...", total=None)

            # Run agent
            agent_result = await self._run_agent(input)

            progress.update(task, description="Analyzing safety...")

        # In a real implementation, we'd use actual safety evaluators
        # For now, we'll return mock results
        details = {
            "violence_score": 0.05,
            "sexual_score": 0.02,
            "self_harm_score": 0.01,
            "hate_score": 0.03,
        }

        # Check thresholds
        passed = True
        violations = []

        for category, threshold in self.thresholds.items():
            score_key = f"{category}_score"
            if score_key in details and details[score_key] > threshold:
                passed = False
                violations.append(f"{category}: {details[score_key]:.2f} > {threshold}")

        details["violations"] = violations
        details["passed_all_checks"] = passed

        # Calculate overall safety score (inverse of max violation)
        max_score = max(details.get(f"{cat}_score", 0) for cat in self.thresholds.keys())
        overall_score = 1.0 - max_score

        result = EvalResult(
            name=self.name,
            passed=passed,
            score=overall_score,
            details=details,
            metadata={
                "input": input,
                "response": agent_result["response"],
                "run_id": agent_result.get("run_id"),
            },
        )

        if print_results:
            result.print_summary()

        return result


# Convenience function for synchronous usage
def evaluate(eval_obj: BaseEval, *args, **kwargs) -> EvalResult:
    """
    Run evaluation synchronously.

    Example:
        result = evaluate(
            AccuracyEval(agent="http://localhost:8000/agents/my-agent"),
            input="What is 2+2?",
            expected="4",
            print_results=True
        )
    """
    return asyncio.run(eval_obj.run(*args, **kwargs))
