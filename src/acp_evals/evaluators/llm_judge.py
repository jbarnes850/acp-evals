"""LLM Judge for evaluating agent outputs."""

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from ..providers.base import LLMProvider
from ..providers.factory import ProviderFactory


@dataclass
class JudgeResult:
    """Result from LLM judge evaluation."""

    score: float
    feedback: str
    passed: bool
    breakdown: dict[str, float] | None = None


class LLMJudge:
    """Simple LLM-based judge for evaluating outputs."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        rubric: dict[str, Any] | None = None,
        pass_threshold: float = 0.7,
        model: str | None = None,
        judge_url: str | None = None,
        judge_agent: str | None = None,
        **kwargs,
    ):
        """Initialize with optional provider and configuration."""
        self.provider = provider or ProviderFactory.create()
        self.rubric = rubric or {}
        self.pass_threshold = pass_threshold
        self.model = model
        self.judge_url = judge_url
        self.judge_agent = judge_agent

    async def evaluate(
        self,
        task: str = None,
        prompt: str = None,
        response: str = None,
        reference: str = None,
        expected: str = None,
        rubric: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> JudgeResult:
        """Evaluate response against expected output."""
        # Use task or prompt for the input
        input_text = task or prompt or ""

        # Use reference if expected not provided
        check_against = reference or expected or ""

        # Build evaluation prompt
        eval_prompt = f"""
You are an expert evaluator. Please evaluate the following response based on the expected output.

Input: {input_text}
Response: {response}
Expected: {check_against}

Please score the response from 0.0 to 1.0 based on how well it matches the expected output.
Consider:
- Factual accuracy
- Completeness
- Relevance

Respond with:
- Score: [0.0-1.0]
- Feedback: [Brief explanation]
"""

        try:
            # Use the LLM provider to evaluate
            response_obj = await self.provider.complete(eval_prompt)
            result = response_obj.content

            # Parse the response - handle different formats
            lines = result.strip().split("\n")
            score = None
            feedback = ""

            for line in lines:
                line = line.strip()
                # Handle different score formats
                if line.startswith("Score:") or line.startswith("- Score:"):
                    try:
                        score_text = line.split(":")[-1].strip()
                        score = float(score_text)
                        # Ensure score is within valid range
                        score = max(0.0, min(1.0, score))
                    except (ValueError, TypeError):
                        # If we can't parse the score, this is a critical error
                        raise ValueError(f"LLM judge returned invalid score format: {line}")
                # Handle different feedback formats
                elif line.startswith("Feedback:") or line.startswith("- Feedback:"):
                    feedback = line.split(":", 1)[-1].strip()

            # If we couldn't parse score or feedback, this is a critical error
            if score is None or not feedback:
                raise ValueError(
                    f"LLM judge failed to provide score and feedback. Raw response: {result}"
                )

        except Exception as e:
            # NO FALLBACKS - if LLM evaluation fails, we must fail
            raise RuntimeError(f"LLM evaluation failed and no fallbacks allowed: {str(e)}")

        passed = score >= self.pass_threshold

        return JudgeResult(
            score=score, passed=passed, feedback=feedback, breakdown={"similarity": score}
        )

    async def compare(
        self, prompt: str, response1: str, response2: str, criteria: str | None = None
    ) -> dict[str, Any]:
        """Compare two responses using LLM evaluation."""
        comparison_prompt = f"""
You are an expert evaluator. Please compare the following two responses to determine which is better.

Prompt: {prompt}

Response 1: {response1}

Response 2: {response2}

Criteria: {criteria or "Overall quality, accuracy, helpfulness, and relevance"}

Please evaluate and respond with:
- Similarity: [0.0-1.0] (how similar the responses are)
- Preferred: [1 or 2] (which response is better, or "tie" if equal)
- Feedback: [Brief explanation of your assessment]
"""

        try:
            response_obj = await self.provider.complete(comparison_prompt)
            result = response_obj.content

            # Parse the response
            lines = result.strip().split("\n")
            similarity = 0.5  # Default neutral similarity
            preferred = None
            feedback = ""

            for line in lines:
                if line.startswith("Similarity:"):
                    try:
                        similarity = float(line.split(":")[-1].strip())
                        similarity = max(0.0, min(1.0, similarity))
                    except (ValueError, TypeError):
                        raise ValueError(f"LLM judge returned invalid similarity format: {line}")
                elif line.startswith("Preferred:"):
                    pref_text = line.split(":", 1)[-1].strip().lower()
                    if "1" in pref_text:
                        preferred = 1
                    elif "2" in pref_text:
                        preferred = 2
                    elif "tie" in pref_text:
                        preferred = None
                elif line.startswith("Feedback:"):
                    feedback = line.split(":", 1)[-1].strip()

            if not feedback:
                raise ValueError(
                    f"LLM judge failed to provide comparison feedback. Raw response: {result}"
                )

            return {"similarity": similarity, "feedback": feedback, "preferred": preferred}

        except Exception as e:
            # NO FALLBACKS - if LLM evaluation fails, we must fail
            raise RuntimeError(f"LLM comparison failed and no fallbacks allowed: {str(e)}")
