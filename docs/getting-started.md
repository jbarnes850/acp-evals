# Getting Started with ACP Evals

Welcome to ACP Evals! This guide will help you get up and running with the evaluation framework.

## Installation

### From PyPI (coming soon)
```bash
pip install acp-evals
```

### From Source
```bash
git clone https://github.com/i-am-bee/acp-evals
cd acp-evals/python
pip install -e .
```

## Prerequisites

1. **ACP Agent**: You need an ACP-compatible agent running. The simplest way is to use the echo agent from the ACP examples:

```bash
# Clone ACP repository
git clone https://github.com/i-am-bee/acp
cd acp/examples/python/basic

# Install dependencies
pip install -r requirements.txt

# Run echo agent
python servers/echo.py
```

2. **Python 3.11+**: The framework requires Python 3.11 or later.

## Quick Start

### 1. Basic Token Analysis

The simplest way to start is by analyzing token usage:

```python
import asyncio
from acp_evals.client import ACPEvaluationClient
from acp_evals.metrics import TokenUsageMetric

async def main():
    # Connect to your agent
    client = ACPEvaluationClient(
        base_url="http://localhost:8000",
        metrics=[TokenUsageMetric(model="gpt-4")]
    )
    
    # Run with tracking
    run, events, metrics = await client.run_with_tracking(
        agent_name="echo",
        input="Hello, world!"
    )
    
    # Display token usage
    token_result = metrics["token_usage"]
    print(f"Total tokens: {token_result.value}")
    print(f"Cost: ${token_result.breakdown['cost_usd']:.4f}")

asyncio.run(main())
```

### 2. Running Benchmarks

Evaluate your agent with standardized benchmarks:

```python
from acp_evals.benchmarks import ContextScalingBenchmark

# Create benchmark
benchmark = ContextScalingBenchmark(
    distractor_levels=[0, 1, 3, 5],  # Test with increasing context
    task_categories=["reasoning", "coding"]  # Focus areas
)

# Run evaluation
result = await client.run_benchmark(
    agent_name="your-agent",
    benchmark=benchmark
)

# View results
print(f"Overall score: {result.overall_score:.2%}")
print(f"Performance degradation: {result.summary['total_degradation']:.1f}%")
```

### 3. Custom Metrics

Create your own metrics:

```python
from acp_evals.base import Metric, MetricResult

class ResponseLengthMetric(Metric):
    @property
    def name(self):
        return "response_length"
    
    @property
    def description(self):
        return "Measures response verbosity"
    
    async def calculate(self, run, events):
        total_length = 0
        for event in events:
            if event.type == "message.created" and event.message.role == "assistant":
                for part in event.message.parts:
                    if part.content:
                        total_length += len(part.content)
        
        return MetricResult(
            name=self.name,
            value=total_length,
            unit="characters",
            breakdown={"avg_per_message": total_length / max(1, len(events))}
        )
```

## Core Concepts

### Metrics
Metrics measure specific aspects of agent performance:
- **TokenUsageMetric**: Tracks token consumption and costs
- **LatencyMetric**: Measures response times
- **ContextEfficiencyMetric**: Analyzes context window usage
- **CostMetric**: Provides comprehensive cost analysis

### Benchmarks
Benchmarks test agent capabilities:
- **ContextScalingBenchmark**: Tests performance with increasing irrelevant context
- **HandoffQualityBenchmark**: Measures information preservation in multi-agent systems

### Evaluation Client
The `ACPEvaluationClient` wraps the standard ACP client with:
- Event collection during runs
- Automatic metric calculation
- Benchmark execution support
- Multi-agent tracking

## Examples

Check out the `examples/python` directory for complete examples:

1. **evaluate_single_agent.py**: Comprehensive evaluation with multiple metrics
2. **token_analysis.py**: Focused token usage analysis
3. **multi_agent_evaluation.py**: Evaluate multi-agent systems (coming soon)

## Common Patterns

### Pattern 1: Continuous Monitoring
```python
# Run evaluation periodically
while True:
    result = await evaluate_agent()
    if result.metrics["token_usage"].breakdown["cost_usd"] > threshold:
        alert("High token usage detected!")
    await asyncio.sleep(3600)  # Check hourly
```

### Pattern 2: A/B Testing
```python
# Compare two agent configurations
results_a = await benchmark.evaluate(agent_a)
results_b = await benchmark.evaluate(agent_b)

if results_a.overall_score > results_b.overall_score:
    print("Configuration A performs better")
```

### Pattern 3: Regression Detection
```python
# Track performance over time
baseline = await benchmark.evaluate(agent)
# After changes...
current = await benchmark.evaluate(agent)

if current.overall_score < baseline.overall_score * 0.95:
    print("Performance regression detected!")
```

## Best Practices

1. **Start with Token Metrics**: Token usage explains 80% of performance variance
2. **Use Small Benchmarks**: 20-30 well-chosen tests are often sufficient
3. **Track Context Usage**: Monitor context window utilization to prevent saturation
4. **Compare Architectures**: Test single vs multi-agent on the same tasks
5. **Monitor Costs**: Always track projected costs at scale

## Troubleshooting

### "Agent not found"
Ensure your agent is running and accessible at the specified URL. Check with:
```bash
curl http://localhost:8000/agents
```

### "No token metrics available"
Some metrics require specific event types. Ensure your agent emits standard ACP events.

### High latency measurements
Network latency can affect measurements. Run evaluations close to your agent for accurate results.

## Next Steps

1. Read the [Architecture Guide](architecture.md) to understand the framework design
2. Explore [Creating Custom Benchmarks](benchmarks.md)
3. Learn about [Multi-Agent Evaluation](multi-agent.md)
4. Join the community and share your benchmarks!

## Getting Help

- GitHub Issues: https://github.com/i-am-bee/acp-evals/issues
- Discord: Join the ACP community
- Documentation: Full API reference coming soon