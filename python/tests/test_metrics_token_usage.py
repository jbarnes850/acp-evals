"""
Tests for TokenUsageMetric implementation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from acp_evals.metrics.token_usage import TokenUsageMetric
from acp_evals.base import MetricResult


class TestTokenUsageMetric:
    """Test suite for TokenUsageMetric."""
    
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
        assert result.unit == "tokens"
        assert result.value > 0  # Total tokens
        
        # Check breakdown structure
        assert "input_tokens" in result.breakdown
        assert "output_tokens" in result.breakdown
        assert "total_cost" in result.breakdown
        assert "by_agent" in result.breakdown
        assert "by_event_type" in result.breakdown
        
        # Verify token counts from mock events
        # 3 message events with increasing tokens
        expected_input = 100 + 110 + 120  # 330
        expected_output = 50 + 55 + 60  # 165
        expected_tool = 20 + 80  # 100 from tool event
        
        assert result.breakdown["input_tokens"] == expected_input + expected_tool
        assert result.breakdown["output_tokens"] == expected_output
    
    @pytest.mark.asyncio
    async def test_token_calculation_with_custom_pricing(self):
        """Test token calculation with custom pricing models."""
        custom_pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5": {"input": 0.001, "output": 0.002},
        }
        
        metric = TokenUsageMetric(pricing_per_1k=custom_pricing)
        
        # Create events with model info
        events = []
        for model, tokens in [("gpt-4.1", 1000), ("claude-4-opus", 2000)]:
            event = Mock()
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.data = {
                "tokens": {"input": tokens, "output": tokens // 2},
                "model": model,
            }
            events.append(event)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Verify cost calculation
        # GPT-4.1: 1000 input * 0.03 + 500 output * 0.06 = 30 + 30 = 60
        # Claude-4-Opus: 2000 input * 0.001 + 1000 output * 0.002 = 2 + 2 = 4
        # Total: 64 / 1000 = 0.064
        assert result.breakdown["total_cost"] == pytest.approx(0.064, rel=0.01)
    
    @pytest.mark.asyncio
    async def test_token_calculation_by_agent(self, metric):
        """Test token breakdown by agent."""
        events = []
        
        # Agent 1 events
        for i in range(3):
            event = Mock()
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.agent_id = "agent-1"
            event.data = {"tokens": {"input": 100, "output": 50}}
            events.append(event)
        
        # Agent 2 events
        for i in range(2):
            event = Mock()
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.agent_id = "agent-2"
            event.data = {"tokens": {"input": 200, "output": 100}}
            events.append(event)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        assert "agent-1" in result.breakdown["by_agent"]
        assert "agent-2" in result.breakdown["by_agent"]
        
        # Agent 1: 3 * (100 + 50) = 450
        assert result.breakdown["by_agent"]["agent-1"]["total"] == 450
        # Agent 2: 2 * (200 + 100) = 600
        assert result.breakdown["by_agent"]["agent-2"]["total"] == 600
    
    @pytest.mark.asyncio
    async def test_token_calculation_by_event_type(self, metric):
        """Test token breakdown by event type."""
        events = []
        
        # Message events
        for i in range(2):
            event = Mock()
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.data = {"tokens": {"input": 100, "output": 50}}
            events.append(event)
        
        # Tool events
        for i in range(3):
            event = Mock()
            event.type = "tool.called"
            event.timestamp = datetime.now()
            event.data = {"tokens": {"input": 50, "output": 25}}
            events.append(event)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        assert "message.created" in result.breakdown["by_event_type"]
        assert "tool.called" in result.breakdown["by_event_type"]
        
        # Messages: 2 * (100 + 50) = 300
        assert result.breakdown["by_event_type"]["message.created"]["total"] == 300
        # Tools: 3 * (50 + 25) = 225
        assert result.breakdown["by_event_type"]["tool.called"]["total"] == 225
    
    @pytest.mark.asyncio
    async def test_empty_events(self, metric):
        """Test handling of empty event list."""
        run = Mock()
        result = await metric.calculate(run, [])
        
        assert result.value == 0
        assert result.breakdown["input_tokens"] == 0
        assert result.breakdown["output_tokens"] == 0
        assert result.breakdown["total_cost"] == 0.0
    
    @pytest.mark.asyncio
    async def test_missing_token_data(self, metric):
        """Test handling of events without token data."""
        events = []
        
        # Event with tokens
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.data = {"tokens": {"input": 100, "output": 50}}
        events.append(event1)
        
        # Event without tokens
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.data = {}  # No token data
        events.append(event2)
        
        # Event with partial token data
        event3 = Mock()
        event3.type = "message.created"
        event3.timestamp = datetime.now()
        event3.data = {"tokens": {"input": 50}}  # Missing output
        events.append(event3)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should only count event1 fully and event3 input
        assert result.breakdown["input_tokens"] == 150  # 100 + 50
        assert result.breakdown["output_tokens"] == 50   # Only from event1
    
    @patch('tiktoken.encoding_for_model')
    @pytest.mark.asyncio
    async def test_count_message_tokens(self, mock_encoding):
        """Test token counting for message content."""
        metric = TokenUsageMetric()
        
        # Mock tiktoken encoder
        mock_encoder = Mock()
        mock_encoder.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_encoding.return_value = mock_encoder
        
        # Test message with content
        message = Mock()
        message.parts = [Mock(content="Hello world")]
        
        event = Mock()
        event.type = "message.created"
        event.timestamp = datetime.now()
        event.message = message
        event.data = {}  # No pre-calculated tokens
        
        run = Mock()
        result = await metric.calculate(run, [event])
        
        # Should use tiktoken to count
        mock_encoder.encode.assert_called_once()
        assert result.value > 0
    
    @pytest.mark.asyncio
    async def test_efficiency_score_calculation(self, metric):
        """Test efficiency score calculation."""
        events = []
        
        # Efficient agent (low tokens, completes task)
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "efficient-agent"
        event1.data = {"tokens": {"input": 50, "output": 25}}
        events.append(event1)
        
        # Inefficient agent (high tokens for same task)
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "inefficient-agent"
        event2.data = {"tokens": {"input": 200, "output": 150}}
        events.append(event2)
        
        run = Mock()
        run.metadata = {"task_completed": True}
        result = await metric.calculate(run, events)
        
        # Check efficiency scores
        assert "efficiency_score" in result.breakdown
        assert result.breakdown["efficiency_score"] > 0
        
        # Efficient agent should have better per-token score
        agent_scores = result.breakdown["by_agent"]
        assert agent_scores["efficient-agent"]["total"] < agent_scores["inefficient-agent"]["total"]
    
    @pytest.mark.asyncio 
    async def test_context_window_tracking(self, metric):
        """Test context window usage tracking."""
        metric = TokenUsageMetric(track_context_usage=True)
        
        events = []
        
        # Event with context window info
        event = Mock()
        event.type = "message.created"
        event.timestamp = datetime.now()
        event.data = {
            "tokens": {"input": 3000, "output": 500},
            "context_window": 4096,
        }
        events.append(event)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should track context usage
        assert "context_usage" in result.breakdown
        assert result.breakdown["context_usage"]["percentage"] == pytest.approx(85.4, rel=0.1)
        assert result.breakdown["context_usage"]["tokens_used"] == 3500
        assert result.breakdown["context_usage"]["window_size"] == 4096
    
    @pytest.mark.asyncio
    async def test_metadata_included(self, metric):
        """Test that metadata is properly included."""
        run = Mock()
        run.id = "test-run"
        result = await metric.calculate(run, [])
        
        assert result.metadata["run_id"] == "test-run"
        assert "timestamp" in result.metadata
        assert "metric_version" in result.metadata