# ACP Evals

**Production-ready evaluation framework for ACP agents and multi-agent systems**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[Documentation](./python/docs) • [Examples](./python/examples) • [CLI Reference](#command-line-interface) • [Contributing](./python/CONTRIBUTING.md)

ACP Evals is a comprehensive evaluation framework designed specifically for developers building AI agents with the Agent Communication Protocol (ACP). When you deploy agents to production, you need to measure whether they're working correctly, efficiently, and safely. This framework provides systematic testing and monitoring capabilities that scale from simple accuracy checks to complex multi-agent coordination analysis.

Agent evaluation involves sending test inputs to your agents and automatically scoring the outputs against expected results. Traditional evaluation tools focus on single AI models, but ACP Evals specializes in the unique challenges of agent systems: measuring how well agents use tools, preserve context across conversations, coordinate with other agents, and maintain performance under production workloads.

The framework implements a progressive disclosure design. You can start with a simple three-line evaluation to test basic functionality, then gradually access more sophisticated features like multi-agent workflow testing, production trace analysis, and continuous monitoring pipelines. Every evaluation automatically tracks token usage and costs across different LLM providers, helping you optimize both quality and efficiency as you scale.

## Quick Start

**Three-line evaluation:**
```python
from acp_evals import evaluate, AccuracyEval

result = evaluate(
    AccuracyEval(agent="http://localhost:8000/agents/my-agent"),
    input="What is the capital of France?", 
    expected="Paris"
)
print(f"Score: {result.score:.2f}, Tokens: {result.tokens}")
```

**CLI workflow:**
```bash
# Provider setup and health check
acp-evals check

# Quick agent testing
acp-evals test http://localhost:8000/agents/my-agent --comprehensive

# Generate synthetic test data with LLM
acp-evals generate tests --scenario qa --count 50 --export tests.jsonl

# Multi-agent workflow testing
acp-evals workflow test --pattern supervisor --agents agent1,agent2,agent3
```

### Installation & Setup

```bash
# Install framework
pip install acp-evals

# Configure providers (copy from python/.env.example)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Verify setup
acp-evals check
```

## Core Capabilities

ACP Evals provides four main categories of evaluation capabilities that address the fundamental needs of agent developers. Each category serves a specific purpose in ensuring your agents work reliably in production environments.

**Quality and Performance Evaluation** focuses on measuring how well your agents respond to inputs and how efficiently they use computational resources. The AccuracyEval component uses LLM-as-judge methodology to score response quality against customizable rubrics for different domains like factual accuracy, research quality, or code correctness. PerformanceEval tracks token usage, response latency, and costs across different LLM providers, giving you detailed insights into resource consumption. The framework also includes GroundednessEval for validating that agent responses stay grounded in provided context, and RetrievalEval for measuring information retrieval quality using standard IR metrics like precision, recall, and NDCG.

**Multi-Agent Coordination Testing** addresses the unique challenges of systems where multiple agents work together. This includes handoff quality measurement, which evaluates how much relevant information is preserved when one agent passes control to another. The framework supports testing three primary coordination patterns: Linear (sequential agent execution), Supervisor (centralized coordination with specialized agents), and Swarm (distributed collaboration). Workflow testing validates end-to-end multi-agent processes to ensure the entire system maintains coherence and effectiveness.

**Safety and Reliability Assessment** ensures your agents behave appropriately and handle edge cases gracefully. SafetyEval combines multiple safety checks including content filtering, bias detection, and harmful output classification. ReliabilityEval validates that agents use tools correctly and handle error conditions appropriately. The framework includes comprehensive adversarial testing capabilities that test resistance to real-world attack patterns like prompt injection, jailbreaks, and context manipulation attempts.

### Multi-Agent Evaluation

```python
from acp_evals.patterns import SupervisorPattern
from acp_evals.benchmarks import HandoffBenchmark

# Test multi-agent coordination
pattern = SupervisorPattern(["researcher", "analyzer", "writer"])
benchmark = HandoffBenchmark(pattern=pattern, endpoint="http://localhost:8000")

results = await benchmark.run_batch(
    test_data="coordination_tasks.jsonl",
    parallel=True,
    export="results.json"
)
```

## Command Line Interface

The CLI provides complete evaluation workflows from discovery to production monitoring:

```bash
# Agent discovery and health
acp-evals discover                    # Find available ACP agents
acp-evals check                       # Provider configuration health

# Quick testing and evaluation
acp-evals test <agent-url> --comprehensive
acp-evals run accuracy <agent> -i "input" -e "expected"

# Dataset management and generation
acp-evals dataset list                # External benchmarks (TRAIL, GAIA, SWE-bench)
acp-evals dataset create-suite -d TRAIL -d GAIA -e mixed_suite.jsonl
acp-evals generate tests --scenario research --count 100

# Multi-agent workflow testing
acp-evals workflow test --pattern supervisor --agents agent1,agent2,agent3
acp-evals workflow compare --agents agent1,agent2 --task "research task"

# Production integration
acp-evals traces ingest production.json
acp-evals traces recycle --output dataset.jsonl
acp-evals report results.json --format summary
```

## Advanced Features

Beyond basic evaluation capabilities, ACP Evals provides sophisticated features for production deployment and continuous monitoring that transform it from a development tool into a comprehensive production monitoring system.

**Production Integration and Monitoring** enables you to maintain agent quality after deployment. Trace recycling converts production telemetry data from real user interactions into evaluation datasets, allowing you to continuously validate agent performance using actual usage patterns. The continuous evaluation system runs automated assessments on scheduled intervals, detecting performance regressions and quality drift over time by comparing current results against established baselines. All evaluation metrics can be exported to OpenTelemetry-compatible monitoring systems like Jaeger or Phoenix for real-time dashboard visualization and alerting.

**Comprehensive Dataset and Benchmarking Support** provides access to established evaluation datasets and the ability to create custom test suites. The framework integrates with major external benchmarks including TRAIL for trace debugging, GAIA for multi-step reasoning, SWE-Bench for software engineering tasks, MMLU for broad knowledge assessment, and HumanEval for code generation. It also includes gold standard datasets designed specifically for production-realistic multi-step agent tasks. The synthetic data generation capabilities use LLMs to create high-quality test cases tailored to your specific use cases and domains.

**Security and Robustness Testing** protects against real-world threats and edge cases. The adversarial testing framework evaluates agent resistance to actual attack patterns observed in production systems, including sophisticated prompt injection attempts, jailbreak techniques, and context manipulation strategies. The edge case generation system creates synthetic scenarios that stress-test agent behavior under unusual or challenging conditions, helping identify potential failure modes before they occur in production.

## Provider Support

| Provider | Models | Features |
|----------|--------|----------|
| **OpenAI** | GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, o4-mini | Cost tracking, token optimization |
| **Anthropic** | Claude-4-Opus, Claude-4-Sonnet | Native integration, cost analysis |  
| **Ollama** | granite3.3:8b, qwen3:30b-a3b, custom models | Local deployment, privacy-first |
| **Mock Mode** | Simulated responses for testing | CI/CD integration, rapid iteration |

## ACP/BeeAI Integration

**Native ACP Support:**
- **[ACP Message Handling](./python/src/acp_evals/evaluators/common.py)** - Direct ACP SDK integration for agent communication
- **[Multi-Agent Patterns](./python/src/acp_evals/patterns/)** - Built-in support for ACP coordination patterns
- **[Event Stream Analysis](./python/examples/09_real_acp_agents.py)** - Real-time evaluation of agent interactions
- **[BeeAI Framework](./python/examples/10_acp_agent_discovery.py)** - Seamless integration with BeeAI agent instances


## Examples & Documentation

| Resource | Description |
|----------|-------------|
| [Examples](./python/examples/) | 13 comprehensive usage examples |
| [API Reference](./python/docs/) | Complete API documentation |
| [CLI Reference](./python/src/acp_evals/cli/) | Command-line interface guide |
| [Architecture](./python/docs/architecture.md) | Framework design and extension points |

**Essential Examples:**
- [00_minimal_example.py](./python/examples/00_minimal_example.py) - 3-line agent evaluation
- [01_quickstart_accuracy.py](./python/examples/01_quickstart_accuracy.py) - Basic accuracy assessment  
- [05_multi_agent_patterns.py](./python/examples/05_multi_agent_patterns.py) - Multi-agent coordination testing

**Production Examples:**
- [09_real_acp_agents.py](./python/examples/09_real_acp_agents.py) - Live ACP agent integration
- [12_end_to_end_trace_pipeline.py](./python/examples/12_end_to_end_trace_pipeline.py) - Production trace recycling
- [08_ci_cd_integration.py](./python/examples/08_ci_cd_integration.py) - CI/CD monitoring pipeline

## Batch Evaluation & CI/CD

**Batch Processing:**
```python
# Evaluate multiple test cases in parallel
results = AccuracyEval(agent=my_agent).run_batch(
    test_data="test_cases.jsonl",
    parallel=True,
    export="results.json"
)
print(f"Pass rate: {results.pass_rate}%, Score: {results.avg_score:.2f}")
```

**CI/CD Integration:**
```python
def test_agent_accuracy():
    eval = AccuracyEval(agent=my_agent, mock_mode=CI_ENV)
    result = eval.run(input="test", expected="expected")
    assert result.score > 0.8, f"Score {result.score} below threshold"
```

**CLI Automation:**
```bash
# Run comprehensive evaluation in CI
acp-evals test $AGENT_URL --comprehensive --export results.json
acp-evals report results.json --format markdown > report.md
```

## Results & Debugging

**Consistent Result Structure:**
```python
result = eval.run(input="test", expected="expected")

print(f"Score: {result.score}")      # 0.0-1.0
print(f"Passed: {result.passed}")    # Boolean  
print(f"Tokens: {result.tokens}")    # Usage breakdown
print(f"Latency: {result.latency_ms}ms")
print(f"Details: {result.details}")  # Specific feedback
```

**Debugging:**
```python
if result.score < 0.7:
    print(result.details.get("judge_reasoning"))
    print(result.details.get("issues", []))
```

**Troubleshooting:**
```bash
# Provider issues
acp-evals check --test-connection

# Agent connectivity  
curl http://localhost:8000/agents/my-agent/health

# Performance optimization
acp-evals test agent --comprehensive --parallel --batch-size 10
```

## Framework Architecture

```bash
python/src/acp_evals/
├── api.py                   # 3-line developer API
├── evaluators/              # Quality, performance, safety evaluators
├── patterns/                # Multi-agent coordination (linear, supervisor, swarm)
├── benchmarks/datasets/     # TRAIL, GAIA, SWE-bench integration + gold standard data
├── providers/               # OpenAI, Anthropic, Ollama support
├── evaluation/              # Continuous evaluation and synthetic data generation
├── telemetry/               # OpenTelemetry export and production monitoring
└── cli/                     # Complete command-line toolkit
```

**Extension Points:**
- Add custom evaluators in `evaluators/`
- Implement new LLM providers in `providers/`
- Create coordination patterns in `patterns/`
- Integrate external benchmarks in `benchmarks/datasets/`

See [Contributing Guide](./python/CONTRIBUTING.md) for development setup and guidelines.

## License

Apache License 2.0 - see [LICENSE](./LICENSE) file.

Part of the [BeeAI](https://github.com/i-am-bee) project, an initiative of [Linux Foundation AI & Data](https://lfaidata.foundation/).