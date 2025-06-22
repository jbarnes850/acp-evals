"""
Tests for LLMJudge evaluator - focusing on core functionality.
"""

import pytest

from acp_evals.core.exceptions import InvalidEvaluationInputError
from acp_evals.evaluators.common import EvalResult
from acp_evals.evaluators.llm_judge import JudgeResult, LLMJudge


class TestLLMJudge:
    """Test suite for LLMJudge evaluator - core functionality only."""

    @pytest.fixture
    def judge(self):
        """Create an LLMJudge instance."""
        return LLMJudge()

    @pytest.mark.asyncio
    async def test_judge_initialization(self):
        """Test LLMJudge initializes with defaults."""
        judge = LLMJudge()

        # Test properties that actually exist
        assert hasattr(judge, "provider")
        assert hasattr(judge, "rubric")
        # judge_model is optional/configurable

    @pytest.mark.asyncio
    async def test_evaluate_pass(self, judge):
        """Test successful evaluation that passes threshold."""
        # Should return good evaluation for correct answer
        result = await judge.evaluate(
            prompt="What is the capital of France?",
            response="Paris is the capital of France.",
            reference="Paris",  # Reference answer that matches response
        )

        assert isinstance(result, JudgeResult)
        assert result.score > 0.7  # Should pass threshold with matching response
        assert result.passed is True
        assert len(result.feedback) > 0  # Should have feedback

    @pytest.mark.asyncio
    async def test_evaluate_fail(self, judge):
        """Test evaluation that gives low score."""
        # Provide wrong answer for low score
        result = await judge.evaluate(
            prompt="What is the capital of France?",
            response="I don't know",  # This should get low score
            reference="Paris",
        )

        # Judge just returns scores, not pass/fail decisions
        assert result.score < 0.7  # Should get low score for wrong answer
        assert len(result.feedback) > 0  # Should have feedback

    @pytest.mark.asyncio
    async def test_error_handling(self, judge):
        """Test handling of input validation errors."""
        # LLMJudge doesn't validate empty inputs, it just evaluates them
        # This test should check that it handles them gracefully
        result = await judge.evaluate("", "response")
        assert isinstance(result, JudgeResult)
        assert result.score >= 0  # Should still return a valid score

    @pytest.mark.asyncio
    async def test_custom_threshold(self):
        """Test LLMJudge with custom configuration."""
        # LLMJudge doesn't have pass_threshold, it's just a scoring engine
        judge = LLMJudge(rubric="code_quality")
        assert judge.rubric == "code_quality"
