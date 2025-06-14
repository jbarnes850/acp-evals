"""
Tests for HandoffQualityMetric - focusing on core functionality.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from acp_evals.metrics.handoff_quality import HandoffQualityMetric
from acp_evals.core.base import MetricResult


class TestHandoffQualityMetric:
    """Test suite for HandoffQualityMetric - core functionality only."""
    
    @pytest.fixture
    def metric(self):
        """Create a HandoffQualityMetric instance."""
        return HandoffQualityMetric()
    
    @pytest.fixture
    def handoff_events(self):
        """Create simple mock events simulating agent handoffs."""
        events = []
        
        # Message from agent-1
        msg1 = Mock()
        msg1.parts = [Mock(content="Budget: $50,000, Deadline: March 15")]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Handoff to agent-2
        msg2 = Mock()
        msg2.parts = [Mock(content="Budget is $50,000, Due March 15")]
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        return events
    
    @pytest.mark.asyncio
    async def test_basic_handoff_detection(self, metric, handoff_events):
        """Test detection of handoffs between agents."""
        run = Mock()
        result = await metric.calculate(run, handoff_events)
        
        assert isinstance(result, MetricResult)
        assert result.name == "handoff_quality"
        assert result.breakdown["handoff_count"] == 1  # One handoff
    
    @pytest.mark.asyncio
    async def test_no_handoffs_single_agent(self, metric):
        """Test metric with no handoffs (single agent)."""
        events = []
        
        # All messages from same agent
        for i in range(3):
            msg = Mock()
            msg.parts = [Mock(content=f"Message {i}")]
            
            event = Mock()
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.agent_id = "agent-1"
            event.message = msg
            events.append(event)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        assert result.value == 1.0  # No handoffs = perfect score
        assert result.breakdown["handoff_count"] == 0
    
    @pytest.mark.asyncio
    async def test_information_preservation(self, metric):
        """Test measurement of information preservation across handoffs."""
        events = []
        
        # Agent 1 provides information
        msg1 = Mock()
        msg1.parts = [Mock(content="Budget: $50,000, Deadline: March 15, Use PostgreSQL")]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Agent 2 loses some information
        msg2 = Mock()
        msg2.parts = [Mock(content="Budget: $50,000, Deadline: March")]
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should show information loss
        assert result.value < 1.0
        assert result.breakdown["average_preservation"] < 1.0
    
    @pytest.mark.asyncio
    async def test_empty_events(self, metric):
        """Test handling of empty event list."""
        run = Mock()
        result = await metric.calculate(run, [])
        
        assert result.value == 1.0  # No handoffs
        assert result.breakdown["handoff_count"] == 0