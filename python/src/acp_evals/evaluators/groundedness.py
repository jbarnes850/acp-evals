"""
Groundedness evaluator for ACP agents.

Evaluates whether agent responses are grounded in the provided context
and don't include hallucinated information.
"""

from typing import Any

from ..providers.base import LLMProvider
from .base import EvaluationResult, Evaluator


class GroundednessEvaluator(Evaluator):
    """
    Evaluates if agent responses are grounded in the provided context.

    This evaluator checks whether the agent's response contains only
    information that can be traced back to the given context, without
    adding hallucinated or unsupported claims.
    """

    def __init__(self, provider: LLMProvider | None = None):
        """
        Initialize the groundedness evaluator.

        Args:
            provider: LLM provider for evaluation (uses default if None)
        """
        self.provider = provider
        self._evaluation_prompt = """
You are an AI assistant evaluating the groundedness of a response.

Context provided:
{context}

Agent's response:
{response}

Task: Evaluate whether the agent's response is fully grounded in the provided context.

Evaluation criteria:
1. All factual claims in the response must be supported by the context
2. The response should not include information not present in the context
3. Reasonable inferences from the context are acceptable
4. The response should not contradict the context

Provide your evaluation in the following format:
- Grounded claims: [List specific claims that are supported by context]
- Ungrounded claims: [List any claims not supported by context]
- Contradictions: [List any contradictions with the context]
- Overall groundedness score: [0.0-1.0, where 1.0 is fully grounded]
- Explanation: [Brief explanation of the score]
"""

    @property
    def name(self) -> str:
        """Name of the evaluator."""
        return "GroundednessEvaluator"

    async def evaluate(
        self,
        task: str,
        response: str,
        reference: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate groundedness of an agent response.

        Args:
            task: The task/prompt given to the agent
            response: The agent's response
            reference: Not used for groundedness evaluation
            context: Must contain 'context' key with the grounding context

        Returns:
            EvaluationResult with groundedness score and breakdown
        """
        if not context or 'context' not in context:
            return EvaluationResult(
                score=0.0,
                passed=False,
                breakdown={"error": "No context provided for groundedness evaluation"},
                feedback="Context is required for groundedness evaluation",
                metadata={"evaluator": self.name}
            )

        grounding_context = context['context']

        # Use LLM to evaluate groundedness
        if self.provider:
            prompt = self._evaluation_prompt.format(
                context=grounding_context,
                response=response
            )

            try:
                evaluation = await self.provider.generate(prompt)

                # Parse the evaluation
                score = self._extract_score(evaluation)
                grounded_claims = self._extract_list(evaluation, "Grounded claims:")
                ungrounded_claims = self._extract_list(evaluation, "Ungrounded claims:")
                contradictions = self._extract_list(evaluation, "Contradictions:")
                explanation = self._extract_section(evaluation, "Explanation:")

                passed = score >= 0.8  # 80% threshold for passing

                breakdown = {
                    "grounded_claims": len(grounded_claims),
                    "ungrounded_claims": len(ungrounded_claims),
                    "contradictions": len(contradictions),
                    "groundedness_score": score
                }

                feedback = f"Groundedness: {score:.2f}/1.0. "
                if ungrounded_claims:
                    feedback += f"Found {len(ungrounded_claims)} ungrounded claims. "
                if contradictions:
                    feedback += f"Found {len(contradictions)} contradictions. "
                feedback += explanation

            except Exception as e:
                score = 0.0
                passed = False
                breakdown = {"error": str(e)}
                feedback = f"Error during evaluation: {str(e)}"
        else:
            # Fallback: Simple keyword matching
            score = self._simple_groundedness_check(response, grounding_context)
            passed = score >= 0.8
            breakdown = {"groundedness_score": score}
            feedback = f"Groundedness score: {score:.2f} (using simple keyword matching)"

        return EvaluationResult(
            score=score,
            passed=passed,
            breakdown=breakdown,
            feedback=feedback,
            metadata={
                "evaluator": self.name,
                "task": task,
                "context_length": len(grounding_context),
                "response_length": len(response)
            }
        )

    def _simple_groundedness_check(self, response: str, context: str) -> float:
        """Simple groundedness check using keyword overlap."""
        # Extract key terms from response
        response_terms = set(response.lower().split())
        context_terms = set(context.lower().split())

        # Remove common words
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                       'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                       'could', 'should', 'may', 'might', 'can', 'of', 'to', 'in',
                       'on', 'at', 'by', 'for', 'with', 'from', 'up', 'down', 'out'}

        response_terms = response_terms - common_words
        context_terms = context_terms - common_words

        # Calculate overlap
        if not response_terms:
            return 1.0  # Empty response is technically grounded

        overlap = response_terms.intersection(context_terms)
        score = len(overlap) / len(response_terms)

        return min(score * 1.2, 1.0)  # Boost score slightly, cap at 1.0

    def _extract_score(self, text: str) -> float:
        """Extract score from evaluation text."""
        import re
        pattern = r"Overall groundedness score:\s*([0-9.]+)"
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        return 0.5  # Default middle score

    def _extract_list(self, text: str, marker: str) -> list[str]:
        """Extract list items after a marker."""
        lines = text.split('\n')
        items = []
        found_marker = False

        for line in lines:
            if marker in line:
                found_marker = True
                continue
            if found_marker and line.strip():
                if line.strip().startswith('-'):
                    items.append(line.strip()[1:].strip())
                elif any(line.strip().startswith(m) for m in ['Ungrounded', 'Contradictions', 'Overall', 'Explanation']):
                    break
                else:
                    items.append(line.strip())

        return items

    def _extract_section(self, text: str, marker: str) -> str:
        """Extract text section after a marker."""
        if marker in text:
            parts = text.split(marker)
            if len(parts) > 1:
                return parts[1].strip().split('\n')[0].strip()
        return ""
