# ACP-Evals Examples

This directory contains example agents and servers that can be used for testing with acp-evals.

## ACP Agent Server (OpenAI/Anthropic)

The `acp_agent_server.py` file provides an ACP-compliant server that uses real LLMs (OpenAI GPT-4 or Anthropic Claude).

### Prerequisites

Ensure you have API keys configured in your `.env` file:
```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Running the Server

```bash
python examples/acp_agent_server.py
```

This starts an ACP server on `http://localhost:8000` with three agents:
- `test-openai`: Uses OpenAI GPT-4
- `test-anthropic`: Uses Anthropic Claude
- `my-agent`: Default agent using OpenAI GPT-4

### Testing

```bash
# Test with default agent
acp-evals run accuracy http://localhost:8000/agents/my-agent \
  -i "What is 2+2?" \
  -e "4"

# Test with Anthropic
acp-evals run accuracy http://localhost:8000/agents/test-anthropic \
  -i "Explain quantum computing" \
  -e "Quantum computing uses qubits"
```

## BeeAI ACP Server Example

The `beeai_acp_server.py` file demonstrates how to create a BeeAI agent that's accessible via the ACP protocol.

### Prerequisites

1. Install BeeAI framework:
```bash
pip install beeai-framework
```

2. Install and run Ollama:
```bash
# Install Ollama from https://ollama.com
# Then pull the model:
ollama pull granite3.3:8b
```

### Running the Server

```bash
python examples/beeai_acp_server.py
```

This will start an ACP server on `http://127.0.0.1:8001` with a demo agent available at `http://127.0.0.1:8001/agents/demo_agent`.

### Testing with acp-evals

Once the server is running, you can test it with acp-evals:

```bash
# Test accuracy evaluation
acp-evals run accuracy http://127.0.0.1:8001/agents/demo_agent \
  -i "What is the capital of France?" \
  -e "Paris"

# Test with tool usage
acp-evals run accuracy http://127.0.0.1:8001/agents/demo_agent \
  -i "Calculate 15 + 27" \
  -e "42"

# Test performance
acp-evals run performance http://127.0.0.1:8001/agents/demo_agent \
  -i "Tell me about Python programming"

# Test reliability with expected tools
acp-evals run reliability http://127.0.0.1:8001/agents/demo_agent \
  -i "What's the weather in Paris and calculate 10 * 5" \
  --expected-tools get_weather calculate

# Run comprehensive evaluation
acp-evals test http://127.0.0.1:8001/agents/demo_agent
```

### Available Tools

The demo agent includes three tools:
- `calculate`: Performs mathematical calculations
- `get_weather`: Returns mock weather data for major cities
- `search`: Returns mock search results for common queries

### Customization

You can modify the agent by:
1. Adding more tools
2. Changing the LLM model
3. Adjusting the agent's metadata and description
4. Implementing real APIs instead of mock data

## Simple Mock Server

The `simple_acp_server.py` provides a lightweight ACP server using FastAPI and OpenAI, useful for quick testing.

## Evaluation Examples

The directory also includes example evaluation scripts:
- `accuracy_eval.py`: Demonstrates accuracy evaluation
- `performance_eval.py`: Shows performance testing
- `reliability_eval.py`: Examples of reliability evaluation

## Summary

Choose the appropriate server based on your needs:
- **acp_agent_server.py**: Full ACP-compliant server with real LLMs
- **beeai_acp_server.py**: BeeAI framework integration with tools
- **simple_acp_server.py**: Lightweight mock server for testing