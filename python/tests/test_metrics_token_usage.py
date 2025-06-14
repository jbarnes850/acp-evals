"""
Tests for TokenUsageMetric - focusing on core functionality.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from acp_evals.metrics.token_usage import TokenUsageMetric
from acp_evals.core.base import MetricResult


class TestTokenUsageMetric:
    """Test suite for TokenUsageMetric - core functionality only."""
    
    @pytest.fixture
    def metric(self):
        """Create a TokenUsageMetric instance."""
        return TokenUsageMetric()
    
    @pytest.mark.asyncio
    async def test_basic_token_calculation(self, metric, mock_run, mock_events):
        """Test basic token calculation from events."""
        result = await metric.calculate(mock_run, mock_events)
        
        assert isinstance(result, MetricResult)
        assert result.name == "token_usage"
        assert result.value > 0  # Total tokens
        
        # Check essential breakdown fields
        assert "input_tokens" in result.breakdown
        assert "output_tokens" in result.breakdown
        assert "cost_usd" in result.breakdown
        assert result.breakdown["cost_usd"] > 0
    
    @pytest.mark.asyncio
    async def test_cost_calculation(self):
        """Test cost calculation with model pricing."""
        metric = TokenUsageMetric(model="gpt-4.1")
        
        # Create simple event with tokens
        event = Mock()
        event.type = "message.created"
        event.timestamp = datetime.now()
        event.data = {"tokens": {"input": 1000, "output": 500}}
        event.message = Mock(role="assistant")
        
        run = Mock(run_id="test-run-123")
        result = await metric.calculate(run, [event])
        
        # Verify cost is calculated
        assert result.breakdown["cost_usd"] > 0
        assert result.value == 1500  # Total tokens
    
    @pytest.mark.asyncio
    async def test_multi_agent_tracking(self, metric):
        """Test token tracking for multiple agents."""
        events = []
        
        # Create events for two agents
        for agent_id in ["agent-1", "agent-2"]:
            event = Mock()
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.agent_id = agent_id
            event.data = {"tokens": {"input": 100, "output": 50}}
            event.message = Mock(role="assistant")
            events.append(event)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Verify both agents are tracked
        assert "agent_breakdown" in result.breakdown
        assert "agent-1" in result.breakdown["agent_breakdown"]
        assert "agent-2" in result.breakdown["agent_breakdown"]
    
    @pytest.mark.asyncio
    async def test_empty_events(self, metric):
        """Test handling of empty event list."""
        run = Mock()
        result = await metric.calculate(run, [])
        
        assert result.value == 0
        assert result.breakdown["cost_usd"] == 0.0
    
    @pytest.mark.asyncio 
    async def test_context_percentage(self, metric):
        """Test context window usage tracking."""
        event = Mock()
        event.type = "message.created"
        event.timestamp = datetime.now()
        event.data = {
            "tokens": {"input": 3000, "output": 500},
            "context_window": 4096,
        }
        event.message = Mock(role="assistant")
        
        run = Mock()
        result = await metric.calculate(run, [event])
        
        # Verify context usage is tracked
        assert "context_percentage" in result.breakdown
        assert 0 <= result.breakdown["context_percentage"] <= 100