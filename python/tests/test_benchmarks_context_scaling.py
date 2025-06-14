"""
Tests for ContextScalingBenchmark - focusing on core functionality.
"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from acp_evals.benchmarks.context_scaling import ContextScalingBenchmark
from acp_evals.core.base import BenchmarkResult, BenchmarkTask


class TestContextScalingBenchmark:
    """Test suite for ContextScalingBenchmark - core functionality only."""
    
    @pytest.fixture
    def benchmark(self):
        """Create a simple ContextScalingBenchmark instance."""
        return ContextScalingBenchmark(
            distractor_levels=[0, 5, 10],  # Small set for testing
        )
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent that returns simple responses."""
        agent = AsyncMock()
        
        async def mock_execute(prompt, **kwargs):
            # Simple responses based on known prompts
            if "capital of France" in prompt:
                return "The capital of France is Paris."
            else:
                return "I don't know."
        
        agent.execute = mock_execute
        agent.run = mock_execute  # Support run method
        return agent
    
    @pytest.mark.asyncio
    async def test_benchmark_basic_run(self, benchmark, mock_agent):
        """Test basic benchmark execution."""
        result = await benchmark.evaluate(mock_agent)
        
        assert isinstance(result, BenchmarkResult)
        assert result.benchmark_name == "context_scaling"
        assert result.tasks_total > 0
        assert 0 <= result.overall_score <= 1
    
    @pytest.mark.asyncio
    async def test_distractor_generation(self, benchmark):
        """Test that distractors are generated correctly."""
        distractors = benchmark._generate_distractors(5)
        
        assert len(distractors) == 5
        assert all(isinstance(d, str) for d in distractors)
        assert all(len(d) > 10 for d in distractors)
    
    @pytest.mark.asyncio
    async def test_performance_degradation(self, benchmark):
        """Test that benchmark measures performance degradation."""
        # Mock agent that degrades with more context
        agent = AsyncMock()
        call_count = 0
        
        async def degrading_execute(prompt, **kwargs):
            nonlocal call_count
            call_count += 1
            # Degrade performance based on prompt length (proxy for distractors)
            if len(prompt) < 100:
                return "The capital of France is Paris."
            else:
                return "I'm not sure due to too much context."
        
        agent.execute = degrading_execute
        result = await benchmark.evaluate(agent)
        
        # Check that degradation metrics exist
        assert "total_degradation" in result.summary
        assert "optimal_distractor_level" in result.summary
    
    @pytest.mark.asyncio
    async def test_error_handling(self, benchmark):
        """Test graceful error handling."""
        # Agent that always errors
        error_agent = AsyncMock()
        error_agent.execute.side_effect = Exception("Agent error")
        error_agent.run.side_effect = Exception("Agent error")
        
        result = await benchmark.evaluate(error_agent)
        
        # Benchmark should handle errors gracefully
        assert result.tasks_total > 0
        assert result.overall_score < 0.5  # Low score due to errors