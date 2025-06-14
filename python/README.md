# ACP Evals

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![BeeAI Framework](https://img.shields.io/badge/BeeAI-Framework-yellow.svg)](https://github.com/i-am-bee/beeai-framework)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Production-ready evaluation framework for multi-agent systems in the ACP/BeeAI ecosystem**

[Documentation](./docs) • [Examples](./examples) • [API Reference](#api-reference) • [Contributing](#contributing)

</div>

## Overview

ACP Evals is an evaluation framework for multi-agent systems built on the Agent Communication Protocol. Evaluation frameworks measure the quality, performance, and safety of AI agent outputs through automated scoring methods. In production agent systems, these measurements become critical for ensuring reliability, detecting regressions, and optimizing performance at scale.

Unlike traditional evaluation tools that focus on single-agent accuracy, ACP Evals specializes in the unique challenges of coordinated agent systems. The framework measures how well agents collaborate, preserve information across handoffs, and maintain workflow coherence under production conditions.

ACP Evals addresses the unique challenges of evaluating coordinated agent systems. While traditional evaluation tools focus on single-agent accuracy metrics, this framework provides specialized evaluators for multi-agent coordination patterns, handoff quality preservation, and production trace analysis. The framework integrates directly with ACP-compatible agents and BeeAI workflows, supporting evaluation scenarios from simple three-line accuracy checks to comprehensive multi-agent benchmarking suites.

The framework implements a layered architecture that separates the developer API from evaluation logic, provider abstractions, and infrastructure concerns. This design enables progressive disclosure where beginners can start with simple evaluations and gradually access more sophisticated capabilities like trace recycling, adversarial testing, and continuous evaluation pipelines. All evaluations generate standardized results with token usage tracking, cost analysis, and OpenTelemetry export for production monitoring.

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
cp .env.example .env

# Add your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

See [.env.example](./.env.example) for all configuration options.

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

This pattern extends to all evaluation types. Replace `AccuracyEval` with `PerformanceEval`, `SafetyEval`, or `ReliabilityEval` to measure different aspects of agent behavior. The `evaluate()` function handles provider selection, result formatting, and error management automatically.

## Core Evaluators

ACP Evals provides four primary evaluator classes, each targeting different aspects of agent performance. Understanding when and how to use each evaluator forms the foundation for effective agent evaluation.

### AccuracyEval

Measures response quality using LLM-as-judge evaluation with customizable rubrics. This evaluator sends your agent's response to a separate LLM judge that scores quality according to predefined criteria.

```python
# Use built-in rubrics for common scenarios
eval = AccuracyEval(
    agent=my_agent,
    rubric="research_quality"  # Options: "factual", "code_quality", "research_quality"
)

# Define custom rubrics for specific domains
custom_rubric = {
    "technical_accuracy": {
        "weight": 0.6,
        "criteria": "Response uses correct technical terminology and concepts"
    },
    "completeness": {
        "weight": 0.4,
        "criteria": "Response addresses all aspects of the question"
    }
}

eval = AccuracyEval(agent=my_agent, rubric=custom_rubric)
```

### PerformanceEval

Tracks computational efficiency metrics including token usage, response latency, and cost across different LLM providers. This evaluator measures the resource efficiency of your agents rather than response quality.

```python
perf = PerformanceEval(agent=my_agent)
result = perf.run(
    input="Analyze this complex document...",
    track_tokens=True,
    track_latency=True,
    track_memory=True
)
print(f"Tokens: {result.tokens}, Latency: {result.latency_ms}ms, Cost: ${result.cost:.4f}")
```

### ReliabilityEval

Validates tool usage patterns and error handling behavior. This evaluator tests whether agents use tools appropriately and handle failure cases gracefully.

```python
reliability = ReliabilityEval(agent=my_agent)
result = reliability.run(
    input="Search for recent AI papers and summarize findings",
    expected_tools=["search", "summarize"],
    test_error_handling=True
)
```

### SafetyEval

Composite evaluator that combines multiple safety assessments including content filtering, bias detection, and harmful output classification.

```python
safety = SafetyEval(
    agent=my_agent,
    thresholds={"harmful_content": 0.1, "bias": 0.1}
)
```

## Multi-Agent Evaluation

ACP Evals specializes in evaluating coordinated agent systems. Multi-agent evaluation requires measuring how well agents work together, preserve information across handoffs, and maintain coherent workflows.

### Coordination Patterns

The framework implements three primary coordination patterns that cover most multi-agent architectures:

```python
from acp_evals.patterns import LinearPattern, SupervisorPattern, SwarmPattern

# Sequential agent execution
linear = LinearPattern(["researcher", "analyzer", "writer"])

# Centralized coordination with specialized agents
supervisor = SupervisorPattern(
    supervisor="coordinator",
    specialists=["research_agent", "analysis_agent", "writing_agent"]
)

# Distributed collaboration
swarm = SwarmPattern(
    agents=["agent_1", "agent_2", "agent_3"],
    collaboration_strategy="consensus"
)
```

### Handoff Quality Evaluation

Handoff quality measures how much relevant information is preserved when one agent passes control to another. This metric is unique to multi-agent systems and critical for workflow effectiveness.

```python
from acp_evals import HandoffEval

handoff_eval = HandoffEval(
    agents={
        "researcher": "http://localhost:8000/agents/researcher",
        "writer": "http://localhost:8000/agents/writer"
    }
)

result = handoff_eval.run(
    task="Research quantum computing and write a technical summary",
    expected_handoffs=["researcher->writer"],
    measure_information_preservation=True
)
```

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

## Production Integration

ACP Evals provides advanced features for production monitoring and continuous evaluation. These capabilities transform the framework from a development tool into a production monitoring system.

### Trace Recycling

Trace recycling converts production telemetry data into evaluation datasets. This process enables continuous evaluation using real user interactions and system traces.

```python
from acp_evals.benchmarks.datasets.trace_recycler import TraceRecycler

# Initialize trace recycler with OpenTelemetry exporter
recycler = TraceRecycler()

# Ingest production traces (converts ACP format to OpenTelemetry automatically)
recycler.ingest_trace(production_trace)

# Generate synthetic evaluation datasets
synthetic_tests = recycler.generate_evaluation_dataset(
    count=50,
    adaptive_threshold=True,  # Adjusts quality thresholds based on data
    include_patterns=["success", "error_handling"]
)

# Export datasets for reuse
recycler.export_synthetic_dataset(
    output_path="datasets/production_tests.jsonl",
    count=100,
    format="jsonl"
)
```

### Continuous Evaluation

Continuous evaluation runs automated evaluations on agent deployments, detecting regressions and performance drift over time.

```python
from acp_evals.evaluation.continuous import ContinuousEvaluationPipeline

pipeline = ContinuousEvaluationPipeline(
    agents=["http://localhost:8000/agents/my-agent"],
    evaluators=[AccuracyEval(), PerformanceEval()],
    schedule="0 */6 * * *"  # Every 6 hours
)

# Run with regression detection
pipeline.run_with_baseline_comparison(
    baseline_results="previous_evaluation.json",
    regression_threshold=0.05
)
```

### OpenTelemetry Export

All evaluation results can be exported to OpenTelemetry-compatible monitoring systems for dashboard visualization and alerting.

```python
from acp_evals.telemetry.otel_exporter import OTelExporter

exporter = OTelExporter(
    endpoint="http://jaeger:14268/api/traces",
    service_name="agent-evaluation"
)

# Evaluations automatically export to telemetry when exporter is configured
eval = AccuracyEval(agent=my_agent, telemetry_exporter=exporter)
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

## Architecture and Extension

ACP Evals uses a layered architecture that separates concerns and enables extension. Understanding this structure helps when implementing custom evaluators or integrating with external systems.

### Core Architecture

```bash
acp_evals/
├── api.py                 # Developer-facing API
├── evaluators/            # Evaluation implementations
│   ├── base.py           # Abstract evaluator interface
│   ├── semantic_evaluator.py  # LLM-based semantic evaluation
│   └── composite_evaluators.py  # Multi-evaluator combinations
├── providers/             # LLM provider abstractions
│   ├── openai_provider.py     # OpenAI integration
│   ├── anthropic_provider.py  # Anthropic integration
│   └── ollama_provider.py     # Local model support
├── patterns/              # Multi-agent coordination patterns
├── benchmarks/            # Evaluation datasets and benchmarks
└── telemetry/            # Production monitoring integration
```

### Custom Evaluators

Implement custom evaluators by extending the base evaluator class:

```python
from acp_evals.evaluators.base import Evaluator, EvaluationResult

class CustomEvaluator(Evaluator):
    def __init__(self, agent, custom_threshold=0.8):
        super().__init__(agent)
        self.threshold = custom_threshold
    
    async def evaluate(self, input_text, expected_output, **kwargs):
        # Implement your evaluation logic
        agent_response = await self.agent.run(input_text)
        
        # Calculate custom score
        score = self._calculate_custom_score(agent_response, expected_output)
        
        return EvaluationResult(
            score=score,
            passed=score >= self.threshold,
            details={"custom_metric": score}
        )
    
    def _calculate_custom_score(self, response, expected):
        # Your scoring logic here
        return 0.85
```

## Examples and Learning Resources

The framework includes comprehensive examples that demonstrate real-world usage patterns. These examples serve as both learning resources and starting points for implementation.

### Essential Examples

- **[00_minimal_example.py](./examples/00_minimal_example.py)**: Three-line evaluation setup
- **[01_quickstart_accuracy.py](./examples/01_quickstart_accuracy.py)**: Basic accuracy assessment workflow
- **[04_tool_using_agents.py](./examples/04_tool_using_agents.py)**: Tool usage and reliability evaluation
- **[07_adversarial_testing.py](./examples/07_adversarial_testing.py)**: Security and robustness testing
- **[12_end_to_end_trace_pipeline.py](./examples/12_end_to_end_trace_pipeline.py)**: Complete production evaluation workflow

### Production Examples

- **[09_real_acp_agents.py](./examples/09_real_acp_agents.py)**: Integration with live ACP agents
- **[13_synthetic_data_generation_and_storage.py](./examples/13_synthetic_data_generation_and_storage.py)**: Dataset creation and management

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

## Contributing

ACP Evals is designed for community extension. The framework provides clear interfaces for adding new evaluators, providers, and coordination patterns.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/jbarnes850/acp-evals
cd acp-evals/python
pip install -e ".[dev,all-providers]"

# Run tests to verify setup
pytest

# Run linting and type checking
ruff check src/
pyright src/
```

### Extension Points

The framework offers several extension points:

- **New Evaluators**: Implement custom evaluation logic in `evaluators/`
- **Provider Support**: Add new LLM providers in `providers/`
- **Coordination Patterns**: Implement new multi-agent patterns in `patterns/`
- **Dataset Integration**: Add external benchmark support in `benchmarks/datasets/`

See our [Contributing Guide](../CONTRIBUTING.md) for detailed development guidelines and code style requirements.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.

Part of the [BeeAI](https://github.com/i-am-bee) project, an initiative of the [Linux Foundation AI & Data](https://lfaidata.foundation/).