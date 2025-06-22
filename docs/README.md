# ACP Evals Documentation

A simplified evaluation framework for AI agents with three core evaluators.

## Overview

ACP Evals provides a streamlined API for evaluating AI agent performance across three key dimensions with comprehensive visual feedback:

- **AccuracyEval** - Evaluates response quality and correctness using LLM-as-judge with detailed input/expected/actual comparison
- **PerformanceEval** - Measures token usage and response latency with visual performance metrics
- **ReliabilityEval** - Validates tool usage and execution reliability with detailed tool analysis

All evaluations include professional rich terminal display with complete transparency:
- Full input/expected/actual output comparison without truncation
- Detailed score breakdowns with 3-decimal precision
- Complete LLM judge reasoning and evaluation criteria
- Performance analysis with user experience context
- Visual score bars and structured feedback panels

## Quick Start

```python
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

# Initialize evaluators with agent URL
accuracy = AccuracyEval(agent="http://localhost:8000")
performance = PerformanceEval(agent="http://localhost:8000")
reliability = ReliabilityEval(agent="http://localhost:8000")

# Run evaluations
accuracy_result = await accuracy.run(input="What is 2+2?", expected="4")
performance_result = await performance.run(input="Process this data")
reliability_result = await reliability.run(input="Search for Python tutorials")
```

## Core Evaluators

### AccuracyEval
Evaluates the correctness and quality of agent responses using LLM-as-judge methodology.

**Key Features:**
- Response quality assessment
- Correctness validation
- Semantic similarity evaluation

### PerformanceEval
Measures computational efficiency and response times.

**Key Features:**
- Token usage tracking
- Response latency measurement
- Cost estimation

### ReliabilityEval
Validates tool usage patterns and execution reliability.

**Key Features:**
- Tool call validation
- Execution path verification
- Error handling assessment

## API Pattern

All evaluators follow a consistent async/await pattern:

```python
async def run(self, input: str, **kwargs) -> EvalResult:
    """
    Run evaluation on agent with given input.
    
    Args:
        input: Input to send to the agent
        **kwargs: Additional evaluator-specific parameters
        
    Returns:
        EvalResult containing score and metadata
    """
```

## Installation

```bash
pip install acp-evals
```

## Configuration

Set your LLM provider credentials:

```bash
export OPENAI_API_KEY="your-api-key"
# or
export ANTHROPIC_API_KEY="your-api-key"
```

## Examples

See the [examples/](../examples/) directory for complete working examples.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to the project.