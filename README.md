# ACP Evals

**Simple, Powerful Evaluation Framework for ACP Agents**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![Apache License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<a href="./docs">Documentation</a> • 
<a href="./examples">Examples</a> • 
<a href="#quick-start">Quick Start</a> • 
<a href="./CONTRIBUTING.md">Contributing</a>

---

## Test Your Agent in 3 Lines

```python
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

# Test accuracy
result = await AccuracyEval("http://localhost:8001/agents/my-agent").run(
    input="What is 2+2?", 
    expected="4"
)
print(f"Score: {result.score}")  # Score: 1.0
```

ACP Evals provides three simple evaluators for testing AI agents that follow the [Agent Communication Protocol](https://agentcommunicationprotocol.dev).

## What You Can Evaluate

### 🎯 AccuracyEval
Test if your agent gives correct answers:
```python
eval = AccuracyEval(agent_url, rubric="factual")
result = await eval.run(input="What is the capital of France?", expected="Paris")
```

### ⚡ PerformanceEval
Measure speed and resource usage:
```python
eval = PerformanceEval(agent_url, track_tokens=True)
result = await eval.run(input="Generate a haiku")
```

### 🔧 ReliabilityEval
Check tool usage and error handling:
```python
eval = ReliabilityEval(agent_url)
result = await eval.run(input="Search and calculate", expected_tools=["search", "calculator"])
```

## Features

- **Simple API**: Just 3 evaluators with clear purposes
- **Real LLM Evaluation**: Uses GPT-4, Claude, or Ollama for intelligent assessment
- **Rich Terminal Display**: Beautiful progress bars and formatted results
- **Flexible Agents**: Test ACP agents, Python functions, or any callable
- **Export Results**: Save to JSON for CI/CD integration

## Prerequisites

- Python 3.11 or newer
- An LLM API key (OpenAI, Anthropic, or local Ollama)
- An ACP-compatible agent to test

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

## Quick Start

### 1. Configure Your LLM Provider

```bash
# Copy example configuration
cp .env.example .env

# Add your API key to .env
OPENAI_API_KEY=your-key-here
# or
ANTHROPIC_API_KEY=your-key-here

# Verify setup
acp-evals check
```

### 2. Test an Agent

```python
import asyncio
from acp_evals import AccuracyEval

async def main():
    # Create evaluator
    eval = AccuracyEval("http://localhost:8001/agents/my-agent")
    
    # Run evaluation
    result = await eval.run(
        input="What is the capital of France?",
        expected="Paris",
        print_results=True
    )
    
    print(f"Score: {result.score}")
    print(f"Passed: {result.passed}")

asyncio.run(main())
```

### 3. Use the CLI

```bash
# Run accuracy test
acp-evals run accuracy http://localhost:8001/agents/my-agent \
  -i "What is 2+2?" \
  -e "4"

# Run performance test
acp-evals run performance http://localhost:8001/agents/my-agent \
  -i "Tell me a story"

# Run reliability test
acp-evals run reliability http://localhost:8001/agents/my-agent \
  -i "Search for Python tutorials" \
  --expected-tools search

# Run comprehensive test suite
acp-evals test http://localhost:8001/agents/my-agent
```


## Example Agent

Need an agent to test? Check out the [examples](./examples) directory:

```bash
# Install BeeAI framework
pip install beeai-framework

# Run the example ACP server
python examples/beeai_acp_server.py

# Test it
acp-evals test http://localhost:8001/agents/demo_agent
```

## Detailed Examples

### Accuracy Evaluation with Rich Output

```bash
acp-evals run accuracy http://localhost:8001/agents/my-agent \
  -i "What is 2+2?" \
  -e "4"
```

Output:
```
Running Accuracy Evaluation
Agent: http://localhost:8001/agents/my-agent
Input: What is 2+2?

⠋ Running agent...
✓ Agent response received
⠋ Evaluating response...
✓ Evaluation complete

Evaluation Result - Accuracy Evaluation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score: ████████████████████ 1.00
Status: PASS

Feedback:
The response correctly answers the mathematical question.

Criteria Scores:
  accuracy: ████████████ 1.00
  completeness: ████████████ 1.00
  relevance: ████████████ 1.00
```

### Batch Evaluation

```python
import asyncio
from acp_evals import AccuracyEval

async def main():
    eval = AccuracyEval("http://localhost:8001/agents/my-agent")
    
    test_cases = [
        {"input": "What is 2+2?", "expected": "4"},
        {"input": "Capital of France?", "expected": "Paris"},
        {"input": "Largest planet?", "expected": "Jupiter"}
    ]
    
    results = await eval.run_batch(test_cases, print_results=True)
    print(f"Pass rate: {results.pass_rate}%")

asyncio.run(main())
```

### Available CLI Commands

```bash
# Check configuration
acp-evals check

# List available rubrics
acp-evals list-rubrics

# Discover agents
acp-evals discover

# Generate evaluation template
acp-evals init my_eval.py --type accuracy

# Run evaluations
acp-evals run accuracy <agent> -i <input> -e <expected>
acp-evals run performance <agent> -i <input>
acp-evals run reliability <agent> -i <input> --expected-tools <tool1> <tool2>

# Quick test
acp-evals test <agent>
```

## Understanding Results

### Scores
- **1.0** - Perfect match
- **0.7+** - Good (default pass threshold)
- **<0.7** - Needs improvement

### Performance Metrics
- **Latency** - Response time in milliseconds
- **Tokens** - Input + output token count
- **Cost** - Estimated API cost

## Common Issues

**"No providers configured"**
- Ensure `.env` file has valid API keys
- Run `acp-evals check` to verify

**"Failed to connect to agent"**
- Check agent is running: `curl http://localhost:8001/agents`
- Verify the agent URL is correct

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Examples

Check out the [examples](./examples) directory for:
- BeeAI ACP server example
- Simple mock server
- Custom evaluation scripts

## License

Apache 2.0 - see [LICENSE](./LICENSE)