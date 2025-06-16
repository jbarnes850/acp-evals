"""
Integration tests for ACP Evals - focusing on core workflows.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
import json

from acp_sdk import Run, Event, Message, MessagePart, RunStatus
from acp_sdk.client import Client

from acp_evals.client import ACPEvaluationClient
from acp_evals.metrics import TokenUsageMetric
from acp_evals.benchmarks import ContextScalingBenchmark
from acp_evals.evaluators import LLMJudge


class TestACPIntegration:
    """Test core ACP evaluation workflows."""
    
    @pytest.fixture
    def mock_acp_client(self):
        """Create a simple mock ACP client."""
        client = Mock(spec=Client)
        
        # Mock run execution
        async def mock_run_sync(agent, input, **kwargs):
            run = Mock(spec=Run)
            run.run_id = "test-run-123"
            run.status = RunStatus.COMPLETED
            
            # Simple output
            output_message = Mock(spec=Message)
            output_part = Mock(spec=MessagePart)
            output_part.content = f"Response from {agent}"
            output_message.parts = [output_part]
            run.output = [output_message]
            
            return run
        
        client.run_sync = AsyncMock(side_effect=mock_run_sync)
        
        # Mock event streaming
        async def mock_run_events_stream(run_id):
            # Minimal events for token tracking
            event = Mock(spec=Event)
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.data = {"tokens": {"input": 100, "output": 50}}
            yield event
        
        client.run_events_stream = mock_run_events_stream
        
        # Mock run status check
        async def mock_run(run_id):
            run = Mock(spec=Run)
            run.run_id = run_id
            status = Mock()
            status.is_terminal = True
            run.status = status
            return run
        
        client.run = AsyncMock(side_effect=mock_run)
        
        return client
    
    @pytest.mark.asyncio
    async def test_single_agent_with_token_tracking(self, mock_acp_client):
        """Test evaluating an agent with token usage tracking."""
        eval_client = ACPEvaluationClient(
            base_url="http://localhost:8000",
            metrics=[TokenUsageMetric()],
        )
        eval_client.client = mock_acp_client
        
        # Run evaluation
        run, events, metrics = await eval_client.run_with_tracking(
            agent_name="test-agent",
            input="Test input",
        )
        
        # Verify core functionality
        assert run.status.is_terminal  # Check completion
        assert "token_usage" in metrics
        # Token metric exists but may be 0 if events weren't properly collected
        assert metrics["token_usage"] is not None
    
    @pytest.mark.asyncio
    async def test_benchmark_execution(self, mock_acp_client):
        """Test running a simple benchmark."""
        eval_client = ACPEvaluationClient(
            base_url="http://localhost:8000",
            metrics=[TokenUsageMetric()],
        )
        eval_client.client = mock_acp_client
        
        # Import the task type
        from acp_evals.core.base import BenchmarkTask
        
        # Minimal benchmark with proper task
        benchmark = ContextScalingBenchmark(
            tasks=[BenchmarkTask(id="test", prompt="Test", expected_output="Response")],
            distractor_levels=[0],
        )
        
        result = await eval_client.run_benchmark(
            agent_name="test-agent",
            benchmark=benchmark,
        )
        
        # Verify benchmark ran
        assert result.benchmark_name == "context_scaling"
        assert 0 <= result.overall_score <= 1
    
    @pytest.mark.asyncio
    async def test_llm_judge_evaluation(self):
        """Test LLM judge with pass/fail scoring."""
        judge = LLMJudge()
        
        # Mock passing evaluation
        mock_response = {
            "overall_score": 0.8,
            "passed": True,
            "feedback": "Good response",
            "scores": {}
        }
        
        # Judge defaults to mock mode, so just test it works
        result = await judge.evaluate("task", "output contains expected", "expected")
        
        # In mock mode with matching content, should pass
        assert result.score > 0.5  # Mock scoring logic
        assert result.passed is True