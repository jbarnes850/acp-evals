"""
LLM-as-Judge evaluator based on Anthropic research.

Uses a single LLM call with structured rubric for consistent evaluation.
Supports both real LLM providers and mock mode for testing.
"""

import json
import logging
import os
import re
from typing import Any

from acp_evals.core.exceptions import (
    ConfigurationError,
    InvalidEvaluationInputError,
    ProviderError,
)
from acp_evals.core.validation import InputValidator
from acp_evals.evaluators.base import EvaluationResult, Evaluator

logger = logging.getLogger(__name__)


class LLMJudge(Evaluator):
    """
    Automated evaluation using LLM with structured rubrics.

    Based on Anthropic's findings that single LLM calls with
    comprehensive rubrics are more consistent than multiple calls.

    Supports multiple LLM providers (OpenAI, Anthropic, Azure, Ollama)
    with automatic fallback to mock mode for testing.
    """

    DEFAULT_RUBRIC = {
        "factual_accuracy": {
            "weight": 0.3,
            "criteria": "Does the response accurately answer the question with correct information?"
        },
        "completeness": {
            "weight": 0.25,
            "criteria": "Does the response address all aspects of the task or question?"
        },
        "clarity": {
            "weight": 0.2,
            "criteria": "Is the response clear, well-structured, and easy to understand?"
        },
        "relevance": {
            "weight": 0.15,
            "criteria": "Does the response stay focused on the task without unnecessary information?"
        },
        "efficiency": {
            "weight": 0.1,
            "criteria": "Is the response appropriately concise while remaining complete?"
        }
    }

    def __init__(
        self,
        # Legacy parameters for backward compatibility
        judge_url: str | None = None,
        judge_agent: str | None = None,

        # New provider-based parameters
        provider: str | None = None,
        model: str | None = None,

        # Common parameters
        rubric: dict[str, dict[str, Any]] | None = None,
        pass_threshold: float = 0.7,
        mock_mode: bool | None = None,

        # LLM parameters
        temperature: float = 0.0,
        max_tokens: int = 1000,

        **provider_kwargs
    ):
        """
        Initialize LLM Judge.

        Args:
            judge_url: (Legacy) URL of ACP server - triggers provider mode if None
            judge_agent: (Legacy) Agent name - ignored in provider mode
            provider: LLM provider to use (auto-detects if not specified)
            model: Model to use (uses provider default if not specified)
            rubric: Custom evaluation rubric (uses default if None)
            pass_threshold: Minimum score to pass (0.0 to 1.0)
            mock_mode: Force mock mode (auto-detected if None)
            temperature: LLM temperature (0.0 for consistent evaluation)
            max_tokens: Maximum tokens for evaluation response
            **provider_kwargs: Additional provider-specific configuration
        """
        self.rubric = rubric or self.DEFAULT_RUBRIC
        self.pass_threshold = pass_threshold
        self.temperature = temperature or float(os.getenv("EVALUATION_TEMPERATURE", "0.0"))
        self.max_tokens = max_tokens or int(os.getenv("EVALUATION_MAX_TOKENS", "1000"))

        # Determine if we should use provider mode or legacy ACP mode
        self.use_provider_mode = judge_url is None or judge_url == "http://localhost:8000"

        # Initialize provider if in provider mode
        if self.use_provider_mode:
            # Lazy import to avoid circular dependency
            from acp_evals.providers import ProviderFactory

            try:
                # Auto-detect provider if not specified
                if not provider:
                    provider = ProviderFactory.get_default_provider()
                    if not provider:
                        if mock_mode is False:
                            raise ValueError(
                                "No LLM provider configured. Please set up API keys in .env file "
                                "or pass provider configuration."
                            )
                        # No provider and mock_mode not explicitly False - use mock
                        self.provider = None
                        self.provider_name = "mock"
                        self.mock_mode = True
                    else:
                        # Provider found
                        if model:
                            provider_kwargs["model"] = model
                        self.provider = ProviderFactory.create(provider, **provider_kwargs)
                        self.provider_name = provider
                        self.mock_mode = False
                else:
                    # Provider explicitly specified
                    if model:
                        provider_kwargs["model"] = model
                    self.provider = ProviderFactory.create(provider, **provider_kwargs)
                    self.provider_name = provider
                    self.mock_mode = False

            except Exception as e:
                if mock_mode is False:
                    # User explicitly wants real LLM, so fail
                    raise
                # Fall back to mock mode
                print(f"Warning: {str(e)}. Falling back to mock evaluation mode.")
                self.provider = None
                self.provider_name = "mock"
                self.mock_mode = True
        else:
            # Legacy ACP mode
            self.judge_url = judge_url
            self.judge_agent = judge_agent or "default"
            self.mock_mode = mock_mode if mock_mode is not None else False
            self.provider = None
            self.provider_name = "acp"

            if not self.mock_mode:
                from acp_sdk.client import Client
                self.client = Client(base_url=judge_url)

    @property
    def name(self) -> str:
        if self.use_provider_mode:
            return f"llm_judge_{self.provider_name}"
        return "llm_judge"

    def _build_evaluation_prompt(
        self,
        task: str,
        response: str,
        reference: str | None = None,
    ) -> str:
        """Build the evaluation prompt for the judge LLM."""
        rubric_text = ""
        for criterion, details in self.rubric.items():
            rubric_text += f"\n- {criterion} (weight: {details['weight']}): {details['criteria']}"

        prompt = f"""You are an expert evaluator assessing an AI agent's response quality.

Task given to the agent:
{task}

Agent's response:
{response}

{f"Reference answer for comparison:\n{reference}\n" if reference else ""}

Evaluation rubric:{rubric_text}

Instructions:
1. Evaluate the response on each criterion, providing a score from 0.0 to 1.0
2. Calculate the weighted overall score
3. Provide brief, constructive feedback
4. Return your evaluation as a JSON object with this structure:
{{
    "scores": {{
        "criterion_name": score,
        ...
    }},
    "overall_score": weighted_score,
    "passed": true/false (based on >= {self.pass_threshold}),
    "feedback": "Brief explanation of strengths and areas for improvement"
}}

Important: Return ONLY the JSON object, no other text."""

        return prompt

    def _mock_evaluate(self, task: str, response: str, reference: str | None = None) -> EvaluationResult:
        """Simple mock evaluation for testing."""
        scores = {}
        for criterion, details in self.rubric.items():
            # Simple scoring logic for testing
            if reference and response:
                if str(reference).lower() in str(response).lower():
                    scores[criterion] = 1.0
                elif response.lower() != "i don't know":
                    scores[criterion] = 0.5
                else:
                    scores[criterion] = 0.2
            else:
                scores[criterion] = 0.5

        # Calculate weighted score
        total_weight = sum(d["weight"] for d in self.rubric.values())
        overall_score = sum(
            scores[c] * self.rubric[c]["weight"] / total_weight
            for c in scores
        )

        return EvaluationResult(
            score=overall_score,
            passed=overall_score >= self.pass_threshold,
            breakdown=scores,
            feedback="Mock evaluation (no LLM provider configured)"
        )

    async def evaluate(
        self,
        task: str,
        response: str,
        reference: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate an agent response using LLM judge.

        Args:
            task: The task/prompt given to the agent
            response: The agent's response
            reference: Optional reference answer
            context: Optional additional context

        Returns:
            EvaluationResult with score and breakdown

        Raises:
            InvalidEvaluationInputError: If inputs are invalid
            ProviderError: If LLM provider fails
            EvaluationTimeoutError: If evaluation times out
        """
        # Validate inputs
        try:
            InputValidator.validate_test_input(task)
            InputValidator.validate_test_input(response)
            if reference:
                InputValidator.validate_expected_output(reference)
        except InvalidEvaluationInputError as e:
            logger.error(f"Invalid evaluation input: {e}")
            raise

        # Use mock evaluation if in mock mode
        if self.mock_mode:
            return self._mock_evaluate(task, response, reference)

        # Build evaluation prompt
        eval_prompt = self._build_evaluation_prompt(task, response, reference)

        if self.use_provider_mode and self.provider:
            # Use LLM provider
            try:
                # Get evaluation from LLM
                llm_response = await self.provider.complete(
                    prompt=eval_prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                # Parse JSON response
                try:
                    evaluation = json.loads(llm_response.content)
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    json_match = re.search(r'\{.*\}', llm_response.content, re.DOTALL)
                    if json_match:
                        evaluation = json.loads(json_match.group())
                    else:
                        raise ValueError(f"Could not parse LLM response as JSON: {llm_response.content[:200]}...")

                # Validate and extract evaluation data
                scores = evaluation.get("scores", {})
                overall_score = evaluation.get("overall_score", 0.0)
                passed = evaluation.get("passed", overall_score >= self.pass_threshold)
                feedback = evaluation.get("feedback", "No feedback provided")

                # Add usage and cost info to feedback if available
                if llm_response.usage:
                    feedback += f"\n\n[Evaluation used {llm_response.usage.get('total_tokens', 0)} tokens"
                    if llm_response.cost and llm_response.cost > 0:
                        feedback += f", cost: ${llm_response.cost:.4f}"
                    feedback += "]"

                return EvaluationResult(
                    score=overall_score,
                    passed=passed,
                    breakdown=scores,
                    feedback=feedback,
                    metadata={
                        "provider": self.provider_name,
                        "model": self.provider.model,
                        "usage": llm_response.usage,
                        "cost": llm_response.cost
                    }
                )

            except ProviderError as e:
                # Re-raise provider errors with context
                logger.error(f"Provider error during evaluation: {e}")
                raise

            except json.JSONDecodeError as e:
                # Log error and provide helpful message
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.debug(f"Raw response: {llm_response.content[:500]}...")

                # Try to provide a meaningful error
                raise ConfigurationError(
                    "LLM did not return valid JSON evaluation. This may indicate the model "
                    "is not suitable for evaluation tasks. Try using a different model.",
                    suggestion="Consider using GPT-4 or Claude-3 for better results"
                )

            except Exception as e:
                # Log unexpected errors
                logger.error(f"Unexpected error during LLM evaluation: {str(e)}", exc_info=True)

                # Provide context about the error
                raise ConfigurationError(
                    f"Evaluation failed: {str(e)}",
                    suggestion="Check logs for details. You may want to try mock mode for testing."
                )

        else:
            # Legacy ACP mode
            from acp_sdk import Message, MessagePart

            # Create message for judge
            message = Message(
                parts=[MessagePart(content=eval_prompt, content_type="text/plain")]
            )

            try:
                # Get evaluation from judge LLM
                run = await self.client.run_sync(
                    agent=self.judge_agent,
                    input=[message]
                )

                # Extract response
                if run.output and run.output[0].parts:
                    judge_response = run.output[0].parts[0].content

                    # Parse JSON response
                    try:
                        evaluation = json.loads(judge_response)
                    except json.JSONDecodeError:
                        # Try to extract JSON from response
                        json_match = re.search(r'\{.*\}', judge_response, re.DOTALL)
                        if json_match:
                            evaluation = json.loads(json_match.group())
                        else:
                            raise ValueError("Could not parse judge response as JSON")

                    # Create result
                    return EvaluationResult(
                        score=evaluation.get("overall_score", 0.0),
                        passed=evaluation.get("passed", False),
                        breakdown=evaluation.get("scores", {}),
                        feedback=evaluation.get("feedback", "No feedback provided")
                    )
                else:
                    raise ValueError("No response from judge agent")

            except Exception as e:
                # Return error result
                return EvaluationResult(
                    score=0.0,
                    passed=False,
                    breakdown={},
                    feedback=f"Evaluation failed: {str(e)}"
                )
