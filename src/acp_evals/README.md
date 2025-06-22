# ACP Evals Package Structure

This directory contains the core implementation of the ACP Evaluation Framework.

## Directory Structure

```
acp_evals/
├── __init__.py           # Package exports and version
├── api.py                # Simple, powerful agent evaluation API
│
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── base.py          # Base data models
│   ├── config.py        # Configuration management
│   ├── exceptions.py    # Custom exception hierarchy
│   └── validation.py    # Input validation
│
├── evaluators/          # The 3 core evaluation types
│   ├── __init__.py
│   ├── common.py        # Base evaluator and result classes
│   ├── accuracy.py      # LLM-as-judge accuracy evaluation
│   ├── performance.py   # Latency and throughput testing
│   ├── reliability.py   # Tool usage and error handling
│   └── llm_judge.py     # LLM judge implementation
│
├── providers/           # LLM provider implementations
│   ├── __init__.py
│   ├── base.py          # Abstract provider interface
│   ├── factory.py       # Provider factory and auto-detection
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── ollama_provider.py
│
├── cli/                 # Command-line interface
│   ├── __init__.py
│   ├── main.py          # CLI entry point
│   ├── display.py       # Rich terminal output
│   ├── check.py         # Environment checking
│   ├── templates.py     # Example code templates
│   └── commands/        # CLI commands
│       ├── discover.py  # Agent discovery
│       ├── quickstart.py # Quick start guide
│       ├── run.py       # Run single evaluation
│       └── test.py      # Run test suites
│
└── utils/               # Utilities
    ├── __init__.py
    └── logging.py       # Logging configuration
```

## Key Design Principles

1. **Simple by Default**: One-line evaluation with sensible defaults
2. **Powerful When Needed**: Progressive disclosure of advanced features
3. **Professional Focus**: Built for production AI systems
4. **BeeAI Native**: Optimized for the BeeAI/ACP ecosystem

## Usage

```python
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

# Test accuracy
eval = AccuracyEval("http://localhost:8000/agent")
result = await eval.run("What is 2+2?", "4")

# Test performance
perf = PerformanceEval("http://localhost:8000/agent")
result = await perf.run("Hello")

# Test reliability
reliable = ReliabilityEval("http://localhost:8000/agent")
result = await reliable.run("Use the search tool", expected_tools=["search"])
```