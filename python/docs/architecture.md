# Architecture Guide

## Overview

ACP Evals is designed with a layered architecture that balances simplicity for developers with powerful capabilities for production use. The framework follows the principles established in our [proposal](../../docs/acp-evals-proposal.md), implementing the key insights from multi-agent system research.

## Core Design Principles

1. **Token-First Metrics**: Every evaluation tracks token usage as the primary performance driver
2. **Multi-Agent Native**: Built specifically for evaluating agent coordination and handoffs
3. **Provider Agnostic**: Support for multiple LLM providers with automatic fallback
4. **Progressive Disclosure**: Simple API hides complexity, power users can access advanced features
5. **Production Ready**: Error handling, validation, telemetry, and cost tracking built-in

## Architecture Layers

```bash
┌─────────────────────────────────────────────────────────────┐
│                      Simple API Layer                       │
│  AccuracyEval, PerformanceEval, ReliabilityEval, SafetyEval │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Evaluation Core                          │
│        LLMJudge, Evaluators, Metrics, Benchmarks            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Provider Layer                           │
│     OpenAI, Anthropic, Ollama, etc. (Auto-detection)        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│    Validation, Exceptions, Logging, Telemetry, Config       │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Simple API Layer (`simple.py`)

The developer-facing API that provides the "zero to evaluation in < 5 lines" experience:

```python
# Evaluation classes
AccuracyEval    # LLM-as-judge quality evaluation
PerformanceEval # Token usage, latency, costs
ReliabilityEval # Tool usage, error handling
SafetyEval      # Composite safety checks

# Result containers
EvalResult      # Single evaluation result
BatchResult     # Multiple evaluation results

# Helper function
evaluate()      # Synchronous wrapper for async evaluation
```

### Evaluation Core

#### Evaluators (`evaluators/`)
- **LLMJudge**: Single-call evaluation with structured rubrics (based on Anthropic research)
- **Base**: Abstract evaluator interface for extensibility

#### Metrics (`metrics/`)
- **TokenUsageMetric**: Comprehensive token tracking with cost analysis
- **LatencyMetric**: Response time and throughput measurement  
- **ContextEfficiencyMetric**: Context window utilization (critical for multi-agent)
- **HandoffQualityMetric**: Information preservation across agent boundaries
- **CostMetric**: Real dollar costs with model-specific pricing

#### Benchmarks (`benchmarks/`)
- **ContextScalingBenchmark**: Test performance degradation with distractors
- **HandoffBenchmark**: Multi-agent coordination testing
- **PatternComparison**: Compare supervisor vs swarm architectures

#### Patterns (`patterns/`)
- **LinearPattern**: Sequential single-threaded execution
- **SupervisorPattern**: Centralized coordination
- **SwarmPattern**: Distributed agent collaboration

### Provider Layer (`providers/`)

Abstraction over LLM providers with automatic configuration:

```python
ProviderFactory.create("openai")     # Explicit provider
ProviderFactory.get_default_provider() # Auto-detect from environment
```

Features:
- Automatic fallback to mock mode
- Unified error handling
- Cost calculation per provider
- Token usage tracking
- Async-first design

### Infrastructure Layer

#### Configuration (`config.py`)
- Environment variable loading
- Provider auto-detection
- Default settings management

#### Validation (`validation.py`)
- Input sanitization
- Type checking
- Size limits
- Security checks

#### Exceptions (`exceptions.py`)
- Structured error hierarchy
- Helpful error messages
- Recovery suggestions
- Provider-specific errors

#### Logging (`logging_config.py`)
- Structured logging
- Cost tracking
- Performance monitoring
- Debug support

## Data Flow

### Single Evaluation Flow

```
User Input → Simple API → Validation → Agent Execution → 
→ Metric Collection → LLM Judge → Result Formatting → User Output
```

### Batch Evaluation Flow

```
Test Data → Batch Loader → Parallel/Sequential Execution →
→ Progress Tracking → Result Aggregation → Summary Report
```

### Multi-Agent Evaluation Flow

```
Agent Graph → Pattern Selection → Coordinated Execution →
→ Handoff Analysis → Context Tracking → Architecture Comparison
```

## Integration Points

### ACP Protocol

Native support for ACP communication:
- Message and MessagePart handling
- Event stream processing
- Telemetry integration
- Run management

### BeeAI Framework

Seamless integration with BeeAI components:
- Direct agent instance evaluation
- Workflow compatibility
- Shared telemetry
- Platform publishing

### External Tools

Extensible tool support:
- LangChain tools via adapters
- Model Context Protocol (MCP)
- Custom tool definitions
- Tool usage metrics

## Performance Considerations

### Token Optimization
- Batch processing to reduce overhead
- Context window monitoring
- Efficient prompt construction
- Result caching (when appropriate)

### Concurrency
- Async-first design throughout
- Configurable parallelism
- Resource pooling
- Timeout management

### Cost Management
- Real-time cost tracking
- Budget alerts
- Provider comparison
- Optimization recommendations

## Security

### Input Validation
- Size limits on all inputs
- Content sanitization
- Injection prevention
- Type enforcement

### API Key Management
- Environment variable best practices
- No keys in code or logs
- Secure error messages
- Provider isolation

### Data Privacy
- No automatic data collection
- Local evaluation options
- Configurable telemetry
- GDPR-friendly design

## Extensibility

### Adding New Evaluators

```python
class CustomEvaluator(Evaluator):
    async def evaluate(self, task, response, reference=None):
        # Custom evaluation logic
        return EvaluationResult(...)
```

### Adding New Providers

```python
class NewProvider(LLMProvider):
    async def complete(self, prompt, **kwargs):
        # Provider-specific implementation
        return LLMResponse(...)
```

### Adding New Metrics

```python
class CustomMetric(Metric):
    async def calculate(self, run, events):
        # Metric calculation logic
        return MetricResult(...)
```

## Best Practices

1. **Use Mock Mode for Development**: No API calls, fast iteration
2. **Start with Simple API**: Only drop to lower levels when needed
3. **Monitor Token Usage**: Primary driver of cost and performance
4. **Batch When Possible**: More efficient than individual evaluations
5. **Choose Appropriate Models**: Balance quality vs cost for evaluation

## Future Directions

Based on our proposal and ecosystem needs:

1. **Advanced Safety Evaluators**: Violence, hate speech, copyright
2. **Simulation Capabilities**: Synthetic data generation, adversarial testing
3. **MLOps Integration**: Experiment tracking, model registry support
4. **Cross-Framework Evaluation**: Test agents from any framework via ACP
5. **Real-time Monitoring**: Live evaluation during production

This architecture provides a solid foundation for comprehensive agent evaluation while maintaining the simplicity that makes it accessible to all developers in the ACP/BeeAI ecosystem.