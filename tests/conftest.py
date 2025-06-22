"""
Pytest configuration and shared fixtures for ACP evals tests.
"""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from acp_sdk import Event, Message, MessagePart, Run

from acp_evals.core.base import (
    AgentInfo,
    BenchmarkTask,
)

# Event loop is now handled by pytest-asyncio's default configuration


# Mock ACP SDK objects
@pytest.fixture
def mock_run():
    """Create a mock Run object."""
    run = Mock(spec=Run)
    run.id = "test-run-123"
    run.run_id = "test-run-123"  # Some code expects run_id instead of id
    run.status = "completed"
    run.created_at = datetime.now()
    run.updated_at = datetime.now()
    run.metadata = {}
    return run


@pytest.fixture
def mock_message_part():
    """Create a mock MessagePart."""
    part = Mock(spec=MessagePart)
    part.content = "Test message content"
    part.type = "text"
    part.name = None  # MessagePart can have optional name
    part.content_type = "text/plain"  # Content type for the part
    part.content_encoding = "plain"  # Default encoding
    part.content_url = None  # No URL for this part
    return part


@pytest.fixture
def mock_message(mock_message_part):
    """Create a mock Message with parts."""
    message = Mock(spec=Message)
    message.parts = [mock_message_part]
    message.role = "assistant"
    return message


@pytest.fixture
def mock_events(mock_message):
    """Create a list of mock events."""
    events = []

    # Run created event
    run_created = Mock(spec=Event)
    run_created.type = "run.created"
    run_created.timestamp = datetime.now()
    run_created.data = {"run_id": "test-run-123"}
    events.append(run_created)

    # Message created events
    for i in range(3):
        msg_event = Mock(spec=Event)
        msg_event.type = "message.created"
        msg_event.timestamp = datetime.now()
        msg_event.message = mock_message
        msg_event.agent_id = f"agent-{i % 2}"  # Alternate between 2 agents
        msg_event.data = {
            "tokens": {
                "input": 100 + i * 10,
                "output": 50 + i * 5,
            }
        }
        events.append(msg_event)

    # Tool call events
    tool_event = Mock(spec=Event)
    tool_event.type = "tool.called"
    tool_event.timestamp = datetime.now()
    tool_event.data = {
        "tool_name": "search",
        "tokens": {"input": 20, "output": 80},
    }
    events.append(tool_event)

    return events


@pytest.fixture
def mock_agent_info():
    """Create mock AgentInfo objects."""
    agents = []
    for i in range(3):
        agent = AgentInfo(
            name=f"test-agent-{i}",
            url=f"http://localhost:800{i}",
            role=f"Test agent {i}",
            capabilities=["text-generation", "tool-use"],
        )
        agents.append(agent)
    return agents


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for LLMJudge tests."""
    return AsyncMock(
        return_value={
            "score": 0.85,
            "feedback": "Good quality output with minor issues",
            "scores": {
                "factual_accuracy": 0.9,
                "completeness": 0.8,
                "clarity": 0.85,
                "relevance": 0.9,
                "efficiency": 0.8,
            },
        }
    )


@pytest.fixture
def sample_benchmark_tasks():
    """Create sample benchmark tasks."""
    return [
        BenchmarkTask(
            id="task-1",
            prompt="What is the capital of France?",
            expected_output="Paris",
            category="factual",
            metadata={"difficulty": "easy"},
        ),
        BenchmarkTask(
            id="task-2",
            prompt="Explain quantum computing in simple terms",
            expected_output={"keywords": ["qubits", "superposition", "entanglement"]},
            category="explanation",
            metadata={"difficulty": "medium"},
        ),
        BenchmarkTask(
            id="task-3",
            prompt="Write a function to calculate factorial",
            expected_output={"contains": ["def", "factorial", "return"]},
            category="coding",
            metadata={"difficulty": "medium"},
        ),
    ]


@pytest.fixture
def mock_telemetry_exporter():
    """Mock OpenTelemetry exporter."""
    exporter = MagicMock()
    exporter.export_run = AsyncMock()
    exporter.export_benchmark = AsyncMock()
    exporter.shutdown = AsyncMock()
    return exporter


# Utility functions for tests
def create_mock_event(
    event_type: str,
    timestamp: datetime | None = None,
    data: dict[str, Any] | None = None,
    **kwargs,
) -> Mock:
    """Create a mock event with specified attributes."""
    event = Mock(spec=Event)
    event.type = event_type
    event.timestamp = timestamp or datetime.now()
    event.data = data or {}

    # Add any additional attributes
    for key, value in kwargs.items():
        setattr(event, key, value)

    return event


def create_mock_run_with_events(
    run_id: str = "test-run",
    num_messages: int = 5,
    num_agents: int = 2,
) -> tuple[Mock, list[Mock]]:
    """Create a mock run with associated events."""
    run = Mock(spec=Run)
    run.id = run_id
    run.status = "completed"
    run.created_at = datetime.now()
    run.metadata = {"test": True}

    events = []

    # Run created
    events.append(create_mock_event("run.created", data={"run_id": run_id}))

    # Message events
    for i in range(num_messages):
        agent_id = f"agent-{i % num_agents}"
        message = Mock(spec=Message)
        message.parts = [Mock(content=f"Message {i} from {agent_id}")]

        events.append(
            create_mock_event(
                "message.created",
                message=message,
                agent_id=agent_id,
                data={
                    "tokens": {
                        "input": 100 + i * 10,
                        "output": 50 + i * 5,
                    }
                },
            )
        )

    return run, events


# Async test helpers
async def async_return(value):
    """Helper to return a value asynchronously."""
    return value


async def async_raise(exception):
    """Helper to raise an exception asynchronously."""
    raise exception
