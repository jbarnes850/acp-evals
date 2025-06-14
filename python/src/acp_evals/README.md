# ACP Evals Package Structure

This directory contains the core implementation of the ACP Evaluation Framework.

## Directory Structure

```
acp_evals/
├── __init__.py           # Package exports and version
├── simple.py             # High-level developer-friendly API
├── config.py             # Configuration management
├── validation.py         # Input validation and security
├── exceptions.py         # Custom exception hierarchy
├── logging_config.py     # Logging and telemetry setup
│
├── providers/            # LLM provider implementations
│   ├── __init__.py
│   ├── base.py          # Abstract provider interface
│   ├── factory.py       # Provider factory and auto-detection
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── ollama_provider.py
│
├── evaluators/          # Evaluation implementations
│   ├── __init__.py
│   ├── base.py          # Abstract evaluator interface
│   └── llm_judge.py     # LLM-as-judge evaluator
│
├── metrics/             # Performance and quality metrics
│   ├── __init__.py
│   ├── base.py          # Abstract metric interface
│   ├── token_usage.py   # Token counting and costs
│   ├── latency.py       # Response time tracking
│   ├── context_efficiency.py  # Context window usage
│   ├── handoff_quality.py     # Multi-agent handoffs
│   └── cost.py          # Cost calculations
│
├── benchmarks/          # Standardized test suites
│   ├── __init__.py
│   ├── base.py          # Abstract benchmark interface
│   ├── context_scaling.py     # Context degradation tests
│   ├── handoff.py       # Multi-agent coordination
│   └── pattern_comparison.py  # Architecture comparisons
│
├── patterns/            # Multi-agent patterns
│   ├── __init__.py
│   ├── base.py          # Abstract pattern interface
│   ├── linear.py        # Sequential execution
│   ├── supervisor.py    # Centralized coordination
│   └── swarm.py         # Distributed collaboration
│
├── quality/             # Quality evaluators (optional)
│   ├── __init__.py
│   ├── groundedness.py  # Response grounding
│   ├── completeness.py  # Task completion
│   ├── task_adherence.py # Instruction following
│   └── tool_accuracy.py # Tool usage validation
│
├── simulator.py         # Test data generation
├── cli.py              # Command-line interface
└── cli_check.py        # Provider verification command
```

## Key Components

### Simple API (`simple.py`)

The main entry point for developers. Provides:
- `AccuracyEval` - LLM-based quality evaluation
- `PerformanceEval` - Resource usage tracking
- `ReliabilityEval` - Robustness testing
- `SafetyEval` - Content safety checks
- `evaluate()` - Synchronous helper function

### Providers (`providers/`)

Abstraction layer for LLM providers:
- Automatic provider detection
- Unified error handling
- Cost calculation
- Mock mode for testing

### Evaluators (`evaluators/`)

Core evaluation logic:
- `LLMJudge` - Single-call evaluation with rubrics
- Extensible interface for custom evaluators

### Metrics (`metrics/`)

Comprehensive measurement system:
- Token usage (primary performance driver)
- Latency and throughput
- Context efficiency
- Multi-agent coordination
- Real cost tracking

### Patterns (`patterns/`)

Multi-agent architectural patterns:
- Linear (sequential)
- Supervisor (hub-and-spoke)
- Swarm (peer-to-peer)

## Design Principles

1. **Simplicity First**: High-level API hides complexity
2. **Token Awareness**: Every operation tracks tokens
3. **Provider Agnostic**: Work with any LLM
4. **Production Ready**: Validation, logging, error handling
5. **Extensible**: Easy to add new components

## Extension Points

### Adding a New Evaluator

```python
from acp_evals.evaluators.base import Evaluator, EvaluationResult

class MyEvaluator(Evaluator):
    async def evaluate(self, task, response, reference=None):
        # Custom logic
        return EvaluationResult(
            score=0.95,
            passed=True,
            breakdown={},
            feedback="Great job!"
        )
```

### Adding a New Provider

```python
from acp_evals.providers.base import LLMProvider, LLMResponse

class MyProvider(LLMProvider):
    async def complete(self, prompt, **kwargs):
        # Provider logic
        return LLMResponse(
            content="...",
            usage={...},
            cost=0.01
        )
```

### Adding a New Metric

```python
from acp_evals.metrics.base import Metric, MetricResult

class MyMetric(Metric):
    async def calculate(self, run, events):
        # Calculation logic
        return MetricResult(
            name="my_metric",
            value=42,
            unit="points"
        )
```

## Best Practices

1. **Import from Top Level**: Use `from acp_evals import ...`
2. **Use Type Hints**: All public APIs are fully typed
3. **Handle Errors**: Framework provides structured exceptions
4. **Track Costs**: Monitor token usage and costs
5. **Test with Mock**: Use mock mode during development

## Contributing

See the main [Contributing Guide](../../CONTRIBUTING.md) for details on:
- Code style and standards
- Testing requirements
- Documentation guidelines
- Pull request process