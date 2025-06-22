# ACP Evals Demo Script

## 1. Initial Setup & Configuration

```bash
# Show current directory
pwd

# Check provider configuration
acp-evals check

# List available evaluation rubrics
acp-evals list-rubrics
```

## 2. Accuracy Evaluation

```bash
# Basic accuracy test with Python function
acp-evals run accuracy examples/test_agent.py:smart_agent -i "What is 2+2?" -e "4"

# More complex accuracy test
acp-evals run accuracy examples/test_agent.py:smart_agent -i "What is the capital of France?" -e "Paris"

# Test with factual rubric (detailed output)
acp-evals run accuracy examples/test_agent.py:smart_agent -i "What is machine learning?" -e "Machine learning is a subset of AI" --show-details
```

## 3. Performance Evaluation

```bash
# Basic performance test
acp-evals run performance examples/test_agent.py:calculator_agent -i "Calculate 25% of 80"

# Performance with memory tracking
acp-evals run performance examples/test_agent.py:smart_agent -i "Explain quantum computing" --track-memory

# Multiple iterations for statistical significance
acp-evals run performance examples/test_agent.py:calculator_agent -i "Calculate 5 factorial" --iterations 10
```

## 4. Reliability Evaluation

```bash
# Test with expected tool usage
acp-evals run reliability examples/test_agent.py:research_agent -i "Search for latest AI news and summarize it" --expected-tools search summarize

# Test consistency
acp-evals run reliability examples/test_agent.py:smart_agent -i "Generate a greeting" --test-consistency
```

## 5. Comprehensive Evaluation (All Three Dimensions)

```bash
# Run all evaluations at once
acp-evals comprehensive examples/test_agent.py:smart_agent -i "What is machine learning?" -e "Machine learning is a subset of AI" --show-details

# Another comprehensive test
acp-evals comprehensive examples/test_agent.py:research_agent -i "Explain quantum computing" -e "Quantum computing uses quantum mechanics principles"
```

## 6. Quick Test Command

```bash
# Quick functionality test
acp-evals test examples/test_agent.py:smart_agent

# Test different agents
acp-evals test examples/test_agent.py:calculator_agent
acp-evals test examples/test_agent.py:research_agent
```

## 7. Batch Evaluation

```bash
# Create test cases file
cat > test_cases.jsonl << 'EOF'
{"input": "What is 2+2?", "expected": "4"}
{"input": "What is the capital of France?", "expected": "Paris"}
{"input": "Is 11 a prime number?", "expected": "Yes"}
{"input": "What is machine learning?", "expected": "Machine learning is a subset of AI"}
EOF

# Run batch evaluation
acp-evals run accuracy examples/test_agent.py:smart_agent --test-file test_cases.jsonl

# Export results to JSON
acp-evals run accuracy examples/test_agent.py:smart_agent --test-file test_cases.jsonl --export results.json

# View results
cat results.json | jq .summary

# Clean up
rm test_cases.jsonl results.json
```

## 8. Using Different Judge Models

```bash
# Using Anthropic Claude (if configured)
acp-evals run accuracy examples/test_agent.py:smart_agent -i "Explain DNA" -e "DNA stores genetic information" --judge-model claude-sonnet-4

# Using Ollama local model
acp-evals run accuracy examples/test_agent.py:smart_agent -i "Hello" -e "Hi there" --judge-model ollama:qwen3:8b
```

## 9. Running Example Evaluation Scripts

```bash
# Run standalone accuracy evaluation
python examples/accuracy_eval.py

# Run performance evaluation
python examples/performance_eval.py

# Run reliability evaluation
python examples/reliability_eval.py
```

## Key Demo Points

1. **Latest Models**: Shows gpt-4o (OpenAI) and qwen3:8b (Ollama)
2. **Rich TUI Display**: Beautiful terminal UI with progress bars and color coding
3. **LLM Judge Analysis**: Detailed reasoning and scoring explanations
4. **Performance Metrics**: Latency analysis with UX impact assessment
5. **Tool Usage Detection**: Reliability eval detects actual tool calls
6. **Python Function Support**: Seamless evaluation of Python functions as agents
7. **Comprehensive Mode**: All three dimensions evaluated together
8. **Batch Testing**: Scale to multiple test cases with export functionality

## Quick 5-Minute Demo Commands

```bash
# 1. Setup
acp-evals check

# 2. Accuracy
acp-evals run accuracy examples/test_agent.py:smart_agent -i "What is 2+2?" -e "4"

# 3. Performance
acp-evals run performance examples/test_agent.py:calculator_agent -i "Calculate 25% of 80" --track-memory

# 4. Reliability
acp-evals run reliability examples/test_agent.py:research_agent -i "Search for AI news" --expected-tools search

# 5. Comprehensive
acp-evals comprehensive examples/test_agent.py:smart_agent -i "What is AI?" -e "Artificial Intelligence" --show-details
```

## Notes

- All examples use Python functions which work perfectly with acp-evals
- The test_agent.py file contains three agent functions:
  - `smart_agent`: General purpose Q&A agent
  - `calculator_agent`: Mathematical calculations
  - `research_agent`: Simulates tool usage for research tasks
- Each evaluation type provides detailed, actionable feedback
- The framework is designed for professional software engineers building production AI systems