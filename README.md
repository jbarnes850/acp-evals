# ACP Evals

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![ACP Compatible](https://img.shields.io/badge/ACP-compatible-brightgreen.svg)](https://github.com/i-am-bee/acp)

**ACP Evals is an open framework for evaluating AI agents across accuracy, performance, and reliability dimensions.**

Modern AI agents need comprehensive testing before deployment. ACP Evals provides production-grade evaluation using LLM-as-judge methodology, designed to integrate seamlessly with the BeeAI ecosystem and any ACP-compliant agent.

ACP Evals enables you to:
- Measure response accuracy using configurable LLM judges
- Track performance metrics including latency and memory usage
- Validate tool usage patterns and error handling
- Run batch evaluations for comprehensive test coverage
- Generate detailed reports for continuous improvement

## Core Concepts

| **Concept** | **Description** |
|-------------|------------------|
| **Accuracy** | Evaluates response quality against expected outputs using LLM-as-judge methodology. Supports custom rubrics for domain-specific evaluation. |
| **Performance** | Measures latency, memory usage, and token efficiency. Essential for production deployments where speed and resource constraints matter. |
| **Reliability** | Validates tool usage patterns, error handling, and consistency across runs. Critical for agents that interact with external systems. |

## Quick Example

Evaluate agent accuracy with just a few lines:

```python calculate_accuracy.py
from acp_evals import AccuracyEval

evaluation = AccuracyEval(
    agent="http://localhost:8001/agents/my-agent",
    rubric="factual"
)

result = await evaluation.run(
    input="What is 10*5 then to the power of 2? do it step by step",
    expected="2500",
    print_results=True
)
assert result is not None and result.score >= 0.7
```

## Core Features

- **[Comprehensive Evaluation](./examples/comprehensive_eval.py)** - Run all three evaluation dimensions in a single command
- **[Rich TUI Display](./src/acp_evals/cli/display.py)** - Interactive terminal UI with detailed metrics and LLM judge explanations
- **[Batch Testing](./docs/api-reference.md#batch-evaluation)** - Evaluate multiple test cases with parallel execution
- **[Multiple Provider Support](./docs/providers.md)** - Works with OpenAI, Anthropic, Ollama, and more
- **[Export Capabilities](./docs/api-reference.md#result-objects)** - Generate JSON reports for CI/CD integration

## Installation

```bash
pip install acp-evals
```

## Quickstart

**1. Configure your LLM provider**

```bash
echo "OPENAI_API_KEY=your-key-here" > .env
acp-evals check
```

**2. Run your first evaluation**

```bash
# Test accuracy
acp-evals run accuracy http://localhost:8001/agents/my-agent \
  -i "What is 2+2?" -e "4"
```

**3. Run comprehensive evaluation**

```bash
acp-evals comprehensive http://localhost:8001/agents/my-agent \
  -i "Calculate compound interest" -e "Detailed calculation"
```

## Examples

### Performance Evaluation

```python
from acp_evals import PerformanceEval

evaluation = PerformanceEval(
    agent="http://localhost:8001/agents/my-agent",
    num_iterations=5,
    track_memory=True
)

result = await evaluation.run(
    input_text="What is the capital of France?",
    print_results=True
)
```

### Reliability Evaluation

```python
from acp_evals import ReliabilityEval

evaluation = ReliabilityEval(
    agent="http://localhost:8001/agents/my-agent",
    tool_definitions=["search", "calculator"]
)

result = await evaluation.run(
    input="Search for AAPL price and calculate P/E ratio",
    expected_tools=["search", "calculator"],
    print_results=True
)
assert result.passed
```

## Agent Formats

ACP Evals works with any agent implementation:

- **ACP-compliant agents**: `http://localhost:8001/agents/my-agent`
- **Python functions**: `agent.py:function_name`
- **Python modules**: `mymodule.agent_function`

## CLI Reference

```bash
# Check setup
acp-evals check

# Run evaluations
acp-evals run accuracy <agent> -i <input> -e <expected>
acp-evals run performance <agent> -i <input>
acp-evals run reliability <agent> -i <input> --expected-tools <tool>

# Comprehensive testing
acp-evals comprehensive <agent> -i <input> -e <expected>

# Batch testing
acp-evals run accuracy <agent> --test-file tests.jsonl
```

## Resources

- **[Documentation](./docs)** - API reference and guides
- **[Examples](./examples)** - Ready-to-run code samples
- **[Issues](https://github.com/i-am-bee/acp-evals/issues)** - Report bugs or request features

## License

Apache 2.0 - see [LICENSE](./LICENSE)

---

Developed by contributors to the BeeAI project, this initiative is part of the [Linux Foundation AI & Data program](https://lfaidata.foundation/projects/). Its development follows open, collaborative, and community-driven practices.