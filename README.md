# ACP Evals

**Production-ready evaluation framework for multi-agent systems in the ACP/BeeAI ecosystem**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

ACP Evals bridges the evaluation gap in the BeeAI ecosystem. While [BeeAI Framework](https://github.com/i-am-bee/beeai-framework) enables building production-ready multi-agent systems and [ACP](https://github.com/i-am-bee/acp) provides agent communication protocols, comprehensive evaluation capabilities have been missing—until now.

**The Problem**: Existing evaluation frameworks focus on single agents with accuracy-first metrics, leaving multi-agent coordination, production token efficiency, and adversarial robustness unmeasured.

**The Solution**: ACP Evals provides token-first, multi-agent specialized evaluation with production telemetry integration, designed specifically for the evolving agent ecosystem.

## Core Evaluation Capabilities

### **Quality & Performance Evaluators**
- **AccuracyEval**: LLM-as-judge with customizable rubrics (factual, research, code quality)
- **GroundednessEvaluator**: Context-grounded response validation
- **RetrievalEvaluator**: Information retrieval quality assessment  
- **DocumentRetrievalEvaluator**: Full IR metrics (precision, recall, NDCG, MAP, MRR)
- **PerformanceEval**: Token usage, latency, and cost tracking across providers

### **Multi-Agent Specialized Metrics**
- **Handoff Quality**: Information preservation across agent transitions
- **Coordination Patterns**: LinearPattern, SupervisorPattern, SwarmPattern evaluation
- **Context Maintenance**: Cross-agent context analysis and noise detection
- **Decision Preservation**: Agent-to-agent decision quality tracking

### **Risk & Safety Evaluators**
- **SafetyEval**: Composite safety and bias detection
- **Adversarial Testing**: Real-world attack pattern resistance (prompt injection, jailbreaks)
- **Content Safety**: Multi-layer safety evaluation with severity classification
- **ReliabilityEval**: Tool usage validation and error handling assessment

## Quick Start

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
- **Trace Recycling**: Convert production telemetry to evaluation datasets
- **Continuous Evaluation**: Automated regression detection and baseline tracking  
- **OpenTelemetry Export**: Real-time metrics to Jaeger, Phoenix, and observability platforms
- **Cost Optimization**: Multi-provider cost comparison and budget alerts

### **Adversarial & Robustness Testing**
- **Real-World Attack Patterns**: Prompt injection, context manipulation, data extraction
- **Multi-Turn Adversarial**: Complex attack chain resistance testing
- **Edge Case Generation**: Synthetic adversarial scenario creation
- **Defense Depth Analysis**: Multi-layer security assessment

### **Dataset & Benchmarking**
- **Gold Standard Datasets**: Production-realistic multi-step agent tasks
- **External Integration**: TRAIL, GAIA, SWE-Bench benchmark support
- **Custom Dataset Loaders**: Flexible evaluation data management
- **Synthetic Data Generation**: Automated test case creation

## Installation & Setup

```bash
# Basic installation
pip install acp-evals

# With specific providers
pip install "acp-evals[openai]"
pip install "acp-evals[anthropic]" 
pip install "acp-evals[all-providers]"

# Development installation
cd python/
pip install -e ".[dev,all-providers]"
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

| Provider | Models | Local | Cost Tracking |
|----------|--------|-------|---------------|
| **OpenAI** | GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, o4-mini | ❌ | ✅ |
| **Anthropic** | Claude-4-Opus, Claude-4-Sonnet | ❌ | ✅ |
| **Ollama** | granite3.3:8b, qwen3:30b-a3b, custom | ✅ | ✅ |
| **Mock Mode** | Simulated responses | ✅ | ✅ |

## Architecture & Integration

### **Progressive Disclosure Design**
```python
# Beginner: 3-line evaluation
result = evaluate(AccuracyEval(agent=agent), input, expected)

# Intermediate: Custom rubrics and batch processing  
eval = AccuracyEval(agent=agent, rubric="research_quality")
results = await eval.run_batch("tasks.jsonl", parallel=True)

# Expert: Multi-agent coordination benchmarks
benchmark = HandoffBenchmark(pattern=SupervisorPattern(...))
analysis = await benchmark.comprehensive_analysis()
```

### **Native ACP/BeeAI Integration**
- **ACP Message Handling**: Native support for ACP communication patterns
- **BeeAI Agent Instances**: Direct integration with BeeAI Framework agents
- **Workflow Evaluation**: Built-in support for BeeAI multi-agent workflows
- **Event Stream Analysis**: Real-time evaluation of agent interactions

## CLI Commands

```bash
# Check provider configuration and system health
acp-evals check

# Generate evaluation templates
acp-evals init simple --name MyAgent --interactive
acp-evals init comprehensive --name ResearchAgent

# List available rubrics and datasets
acp-evals list-rubrics

# Generate reports from results
acp-evals report results.json --format summary
acp-evals report results.json --format detailed
```

## Development Workflow

```bash
# Environment setup
cd python/
pip install -e ".[dev,all-providers]"
cp .env.example .env  # Configure API keys

# Code quality
ruff check src/ && pyright src/

# Testing
python run_tests.py                    # All tests with coverage
MOCK_MODE=true pytest tests/           # No API calls
pytest tests/test_simple.py -v        # Specific test file

# Examples
cd examples/
python 00_minimal_example.py          # 3-line evaluation
python 02_multi_agent_evaluation.py   # Agent coordination
python 12_end_to_end_trace_pipeline.py # Production integration
```

## Documentation & Examples

| Resource | Description |
|----------|-------------|
| 📚 [Architecture Guide](./python/docs/architecture.md) | Framework design and components |
| 🚀 [Setup Guide](./python/docs/setup.md) | Installation and configuration |
| 🔌 [Provider Setup](./python/docs/providers.md) | LLM provider configuration |
| 🏗️ [Multi-Agent Guide](./python/docs/multi_agent.md) | Coordination pattern evaluation |
| 📊 [Metrics Reference](./python/docs/metrics.md) | Available metrics and interpretation |
| 🛡️ [Security Guide](./python/docs/security.md) | Adversarial testing and safety |
| 💡 [Examples](./python/examples/) | 13 comprehensive usage examples |

### **Example Gallery**
- **00_minimal_example.py**: 3-line agent evaluation
- **01_quickstart_accuracy.py**: Basic accuracy assessment
- **02_multi_agent_evaluation.py**: Agent coordination testing
- **03_adversarial_testing.py**: Security and robustness evaluation
- **04_continuous_evaluation.py**: Production monitoring pipeline
- **12_end_to_end_trace_pipeline.py**: Complete evaluation workflow
- **13_synthetic_data_generation.py**: Custom dataset creation

## Project Structure

```
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
└── internal-docs/                   # Development planning
```

## Contributing

We welcome contributions! The framework is designed for extensibility:

- **New Evaluators**: Add custom evaluation logic in `evaluators/`
- **Provider Support**: Extend `providers/` for new LLM providers  
- **Coordination Patterns**: Implement new multi-agent patterns in `patterns/`
- **Dataset Integration**: Add external benchmarks in `benchmarks/datasets/`

See our [contribution guide](./python/CONTRIBUTING.md) for detailed guidance.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## Community

- 💬 [GitHub Discussions](https://github.com/i-am-bee/acp-evals/discussions)
- 🐛 [Issue Tracker](https://github.com/i-am-bee/acp-evals/issues)
- 💬 [Discord Community](https://discord.gg/NradeA6ZNF)

---

Part of the [BeeAI](https://github.com/i-am-bee) project, an initiative of the [Linux Foundation AI & Data](https://lfaidata.foundation/)