"""
Tests for LLMJudge evaluator implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from acp_evals.evaluators.llm_judge import LLMJudge
from acp_evals.base import EvaluatorResult


class TestLLMJudge:
    """Test suite for LLMJudge evaluator."""
    
    @pytest.fixture
    def judge(self):
        """Create an LLMJudge instance."""
        return LLMJudge(model="gpt-4")
    
    @pytest.fixture
    def custom_rubric(self):
        """Create a custom evaluation rubric."""
        return {
            "accuracy": {
                "weight": 0.4,
                "criteria": "How accurate is the information?",
            },
            "relevance": {
                "weight": 0.3,
                "criteria": "How relevant is the response to the question?",
            },
            "completeness": {
                "weight": 0.3,
                "criteria": "How complete is the answer?",
            },
        }
    
    @pytest.mark.asyncio
    async def test_judge_initialization(self):
        """Test LLMJudge initialization with defaults."""
        judge = LLMJudge()
        
        assert judge.model == "gpt-4"
        assert judge.rubric == LLMJudge.DEFAULT_RUBRIC
        assert judge.temperature == 0.0
        assert judge.pass_threshold == 0.7
    
    @pytest.mark.asyncio
    async def test_judge_with_custom_rubric(self, custom_rubric):
        """Test LLMJudge with custom rubric."""
        judge = LLMJudge(rubric=custom_rubric, pass_threshold=0.8)
        
        assert judge.rubric == custom_rubric
        assert judge.pass_threshold == 0.8
        
        # Verify rubric validation
        total_weight = sum(c["weight"] for c in custom_rubric.values())
        assert total_weight == pytest.approx(1.0, rel=0.01)
    
    @pytest.mark.asyncio
    async def test_build_evaluation_prompt(self, judge):
        """Test evaluation prompt construction."""
        output = "Paris is the capital of France."
        reference = "The capital of France is Paris."
        
        prompt = judge._build_evaluation_prompt(output, reference)
        
        assert output in prompt
        assert reference in prompt
        assert "JSON" in prompt
        
        # Check that all rubric criteria are included
        for criterion, details in judge.rubric.items():
            assert criterion in prompt
            assert details["criteria"] in prompt
    
    @pytest.mark.asyncio
    @patch('acp_evals.evaluators.llm_judge.LLMJudge._call_llm')
    async def test_evaluate_success(self, mock_call_llm, judge):
        """Test successful evaluation."""
        # Mock LLM response
        mock_response = {
            "score": 0.85,
            "pass": True,
            "feedback": "Good answer with minor issues.",
            "scores": {
                "factual_accuracy": 0.9,
                "completeness": 0.8,
                "clarity": 0.85,
                "relevance": 0.9,
                "efficiency": 0.8,
            },
        }
        mock_call_llm.return_value = json.dumps(mock_response)
        
        result = await judge.evaluate(
            "Paris is the capital of France.",
            "The capital of France is Paris."
        )
        
        assert isinstance(result, EvaluatorResult)
        assert result.score == 0.85
        assert result.passed is True
        assert result.feedback == "Good answer with minor issues."
        assert result.details["scores"] == mock_response["scores"]
    
    @pytest.mark.asyncio
    @patch('acp_evals.evaluators.llm_judge.LLMJudge._call_llm')
    async def test_evaluate_with_context(self, mock_call_llm, judge):
        """Test evaluation with additional context."""
        mock_response = {
            "score": 0.9,
            "pass": True,
            "feedback": "Excellent answer.",
            "scores": {criterion: 0.9 for criterion in judge.rubric},
        }
        mock_call_llm.return_value = json.dumps(mock_response)
        
        context = {
            "task_type": "factual_qa",
            "difficulty": "easy",
            "domain": "geography",
        }
        
        result = await judge.evaluate(
            "Paris",
            "Paris",
            context=context
        )
        
        # Check that context was passed to prompt
        call_args = mock_call_llm.call_args[0][0]
        assert "factual_qa" in call_args
        assert "geography" in call_args
    
    @pytest.mark.asyncio
    @patch('acp_evals.evaluators.llm_judge.LLMJudge._call_llm')
    async def test_evaluate_failure(self, mock_call_llm, judge):
        """Test evaluation that fails threshold."""
        mock_response = {
            "score": 0.4,
            "pass": False,
            "feedback": "Incorrect answer with multiple issues.",
            "scores": {criterion: 0.4 for criterion in judge.rubric},
        }
        mock_call_llm.return_value = json.dumps(mock_response)
        
        result = await judge.evaluate(
            "London is the capital of France.",
            "The capital of France is Paris."
        )
        
        assert result.score == 0.4
        assert result.passed is False
        assert "Incorrect" in result.feedback
    
    @pytest.mark.asyncio
    @patch('acp_evals.evaluators.llm_judge.LLMJudge._call_llm')
    async def test_malformed_llm_response(self, mock_call_llm, judge):
        """Test handling of malformed LLM responses."""
        # Non-JSON response
        mock_call_llm.return_value = "This is not JSON"
        
        result = await judge.evaluate("output", "reference")
        
        assert result.score == 0.0
        assert result.passed is False
        assert "Failed to parse" in result.feedback
        assert result.details["error"] is not None
    
    @pytest.mark.asyncio
    @patch('acp_evals.evaluators.llm_judge.LLMJudge._call_llm')
    async def test_missing_score_fields(self, mock_call_llm, judge):
        """Test handling of incomplete LLM responses."""
        # Response missing required fields
        mock_response = {
            "feedback": "Some feedback",
            # Missing score and pass fields
        }
        mock_call_llm.return_value = json.dumps(mock_response)
        
        result = await judge.evaluate("output", "reference")
        
        assert result.score == 0.0
        assert result.passed is False
        assert "Missing required fields" in result.feedback
    
    @pytest.mark.asyncio
    async def test_rubric_validation(self):
        """Test rubric weight validation."""
        # Invalid weights (don't sum to 1.0)
        invalid_rubric = {
            "criterion1": {"weight": 0.5, "criteria": "Test"},
            "criterion2": {"weight": 0.3, "criteria": "Test"},
        }
        
        with pytest.raises(ValueError, match="Rubric weights must sum to 1.0"):
            LLMJudge(rubric=invalid_rubric)
    
    @pytest.mark.asyncio
    @patch('acp_evals.evaluators.llm_judge.LLMJudge._call_llm')
    async def test_score_calculation(self, mock_call_llm, judge):
        """Test weighted score calculation."""
        mock_response = {
            "score": 0.0,  # Will be recalculated
            "pass": True,
            "feedback": "Test",
            "scores": {
                "factual_accuracy": 1.0,    # weight: 0.3
                "completeness": 0.8,         # weight: 0.25
                "clarity": 0.6,              # weight: 0.2
                "relevance": 0.4,            # weight: 0.15
                "efficiency": 0.2,           # weight: 0.1
            },
        }
        mock_call_llm.return_value = json.dumps(mock_response)
        
        result = await judge.evaluate("output", "reference")
        
        # Calculate expected score
        expected = (
            1.0 * 0.3 +   # factual_accuracy
            0.8 * 0.25 +  # completeness
            0.6 * 0.2 +   # clarity
            0.4 * 0.15 +  # relevance
            0.2 * 0.1     # efficiency
        )
        assert result.score == pytest.approx(expected, rel=0.01)
    
    @pytest.mark.asyncio
    async def test_api_client_configuration(self):
        """Test different API client configurations."""
        # Test with API key
        judge = LLMJudge(api_key="test-key", api_base="https://custom.api")
        assert judge.api_key == "test-key"
        assert judge.api_base == "https://custom.api"
        
        # Test with environment variable fallback
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'}):
            judge = LLMJudge()
            assert judge.api_key == "env-key"
    
    @pytest.mark.asyncio
    @patch('acp_evals.evaluators.llm_judge.LLMJudge._call_llm')
    async def test_batch_evaluation(self, mock_call_llm):
        """Test batch evaluation of multiple outputs."""
        judge = LLMJudge()
        
        outputs = [
            ("Paris", "Paris"),
            ("London", "Paris"),
            ("The capital is Paris", "Paris"),
        ]
        
        # Mock different responses
        mock_responses = [
            {"score": 1.0, "pass": True, "feedback": "Perfect", "scores": {}},
            {"score": 0.0, "pass": False, "feedback": "Wrong", "scores": {}},
            {"score": 0.9, "pass": True, "feedback": "Good", "scores": {}},
        ]
        
        mock_call_llm.side_effect = [json.dumps(r) for r in mock_responses]
        
        results = await judge.batch_evaluate(outputs)
        
        assert len(results) == 3
        assert results[0].score == 1.0
        assert results[1].score == 0.0
        assert results[2].score == 0.9
    
    @pytest.mark.asyncio
    async def test_custom_model_parameters(self):
        """Test custom model parameters."""
        judge = LLMJudge(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=1000,
            top_p=0.9,
        )
        
        assert judge.model == "gpt-3.5-turbo"
        assert judge.temperature == 0.5
        assert judge.max_tokens == 1000
        assert judge.top_p == 0.9