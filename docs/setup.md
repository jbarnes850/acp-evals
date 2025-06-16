# Setup Guide

This guide will help you get started with ACP Evals, from installation to running your first evaluation.

## Prerequisites

- Python 3.11 or higher
- (Optional) Ollama for local LLM inference
- (Optional) API keys for cloud LLM providers

## Installation

### Basic Installation

```bash
# Install the core package
pip install acp-evals

# Or install from source
git clone https://github.com/jbarnes850/acp-evals
cd acp-evals/python
pip install -e .
```

### With LLM Provider Support

```bash
# For OpenAI support
pip install "acp-evals[openai]"

# For Anthropic support  
pip install "acp-evals[anthropic]"

# For all providers
pip install "acp-evals[all-providers]"

# For development
pip install "acp-evals[dev,all-providers]"
```

## Configuration

### 1. Create Configuration File

Copy the example configuration:

```bash
cp .env.example .env
```

### 2. Configure LLM Providers

Edit `.env` with your preferred provider settings:

#### OpenAI (June 2025 Models)

```bash
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...your-key-here...

# Choose a model (latest as of June 2025)
OPENAI_MODEL=gpt-4.1  # Best overall performance
# OPENAI_MODEL=o3      # Best for complex reasoning
# OPENAI_MODEL=o4-mini # Cost-efficient reasoning
```

#### Anthropic (June 2025 Models)

```bash
# Get your API key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-...your-key-here...

# Choose a model (latest as of June 2025)
ANTHROPIC_MODEL=claude-4-sonnet  # Best balance of performance/cost
# ANTHROPIC_MODEL=claude-4-opus   # Highest quality, longer tasks
```

#### Ollama (Local LLMs)

```bash
# Install Ollama from: https://ollama.ai
# Pull a model: ollama pull qwen3:30b-a3b

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:30b-a3b  # Excellent local model

# Other great options:
# OLLAMA_MODEL=llama3.3:70b  # Meta's latest
# OLLAMA_MODEL=phi-4         # Microsoft's reasoning model
```

#### Default Provider

```bash
# Set your default evaluation provider
EVALUATION_PROVIDER=openai  # Options: openai, anthropic, ollama, mock
```

### 3. Verify Configuration

Check that your providers are configured correctly:

```bash
acp-evals check
```

Expected output:
```
✓ OpenAI provider configured (API key found)
✓ Model 'gpt-4.1' is valid
✓ Connection test successful
```

## Quick Start Examples

### 1. Minimal Evaluation (3 lines)

```python
from acp_evals import evaluate, AccuracyEval

result = evaluate(
    AccuracyEval(agent="http://localhost:8000/agents/my-agent"),
    input="What is the capital of France?",
    expected="Paris"
)
```

### 2. With Rich Output

```python
from acp_evals import AccuracyEval

eval = AccuracyEval(agent="http://localhost:8000/agents/my-agent")
result = await eval.run(
    input="Explain quantum computing",
    expected="A clear explanation covering superposition and entanglement",
    print_results=True  # Shows rich console output
)
```

### 3. Using Different Providers

```python
# Explicitly use OpenAI's latest model
eval = AccuracyEval(
    agent=my_agent,
    judge_model="gpt-4.1"
)

# Use Anthropic's Claude 4
eval = AccuracyEval(
    agent=my_agent,
    judge_model="claude-4-sonnet"
)

# Use local Ollama
eval = AccuracyEval(
    agent=my_agent,
    judge_model="qwen3:30b-a3b"
)

# Use mock mode (no LLM calls)
eval = AccuracyEval(
    agent=my_agent,
    mock_mode=True
)
```

### 4. Batch Evaluation

```python
# Create test data file (test_cases.jsonl)
{"input": "What is 2+2?", "expected": "4"}
{"input": "Capital of Japan?", "expected": "Tokyo"}

# Run batch evaluation
from acp_evals import AccuracyEval

eval = AccuracyEval(agent=my_agent)
results = await eval.run_batch(
    test_data="test_cases.jsonl",
    parallel=True,
    print_results=True
)
```

## Development Setup

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=acp_evals

# Run specific test
pytest tests/test_simple.py
```

### Linting and Type Checking

```bash
# Run linter
ruff check src/

# Run type checker
pyright src/
```

## Common Issues

### "No LLM provider configured"

**Solution**: Make sure you have:
1. Created a `.env` file with your API keys
2. Set `EVALUATION_PROVIDER` to a configured provider
3. Or use `mock_mode=True` for testing without LLMs

### "Model not found" errors

**Solution**: Ensure you're using the correct model names:
- OpenAI: `gpt-4.1`, `o3`, `o4-mini`
- Anthropic: `claude-4-opus`, `claude-4-sonnet`
- Ollama: Model must be pulled first with `ollama pull model-name`

### Timeout errors with Ollama

**Solution**: First run of a model can be slow. Either:
1. Pre-load the model: `ollama run qwen3:30b-a3b`
2. Increase timeout in configuration
3. Use a smaller model like `qwen3:4b`

### High costs with cloud providers

**Solution**: 
1. Use `mock_mode=True` during development
2. Use smaller models (e.g., `o4-mini` instead of `o3`)
3. Monitor costs with the built-in cost tracking
4. Set `COST_ALERT_THRESHOLD` in your `.env`

## Next Steps

- Explore [examples](../examples/) for more use cases
- Read the [Architecture Guide](./architecture.md) to understand the framework
- Check [Provider Setup](./providers.md) for detailed provider configuration
- Join our [Discord](https://discord.gg/NradeA6ZNF) for support

## Getting Help

- [Full Documentation](../README.md)
- [GitHub Discussions](https://github.com/jbarnes850/acp-evals/discussions)
- [Issue Tracker](https://github.com/jbarnes850/acp-evals/issues)