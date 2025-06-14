# ACP Evals Examples

This directory contains practical examples showing how to evaluate different types of ACP agents.

## Quick Start

The fastest way to get started is with `quickstart.py`:

```python
from acp_evals import AccuracyEval, evaluate

# Evaluate any function
async def my_agent(input: str) -> str:
    return "response"

result = evaluate(
    AccuracyEval(agent=my_agent),
    input="test question",
    expected="expected answer",
    print_results=True
)
```

## Examples by Agent Type

### 1. Simple Accuracy Evaluation (`simple_accuracy_eval.py`)
- Basic accuracy testing with built-in rubrics
- Batch evaluation with test cases
- Custom rubrics for specific domains

### 2. Research Agent (`research_agent_eval.py`)
- Evaluating deep research agents
- Testing information depth and source quality
- Performance benchmarks for long-form generation
- Multi-aspect evaluation (accuracy + performance + reliability)

### 3. Multi-Agent Systems (`multi_agent_eval.py`)
- Testing agent collaboration and handoffs
- Information preservation across agents
- System-wide performance evaluation
- Error handling in multi-agent workflows

### 4. Tool-Using Agents (`tool_agent_eval.py`)
- Verifying correct tool selection
- Testing tool chaining and composition
- Error handling with external tools
- Performance with tool overhead

## Running the Examples

1. Install ACP Evals:
```bash
pip install -e .
```

2. Run any example:
```bash
python examples/quickstart.py
python examples/research_agent_eval.py
python examples/multi_agent_eval.py
python examples/tool_agent_eval.py
```

## Key Features Demonstrated

- **Zero-setup evaluation**: Evaluate agents with minimal code
- **Multiple agent types**: Functions, URLs, or agent instances
- **Rich output**: Beautiful console output with progress tracking
- **Batch testing**: Run multiple test cases efficiently
- **Export results**: Save to JSON for further analysis
- **Flexible rubrics**: Use built-in or custom evaluation criteria

## Built-in Rubrics

### Factual Accuracy
Best for: Q&A agents, information retrieval
```python
eval = AccuracyEval(agent=my_agent, rubric="factual")
```

### Research Quality
Best for: Research agents, analysis tools
```python
eval = AccuracyEval(agent=my_agent, rubric="research_quality")
```

### Code Quality
Best for: Code generation agents
```python
eval = AccuracyEval(agent=my_agent, rubric="code_quality")
```

## Custom Rubrics

Create your own evaluation criteria:
```python
eval = AccuracyEval(
    agent=my_agent,
    rubric={
        "criterion1": {"weight": 0.5, "criteria": "Is it correct?"},
        "criterion2": {"weight": 0.5, "criteria": "Is it complete?"},
    }
)
```

## Tips

1. **Start simple**: Use the quickstart example as a template
2. **Use built-in rubrics**: They cover most common use cases
3. **Batch evaluation**: Test multiple cases for statistical significance
4. **Export results**: Use JSON export for tracking progress over time
5. **Combine evaluators**: Use AccuracyEval + PerformanceEval + ReliabilityEval for comprehensive testing