"""
Base class for multi-agent patterns.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from acp_sdk import Message, MessagePart
from acp_sdk.client import Client


@dataclass
class AgentInfo:
    """Information about an agent in a pattern."""
    name: str
    url: str
    role: str | None = None
    capabilities: list[str] | None = None
    metadata: dict[str, Any] | None = None


class AgentPattern(ABC):
    """Base class for multi-agent execution patterns."""

    def __init__(self, agents: list[AgentInfo], name: str | None = None):
        """
        Initialize pattern with agent information.

        Args:
            agents: List of agent information
            name: Optional pattern name
        """
        self.agents = agents
        self.name = name or self.__class__.__name__
        self._clients = {}

    def _get_client(self, agent: AgentInfo) -> Client:
        """Get or create client for an agent."""
        if agent.name not in self._clients:
            self._clients[agent.name] = Client(base_url=agent.url)
        return self._clients[agent.name]

    def _create_message(self, content: str) -> Message:
        """Create a standard message."""
        return Message(
            parts=[MessagePart(content=content, content_type="text/plain")]
        )

    @abstractmethod
    async def execute(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the pattern with given task.

        Args:
            task: The task to execute
            context: Optional context information

        Returns:
            Pattern execution results including responses and metrics
        """
        pass

    @property
    @abstractmethod
    def pattern_type(self) -> str:
        """Type of pattern (e.g., 'linear', 'supervisor', 'swarm')."""
        pass

    @property
    def agent_count(self) -> int:
        """Number of agents in the pattern."""
        return len(self.agents)

    async def close(self):
        """Close all client connections."""
        for client in self._clients.values():
            await client.close()
