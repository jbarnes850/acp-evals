"""
Tests for LLMJudge evaluator - focusing on core functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import json

from acp_evals.evaluators.llm_judge import LLMJudge
from acp_evals.base import EvaluatorResult


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
        
        assert judge.judge_agent == "default"
        assert judge.pass_threshold == 0.7
        assert hasattr(judge, 'rubric')
    
    @pytest.mark.asyncio
    async def test_evaluate_pass(self, judge):
        """Test successful evaluation that passes threshold."""
        # Mock the client's run_sync method
        mock_run = Mock()
        mock_run.output = [Mock(parts=[Mock(content=json.dumps({
            "scores": {"accuracy": 0.9},
            "overall_score": 0.85,
            "passed": True,
            "feedback": "Good answer."
        }))])]
        
        judge.client.run_sync = AsyncMock(return_value=mock_run)
        
        result = await judge.evaluate(
            "What is the capital of France?",
            "Paris is the capital of France.",
            "The capital of France is Paris."
        )
        
        assert isinstance(result, EvaluatorResult)
        assert result.score == 0.85
        assert result.passed is True
    
    @pytest.mark.asyncio
    async def test_evaluate_fail(self, judge):
        """Test evaluation that fails threshold."""
        # Mock failing response
        mock_run = Mock()
        mock_run.output = [Mock(parts=[Mock(content=json.dumps({
            "scores": {"accuracy": 0.3},
            "overall_score": 0.3,
            "passed": False,
            "feedback": "Incorrect answer."
        }))])]
        
        judge.client.run_sync = AsyncMock(return_value=mock_run)
        
        result = await judge.evaluate(
            "What is the capital of France?",
            "London is the capital of France.",
            "The capital of France is Paris."
        )
        
        assert result.score == 0.3
        assert result.passed is False
    
    @pytest.mark.asyncio
    async def test_error_handling(self, judge):
        """Test handling of LLM errors."""
        # Mock response with invalid JSON
        mock_run = Mock()
        mock_run.output = [Mock(parts=[Mock(content="Not valid JSON")])]
        
        judge.client.run_sync = AsyncMock(return_value=mock_run)
        
        result = await judge.evaluate("task", "response")
        
        assert result.score == 0.0
        assert result.passed is False
        assert "failed" in result.feedback.lower()
    
    @pytest.mark.asyncio
    async def test_custom_threshold(self):
        """Test custom pass threshold."""
        judge = LLMJudge(pass_threshold=0.9)
        assert judge.pass_threshold == 0.9