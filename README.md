<p align="center">

# ACP Evals

**Open-Source, Research-Driven Evaluation Framework for ACP Agents and Multi-Agent Systems**

<a href="https://www.python.org">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python" />
</a>
<a href="https://agentcommunicationprotocol.dev">
  <img src="https://img.shields.io/badge/ACP-Compatible-green.svg" alt="ACP Compatible" />
</a>
<a href="https://opensource.org/licenses/Apache-2.0">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License" />
</a>

<br/>

<a href="./python/docs">Documentation</a> • 
<a href="./python/examples">Examples</a> • 
<a href="#command-line-interface">CLI Reference</a> • 
<a href="./python/CONTRIBUTING.md">Contributing</a>

</p>

---

**ACP Evals** is an open-source, research-driven framework for evaluating AI agents and multi-agent systems—built to set the new standard for reliability, safety, and continuous improvement in agent workflows.

---

**Agent evaluation is evolving.**

- Traditional tools focus on single-model accuracy, but modern agent systems demand more:
  - Multi-agent coordination
  - Tool use and context preservation
  - Production-grade reliability and safety
  - Continuous, in-context feedback for developers

ACP Evals brings these capabilities to every developer, making advanced evaluation as easy as writing a unit test.

---

## Quick Start:

**Install ACP Evals:**
```bash
pip install acp-evals
```

**Configure your providers (OpenAI, Anthropic, etc):**
```bash
cp python/.env.example .env
# Edit .env and add your API keys
```

**Check your setup:**
```bash
acp-evals check
```

**Discover available agents:**
```bash
acp-evals discover
```

**Run a quick test on your agent:**
```bash
acp-evals test http://localhost:8000/agents/my-agent
```

**Run a comprehensive evaluation suite:**
```bash
acp-evals test http://localhost:8000/agents/my-agent --comprehensive
```

**Generate synthetic test data:**
```bash
acp-evals generate tests --scenario qa --count 50 --export tests.jsonl
```

**Evaluate a multi-agent workflow:**
```bash
acp-evals workflow test --pattern supervisor --agents agent1,agent2,agent3 --task "Research and summarize AI trends"
```

**Get help for any command:**
```bash
acp-evals --help
acp-evals <command> --help
```

---

## How ACP Evals Fits Into the ACP Ecosystem

ACP Evals is designed to integrate seamlessly with the Agent Communication Protocol (ACP) stack:

- **Discover:** Find and register agents and tools across your environment.
- **Run:** Evaluate agents using a variety of LLM providers and real-world scenarios.
- **Compose:** Test multi-agent workflows, handoffs, and coordination patterns.
- **Build:** Develop, extend, and benchmark agents in Python or TypeScript, leveraging ACP's modular architecture.

This layered approach ensures that evaluation is a first-class part of the agent development lifecycle, from discovery to production.

---

## Practical Example: Real ACP Agent Evaluation

See [`examples/09_real_acp_agents.py`](examples/09_real_acp_agents.py) for a full workflow that:
- Discovers available ACP agents
- Runs health checks and basic evaluations
- Benchmarks accuracy, performance, and safety
- Generates a comprehensive report for your agent ecosystem

---

## Troubleshooting

If you run into issues, see [docs/troubleshooting.md](docs/troubleshooting.md) for solutions to common problems.

---

## Core Features

- **Quality & Performance:**
  - LLM-as-judge scoring, token/cost tracking, latency, groundedness, retrieval metrics
- **Multi-Agent Coordination:**
  - Linear, supervisor, and swarm patterns; handoff quality; workflow-level evaluation
- **Safety & Reliability:**
  - Content filtering, bias/harm checks, adversarial and edge-case testing
- **Production Integration:**
  - Trace recycling, continuous evaluation, OpenTelemetry export, CI/CD hooks
- **Extensible & Modular:**
  - Plug in new evaluators, providers, patterns, and datasets

---

## Core Workflow Integrations

- **Auto-synthesized edge-case evals** from live logs (cf. Agent Bricks)
- **Inline diff and conversational feedback** (cf. Loop/Braintrust)
- **Design-time, in-context evaluation:**
  - Treat evals like unit tests—see results instantly, fix failures before merge
- **Continuous optimization:**
  - Pareto-front tuning for cost vs. quality, nightly retraining from prod traces

---

## High-Level Architecture

```mermaid
flowchart TD
    subgraph Developer
      CLI[CLI / VS Code Plugin]
      API[Python API]
    end
    CLI -- "Run Evals, Generate Data" --> Core
    API -- "Programmatic Access" --> Core

    subgraph ACP_Evals_Core["ACP Evals Core"]
      Core[Evaluation Orchestrator]
      Evaluators[Evaluators: Quality, Safety, Coordination]
      Patterns[Coordination Patterns: Linear, Supervisor, Swarm]
      Providers[LLM Providers: OpenAI, Anthropic, Ollama, Mock]
      Datasets[Datasets & Benchmarks]
      Telemetry[Telemetry & Monitoring]
    end

    Core -- "Agent Calls, Trace Ingest" --> ACP[ACP Agents / BeeAI]
    Core -- "Export Metrics" --> Telemetry
    Core -- "Store Results" --> Datasets
    Core -- "Integrate" --> Providers
    Core -- "Pattern Execution" --> Patterns
    Core -- "Eval Logic" --> Evaluators
```

---

## Example: Multi-Agent Evaluation

```python
from acp_evals.patterns import SupervisorPattern
from acp_evals.benchmarks import HandoffBenchmark

pattern = SupervisorPattern(["researcher", "analyzer", "writer"])
benchmark = HandoffBenchmark(pattern=pattern, endpoint="http://localhost:8000")
results = await benchmark.run_batch(
    test_data="coordination_tasks.jsonl",
    parallel=True,
    export="results.json"
)
```

---

## Production & Monitoring

- **Trace recycling:** Convert real user interactions into eval datasets
- **Continuous evaluation:** Automated, scheduled assessments for drift and regression
- **OpenTelemetry export:** Integrate with Jaeger, Phoenix, and other dashboards
- **CI/CD integration:**
  ```bash
  acp-evals test $AGENT_URL --comprehensive --export results.json
  acp-evals report results.json --format markdown > report.md
  ```

---

## Extending ACP Evals

- **Add custom evaluators:** [`python/src/acp_evals/evaluators/`](./python/src/acp_evals/evaluators/)
- **New LLM providers:** [`python/src/acp_evals/providers/`](./python/src/acp_evals/providers/)
- **Coordination patterns:** [`python/src/acp_evals/patterns/`](./python/src/acp_evals/patterns/)
- **Benchmarks/datasets:** [`python/src/acp_evals/benchmarks/datasets/`](./python/src/acp_evals/benchmarks/datasets/)

See [Contributing Guide](./python/CONTRIBUTING.md) for details.

---

## Community & Support

- **Docs:** [API Reference](./python/docs/), [Examples](./python/examples/)
- **Discussions:** [ACP Protocol](https://github.com/i-am-bee/beeai-platform/discussions/284)
- **Contribute:** [CONTRIBUTING.md](./python/CONTRIBUTING.md)
- **Part of [BeeAI](https://github.com/i-am-bee) / [Linux Foundation AI & Data](https://lfaidata.foundation/)**

---

## References & Further Reading

- [Agent Bricks | Databricks](https://www.databricks.com/product/artificial-intelligence/agent-bricks)
- [Introducing Agent Bricks: Auto-Optimized Agents](https://www.databricks.com/blog/introducing-agent-bricks?utm_source=chatgpt.com)
- [Databricks Launches Agent Bricks](https://www.databricks.com/company/newsroom/press-releases/databricks-launches-agent-bricks-new-approach-building-ai-agents?utm_source=chatgpt.com)
- [Loop - Docs - Braintrust](https://www.braintrust.dev/docs/guides/loop)
- [Visualize and interpret evaluations - Braintrust](https://www.braintrust.dev/docs/guides/evals/interpret?utm_source=chatgpt.com)
- [ACP Protocol](https://agentcommunicationprotocol.dev)
- [MCP: Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)
- [NLIP Specification](https://github.com/nlip-project/documents/blob/main/NLIP%5FSpecification.pdf)
- [ACDP: Agent Communication & Discovery Protocol](https://github.com/zerocmd/acdp/blob/main/ACDP.md)

---

## License

Apache License 2.0 – see [LICENSE](./LICENSE).

---

**_ACP Evals: The open, extensible backbone for agent reliability, benchmarking, and governance. Build, test, and ship agents with confidence._**
