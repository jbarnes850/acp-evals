# Proposal v2: Evaluation Framework for ACP and BeeAI

## Executive Summary

This proposal outlines the design and implementation of a comprehensive evaluation framework for the Agent Communication Protocol (ACP) and BeeAI Framework ecosystems. Based on analysis of both codebases and recent research on multi-agent systems from Anthropic, Cognition, and LangChain, we propose a framework that addresses the unique challenges of evaluating both single and multi-agent systems, with particular focus on context management, token efficiency, and architectural patterns.

## Background and Motivation

### Current State Analysis

After reviewing both repositories and recent industry research, the following observations were made:

**ACP Repository (i-am-bee/acp)**
- Strong functional testing infrastructure with unit and e2e tests
- Comprehensive event tracking system (`RunCreatedEvent`, `MessageCreatedEvent`, etc.)
- Built-in OpenTelemetry integration for observability
- Example of agent-based evaluation pattern (`beeai-evaluator-optimizer`)
- **Gap**: No standardized metrics, benchmarks, or performance evaluation tools

**BeeAI Framework Repository (i-am-bee/beeai-framework)**
- Focus on multi-agent workflow orchestration
- Built-in observability features with real-time monitoring
- Recognized need for automated testing (Issue #750)
- **Gap**: Limited evaluation infrastructure for agent quality assessment

### Key Insights from Recent Research

1. **Token Usage as Primary Performance Driver** (Anthropic): Token usage explains 80% of performance variance in agent systems
2. **Context Sharing is Critical** (Cognition): Full agent traces must be shared, not just individual messages
3. **Architecture Matters** (LangChain): Different multi-agent patterns (supervisor, swarm) have significant performance trade-offs
4. **Small Samples Work** (Anthropic): 20 test cases can reveal dramatic performance differences
5. **Errors Compound** (Anthropic): Agent systems are stateful and minor failures cascade

## Proposed Solution

### Overview

Create `acp-evals`: a modular evaluation framework that provides:
- Token efficiency and cost metrics as first-class citizens
- Context degradation and handoff quality measurements
- Architecture-specific benchmarks (single, supervisor, swarm patterns)
- Small but effective evaluation sets (20-50 cases per benchmark)
- Both automated (LLM-as-judge) and human evaluation support

### Updated Architecture

```
acp-evals/
├── python/
│   ├── src/
│   │   └── acp_evals/
│   │       ├── metrics/
│   │       │   ├── __init__.py
│   │       │   ├── quality.py           # Output quality scoring
│   │       │   ├── performance.py       # Latency, throughput
│   │       │   ├── cost.py             # Token usage, API costs (PRIORITY)
│   │       │   ├── context.py          # Context window usage, handoff quality
│   │       │   └── composite.py        # Multi-dimensional scoring
│   │       ├── benchmarks/
│   │       │   ├── __init__.py
│   │       │   ├── single_agent/       # Single agent benchmarks
│   │       │   │   ├── qa.py
│   │       │   │   ├── context_scaling.py  # Test degradation with context
│   │       │   │   └── tool_use.py
│   │       │   ├── multi_agent/        # Multi-agent specific
│   │       │   │   ├── handoff.py      # Test information preservation
│   │       │   │   ├── parallel_tasks.py
│   │       │   │   └── architectures.py # Compare supervisor vs swarm
│   │       │   └── datasets/
│   │       │       └── tau_bench_subset.py # Adapt tau-bench for ACP
│   │       ├── evaluators/
│   │       │   ├── __init__.py
│   │       │   ├── base.py
│   │       │   ├── llm_judge.py        # With rubrics from Anthropic research
│   │       │   ├── rule_based.py
│   │       │   └── human_eval.py       # Interface for human evaluation
│   │       ├── patterns/
│   │       │   ├── __init__.py
│   │       │   ├── supervisor.py       # Supervisor pattern implementation
│   │       │   ├── swarm.py           # Swarm pattern implementation
│   │       │   └── linear.py          # Single-threaded linear pattern
│   │       └── analysis/
│   │           ├── __init__.py
│   │           ├── token_analysis.py   # Token usage patterns
│   │           ├── context_analysis.py # Context window utilization
│   │           └── error_cascades.py   # Track error propagation
│   ├── tests/
│   └── pyproject.toml
```

### Core Components (Updated)

#### 1. Token and Cost Metrics (Priority)

Based on Anthropic's findings that token usage drives 80% of performance variance:

```python
class TokenUsageMetric(Metric):
    """Tracks token consumption with detailed breakdowns."""
    
    async def calculate(self, run: Run, events: List[Event]) -> MetricResult:
        # Track tokens per:
        # - Agent/subagent
        # - Tool call
        # - Message type
        # - Context window percentage used
        
        return MetricResult(
            name="token_usage",
            value=total_tokens,
            breakdown={
                "input_tokens": input_count,
                "output_tokens": output_count,
                "tool_tokens": tool_count,
                "cost_usd": estimated_cost,
                "efficiency_score": output_value / total_tokens
            }
        )

class ContextEfficiencyMetric(Metric):
    """Measures how efficiently agents use their context window."""
    
    async def calculate(self, run: Run, events: List[Event]) -> MetricResult:
        # Analyze context window usage patterns
        # Identify wasteful context retention
        # Track context compression effectiveness
```

#### 2. Architecture-Aware Benchmarks

Following LangChain's research on different patterns:

```python
class MultiAgentArchitectureBenchmark(Benchmark):
    """Compare different multi-agent architectures on same tasks."""
    
    def __init__(self, architecture: str = "supervisor"):
        self.architecture = architecture
        self.distractor_domains = []  # Add irrelevant tools/context
        
    async def evaluate_with_distractors(self, agent, num_distractors: int):
        """Test performance degradation with added context."""
        # Based on LangChain's tau-bench approach
        
class HandoffQualityBenchmark(Benchmark):
    """Measure information preservation across agent handoffs."""
    
    async def evaluate(self, agents: List[Agent]) -> BenchmarkResult:
        # Test "telephone game" effects
        # Measure context degradation
        # Track decision conflicts
```

#### 3. LLM-as-Judge with Rubrics

Following Anthropic's successful approach:

```python
class LLMJudge(Evaluator):
    """Evaluates outputs using LLM with structured rubrics."""
    
    def __init__(self):
        self.rubric = {
            "factual_accuracy": {"weight": 0.3, "criteria": "..."},
            "citation_accuracy": {"weight": 0.2, "criteria": "..."},
            "completeness": {"weight": 0.2, "criteria": "..."},
            "source_quality": {"weight": 0.15, "criteria": "..."},
            "efficiency": {"weight": 0.15, "criteria": "..."}
        }
        
    async def evaluate(self, output: str, reference: str) -> float:
        # Single LLM call with 0.0-1.0 scoring
        # Pass/fail grade
        # Detailed feedback
```

#### 4. Context Engineering Patterns

Based on Cognition's principles:

```python
class ContextAnalyzer:
    """Analyzes context sharing and decision preservation."""
    
    def analyze_handoff(self, 
                       source_agent_trace: List[Event],
                       target_agent_trace: List[Event]) -> HandoffQuality:
        # Measure information loss
        # Identify conflicting decisions
        # Track context compression quality
        
    def recommend_pattern(self, task_type: str) -> str:
        """Recommend single-threaded vs multi-agent based on task."""
        # Use Cognition's heuristics
```

### Implementation Priorities (Revised)

#### Phase 0: MVP with Core Insights (Weeks 1-2)
- Implement token usage and cost metrics
- Create simple 20-case benchmark set
- Basic LLM-as-judge evaluator
- Test with single agent baseline

#### Phase 1: Multi-Agent Patterns (Weeks 3-6)
- Implement supervisor and swarm patterns
- Context degradation benchmarks
- Handoff quality metrics
- Architecture comparison tools

#### Phase 2: Production Features (Weeks 7-10)
- Error cascade tracking
- State management evaluation
- Long-running agent tests
- Human evaluation interface

#### Phase 3: Advanced Analysis (Weeks 11-12)
- Token efficiency optimization recommendations
- Context compression strategies
- Architecture selection advisor
- Cost-benefit analysis tools

## Key Design Decisions

### 1. Start Small, But Smart
- Initial benchmark suite of 20-30 carefully chosen cases
- Focus on high-effect-size measurements
- Rapid iteration based on early findings

### 2. Token-First Metrics
- Every evaluation tracks token usage
- Cost estimates for all operations
- Efficiency scores (value per token)
- Multi-agent token multiplication factors

### 3. Architecture-Agnostic, Pattern-Aware
- Support any ACP-compatible agent
- Specific tests for known patterns
- Recommendations based on task characteristics

### 4. Context is King
- Full trace preservation in evaluations
- Handoff quality as first-class metric
- Context window utilization tracking

### 5. Production Realism
- Stateful error tracking
- Long-running stability tests
- Recovery and resume capabilities

## Success Metrics (Updated)

1. **Token Efficiency**: Identify 80%+ of performance variance through token analysis
2. **Architecture Guidance**: Clear recommendations for single vs multi-agent patterns
3. **Early Detection**: Catch major issues with <30 test cases
4. **Cost Transparency**: Accurate cost projections for different approaches
5. **Context Optimization**: 30%+ reduction in context waste through better patterns

## Technical Considerations

### Handling Stateful Evaluations
```python
class StatefulEvaluator:
    """Handles long-running evaluations with checkpoints."""
    
    async def evaluate_with_checkpoints(self, agent, task):
        # Save state at regular intervals
        # Support resume from checkpoint
        # Track error propagation patterns
```

### Multi-Agent Coordination Testing
```python
class CoordinationBenchmark:
    """Tests requiring true agent coordination."""
    
    async def evaluate_parallel_work(self, agents):
        # Genuinely parallelizable tasks
        # Measure coordination overhead
        # Track redundant work
```

## Conclusion

This updated evaluation framework incorporates cutting-edge insights from production multi-agent systems. By prioritizing token efficiency, context management, and architectural patterns, we can provide the ACP/BeeAI community with tools that address real-world challenges. The focus on small but effective evaluation sets and production-ready patterns ensures both accessibility and practical value.

The framework acknowledges that multi-agent systems are powerful but complex, requiring careful evaluation of trade-offs between performance, cost, and reliability. By building these considerations into our evaluation tools from the start, we can help developers make informed decisions about when and how to use multi-agent architectures.