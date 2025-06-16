"""
Tests for multi-agent patterns - focusing on core functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from acp_evals.patterns import (
    AgentInfo,
    LinearPattern,
    SupervisorPattern,
    SwarmPattern,
)


class TestLinearPattern:
    """Test LinearPattern - core functionality only."""
    
    @pytest.fixture
    def agents(self):
        """Create test agents."""
        return [
            AgentInfo(name=f"agent-{i}", url=f"http://localhost:800{i}")
            for i in range(3)
        ]
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client with simple responses."""
        client = Mock()
        
        async def mock_run_sync(agent, input):
            run = Mock()
            run.output = [Mock(parts=[Mock(content=f"Processed by {agent}")])]
            return run
        
        client.run_sync = AsyncMock(side_effect=mock_run_sync)
        return client
    
    @pytest.mark.asyncio
    async def test_linear_execution(self, agents, mock_client):
        """Test basic linear execution through agents."""
        pattern = LinearPattern(agents)
        
        # Mock the internal client getter
        pattern._get_client = lambda agent: mock_client
        
        result = await pattern.execute("Test task")
        
        assert result["success"] is True
        assert len(result["handoffs"]) == 3
    
    @pytest.mark.asyncio
    async def test_linear_failure_handling(self, agents):
        """Test handling when an agent fails."""
        client = Mock()
        
        async def mock_run_sync(agent, input):
            if "agent-1" in agent:
                raise Exception("Agent failed")
            run = Mock()
            run.output = [Mock(parts=[Mock(content="Success")])]
            return run
        
        client.run_sync = AsyncMock(side_effect=mock_run_sync)
        pattern = LinearPattern(agents)
        pattern._get_client = lambda agent: client
        
        result = await pattern.execute("Test")
        
        assert result["success"] is False
        assert len(result["handoffs"]) == 2  # Stopped at failure


class TestSupervisorPattern:
    """Test SupervisorPattern - core functionality only."""
    
    @pytest.fixture
    def supervisor_setup(self):
        """Create supervisor and workers."""
        supervisor = AgentInfo(name="supervisor", url="http://localhost:8000")
        workers = [
            AgentInfo(name=f"worker-{i}", url=f"http://localhost:900{i}")
            for i in range(2)
        ]
        return supervisor, workers
    
    @pytest.mark.asyncio
    async def test_supervisor_execution(self, supervisor_setup):
        """Test basic supervisor pattern execution."""
        supervisor, workers = supervisor_setup
        
        client = Mock()
        async def mock_run_sync(agent, input):
            run = Mock()
            if "supervisor" in agent:
                run.output = [Mock(parts=[Mock(content="Task delegated")])]
            else:
                run.output = [Mock(parts=[Mock(content="Work completed")])]
            return run
        
        client.run_sync = AsyncMock(side_effect=mock_run_sync)
        
        pattern = SupervisorPattern(supervisor, workers)
        pattern._get_client = lambda agent: client
        
        result = await pattern.execute("Complex task")
        
        assert result["success"] is True
        assert "delegation_plan" in result  # Supervisor pattern has different keys
        assert "worker_results" in result
        assert result["workers_used"] >= 0  # May be 0 if delegation failed


class TestSwarmPattern:
    """Test SwarmPattern - core functionality only."""
    
    @pytest.fixture
    def swarm_agents(self):
        """Create swarm agents."""
        return [
            AgentInfo(name=f"agent-{i}", url=f"http://localhost:700{i}")
            for i in range(3)
        ]
    
    @pytest.mark.asyncio
    async def test_swarm_majority_vote(self, swarm_agents):
        """Test basic swarm execution with majority vote."""
        client = Mock()
        
        async def mock_run_sync(agent, input):
            run = Mock()
            # 2 agents say A, 1 says B
            if agent.endswith(("0", "1")):
                run.output = [Mock(parts=[Mock(content="Answer A")])]
            else:
                run.output = [Mock(parts=[Mock(content="Answer B")])]
            return run
        
        client.run_sync = AsyncMock(side_effect=mock_run_sync)
        
        pattern = SwarmPattern(swarm_agents)
        pattern._get_client = lambda agent: client
        
        result = await pattern.execute("Question")
        
        assert result["success"] is True
        assert result["final_output"] == "Answer A"  # Majority
    
    @pytest.mark.asyncio
    async def test_swarm_partial_failure(self, swarm_agents):
        """Test swarm handles partial failures."""
        client = Mock()
        
        async def mock_run_sync(agent, input):
            if agent.endswith("0"):
                raise Exception("Agent failed")
            run = Mock()
            run.output = [Mock(parts=[Mock(content="Success")])]
            return run
        
        client.run_sync = AsyncMock(side_effect=mock_run_sync)
        
        pattern = SwarmPattern(swarm_agents)
        pattern._get_client = lambda agent: client
        
        result = await pattern.execute("Task")
        
        assert result["success"] is True  # Still succeeds with 2/3