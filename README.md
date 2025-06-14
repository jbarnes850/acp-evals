# ACP Evals

**Production-ready evaluation framework for agents in the ACP/BeeAI ecosystem**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

ACP Evals provides comprehensive evaluation tools for agents built with the Agent Communication Protocol (ACP). It enables developers to measure, benchmark, and improve agent performance with a focus on multi-agent systems, production metrics, and developer experience.

## Key Features

- 🚀 **Zero to evaluation in < 5 lines of code**
- 🤖 **Multi-agent focused** - Specialized metrics for agent coordination
- 🔌 **Multiple LLM providers** - OpenAI, Anthropic, Ollama, or mock mode
- 📊 **Production metrics** - Token usage, costs, latency tracking
- 🎯 **Built-in evaluators** - Accuracy, performance, reliability, safety

## Quick Start

```python
from acp_evals import evaluate, AccuracyEval

# Evaluate any agent with just 3 lines
result = evaluate(
    AccuracyEval(agent="http://localhost:8000/agents/my-agent"),
    input="What is the capital of France?",
    expected="Paris"
)
```

## Documentation

- 📚 [Full Documentation](./python/README.md)
- 🚀 [Getting Started](./python/docs/setup.md)
- 🏗️ [Architecture Guide](./python/docs/architecture.md)
- 🔧 [Provider Setup](./python/docs/providers.md)
- 💡 [Examples](./python/examples/)

## Installation

```bash
pip install acp-evals

# Or with specific provider support
pip install "acp-evals[openai]"
pip install "acp-evals[anthropic]"
pip install "acp-evals[all-providers]"
```

## Project Structure

```
acp-evals/
├── python/                 # Python implementation
│   ├── src/acp_evals/     # Core package
│   ├── tests/             # Test suite
│   ├── examples/          # Example scripts
│   └── docs/              # Documentation
└── internal-docs/         # Internal planning documents
```

## Contributing

We welcome contributions! Please see the [Python contributing guide](./python/CONTRIBUTING.md) for details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## Community

- 💬 [GitHub Discussions](https://github.com/i-am-bee/acp-evals/discussions)
- 🐛 [Issue Tracker](https://github.com/i-am-bee/acp-evals/issues)
- 💬 [Discord Community](https://discord.gg/NradeA6ZNF)

---

Part of the [BeeAI](https://github.com/i-am-bee) project, an initiative of the [Linux Foundation AI & Data](https://lfaidata.foundation/)