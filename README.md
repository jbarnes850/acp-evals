# ACP Evals

**Open-Source, Research-Driven Evaluation Framework for AI agents built with the Agent Communication Protocol**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![Apache License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<a href="./docs">Documentation</a> • 
<a href="./examples">Examples</a> • 
<a href="#available-commands">Commands</a> • 
<a href="./CONTRIBUTING.md">Contributing</a>

---

ACP Evals helps you test AI agents systematically. It works with any agent that follows the [Agent Communication Protocol](https://agentcommunicationprotocol.dev).

## What You Can Do

- Test agent accuracy, performance, and safety
- Generate test data automatically
- Compare different agents on the same tasks
- Track performance over time
- Export results for CI/CD pipelines

## Key Features

- **LLM-as-Judge**: Uses advanced language models to evaluate agent responses
- **Multi-Criteria Scoring**: Breaks down evaluations into specific criteria (accuracy, completeness, relevance, etc.)
- **Token & Cost Tracking**: Monitor resource usage for every evaluation
- **Flexible Rubrics**: Choose from factual, research quality, or code quality evaluation criteria
- **Binary Mode**: Convert nuanced scores to clear pass/fail decisions
- **Production Ready**: Export results, CI/CD integration, batch processing

## Prerequisites

- Python 3.11 or newer
- An LLM API key (OpenAI, Anthropic, or Ollama)
- ACP-compatible agents to test (or use the examples)

## Installation

### From PyPI

```bash
pip install acp-evals
```

### From Source

```bash
git clone https://github.com/jbarnes850/acp-evals.git
cd acp-evals
pip install -e .
```

## Getting Started

### 1. Set Up Your API Keys

```bash
cp .env.example .env
```

Open `.env` and add your API key:
```
OPENAI_API_KEY=your-key-here
```

### 2. Verify Everything Works

```bash
acp-evals check
```

You should see:
```
Provider Status
┌───────────┬────────────┬───────────────┬──────────────────┐
│ Provider  │ Configured │ Model         │ Status           │
├───────────┼────────────┼───────────────┼──────────────────┤
│ OpenAI    │ Yes        │ gpt-4.1       │ Connected (2ms)  │
└───────────┴────────────┴───────────────┴──────────────────┘
```

### 3. Test Your First Agent

If you have an ACP agent running:
```bash
acp-evals run accuracy http://localhost:8000/agents/my-agent \
  -i "What is 2+2?" \
  -e "4"
```

Expected output:
```bash
Evaluation Result
┌────────┬──────┐
│ Score  │ 1.00 │
│ Passed │ Yes  │
└────────┴──────┘

╭───────────────── Evaluation Details ─────────────────╮
│ Feedback:                                             │
│ The response correctly answers the mathematical       │
│ question. The answer is accurate and directly         │
│ addresses what was asked.                             │
│                                                       │
│ Criteria Scores:                                      │
│   • accuracy: 1.00                                    │
│   • completeness: 1.00                                │
│   • relevance: 1.00                                   │
│                                                       │
│ [Evaluation used 316 tokens]                          │
╰───────────────────────────────────────────────────────╯
```

### 4. Generate Test Data

Create test cases automatically:
```bash
acp-evals generate tests --scenario qa --count 10 --export tests.jsonl
```

This creates 10 question-answer test cases in `tests.jsonl`.

## Running an Example Agent

Need an agent to test? Here's a minimal example:

```python
# example_agent.py
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server

server = Server()

@server.agent()
async def echo(input: list[Message], context):
    """Echoes whatever you send it"""
    for message in input:
        yield message

server.run()
```

Run it:
```bash
pip install acp-sdk
python example_agent.py
```

Then test it:
```bash
acp-evals run accuracy http://localhost:8000/agents/echo \
  -i "Hello world" \
  -e "Hello world"
```

## Available Commands

### Basic Testing

```bash
# Test accuracy
acp-evals run accuracy <agent-url> -i "input text" -e "expected output"

# Test performance
acp-evals run performance <agent-url> -i "input text"

# Quick test suite
acp-evals test <agent-url> --quick
```

Example with partial score:
```bash
acp-evals run accuracy http://localhost:8000/agents/research-agent \
  -i "Explain quantum computing" \
  -e "Quantum computing uses qubits that can be in superposition"
```

Output showing detailed evaluation:
```
Evaluation Result
┌────────┬──────┐
│ Score  │ 0.73 │
│ Passed │ Yes  │
└────────┴──────┘

╭───────────────── Evaluation Details ─────────────────╮
│ Feedback:                                             │
│ The agent provided information about quantum          │
│ computing but missed the specific concept of          │
│ superposition mentioned in the expected answer.       │
│ While the response discussed qubits and their         │
│ applications, it should have explicitly explained     │
│ how qubits can exist in multiple states               │
│ simultaneously through superposition.                  │
│                                                       │
│ Criteria Scores:                                      │
│   • accuracy: 0.70                                    │
│   • completeness: 0.65                                │
│   • relevance: 0.85                                  │
│                                                       │
│ [Evaluation used 524 tokens, cost: $0.0087]          │
╰───────────────────────────────────────────────────────╯
```

### Performance Testing

```bash
acp-evals run performance http://localhost:8000/agents/my-agent \
  -i "Generate a summary of machine learning"
```

Output:
```bash
Evaluation Result
┌────────┬────────────┐
│ Score  │ 1.00       │
│ Passed │ Yes        │
│ Latency│ 342ms      │
│ Tokens │ 156        │
└────────┴────────────┘

╭───────────────── Evaluation Details ─────────────────╮
│ Feedback:                                             │
│ Performance evaluation completed successfully.        │
│                                                       │
│ Criteria Scores:                                      │
│   • latency_ms: 342                                   │
│   • total_tokens: 156                                 │
│   • input_tokens: 42                                  │
│   • output_tokens: 114                                │
│   • tokens_per_second: 456                            │
│   • estimated_cost: 0.0024                            │
╰───────────────────────────────────────────────────────╯
```

### Code Quality Evaluation

```bash
acp-evals run accuracy http://localhost:8000/agents/code-reviewer \
  -i "def add(a, b): return a + b" \
  --rubric code_quality
```

Output:
```bash
Evaluation Result
┌────────┬──────┐
│ Score  │ 0.85 │
│ Passed │ Yes  │
└────────┴──────┘

╭───────────────── Evaluation Details ─────────────────╮
│ Feedback:                                            │
│ The code is functional and implements the basic      │
│ addition operation correctly. However, it lacks      │
│ type annotations and documentation which are         │
│ important for maintainability and clarity in         │
│ production code. The implementation itself is        │
│ efficient for this simple operation.                 │
│                                                      │
│ Criteria Scores:                                     │
│   • correctness: 1.00                                │
│   • efficiency: 1.00                                 │
│   • readability: 0.90                                │
│   • best_practices: 0.50                             │
│                                                      │
│ [Evaluation used 412 tokens]                         │
╰──────────────────────────────────────────────────────╯
```

### Data Generation

```bash
# Generate QA pairs
acp-evals generate tests --scenario qa --count 20

# Generate adversarial tests
acp-evals generate adversarial --severity high --count 5
```

### Multi-Agent Testing

```bash
# Test agent coordination
acp-evals workflow test --pattern linear \
  --agents agent1 agent2 agent3 \
  --task "Research AI trends"
```

### View Available Options

```bash
# List evaluation types
acp-evals list-rubrics

# List datasets
acp-evals dataset list

# Get help
acp-evals --help
```

## Understanding Results

### Accuracy Scores

- **1.0** - Perfect match
- **0.8-0.9** - Good, minor issues
- **0.6-0.7** - Acceptable, needs improvement
- **Below 0.6** - Significant problems

### Performance Metrics

- **Latency** - Response time in milliseconds
- **Tokens** - Number of tokens used (input + output)
- **Cost** - Estimated cost based on token usage

### Advanced Features

#### Binary Evaluation Mode
For clearer pass/fail decisions, use binary mode:
```bash
acp-evals run accuracy <agent-url> \
  -i "input" -e "expected" \
  --binary --threshold 0.7
```

This converts continuous scores (0-1) into binary pass/fail based on your threshold.

#### Context-Aware Evaluation
Pass additional context for more nuanced evaluation:
```bash
acp-evals run accuracy <agent-url> \
  -i "Explain AI to a 5-year-old" \
  -e "Simple explanation" \
  --context '{"target_audience": "child", "complexity": "simple"}'
```

#### Mock Mode for Development
Test without making LLM API calls:
```bash
acp-evals run accuracy <agent-url> \
  -i "test input" -e "expected" \
  --mock
```

## Common Issues

### "No providers configured"

Make sure your `.env` file exists and contains valid API keys:
```bash
cat .env  # Should show your API keys (be careful not to share these!)
```

### "Failed to connect to agent"

Check that your agent is running:
```bash
curl http://localhost:8000/agents
```

You should see a JSON response listing available agents.

### "Import error: No module named acp_evals"

Install the package:
```bash
pip install acp-evals
# or if installing from source:
pip install -e .
```

## Examples

See the [examples](./examples) directory for:
- Testing different agent types
- Creating custom evaluations
- Batch testing workflows
- CI/CD integration

## Architecture

ACP Evals evaluates agents by:
1. Sending test inputs to your agent
2. Comparing outputs to expected results
3. Using LLMs to assess quality when exact matches aren't appropriate
4. Tracking performance metrics
5. Generating detailed reports

## License

Apache 2.0 - see [LICENSE](./LICENSE)