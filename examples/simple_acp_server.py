#!/usr/bin/env python3
"""
Simple ACP Server Example using OpenAI

This example demonstrates a minimal ACP server that can be used
for testing with acp-evals. It uses OpenAI API which is already
configured in the environment.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Simple ACP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ACP Models
class MessagePart(BaseModel):
    content: str
    content_type: str = "text/plain"


class Message(BaseModel):
    role: str = "user"
    parts: list[MessagePart]


class RunRequest(BaseModel):
    input: list[Message]
    stream: bool = False


class RunResponse(BaseModel):
    run_id: str
    status: str
    output: list[Message] = []
    created_at: datetime = None
    updated_at: datetime = None


class AgentInfo(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    tools: list[str] = []


# In-memory storage for runs
runs = {}

# Available agents
agents = {
    "simple_agent": AgentInfo(
        name="simple_agent",
        description="A simple agent for testing acp-evals",
        tools=["calculate", "search"],
    )
}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Simple ACP Server", "agents": list(agents.keys())}


@app.get("/agents")
async def list_agents():
    """List available agents."""
    return {"agents": list(agents.values())}


@app.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get agent information."""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    return agents[agent_name]


@app.post("/agents/{agent_name}/runs")
async def create_run(agent_name: str, request: RunRequest):
    """Create a new run for the agent."""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    # Generate run ID
    run_id = str(uuid.uuid4())

    # Create run
    run = RunResponse(
        run_id=run_id, status="processing", created_at=datetime.now(), updated_at=datetime.now()
    )
    runs[run_id] = run

    # Process asynchronously
    asyncio.create_task(process_run(run_id, request))

    return run


@app.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get run status."""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return runs[run_id]


async def process_run(run_id: str, request: RunRequest):
    """Process the run asynchronously."""
    try:
        # Extract user message
        user_message = ""
        for msg in request.input:
            for part in msg.parts:
                user_message += part.content + " "
        user_message = user_message.strip()

        # Check for tool usage patterns
        tools_used = []
        if "calculate" in user_message.lower() or any(
            op in user_message for op in ["+", "-", "*", "/", "="]
        ):
            tools_used.append("calculate")
        if (
            "search" in user_message.lower()
            or "what is" in user_message.lower()
            or "tell me" in user_message.lower()
        ):
            tools_used.append("search")

        # Simple response logic
        response_text = ""

        # Handle calculations
        if "calculate" in tools_used:
            try:
                # Extract simple math expressions
                import re

                math_pattern = r"(\d+\s*[+\-*/]\s*\d+)"
                matches = re.findall(math_pattern, user_message)
                if matches:
                    for expr in matches:
                        result = eval(expr)
                        response_text += f"The result of {expr} is {result}. "
            except Exception:
                pass

        # Handle search queries
        if "search" in tools_used or not response_text:
            # Use OpenAI to generate a response
            try:
                completion = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Keep responses concise.",
                        },
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.7,
                    max_tokens=150,
                )
                response_text += completion.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                response_text = f"I understand you asked: {user_message}. Let me help with that."

        # Update run with response
        runs[run_id].output = [
            Message(role="assistant", parts=[MessagePart(content=response_text)])
        ]
        runs[run_id].status = "completed"
        runs[run_id].updated_at = datetime.now()

    except Exception as e:
        logger.error(f"Error processing run {run_id}: {e}")
        runs[run_id].status = "failed"
        runs[run_id].updated_at = datetime.now()


def main():
    """Run the server."""
    logger.info("Starting Simple ACP Server...")
    logger.info("Server will be available at: http://127.0.0.1:8002")
    logger.info("Agent 'simple_agent' available at: http://127.0.0.1:8002/agents/simple_agent")
    logger.info("\nTest with acp-evals:")
    logger.info(
        "acp-evals run accuracy http://127.0.0.1:8002/agents/simple_agent -i 'What is 2+2?' -e '4'"
    )

    uvicorn.run(app, host="127.0.0.1", port=8002)


if __name__ == "__main__":
    main()
