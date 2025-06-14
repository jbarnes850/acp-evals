"""
Tests for HandoffQualityMetric implementation.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from acp_evals.metrics.handoff_quality import HandoffQualityMetric
from acp_evals.base import MetricResult


class TestHandoffQualityMetric:
    """Test suite for HandoffQualityMetric."""
    
    @pytest.fixture
    def metric(self):
        """Create a HandoffQualityMetric instance."""
        return HandoffQualityMetric()
    
    @pytest.fixture
    def handoff_events(self):
        """Create mock events simulating agent handoffs."""
        events = []
        
        # Initial message from agent-1
        msg1 = Mock()
        msg1.parts = [Mock(content="""
        Project requirements:
        - Budget: $50,000
        - Deadline: March 15, 2025
        - Must include user authentication
        - Use PostgreSQL for database
        """)]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Handoff to agent-2 (preserves most info)
        msg2 = Mock()
        msg2.parts = [Mock(content="""
        Based on the requirements:
        - Budget is $50,000
        - Due by March 15, 2025
        - Need user authentication system
        - Database: PostgreSQL
        - Adding: implement microservices
        """)]
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        # Handoff to agent-3 (loses some info)
        msg3 = Mock()
        msg3.parts = [Mock(content="""
        Working on project with:
        - Budget constraint
        - March deadline
        - Auth system needed
        - Using microservices architecture
        """)]
        
        event3 = Mock()
        event3.type = "message.created"
        event3.timestamp = datetime.now()
        event3.agent_id = "agent-3"
        event3.message = msg3
        events.append(event3)
        
        return events
    
    @pytest.mark.asyncio
    async def test_basic_handoff_detection(self, metric, handoff_events):
        """Test detection of handoffs between agents."""
        run = Mock()
        result = await metric.calculate(run, handoff_events)
        
        assert isinstance(result, MetricResult)
        assert result.name == "handoff_quality"
        assert result.breakdown["handoff_count"] == 2  # agent-1 to 2, agent-2 to 3
    
    @pytest.mark.asyncio
    async def test_no_handoffs(self, metric):
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
        
        assert result.value == 1.0  # No handoffs = no loss
        assert result.breakdown["handoff_count"] == 0
    
    @pytest.mark.asyncio
    async def test_information_preservation_score(self, metric):
        """Test calculation of information preservation."""
        events = []
        
        # Perfect preservation
        msg1 = Mock()
        msg1.parts = [Mock(content="Budget: $50,000, Deadline: March 15")]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Agent 2 preserves all info
        msg2 = Mock()
        msg2.parts = [Mock(content="Confirmed - Budget: $50,000, Deadline: March 15")]
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        assert result.breakdown["average_preservation"] > 0.8  # High preservation
    
    @pytest.mark.asyncio
    async def test_constraint_tracking(self, metric):
        """Test tracking of constraint preservation."""
        metric = HandoffQualityMetric(
            track_constraints=True,
            track_decisions=False,
            track_entities=False
        )
        
        events = []
        
        # Message with constraints
        msg1 = Mock()
        msg1.parts = [Mock(content="""
        Budget: $100,000
        Deadline: June 2025
        Must have SSL encryption
        Require 99.9% uptime
        """)]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Agent 2 loses some constraints
        msg2 = Mock()
        msg2.parts = [Mock(content="""
        Budget: $100,000
        Due in June
        Need encryption
        """)]
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should detect constraint loss
        assert result.breakdown["average_preservation"] < 1.0
    
    @pytest.mark.asyncio
    async def test_decision_preservation(self, metric):
        """Test tracking of decision preservation."""
        metric = HandoffQualityMetric(
            track_constraints=False,
            track_decisions=True,
            track_entities=False
        )
        
        events = []
        
        # Message with decisions
        msg1 = Mock()
        msg1.parts = [Mock(content="""
        Decided to:
        - Use PostgreSQL for the database
        - Implement microservices architecture
        - Choose AWS for deployment
        - Select React for frontend
        """)]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Agent 2 changes some decisions
        msg2 = Mock()
        msg2.parts = [Mock(content="""
        Plan update:
        - Use MySQL instead (better performance)
        - Keep microservices architecture
        - Choose AWS for deployment
        - Select Vue.js for frontend
        """)]
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should detect decision conflicts
        assert result.breakdown["decision_conflicts"] > 0
    
    @pytest.mark.asyncio
    async def test_entity_preservation(self, metric):
        """Test tracking of entity/name preservation."""
        metric = HandoffQualityMetric(
            track_constraints=False,
            track_decisions=False,
            track_entities=True
        )
        
        events = []
        
        # Message with entities
        msg1 = Mock()
        msg1.parts = [Mock(content="""
        Team members: Alice Johnson, Bob Smith, Charlie Davis
        Using services: AuthService, PaymentGateway, NotificationHub
        Clients: Acme Corp, TechStart Inc
        """)]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Agent 2 loses some entities
        msg2 = Mock()
        msg2.parts = [Mock(content="""
        Team has Alice and Bob working on this.
        Main services: AuthService and PaymentGateway
        Client: Acme Corp
        """)]
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should detect entity loss (Charlie Davis, NotificationHub, TechStart Inc)
        assert result.breakdown["average_preservation"] < 0.7
    
    @pytest.mark.asyncio
    async def test_noise_accumulation(self, metric):
        """Test detection of noise accumulation."""
        events = []
        
        # Short initial message
        msg1 = Mock()
        msg1.parts = [Mock(content="Build a web app with user auth")]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Agent 2 adds lots of unnecessary detail
        msg2 = Mock()
        msg2.parts = [Mock(content="""
        Build a web app with user auth. This is a very important project that requires
        careful consideration of many factors. We need to think about scalability,
        performance, security, usability, and many other aspects. The authentication
        system should be robust and handle various edge cases. We should also consider
        the user experience and make sure the interface is intuitive. Additionally,
        we need to plan for future expansion and ensure our architecture is flexible.
        """ * 3)]  # Repeat to make it very long
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should detect noise accumulation
        assert result.breakdown["noise_added_bytes"] > 0
    
    @pytest.mark.asyncio
    async def test_degradation_factor(self, metric):
        """Test exponential degradation factor calculation."""
        events = []
        
        # Create a chain with degrading quality
        contents = [
            "Requirements: A=$1000, B=2025, C=auth, D=postgres, E=react",
            "Project needs: A=$1000, B=2025, C=auth, D=postgres",  # Lost E
            "Working on: A=$1000, B=2025, C=auth",  # Lost D
            "Task: A=$1000, B=2025",  # Lost C
        ]
        
        for i, content in enumerate(contents):
            msg = Mock()
            msg.parts = [Mock(content=content)]
            
            event = Mock()
            event.type = "message.created"
            event.timestamp = datetime.now()
            event.agent_id = f"agent-{i}"
            event.message = msg
            events.append(event)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should calculate degradation factor
        assert result.breakdown["degradation_factor"] > 0
        assert result.breakdown["final_preservation"] < result.breakdown["average_preservation"]
    
    @pytest.mark.asyncio
    async def test_complex_handoff_chain(self, metric, handoff_events):
        """Test analysis of complex handoff chain."""
        run = Mock()
        result = await metric.calculate(run, handoff_events)
        
        # Check detailed breakdown
        assert "preservation_by_handoff" in result.breakdown
        assert len(result.breakdown["preservation_by_handoff"]) == 2
        
        # First handoff should have better preservation than second
        scores = result.breakdown["preservation_by_handoff"]
        assert scores[0] > scores[1]  # Quality degrades
    
    @pytest.mark.asyncio
    async def test_empty_message_handling(self, metric):
        """Test handling of empty messages."""
        events = []
        
        # Normal message
        msg1 = Mock()
        msg1.parts = [Mock(content="Important information")]
        
        event1 = Mock()
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Empty message
        msg2 = Mock()
        msg2.parts = []
        
        event2 = Mock()
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        run = Mock()
        result = await metric.calculate(run, events)
        
        # Should handle gracefully
        assert result.value == 0.0  # Complete information loss
    
    @pytest.mark.asyncio
    async def test_metadata_included(self, metric):
        """Test that metadata is properly included."""
        run = Mock()
        run.id = "test-run"
        
        result = await metric.calculate(run, [])
        
        assert result.metadata["message"] == "No handoffs detected"
        assert result.metadata["track_settings"]["decisions"] is True
        assert result.metadata["track_settings"]["constraints"] is True
        assert result.metadata["track_settings"]["entities"] is True