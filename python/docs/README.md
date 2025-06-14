# ACP Evals Documentation

Welcome to the ACP Evals documentation. This directory contains detailed guides for using and extending the evaluation framework.

## Documentation Overview

### Getting Started
- **[Setup Guide](setup.md)** - Installation and configuration
- **[Architecture Overview](architecture.md)** - System design and components
- **[Provider Configuration](providers.md)** - Setting up LLM providers

### Core Features
- **[Continuous AI Integration](continuous-ai.md)** - CI/CD for AI agents
- **[Trace Recycling](trace-recycling.md)** - Convert production telemetry to evaluation datasets
- **[New Features Summary](new-features-summary.md)** - Latest enhancements and Azure parity features

### Key Concepts

#### Evaluation Types
1. **Accuracy Evaluation** - LLM-as-judge quality assessment
2. **Performance Evaluation** - Token usage and latency metrics
3. **Safety Evaluation** - Adversarial testing and bias detection
4. **Reliability Evaluation** - Tool usage validation

#### Dataset Types
1. **Gold Standard** - Production-ready multi-step tasks
2. **Adversarial** - Security and safety test scenarios
3. **External Benchmarks** - TRAIL, GAIA, SWE-Bench, etc.
4. **Recycled Traces** - Production telemetry converted to tests

#### Advanced Features
- **Continuous Evaluation Pipeline** - Automated testing with regression detection
- **Multi-Agent Patterns** - Linear, Supervisor, and Swarm architectures
- **Custom Evaluators** - Groundedness, Retrieval, Document Retrieval

## Quick Links

### For Developers
- [Examples Directory](../examples/) - Working code examples
- [API Reference](architecture.md#api-design) - Core API documentation
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

### For Operations
- [Trace Recycling Setup](trace-recycling.md#configuration-options)
- [Continuous Evaluation](new-features-summary.md#7-continuous-evaluation-pipeline)
- [Telemetry Integration](architecture.md#telemetry-layer)

## Recent Updates

See [New Features Summary](new-features-summary.md) for the latest enhancements including:
- TRAIL-inspired trace-based evaluation
- Azure AI Evaluation SDK feature parity
- Production trace recycling
- Enhanced adversarial testing

## Support

For questions and support:
- Check the [examples](../examples/) for common patterns
- Review the [architecture guide](architecture.md) for design decisions
- Open an issue on GitHub for bugs or feature requests