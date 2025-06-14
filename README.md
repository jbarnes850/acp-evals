# ACP Evals: Evaluation Framework for Agent Communication Protocol

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-purple.svg)](https://github.com/i-am-bee/acp)

ACP Evals is a comprehensive evaluation framework designed to benchmark, measure, and analyze agent performance in the Agent Communication Protocol (ACP) ecosystem. It provides standardized tools to assess agent quality, efficiency, and behavior across various dimensions.

## 🎯 Why ACP Evals?

The ACP and BeeAI ecosystem lacks standardized ways to:
- Benchmark agent performance across different implementations
- Measure quality and efficiency metrics
- Compare single-agent vs multi-agent architectures
- Understand cost/performance trade-offs
- Track performance regressions

ACP Evals fills this gap with:
- **Token-first metrics** - Token usage explains 80% of performance variance
- **Architecture-aware benchmarks** - Compare supervisor, swarm, and linear patterns
- **Context degradation analysis** - Measure how agents handle irrelevant information
- **Multi-agent evaluation** - Track handoff quality and coordination efficiency
- **Production-ready insights** - Cost projections, error cascades, and optimization recommendations

## 🚀 Quick Start

```bash
# Install
pip install acp-evals

# Evaluate a local ACP agent
acp-evals evaluate http://localhost:8000 --metrics all --benchmark context-scaling

# Compare multiple agents
acp-evals compare agent1:8000 agent2:8001 --output comparison.json
```

## 📊 Key Features

### 1. Comprehensive Metrics
- **Token Usage & Costs** - Detailed breakdowns with model-specific pricing
- **Latency & Throughput** - Response time analysis
- **Quality Scoring** - LLM-as-judge evaluation with unified rubrics
- **Context Efficiency** - Window utilization and compression effectiveness
- **Error Analysis** - Cascade tracking and recovery patterns

### 2. Diverse Benchmarks
- **Context Scaling** - Performance with progressive distractor addition
- **Multi-Agent Handoffs** - Information preservation across agent chains
- **Tool Usage** - Accuracy and efficiency of tool selection
- **Long-Horizon Tasks** - Persistence and state management
- **Domain-Specific** - Extensible framework for custom benchmarks

### 3. Architecture Patterns
- Single agent baseline evaluation
- Supervisor pattern analysis
- Swarm coordination testing
- Linear chain efficiency
- Custom pattern support

### 4. Rich Insights
```bash
🔍 ACP Agent Evaluation Results

Context Scaling Benchmark
┌─────────────┬──────────┬───────────┬────────────┐
│ Distractors │ Accuracy │ Latency   │ Token Cost │
├─────────────┼──────────┼───────────┼────────────┤
│ 0           │ 100%     │ 1.2s      │ $0.0012    │
│ 3           │ 95%      │ 1.8s      │ $0.0024    │
│ 10          │ 75%      │ 3.1s      │ $0.0048    │
└─────────────┴──────────┴───────────┴────────────┘

Key Insights:
• Performance degradation: 25% with 10 distractors
• Token efficiency: 0.00083 success/token
• Estimated monthly cost: $72 for 1000 queries/day
```

## 🔧 Core Components

### Metrics
```python
from acp_evals.metrics import TokenUsageMetric, QualityMetric

# Track comprehensive token usage
token_metric = TokenUsageMetric(model="gpt-4.1")
result = await token_metric.calculate(run, events)
print(f"Total cost: ${result.breakdown['cost_usd']:.4f}")
```

### Benchmarks
```python
from acp_evals.benchmarks import ContextScalingBenchmark

# Test context degradation
benchmark = ContextScalingBenchmark()
results = await benchmark.evaluate_with_context_levels(
    agent, 
    levels=[0, 1, 3, 5, 10]
)
```

### Evaluators
```python
from acp_evals.evaluators import LLMJudge

# Automated quality evaluation
judge = LLMJudge()
score = await judge.evaluate(
    task="Write a Python function",
    response=agent_output,
    rubric="default"
)
```

## 📈 Use Cases

1. **Development** - Track performance during agent development
2. **CI/CD** - Automated regression detection in pipelines
3. **Architecture Selection** - Data-driven pattern choices
4. **Cost Optimization** - Identify efficiency opportunities
5. **Production Monitoring** - Continuous evaluation of deployed agents

## 🛠️ Installation

### From PyPI
```bash
pip install acp-evals
```

### From Source
```bash
git clone https://github.com/i-am-bee/acp-evals
cd acp-evals/python
pip install -e .
```

## 🧪 Testing & Validation

### Running Tests

```bash
cd python
pip install -r requirements-test.txt
./run_tests.py
```

### Validate Implementation

```bash
cd python
./validate.py
```

This will verify:
- All required modules are present
- Base classes properly implemented
- Metrics follow the correct interface
- Benchmarks include required features
- Research insights are incorporated

## 📚 Documentation

- [Getting Started](docs/getting-started.md)
- [Metrics Guide](docs/metrics.md)
- [Benchmark Creation](docs/benchmarks.md)
- [Architecture Patterns](docs/patterns.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

Key areas for contribution:
- New benchmark scenarios
- Additional metrics
- Domain-specific evaluations
- Multi-language support
- Visualization improvements

## 📊 Research Foundation

ACP Evals is built on insights from leading research:
- Anthropic's multi-agent system analysis
- Cognition's context engineering principles
- LangChain's architecture patterns
- Adaline Labs' dynamic evaluation approaches

## 🗺️ Roadmap

- [ ] Web dashboard for result visualization
- [ ] Real-time evaluation streaming
- [ ] Integration with CI/CD platforms
- [ ] Domain-specific benchmark libraries
- [ ] Multi-language agent support

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ACP team for the foundational protocol
- BeeAI Framework for multi-agent patterns
- Research teams at Anthropic, Cognition, and LangChain
- The open-source community

---

Built with ❤️ for the ACP community