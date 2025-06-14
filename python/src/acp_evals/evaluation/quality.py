"""
Quality evaluators for specific evaluation criteria.

These evaluators focus on specific aspects of response quality.
"""

from collections.abc import Callable
from typing import Any

from ..simple import AccuracyEval, EvalResult


class GroundednessEval(AccuracyEval):
    """
    Evaluate if responses are grounded in provided context.

    Use this when agents have access to specific documents or context
    and you want to ensure they don't hallucinate.
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        name: str = "Groundedness Evaluation",
    ):
        """Initialize groundedness evaluator."""
        rubric = {
            "grounded_in_context": {
                "weight": 0.4,
                "criteria": "Is every claim in the response directly supported by the provided context?"
            },
            "no_hallucination": {
                "weight": 0.3,
                "criteria": "Does the response avoid adding information not present in the context?"
            },
            "accurate_citations": {
                "weight": 0.2,
                "criteria": "Are sources/citations accurate when provided?"
            },
            "acknowledges_limitations": {
                "weight": 0.1,
                "criteria": "Does the response acknowledge when information is not available in context?"
            }
        }

        super().__init__(
            agent=agent,
            rubric=rubric,
            pass_threshold=0.8,  # High threshold for groundedness
            name=name
        )

    async def run(
        self,
        input: str,
        context: dict[str, Any],
        expected: str | None = None,
        print_results: bool = False,
        _disable_progress: bool = False,
    ) -> EvalResult:
        """
        Run groundedness evaluation.

        Args:
            input: The query/prompt
            context: The context that should ground the response
                    Should include 'documents' or 'sources' key
            expected: Optional expected behavior description
            print_results: Whether to print results

        Returns:
            EvalResult with groundedness score
        """
        # Ensure context includes source material
        if "documents" not in context and "sources" not in context:
            raise ValueError("Context must include 'documents' or 'sources' for groundedness evaluation")

        # Create expected behavior if not provided
        if expected is None:
            expected = "Response should be fully grounded in the provided context without hallucination"

        return await super().run(
            input=input,
            expected=expected,
            context=context,
            print_results=print_results,
            _disable_progress=_disable_progress
        )


class CompletenessEval(AccuracyEval):
    """
    Evaluate if responses fully address all aspects of a query.

    Use this to ensure agents don't ignore parts of multi-part questions
    or complex requests.
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        name: str = "Completeness Evaluation",
    ):
        """Initialize completeness evaluator."""
        rubric = {
            "addresses_all_parts": {
                "weight": 0.4,
                "criteria": "Does the response address every part of the multi-part question?"
            },
            "sufficient_detail": {
                "weight": 0.3,
                "criteria": "Is each part answered with appropriate depth and detail?"
            },
            "logical_organization": {
                "weight": 0.2,
                "criteria": "Are all parts organized in a logical, easy-to-follow structure?"
            },
            "no_missing_elements": {
                "weight": 0.1,
                "criteria": "Are there no obviously missing elements that the question asked for?"
            }
        }

        super().__init__(
            agent=agent,
            rubric=rubric,
            pass_threshold=0.75,
            name=name
        )


class TaskAdherenceEval(AccuracyEval):
    """
    Evaluate if responses follow specific task instructions.

    Use this when you have specific format requirements, constraints,
    or instructions that must be followed.
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        task_requirements: dict[str, str] | None = None,
        name: str = "Task Adherence Evaluation",
    ):
        """
        Initialize task adherence evaluator.

        Args:
            agent: Agent to evaluate
            task_requirements: Specific requirements to check
                             e.g., {"format": "JSON", "length": "< 500 words"}
        """
        rubric = {
            "follows_instructions": {
                "weight": 0.4,
                "criteria": "Does the response follow all given instructions exactly?"
            },
            "correct_format": {
                "weight": 0.3,
                "criteria": "Is the response in the requested format (if specified)?"
            },
            "meets_constraints": {
                "weight": 0.2,
                "criteria": "Does the response meet all specified constraints (length, style, etc.)?"
            },
            "appropriate_tone": {
                "weight": 0.1,
                "criteria": "Is the tone/style appropriate for the requested task?"
            }
        }

        super().__init__(
            agent=agent,
            rubric=rubric,
            pass_threshold=0.8,
            name=name
        )

        self.task_requirements = task_requirements or {}


class ToolAccuracyEval(AccuracyEval):
    """
    Evaluate if tool-using agents select and use tools correctly.

    Use this for agents that have access to calculators, search engines,
    databases, or other tools.
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        available_tools: list[str],
        name: str = "Tool Accuracy Evaluation",
    ):
        """
        Initialize tool accuracy evaluator.

        Args:
            agent: Agent to evaluate
            available_tools: List of tool names the agent can use
        """
        rubric = {
            "correct_tool_selection": {
                "weight": 0.4,
                "criteria": "Does the agent select the most appropriate tool(s) for the task?"
            },
            "proper_tool_usage": {
                "weight": 0.3,
                "criteria": "Are tools used with correct parameters and in the right sequence?"
            },
            "result_interpretation": {
                "weight": 0.2,
                "criteria": "Does the agent correctly interpret and use tool outputs?"
            },
            "efficiency": {
                "weight": 0.1,
                "criteria": "Are tools used efficiently without unnecessary calls?"
            }
        }

        super().__init__(
            agent=agent,
            rubric=rubric,
            pass_threshold=0.75,
            name=name
        )

        self.available_tools = available_tools

    async def run(
        self,
        input: str,
        expected_tools: list[str],
        context: dict[str, Any] | None = None,
        print_results: bool = False,
        _disable_progress: bool = False,
    ) -> EvalResult:
        """
        Run tool accuracy evaluation.

        Args:
            input: The task requiring tool use
            expected_tools: Tools that should be used for this task
            context: Additional context
            print_results: Whether to print results

        Returns:
            EvalResult with tool accuracy score
        """
        # Add tool information to context
        if context is None:
            context = {}

        context["available_tools"] = self.available_tools
        context["expected_tools"] = expected_tools

        # Create expected behavior description
        expected = f"Use tools {expected_tools} appropriately to complete the task"

        return await super().run(
            input=input,
            expected=expected,
            context=context,
            print_results=print_results,
            _disable_progress=_disable_progress
        )


# Composite Quality Evaluator
class QualityEval:
    """
    Comprehensive quality evaluation combining multiple aspects.

    This runs multiple quality evaluations and provides an overall
    quality score.
    """

    def __init__(
        self,
        agent: str | Callable | Any,
        evaluate_groundedness: bool = True,
        evaluate_completeness: bool = True,
        evaluate_task_adherence: bool = True,
        evaluate_tool_accuracy: bool = False,
        available_tools: list[str] | None = None,
    ):
        """
        Initialize comprehensive quality evaluator.

        Args:
            agent: Agent to evaluate
            evaluate_groundedness: Include groundedness checks
            evaluate_completeness: Include completeness checks
            evaluate_task_adherence: Include task adherence checks
            evaluate_tool_accuracy: Include tool accuracy checks
            available_tools: Required if evaluate_tool_accuracy is True
        """
        self.agent = agent
        self.evaluators = {}

        if evaluate_groundedness:
            self.evaluators["groundedness"] = GroundednessEval(agent)

        if evaluate_completeness:
            self.evaluators["completeness"] = CompletenessEval(agent)

        if evaluate_task_adherence:
            self.evaluators["task_adherence"] = TaskAdherenceEval(agent)

        if evaluate_tool_accuracy:
            if not available_tools:
                raise ValueError("available_tools required for tool accuracy evaluation")
            self.evaluators["tool_accuracy"] = ToolAccuracyEval(agent, available_tools)

    async def run(
        self,
        input: str,
        context: dict[str, Any] | None = None,
        expected: str | dict[str, Any] | None = None,
        expected_tools: list[str] | None = None,
        print_results: bool = True,
    ) -> dict[str, Any]:
        """
        Run comprehensive quality evaluation.

        Returns:
            Dictionary with results from each evaluator and overall score
        """
        results = {}
        scores = []

        # Run applicable evaluators
        if "groundedness" in self.evaluators and context and ("documents" in context or "sources" in context):
            result = await self.evaluators["groundedness"].run(
                input=input,
                context=context,
                expected=expected,
                print_results=False
            )
            results["groundedness"] = result
            scores.append(result.score)

        if "completeness" in self.evaluators:
            result = await self.evaluators["completeness"].run(
                input=input,
                expected=expected,
                context=context,
                print_results=False
            )
            results["completeness"] = result
            scores.append(result.score)

        if "task_adherence" in self.evaluators:
            result = await self.evaluators["task_adherence"].run(
                input=input,
                expected=expected,
                context=context,
                print_results=False
            )
            results["task_adherence"] = result
            scores.append(result.score)

        if "tool_accuracy" in self.evaluators and expected_tools:
            result = await self.evaluators["tool_accuracy"].run(
                input=input,
                expected_tools=expected_tools,
                context=context,
                print_results=False
            )
            results["tool_accuracy"] = result
            scores.append(result.score)

        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        overall_passed = overall_score >= 0.75

        summary = {
            "overall_score": overall_score,
            "overall_passed": overall_passed,
            "aspect_scores": {name: r.score for name, r in results.items()},
            "detailed_results": results
        }

        if print_results:
            from rich.console import Console
            from rich.table import Table

            console = Console()

            # Create summary table
            table = Table(title="Quality Evaluation Results")
            table.add_column("Aspect", style="cyan")
            table.add_column("Score", style="magenta")
            table.add_column("Status", style="green")

            for name, result in results.items():
                status = "✅" if result.passed else "❌"
                table.add_row(
                    name.replace("_", " ").title(),
                    f"{result.score:.2f}",
                    status
                )

            table.add_row(
                "[bold]Overall[/bold]",
                f"[bold]{overall_score:.2f}[/bold]",
                "✅" if overall_passed else "❌",
                style="bold"
            )

            console.print(table)

        return summary
