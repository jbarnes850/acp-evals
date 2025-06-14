"""
Tests for multi-agent pattern implementations.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import asyncio

from acp_evals.patterns import (
    AgentInfo,
    LinearPattern,
    SupervisorPattern,
    SwarmPattern,
)


class TestAgentInfo:
    """Test AgentInfo data class."""
    
    def test_agent_info_creation(self):
        """Test creating AgentInfo instances."""
        agent = AgentInfo(
            name="test-agent",
            url="http://localhost:8000",
            role="Test agent",
            capabilities=["text", "tools"],
        )
        
        assert agent.name == "test-agent"
        assert agent.url == "http://localhost:8000"
        assert agent.role == "Test agent"
        assert agent.capabilities == ["text", "tools"]
    
    def test_agent_info_defaults(self):
        """Test AgentInfo with minimal parameters."""
        agent = AgentInfo(
            name="minimal",
            url="http://example.com"
        )
        
        assert agent.role is None
        assert agent.capabilities is None


class TestLinearPattern:
    """Test LinearPattern implementation."""
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        agents = []
        for i in range(3):
            agent = AgentInfo(
                name=f"agent-{i}",
                url=f"http://localhost:800{i}",
                role=f"Agent {i}",
            )
            agents.append(agent)
        return agents
    
    @pytest.fixture
    def mock_client(self):
        """Create mock ACP client."""
        client = AsyncMock()
        
        # Mock different responses for each agent
        async def mock_execute(agent_url, prompt, context=None):
            if "agent-0" in agent_url:
                return {
                    "output": f"Agent 0 processed: {prompt[:50]}...",
                    "success": True,
                    "metadata": {"stage": 1},
                }
            elif "agent-1" in agent_url:
                return {
                    "output": f"Agent 1 enhanced the previous output",
                    "success": True,
                    "metadata": {"stage": 2},
                }
            else:
                return {
                    "output": f"Agent 2 finalized the result",
                    "success": True,
                    "metadata": {"stage": 3},
                }
        
        client.execute_agent = mock_execute
        return client
    
    @pytest.mark.asyncio
    async def test_linear_pattern_initialization(self, mock_agents):
        """Test LinearPattern initialization."""
        pattern = LinearPattern(mock_agents)
        
        assert pattern.name == "linear"
        assert len(pattern.agents) == 3
        assert pattern.preserve_context is True
    
    @pytest.mark.asyncio
    async def test_linear_pattern_execution(self, mock_agents, mock_client):
        """Test linear execution through agents."""
        pattern = LinearPattern(mock_agents, client=mock_client)
        
        result = await pattern.execute(
            "Process this task",
            context={"initial": "data"}
        )
        
        assert result["success"] is True
        assert "final_output" in result
        assert "handoffs" in result
        assert len(result["handoffs"]) == 3
        
        # Verify sequential execution
        assert mock_client.execute_agent.call_count == 3
    
    @pytest.mark.asyncio
    async def test_linear_pattern_context_preservation(self, mock_agents, mock_client):
        """Test context preservation across handoffs."""
        pattern = LinearPattern(mock_agents, preserve_context=True)
        pattern.client = mock_client
        
        initial_context = {"key": "value", "preserve": "this"}
        result = await pattern.execute("Task", context=initial_context)
        
        # Check that context was preserved
        for handoff in result["handoffs"]:
            assert "context" in handoff
            assert handoff["context"]["preserve"] == "this"
    
    @pytest.mark.asyncio
    async def test_linear_pattern_failure_handling(self, mock_agents):
        """Test handling of agent failures."""
        client = AsyncMock()
        
        # Second agent fails
        async def mock_execute(agent_url, prompt, context=None):
            if "agent-1" in agent_url:
                return {"output": "", "success": False, "error": "Agent failed"}
            return {"output": "Success", "success": True}
        
        client.execute_agent = mock_execute
        
        pattern = LinearPattern(mock_agents, client=client)
        result = await pattern.execute("Task")
        
        assert result["success"] is False
        assert "error" in result
        assert len(result["handoffs"]) == 2  # Stopped at failure
    
    @pytest.mark.asyncio
    async def test_linear_pattern_information_preservation(self, mock_agents, mock_client):
        """Test information preservation metric calculation."""
        pattern = LinearPattern(mock_agents, client=mock_client)
        
        result = await pattern.execute("Important: Budget is $50,000")
        
        assert "information_preservation" in result
        assert 0 <= result["information_preservation"] <= 1
        
        # Check handoff quality tracking
        for handoff in result["handoffs"]:
            assert "output_length" in handoff
            assert "latency" in handoff


class TestSupervisorPattern:
    """Test SupervisorPattern implementation."""
    
    @pytest.fixture
    def supervisor_setup(self):
        """Create supervisor and worker agents."""
        supervisor = AgentInfo(
            name="supervisor",
            url="http://localhost:8000",
            role="Supervisor",
            capabilities=["coordination", "planning"],
        )
        
        workers = [
            AgentInfo(
                name=f"worker-{i}",
                url=f"http://localhost:900{i}",
                role=f"Worker {i}",
                capabilities=["task_execution"],
            )
            for i in range(3)
        ]
        
        return supervisor, workers
    
    @pytest.fixture
    def mock_supervisor_client(self):
        """Create mock client for supervisor pattern."""
        client = AsyncMock()
        
        async def mock_execute(agent_url, prompt, context=None):
            if "supervisor" in agent_url:
                # Supervisor delegates tasks
                return {
                    "output": "Task delegated to workers",
                    "success": True,
                    "plan": {
                        "worker-0": "Research the topic",
                        "worker-1": "Analyze the data",
                        "worker-2": "Create summary",
                    },
                }
            elif "worker" in agent_url:
                # Workers execute tasks
                worker_id = agent_url.split("900")[1]
                return {
                    "output": f"Worker {worker_id} completed task",
                    "success": True,
                }
            
            return {"output": "Unknown agent", "success": False}
        
        client.execute_agent = mock_execute
        return client
    
    @pytest.mark.asyncio
    async def test_supervisor_pattern_initialization(self, supervisor_setup):
        """Test SupervisorPattern initialization."""
        supervisor, workers = supervisor_setup
        pattern = SupervisorPattern(supervisor, workers)
        
        assert pattern.name == "supervisor"
        assert pattern.supervisor == supervisor
        assert len(pattern.workers) == 3
        assert pattern.parallel_execution is True
    
    @pytest.mark.asyncio
    async def test_supervisor_pattern_execution(self, supervisor_setup, mock_supervisor_client):
        """Test supervisor pattern execution."""
        supervisor, workers = supervisor_setup
        pattern = SupervisorPattern(supervisor, workers, client=mock_supervisor_client)
        
        result = await pattern.execute("Complex task requiring coordination")
        
        assert result["success"] is True
        assert "supervisor_output" in result
        assert "worker_outputs" in result
        assert len(result["worker_outputs"]) == 3
        
        # Verify supervisor was called first
        first_call = mock_supervisor_client.execute_agent.call_args_list[0]
        assert "supervisor" in first_call[0][0]
    
    @pytest.mark.asyncio
    async def test_supervisor_parallel_execution(self, supervisor_setup):
        """Test parallel execution of worker tasks."""
        supervisor, workers = supervisor_setup
        
        # Track execution order
        execution_times = {}
        
        async def mock_execute(agent_url, prompt, context=None):
            execution_times[agent_url] = datetime.now()
            if "supervisor" in agent_url:
                return {
                    "output": "Plan created",
                    "success": True,
                    "plan": {w.name: f"Task for {w.name}" for w in workers},
                }
            # Simulate different execution times
            await asyncio.sleep(0.1 if "worker-0" in agent_url else 0.05)
            return {"output": "Done", "success": True}
        
        client = AsyncMock()
        client.execute_agent = mock_execute
        
        pattern = SupervisorPattern(
            supervisor, workers,
            parallel_execution=True,
            client=client
        )
        
        await pattern.execute("Task")
        
        # Check that workers started roughly at the same time
        worker_times = [t for url, t in execution_times.items() if "worker" in url]
        time_diffs = [
            (worker_times[i] - worker_times[0]).total_seconds()
            for i in range(1, len(worker_times))
        ]
        
        # All should start within 0.01 seconds of each other
        assert all(diff < 0.01 for diff in time_diffs)
    
    @pytest.mark.asyncio
    async def test_supervisor_sequential_execution(self, supervisor_setup):
        """Test sequential execution mode."""
        supervisor, workers = supervisor_setup
        pattern = SupervisorPattern(
            supervisor, workers,
            parallel_execution=False
        )
        
        execution_order = []
        
        async def mock_execute(agent_url, prompt, context=None):
            execution_order.append(agent_url)
            if "supervisor" in agent_url:
                return {"output": "Plan", "success": True, "plan": {}}
            return {"output": "Done", "success": True}
        
        pattern.client = AsyncMock()
        pattern.client.execute_agent = mock_execute
        
        await pattern.execute("Task")
        
        # Verify sequential order
        assert execution_order[0] == supervisor.url
        for i in range(len(workers)):
            assert execution_order[i + 1] == workers[i].url
    
    @pytest.mark.asyncio
    async def test_supervisor_aggregation(self, supervisor_setup, mock_supervisor_client):
        """Test supervisor aggregation of worker results."""
        supervisor, workers = supervisor_setup
        
        # Custom aggregation logic
        async def aggregate_results(worker_outputs, supervisor_output):
            combined = " | ".join(worker_outputs.values())
            return f"Supervisor says: {supervisor_output} | Workers: {combined}"
        
        pattern = SupervisorPattern(
            supervisor, workers,
            client=mock_supervisor_client,
            aggregation_fn=aggregate_results
        )
        
        result = await pattern.execute("Task")
        
        assert "Supervisor says:" in result["final_output"]
        assert "Workers:" in result["final_output"]


class TestSwarmPattern:
    """Test SwarmPattern implementation."""
    
    @pytest.fixture
    def swarm_agents(self):
        """Create agents for swarm pattern."""
        return [
            AgentInfo(
                name=f"swarm-agent-{i}",
                url=f"http://localhost:700{i}",
                role=f"Swarm agent {i}",
            )
            for i in range(5)
        ]
    
    @pytest.fixture
    def mock_swarm_client(self):
        """Create mock client for swarm pattern."""
        client = AsyncMock()
        
        async def mock_execute(agent_url, prompt, context=None):
            # Different agents provide different answers
            agent_num = int(agent_url[-1])
            if agent_num < 3:
                return {"output": "Answer A", "success": True}
            else:
                return {"output": "Answer B", "success": True}
        
        client.execute_agent = mock_execute
        return client
    
    @pytest.mark.asyncio
    async def test_swarm_pattern_initialization(self, swarm_agents):
        """Test SwarmPattern initialization."""
        pattern = SwarmPattern(swarm_agents)
        
        assert pattern.name == "swarm"
        assert len(pattern.agents) == 5
        assert pattern.aggregation_strategy == "majority_vote"
    
    @pytest.mark.asyncio
    async def test_swarm_parallel_execution(self, swarm_agents, mock_swarm_client):
        """Test parallel execution of all agents."""
        pattern = SwarmPattern(swarm_agents, client=mock_swarm_client)
        
        start_time = datetime.now()
        result = await pattern.execute("Question for the swarm")
        end_time = datetime.now()
        
        assert result["success"] is True
        assert "agent_outputs" in result
        assert len(result["agent_outputs"]) == 5
        
        # Should complete quickly due to parallel execution
        assert (end_time - start_time).total_seconds() < 1.0
    
    @pytest.mark.asyncio
    async def test_swarm_majority_vote(self, swarm_agents, mock_swarm_client):
        """Test majority vote aggregation."""
        pattern = SwarmPattern(
            swarm_agents,
            aggregation_strategy="majority_vote",
            client=mock_swarm_client
        )
        
        result = await pattern.execute("What is the answer?")
        
        # 3 agents say "Answer A", 2 say "Answer B"
        assert result["final_output"] == "Answer A"
        assert result["aggregation_details"]["votes"]["Answer A"] == 3
        assert result["aggregation_details"]["votes"]["Answer B"] == 2
    
    @pytest.mark.asyncio
    async def test_swarm_longest_common_subsequence(self, swarm_agents):
        """Test longest common subsequence aggregation."""
        client = AsyncMock()
        
        async def mock_execute(agent_url, prompt, context=None):
            responses = [
                "The capital of France is Paris",
                "Paris is the capital of France",
                "The capital city of France is Paris",
                "France's capital is Paris",
                "Capital of France: Paris",
            ]
            agent_num = int(agent_url[-1])
            return {"output": responses[agent_num], "success": True}
        
        client.execute_agent = mock_execute
        
        pattern = SwarmPattern(
            swarm_agents,
            aggregation_strategy="longest_common",
            client=client
        )
        
        result = await pattern.execute("What is the capital of France?")
        
        # Should find common elements
        assert "Paris" in result["final_output"]
        assert "France" in result["final_output"]
    
    @pytest.mark.asyncio
    async def test_swarm_quality_weighted(self, swarm_agents):
        """Test quality-weighted aggregation."""
        client = AsyncMock()
        
        async def mock_execute(agent_url, prompt, context=None):
            agent_num = int(agent_url[-1])
            # Simulate different quality scores
            return {
                "output": f"Answer from agent {agent_num}",
                "success": True,
                "quality_score": 0.9 if agent_num == 0 else 0.5,
            }
        
        client.execute_agent = mock_execute
        
        pattern = SwarmPattern(
            swarm_agents,
            aggregation_strategy="quality_weighted",
            client=client
        )
        
        result = await pattern.execute("Question")
        
        # Agent 0 with highest quality should dominate
        assert "agent 0" in result["final_output"]
    
    @pytest.mark.asyncio
    async def test_swarm_partial_failures(self, swarm_agents):
        """Test swarm with some agent failures."""
        client = AsyncMock()
        
        async def mock_execute(agent_url, prompt, context=None):
            agent_num = int(agent_url[-1])
            if agent_num < 2:  # First two agents fail
                return {"output": "", "success": False}
            return {"output": "Success", "success": True}
        
        client.execute_agent = mock_execute
        
        pattern = SwarmPattern(swarm_agents, client=client)
        result = await pattern.execute("Task")
        
        # Should still succeed with partial results
        assert result["success"] is True
        assert result["statistics"]["failed_agents"] == 2
        assert result["statistics"]["successful_agents"] == 3
    
    @pytest.mark.asyncio
    async def test_swarm_complete_failure(self, swarm_agents):
        """Test swarm when all agents fail."""
        client = AsyncMock()
        client.execute_agent.return_value = {"output": "", "success": False}
        
        pattern = SwarmPattern(swarm_agents, client=client)
        result = await pattern.execute("Task")
        
        assert result["success"] is False
        assert "All agents failed" in result.get("error", "")
    
    @pytest.mark.asyncio
    async def test_swarm_custom_aggregation(self, swarm_agents, mock_swarm_client):
        """Test custom aggregation function."""
        async def custom_aggregate(outputs):
            # Custom logic: concatenate all outputs
            return " AND ".join(outputs.values())
        
        pattern = SwarmPattern(
            swarm_agents,
            aggregation_strategy="custom",
            custom_aggregator=custom_aggregate,
            client=mock_swarm_client
        )
        
        result = await pattern.execute("Task")
        
        assert " AND " in result["final_output"]
        assert result["final_output"].count(" AND ") == 4  # 5 outputs joined