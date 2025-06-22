# ACP Evals Examples

This directory contains example scripts demonstrating how to use acp-evals.

## Agent Examples

### test_agent.py
Contains three Python function agents for testing:
- `smart_agent`: General purpose Q&A agent
- `calculator_agent`: Mathematical calculations with fast response time  
- `research_agent`: Simulates tool usage (search, summarize) for research tasks

```bash
# Use with CLI
acp-evals run accuracy examples/test_agent.py:smart_agent -i "What is AI?" -e "Artificial Intelligence"
acp-evals run performance examples/test_agent.py:calculator_agent -i "Calculate 25% of 80"
acp-evals run reliability examples/test_agent.py:research_agent -i "Search for news" --expected-tools search
```

### beeai_acp_server.py
Example BeeAI framework agent with ACP server integration.

**Prerequisites:**
```bash
pip install beeai-framework
ollama pull granite3.3:8b
```

**Running:**
```bash
python examples/beeai_acp_server.py
```

## Evaluation Examples

### accuracy_eval.py
Demonstrates programmatic accuracy evaluation:
- Uses LLM-as-judge methodology
- Shows batch evaluation capabilities
- Beautiful terminal output with detailed feedback

```bash
python examples/accuracy_eval.py
```

### performance_eval.py
Demonstrates performance evaluation:
- Measures latency and memory usage
- Shows statistical analysis across multiple runs
- Provides UX impact assessment

```bash
python examples/performance_eval.py
```

### reliability_eval.py
Demonstrates reliability evaluation:
- Tests tool usage detection
- Evaluates consistency across runs
- Shows error handling capabilities

```bash
python examples/reliability_eval.py
```

## Quick Start

1. **Test Python functions directly:**
```bash
acp-evals comprehensive examples/test_agent.py:smart_agent -i "What is machine learning?" -e "Machine learning is a subset of AI" --show-details
```

2. **Run evaluation examples:**
```bash
python examples/accuracy_eval.py
python examples/performance_eval.py
python examples/reliability_eval.py
```

3. **Batch evaluation:**
```bash
cat > tests.jsonl << 'EOF'
{"input": "What is 2+2?", "expected": "4"}
{"input": "Capital of France?", "expected": "Paris"}
EOF

acp-evals run accuracy examples/test_agent.py:smart_agent --test-file tests.jsonl
```

## Notes

- All examples work out of the box with configured LLM providers
- The test_agent.py functions can be used directly with the CLI
- Example scripts demonstrate both programmatic API and beautiful terminal output
- Designed for professional software engineers building production AI systems