# ACP Evals Development Setup Guide v2

## Quick Start: Token-First MVP

Based on recent research showing token usage drives 80% of performance variance, we'll start with a token-focused MVP.

### 1. Create Repository Structure

```bash
# Create main directory
mkdir acp-evals
cd acp-evals
git init

# Create focused initial structure
mkdir -p python/src/acp_evals/{metrics,benchmarks,evaluators,analysis}
mkdir -p python/tests
mkdir -p examples/python
mkdir docs

# Create README
cat > README.md << 'EOF'
# ACP Evals

Token-first evaluation framework for ACP agents, incorporating insights from production multi-agent systems.

## Key Features
- Token usage and cost analysis (80% of performance variance)
- Context degradation measurement
- Multi-agent architecture comparison
- Small but effective benchmark sets (20-50 cases)

## Quick Start
```bash
pip install acp-evals
acp-evals evaluate http://localhost:8000 --metrics token,latency,quality
```
EOF
```

### 2. Set Up Python Package

Create `python/pyproject.toml`:

```toml
[project]
name = "acp-evals"
version = "0.1.0"
description = "Token-first evaluation framework for ACP agents"
readme = "../README.md"
requires-python = ">=3.11"
dependencies = [
    "acp-sdk",
    "numpy",
    "pandas", 
    "rich",
    "tiktoken",  # For accurate token counting
    "pydantic",  # For config management
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "ruff",
    "pyright",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 3. Core Components: Token-First Implementation

#### Base Classes (`python/src/acp_evals/base.py`):

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

@dataclass
class MetricResult:
    name: str
    value: float
    unit: str
    breakdown: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    tool_tokens: int
    total_tokens: int
    cost_usd: float
    model: str
    context_percentage: float  # How full was the context window?
```

#### Token Usage Metric (`python/src/acp_evals/metrics/token_usage.py`):

```python
import tiktoken
from typing import List, Dict
from acp_sdk import Run, Event, Message
from ..base import Metric, MetricResult, TokenUsage

class TokenUsageMetric(Metric):
    """Primary metric: tracks token consumption with cost analysis."""
    
    # Approximate costs per 1K tokens (update as needed)
    COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.encoder = tiktoken.get_encoding("cl100k_base")
        
    async def calculate(self, run: Run, events: List[Event]) -> MetricResult:
        usage = TokenUsage(
            input_tokens=0,
            output_tokens=0,
            tool_tokens=0,
            total_tokens=0,
            cost_usd=0.0,
            model=self.model,
            context_percentage=0.0
        )
        
        # Track tokens by agent/subagent
        agent_breakdown = {}
        
        for event in events:
            if event.type == "message.created":
                tokens = self._count_message_tokens(event.message)
                
                if event.agent_id not in agent_breakdown:
                    agent_breakdown[event.agent_id] = {"in": 0, "out": 0, "tool": 0}
                
                if event.message.role == "user":
                    usage.input_tokens += tokens
                    agent_breakdown[event.agent_id]["in"] += tokens
                elif event.message.role == "assistant":
                    usage.output_tokens += tokens
                    agent_breakdown[event.agent_id]["out"] += tokens
                elif event.message.role == "tool":
                    usage.tool_tokens += tokens
                    agent_breakdown[event.agent_id]["tool"] += tokens
        
        usage.total_tokens = usage.input_tokens + usage.output_tokens + usage.tool_tokens
        usage.cost_usd = self._calculate_cost(usage)
        
        # Calculate efficiency score (tokens per successful task)
        efficiency_score = 1.0 / usage.total_tokens if run.status == "completed" else 0.0
        
        return MetricResult(
            name="token_usage",
            value=usage.total_tokens,
            unit="tokens",
            breakdown={
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "tool_tokens": usage.tool_tokens,
                "cost_usd": usage.cost_usd,
                "efficiency_score": efficiency_score,
                "agent_breakdown": agent_breakdown,
                "tokens_per_message": usage.total_tokens / len(events) if events else 0
            },
            metadata={"model": self.model, "run_id": run.id}
        )
```

#### Context Degradation Benchmark (`python/src/acp_evals/benchmarks/context_scaling.py`):

```python
from typing import List
from ..base import Benchmark, BenchmarkTask, BenchmarkResult

class ContextScalingBenchmark(Benchmark):
    """Tests performance degradation with increasing context (tau-bench inspired)."""
    
    def __init__(self):
        # Core task that actually needs to be solved
        self.core_task = BenchmarkTask(
            id="find_info",
            prompt="What is the return policy for electronics?",
            expected_keywords=["30 days", "original packaging", "receipt"],
            category="information_retrieval"
        )
        
        # Distractor contexts that shouldn't affect the answer
        self.distractors = [
            "Restaurant menu: We serve pizza, pasta, and salads...",
            "Car manual: Change oil every 5000 miles...",
            "Recipe book: To make cookies, mix flour and sugar...",
            # Add more realistic distractors
        ]
    
    async def evaluate_with_context_levels(self, agent, levels=[0, 1, 3, 5, 10]):
        """Test agent with increasing amounts of irrelevant context."""
        results = []
        
        for num_distractors in levels:
            # Build prompt with distractors
            context = "\n\n".join(self.distractors[:num_distractors])
            full_prompt = f"{context}\n\n{self.core_task.prompt}" if context else self.core_task.prompt
            
            # Run agent and measure performance
            start_time = datetime.now()
            response = await agent.run(full_prompt)
            latency = (datetime.now() - start_time).total_seconds()
            
            # Check if core task was solved correctly
            score = sum(1 for kw in self.core_task.expected_keywords 
                       if kw.lower() in response.lower())
            accuracy = score / len(self.core_task.expected_keywords)
            
            results.append({
                "distractor_count": num_distractors,
                "accuracy": accuracy,
                "latency": latency,
                "response_length": len(response)
            })
        
        return BenchmarkResult(
            benchmark_name="ContextScaling",
            agent_id=agent.id,
            results=results,
            summary={
                "degradation_rate": self._calculate_degradation(results),
                "optimal_context_size": self._find_optimal_size(results)
            }
        )
```

#### Multi-Agent Handoff Test (`python/src/acp_evals/benchmarks/handoff_quality.py`):

```python
class HandoffQualityBenchmark(Benchmark):
    """Measures information preservation across agent handoffs (Cognition insights)."""
    
    async def evaluate_handoff_chain(self, agents: List[Agent], initial_task: str):
        """Test information preservation through multiple handoffs."""
        
        original_info = {
            "task": initial_task,
            "constraints": ["budget: $1000", "deadline: Friday", "quality: high"],
            "decisions": ["use Python", "deploy on AWS", "include tests"]
        }
        
        current_context = self._format_initial_context(original_info)
        handoff_results = []
        
        for i, agent in enumerate(agents):
            # Each agent processes and passes to next
            response = await agent.run(f"""
            Previous agent context: {current_context}
            
            Your task: Understand the requirements and pass them to the next agent.
            Preserve all important details and decisions.
            """)
            
            # Analyze information preservation
            preserved_constraints = sum(1 for c in original_info["constraints"] 
                                      if c in response)
            preserved_decisions = sum(1 for d in original_info["decisions"] 
                                    if d in response)
            
            preservation_score = (preserved_constraints + preserved_decisions) / \
                               (len(original_info["constraints"]) + len(original_info["decisions"]))
            
            handoff_results.append({
                "agent": i,
                "preservation_score": preservation_score,
                "response_length": len(response),
                "added_noise": len(response) - len(current_context)  # Information bloat
            })
            
            current_context = response
        
        return BenchmarkResult(
            benchmark_name="HandoffQuality",
            results=handoff_results,
            summary={
                "total_degradation": 1.0 - handoff_results[-1]["preservation_score"],
                "noise_accumulation": sum(r["added_noise"] for r in handoff_results)
            }
        )
```

### 4. LLM-as-Judge Implementation

Create `python/src/acp_evals/evaluators/llm_judge.py`:

```python
from acp_sdk import Client
import json

class LLMJudge:
    """Automated evaluation using LLM with rubrics (Anthropic approach)."""
    
    def __init__(self, judge_model="gpt-4"):
        self.judge_model = judge_model
        self.rubric = {
            "accuracy": {
                "weight": 0.4,
                "prompt": "Does the response accurately answer the question?"
            },
            "completeness": {
                "weight": 0.3,
                "prompt": "Does the response cover all requested aspects?"
            },
            "efficiency": {
                "weight": 0.3,
                "prompt": "Is the response concise without unnecessary information?"
            }
        }
    
    async def evaluate(self, task: str, response: str, reference: str = None) -> Dict:
        """Single LLM call for all criteria (more consistent than multiple calls)."""
        
        prompt = f"""
        Evaluate this agent response using the rubric below.
        
        Task: {task}
        Agent Response: {response}
        {f'Reference Answer: {reference}' if reference else ''}
        
        Rubric:
        {json.dumps(self.rubric, indent=2)}
        
        Provide scores from 0.0 to 1.0 for each criterion and an overall pass/fail.
        Format: JSON with keys matching the rubric criteria plus "overall_score" and "pass".
        """
        
        # Use your judge model to evaluate
        # This is simplified - implement actual LLM call
        evaluation = await self._call_judge_llm(prompt)
        
        return evaluation
```

### 5. Quick Evaluation Script

Create `examples/python/evaluate_with_insights.py`:

```python
import asyncio
from acp_sdk import Client
from acp_evals.metrics import TokenUsageMetric, LatencyMetric
from acp_evals.benchmarks import ContextScalingBenchmark
from acp_evals.evaluators import LLMJudge
from rich.console import Console
from rich.table import Table

console = Console()

async def main():
    # Connect to agent
    client = Client(base_url="http://localhost:8000")
    
    # Initialize evaluation components
    token_metric = TokenUsageMetric(model="gpt-4")
    context_benchmark = ContextScalingBenchmark()
    judge = LLMJudge()
    
    console.print("[bold]🔍 ACP Agent Evaluation[/bold]\n")
    
    # Get agent
    agents = await client.agents()
    if not agents:
        console.print("[red]No agents found![/red]")
        return
    
    agent = agents[0]
    console.print(f"Evaluating: [cyan]{agent.manifest.name}[/cyan]\n")
    
    # Run context scaling test
    console.print("[yellow]Running context scaling benchmark...[/yellow]")
    scaling_results = await context_benchmark.evaluate_with_context_levels(
        agent, 
        levels=[0, 1, 3, 5]
    )
    
    # Display results in a table
    table = Table(title="Context Scaling Results")
    table.add_column("Distractors", style="cyan")
    table.add_column("Accuracy", style="green")
    table.add_column("Latency (s)", style="yellow")
    table.add_column("Token Cost", style="red")
    
    for result in scaling_results.results:
        # Get token metrics for this run
        run = await client.get_latest_run(agent.id)
        events = await client.run_events(run_id=run.id)
        token_result = await token_metric.calculate(run, events)
        
        table.add_row(
            str(result["distractor_count"]),
            f"{result['accuracy']:.0%}",
            f"{result['latency']:.2f}",
            f"${token_result.breakdown['cost_usd']:.4f}"
        )
    
    console.print(table)
    
    # Key insights
    console.print(f"\n[bold]Key Insights:[/bold]")
    console.print(f"• Performance degradation: {scaling_results.summary['degradation_rate']:.1%}")
    console.print(f"• Token efficiency: {1/token_result.value:.6f} success/token")
    console.print(f"• Estimated cost for 1000 queries: ${token_result.breakdown['cost_usd'] * 1000:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development Workflow

### 1. Start with Token Analysis

Focus initial efforts on understanding token usage patterns:

```bash
# Set up environment
cd python
uv sync

# Run token analysis on existing agents
uv run python examples/evaluate_with_insights.py
```

### 2. Build Small, Effective Benchmarks

Create 20-30 high-impact test cases:
- Focus on tasks that reveal architectural differences
- Include context scaling tests
- Add multi-agent handoff scenarios

### 3. Implement Architecture Patterns

Test different multi-agent patterns:
```python
# Supervisor pattern
supervisor = SupervisorPattern(agents=[agent1, agent2])
results = await benchmark.evaluate(supervisor)

# Swarm pattern  
swarm = SwarmPattern(agents=[agent1, agent2])
results = await benchmark.evaluate(swarm)

# Compare results
comparison = compare_patterns(supervisor_results, swarm_results)
```

### 4. Community Engagement

When sharing results, emphasize:
- Token usage insights (15x multiplier for multi-agent)
- Context degradation findings
- Architecture recommendations
- Cost projections

## Key Implementation Notes

1. **Token Tracking is Essential**: Every evaluation must track tokens
2. **Small Sample Sizes Work**: 20-50 carefully chosen cases reveal most issues
3. **Context Matters**: Full traces, not just messages
4. **Architecture Affects Everything**: Test patterns separately
5. **Costs Add Up**: Multi-agent = 15x tokens = 15x cost

## Next Steps

1. Implement token metric MVP
2. Create 20-case benchmark set
3. Test with single agent baseline
4. Add multi-agent patterns
5. Share findings with community
6. Iterate based on feedback

## Future Extensibility Example

While building the MVP, design interfaces that could support domain-specific evaluation:

```python
# Example of extensible design for future domain-specific evals
class DomainSpecificBenchmark(Benchmark):
    """Base class that could support custom domain benchmarks."""
    
    @classmethod
    def from_traces(cls, traces: List[AgentTrace]):
        """Future: Generate benchmark from real usage traces."""
        pass
    
    @classmethod
    def generate_synthetic(cls, domain: str, num_cases: int):
        """Future: Use LLM to generate domain-specific test cases."""
        pass
    
    def adapt_difficulty(self, agent_performance: float):
        """Future: Adjust benchmark difficulty based on agent capability."""
        pass
```

This ensures our initial framework can grow to support the market's move toward domain-specific, adaptive evaluation without major rewrites.