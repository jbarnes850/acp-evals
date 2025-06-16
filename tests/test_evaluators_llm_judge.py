"""
Tests for LLMJudge evaluator - focusing on core functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import json

from acp_evals.evaluators.llm_judge import LLMJudge
from acp_evals.evaluators.base import EvaluationResult
from acp_evals.core.exceptions import InvalidEvaluationInputError


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
        
        # Test modern properties that actually exist
        assert judge.pass_threshold == 0.7
        assert hasattr(judge, 'rubric')
        # Mock mode depends on whether providers are configured
        assert hasattr(judge, 'mock_mode')
    
    @pytest.mark.asyncio
    async def test_evaluate_pass(self, judge):
        """Test successful evaluation that passes threshold."""
        # Should return good evaluation for correct answer
        result = await judge.evaluate(
            "What is the capital of France?",
            "Paris is the capital of France.",
            "Paris"  # Reference answer that matches response
        )
        
        assert isinstance(result, EvaluationResult)
        assert result.score > 0.7  # Should pass threshold with matching response
        assert result.passed is True
        assert len(result.feedback) > 0  # Should have feedback
    
    @pytest.mark.asyncio
    async def test_evaluate_fail(self, judge):
        """Test evaluation that fails threshold."""
        # Provide wrong answer for low score
        result = await judge.evaluate(
            "What is the capital of France?",
            "I don't know",  # This should get low score
            "Paris"
        )
        
        assert result.score < 0.7  # Should fail threshold
        assert result.passed is False
        assert len(result.feedback) > 0  # Should have feedback
    
    @pytest.mark.asyncio
    async def test_error_handling(self, judge):
        """Test handling of input validation errors."""
        # Test with empty input which should raise validation error
        with pytest.raises(InvalidEvaluationInputError):
            await judge.evaluate("", "response")
    
    @pytest.mark.asyncio
    async def test_custom_threshold(self):
        """Test custom pass threshold."""
        judge = LLMJudge(pass_threshold=0.9)
        assert judge.pass_threshold == 0.9