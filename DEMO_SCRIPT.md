# ACP Evals Live Demo Script

## Overview
ACP Evals is an open-source, research-driven evaluation framework for AI agents and multi-agent systems. This demo showcases its capabilities from simple single-agent testing to complex multi-agent orchestration.

---

## Pre-Demo Setup

```bash
# Ensure you have the latest version installed
pip install -U acp-evals

# Set up your environment (have .env file ready with API keys)
cp .env.example .env
# Add your OpenAI/Anthropic API keys to .env

# Verify your setup
acp-evals check --test-connection
```

**Expected Output**: Green checkmarks for configured providers

---

## Demo Flow

### Part 1: Zero to Evaluation in 30 Seconds

**Message**: "Let's see how easy it is to get started with ACP Evals"

```bash
# 1. Check available evaluation rubrics
acp-evals list-rubrics
```

**Expected Output**: List of rubrics (factual, research_quality, code_quality, etc.)

```bash
# 2. Run your first evaluation with real agent
acp-evals run accuracy http://localhost:8000/agents/qa_agent \
  -i "What is the capital of France?" \
  -e "Paris"
```

**Expected Output**: 
- Score: 1.0 ✓
- Clear pass/fail indicator
- Execution time and token usage

**Key Points**:
- Single command evaluation
- Beautiful terminal output
- Immediate feedback

---

### Part 2: Discovering and Testing ACP Agents

**Message**: "ACP Evals integrates seamlessly with the ACP ecosystem"

```bash
# 1. Discover available agents
acp-evals discover --server http://localhost:8000
```

**Expected Output**: Table of discovered agents with names, URLs, and capabilities

```bash
# 2. Quick test all discovered agents
acp-evals discover --test-all --export discovered-agents.json
```

**Expected Output**: 
- Progress bar showing tests
- Summary table with pass/fail for each agent
- JSON export confirmation

```bash
# 3. Run comprehensive test on a specific agent
acp-evals test http://localhost:8000/agents/research-agent --comprehensive
```

**Expected Output**:
- Multiple evaluation categories (Accuracy, Performance, Reliability, Safety)
- Detailed scoring breakdowns
- Overall pass/fail status

**Key Points**:
- Auto-discovery of ACP agents
- Batch testing capabilities
- Comprehensive evaluation suites

---

### Part 3: Synthetic Data Generation

**Message**: "Creating high-quality test data is crucial for thorough evaluation"

```bash
# 1. Generate research-focused test cases
acp-evals generate tests --scenario research --count 10 --use-llm \
  --export research-tests.jsonl
```

**Expected Output**: 
- Progress spinner
- "Generated 10 test cases"
- File saved confirmation

```bash
# 2. Preview generated tests
head -3 research-tests.jsonl | jq .
```

**Expected Output**: JSON objects with input prompts and expected behaviors

```bash
# 3. Generate adversarial test cases
acp-evals generate adversarial --severity high --count 5 \
  --export adversarial-tests.jsonl
```

**Expected Output**: Adversarial scenarios targeting robustness

**Key Points**:
- LLM-powered test generation
- Domain-specific scenarios
- Security-focused testing

---

### Part 4: Advanced Quality Evaluation

**Message**: "Let's dive into sophisticated quality metrics beyond simple accuracy"

```bash
# 1. Create a comprehensive evaluation script
acp-evals init comprehensive --name ResearchAgent --output eval_research.py
```

```bash
# 2. Run multi-dimensional quality evaluation
python eval_research.py
```

**Expected Output**:
- Groundedness scores (responses based on context)
- Completeness evaluation (addressing all query parts)
- Task adherence (following instructions)
- Tool accuracy (if applicable)
- Beautiful summary table

**Key Points**:
- Goes beyond accuracy to measure quality
- Research-based evaluation criteria
- Production-ready metrics

---

### Part 5: Multi-Agent Workflow Testing

**Message**: "Modern AI systems often require multiple agents working together"

```bash
# 1. Test a linear pipeline pattern
acp-evals workflow test --pattern linear \
  --agents researcher analyzer writer \
  --task "Research and summarize recent AI breakthroughs" \
  --export linear-results.json
```

**Expected Output**:
- Step-by-step execution progress
- Information preservation scores between handoffs
- Individual agent performance
- Overall workflow success

```bash
# 2. Compare different coordination patterns
acp-evals workflow compare \
  --agents researcher analyzer writer \
  --task "Analyze market trends in renewable energy" \
  --export pattern-comparison.json
```

**Expected Output**:
- Side-by-side comparison of Linear vs Supervisor vs Swarm
- Efficiency metrics
- Quality scores
- Recommendation based on task type

```bash
# 3. Test handoff quality specifically
acp-evals workflow handoff \
  --agents agent1 agent2 agent3 \
  --rounds 3
```

**Expected Output**:
- Information preservation percentage
- Degradation analysis
- Specific handoff failures

**Key Points**:
- Tests real multi-agent collaboration
- Based on research (linear often beats parallel)
- Critical for enterprise workflows

---

### Part 6: Production Integration

**Message**: "ACP Evals is built for production environments"

```bash
# 1. Load and analyze production traces
acp-evals traces ingest production-traces.json --validate
```

```bash
# 2. Convert traces into test cases
acp-evals traces recycle production-traces.json \
  --output recycled-tests.jsonl \
  --min-quality 0.8
```

**Expected Output**:
- Number of traces processed
- Quality filtering results
- Generated test cases

```bash
# 3. Run regression testing
acp-evals traces regression \
  --baseline baseline-traces.json \
  --current current-traces.json \
  --threshold 0.05
```

**Expected Output**:
- Performance comparison
- Regression detection
- Detailed breakdown of changes

**Key Points**:
- Learn from production data
- Continuous improvement
- Regression prevention

---

### Part 7: CI/CD Integration

**Message**: "Integrate evaluation into your development workflow"

```bash
# 1. Show CI/CD friendly output
acp-evals test $AGENT_URL --comprehensive \
  --export results.json \
  --pass-threshold 80
```

```bash
# 2. Generate markdown report
acp-evals report results.json --format markdown > evaluation-report.md
```

```bash
# 3. Show the report
cat evaluation-report.md
```

**Expected Output**:
- Professional markdown report
- Charts and tables
- Executive summary
- Detailed breakdowns

**Key Points**:
- Exit codes for CI/CD
- Multiple export formats
- Automated quality gates

---

### Part 8: Advanced Features Showcase

**Message**: "Let's explore some unique capabilities"

```bash
# 1. Context scaling benchmark
python examples/benchmarks/context_scaling_demo.py
```

**Expected Output**:
- Performance vs context size graph
- Degradation patterns
- Recommendations

```bash
# 2. Cost tracking across providers
acp-evals test $AGENT_URL --track-tokens --track-latency \
  --export cost-analysis.json
```

**Expected Output**:
- Token usage breakdown
- Cost estimates
- Latency percentiles
- Provider comparison

```bash
# 3. Mock mode for development
acp-evals test $AGENT_URL --mock --quick
```

**Expected Output**:
- Fast execution without API calls
- Useful for CI/CD testing
- Development iteration

**Key Points**:
- Production considerations (cost, latency)
- Developer-friendly features
- Comprehensive tracking

---

## Key Differentiators to Emphasize

1. **Simplicity**: From 5-line scripts to enterprise deployments
2. **Comprehensive**: Accuracy, performance, quality, safety, reliability
3. **Multi-Agent Native**: First-class support for agent orchestration
4. **Production-Ready**: Trace recycling, CI/CD integration, cost tracking
5. **Research-Driven**: Based on latest findings from Anthropic, OpenAI, academic research
6. **Open Source**: Extensible, community-driven, Apache 2.0 licensed
7. **ACP Ecosystem**: Seamless integration with BeeAI and ACP protocol

---

## Closing

**Message**: "ACP Evals makes agent evaluation as easy as unit testing, while providing enterprise-grade capabilities"

```bash
# Show where to learn more
echo "Learn more at: https://github.com/jbarnes850/acp-evals"
echo "Join the community: https://github.com/i-am-bee/beeai-platform/discussions"
```

---

## Backup Commands / Edge Cases

### If no agents are running:
```bash
# Use mock provider
acp-evals test mock://demo-agent --quick
```

### If API keys are missing:
```bash
# Use template-based generation
acp-evals generate tests --use-templates --count 10
```

### If network is slow:
```bash
# Use local Ollama
export ANTHROPIC_API_KEY=""
export OPENAI_API_KEY=""
acp-evals check  # Should show Ollama as available
```

---

## Q&A Preparation

### Common Questions:

**Q: How does this compare to LangChain's evaluation tools?**
A: ACP Evals is specifically designed for agent evaluation with first-class multi-agent support, production trace recycling, and native ACP protocol integration.

**Q: What LLM providers are supported?**
A: OpenAI, Anthropic, Azure OpenAI, Ollama (local), and any OpenAI-compatible endpoint. Easy to add more.

**Q: Can I add custom evaluators?**
A: Yes! Simply inherit from the Evaluator base class and implement the evaluate method. Examples in the codebase.

**Q: How do you handle non-deterministic agent outputs?**
A: Multiple strategies: semantic similarity scoring, multiple runs with consistency checks, and binary evaluators for clear pass/fail.

**Q: What's the performance overhead?**
A: Minimal - async execution, batching, and optional mock mode for development. Production traces can be evaluated offline.

---

## Demo Tips

1. **Have agents running**: Set up at least 2-3 demo agents beforehand
2. **Pre-generate data**: Have some test files ready as backup
3. **Use split terminal**: Show commands and output simultaneously
4. **Keep pace brisk**: The tool outputs are visually appealing, let them shine
5. **Emphasize real-world**: Connect each feature to production use cases

---

**Total Demo Time**: 15-20 minutes (adjust by adding/removing sections)