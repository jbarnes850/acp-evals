# ACP-Evals Architecture

## Overview

ACP-Evals provides a minimal, focused framework for evaluating AI agents. The architecture prioritizes simplicity and developer experience while maintaining professional-grade evaluation capabilities.

## Core Design Principles

1. **Minimal Surface Area**: Three core evaluators with clean abstractions
2. **Token-First**: All evaluations track token usage and costs
3. **Provider Agnostic**: Support for OpenAI, Anthropic, and Ollama
4. **Zero Configuration**: Works out of the box with sensible defaults

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                         │
│              src/acp_evals/api.py                   │
│    AccuracyEval | PerformanceEval | ReliabilityEval │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                Evaluator Layer                      │
│          src/acp_evals/evaluators/                  │
│   accuracy.py | performance.py | reliability.py     │
│              llm_judge.py | common.py               │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                  Core Layer                         │
│            src/acp_evals/core/                      │
│     base.py | config.py | validation.py             │
│        exceptions.py | acp_diagnostics.py           │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                Provider Layer                       │
│          src/acp_evals/providers/                   │
│   openai | anthropic | ollama | factory | base      │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                   CLI Layer                         │
│            src/acp_evals/cli/                       │
│     main.py | commands/ | display.py | check.py     │
└─────────────────────────────────────────────────────┘
```

## Component Details

### API Layer (`api.py`)

The single entry point for all evaluation operations:

- **AccuracyEval**: LLM-as-judge evaluation against expected outputs
- **PerformanceEval**: Latency, throughput, and resource usage metrics
- **ReliabilityEval**: Tool usage validation and error handling assessment

### Evaluator Layer (`evaluators/`)

Core evaluation implementations:

- **accuracy.py**: Semantic and factual accuracy evaluation
- **performance.py**: Performance metric collection and analysis
- **reliability.py**: Tool call verification and error resilience
- **llm_judge.py**: Shared LLM judge implementation
- **common.py**: Shared data structures (EvalResult, BatchResult)

### Core Layer (`core/`)

Foundation classes and utilities:

- **base.py**: Base data models (TokenUsage, MetricResult)
- **config.py**: Configuration management and defaults
- **validation.py**: Input validation and sanitization
- **exceptions.py**: Structured error hierarchy
- **acp_diagnostics.py**: ACP protocol diagnostics

### Provider Layer (`providers/`)

LLM provider abstraction:

- **base.py**: Abstract provider interface
- **factory.py**: Provider auto-detection and instantiation
- **openai_provider.py**: OpenAI GPT models
- **anthropic_provider.py**: Anthropic Claude models
- **ollama_provider.py**: Local Ollama models

### CLI Layer (`cli/`)

Command-line interface:

- **main.py**: CLI entry point
- **commands/**: Individual commands (run, test, discover, quickstart)
- **display.py**: Result formatting and display
- **check.py**: System diagnostics

## Data Flow

```
Input → API → Validation → Agent Execution → 
→ Metric Collection → Evaluation → Result
```

## Key Features

### Token Tracking
Every evaluation tracks:
- Input/output token counts
- Total token usage
- Cost estimation per model
- Model identification

### Provider Auto-Detection
```python
# Automatic provider selection based on environment
eval = AccuracyEval("http://localhost:8000/agent")

# Explicit provider specification
eval = AccuracyEval(agent_url, judge_model="gpt-4o")
```

### Unified Result Format
All evaluators return consistent `EvalResult` objects containing:
- Pass/fail status
- Numeric score
- Detailed feedback
- Token usage and costs
- Execution metadata

## Integration Points

### Agent Communication
- HTTP endpoint support for any agent URL
- ACP protocol message handling
- Streaming response support

### Model Providers
- Environment-based configuration
- Automatic fallback handling
- Cost tracking per provider

## Example Usage

```python
from acp_evals import AccuracyEval

# Simple evaluation
eval = AccuracyEval("http://localhost:8000/agent")
result = await eval.run("What is 2+2?", "4")

# Advanced configuration
eval = AccuracyEval(
    agent_url,
    rubric="semantic",
    judge_model="claude-3-5-sonnet-20241022",
    pass_threshold=0.8
)
```

## Best Practices

1. **Start Simple**: Use default configurations and add complexity as needed
2. **Monitor Costs**: Check token usage in results to manage API costs
3. **Choose Appropriate Models**: Balance evaluation quality vs cost
4. **Validate Inputs**: The framework handles validation, but sanitize user data
5. **Handle Errors**: All evaluators provide structured error information

This architecture provides a clean, focused foundation for agent evaluation with minimal complexity and maximum developer productivity.