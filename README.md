# ACP Evals

**Production-ready evaluation framework for multi-agent systems in the ACP/BeeAI ecosystem**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

ACP Evals is an evaluation framework for multi-agent systems built on the Agent Communication Protocol. Evaluation frameworks measure the quality, performance, and safety of AI agent outputs through automated scoring methods. In production agent systems, these measurements become critical for ensuring reliability, detecting regressions, and optimizing performance at scale.

ACP Evals specializes in the unique challenges of coordinated agent systems. The framework measures how well agents collaborate, preserve information across handoffs, and maintain workflow coherence under production conditions.

## Getting Started

The quickest way to understand ACP Evals is through the basic evaluation workflow. Install the framework, configure your LLM provider, and run your first evaluation to establish the fundamental pattern.

### Installation

```bash
# Basic installation
pip install acp-evals

# Development installation with all providers
cd python/
pip install -e ".[dev,all-providers]"
```

### Provider Configuration

Create a `.env` file in your project root:

```bash
# Copy the example configuration
cp python/.env.example python/.env

# Add your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

### Basic Evaluation

```python
from acp_evals import evaluate, AccuracyEval

# Evaluate any ACP agent with three lines
result = evaluate(
    AccuracyEval(agent="http://localhost:8000/agents/my-agent"),
    input="What is the capital of France?",
    expected="Paris"
)
print(f"Score: {result.score:.2f}, Cost: ${result.cost:.4f}")
```

```python
# Works with any provider out of the box
eval = AccuracyEval(agent=my_agent, provider="anthropic")  # or "openai", "ollama"

# Multi-agent coordination (unique to ACP Evals)
from acp_evals import HandoffEval
result = HandoffEval(agents={"researcher": url1, "writer": url2}).run(task)
```

This pattern extends to all evaluation types. Replace `AccuracyEval` with `PerformanceEval`, `SafetyEval`, or `ReliabilityEval` to measure different aspects of agent behavior.

## System Architecture

```mermaid
graph TB
    A[ACP Agent] --> B[ACP Evals Framework]
    
    B --> C[Developer API<br/>evaluate Accuracy and Performance]
    B --> D[Multi-Agent Evaluators<br/> Communication Patterns and Framework Integrity]
    B --> E[Production Features<br/>Trace Recycling and Continuous Evaluation]
    
    F[LLM Providers<br/>OpenAI Anthropic Ollama] --> B
    
    B --> G[Results<br/>Eval Performance and Costs Analytics]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style G fill:#e0f2f1
```

## Core Evaluation Capabilities

> **Quick Start**: Start with 3-line evaluations, scale to enterprise multi-agent benchmarks

### **Quality & Performance Evaluators**
- **[AccuracyEval](./python/src/acp_evals/evaluators/accuracy.py)**: LLM-as-judge with customizable rubrics (factual, research, code quality)
- **[GroundednessEvaluator](./python/src/acp_evals/evaluators/groundedness.py)**: Context-grounded response validation
- **[RetrievalEvaluator](./python/src/acp_evals/evaluators/retrieval.py)**: Information retrieval quality assessment  
- **[DocumentRetrievalEvaluator](./python/src/acp_evals/evaluators/document_retrieval.py)**: Full IR metrics (precision, recall, NDCG, MAP, MRR)
- **[PerformanceEval](./python/src/acp_evals/evaluators/performance.py)**: Token usage, latency, and cost tracking across providers

### **Multi-Agent Specialized Metrics**
> **Industry First**: An evaluation framework built specifically for multi-agent coordination

- **[Handoff Quality](./python/src/acp_evals/metrics/handoff_quality.py)**: Information preservation across agent transitions
- **[Coordination Patterns](./python/src/acp_evals/patterns/)**: [LinearPattern](./python/src/acp_evals/patterns/linear.py), [SupervisorPattern](./python/src/acp_evals/patterns/supervisor.py), [SwarmPattern](./python/src/acp_evals/patterns/swarm.py) evaluation
- **Context Maintenance**: Cross-agent context analysis and noise detection
- **Decision Preservation**: Agent-to-agent decision quality tracking

### **Risk & Safety Evaluators**
- **[SafetyEval](./python/src/acp_evals/evaluators/safety.py)**: Composite safety and bias detection
- **[Adversarial Testing](./python/src/acp_evals/benchmarks/datasets/adversarial_datasets.py)**: Real-world attack pattern resistance (prompt injection, jailbreaks)
- **[ReliabilityEval](./python/src/acp_evals/evaluators/reliability.py)**: Tool usage validation and error handling assessment

## Quick Start

> **⚡ Zero to Evaluation**: Get comprehensive agent metrics in under 60 seconds

```python
from acp_evals import evaluate, AccuracyEval

# Evaluate any ACP agent in 3 lines
result = evaluate(
    AccuracyEval(agent="http://localhost:8000/agents/research-agent"),
    input="What are the latest developments in quantum computing?",
    expected="Recent quantum computing advances include..."
)
print(f"Score: {result.score}, Cost: ${result.cost}")
```

## Multi-Agent Evaluation

> **Coordination Testing**: Measure how well agents work together, not just individually

```python
from acp_evals.benchmarks import HandoffBenchmark
from acp_evals.patterns import LinearPattern

# Evaluate agent coordination
benchmark = HandoffBenchmark(
    pattern=LinearPattern(["researcher", "analyzer", "synthesizer"]),
    tasks="research_quality",
    endpoint="http://localhost:8000"
)

results = await benchmark.run_batch(
    test_data="multi_agent_tasks.jsonl",
    parallel=True,
    export="coordination_results.json"
)
```

## Advanced Features

### **Production Integration**
> Built for real-world deployment monitoring

- **[Trace Recycling](./python/src/acp_evals/benchmarks/datasets/trace_recycler.py)**: Convert production telemetry to evaluation datasets ([example](./python/examples/11_trace_recycling_example.py))
- **[Continuous Evaluation](./python/src/acp_evals/evaluation/continuous.py)**: Automated regression detection and baseline tracking ([docs](./python/docs/continuous-ai.md))
- **[OpenTelemetry Export](./python/src/acp_evals/telemetry/otel_exporter.py)**: Real-time metrics to Jaeger, Phoenix, and observability platforms
- **Cost Optimization**: Multi-provider cost comparison and budget alerts

### **Adversarial & Robustness Testing**
> Test against real-world attack patterns, not academic examples

- **[Real-World Attack Patterns](./python/src/acp_evals/benchmarks/datasets/adversarial_datasets.py)**: Prompt injection, context manipulation, data extraction ([example](./python/examples/07_adversarial_testing.py))
- **[Edge Case Generation](./python/src/acp_evals/evaluation/simulator.py)**: Synthetic adversarial scenario creation

### **Dataset & Benchmarking**
> Gold standard datasets to custom synthetic data

- **[Gold Standard Datasets](./python/src/acp_evals/benchmarks/datasets/gold_standard_datasets.py)**: Production-realistic multi-step agent tasks
- **[External Integration](./python/src/acp_evals/benchmarks/datasets/)**: [TRAIL](./python/src/acp_evals/benchmarks/datasets/trail_integration.py), GAIA, SWE-Bench benchmark support
- **[Custom Dataset Loaders](./python/src/acp_evals/benchmarks/datasets/dataset_loader.py)**: Flexible evaluation data management
- **[Synthetic Data Generation](./python/examples/13_synthetic_data_generation_and_storage.py)**: Automated test case creation

## Installation & Setup

```bash
# Basic installation
pip install acp-evals

# Development installation
cd python/
pip install -e .
```

### Provider Configuration
```bash
# Copy environment template
cp python/.env.example python/.env

# Configure API keys in .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

## Supported Providers & Models

> ** Provider Flexibility**: Test locally with Ollama or scale with cloud providers

| Provider | Models | Cost Tracking |
|----------|--------|---------------|
| **OpenAI** | GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, o4-mini | ✅ |
| **Anthropic** | Claude-4-Opus, Claude-4-Sonnet | ✅ |
| **Ollama** | granite3.3:8b, qwen3:30b-a3b, custom | ✅ |
| **Mock Mode** | Simulated responses | ✅ |

### **Native ACP/BeeAI Integration**
> **🔗 Ecosystem Native**: Purpose-built for the ACP/BeeAI stack

- **[ACP Message Handling](./python/src/acp_evals/client/acp_client.py)**: Native support for ACP communication patterns ([example](./python/examples/09_real_acp_agents.py))
- **[BeeAI Agent Instances](./python/examples/10_acp_agent_discovery.py)**: Direct integration with BeeAI Framework agents
- **Workflow Evaluation**: Built-in support for BeeAI multi-agent workflows
- **Event Stream Analysis**: Real-time evaluation of agent interactions


## Documentation & Examples


| Resource | Description |
|----------|-------------|
| 📚 [Architecture Guide](./python/docs/architecture.md) | Framework design and components |
| 🚀 [Setup Guide](./python/docs/setup.md) | Installation and configuration |
| 🔌 [Provider Setup](./python/docs/providers.md) | LLM provider configuration |
| 💡 [Examples](./python/examples/) | 13 comprehensive usage examples |

### **Quick Start Examples**

**Essential (Start Here):**
- **[00_minimal_example.py](./python/examples/00_minimal_example.py)**: 3-line agent evaluation
- **[01_quickstart_accuracy.py](./python/examples/01_quickstart_accuracy.py)**: Basic accuracy assessment
- **[02_multi_agent_evaluation.py](./python/examples/02_multi_agent_evaluation.py)**: Agent coordination testing

**Production Integration:**
- **[04_continuous_evaluation.py](./python/examples/04_continuous_evaluation.py)**: CI/CD monitoring pipeline
- **[12_end_to_end_trace_pipeline.py](./python/examples/12_end_to_end_trace_pipeline.py)**: Production trace recycling
- **[09_real_acp_agents.py](./python/examples/09_real_acp_agents.py)**: Live ACP agent integration

**Advanced:**
- **[07_adversarial_testing.py](./python/examples/07_adversarial_testing.py)**: Security robustness evaluation
- **[13_synthetic_data_generation.py](./python/examples/13_synthetic_data_generation_and_storage.py)**: Custom dataset creation

## Batch Evaluation and Automation

Production agent systems require automated evaluation workflows that can process multiple test cases, generate comprehensive reports, and integrate with continuous integration systems.

### Batch Processing

```python
# Evaluate multiple test cases from a dataset
results = AccuracyEval(agent=my_agent).run_batch(
    test_data="test_cases.jsonl",
    parallel=True,
    progress=True,
    export="results.json"
)

print(f"Pass rate: {results.pass_rate}%, Average score: {results.avg_score:.2f}")
```

The JSONL format expects each line to contain a JSON object with `input` and `expected` fields:

```jsonl
{"input": "What is machine learning?", "expected": "Machine learning is a method of data analysis..."}
{"input": "Explain neural networks", "expected": "Neural networks are computing systems inspired by..."}
```

### CI/CD Integration

```python
# Integrate with pytest or other testing frameworks
def test_agent_accuracy():
    eval = AccuracyEval(agent=my_agent, mock_mode=CI_ENV)
    result = eval.run(
        input="Test question for CI",
        expected="Expected answer"
    )
    assert result.score > 0.8, f"Agent scored {result.score}, below threshold"
```

## Understanding Results

Evaluation results follow a consistent structure across all evaluator types. Understanding result interpretation enables effective debugging and optimization workflows.

### Result Structure

```python
# All evaluators return results with this structure
result = eval.run(input="test", expected="expected")

print(f"Score: {result.score}")           # Float 0.0-1.0
print(f"Passed: {result.passed}")         # Boolean pass/fail
print(f"Cost: ${result.cost:.4f}")        # USD cost
print(f"Tokens: {result.tokens}")         # Token usage breakdown
print(f"Latency: {result.latency_ms}ms")  # Response time
print(f"Details: {result.details}")       # Evaluator-specific metrics
```

### Debugging Failed Evaluations

When evaluations fail or score lower than expected, the `details` field provides specific feedback:

```python
result = AccuracyEval(agent=my_agent).run(
    input="Complex technical question",
    expected="Technical answer"
)

if result.score < 0.7:
    print("Evaluation feedback:")
    print(result.details.get("judge_reasoning", "No reasoning provided"))
    print(f"Specific issues: {result.details.get('issues', [])}")
```

## Troubleshooting

Common issues and solutions for evaluation setup and execution.

### Provider Configuration Issues

If evaluations fail with authentication errors, verify your provider configuration:

```python
# Test provider connectivity
from acp_evals.providers.factory import ProviderFactory

provider = ProviderFactory.get_provider("openai")  # or "anthropic", "ollama"
print(f"Provider status: {provider.health_check()}")
```

### Agent Connection Problems

For ACP agent connectivity issues:

```python
# Test agent health before evaluation
import httpx

async def test_agent_health(agent_url):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{agent_url}/health")
        return response.status_code == 200

# Use in evaluations
if await test_agent_health("http://localhost:8000/agents/my-agent"):
    result = evaluate(AccuracyEval(agent=agent_url), input, expected)
```

### Performance Optimization

For large-scale evaluations:

```python
# Use batch processing with parallelization
results = AccuracyEval(agent=my_agent).run_batch(
    test_data="large_dataset.jsonl",
    parallel=True,
    batch_size=10,  # Process 10 at a time
    max_workers=4   # Limit concurrent evaluations
)
```

## Project Structure

```bash
acp-evals/
├── python/                          # Core Python implementation
│   ├── src/acp_evals/
│   │   ├── api.py                   # Simple developer API
│   │   ├── evaluators/              # Built-in evaluators
│   │   │   ├── accuracy.py          # LLM-as-judge evaluation
│   │   │   ├── groundedness.py      # Context grounding assessment
│   │   │   ├── retrieval.py         # Information retrieval metrics
│   │   │   └── safety.py            # Safety and bias detection
│   │   ├── benchmarks/              # Multi-agent benchmarking
│   │   │   ├── datasets/            # Gold standard & adversarial data
│   │   │   │   ├── gold_standard_datasets.py
│   │   │   │   ├── adversarial_datasets.py
│   │   │   │   └── trace_recycler.py
│   │   │   └── multi_agent/         # Agent coordination benchmarks
│   │   ├── patterns/                # Agent architecture patterns
│   │   │   ├── linear.py            # Sequential execution
│   │   │   ├── supervisor.py        # Centralized coordination
│   │   │   └── swarm.py             # Distributed collaboration
│   │   ├── providers/               # LLM provider abstractions
│   │   │   ├── openai.py            # OpenAI integration
│   │   │   ├── anthropic.py         # Anthropic integration
│   │   │   └── ollama.py            # Local model support
│   │   ├── evaluation/              # Advanced evaluation features
│   │   │   ├── continuous.py        # Continuous eval pipeline
│   │   │   └── simulator.py         # Synthetic data generation
│   │   ├── telemetry/               # Observability integration
│   │   │   └── otel_exporter.py     # OpenTelemetry export
│   │   └── cli.py                   # Command-line interface
│   ├── tests/                       # Comprehensive test suite
│   ├── examples/                    # Usage examples (13 files)
│   └── docs/                        # Architecture & setup guides
```

## Contributing

The framework is designed for extensibility:

- **New Evaluators**: Add custom evaluation logic in `evaluators/`
- **Provider Support**: Extend `providers/` for new LLM providers  
- **Coordination Patterns**: Implement new multi-agent patterns in `patterns/`
- **Dataset Integration**: Add external benchmarks in `benchmarks/datasets/`

See our [contribution guide](./python/CONTRIBUTING.md) for detailed guidance.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

Part of the [BeeAI](https://github.com/i-am-bee) project, an initiative of the [Linux Foundation AI & Data](https://lfaidata.foundation/)