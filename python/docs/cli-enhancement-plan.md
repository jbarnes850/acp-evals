# CLI Enhancement Plan for ACP Evals

## Overview

This document outlines the comprehensive enhancement plan for the ACP Evals CLI, transforming it from a basic evaluation tool into a best-in-class CLI product for AI agent evaluation workflows.

## Design Principles

1. **Progressive Disclosure**: Simple commands for beginners, advanced options for experts
2. **ACP-Native**: Every command understands ACP agent manifests and protocols  
3. **Production-First**: Commands assume production use cases (traces, monitoring, CI)
4. **Multi-Agent Aware**: First-class support for agent coordination patterns
5. **Fast Feedback**: Quick commands that provide immediate value

## Command Structure

### Core Workflow Commands (Priority 1 - Today)

#### 1. `acp-evals test` - Quick Agent Testing
```bash
# Direct agent testing
acp-evals test <agent-url> [--quick|--comprehensive|--adversarial]
acp-evals test http://localhost:8000/agents/my-agent --quick

# Options:
--quick         # 3-5 basic test cases
--comprehensive # Full test suite with multiple evaluators
--adversarial   # Include security/robustness tests
--export        # Save results
```

#### 2. `acp-evals run` - Direct Evaluation
```bash
# Run specific evaluator
acp-evals run accuracy <agent> -i "What is 2+2?" -e "4"
acp-evals run performance <agent> -i "Complex task" --track-tokens
acp-evals run safety <agent> --adversarial-suite high

# Multi-agent
acp-evals run handoff agent1 agent2 --pattern linear
```

#### 3. `acp-evals discover` - Agent Discovery
```bash
# Discover available agents
acp-evals discover [--server http://localhost:8000]
acp-evals discover --test-all  # Run quick test on all discovered agents
```

### Dataset & Trace Commands (Priority 2)

#### 4. `acp-evals dataset` - Dataset Management
```bash
# List available datasets
acp-evals dataset list [--task-type qa|code|reasoning]

# Load external datasets
acp-evals dataset load GAIA --split test --export gaia-test.jsonl

# Create from traces
acp-evals dataset create --from-traces production.json --quality-threshold 0.8

# Analyze dataset quality
acp-evals dataset analyze my-dataset.jsonl --report quality.html
```

#### 5. `acp-evals traces` - Production Trace Ingestion
```bash
# Ingest traces
acp-evals traces ingest <file> --format [otel|acp|json]

# Recycle to dataset
acp-evals traces recycle --output eval-dataset.jsonl --count 100

# Extract patterns
acp-evals traces analyze --detect-patterns --export patterns.json
```

#### 6. `acp-evals generate` - Synthetic Data Generation
```bash
# Generate test cases
acp-evals generate tests --scenario [qa|research|code] --count 50

# Generate adversarial tests
acp-evals generate adversarial --severity [low|medium|high|critical]

# From templates
acp-evals generate from-template research-template.yaml
```

### Continuous Evaluation Commands (Priority 3)

#### 7. `acp-evals monitor` - Continuous Monitoring
```bash
# Start monitoring
acp-evals monitor <agent> --interval 1h --baseline v1.0

# View status
acp-evals monitor status [--agent <name>]

# Set alerts
acp-evals monitor alerts --regression-threshold 0.05 --notify webhook
```

#### 8. `acp-evals benchmark` - Comprehensive Benchmarking
```bash
# Run benchmark suite
acp-evals benchmark <agent> --suite [standard|comprehensive|production]

# Compare agents
acp-evals benchmark compare agent1 agent2 --dataset production

# Multi-agent patterns
acp-evals benchmark patterns --agents researcher,writer,critic
```

### Workflow & Integration Commands (Priority 4)

#### 9. `acp-evals workflow` - Multi-Agent Workflows
```bash
# Test workflow
acp-evals workflow test research-pipeline.yaml

# Validate workflow
acp-evals workflow validate --acp-manifest manifest.json

# Generate workflow template
acp-evals workflow init --pattern [linear|supervisor|swarm]
```

#### 10. `acp-evals ci` - CI/CD Integration
```bash
# CI mode
acp-evals ci --config .acp-evals.yml --fail-on-regression

# GitHub Action mode
acp-evals ci github --pr-comment --baseline main
```

### Analysis & Reporting (Enhanced)

#### 11. `acp-evals report` (Enhanced)
```bash
# Current + new options
acp-evals report results.json --format [summary|detailed|markdown|html]

# Trend analysis
acp-evals report trends --days 7 --metric [accuracy|latency|cost]

# Comparison
acp-evals report compare baseline.json current.json
```

#### 12. `acp-evals analyze` - Deep Analysis
```bash
# Cost analysis
acp-evals analyze cost --provider-comparison --optimization-tips

# Performance bottlenecks
acp-evals analyze performance --identify-bottlenecks

# Token efficiency
acp-evals analyze tokens --context-usage --recommendations
```

### Enhanced Init Command

#### 13. `acp-evals init` (Enhanced)
```bash
# Current templates + new ones
acp-evals init [simple|comprehensive|research|tool|acp-agent|multi-agent|workflow]

# Project scaffolding
acp-evals init project my-agent-evals --with-ci --with-datasets
```

## Implementation Timeline

### Today (for PyPI release)
1. ✅ Create implementation plan
2. ⬜ Implement `test` command
3. ⬜ Implement `run` command  
4. ⬜ Implement `discover` command
5. ⬜ Add `acp-agent` and `multi-agent` templates
6. ⬜ Update help text and documentation

### Next Release (Week 1)
7. ⬜ Implement `dataset` commands
8. ⬜ Implement `traces` commands
9. ⬜ Implement `generate` command
10. ⬜ Implement `workflow` command

### Future Releases
11. ⬜ Implement `monitor` command
12. ⬜ Implement `benchmark` command
13. ⬜ Implement `ci` command
14. ⬜ Implement `analyze` command

## Success Metrics

- **Adoption**: 80% of ACP developers use CLI for evaluation
- **Time to First Eval**: < 60 seconds from install to first result
- **Coverage**: Support for all major evaluation workflows
- **Satisfaction**: Positive feedback on usability and completeness

## Technical Considerations

1. **Async Support**: All commands should support async operations
2. **Error Handling**: Clear, actionable error messages
3. **Progress Indicators**: Rich progress bars for long operations
4. **Output Formats**: JSON, YAML, and human-readable outputs
5. **Extensibility**: Plugin architecture for custom commands

## Evaluation Workflow

The CLI creates a complete evaluation workflow:
- **Ingest** → `traces`/`dataset` commands
- **Create** → `generate`/`dataset` commands  
- **Evaluate** → `test`/`run`/`benchmark` commands
- **Analyze** → `report`/`analyze` commands
- **Monitor** → `monitor`/`ci` commands

This makes the CLI the primary interface for the entire agent evaluation lifecycle.