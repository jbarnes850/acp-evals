"""ACP-compliant agent server for testing ACP-Evals with real LLMs."""

import asyncio
import logging
import os
import uuid
from datetime import UTC, datetime, timezone
from typing import Any, Optional, cast

import uvicorn

# ACP SDK imports
from acp_sdk.models import (
    Agent,
    AgentsListResponse,
    Message,
    MessagePart,
    PingResponse,
    Run,
    RunCreateRequest,
    RunCreateResponse,
    RunReadResponse,
    RunStatus,
)
from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Test ACP Agent Server", version="1.0.0")

# Initialize LLM clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# In-memory storage for runs
runs_storage: dict[str, dict[str, Any]] = {}

# Agent definitions
AGENTS = {
    "test-openai": Agent(name="test-openai", description="Test agent using OpenAI GPT-4"),
    "test-anthropic": Agent(name="test-anthropic", description="Test agent using Anthropic Claude"),
    "my-agent": Agent(  # Default agent name used in examples
        name="my-agent", description="Default test agent using OpenAI GPT-4"
    ),
}


async def run_openai_agent(messages: list[Message]) -> str:
    """Run OpenAI agent with messages."""
    # Convert ACP messages to OpenAI format with proper typing
    openai_messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "You are a helpful assistant. Be concise and direct."}
    ]

    for msg in messages:
        content = ""
        for part in msg.parts:
            if part.content_type == "text/plain" and part.content:
                content += part.content
        if content:
            openai_messages.append({"role": "user", "content": content})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o", messages=openai_messages, max_tokens=150, temperature=0.7
        )
        # Handle potential None value
        message_content = response.choices[0].message.content
        if message_content is None:
            return "No response generated"
        return message_content.strip()
    except Exception as e:
        logger.error(f"OpenAI error: {str(e)}")
        return f"Error: {str(e)}"


async def run_anthropic_agent(messages: list[Message]) -> str:
    """Run Anthropic agent with messages."""
    # Convert ACP messages to Anthropic format
    content = ""
    for msg in messages:
        for part in msg.parts:
            if part.content_type == "text/plain" and part.content:
                content += part.content + " "

    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": content.strip()}],
            max_tokens=150,
            temperature=0.7,
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Anthropic error: {str(e)}")
        return f"Error: {str(e)}"


@app.get("/ping")
async def ping() -> PingResponse:
    """Health check endpoint."""
    return PingResponse()


@app.get("/agents")
async def list_agents() -> AgentsListResponse:
    """List available agents."""
    return AgentsListResponse(agents=list(AGENTS.values()))


@app.get("/agents/{agent_name}")
async def get_agent(agent_name: str) -> Agent:
    """Get specific agent details."""
    if agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    return AGENTS[agent_name]


@app.post("/runs")
async def create_run(request: RunCreateRequest) -> RunCreateResponse:
    """Create a new agent run."""
    run_id = str(uuid.uuid4())

    logger.info(f"Creating run {run_id} for agent {request.agent_name}")

    # Validate agent exists
    if request.agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")

    # Create run object
    run = Run(
        run_id=uuid.UUID(run_id),
        agent_name=request.agent_name,
        status=RunStatus.IN_PROGRESS,
        created_at=datetime.now(UTC),
    )

    # Store run
    runs_storage[run_id] = {
        "run": run,
        "status": RunStatus.IN_PROGRESS,
        "output": None,
        "error": None,
    }

    # Process run asynchronously
    asyncio.create_task(process_run(run_id, request.agent_name, request.input))

    # Return response with proper field names
    return RunCreateResponse(agent_name=request.agent_name, run_id=run.run_id)


async def process_run(run_id: str, agent_name: str, messages: list[Message]):
    """Process agent run in background."""
    try:
        logger.info(f"Processing run {run_id} with agent {agent_name}")

        # Run appropriate agent
        if agent_name == "test-anthropic":
            response_text = await run_anthropic_agent(messages)
        else:  # Default to OpenAI for "test-openai", "my-agent", etc.
            response_text = await run_openai_agent(messages)

        # Create response message
        output_message = Message(
            parts=[MessagePart(content=response_text, content_type="text/plain")]
        )

        # Update run with results
        run_data = runs_storage[run_id]
        run_data["status"] = RunStatus.COMPLETED
        run_data["output"] = [output_message]
        run_data["run"].status = RunStatus.COMPLETED
        run_data["run"].output = [output_message]
        run_data["run"].finished_at = datetime.now(UTC)

        logger.info(f"Run {run_id} completed successfully")

    except Exception as e:
        logger.error(f"Run {run_id} failed: {str(e)}")
        run_data = runs_storage[run_id]
        run_data["status"] = RunStatus.FAILED
        run_data["error"] = str(e)
        run_data["run"].status = RunStatus.FAILED


@app.get("/runs/{run_id}")
async def get_run(run_id: str) -> RunReadResponse:
    """Get run status and results."""
    if run_id not in runs_storage:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    run_data = runs_storage[run_id]
    # Return response with proper field names
    return RunReadResponse(agent_name=run_data["run"].agent_name, run_id=run_data["run"].run_id)


if __name__ == "__main__":
    logger.info("Starting ACP-compliant test agent server on http://localhost:8000")
    logger.info("Available agents: test-openai, test-anthropic, my-agent")
    logger.info(
        "Example test: acp-evals run accuracy http://localhost:8000/agents/my-agent -i 'What is 2+2?' -e '4'"
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)
