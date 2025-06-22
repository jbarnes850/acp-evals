# ACP Evals Demo Commands

## Setup (Terminal 1)

```bash
# 1. Check configuration
acp-evals check

# 2. List available rubrics
acp-evals list-rubrics
```

## Start Server (Terminal 2)

```bash
# Start the simple ACP server
python examples/simple_acp_server.py
```

## Demo Commands (Terminal 1)

```bash
# 3. Discover agents
acp-evals discover --server http://localhost:8002

# 4. Accuracy evaluation - Simple
acp-evals run accuracy http://localhost:8002/agents/simple_agent -i "What is 2+2?" -e "4"

# 5. Accuracy evaluation - Python function
acp-evals run accuracy examples/test_agent.py:smart_agent -i "What is the capital of France?" -e "Paris"

# 6. Performance evaluation
acp-evals run performance examples/test_agent.py:calculator_agent -i "Calculate 25% of 80" --track-memory

# 7. Reliability evaluation
acp-evals run reliability examples/test_agent.py:research_agent -i "Search for latest AI news and summarize it" --expected-tools search summarize

# 8. Comprehensive evaluation (all 3 dimensions)
acp-evals comprehensive examples/test_agent.py:smart_agent -i "What is machine learning?" -e "Machine learning is a subset of AI" --show-details

# 9. Quick test
acp-evals test http://localhost:8002/agents/simple_agent

# 10. Batch evaluation
cat > test_cases.jsonl << 'EOF'
{"input": "What is 2+2?", "expected": "4"}
{"input": "Capital of France?", "expected": "Paris"}
{"input": "What is AI?", "expected": "Artificial Intelligence"}
EOF

acp-evals run accuracy examples/test_agent.py:smart_agent --test-file test_cases.jsonl --export results.json

# Clean up
rm test_cases.jsonl results.json
```

## Key Points to Highlight

1. **Provider Setup** - Shows configured providers (OpenAI, Anthropic, Ollama)
2. **Multiple Agent Formats** - HTTP agents and Python functions
3. **Rich TUI** - Beautiful terminal UI with progress bars and detailed feedback
4. **LLM Judge** - Detailed scoring explanations
5. **Performance Metrics** - Latency, memory, and UX impact
6. **Tool Detection** - Reliability eval detects actual tool usage
7. **Comprehensive Mode** - All three evaluations in one command
8. **Batch Testing** - Scale to multiple test cases

## Quick 5-Minute Demo Path

```bash
# 1. Setup check
acp-evals check

# 2. Start server (in another terminal)
python examples/simple_acp_server.py

# 3. Accuracy test
acp-evals run accuracy examples/test_agent.py:smart_agent -i "What is 2+2?" -e "4"

# 4. Performance test  
acp-evals run performance examples/test_agent.py:calculator_agent -i "Calculate 100!" --track-memory

# 5. Comprehensive test
acp-evals comprehensive examples/test_agent.py:research_agent -i "Explain quantum computing" -e "Quantum computing uses quantum mechanics" --show-details
```