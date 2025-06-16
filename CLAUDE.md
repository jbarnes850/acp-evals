# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ACP Evals is a production-ready Python evaluation framework for multi-agent AI systems built on the Agent Communication Protocol (ACP). It's designed for testing and benchmarking AI agent performance, coordination, and safety in enterprise environments.

## Development Commands

### Python Package Management
```bash
# Development installation (from /python directory)
cd python/
pip install -e ".[dev,all-providers]"

# Install with specific providers only
pip install -e ".[dev,openai]"   # OpenAI only
pip install -e ".[dev,anthropic]" # Anthropic only
```

### Code Quality & Testing
```bash
# Run tests
cd python/
pytest

# Run tests with coverage
pytest --cov=src/acp_evals

# Lint and format code
ruff check src/ tests/
ruff format src/ tests/

# Type checking
pyright src/
```

### Build & Package
```bash
cd python/
python -m build
```

## Core Architecture

The framework follows a layered architecture with clear separation of concerns:

- **Simple API Layer** (`api.py`): Three-line evaluation interface for developers
- **Evaluation Core** (`evaluators/`): LLM judges, metrics, and built-in evaluators
- **Provider Abstraction** (`providers/`): OpenAI, Anthropic, Ollama integrations
- **Multi-Agent Patterns** (`patterns/`): Linear, Supervisor, Swarm coordination patterns
- **Benchmarking Suite** (`benchmarks/`): Datasets, trace recycling, gold standards
- **Infrastructure** (`core/`, `telemetry/`): Validation, logging, OpenTelemetry

### Key Components

**Evaluators** (`src/acp_evals/evaluators/`):
- `AccuracyEval`: LLM-as-judge with customizable rubrics
- `PerformanceEval`: Token usage, latency, cost tracking
- `SafetyEval`: Security and bias detection
- `HandoffEval`: Multi-agent information preservation

**CLI Interface** (`src/acp_evals/cli/`):
- `acp-evals test <agent>`: Quick agent testing
- `acp-evals run <evaluator> <agent>`: Single evaluations
- `acp-evals discover`: Agent discovery and health checks
- `acp-evals generate`: Synthetic test data creation
- `acp-evals workflow`: Multi-agent coordination testing

**Provider Support**:
- OpenAI (GPT-4.1, GPT-4.1-mini, o4-mini)
- Anthropic (Claude-4-Opus, Claude-4-Sonnet) 
- Ollama (local models)
- Mock mode for testing

## Configuration

### Environment Setup
Copy `python/.env.example` to `python/.env` and configure:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

### Key Settings
- **Line Length**: 100 characters (Ruff)
- **Python Version**: 3.11+ required
- **Entry Point**: `acp-evals` CLI command
- **Package Structure**: `src/acp_evals/` layout

## Multi-Agent Focus

This framework specializes in multi-agent evaluation - unique capabilities include:

- **Handoff Quality Metrics**: Information preservation across agent transitions
- **Coordination Patterns**: Linear, Supervisor, Swarm pattern evaluation
- **Context Maintenance**: Cross-agent context analysis
- **ACP Protocol Integration**: Native support for Agent Communication Protocol

## Production Features

- **Trace Recycling**: Convert production telemetry to evaluation datasets
- **Continuous Evaluation**: Automated regression detection
- **OpenTelemetry Export**: Real-time metrics to observability platforms
- **Cost Tracking**: Multi-provider cost analysis and optimization

## Testing Approach

- **Pytest** with async support (`pytest-asyncio`)
- **Mock Framework** for testing without API calls
- **Coverage Reporting** with `pytest-cov`
- **Real Agent Validation** for integration testing

## Examples Directory

The `python/examples/` directory contains 13 comprehensive usage examples covering:
- Basic evaluation patterns
- Multi-agent coordination
- Production integration
- Adversarial testing
- Synthetic data generation
- CI/CD integration

## Key Design Patterns

- **Async-first**: All evaluations support async/await
- **Provider Agnostic**: Unified interface across LLM providers
- **Extensible**: Plugin architecture for custom evaluators
- **Production Ready**: Cost tracking, telemetry, error handling
- **Enterprise Focus**: Professional interface, no decorative elements