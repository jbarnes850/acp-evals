#!/usr/bin/env python3
"""
ACP Server implementation for serving agents via Agent Communication Protocol.

This server wraps agent functions and makes them available via the ACP protocol,
compatible with BeeAI framework and other ACP clients.
"""

import asyncio
import logging
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional

try:
    from acp_sdk import models as acp_models
    from acp_sdk.server import ACPServer, ACPServerAgent, ACPServerConfig

    ACP_SDK_AVAILABLE = True
except ImportError:
    ACP_SDK_AVAILABLE = False
    # Fallback implementation
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

logger = logging.getLogger(__name__)


if ACP_SDK_AVAILABLE:
    # Use official ACP SDK
    class ACPEvaluationServer:
        """ACP server for serving evaluation agents."""

        def __init__(self, port: int = 8001, host: str = "localhost"):
            self.config = ACPServerConfig(port=port, host=host)
            self.server = ACPServer(config=self.config)
            self.agents: dict[str, Callable] = {}

        def register_agent(
            self,
            agent_function: Callable,
            name: str,
            description: str = "Evaluation agent",
            tags: list[str] | None = None,
            **metadata,
        ):
            """Register an agent function with the ACP server."""
            self.agents[name] = agent_function

            # Wrap the function for ACP compatibility
            async def acp_agent_wrapper(inputs):
                """Wrapper to make agent function ACP-compatible."""
                if isinstance(inputs, list) and inputs:
                    # Extract text from first message
                    first_input = inputs[0]
                    if hasattr(first_input, "parts") and first_input.parts:
                        text = first_input.parts[0].content
                    else:
                        text = str(first_input)
                else:
                    text = str(inputs)

                # Call the agent function
                if asyncio.iscoroutinefunction(agent_function):
                    response = await agent_function(text)
                else:
                    response = agent_function(text)

                # Return ACP-compatible response
                return acp_models.MessagePart(content=str(response), role="assistant")

            # Register with ACP server
            self.server.register(
                acp_agent_wrapper,
                name=name,
                description=description,
                tags=tags or ["evaluation"],
                programming_language="Python",
                natural_languages=["English"],
                framework="ACP-Evals",
                **metadata,
            )

        def serve(self):
            """Start the ACP server."""
            logger.info(f"Starting ACP server on {self.config.host}:{self.config.port}")
            self.server.serve()

else:
    # Fallback HTTP implementation
    class AgentModel(BaseModel):
        name: str
        description: str
        version: str = "1.0.0"
        tags: list[str] = []
        framework: str = "ACP-Evals"

    class MessageModel(BaseModel):
        content: str
        role: str = "user"

    class RunRequestModel(BaseModel):
        input: list[MessageModel]
        session_id: str | None = None

    class ACPEvaluationServer:
        """Fallback ACP server implementation."""

        def __init__(self, port: int = 8001, host: str = "localhost"):
            self.port = port
            self.host = host
            self.app = FastAPI(title="ACP Evaluation Server")
            self.agents: dict[str, dict] = {}
            self.agent_functions: dict[str, Callable] = {}
            self._setup_routes()

        def _setup_routes(self):
            """Setup FastAPI routes for ACP compatibility."""

            @self.app.get("/agents")
            async def list_agents():
                """List all available agents."""
                return list(self.agents.values())

            @self.app.get("/agents/{agent_name}")
            async def get_agent(agent_name: str):
                """Get specific agent details."""
                if agent_name not in self.agents:
                    raise HTTPException(status_code=404, detail="Agent not found")
                return self.agents[agent_name]

            @self.app.post("/agents/{agent_name}/run")
            async def run_agent(agent_name: str, request: RunRequestModel):
                """Execute an agent."""
                if agent_name not in self.agent_functions:
                    raise HTTPException(status_code=404, detail="Agent not found")

                try:
                    # Extract text from input messages
                    if request.input and len(request.input) > 0:
                        text = request.input[0].content
                    else:
                        text = ""

                    # Call the agent function
                    agent_func = self.agent_functions[agent_name]
                    if asyncio.iscoroutinefunction(agent_func):
                        response = await agent_func(text)
                    else:
                        response = agent_func(text)

                    return {
                        "output": [{"content": str(response), "role": "assistant"}],
                        "session_id": request.session_id or str(uuid.uuid4()),
                        "status": "completed",
                    }

                except Exception as e:
                    logger.error(f"Error running agent {agent_name}: {e}")
                    raise HTTPException(status_code=500, detail=str(e))

        def register_agent(
            self,
            agent_function: Callable,
            name: str,
            description: str = "Evaluation agent",
            tags: list[str] | None = None,
            **metadata,
        ):
            """Register an agent function."""
            self.agent_functions[name] = agent_function
            self.agents[name] = {
                "name": name,
                "description": description,
                "version": metadata.get("version", "1.0.0"),
                "tags": tags or ["evaluation"],
                "framework": "ACP-Evals",
                "created_at": datetime.now().isoformat(),
                "url": f"http://{self.host}:{self.port}/agents/{name}",
                **metadata,
            }

        def serve(self):
            """Start the server."""
            logger.info(f"Starting ACP server on {self.host}:{self.port}")
            uvicorn.run(self.app, host=self.host, port=self.port)


def create_server(port: int = 8001, host: str = "localhost") -> ACPEvaluationServer:
    """Create an ACP evaluation server."""
    return ACPEvaluationServer(port=port, host=host)


def serve_agent(
    agent_function: Callable,
    name: str = "evaluation_agent",
    description: str = "ACP Evaluation Agent",
    port: int = 8001,
    host: str = "localhost",
    tags: list[str] | None = None,
    **metadata,
):
    """Serve a single agent via ACP protocol."""
    server = create_server(port=port, host=host)
    server.register_agent(
        agent_function=agent_function, name=name, description=description, tags=tags, **metadata
    )
    server.serve()


if __name__ == "__main__":
    # Example usage
    def example_agent(text: str) -> str:
        """Example agent for testing."""
        if "hello" in text.lower():
            return "Hello! How can I help you?"
        elif "2+2" in text:
            return "4"
        elif "capital of france" in text.lower():
            return "Paris"
        else:
            return "I'm not sure about that. Could you rephrase?"

    # Serve the example agent
    serve_agent(
        agent_function=example_agent,
        name="example_agent",
        description="A simple example agent for testing ACP evaluations",
        tags=["example", "test"],
        version="1.0.0",
    )
