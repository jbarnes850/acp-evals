"""
Integration tests for ACP Evals framework.

These tests validate the complete workflow of evaluating agents
using the ACP SDK patterns.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
import json

from acp_sdk import Run, Event, Message, MessagePart, RunStatus
from acp_sdk.client import Client

from acp_evals.client import ACPEvaluationClient
from acp_evals.metrics import TokenUsageMetric, HandoffQualityMetric
from acp_evals.benchmarks import ContextScalingBenchmark
from acp_evals.evaluators import LLMJudge
from acp_evals.patterns import LinearPattern, SupervisorPattern, SwarmPattern, AgentInfo


class TestACPIntegration:
    """Test complete ACP evaluation workflows."""
    
    @pytest.fixture
    def mock_acp_client(self):
        """Create a mock ACP client with proper response structure."""
        client = Mock(spec=Client)
        
        # Mock agent listing
        async def mock_agents():
            return [
                {"name": "test-agent", "description": "Test agent", "metadata": {}},
                {"name": "helper-agent", "description": "Helper agent", "metadata": {}},
            ]
        
        client.agents = AsyncMock(side_effect=mock_agents)
        
        # Mock run creation and execution
        async def mock_run_sync(agent, input, **kwargs):
            # Create proper Run object structure
            run = Mock(spec=Run)
            run.run_id = "test-run-123"
            run.agent_name = agent
            run.status = RunStatus.COMPLETED
            run.created_at = datetime.now()
            run.updated_at = datetime.now()
            
            # Create output message
            output_message = Mock(spec=Message)
            output_part = Mock(spec=MessagePart)
            output_part.content = f"Response from {agent}"
            output_part.content_type = "text/plain"
            output_message.parts = [output_part]
            
            run.output = [output_message]
            run.error = None
            
            return run
        
        client.run_sync = AsyncMock(side_effect=mock_run_sync)
        
        # Mock event streaming
        async def mock_run_events_stream(run_id):
            events = []
            
            # Run created event
            event1 = Mock(spec=Event)
            event1.type = "run.created"
            event1.timestamp = datetime.now()
            event1.data = {"run_id": run_id}
            events.append(event1)
            
            # Message created event with tokens
            event2 = Mock(spec=Event)
            event2.type = "message.created"
            event2.timestamp = datetime.now()
            event2.agent_id = "test-agent"
            event2.data = {
                "tokens": {"input": 150, "output": 75},
                "model": "gpt-4",
            }
            events.append(event2)
            
            # Run completed event
            event3 = Mock(spec=Event)
            event3.type = "run.completed"
            event3.timestamp = datetime.now()
            event3.data = {"run_id": run_id}
            events.append(event3)
            
            for event in events:
                yield event
        
        client.run_events_stream = mock_run_events_stream
        
        # Mock run status checking
        async def mock_run(run_id):
            run = Mock(spec=Run)
            run.run_id = run_id
            run.status = RunStatus.COMPLETED
            run.status.is_terminal = True
            return run
        
        client.run = AsyncMock(side_effect=mock_run)
        
        return client
    
    @pytest.mark.asyncio
    async def test_single_agent_evaluation(self, mock_acp_client):
        """Test evaluating a single agent with metrics."""
        # Create evaluation client
        eval_client = ACPEvaluationClient(
            base_url="http://localhost:8000",
            metrics=[TokenUsageMetric()],
        )
        eval_client.client = mock_acp_client
        
        # Run evaluation
        run, events, metrics = await eval_client.run_with_tracking(
            agent_name="test-agent",
            input="What is the capital of France?",
        )
        
        # Verify results
        assert run.status == RunStatus.COMPLETED
        assert len(events) > 0
        assert "token_usage" in metrics
        
        # Check token metrics
        token_metric = metrics["token_usage"]
        assert token_metric.value > 0
        assert token_metric.breakdown["input_tokens"] == 150
        assert token_metric.breakdown["output_tokens"] == 75
    
    @pytest.mark.asyncio
    async def test_benchmark_execution(self, mock_acp_client):
        """Test running a benchmark against an agent."""
        # Create evaluation client
        eval_client = ACPEvaluationClient(
            base_url="http://localhost:8000",
            metrics=[TokenUsageMetric()],
        )
        eval_client.client = mock_acp_client
        
        # Create benchmark with minimal tasks
        benchmark = ContextScalingBenchmark(
            tasks=[{
                "id": "test-task",
                "prompt": "Test prompt",
                "expected_output": "Test response",
            }],
            context_levels=[0, 5],
        )
        
        # Run benchmark
        result = await eval_client.run_benchmark(
            agent_name="test-agent",
            benchmark=benchmark,
        )
        
        # Verify benchmark result
        assert result.benchmark_name == "context_scaling"
        assert result.tasks_completed >= 0
        assert result.tasks_total == 2  # 1 task × 2 context levels
        assert 0 <= result.overall_score <= 1
    
    @pytest.mark.asyncio
    async def test_multi_agent_linear_pattern(self):
        """Test linear multi-agent pattern execution."""
        # Create mock agents
        agents = [
            AgentInfo(
                name="analyzer",
                url="http://localhost:8001",
                role="Analyze the input",
            ),
            AgentInfo(
                name="enhancer",
                url="http://localhost:8002",
                role="Enhance the analysis",
            ),
            AgentInfo(
                name="finalizer",
                url="http://localhost:8003",
                role="Finalize the output",
            ),
        ]
        
        # Create pattern
        pattern = LinearPattern(agents)
        
        # Mock client responses for each agent
        mock_clients = {}
        for agent in agents:
            client = Mock(spec=Client)
            
            async def make_response(agent_name):
                async def mock_run_sync(agent, input, **kwargs):
                    run = Mock(spec=Run)
                    run.output = [Mock(parts=[Mock(content=f"Processed by {agent_name}")])]
                    return run
                return mock_run_sync
            
            client.run_sync = AsyncMock(side_effect=await make_response(agent.name))
            mock_clients[agent.name] = client
        
        # Mock client creation
        pattern._get_client = lambda agent: mock_clients[agent.name]
        
        # Execute pattern
        result = await pattern.execute(
            "Analyze this data",
            context={"preserve": {"key": "value"}},
        )
        
        # Verify execution
        assert result["pattern"] == "linear"
        assert result["success"] is True
        assert len(result["handoffs"]) == 3
        assert "Processed by finalizer" in result["final_output"]
    
    @pytest.mark.asyncio
    async def test_llm_judge_evaluation(self):
        """Test LLM-as-Judge evaluator with proper rubric."""
        # Create judge
        judge = LLMJudge(
            model="gpt-4",
            temperature=0.0,
        )
        
        # Mock LLM response
        mock_response = {
            "score": 0.85,
            "pass": True,
            "feedback": "Good response with minor issues in clarity.",
            "scores": {
                "factual_accuracy": 0.95,
                "completeness": 0.80,
                "clarity": 0.75,
                "relevance": 0.90,
                "efficiency": 0.85,
            }
        }
        
        with patch.object(judge, '_call_llm', return_value=json.dumps(mock_response)):
            result = await judge.evaluate(
                "Paris is the capital of France.",
                "The capital of France is Paris.",
            )
        
        # Verify evaluation
        assert result.score == 0.85
        assert result.passed is True
        assert "minor issues" in result.feedback
        assert result.details["scores"]["factual_accuracy"] == 0.95
    
    @pytest.mark.asyncio
    async def test_handoff_quality_tracking(self):
        """Test handoff quality metric in multi-agent scenario."""
        metric = HandoffQualityMetric()
        
        # Create mock events simulating handoffs
        events = []
        
        # Agent 1 initial message
        msg1 = Mock(spec=Message)
        msg1.parts = [Mock(content="Budget: $50,000, Deadline: March 2025")]
        
        event1 = Mock(spec=Event)
        event1.type = "message.created"
        event1.timestamp = datetime.now()
        event1.agent_id = "agent-1"
        event1.message = msg1
        events.append(event1)
        
        # Agent 2 preserves most info
        msg2 = Mock(spec=Message)
        msg2.parts = [Mock(content="Working with budget $50,000 and March 2025 deadline")]
        
        event2 = Mock(spec=Event)
        event2.type = "message.created"
        event2.timestamp = datetime.now()
        event2.agent_id = "agent-2"
        event2.message = msg2
        events.append(event2)
        
        # Agent 3 loses some info
        msg3 = Mock(spec=Message)
        msg3.parts = [Mock(content="Project has budget constraints and Q1 deadline")]
        
        event3 = Mock(spec=Event)
        event3.type = "message.created"
        event3.timestamp = datetime.now()
        event3.agent_id = "agent-3"
        event3.message = msg3
        events.append(event3)
        
        # Calculate metric
        run = Mock(spec=Run)
        result = await metric.calculate(run, events)
        
        # Verify handoff analysis
        assert result.name == "handoff_quality"
        assert result.breakdown["handoff_count"] == 2
        assert 0 < result.value < 1  # Some degradation expected
        assert result.breakdown["degradation_factor"] > 0
    
    @pytest.mark.asyncio
    async def test_supervisor_pattern_coordination(self):
        """Test supervisor pattern with worker coordination."""
        # Create supervisor and workers
        supervisor = AgentInfo(
            name="supervisor",
            url="http://localhost:8000",
            role="Coordinate tasks",
        )
        
        workers = [
            AgentInfo(name=f"worker-{i}", url=f"http://localhost:800{i}", role=f"Worker {i}")
            for i in range(3)
        ]
        
        pattern = SupervisorPattern(supervisor, workers, parallel_execution=True)
        
        # Mock supervisor planning
        supervisor_client = Mock(spec=Client)
        async def mock_supervisor_run(agent, input, **kwargs):
            run = Mock(spec=Run)
            run.output = [Mock(parts=[Mock(content="Delegating tasks to workers")])]
            return run
        
        supervisor_client.run_sync = AsyncMock(side_effect=mock_supervisor_run)
        
        # Mock worker executions
        worker_clients = {}
        for worker in workers:
            client = Mock(spec=Client)
            async def make_worker_response(name):
                async def mock_run(agent, input, **kwargs):
                    run = Mock(spec=Run)
                    run.output = [Mock(parts=[Mock(content=f"Task completed by {name}")])]
                    return run
                return mock_run
            
            client.run_sync = AsyncMock(side_effect=await make_worker_response(worker.name))
            worker_clients[worker.name] = client
        
        # Mock client creation
        def get_client(agent):
            if agent.name == "supervisor":
                return supervisor_client
            return worker_clients[agent.name]
        
        pattern._get_client = get_client
        
        # Execute pattern
        result = await pattern.execute("Complex task requiring coordination")
        
        # Verify coordination
        assert result["pattern"] == "supervisor"
        assert result["success"] is True
        assert "supervisor_output" in result
        assert len(result["worker_outputs"]) == 3
        assert all(f"worker-{i}" in str(result["worker_outputs"]) for i in range(3))
    
    @pytest.mark.asyncio
    async def test_swarm_pattern_voting(self):
        """Test swarm pattern with majority voting."""
        # Create swarm agents
        agents = [
            AgentInfo(name=f"agent-{i}", url=f"http://localhost:900{i}")
            for i in range(5)
        ]
        
        pattern = SwarmPattern(agents, aggregation_strategy="majority_vote")
        
        # Mock responses - 3 say A, 2 say B
        mock_clients = {}
        for i, agent in enumerate(agents):
            client = Mock(spec=Client)
            answer = "Answer A" if i < 3 else "Answer B"
            
            async def make_response(ans):
                async def mock_run(agent, input, **kwargs):
                    run = Mock(spec=Run)
                    run.output = [Mock(parts=[Mock(content=ans)])]
                    return run
                return mock_run
            
            client.run_sync = AsyncMock(side_effect=await make_response(answer))
            mock_clients[agent.name] = client
        
        pattern._get_client = lambda agent: mock_clients[agent.name]
        
        # Execute pattern
        result = await pattern.execute("What is the answer?")
        
        # Verify voting
        assert result["pattern"] == "swarm"
        assert result["success"] is True
        assert result["final_output"] == "Answer A"
        assert result["aggregation_details"]["votes"]["Answer A"] == 3
        assert result["aggregation_details"]["votes"]["Answer B"] == 2
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, mock_acp_client):
        """Test complete evaluation workflow with all components."""
        # Create evaluation client with multiple metrics
        eval_client = ACPEvaluationClient(
            base_url="http://localhost:8000",
            metrics=[
                TokenUsageMetric(),
                HandoffQualityMetric(),
            ],
        )
        eval_client.client = mock_acp_client
        
        # List available agents
        agents = await eval_client.list_agents()
        assert len(agents) == 2
        assert any(a["name"] == "test-agent" for a in agents)
        
        # Get specific agent
        agent = await eval_client.get_agent("test-agent")
        assert agent is not None
        assert agent["name"] == "test-agent"
        
        # Run simple evaluation
        response = await eval_client.run_sync_simple(
            "test-agent",
            "Hello, world!",
        )
        assert "Response from test-agent" in response
        
        # Run streaming evaluation with callback
        events_received = []
        
        async def event_callback(event):
            events_received.append(event.type)
        
        run, events, metrics = await eval_client.evaluate_streaming(
            "test-agent",
            "Stream this response",
            callback=event_callback,
        )
        
        # Verify streaming worked
        assert len(events_received) > 0
        assert "run.created" in events_received
        assert "run.completed" in events_received