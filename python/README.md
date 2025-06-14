# ACP Evals

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![BeeAI Framework](https://img.shields.io/badge/BeeAI-Framework-yellow.svg)](https://github.com/i-am-bee/beeai-framework)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Production-ready evaluation framework for agents in the ACP/BeeAI ecosystem**

[Documentation](./docs) • [Examples](./examples) • [API Reference](#api-reference) • [Contributing](#contributing)

</div>

## Overview

ACP Evals is a comprehensive evaluation framework designed specifically for the Agent Communication Protocol (ACP) ecosystem. It provides developers with powerful tools to measure, benchmark, and improve agent performance with a focus on multi-agent systems, real-world production metrics, and developer experience.

### Key Features

- 🚀 **Zero to evaluation in < 5 lines of code**
- 🤖 **Multi-agent focused** - Specialized metrics for agent coordination and handoffs
- 🔌 **Multiple LLM providers** - OpenAI, Anthropic, Azure, Ollama, or mock mode
- 📊 **Production metrics** - Token usage, costs, latency, and context efficiency
- 🎯 **Built-in evaluators** - Accuracy, performance, reliability, and safety
- 🎨 **Beautiful output** - Rich console formatting with progress tracking
- 🧪 **Flexible testing** - Single runs, batch evaluation, and CI/CD integration

## Quick Start

### Installation

```bash
# Basic installation
pip install acp-evals

# With specific LLM provider support
pip install "acp-evals[openai]"        # OpenAI support
pip install "acp-evals[anthropic]"     # Anthropic support
pip install "acp-evals[all-providers]" # All providers
```

### Basic Usage

```python
from acp_evals import evaluate, AccuracyEval

# Evaluate any agent with just 3 lines
result = evaluate(
    AccuracyEval(agent="http://localhost:8000/agents/my-agent"),
    input="What is the capital of France?",
    expected="Paris"
)
print(f"Score: {result.score:.2f}")  # Score: 0.95
```

### Multi-Agent Evaluation

```python
from acp_evals import PerformanceEval, HandoffEval

# Evaluate agent coordination
handoff_eval = HandoffEval(
    agents={
        "researcher": "http://localhost:8000/agents/researcher",
        "writer": "http://localhost:8000/agents/writer"
    }
)

result = handoff_eval.run(
    task="Write a report on quantum computing",
    expected_handoffs=["researcher->writer"],
    measure_information_preservation=True,
    print_results=True
)
```

## Configuration

### Environment Setup

Create a `.env` file in your project root:

```bash
# Copy the example configuration
cp .env.example .env

# Edit with your API keys
nano .env
```

See [.env.example](./.env.example) for all configuration options.

### LLM Provider Configuration

ACP Evals supports multiple LLM providers for evaluation:

```python
# Auto-detect from environment
eval = AccuracyEval(agent=my_agent)  # Uses EVALUATION_PROVIDER from .env

# Explicit provider
eval = AccuracyEval(
    agent=my_agent,
    judge_model="gpt-4",  # or "claude-3", "llama3", etc.
)

# Mock mode for testing (no API calls)
eval = AccuracyEval(agent=my_agent, mock_mode=True)
```

## Available Evaluators

### 1. AccuracyEval
Measures response quality using LLM-as-judge with customizable rubrics.

```python
eval = AccuracyEval(
    agent=my_agent,
    rubric="research_quality"  # or "factual", "code_quality", or custom
)
```

### 2. PerformanceEval
Tracks token usage, costs, latency, and resource utilization.

```python
perf = PerformanceEval(agent=my_agent)
result = perf.run(
    input="Analyze this document...",
    track_tokens=True,
    track_latency=True,
    track_memory=True
)
print(f"Tokens: {result.tokens}, Cost: ${result.cost:.4f}")
```

### 3. ReliabilityEval
Validates tool usage and error handling.

```python
reliability = ReliabilityEval(agent=my_agent)
result = reliability.run(
    input="Search and summarize recent AI papers",
    expected_tools=["search", "summarize"],
    test_error_handling=True
)
```

### 4. SafetyEval
Composite evaluator for content safety and bias detection.

```python
safety = SafetyEval(
    agent=my_agent,
    thresholds={"harmful_content": 0.1, "bias": 0.1}
)
```

## Architecture

ACP Evals is built with a layered architecture optimized for both simplicity and power:

```
acp_evals/
├── simple.py          # High-level API (start here)
├── providers/         # LLM provider integrations
├── evaluators/        # Core evaluation logic
│   ├── llm_judge.py   # LLM-as-judge implementation
│   └── base.py        # Evaluator interface
├── metrics/           # Performance and quality metrics
├── benchmarks/        # Multi-agent benchmarking
└── patterns/          # Agent architecture patterns
```

See [Architecture Guide](./docs/architecture.md) for detailed design documentation.

## Advanced Features

### TRAIL-Level Semantic Evaluation & Trace Recycling

ACP Evals achieves **TRAIL dataset parity** with production-realistic multi-step evaluation using LLM-based semantic assessment and adaptive quality thresholds. Unlike keyword matching, our semantic evaluator understands true meaning and reasoning quality.

#### Semantic Evaluation with GPT-4.1-nano

```python
from acp_evals.evaluators.semantic_evaluator import SemanticEvaluator

# Initialize semantic evaluator
evaluator = SemanticEvaluator(model="gpt-4.1-nano")

# Evaluate with production-realistic criteria
result = await evaluator.evaluate_semantic(
    task="Debug this production microservice showing race conditions...",
    response=agent_response,
    criteria={
        "identifies_race_condition": {"weight": 0.4, "description": "Recognizes concurrent access issues"},
        "proposes_locking_mechanism": {"weight": 0.3, "description": "Suggests atomic operations"},
        "addresses_error_handling": {"weight": 0.2, "description": "Improves exception handling"},
        "considers_scalability": {"weight": 0.1, "description": "Mentions performance impact"}
    },
    expected_tools=["code_analyzer", "database_profiler", "transaction_manager"],
    pass_threshold=0.75
)
```

#### Production-Realistic Datasets

Our enhanced datasets include real-world scenarios from:
- **High-traffic payment processing** with race condition debugging
- **Enterprise customer escalations** with CEO involvement
- **Security incident response** for credential stuffing attacks
- **Distributed system deadlocks** during Black Friday traffic
- **ML data pipeline failures** affecting model performance

#### Trace Recycling with Adaptive Thresholds

```python
from acp_evals.benchmarks.datasets.trace_recycler import TraceRecycler

# Initialize trace recycler
recycler = TraceRecycler()

# Feed production traces (OpenTelemetry format)
recycler.ingest_trace(otel_trace)

# Generate synthetic tests with adaptive threshold (default)
synthetic_tests = recycler.generate_evaluation_dataset(
    count=50,
    adaptive_threshold=True  # Automatically adjusts 0.2-0.5 based on data
)

# Export synthetic datasets to disk for reuse
recycler.export_synthetic_dataset(
    output_path="datasets/production_tests.jsonl",
    count=100,
    format="jsonl"  # Options: "jsonl", "json", "csv"
)
```

**TRAIL Parity Features:**
- **Multi-step reasoning validation**: Tests systematic problem-solving approaches
- **Tool usage verification**: Validates appropriate tool selection and sequencing  
- **Production edge cases**: Memory leaks, cascading failures, data corruption
- **Semantic understanding**: GPT-4.1-nano replaces keyword matching
- **Adaptive quality thresholds**: Data-driven thresholds (0.2-0.5) instead of theoretical 0.7+
- **Trace-based evaluation**: Validates reasoning steps, not just final outputs

**Quality Improvements:**
- **5x complexity increase**: From "What is 2+2?" to "Debug production race conditions"
- **Production realism**: Real enterprise scenarios with time pressure and stakeholder involvement
- **Edge case coverage**: Subtle bugs that only appear under production load
- **Multi-step validation**: Tests systematic approach, not just correctness

### Batch Evaluation

```python
# Evaluate multiple test cases
results = AccuracyEval(agent=my_agent).run_batch(
    test_data="test_cases.jsonl",
    parallel=True,
    progress=True,
    export="results.json"
)
print(f"Pass rate: {results.pass_rate}%")
```

### CI/CD Integration

```python
# In your test suite
def test_agent_accuracy():
    eval = AccuracyEval(agent=my_agent, mock_mode=CI_ENV)
    result = eval.run(
        input="Test question",
        expected="Expected answer"
    )
    assert result.score > 0.8
```

### Custom Rubrics

```python
custom_rubric = {
    "technical_accuracy": {
        "weight": 0.4,
        "criteria": "Response uses correct technical terminology"
    },
    "code_correctness": {
        "weight": 0.6,
        "criteria": "Code examples are syntactically correct and runnable"
    }
}

eval = AccuracyEval(agent=my_agent, rubric=custom_rubric)
```

## Integration with ACP/BeeAI

ACP Evals is designed as a core component of the BeeAI ecosystem:

- **ACP Protocol**: Native support for ACP agent communication
- **BeeAI Framework**: Seamless integration with BeeAI workflows
- **BeeAI Platform**: Publish evaluation results to the platform catalog

```python
# Evaluate BeeAI framework agents
from beeai_framework import ReActAgent
from acp_evals import AccuracyEval

agent = ReActAgent(name="research-assistant")
eval = AccuracyEval(agent=agent)  # Direct agent instance support
```

## Examples

Explore our [examples directory](./examples) for:
- [Quickstart](./examples/quickstart.py) - Minimal evaluation example
- [Research Agent](./examples/research_agent_eval.py) - Deep research evaluation
- [Multi-Agent](./examples/multi_agent_eval.py) - Agent coordination testing
- [Tool Agent](./examples/tool_agent_eval.py) - Tool usage validation

## API Reference

### Core Classes

- `AccuracyEval` - LLM-based quality evaluation
- `PerformanceEval` - Resource and efficiency metrics
- `ReliabilityEval` - Robustness and tool usage
- `SafetyEval` - Content safety composite
- `EvalResult` - Single evaluation result
- `BatchResult` - Multiple evaluation results

### Utility Functions

- `evaluate()` - Synchronous evaluation helper
- `simulate()` - Generate synthetic test data

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/i-am-bee/acp-evals
cd acp-evals/python

# Install in development mode
pip install -e ".[dev,all-providers]"

# Run tests
pytest

# Run linting
ruff check src/
```

## Roadmap

- [ ] Additional safety evaluators (violence, hate speech detection)
- [ ] Groundedness and completeness metrics
- [ ] Advanced conversation simulation
- [ ] Integration with BeeAI Platform for result visualization
- [ ] Support for more LLM providers

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.

## Support

- 📚 [Documentation](./docs)
- 💬 [GitHub Discussions](https://github.com/i-am-bee/acp-evals/discussions)
- 🐛 [Issue Tracker](https://github.com/i-am-bee/acp-evals/issues)
- 💬 [Discord Community](https://discord.gg/NradeA6ZNF)

---

Part of the [BeeAI](https://github.com/i-am-bee) project, an initiative of the [Linux Foundation AI & Data](https://lfaidata.foundation/).