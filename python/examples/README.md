# ACP Evals Examples

This directory contains example scripts demonstrating how to use the ACP Evals framework, ordered from simple to complex.

## Examples Overview

### Getting Started
- **01_minimal_example.py** - Absolute minimal example (3 lines of code!)
- **02_basic_accuracy_evaluation.py** - Basic accuracy evaluation with beautiful output

### Core Evaluation Types  
- **03_research_agent_evaluation.py** - Evaluating research assistants with comprehensive metrics
- **04_tool_using_agents.py** - Testing agents that use external tools (calculator, search, etc.)
- **05_multi_agent_patterns.py** - Evaluating multi-agent collaboration and handoffs
- **06_comprehensive_evaluation.py** - Advanced quality metrics (groundedness, completeness)

### Advanced Features
- **07_adversarial_testing.py** - Generating synthetic test data for robust evaluation
- **08_ci_cd_integration.py** - Automated evaluation in CI/CD pipelines

### Production Integration
- **09_real_acp_agents.py** - Testing against real ACP agents from BeeAI ecosystem
- **10_acp_agent_discovery.py** - Discovering and testing available ACP agents
- **11_trace_recycling_example.py** - Converting production traces to evaluation datasets

## Running Examples

### Prerequisites

```bash
# Install the package (from the python directory)
pip install -e ..

# Or install with all providers
pip install -e "..[all-providers]"

# Copy and configure environment
cp ../.env.example ../.env
# Edit .env with your API keys
```

### Running Individual Examples

```bash
# Minimal example
python 01_minimal_example.py

# Basic accuracy evaluation
python 02_basic_accuracy_evaluation.py

# Research agent evaluation
python 03_research_agent_evaluation.py

# Test against real ACP agents
python 09_real_acp_agents.py

# Advanced: Trace recycling
python 11_trace_recycling_example.py
```

### Batch Running

```bash
# Run all examples in order  
for example in 0*.py 1*.py; do
    echo "Running $example..."
    python "$example"
done
```

## Configuration Options

### Environment Variables

The examples use these key environment variables:

```bash
# LLM Provider (openai, anthropic, ollama)
EVALUATION_PROVIDER=openai

# API Keys
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# Ollama (for local LLMs)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:30b-a3b
```

### Testing with Real Agents

The framework works with real ACP agents:

```python
# Connect to a running ACP agent
eval = AccuracyEval(agent="http://localhost:8000/agents/my-agent")

# Or use a callable agent
eval = AccuracyEval(agent=my_agent_function)
```

## Example Patterns

### Pattern 1: Quick Evaluation
```python
# From 01_minimal_example.py
from acp_evals import evaluate, AccuracyEval
result = evaluate(AccuracyEval(agent=agent), "What is 2+2?", "4")
```

### Pattern 2: Detailed Evaluation
```python
# From 02_basic_accuracy_evaluation.py
eval = AccuracyEval(agent=agent, rubric="factual")
result = await eval.run(
    input="Complex question",
    expected="Detailed answer",
    print_results=True  # Beautiful console output
)
```

### Pattern 3: Batch Evaluation
```python
# From 03_research_agent_evaluation.py
results = await eval.run_batch(
    test_data="test_cases.jsonl",
    parallel=True,
    progress=True
)
```

### Pattern 4: Multi-Agent Coordination
```python
# From 05_multi_agent_patterns.py
handoff_eval = HandoffEval(agents={"researcher": url1, "writer": url2})
result = await handoff_eval.run(
    task="Create report",
    expected_handoffs=["researcher->writer"]
)
```

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

1. **Start Simple**: Begin with `01_minimal_example.py`
2. **Use Real Agents**: Test with actual ACP agents or callable functions
3. **Monitor Costs**: Examples show token usage and costs
4. **Check Results**: Look for `results/` directory for detailed output
5. **Customize Rubrics**: Examples show how to create custom evaluation criteria

## Next Steps

- Read the [main documentation](../README.md)
- Explore [architecture guide](../docs/architecture.md)
- Create your own evaluations based on these patterns
- Join our [Discord](https://discord.gg/NradeA6ZNF) for help