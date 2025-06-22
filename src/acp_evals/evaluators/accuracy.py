"""
Accuracy evaluation using LLM-as-judge methodology.

This module provides the AccuracyEval class for evaluating agent responses
against expected outputs using configurable rubrics.
"""

import asyncio
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rich.progress import Progress, SpinnerColumn, TextColumn

from .common import BaseEval, BatchResult, EvalResult, console
from .llm_judge import LLMJudge


class AccuracyEval(BaseEval):
    """
    Evaluate agent response accuracy using LLM-as-Judge.

    Supports both continuous scoring (default) and binary mode based on
    research showing binary outputs improve evaluator performance.

    Example:
        # Traditional continuous scoring
        eval = AccuracyEval(agent="http://localhost:8000/agents/my-agent")

        # Binary mode (recommended for better performance)
        eval = AccuracyEval(
            agent="http://localhost:8000/agents/my-agent",
            binary_mode=True,
            binary_threshold=0.7
        )

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
        binary_mode: bool = False,
        binary_threshold: float | None = None,
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
            binary_mode: Use binary pass/fail instead of continuous scoring
            binary_threshold: Threshold for binary mode (defaults to pass_threshold)
        """
        super().__init__(agent, name)

        # Get rubric
        if isinstance(rubric, str):
            if rubric not in self.RUBRICS:
                raise ValueError(
                    f"Unknown rubric: {rubric}. Available: {list(self.RUBRICS.keys())}"
                )
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
        self.binary_mode = binary_mode
        self.binary_threshold = binary_threshold or pass_threshold

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

            if task is not None:
                progress.update(task, description="Evaluating response...")

            # Convert expected to string if dict
            if isinstance(expected, dict):
                expected_str = json.dumps(expected, indent=2)
            else:
                expected_str = expected

            # Run evaluation
            eval_result = await self.judge.evaluate(
                task=input, response=response, reference=expected_str, context=context
            )

            if task is not None:
                progress.update(task, description="Complete!")

        # Apply binary mode if enabled
        if self.binary_mode:
            # Convert continuous score to binary decision
            binary_passed = eval_result.score >= self.binary_threshold
            binary_score = 1.0 if binary_passed else 0.0

            # Add binary mode info to feedback
            binary_feedback = (
                f"{eval_result.feedback}\n\n"
                f"[Binary Mode: {'PASS' if binary_passed else 'FAIL'} "
                f"(score {eval_result.score:.3f} vs threshold {self.binary_threshold:.3f})]"
            )

            # Create result with binary scoring
            result = EvalResult(
                name=self.name,
                passed=binary_passed,
                score=binary_score,
                details={
                    "feedback": binary_feedback,
                    "scores": eval_result.breakdown,
                    "latency_ms": agent_result["latency_ms"],
                    "binary_mode": True,
                    "original_score": eval_result.score,
                    "threshold": self.binary_threshold,
                },
                metadata={
                    "input": input,
                    "expected": expected,
                    "response": response,
                    "run_id": agent_result.get("run_id"),
                },
            )
        else:
            # Traditional continuous scoring
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
            # Use rich display components for comprehensive LLM evaluation details
            from ..cli.display import display_single_evaluation_result

            display_single_evaluation_result(
                evaluation_type="accuracy",
                agent_identifier=str(self.agent),
                input_text=input,
                result=result,
                show_details=True,
                show_performance=True,
            )

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
            # Use rich display components for batch results
            from ..cli.display import display_evaluation_report

            # Convert batch results to display format
            display_data = {
                "scores": {"overall": batch_result.avg_score},
                "test_results": [
                    {
                        "name": f"Test {i + 1}",
                        "passed": result.passed,
                        "score": result.score,
                        "reason": result.details.get("feedback", "")[:100] + "..."
                        if len(result.details.get("feedback", "")) > 100
                        else result.details.get("feedback", ""),
                    }
                    for i, result in enumerate(batch_result.results)
                ],
                "metrics": {
                    "total_tests": batch_result.total,
                    "passed": batch_result.passed,
                    "failed": batch_result.failed,
                    "pass_rate": f"{batch_result.pass_rate:.1f}%",
                    "average_score": batch_result.avg_score,
                },
            }

            display_evaluation_report(
                display_data, show_details=True, show_suggestions=False, show_costs=False
            )

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
