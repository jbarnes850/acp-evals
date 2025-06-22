# Setup Guide

This guide will help you get started with ACP Evals. The framework provides production-grade evaluation with LLM-powered assessment.

## Prerequisites

- Python 3.11 or higher
- LLM API key (OpenAI, Anthropic, or local Ollama)
- Agent to evaluate (ACP-compatible or Python function)

## Installation

```bash
# Install from PyPI
pip install acp-evals

# Or install from source
git clone https://github.com/jbarnes850/acp-evals
cd acp-evals
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# OpenAI Configuration (recommended)
OPENAI_API_KEY=sk-...your-key-here...
OPENAI_MODEL=gpt-4.1

# Anthropic Configuration (alternative)
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Ollama Configuration (local LLMs)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# Default Provider
EVALUATION_PROVIDER=openai
```

### Verify Setup

```bash
acp-evals check
```

Expected output:
```
ACP Evals Provider Configuration Check

Found .env file at: /path/to/.env
                      Provider Status                       
╭───────────┬────────────┬────────────────────────┬────────╮
│ Provider  │ Configured │ Model                  │ Status │
├───────────┼────────────┼────────────────────────┼────────┤
│ Openai    │ Yes        │ gpt-4.1                │ —      │
│ Anthropic │ Yes        │ claude-sonnet-4-20250514│ —      │
│ Ollama    │ Yes        │ qwen3:8b               │ —      │
╰───────────┴────────────┴────────────────────────┴────────╯

All providers configured!
```

## Quick Start

### 1. Basic Evaluation

```python
from acp_evals import AccuracyEval

eval = AccuracyEval("http://localhost:8001/agents/my-agent")
result = await eval.run(
    input="What is 2+2?",
    expected="4"
)
print(f"Score: {result.score}")  # Score: 1.000
```

### 2. CLI Evaluation

```bash
# Accuracy test
acp-evals run accuracy my_agent.py:agent_function -i "What is 2+2?" -e "4"

# Performance test
acp-evals run performance my_agent.py:agent_function -i "Complex task" --track-latency

# Reliability test
acp-evals run reliability my_agent.py:agent_function -i "Use tools" --expected-tools search
```

### 3. Batch Evaluation

```python
test_cases = [
    {"input": "What is 2+2?", "expected": "4"},
    {"input": "Capital of France?", "expected": "Paris"},
    {"input": "Largest planet?", "expected": "Jupiter"}
]

eval = AccuracyEval("http://localhost:8001/agents/my-agent")
results = await eval.run_batch(test_cases, print_results=True)
print(f"Pass rate: {results.pass_rate}%")
```

## Agent Input Formats

ACP Evals supports multiple agent formats:

```bash
# ACP URL
acp-evals run accuracy http://localhost:8001/agents/my-agent -i "test" -e "result"

# Python file with function
acp-evals run accuracy agent.py:function_name -i "test" -e "result"

# Python module
acp-evals run accuracy mymodule.agent_function -i "test" -e "result"
```

## Evaluation Types

### AccuracyEval
LLM-powered evaluation with detailed feedback:
```python
eval = AccuracyEval(agent, rubric="factual")  # or research_quality, code_quality
result = await eval.run(input="question", expected="answer")
```

### PerformanceEval
Measure response latency and efficiency:
```python
eval = PerformanceEval(agent, track_tokens=True, track_latency=True)
result = await eval.run(input="task")
```

### ReliabilityEval
Assess consistency and tool usage:
```python
eval = ReliabilityEval(agent)
result = await eval.run(input="task", expected_tools=["search", "calculate"])
```

## Understanding Results

### Scores
- **1.000** - Perfect response quality (3-decimal precision)
- **0.700+** - Good quality (default pass threshold)
- **<0.700** - Needs improvement

### Enhanced LLM Evaluation Display
All accuracy evaluations use real LLM assessment with complete transparency:
- Full input, expected output, and actual agent output (no truncation)
- Detailed score breakdown by evaluation criteria
- Complete LLM judge reasoning explaining the score
- Performance analysis with user experience context
- No fallbacks to simple text matching

## Common Issues

### "No providers configured"
```bash
echo "OPENAI_API_KEY=your-key" > .env
acp-evals check
```

### "Failed to connect to agent"
```bash
# Check ACP agent is running
curl http://localhost:8001/agents

# Use Python function instead
acp-evals run accuracy my_agent.py:my_function -i "test" -e "result"
```

### "LLM evaluation failed"
Ensure valid API key and network connectivity. Framework requires real LLM evaluation.

## Provider Setup

### OpenAI
Get API key from: https://platform.openai.com/api-keys
```bash
OPENAI_API_KEY=sk-...your-key-here...
OPENAI_MODEL=gpt-4.1
```

### Anthropic
Get API key from: https://console.anthropic.com/
```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### Ollama (Local)
Install from: https://ollama.ai
```bash
ollama pull qwen3:8b
ollama serve

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

## Next Steps

- Review [CLI Commands](./cli-reference.md) for complete command reference
- Check [Examples](../examples/) for implementation patterns
- Read [API Reference](./api-reference.md) for programmatic usage